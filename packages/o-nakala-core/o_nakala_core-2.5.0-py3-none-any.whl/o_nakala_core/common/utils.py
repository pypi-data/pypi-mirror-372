"""
Common utilities for Nakala client operations.
Provides shared functionality across all Nakala client modules.
"""

import os
import mimetypes
import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


# Standalone utility functions for backward compatibility
def prepare_metadata(metadata_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Standalone function to prepare metadata from dictionary.
    Wrapper around NakalaCommonUtils.prepare_nakala_metadata for backward compatibility.
    """
    utils = NakalaCommonUtils()
    return utils.prepare_nakala_metadata(metadata_dict)


def parse_multilingual_field(value: str) -> List[Tuple[Optional[str], str]]:
    """
    Standalone function to parse multilingual field.
    Wrapper around NakalaCommonUtils.parse_multilingual_field for backward compatibility.
    """
    return NakalaCommonUtils.parse_multilingual_field(value)


class NakalaCommonUtils:
    """Shared utilities for Nakala client operations."""

    # Standard Nakala property URIs
    PROPERTY_URIS = {
        "type": "http://nakala.fr/terms#type",
        "title": "http://nakala.fr/terms#title",
        "creator": "http://nakala.fr/terms#creator",
        "created": "http://nakala.fr/terms#created",
        "license": "http://nakala.fr/terms#license",
        "description": "http://purl.org/dc/terms/description",
        "subject": "http://purl.org/dc/terms/subject",
        "contributor": "http://purl.org/dc/terms/contributor",
        "publisher": "http://purl.org/dc/terms/publisher",
        "rights": "http://purl.org/dc/terms/rights",
        "coverage": "http://purl.org/dc/terms/coverage",
        "relation": "http://purl.org/dc/terms/relation",
        "source": "http://purl.org/dc/terms/source",
        "language": "http://purl.org/dc/terms/language",
        "format": "http://purl.org/dc/terms/format",
        "identifier": "http://purl.org/dc/terms/identifier",
        # Missing fields used in sample dataset
        "alternative": "http://purl.org/dc/terms/alternative",
        "temporal": "http://purl.org/dc/terms/temporal",
        "spatial": "http://purl.org/dc/terms/spatial",
        "accessRights": "http://purl.org/dc/terms/accessRights",
        # Common aliases for better CSV compatibility
        "keywords": "http://purl.org/dc/terms/subject",
        "date": "http://nakala.fr/terms#created",
    }

    # Folder type mappings for automatic categorization
    FOLDER_TYPE_MAPPINGS = {
        "code": ["code", "fichiers de code", "scripts", "programmes", "src", "source"],
        "data": ["data", "données", "dataset", "fichiers de données", "csv", "json"],
        "documents": [
            "documents",
            "documentation",
            "research documents",
            "papers",
            "docs",
        ],
        "images": [
            "images",
            "collection d'images",
            "photos",
            "visualizations",
            "img",
            "pictures",
        ],
        "presentations": [
            "presentations",
            "matériaux de présentation",
            "slides",
            "diapositives",
            "ppt",
        ],
        "audio": ["audio", "son", "music", "musique", "sound"],
        "video": ["video", "vidéo", "movies", "films", "mov"],
    }

    @staticmethod
    def parse_multilingual_field(value: str) -> List[Tuple[Optional[str], str]]:
        """
        Parse a multilingual field like 'fr:Texte FR|en:Text EN' into list of (lang, value) tuples.

        Args:
            value: String in format "lang:text|lang:text" or plain text

        Returns:
            List of (language, text) tuples
        """
        if not value or not value.strip():
            return []

        result: List[Tuple[Optional[str], str]] = []
        for part in value.split("|"):
            part = part.strip()
            if (
                ":" in part and len(part.split(":", 1)[0]) <= 3
            ):  # Language codes are typically 2-3 chars
                lang, text = part.split(":", 1)
                result.append((lang.strip(), text.strip()))
            else:
                # Fallback: no language specified or not a language pattern
                result.append((None, part))

        return result

    @staticmethod
    def prepare_nakala_metadata(
        config: Dict[str, str], field_mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare metadata for Nakala API from configuration dictionary.

        Args:
            config: Configuration dictionary with metadata fields
            field_mapping: Optional custom mapping of config keys to Nakala property URIs

        Returns:
            List of metadata dictionaries for Nakala API
        """
        if field_mapping is None:
            field_mapping = {
                "title": NakalaCommonUtils.PROPERTY_URIS["title"],
                "description": NakalaCommonUtils.PROPERTY_URIS["description"],
                "keywords": NakalaCommonUtils.PROPERTY_URIS["subject"],
                "creator": NakalaCommonUtils.PROPERTY_URIS["creator"],
                "contributor": NakalaCommonUtils.PROPERTY_URIS["contributor"],
                "publisher": NakalaCommonUtils.PROPERTY_URIS["publisher"],
                "date": NakalaCommonUtils.PROPERTY_URIS["created"],
                "rights": NakalaCommonUtils.PROPERTY_URIS["rights"],
                "coverage": NakalaCommonUtils.PROPERTY_URIS["coverage"],
                "relation": NakalaCommonUtils.PROPERTY_URIS["relation"],
                "source": NakalaCommonUtils.PROPERTY_URIS["source"],
                "type": NakalaCommonUtils.PROPERTY_URIS["type"],
                "license": NakalaCommonUtils.PROPERTY_URIS["license"],
                # Add missing fields used in sample dataset
                "alternative": NakalaCommonUtils.PROPERTY_URIS["alternative"],
                "temporal": NakalaCommonUtils.PROPERTY_URIS["temporal"],
                "spatial": NakalaCommonUtils.PROPERTY_URIS["spatial"],
                "accessRights": NakalaCommonUtils.PROPERTY_URIS["accessRights"],
                # Common additional fields
                "language": NakalaCommonUtils.PROPERTY_URIS["language"],
                "format": NakalaCommonUtils.PROPERTY_URIS["format"],
                "identifier": NakalaCommonUtils.PROPERTY_URIS["identifier"],
            }

        metas = []

        # Collect creator/contributor arrays separately to handle them as single metadata entries
        creator_arrays: Dict[str, List[str]] = {}

        for field_name, property_uri in field_mapping.items():
            if field_name not in config or not config[field_name]:
                continue

            # Handle special fields first
            if field_name == "type":
                metas.append(
                    {
                        "value": config[field_name],
                        "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI",
                        "propertyUri": property_uri,
                    }
                )
                continue

            # Handle multilingual fields
            parsed_values = NakalaCommonUtils.parse_multilingual_field(
                config[field_name]
            )

            for lang, value in parsed_values:
                if field_name == "keywords":
                    # Split keywords by semicolon
                    for keyword in value.split(";"):
                        keyword = keyword.strip()
                        if keyword:
                            metas.append(
                                {
                                    "value": keyword,
                                    "lang": lang if lang else "und",
                                    "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                                    "propertyUri": property_uri,
                                }
                            )
                elif field_name in ["creator", "contributor"]:
                    # Collect person data for array-based fields
                    if property_uri not in creator_arrays:
                        creator_arrays[property_uri] = []

                    for person in value.split(";"):
                        person = person.strip()
                        if person and "," in person:
                            surname, givenname = person.split(",", 1)
                            person_data = {
                                "givenname": givenname.strip(),
                                "surname": surname.strip(),
                            }
                            creator_arrays[property_uri].append(person_data)
                        elif person:
                            # For simple string names, still create person objects
                            creator_arrays[property_uri].append({"name": person})
                elif field_name in ["date", "created"]:
                    # Handle date fields with proper date type
                    metas.append(
                        {
                            "value": value,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#date",
                            "propertyUri": property_uri,
                        }
                    )
                elif field_name in ["license", "accessRights"]:
                    # Handle fields that cannot have language attributes
                    metas.append(
                        {
                            "value": value,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            "propertyUri": property_uri,
                        }
                    )
                elif field_name in ["identifier"]:
                    # Handle URI-type fields
                    metas.append(
                        {
                            "value": value,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI",
                            "propertyUri": property_uri,
                        }
                    )
                else:
                    # Handle regular text fields with language
                    metas.append(
                        {
                            "value": value,
                            "lang": lang if lang else "und",
                            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            "propertyUri": property_uri,
                        }
                    )

        # Add creator/contributor arrays as single metadata entries
        for property_uri, person_array in creator_arrays.items():
            if person_array:  # Only add if there are actual creators/contributors
                metas.append({"value": person_array, "propertyUri": property_uri})

        return metas

    @staticmethod
    def normalize_path(path: str, base_path: Optional[str] = None) -> str:
        """
        Normalize path for consistent handling across scripts.

        Args:
            path: Path to normalize
            base_path: Optional base path for relative resolution

        Returns:
            Normalized path string
        """
        if base_path:
            path = os.path.join(base_path, path)

        return os.path.normpath(path)

    @staticmethod
    def extract_folder_name(path: str) -> str:
        """
        Extract the folder name from a path for matching purposes.

        Args:
            path: File or folder path

        Returns:
            Folder name for matching
        """
        # Handle both file paths and folder paths
        if os.path.isfile(path):
            folder_path = os.path.dirname(path)
        else:
            folder_path = path

        return os.path.basename(folder_path.rstrip("/\\"))

    @staticmethod
    def matches_folder_type(item_title: str, folder_patterns: List[str]) -> bool:
        """
        Check if an item title matches any of the folder patterns.

        Args:
            item_title: Title of the data item
            folder_patterns: List of folder patterns to match against

        Returns:
            True if title matches any pattern
        """
        title_lower = item_title.lower()

        for pattern in folder_patterns:
            folder_name = NakalaCommonUtils.extract_folder_name(pattern)

            # Direct match
            if folder_name in title_lower:
                return True

            # Pattern-based match using mappings
            if folder_name in NakalaCommonUtils.FOLDER_TYPE_MAPPINGS:
                keywords = NakalaCommonUtils.FOLDER_TYPE_MAPPINGS[folder_name]
                if any(keyword in title_lower for keyword in keywords):
                    return True

        return False

    @staticmethod
    def validate_nakala_identifier(identifier: str) -> bool:
        """
        Validate a Nakala identifier format.

        Args:
            identifier: Identifier to validate

        Returns:
            True if identifier is valid
        """
        pattern = r"^((10\.34847/nkl\.|11280/)[a-z0-9]{8})(\.v([0-9]+))?$"
        return bool(re.match(pattern, identifier))

    @staticmethod
    def prepare_rights_list(
        rights_string: str, valid_group_ids: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare rights list from string format.

        Args:
            rights_string: Rights in format "group_id,role;group_id,role"
            valid_group_ids: Optional list of valid group IDs to filter against

        Returns:
            List of rights dictionaries
        """
        if valid_group_ids is None:
            valid_group_ids = ["de0f2a9b-a198-48a4-8074-db5120187a16"]

        rights: List[Dict[str, str]] = []
        if not rights_string:
            return rights

        for right_entry in rights_string.split(";"):
            right_entry = right_entry.strip()
            if "," in right_entry:
                group_id, role = right_entry.split(",", 1)
                group_id = group_id.strip()
                role = role.strip()

                if group_id in valid_group_ids:
                    rights.append({"id": group_id, "role": role})
                else:
                    logger.warning(f"Invalid group ID: {group_id}")

        return rights

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """
        Detect file type based on extension and MIME type.

        Args:
            file_path: Path to the file

        Returns:
            Detected file type category
        """
        ext = os.path.splitext(file_path)[1].lower()
        mime_type, _ = mimetypes.guess_type(file_path)

        # Extension-based detection
        extension_mapping = {
            "code": [
                ".py",
                ".js",
                ".java",
                ".cpp",
                ".h",
                ".cs",
                ".php",
                ".r",
                ".sql",
                ".sh",
            ],
            "data": [".csv", ".json", ".xml", ".xlsx", ".xls", ".db", ".sqlite"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp", ".svg"],
            "presentations": [".ppt", ".pptx", ".key", ".odp"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"],
        }

        for file_type, extensions in extension_mapping.items():
            if ext in extensions:
                return file_type

        # MIME type fallback
        if mime_type:
            if mime_type.startswith("image/"):
                return "images"
            elif mime_type.startswith("text/"):
                return "documents"
            elif mime_type.startswith("audio/"):
                return "audio"
            elif mime_type.startswith("video/"):
                return "video"
            elif mime_type == "application/pdf":
                return "documents"

        return "other"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human readable size string
        """
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math

        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"


class NakalaPathResolver:
    """Handle path resolution consistently across scripts."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        logger.debug(f"Initialized path resolver with base: {self.base_path}")

    def get_relative_path(self, file_path: str) -> str:
        """Get relative path from base directory."""
        try:
            resolved_path = Path(file_path).resolve()
            return str(resolved_path.relative_to(self.base_path))
        except ValueError:
            # Path is not relative to base_path
            logger.warning(f"Path {file_path} is not relative to base {self.base_path}")
            return str(file_path)

    def get_absolute_path(self, relative_path: str) -> str:
        """Get absolute path from relative path."""
        return str(self.base_path / relative_path)

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        if os.path.isabs(path):
            return Path(path).exists()
        else:
            return (self.base_path / path).exists()

    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        if os.path.isabs(path):
            return Path(path).is_file()
        else:
            return (self.base_path / path).is_file()

    def list_files(self, pattern: str = "*") -> List[str]:
        """List files matching pattern in base directory."""
        return [
            str(p.relative_to(self.base_path))
            for p in self.base_path.glob(pattern)
            if p.is_file()
        ]


def setup_common_logging(
    log_file: str = "o_nakala_core.log",
    level: int = logging.INFO,
    include_console: bool = True,
) -> logging.Logger:
    """
    Setup common logging configuration for all Nakala client modules.

    Args:
        log_file: Log file name
        level: Logging level
        include_console: Whether to include console output

    Returns:
        Configured logger instance
    """
    handlers: List[logging.Handler] = [logging.FileHandler(log_file)]
    if include_console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    return logging.getLogger("o_nakala_core")
