"""
Configuration management for Nakala client operations.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class NakalaConfig:
    """Configuration class for Nakala API operations."""

    # API Configuration
    api_url: str = "https://apitest.nakala.fr"
    api_key: Optional[str] = None

    # File and Directory Paths
    base_path: str = "."
    dataset_path: str = ""
    output_path: str = "output.csv"

    # Processing Options
    mode: str = "folder"  # "csv" or "folder"
    status: str = "pending"  # "pending" or "published"

    # Default metadata
    default_license: str = "CC-BY-4.0"
    default_language: str = "fr"
    default_rights: str = "de0f2a9b-a198-48a4-8074-db5120187a16,ROLE_READER"

    # Valid group IDs for rights management
    valid_group_ids: list = field(
        default_factory=lambda: ["de0f2a9b-a198-48a4-8074-db5120187a16"]
    )

    # Request settings
    max_retries: int = 5
    retry_delay: int = 4
    timeout: int = 600  # Increased to 10 minutes for dataset creation
    upload_timeout: int = 300  # Separate timeout for file uploads

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        # Load from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("NAKALA_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key must be provided either in config or NAKALA_API_KEY environment variable"
            )

        # Ensure base_path is absolute
        self.base_path = str(Path(self.base_path).resolve())

        logger.debug(f"Initialized NakalaConfig with API URL: {self.api_url}")

    @classmethod
    def from_env(cls) -> "NakalaConfig":
        """
        Create configuration from environment variables.

        Returns:
            NakalaConfig instance
        """
        kwargs = {}

        # Map environment variables to config fields
        env_mapping = {
            "NAKALA_API_KEY": "api_key",
            "NAKALA_API_URL": "api_url",
            "NAKALA_BASE_PATH": "base_path",
            "NAKALA_DEFAULT_LICENSE": "default_license",
            "NAKALA_DEFAULT_LANGUAGE": "default_language",
            "NAKALA_DEFAULT_RIGHTS": "default_rights",
        }

        for env_key, config_key in env_mapping.items():
            env_value = os.getenv(env_key)
            if env_value:
                kwargs[config_key] = env_value

        return cls(**kwargs)

    def get_headers(self) -> Dict[str, str]:
        """Get standard HTTP headers for API requests."""
        return {"Content-Type": "application/json", "X-API-KEY": self.api_key}

    def get_upload_headers(self) -> Dict[str, str]:
        """Get headers for file upload requests."""
        return {"X-API-KEY": self.api_key}

    def validate_paths(self) -> bool:
        """
        Validate that required paths exist.

        Returns:
            True if all paths are valid
        """
        if not os.path.exists(self.base_path):
            logger.error(f"Base path does not exist: {self.base_path}")
            return False

        if self.dataset_path and not os.path.exists(self.dataset_path):
            logger.error(f"Dataset path does not exist: {self.dataset_path}")
            return False

        return True

    def validate(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if configuration is valid
        """
        if not self.api_key:
            logger.error("API key is required")
            return False

        if not self.api_url:
            logger.error("API URL is required")
            return False

        return self.validate_paths()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_url": self.api_url,
            "base_path": self.base_path,
            "dataset_path": self.dataset_path,
            "output_path": self.output_path,
            "mode": self.mode,
            "status": self.status,
            "default_license": self.default_license,
            "default_language": self.default_language,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
        }


@dataclass
class DatasetConfig:
    """Configuration for dataset processing."""

    # Dataset information
    title: str = ""
    description: str = ""
    keywords: str = ""
    creator: str = ""
    contributor: str = ""

    # Processing options
    file_pattern: str = "*"
    include_subdirs: bool = True
    validate_files: bool = True

    # Metadata options
    auto_detect_type: bool = True
    default_type: str = "http://purl.org/coar/resource_type/c_c513"  # Other

    def validate(self) -> bool:
        """Validate dataset configuration."""
        if not self.title:
            logger.error("Dataset title is required")
            return False

        return True


@dataclass
class CollectionConfig:
    """Configuration for collection creation."""

    # Collection information
    title: str = ""
    description: str = ""
    keywords: str = ""
    status: str = "private"

    # Data source configuration
    data_items: str = ""  # Folder patterns or data IDs
    source_type: str = "folders"  # "folders", "ids", or "upload_output"

    # Processing options
    validate_items: bool = True

    def validate(self) -> bool:
        """Validate collection configuration."""
        if not self.title:
            logger.error("Collection title is required")
            return False

        if not self.data_items:
            logger.error("Data items specification is required")
            return False

        if self.status not in ["private", "public"]:
            logger.error(f"Invalid status: {self.status}")
            return False

        return True
