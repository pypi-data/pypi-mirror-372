"""
Custom exceptions for ObsidianReaderMCP.
"""

from typing import Optional, Any


class ObsidianError(Exception):
    """Base exception for all Obsidian-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class ConnectionError(ObsidianError):
    """Raised when connection to Obsidian API fails."""

    pass


class AuthenticationError(ObsidianError):
    """Raised when API authentication fails."""

    pass


class NotFoundError(ObsidianError):
    """Raised when a requested resource is not found."""

    pass


class ValidationError(ObsidianError):
    """Raised when input validation fails."""

    pass


class RateLimitError(ObsidianError):
    """Raised when API rate limit is exceeded."""

    pass


class ServerError(ObsidianError):
    """Raised when the Obsidian API server encounters an error."""

    pass


class TimeoutError(ObsidianError):
    """Raised when an operation times out."""

    pass
