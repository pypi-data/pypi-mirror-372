"""
Nakala Collection Client

Handles creating and managing collections in the Nakala API.
"""

import csv
import json
import logging
import argparse
import os
from typing import Dict, Any, List, Optional, TypedDict
import requests
from datetime import datetime

# Import common utilities
from .common import (
    NakalaCommonUtils,
    NakalaConfig,
    CollectionConfig,
    NakalaValidationError,
    NakalaAPIError,
    NakalaFileError,
    setup_common_logging,
)

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class CollectionResult(TypedDict):
    """Type definition for collection creation results."""

    title: str
    status: str
    data_ids: List[str]
    data_count: int
    creation_status: str
    error: str
    id: str
    timestamp: str
    mapping_diagnostics: Optional[Dict[str, Any]]


class MappingDiagnostics(TypedDict):
    """Type definition for folder mapping diagnostics."""

    folder: Dict[str, Dict[str, Any]]
    matched_items: List[str]
    unmatched_folders: List[str]


class NakalaCollectionClient:
    """Main client for Nakala collection operations."""

    def __init__(self, config: NakalaConfig):
        self.config = config
        self.utils = NakalaCommonUtils()
        self.session = requests.Session()

        # Set up session headers
        self.session.headers.update(
            {
                "X-API-KEY": config.api_key,
                "Content-Type": "application/json",
                "User-Agent": "Nakala-Client/2.0",
            }
        )

        # Validate configuration
        if not config.validate_paths():
            raise NakalaValidationError("Invalid configuration paths")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def create_collection(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new collection in Nakala."""
        try:
            # Log payload for debugging
            payload_str = json.dumps(collection_data, ensure_ascii=False, indent=2)
            logger.debug(f"Creating collection with payload: {payload_str}")

            response = requests.post(
                f"{self.config.api_url}/collections",
                headers=self.config.get_headers(),
                data=json.dumps(collection_data),
                timeout=self.config.timeout,
            )

            if response.status_code == 201:
                result = response.json()
                collection_id = result.get("payload", {}).get("id", "Unknown ID")
                logger.info(f"Created collection: {collection_id}")
                return result
            else:
                raise NakalaAPIError(
                    "Failed to create collection",
                    status_code=response.status_code,
                    response_text=response.text,
                )

        except requests.RequestException as e:
            raise NakalaAPIError(f"Network error creating collection: {e}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def add_data_to_collection(self, collection_id: str, data_ids: List[str]) -> bool:
        """Add data items to an existing collection."""
        try:
            response = requests.post(
                f"{self.config.api_url}/collections/{collection_id}/datas",
                headers=self.config.get_headers(),
                data=json.dumps(data_ids),
                timeout=self.config.timeout,
            )

            if response.status_code == 201:
                logger.info(
                    f"Successfully added {len(data_ids)} data items to collection {collection_id}"
                )
                return True
            else:
                raise NakalaAPIError(
                    f"Failed to add data to collection {collection_id}",
                    status_code=response.status_code,
                    response_text=response.text,
                )

        except requests.RequestException as e:
            raise NakalaAPIError(
                f"Network error adding data to collection {collection_id}: {e}"
            )

    def prepare_collection_metadata(
        self, config: CollectionConfig
    ) -> List[Dict[str, Any]]:
        """Prepare metadata for collection creation using common utilities."""
        metadata_dict = {
            "title": config.title,
            "description": config.description,
            "keywords": config.keywords,
        }

        return self.utils.prepare_nakala_metadata(metadata_dict)

    def _create_collection(
        self, metadata: List[Dict[str, Any]], data_ids: List[str]
    ) -> str:
        """Create a collection with metadata and data IDs, return collection identifier."""
        payload = {"metas": metadata, "datas": data_ids, "status": "pending"}

        response = self.session.post(
            f"{self.config.api_url}/collections",
            json=payload,
            timeout=self.config.timeout,
        )

        if response.status_code == 201:
            result = response.json()
            return result.get("payload", {}).get("id", result.get("identifier", ""))
        else:
            raise NakalaAPIError(
                "Collection creation failed",
                status_code=response.status_code,
                response_text=response.text,
            )

    def _validate_collection_config(self, config: Dict[str, Any]) -> None:
        """Validate collection configuration dictionary."""
        required_fields = ["title"]

        for field in required_fields:
            if field not in config:
                raise NakalaValidationError(f"Missing required field: {field}")

        if not config["title"].strip():
            raise NakalaValidationError("Title cannot be empty")

        # Check if data_ids or data sources are provided
        if "data_ids" not in config and "upload_data" not in config:
            raise NakalaValidationError(
                "Either 'data_ids' or 'upload_data' must be provided"
            )

    def create_single_collection(self, config: Dict[str, Any]) -> str:
        """Create a single collection from configuration dictionary."""
        self._validate_collection_config(config)

        # Prepare metadata
        metadata = [
            {
                "propertyUri": "http://nakala.fr/terms#title",
                "value": config["title"],
                "lang": config.get("language", "en"),
                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
            }
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

        # Get data IDs
        data_ids = config.get("data_ids", [])

        # Create collection
        return self._create_collection(metadata, data_ids)

    def _process_upload_output_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Process upload output CSV and return list of data items."""
        if not os.path.exists(csv_path):
            raise NakalaFileError(f"Upload output CSV file not found: {csv_path}")

        results = []
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    results.append(dict(row))
            return results
        except Exception as e:
            raise NakalaFileError(f"Error processing upload output CSV: {e}")

    def _group_data_by_collection(
        self, upload_data: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group upload data by collection name."""
        grouped = {}

        for item in upload_data:
            collection_name = item.get("collection", "Default Collection")
            if collection_name not in grouped:
                grouped[collection_name] = []
            grouped[collection_name].append(item)

        return grouped

    def create_collection_from_uploaded_data(
        self, output_csv: str, collection_config: CollectionConfig
    ) -> Optional[str]:
        """Create a collection from successfully uploaded data items."""
        if not collection_config.validate():
            raise NakalaValidationError("Invalid collection configuration")

        # Read uploaded data from output CSV
        data_ids = []
        try:
            with open(output_csv, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["status"] == "OK" and row["identifier"]:
                        data_ids.append(row["identifier"])

            if not data_ids:
                logger.error("No successfully uploaded data found in output CSV")
                return None

            logger.info(f"Found {len(data_ids)} successfully uploaded data items")

        except Exception as e:
            raise NakalaFileError(f"Error reading output CSV {output_csv}: {e}")

        return self._create_collection_with_data_ids(data_ids, collection_config)

    def create_collection_from_id_list(
        self, data_ids: List[str], collection_config: CollectionConfig
    ) -> Optional[str]:
        """Create a collection from a list of data IDs."""
        if not collection_config.validate():
            raise NakalaValidationError("Invalid collection configuration")

        if not data_ids:
            raise NakalaValidationError("No data IDs provided")

        # Validate data IDs
        invalid_ids = [
            id for id in data_ids if not self.utils.validate_nakala_identifier(id)
        ]
        if invalid_ids:
            logger.warning(f"Invalid Nakala identifiers found: {invalid_ids}")

        return self._create_collection_with_data_ids(data_ids, collection_config)

    def _create_collection_with_data_ids(
        self, data_ids: List[str], collection_config: CollectionConfig
    ) -> Optional[str]:
        """Internal method to create collection with data IDs."""
        # Prepare collection metadata
        metas = self.prepare_collection_metadata(collection_config)

        # Create collection payload
        collection_data = {
            "status": collection_config.status,
            "datas": data_ids,
            "metas": metas,
            "rights": [],  # Empty rights array - only creator will have access initially
        }

        try:
            # Create the collection
            result = self.create_collection(collection_data)
            collection_id = result.get("payload", {}).get("id")

            if collection_id:
                logger.info(
                    f"Collection '{collection_config.title}' created successfully "
                    f"with ID: {collection_id}"
                )
                return collection_id
            else:
                logger.error("Collection creation failed - no ID returned")
                return None

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def create_collections_from_folder_config(
        self, output_csv: str, folder_collections_csv: str
    ) -> List[str]:
        """Create collections based on folder collections configuration."""
        created_collection_ids: List[str] = []
        collection_results: List[CollectionResult] = []

        # Read uploaded data items and map by title
        uploaded_items: Dict[str, str] = {}
        try:
            with open(output_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["status"] == "OK":
                        title = row["title"]
                        uploaded_items[title] = row["identifier"]

            if not uploaded_items:
                logger.error("No successfully uploaded data found in output CSV")
                return created_collection_ids

            logger.info(f"Found {len(uploaded_items)} uploaded data items")

        except Exception as e:
            raise NakalaFileError(f"Error reading output CSV {output_csv}: {e}")

        # Read folder collections configuration and create collections
        try:
            with open(folder_collections_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for collection_config_row in reader:
                    result = self._create_single_collection_with_report(
                        collection_config_row, uploaded_items
                    )
                    collection_results.append(result)

                    if result["creation_status"] == "SUCCESS":
                        created_collection_ids.append(result["id"])

            # Generate CSV report
            self.generate_collection_report(collection_results)

            logger.info(
                f"Created {len(created_collection_ids)} collections from config"
            )

        except Exception as e:
            raise NakalaFileError(
                f"Error reading folder collections CSV {folder_collections_csv}: {e}"
            )

        return created_collection_ids

    def _create_single_collection_with_report(
        self, config_row: Dict[str, str], uploaded_items: Dict[str, str]
    ) -> CollectionResult:
        """Create collection and return detailed result for reporting."""
        result: CollectionResult = {
            "title": config_row.get("title", "Unknown"),
            "status": config_row.get("status", "private"),
            "data_ids": [],
            "data_count": 0,
            "creation_status": "ERROR",
            "error": "",
            "id": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mapping_diagnostics": None,
        }

        try:
            # Validate required fields
            if "data_items" not in config_row:
                result["error"] = "Missing required field: data_items"
                return result

            if "title" not in config_row:
                result["error"] = "Missing required field: title"
                return result

            # Map folder paths to data IDs
            data_item_folders = config_row["data_items"].split("|")
            collection_data_ids: List[str] = []

            logger.info(f"Creating collection: {config_row['title']}")
            logger.info(f"Looking for folder types: {data_item_folders}")
            logger.info(f"Available items: {list(uploaded_items.keys())}")

            # Track mapping diagnostics
            mapping_diagnostics: MappingDiagnostics = {
                "folder": {},
                "matched_items": [],
                "unmatched_folders": [],
            }

            for folder_path in data_item_folders:
                matched_items: List[str] = []
                folder_name = self.utils.extract_folder_name(folder_path)
                mapping_diagnostics["folder"][folder_name] = {
                    "path": folder_path,
                    "matches": [],
                }

                for title, data_id in uploaded_items.items():
                    if self.utils.matches_folder_type(title, [folder_path]):
                        collection_data_ids.append(data_id)
                        matched_items.append(title)
                        mapping_diagnostics["folder"][folder_name]["matches"].append(
                            {"title": title, "id": data_id}
                        )

                if matched_items:
                    logger.info(f"Folder '{folder_path}' matched: {matched_items}")
                    mapping_diagnostics["matched_items"].extend(matched_items)
                else:
                    logger.warning(f"Folder '{folder_path}' matched no items")
                    mapping_diagnostics["unmatched_folders"].append(folder_path)

            # Log detailed mapping diagnostics
            logger.debug("Collection mapping diagnostics:")
            logger.debug(json.dumps(mapping_diagnostics, indent=2))

            if not collection_data_ids:
                result["error"] = (
                    f"No data items found for folders: {data_item_folders}"
                )
                result["mapping_diagnostics"] = mapping_diagnostics
                return result

            result["data_ids"] = collection_data_ids
            result["data_count"] = len(collection_data_ids)
            result["mapping_diagnostics"] = mapping_diagnostics

            # Create collection configuration
            collection_config = CollectionConfig(
                title=config_row["title"],
                description=config_row.get("description", ""),
                keywords=config_row.get("keywords", ""),
                status=config_row.get("status", "private"),
            )

            # Create collection
            collection_id = self._create_collection_with_data_ids(
                collection_data_ids, collection_config
            )

            if collection_id:
                result["id"] = collection_id
                result["creation_status"] = "SUCCESS"
                logger.info(
                    f"Created collection: {config_row['title']} with ID: {collection_id}"
                )
            else:
                result["error"] = "No collection ID returned from API"

        except Exception as e:
            result["error"] = str(e)
            logger.error(
                f"Error creating collection {config_row.get('title', 'Unknown')}: {e}"
            )

        return result

    def generate_collection_report(
        self,
        collection_results: List[CollectionResult],
        output_file: str = "collections_output.csv",
    ) -> None:
        """Generate a CSV report of created collections."""
        try:
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header row
                writer.writerow(
                    [
                        "collection_id",
                        "collection_title",
                        "status",
                        "data_items_count",
                        "data_items_ids",
                        "creation_status",
                        "error_message",
                        "timestamp",
                    ]
                )

                # Data rows
                for result in collection_results:
                    writer.writerow(
                        [
                            result.get("id", ""),
                            result.get("title", ""),
                            result.get("status", ""),
                            result.get("data_count", 0),
                            ";".join(result.get("data_ids", [])),
                            result.get("creation_status", "ERROR"),
                            result.get("error", ""),
                            result.get(
                                "timestamp",
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            ),
                        ]
                    )

            logger.info(f"Collection report saved to: {output_file}")

        except Exception as e:
            logger.error(f"Error generating collection report: {e}")
            raise NakalaFileError(f"Error generating collection report: {e}")

    def validate_collection_data(
        self,
        from_upload_output: str = None,
        from_folder_collections: str = None,
        data_ids: str = None,
    ) -> None:
        """Validate collection data without creating collections."""
        logger.info("Validating collection data...")

        if from_folder_collections:
            self._validate_folder_collections(
                from_upload_output, from_folder_collections
            )
        elif from_upload_output:
            self._validate_upload_output(from_upload_output)
        elif data_ids:
            self._validate_data_ids(data_ids)
        else:
            raise NakalaValidationError("No data source provided for validation")

    def _validate_folder_collections(
        self, upload_output: str, folder_collections: str
    ) -> None:
        """Validate folder collections configuration."""
        # Validate upload output file
        if not os.path.exists(upload_output):
            raise NakalaFileError(f"Upload output file not found: {upload_output}")

        # Validate folder collections file
        if not os.path.exists(folder_collections):
            raise NakalaFileError(
                f"Folder collections file not found: {folder_collections}"
            )

        logger.info(f"✓ Upload output file found: {upload_output}")
        logger.info(f"✓ Folder collections file found: {folder_collections}")

        # Load and validate data
        upload_data = self._load_upload_output(upload_output)
        folder_collections_data = self._load_folder_collections(folder_collections)

        logger.info(f"✓ Upload data loaded: {len(upload_data)} entries")
        logger.info(
            f"✓ Folder collections data loaded: {len(folder_collections_data)} collections"
        )

        # Validate each collection configuration
        valid_collections = 0
        for collection in folder_collections_data:
            try:
                collection_title = collection.get("title", "unknown")
                logger.info(f"Validating collection: {collection_title}")

                # Check required fields
                required_fields = ["title", "description"]
                for field in required_fields:
                    if not collection.get(field):
                        logger.warning(
                            f"Collection '{collection_title}' missing {field}"
                        )
                    else:
                        logger.debug(f"✓ Collection '{collection_title}' has {field}")

                valid_collections += 1

            except Exception as e:
                logger.warning(f"Error validating collection: {e}")

        logger.info(
            f"Validation complete: {valid_collections}/"
            f"{len(folder_collections_data)} collections valid"
        )

    def _load_upload_output(self, upload_output: str) -> List[Dict[str, str]]:
        """Load upload output CSV data."""
        upload_data = []
        try:
            with open(upload_output, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    upload_data.append(row)
        except Exception as e:
            raise NakalaFileError(
                f"Error reading upload output CSV {upload_output}: {e}"
            )
        return upload_data

    def _load_folder_collections(self, folder_collections: str) -> List[Dict[str, str]]:
        """Load folder collections CSV data."""
        collections_data = []
        try:
            with open(folder_collections, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    collections_data.append(row)
        except Exception as e:
            raise NakalaFileError(
                f"Error reading folder collections CSV {folder_collections}: {e}"
            )
        return collections_data

    def _validate_upload_output(self, upload_output: str) -> None:
        """Validate upload output file."""
        if not os.path.exists(upload_output):
            raise NakalaFileError(f"Upload output file not found: {upload_output}")

        logger.info(f"✓ Upload output file found: {upload_output}")

        upload_data = self._load_upload_output(upload_output)
        valid_entries = sum(1 for entry in upload_data if entry.get("status") == "OK")

        logger.info(f"✓ Upload data loaded: {len(upload_data)} entries")
        logger.info(f"✓ Valid upload entries: {valid_entries}/{len(upload_data)}")

    def _validate_data_ids(self, data_ids: str) -> None:
        """Validate data IDs format."""
        ids = [id.strip() for id in data_ids.split(",") if id.strip()]

        if not ids:
            raise NakalaValidationError("No valid data IDs provided")

        logger.info(f"✓ Data IDs provided: {len(ids)} IDs")

        # Validate ID format (Nakala ID format: 10.34847/nkl.xxxxx)
        valid_ids = 0
        for data_id in ids:
            # Check for Nakala ID format: starts with DOI prefix and contains nkl.
            if (data_id.startswith("10.") and "/nkl." in data_id) or (
                len(data_id) > 0 and "-" in data_id
            ):
                valid_ids += 1
                logger.debug(f"✓ Valid ID format: {data_id}")
            else:
                logger.warning(f"✗ Invalid ID format: {data_id}")

        logger.info(f"Validation complete: {valid_ids}/{len(ids)} IDs appear valid")


def create_collection_client(
    api_url: str = None, api_key: str = None, **kwargs
) -> NakalaCollectionClient:
    """
    Factory function to create collection client with configuration.

    Args:
        api_url: Nakala API URL
        api_key: API key
        **kwargs: Additional configuration options

    Returns:
        Configured NakalaCollectionClient
    """
    config_kwargs = {}
    if api_url:
        config_kwargs["api_url"] = api_url
    if api_key:
        config_kwargs["api_key"] = api_key
    config_kwargs.update(kwargs)

    config = NakalaConfig(**config_kwargs)
    return NakalaCollectionClient(config)


def main():
    """
    Main CLI entry point for o-nakala-collection (v2.2.0).

    Examples:
        # Create collections from upload results (validated v2.2.0):
        o-nakala-collection --api-key "33170cfe-f53c-550b-5fb6-4814ce981293" \\
            --from-upload-output upload_results.csv \\
            --from-folder-collections folder_collections.csv \\
            --collection-report collections_output.csv

        # Results: Creates 3 collections with identifiers like 10.34847/nkl.b6f4ygm2
    """
    parser = argparse.ArgumentParser(description="Manage Nakala collections")
    parser.add_argument(
        "--api-url", default="https://apitest.nakala.fr", help="Nakala API URL"
    )
    parser.add_argument("--api-key", required=True, help="Nakala API key")

    # Collection creation options
    parser.add_argument("--title", help="Collection title")
    parser.add_argument("--description", default="", help="Collection description")
    parser.add_argument(
        "--keywords", default="", help="Comma-separated keywords for the collection"
    )
    parser.add_argument(
        "--status",
        choices=["private", "public"],
        default="private",
        help="Collection status (private or public)",
    )

    # Data source options
    parser.add_argument("--from-upload-output", help="Path to upload output CSV file")
    parser.add_argument("--data-ids", help="Comma-separated list of data IDs")
    parser.add_argument(
        "--from-folder-collections", help="Path to folder collections CSV file"
    )

    # Report options
    parser.add_argument(
        "--collection-report",
        default="collections_output.csv",
        help="Filename for collection creation report",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate collection data without creating collections (validation mode)",
    )

    args = parser.parse_args()

    # Validate required arguments
    if args.from_folder_collections and not args.from_upload_output:
        parser.error(
            "--from-upload-output is required when using --from-folder-collections"
        )

    if not any([args.from_folder_collections, args.from_upload_output, args.data_ids]):
        parser.error(
            "One of --from-folder-collections, --from-upload-output, or --data-ids is required"
        )

    # Only require title for single collection creation
    if (
        (args.from_upload_output or args.data_ids)
        and not args.from_folder_collections
        and not args.title
    ):
        parser.error("--title is required when creating a single collection")

    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_common_logging("nakala_collection.log", log_level)

    try:
        # Create configuration
        config = NakalaConfig(api_url=args.api_url, api_key=args.api_key)

        # Create client
        client = NakalaCollectionClient(config)

        if args.validate_only:
            logger.info("Running in validation mode - no collections will be created")
            client.validate_collection_data(
                from_upload_output=args.from_upload_output,
                from_folder_collections=args.from_folder_collections,
                data_ids=args.data_ids,
            )
            logger.info("Validation completed successfully")
            return

        if args.from_folder_collections:
            collection_ids = client.create_collections_from_folder_config(
                output_csv=args.from_upload_output,
                folder_collections_csv=args.from_folder_collections,
            )

            if collection_ids:
                logger.info(f"Successfully created {len(collection_ids)} collections")
                for collection_id in collection_ids:
                    logger.info(f"Collection ID: {collection_id}")
            else:
                logger.error("No collections were created")

        elif args.from_upload_output:
            # Parse keywords
            keywords = ",".join(
                [k.strip() for k in args.keywords.split(",") if k.strip()]
            )

            collection_config = CollectionConfig(
                title=args.title,
                description=args.description,
                keywords=keywords,
                status=args.status,
                data_items=args.from_upload_output,
                source_type="upload_output",
            )

            collection_id = client.create_collection_from_uploaded_data(
                output_csv=args.from_upload_output, collection_config=collection_config
            )

            if collection_id:
                logger.info(f"Successfully created collection with ID: {collection_id}")
            else:
                logger.error("Failed to create collection")

        elif args.data_ids:
            # Parse keywords
            keywords = ",".join(
                [k.strip() for k in args.keywords.split(",") if k.strip()]
            )

            # Parse data IDs
            data_ids = [id.strip() for id in args.data_ids.split(",") if id.strip()]

            collection_config = CollectionConfig(
                title=args.title,
                description=args.description,
                keywords=keywords,
                status=args.status,
                data_items=args.data_ids,
                source_type="ids",
            )

            collection_id = client.create_collection_from_id_list(
                data_ids=data_ids, collection_config=collection_config
            )

            if collection_id:
                logger.info(f"Successfully created collection with ID: {collection_id}")
            else:
                logger.error("Failed to create collection")

        logger.info("Collection management completed successfully")

    except Exception as e:
        logger.error(f"Collection management failed: {e}")
        raise


if __name__ == "__main__":
    main()
