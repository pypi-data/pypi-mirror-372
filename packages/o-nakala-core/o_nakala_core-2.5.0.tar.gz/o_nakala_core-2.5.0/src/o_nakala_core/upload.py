"""
Nakala Upload Client

Handles uploading datasets to the Nakala API with support for both CSV and folder-based datasets.
"""

import csv
import os
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime
import mimetypes
import hashlib

# Import common utilities
from .common import (
    NakalaCommonUtils,
    NakalaPathResolver,
    NakalaConfig,
    NakalaValidationError,
    NakalaAPIError,
    NakalaFileError,
    setup_common_logging,
)

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class NakalaFileProcessor:
    """Handles file processing and metadata generation."""

    def __init__(self, config: NakalaConfig):
        self.config = config
        self.path_resolver = NakalaPathResolver(config.base_path)
        self.utils = NakalaCommonUtils()

    def process_folder_structure(self, folder_config_path: str) -> List[Dict[str, Any]]:
        """Process folder structure based on configuration."""
        if not os.path.exists(folder_config_path):
            raise NakalaFileError(f"Folder config file not found: {folder_config_path}")

        folder_config = self._load_folder_config(folder_config_path)
        folder_files = {}

        for root, _, files in os.walk(self.config.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    rel_path = self.path_resolver.get_relative_path(
                        os.path.dirname(file_path)
                    )

                    if rel_path in folder_config:
                        if rel_path not in folder_files:
                            folder_files[rel_path] = {
                                "metadata": folder_config[rel_path].copy(),
                                "files": [],
                            }
                        folder_files[rel_path]["files"].append(file_path)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

        # Convert to results format
        results = []
        for folder_path, folder_data in folder_files.items():
            results.append(
                {
                    "folder_path": folder_path,
                    "metadata": folder_data["metadata"],
                    "files": folder_data["files"],
                }
            )

        return results

    def _load_folder_config(self, config_path: str) -> Dict[str, Any]:
        """Load folder configuration from CSV file."""
        config = {}
        try:
            with open(config_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    folder_path = row["file"].rstrip("/")
                    config[folder_path] = row
            return config
        except Exception as e:
            raise NakalaFileError(f"Error loading folder config: {e}")

    def validate_file(self, file_path: str) -> bool:
        """Validate that a file exists and is accessible."""
        if not self.path_resolver.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        if not self.path_resolver.is_file(file_path):
            logger.error(f"Path is not a file: {file_path}")
            return False

        return True

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA1 hash of a file."""
        sha1_hash = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1_hash.update(chunk)
        return sha1_hash.hexdigest()

    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract file metadata including size, mimetype, and sha1."""
        if not os.path.exists(file_path):
            raise NakalaFileError(f"File not found: {file_path}")

        # Get file size
        file_size = os.path.getsize(file_path)

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Calculate SHA1 hash
        sha1 = self._calculate_file_hash(file_path)

        return {
            "size": file_size,
            "mimetype": mime_type,
            "sha1": sha1,
            "name": os.path.basename(file_path),
        }


class NakalaUploadClient:
    """Main upload client for Nakala API."""

    def __init__(self, config: NakalaConfig):
        self.config = config
        self.file_processor = NakalaFileProcessor(config)
        self.utils = NakalaCommonUtils()
        self.session = requests.Session()

        # Set up session headers
        self.session.headers.update(
            {"X-API-KEY": config.api_key, "User-Agent": "Nakala-Client/2.0"}
        )

        # Validate configuration
        if not config.validate_paths():
            raise NakalaValidationError("Invalid configuration paths")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def upload_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Upload a single file to Nakala with retry mechanism."""
        try:
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            with open(file_path, "rb") as f:
                files = [("file", (filename, f, mime_type))]

                response = self.session.post(
                    f"{self.config.api_url}/datas/uploads",
                    files=files,
                    timeout=getattr(self.config, "upload_timeout", self.config.timeout),
                )

            if response.status_code == 201:
                file_info = response.json()
                file_info["embargoed"] = datetime.now().strftime("%Y-%m-%d")
                logger.info(f"Successfully uploaded: {filename}")
                return file_info
            else:
                raise NakalaAPIError(
                    f"Upload failed for {filename}",
                    status_code=response.status_code,
                    response_text=response.text,
                )

        except requests.RequestException as e:
            raise NakalaAPIError(f"Network error uploading {filename}: {e}")
        except Exception as e:
            raise NakalaFileError(f"Error uploading {filename}: {e}")

    def _upload_file(self, file_path: str) -> str:
        """Upload a single file and return its SHA1 identifier."""
        filename = os.path.basename(file_path)
        file_info = self.upload_file(file_path, filename)
        return file_info.get("sha1", file_info.get("identifier", ""))

    def _create_dataset(
        self, metadata: List[Dict[str, Any]], files: List[Dict[str, Any]]
    ) -> str:
        """Create a dataset with metadata and files, return identifier."""
        payload = {"metas": metadata, "files": files, "status": "pending"}

        response = self.session.post(
            f"{self.config.api_url}/datas", json=payload, timeout=self.config.timeout
        )

        if response.status_code == 201:
            result = response.json()
            return result.get("identifier", "")
        else:
            raise NakalaAPIError(
                "Dataset creation failed",
                status_code=response.status_code,
                response_text=response.text,
            )

    def _validate_dataset_config(self, config: Dict[str, Any]) -> None:
        """Validate dataset configuration dictionary."""
        required_fields = ["title", "type"]

        for field in required_fields:
            if field not in config:
                raise NakalaValidationError(f"Missing required field: {field}")

        if not config["title"].strip():
            raise NakalaValidationError("Title cannot be empty")

        # Validate type URI format
        type_uri = config["type"]
        if not type_uri.startswith("http://"):
            raise NakalaValidationError(f"Invalid type URI format: {type_uri}")

    def upload_single_dataset(self, config: Dict[str, Any]) -> str:
        """Upload a single dataset from configuration dictionary."""
        self._validate_dataset_config(config)

        # Prepare metadata
        metadata = [
            {
                "propertyUri": "http://nakala.fr/terms#title",
                "value": config["title"],
                "lang": config.get("language", "en"),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
            },
            {
                "propertyUri": "http://nakala.fr/terms#type",
                "value": config["type"],
                "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI",
            },
        ]

        # Add description if provided
        if config.get("description"):
            metadata.append(
                {
                    "propertyUri": "http://nakala.fr/terms#description",
                    "value": config["description"],
                    "lang": config.get("language", "en"),
                    "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                }
            )

        # Process files
        files = []
        for file_path in config.get("files", []):
            if os.path.exists(file_path):
                sha1 = self._upload_file(file_path)
                files.append(
                    {
                        "sha1": sha1,
                        "name": os.path.basename(file_path),
                        "embargoed": datetime.now().strftime("%Y-%m-%d"),
                    }
                )

        # Create dataset
        return self._create_dataset(metadata, files)

    def prepare_metadata_from_dict(
        self, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prepare metadata from dictionary using common utilities."""
        return self.utils.prepare_nakala_metadata(metadata)

    def prepare_rights(self, rights_string: str) -> List[Dict[str, str]]:
        """Prepare rights using common utilities."""
        return self.utils.prepare_rights_list(
            rights_string, self.config.valid_group_ids
        )

    def _resolve_file_path(self, filename: str) -> Optional[str]:
        """
        Resolve file path by searching in base directory and subdirectories.

        Args:
            filename: The filename to search for

        Returns:
            Full path to the file if found, None otherwise
        """
        # First try direct path in base directory
        direct_path = os.path.join(self.config.base_path, filename)
        if os.path.isfile(direct_path):
            return direct_path

        # Search in subdirectories
        for root, _, files in os.walk(self.config.base_path):
            if filename in files:
                found_path = os.path.join(root, filename)
                logger.debug(f"Found file {filename} at {found_path}")
                return found_path

        return None

    @retry(
        stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=4, max=30)
    )
    def create_dataset(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a dataset in Nakala with improved timeout handling."""

        # Validate payload before sending
        validation_errors = self._validate_dataset_payload(payload)
        if validation_errors:
            error_msg = (
                f"Dataset payload validation failed: {'; '.join(validation_errors)}"
            )
            logger.error(error_msg)
            raise NakalaValidationError(error_msg)

        try:
            logger.debug(f"Creating dataset with timeout: {self.config.timeout}s")
            response = requests.post(
                f"{self.config.api_url}/datas",
                headers=self.config.get_headers(),
                data=json.dumps(payload),
                timeout=self.config.timeout,
            )

            if response.status_code == 201:
                result = response.json()
                logger.info(f"Successfully created dataset: {result['payload']['id']}")
                return result
            elif response.status_code == 429:
                # Rate limiting - wait longer before retry
                logger.warning(
                    "Rate limited by API, will retry with exponential backoff"
                )
                raise NakalaAPIError(
                    "Rate limited by API",
                    status_code=response.status_code,
                    response_text=response.text,
                )
            elif response.status_code >= 500:
                # Server errors - retry
                logger.warning(
                    f"Server error (HTTP {response.status_code}), will retry"
                )
                raise NakalaAPIError(
                    f"Server error (HTTP {response.status_code})",
                    status_code=response.status_code,
                    response_text=response.text,
                )
            else:
                # Client errors - don't retry
                error_details = self._parse_api_error(response)
                logger.error(
                    f"API Error (HTTP {response.status_code}): {error_details}"
                )

                # Log payload for debugging metadata issues
                if response.status_code == 400:
                    logger.debug(
                        f"Request payload that caused error: {json.dumps(payload, indent=2)}"
                    )

                raise NakalaAPIError(
                    f"Failed to create dataset (HTTP {response.status_code}): {error_details}",
                    status_code=response.status_code,
                    response_text=response.text,
                )

        except requests.Timeout as e:
            logger.warning(f"Request timeout after {self.config.timeout}s, will retry")
            raise NakalaAPIError(f"Request timeout creating dataset: {e}")
        except requests.ConnectionError as e:
            logger.warning(f"Connection error, will retry: {e}")
            raise NakalaAPIError(f"Connection error creating dataset: {e}")
        except requests.RequestException as e:
            logger.error(f"Unexpected network error: {e}")
            raise NakalaAPIError(f"Network error creating dataset: {e}")

    def _parse_api_error(self, response) -> str:
        """Parse API error response to extract meaningful error messages."""
        try:
            error_data = response.json()

            # Handle different error response formats
            if isinstance(error_data, dict):
                # Check for specific error patterns
                if "message" in error_data:
                    message = error_data["message"]

                    # Provide specific guidance for common metadata errors
                    if "nakala:creator must be an array" in message:
                        return (
                            f"{message} - Ensure creator metadata is properly "
                            "formatted as an array"
                        )
                    elif "must not have" in message and "lang" in message:
                        return (
                            f"{message} - Remove language attributes from system fields "
                            "like date/license"
                        )
                    elif "metadata" in message.lower():
                        return f"Metadata validation error: {message}"

                    return message
                elif "error" in error_data:
                    return str(error_data["error"])
                elif "errors" in error_data:
                    return str(error_data["errors"])

            # Fallback to raw response text
            return response.text[:500]  # Limit length

        except (json.JSONDecodeError, KeyError):
            return response.text[:500]  # Limit length

    def _validate_dataset_payload(self, payload: Dict[str, Any]) -> List[str]:
        """Validate dataset payload to catch common errors early."""
        errors = []

        # Check required fields
        if "metas" not in payload:
            errors.append("Missing 'metas' field in payload")
            return errors

        metas = payload["metas"]
        if not isinstance(metas, list):
            errors.append("'metas' must be a list")
            return errors

        # Validate metadata structure
        for i, meta in enumerate(metas):
            if not isinstance(meta, dict):
                errors.append(f"Meta entry {i} must be a dictionary")
                continue

            # Check required metadata fields
            if "propertyUri" not in meta:
                errors.append(f"Meta entry {i} missing 'propertyUri'")

            if "value" not in meta:
                errors.append(f"Meta entry {i} missing 'value'")
                continue

            # Check creator/contributor arrays
            if meta.get("propertyUri") in [
                "http://nakala.fr/terms#creator",
                "http://purl.org/dc/terms/contributor",
            ]:
                if not isinstance(meta["value"], list):
                    errors.append(
                        f"Creator/contributor metadata must have array value, "
                        f"got {type(meta['value'])}"
                    )

            # Check for forbidden language attributes on system fields
            if meta.get("propertyUri") in [
                "http://purl.org/dc/terms/created",
                "http://purl.org/dc/terms/license",
            ]:
                if "lang" in meta:
                    errors.append(
                        f"System field {meta['propertyUri']} cannot have 'lang' attribute"
                    )

        return errors

    def process_csv_dataset(self, csv_path: str) -> None:
        """Process CSV-based dataset."""
        if not os.path.exists(csv_path):
            raise NakalaFileError(f"CSV file not found: {csv_path}")

        output_path = self.config.output_path

        with open(output_path, "w", newline="", encoding="utf-8") as output:
            output_writer = csv.writer(output)
            output_writer.writerow(
                ["identifier", "files", "title", "status", "response"]
            )

            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                dataset = list(reader)

            # Remove header
            if dataset:
                dataset.pop(0)

            total_entries = len(dataset)
            for num, data in enumerate(dataset, 1):
                logger.info(f"Processing entry {num}/{total_entries}: {data[3]}")
                self._process_csv_entry(data, output_writer)

    def _process_csv_entry(self, data: List[str], output_writer) -> None:
        """Process a single CSV entry."""
        output_data = ["", "", data[3], "", ""]

        try:
            # Upload files
            nakala_files = []
            output_files = []

            filenames = data[0].split(";")
            for filename in filenames:
                # Try to find the file in base directory or subdirectories
                resolved_file_path = self._resolve_file_path(filename)
                if not resolved_file_path:
                    logger.error(f"File not found: {filename}")
                    continue

                logger.info(f"Uploading file: {filename}")
                file_info = self.upload_file(resolved_file_path, filename)
                nakala_files.append(file_info)
                output_files.append(f"{filename},{file_info['sha1']}")

            # Prepare metadata
            metadata_dict = {
                "type": data[2],
                "title": data[3],
                "creator": data[4],
                "date": data[5],
                "license": data[6],
                "description": data[7],
                "keywords": data[8],
            }

            metas = self.prepare_metadata_from_dict(metadata_dict)
            rights = self.prepare_rights(data[9] if len(data) > 9 else "")

            # Create payload
            payload = {
                "status": data[1],
                "files": nakala_files,
                "metas": metas,
                "rights": rights,
            }

            # Create dataset
            result = self.create_dataset(payload)
            output_data[0] = result["payload"]["id"]
            output_data[1] = ";".join(output_files)
            output_data[3] = "OK"
            output_data[4] = json.dumps(result)

        except Exception as e:
            logger.error(f"Error processing CSV entry: {e}")
            output_data[3] = "ERROR"
            output_data[4] = str(e)

        output_writer.writerow(output_data)

    def process_folder_dataset(self, folder_config_path: str) -> None:
        """Process folder-based dataset."""
        results = self.file_processor.process_folder_structure(folder_config_path)

        if not results:
            logger.warning("No folders found to process")
            return

        output_path = self.config.output_path

        with open(output_path, "w", newline="", encoding="utf-8") as output:
            output_writer = csv.writer(output)
            output_writer.writerow(
                ["identifier", "files", "title", "status", "response"]
            )

            for result in results:
                self._process_folder_entry(result, output_writer)

    def _process_folder_entry(self, result: Dict[str, Any], output_writer) -> None:
        """Process a single folder entry."""
        try:
            # Upload all files in the folder
            file_infos = []

            for file_path in result["files"]:
                if not self.file_processor.validate_file(file_path):
                    continue

                filename = os.path.basename(file_path)
                logger.info(f"Uploading file: {filename}")
                file_info = self.upload_file(file_path, filename)
                file_infos.append(file_info)

            if not file_infos:
                logger.warning(
                    f"No valid files found in folder: {result.get('folder_path', 'unknown')}"
                )
                return

            # Prepare metadata and rights
            metadata = result["metadata"]
            metas = self.prepare_metadata_from_dict(metadata)
            rights = self.prepare_rights(metadata.get("rights", ""))

            # Create payload
            payload = {
                "status": metadata.get("status", self.config.status),
                "files": file_infos,
                "metas": metas,
                "rights": rights,
            }

            # Create dataset
            api_result = self.create_dataset(payload)

            # Write output
            file_list = ",".join(
                [
                    f"{os.path.basename(f)},{fi['sha1']}"
                    for f, fi in zip(result["files"], file_infos)
                ]
            )

            output_writer.writerow(
                [
                    api_result["payload"]["id"],
                    file_list,
                    metadata.get("title", "unknown"),
                    "OK",
                    json.dumps(api_result),
                ]
            )

        except Exception as e:
            logger.error(
                f"Error processing folder {result.get('folder_path', 'unknown')}: {e}"
            )

            file_list = ",".join([os.path.basename(f) for f in result.get("files", [])])
            output_writer.writerow(
                [
                    "",
                    file_list,
                    result.get("metadata", {}).get("title", "unknown"),
                    "ERROR",
                    str(e),
                ]
            )

    def validate_dataset(
        self, mode: str = None, dataset_path: str = None, folder_config: str = None
    ) -> None:
        """Validate dataset without uploading."""
        mode = mode or self.config.mode
        dataset_path = dataset_path or self.config.dataset_path

        logger.info(f"Validating dataset in {mode} mode...")

        if mode == "csv":
            if not dataset_path:
                raise NakalaValidationError("Dataset path is required for CSV mode")
            self._validate_csv_dataset(dataset_path)
        elif mode == "folder":
            if not folder_config:
                raise NakalaValidationError(
                    "Folder config is required for folder mode. "
                    "Please specify --folder-config with the path to your CSV configuration file. "
                    "Example: --folder-config folder_data_items.csv"
                )
            self._validate_folder_dataset(folder_config)
        else:
            raise NakalaValidationError(f"Unsupported mode: {mode}")

    def _validate_csv_dataset(self, csv_path: str) -> None:
        """Validate CSV dataset structure and files."""
        if not os.path.exists(csv_path):
            raise NakalaFileError(f"CSV file not found: {csv_path}")

        logger.info(f"Validating CSV file: {csv_path}")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            dataset = list(reader)

        if not dataset:
            raise NakalaValidationError("CSV file is empty")

        # Remove header
        if dataset:
            dataset.pop(0)

        total_entries = len(dataset)
        valid_entries = 0

        for num, data in enumerate(dataset, 1):
            logger.info(
                f"Validating entry {num}/{total_entries}: {data[3] if len(data) > 3 else 'unknown'}"
            )

            try:
                # Validate files exist
                filenames = data[0].split(";")
                for filename in filenames:
                    if self.file_processor.validate_file(filename):
                        logger.debug(f"✓ File found: {filename}")
                    else:
                        logger.warning(f"✗ File not found: {filename}")

                # Validate required fields
                if len(data) < 8:
                    logger.warning(f"Entry {num} missing required fields")
                else:
                    logger.debug(f"✓ Entry {num} has required fields")
                    valid_entries += 1

            except Exception as e:
                logger.warning(f"Error validating entry {num}: {e}")

        logger.info(
            f"Validation complete: {valid_entries}/{total_entries} entries valid"
        )

    def _validate_folder_dataset(self, folder_config_path: str) -> None:
        """Validate folder dataset structure and files."""
        logger.info(f"Validating folder config: {folder_config_path}")

        results = self.file_processor.process_folder_structure(folder_config_path)

        if not results:
            logger.warning("No folders found to validate")
            return

        total_folders = len(results)
        valid_folders = 0

        for i, result in enumerate(results, 1):
            folder_path = result.get("folder_path", "unknown")
            logger.info(f"Validating folder {i}/{total_folders}: {folder_path}")

            try:
                valid_files = 0
                for file_path in result["files"]:
                    if self.file_processor.validate_file(file_path):
                        valid_files += 1
                        logger.debug(f"✓ File found: {os.path.basename(file_path)}")
                    else:
                        logger.warning(f"✗ File not found: {file_path}")

                if valid_files > 0:
                    valid_folders += 1
                    logger.debug(f"✓ Folder {folder_path}: {valid_files} valid files")
                else:
                    logger.warning(f"✗ Folder {folder_path}: no valid files")

            except Exception as e:
                logger.warning(f"Error validating folder {folder_path}: {e}")

        logger.info(
            f"Validation complete: {valid_folders}/{total_folders} folders valid"
        )

    def run(
        self, mode: str = None, dataset_path: str = None, folder_config: str = None
    ) -> None:
        """Run the upload process."""
        mode = mode or self.config.mode
        dataset_path = dataset_path or self.config.dataset_path

        if mode == "csv":
            if not dataset_path:
                raise NakalaValidationError("Dataset path is required for CSV mode")
            self.process_csv_dataset(dataset_path)
        elif mode == "folder":
            if not folder_config:
                raise NakalaValidationError(
                    "Folder config is required for folder mode. "
                    "Please specify --folder-config with the path to your CSV configuration file. "
                    "Example: --folder-config folder_data_items.csv"
                )
            self.process_folder_dataset(folder_config)
        else:
            raise NakalaValidationError(f"Unsupported mode: {mode}")


def create_upload_client(
    api_url: str = None, api_key: str = None, **kwargs
) -> NakalaUploadClient:
    """
    Factory function to create upload client with configuration.

    Args:
        api_url: Nakala API URL
        api_key: API key
        **kwargs: Additional configuration options

    Returns:
        Configured NakalaUploadClient
    """
    config_kwargs = {}
    if api_url:
        config_kwargs["api_url"] = api_url
    if api_key:
        config_kwargs["api_key"] = api_key
    config_kwargs.update(kwargs)

    config = NakalaConfig(**config_kwargs)
    return NakalaUploadClient(config)


def main():
    """
    Main CLI entry point for o-nakala-upload (v2.2.0).

    Examples:
        # Folder mode (validated v2.2.0):
        o-nakala-upload --api-key "33170cfe-f53c-550b-5fb6-4814ce981293" \\
            --dataset folder_data_items.csv --mode folder \\
            --folder-config folder_data_items.csv --base-path . \\
            --output upload_results.csv

        # CSV mode:
        o-nakala-upload --api-key YOUR_KEY --dataset data.csv --mode csv

        # Results: Creates 5 datasets with identifiers like 10.34847/nkl.653c7n3i
    """
    parser = argparse.ArgumentParser(
        description="Upload datasets to Nakala",
        epilog="""
Examples:
  # Folder mode - organize files by directory structure:
  o-nakala-upload --api-key YOUR_KEY --dataset folder_data_items.csv \\
      --base-path . --mode folder --folder-config folder_data_items.csv

  # CSV mode - upload individual datasets:
  o-nakala-upload --api-key YOUR_KEY --dataset data.csv --mode csv
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--api-url", default="https://apitest.nakala.fr", help="Nakala API URL"
    )
    parser.add_argument("--api-key", required=True, help="Nakala API key")
    parser.add_argument(
        "--dataset",
        default="sample_dataset/folder_data_items.csv",
        help="Path to dataset CSV file or folder",
    )
    parser.add_argument(
        "--base-path", default="sample_dataset", help="Base directory for files"
    )
    parser.add_argument(
        "--mode",
        choices=["csv", "folder"],
        default="folder",
        help="Upload mode: csv or folder (folder mode requires --folder-config)",
    )
    parser.add_argument(
        "--folder-config",
        help="Path to folder configuration CSV file (REQUIRED for folder mode)",
    )
    parser.add_argument("--output", default="output.csv", help="Output CSV file path")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate dataset without uploading (validation mode)",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_common_logging("nakala_upload.log", log_level)

    try:
        # Create configuration
        config = NakalaConfig(
            api_url=args.api_url,
            api_key=args.api_key,
            base_path=args.base_path,
            dataset_path=args.dataset,
            output_path=args.output,
            mode=args.mode,
        )

        # Create and run client
        client = NakalaUploadClient(config)

        if args.validate_only:
            logger.info("Running in validation mode - no uploads will be performed")
            client.validate_dataset(folder_config=args.folder_config)
            logger.info("Validation completed successfully")
        else:
            client.run(folder_config=args.folder_config)
            logger.info("Upload process completed successfully")

    except Exception as e:
        logger.error(f"Upload process failed: {e}")
        raise


if __name__ == "__main__":
    main()
