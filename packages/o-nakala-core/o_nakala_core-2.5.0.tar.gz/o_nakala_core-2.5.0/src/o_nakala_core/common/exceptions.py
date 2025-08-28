"""
Custom exceptions for Nakala client operations.
"""

from typing import Optional, Dict, Any


class NakalaError(Exception):
    """Base exception class for all Nakala client errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class NakalaValidationError(NakalaError):
    """Raised when validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field
        self.value = value
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = value


class MetadataValidationError(NakalaValidationError):
    """Raised when metadata validation fails."""

    def __init__(
        self,
        message: str,
        metadata_field: Optional[str] = None,
        metadata_value: Optional[Any] = None,
    ):
        super().__init__(message, field=metadata_field, value=metadata_value)
        self.metadata_field = metadata_field
        self.metadata_value = metadata_value


class NakalaAPIError(NakalaError):
    """Raised when API request fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        super().__init__(message, error_code="API_ERROR")
        self.status_code = status_code
        self.response_text = response_text
        if status_code:
            self.details["status_code"] = status_code
        if response_text:
            self.details["response_text"] = response_text


class NakalaFileError(NakalaError):
    """Raised when file operations fail."""

    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message, error_code="FILE_ERROR")
        self.file_path = file_path
        if file_path:
            self.details["file_path"] = file_path


class NakalaConfigError(NakalaError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str, config_field: Optional[str] = None):
        super().__init__(message, error_code="CONFIG_ERROR")
        self.config_field = config_field
        if config_field:
            self.details["config_field"] = config_field


class NakalaAuthenticationError(NakalaError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed - check API key"):
        super().__init__(message, error_code="AUTH_ERROR")


class NakalaTimeoutError(NakalaError):
    """Raised when request times out."""

    def __init__(
        self, message: str = "Request timed out", timeout_seconds: Optional[int] = None
    ):
        super().__init__(message, error_code="TIMEOUT_ERROR")
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds
