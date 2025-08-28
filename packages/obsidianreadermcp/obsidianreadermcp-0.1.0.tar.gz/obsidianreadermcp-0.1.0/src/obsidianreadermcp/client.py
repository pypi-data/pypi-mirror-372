"""
Obsidian API client for interacting with obsidian-local-rest-api.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from .config import ObsidianConfig
from .exceptions import (
    ObsidianError,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    ValidationError as ObsidianValidationError,
    RateLimitError,
    ServerError,
    TimeoutError,
)
from .models import Note, NoteMetadata, SearchResult, VaultInfo, VaultStats, LinkInfo


logger = logging.getLogger(__name__)


class ObsidianClient:
    """Client for interacting with Obsidian via obsidian-local-rest-api."""

    def __init__(self, config: ObsidianConfig):
        """Initialize the Obsidian client.

        Args:
            config: Configuration object with API settings
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = asyncio.Semaphore(config.rate_limit)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """Establish connection to Obsidian API."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=self.config.headers,
                timeout=self.config.timeout,
            )

            # Test connection
            try:
                await self._make_request("GET", "/")
                logger.info(f"Connected to Obsidian API at {self.config.base_url}")
            except Exception as e:
                await self.disconnect()
                raise ConnectionError(f"Failed to connect to Obsidian API: {e}")

    async def disconnect(self) -> None:
        """Close connection to Obsidian API."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Disconnected from Obsidian API")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Obsidian API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            retries: Number of retries (defaults to config.max_retries)

        Returns:
            Response data as dictionary

        Raises:
            Various ObsidianError subclasses based on response
        """
        if not self._client:
            raise ConnectionError("Client not connected. Call connect() first.")

        if retries is None:
            retries = self.config.max_retries

        async with self._rate_limiter:
            for attempt in range(retries + 1):
                try:
                    # Handle different data types
                    if isinstance(data, str):
                        response = await self._client.request(
                            method=method,
                            url=endpoint,
                            content=data,
                            params=params,
                            headers={"Content-Type": "text/markdown"},
                        )
                    else:
                        response = await self._client.request(
                            method=method,
                            url=endpoint,
                            json=data,
                            params=params,
                        )

                    if response.status_code in (200, 204):
                        if response.status_code == 204 or not response.content:
                            return {}
                        try:
                            return response.json()
                        except Exception:
                            return {}
                    elif response.status_code == 401:
                        raise AuthenticationError("Invalid API key")
                    elif response.status_code == 404:
                        raise NotFoundError("Resource not found")
                    elif response.status_code == 429:
                        if attempt < retries:
                            await asyncio.sleep(2**attempt)
                            continue
                        raise RateLimitError("Rate limit exceeded")
                    elif response.status_code >= 500:
                        if attempt < retries:
                            await asyncio.sleep(2**attempt)
                            continue
                        raise ServerError(f"Server error: {response.status_code}")
                    else:
                        raise ObsidianError(
                            f"Request failed with status {response.status_code}: {response.text}",
                            status_code=response.status_code,
                        )

                except httpx.TimeoutException:
                    if attempt < retries:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise TimeoutError("Request timed out")
                except httpx.RequestError as e:
                    if attempt < retries:
                        await asyncio.sleep(2**attempt)
                        continue
                    raise ConnectionError(f"Request failed: {e}")

    # CRUD Operations

    async def create_note(
        self,
        path: str,
        content: str = "",
        metadata: Optional[NoteMetadata] = None,
    ) -> Note:
        """Create a new note.

        Args:
            path: Note path relative to vault root
            content: Note content
            metadata: Note metadata

        Returns:
            Created note object
        """
        # Ensure path ends with .md
        if not path.endswith(".md"):
            path += ".md"

        # Prepare content with frontmatter if metadata provided
        full_content = content
        if metadata and metadata.frontmatter:
            frontmatter_lines = ["---"]
            for key, value in metadata.frontmatter.items():
                if isinstance(value, list):
                    frontmatter_lines.append(f"{key}:")
                    for item in value:
                        frontmatter_lines.append(f"  - {item}")
                else:
                    frontmatter_lines.append(f"{key}: {value}")
            frontmatter_lines.append("---")
            full_content = "\n".join(frontmatter_lines) + "\n\n" + content

        encoded_path = quote(path, safe="")

        await self._make_request("PUT", f"/vault/{encoded_path}", data=full_content)

        # Return the created note
        return await self.get_note(path)

    async def get_note(self, path: str) -> Note:
        """Get a note by path.

        Args:
            path: Note path relative to vault root

        Returns:
            Note object
        """
        if not path.endswith(".md"):
            path += ".md"

        encoded_path = quote(path, safe="")
        response = await self._make_request("GET", f"/vault/{encoded_path}")

        return Note(
            path=path,
            name=Path(path).stem,
            content=response.get("content", ""),
            metadata=self._parse_metadata(response.get("content", "")),
        )

    async def update_note(
        self,
        path: str,
        content: Optional[str] = None,
        metadata: Optional[NoteMetadata] = None,
    ) -> Note:
        """Update an existing note.

        Args:
            path: Note path relative to vault root
            content: New note content (if None, keeps existing content)
            metadata: New note metadata (if None, keeps existing metadata)

        Returns:
            Updated note object
        """
        if not path.endswith(".md"):
            path += ".md"

        # Get current note if we need to preserve some content
        if content is None or metadata is None:
            current_note = await self.get_note(path)
            if content is None:
                content = current_note.content
            if metadata is None:
                metadata = current_note.metadata

        # Prepare content with frontmatter
        full_content = content
        if metadata and metadata.frontmatter:
            frontmatter_lines = ["---"]
            for key, value in metadata.frontmatter.items():
                if isinstance(value, list):
                    frontmatter_lines.append(f"{key}:")
                    for item in value:
                        frontmatter_lines.append(f"  - {item}")
                else:
                    frontmatter_lines.append(f"{key}: {value}")
            frontmatter_lines.append("---")
            full_content = "\n".join(frontmatter_lines) + "\n\n" + content

        encoded_path = quote(path, safe="")

        await self._make_request("PUT", f"/vault/{encoded_path}", data=full_content)

        # Return the updated note
        return await self.get_note(path)

    async def delete_note(self, path: str) -> bool:
        """Delete a note.

        Args:
            path: Note path relative to vault root

        Returns:
            True if deletion was successful
        """
        if not path.endswith(".md"):
            path += ".md"

        encoded_path = quote(path, safe="")
        await self._make_request("DELETE", f"/vault/{encoded_path}")
        return True

    async def list_notes(self, folder: str = "") -> List[str]:
        """List all notes in the vault or a specific folder.

        Args:
            folder: Folder path to list (empty for root)

        Returns:
            List of note paths
        """
        if folder:
            encoded_folder = quote(folder, safe="")
            endpoint = f"/vault/{encoded_folder}/"
        else:
            endpoint = "/vault/"

        response = await self._make_request("GET", endpoint)
        files = response.get("files", [])

        # Filter for markdown files
        return [f for f in files if f.endswith(".md")]

    async def search_notes(
        self,
        query: str,
        limit: int = 50,
        context_length: int = 100,
    ) -> List[SearchResult]:
        """Search for notes containing the query.

        Args:
            query: Search query
            limit: Maximum number of results
            context_length: Length of context around matches

        Returns:
            List of search results
        """
        params = {
            "query": query,
            "contextLength": context_length,
        }

        response = await self._make_request("POST", "/search/simple/", params=params)
        results = []

        # The response is directly a list of results
        for result in response:
            note = Note(
                path=result["filename"],
                name=Path(result["filename"]).stem,
                content="",  # Search doesn't return full content
            )

            # Extract match contexts
            matches = []
            for match in result.get("matches", []):
                matches.append(match.get("context", ""))

            search_result = SearchResult(
                note=note,
                score=result.get("score"),
                matches=matches,
            )
            results.append(search_result)

        return results[:limit]  # Apply limit

    # Utility methods

    def _parse_metadata(self, content: str) -> NoteMetadata:
        """Parse metadata from note content.

        Args:
            content: Note content with potential frontmatter

        Returns:
            Parsed metadata
        """
        metadata = NoteMetadata()

        if content.startswith("---"):
            try:
                # Find the end of frontmatter
                end_index = content.find("---", 3)
                if end_index != -1:
                    frontmatter_text = content[3:end_index].strip()

                    # Simple YAML parsing (basic implementation)
                    frontmatter = {}
                    for line in frontmatter_text.split("\n"):
                        line = line.strip()
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            value = value.strip()

                            # Handle lists
                            if value.startswith("[") and value.endswith("]"):
                                value = [
                                    item.strip().strip("\"'")
                                    for item in value[1:-1].split(",")
                                ]
                            elif value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]

                            frontmatter[key] = value

                    metadata.frontmatter = frontmatter

                    # Extract common metadata
                    if "tags" in frontmatter:
                        metadata.tags = (
                            frontmatter["tags"]
                            if isinstance(frontmatter["tags"], list)
                            else [frontmatter["tags"]]
                        )
                    if "aliases" in frontmatter:
                        metadata.aliases = (
                            frontmatter["aliases"]
                            if isinstance(frontmatter["aliases"], list)
                            else [frontmatter["aliases"]]
                        )

            except Exception as e:
                logger.warning(f"Failed to parse frontmatter: {e}")

        return metadata

    async def get_vault_info(self) -> VaultInfo:
        """Get information about the vault.

        Returns:
            Vault information
        """
        try:
            # Get basic vault info
            response = await self._make_request("GET", "/")

            # Count notes
            notes = await self.list_notes()
            note_count = len(notes)

            return VaultInfo(
                name=response.get("name", "Unknown"),
                path=response.get("path", ""),
                note_count=note_count,
                total_size=0,  # Would need additional API calls to calculate
                plugins=response.get("plugins", []),
            )
        except Exception as e:
            logger.error(f"Failed to get vault info: {e}")
            return VaultInfo(name="Unknown", path="", note_count=0)

    async def get_tags(self) -> List[str]:
        """Get all tags used in the vault.

        Returns:
            List of unique tags
        """
        try:
            response = await self._make_request("GET", "/tags/")
            return response.get("tags", [])
        except NotFoundError:
            # If tags endpoint doesn't exist, extract from notes
            notes = await self.list_notes()
            tags = set()

            for note_path in notes[:100]:  # Limit to avoid too many requests
                try:
                    note = await self.get_note(note_path)
                    tags.update(note.metadata.tags)
                except Exception:
                    continue

            return list(tags)

    async def get_notes_by_tag(self, tag: str) -> List[Note]:
        """Get all notes with a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of notes with the tag
        """
        notes = []
        note_paths = await self.list_notes()

        for note_path in note_paths:
            try:
                note = await self.get_note(note_path)
                if tag in note.metadata.tags:
                    notes.append(note)
            except Exception as e:
                logger.warning(f"Failed to get note {note_path}: {e}")
                continue

        return notes
