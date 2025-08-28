"""
ObsidianReaderMCP - A comprehensive Python MCP server for managing Obsidian vaults.

This package provides a complete interface to interact with Obsidian vaults
through the obsidian-local-rest-api plugin.
"""

__version__ = "0.1.0"
__author__ = "ObsidianReaderMCP Team"
__email__ = "contact@obsidianreadermcp.com"

from .client import ObsidianClient
from .models import Note, NoteMetadata, SearchResult, VaultInfo
from .exceptions import (
    ObsidianError,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "ObsidianClient",
    "Note",
    "NoteMetadata",
    "SearchResult",
    "VaultInfo",
    "ObsidianError",
    "ConnectionError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
]
