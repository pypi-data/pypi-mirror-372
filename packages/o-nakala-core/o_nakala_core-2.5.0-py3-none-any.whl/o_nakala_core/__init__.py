"""
Nakala Client Package

A comprehensive Python client for interacting with the Nakala API.
Provides tools for uploading, managing collections, searching, and curating data.
"""

__version__ = "2.5.0"
__author__ = "xy-liao"

from .common.utils import NakalaCommonUtils, NakalaPathResolver
from .common.config import NakalaConfig
from .common.exceptions import NakalaError, NakalaValidationError, NakalaAPIError

# Import main client classes
from .user_info import NakalaUserInfoClient
from .curator import NakalaCuratorClient, CuratorConfig, BatchModificationResult

__all__ = [
    "NakalaCommonUtils",
    "NakalaPathResolver",
    "NakalaConfig",
    "NakalaError",
    "NakalaValidationError",
    "NakalaAPIError",
    "NakalaUserInfoClient",
    "NakalaCuratorClient",
    "CuratorConfig",
    "BatchModificationResult",
]
