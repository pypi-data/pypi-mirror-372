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
        try:
            if folder:
                encoded_folder = quote(folder, safe="")
                endpoint = f"/vault/{encoded_folder}/"
            else:
                endpoint = "/vault/"

            response = await self._make_request("GET", endpoint)

            # Handle different response formats
            if isinstance(response, list):
                files = response
            elif isinstance(response, dict):
                files = response.get("files", [])
            else:
                logger.warning(f"Unexpected response format for list_notes: {type(response)}")
                return []

            # Filter for markdown files
            markdown_files = [f for f in files if isinstance(f, str) and f.endswith(".md")]

            # If no files found with direct API, try alternative approach
            if not markdown_files and not folder:
                # Try to get files through search with a common character
                try:
                    search_results = await self._search_notes_content("", limit=1000)
                    markdown_files = list(set(result.note.path for result in search_results))
                    logger.info(f"Fallback search found {len(markdown_files)} notes")
                except Exception as e:
                    logger.warning(f"Fallback search failed: {e}")

            return sorted(markdown_files)

        except Exception as e:
            logger.error(f"Failed to list notes in folder '{folder}': {e}")
            # Try fallback method using search
            if not folder:
                try:
                    # Use search as fallback to get all notes
                    search_results = await self._search_notes_content("", limit=1000)
                    return sorted(list(set(result.note.path for result in search_results)))
                except Exception as search_e:
                    logger.error(f"Fallback search also failed: {search_e}")
            return []

    async def list_folders(self) -> List[str]:
        """List all folders in the vault.

        Returns:
            List of folder paths
        """
        try:
            # Get all notes first
            all_notes = await self.list_notes()

            # Extract unique folder paths
            folders = set()
            for note_path in all_notes:
                if '/' in note_path:
                    # Get all parent folder paths
                    parts = note_path.split('/')
                    for i in range(1, len(parts)):
                        folder_path = '/'.join(parts[:i])
                        folders.add(folder_path)

            return sorted(list(folders))

        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
            return []

    async def get_folder_info(self, folder_path: str) -> dict:
        """Get information about a specific folder.

        Args:
            folder_path: Path to the folder

        Returns:
            Dictionary with folder information
        """
        try:
            # Get notes in this folder
            notes = await self.list_notes(folder=folder_path)

            # Get subfolders
            all_folders = await self.list_folders()
            subfolders = [f for f in all_folders if f.startswith(folder_path + '/') and f.count('/') == folder_path.count('/') + 1]

            # Calculate total size
            total_size = 0
            for note_path in notes:
                try:
                    note = await self.get_note(note_path)
                    total_size += len(note.content)
                except Exception as e:
                    logger.warning(f"Failed to get size for {note_path}: {e}")

            return {
                "path": folder_path,
                "name": folder_path.split('/')[-1],
                "note_count": len(notes),
                "subfolder_count": len(subfolders),
                "total_size": total_size,
                "notes": notes,
                "subfolders": subfolders
            }

        except Exception as e:
            logger.error(f"Failed to get folder info for '{folder_path}': {e}")
            return {
                "path": folder_path,
                "name": folder_path.split('/')[-1] if folder_path else "",
                "note_count": 0,
                "subfolder_count": 0,
                "total_size": 0,
                "notes": [],
                "subfolders": []
            }

    async def _search_notes_content(
        self,
        query: str,
        limit: int = 50,
        context_length: int = 100,
    ) -> List[SearchResult]:
        """Internal method for content-only search.

        Args:
            query: Search query
            limit: Maximum number of results
            context_length: Length of context around matches

        Returns:
            List of search results from content search
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

    async def search_notes(
        self,
        query: str,
        limit: int = 50,
        context_length: int = 100,
        include_folders: bool = True,
        search_in_path: bool = True,
    ) -> List[SearchResult]:
        """Search for notes with enhanced folder and path matching.

        Args:
            query: Search query
            limit: Maximum number of results
            context_length: Length of context around matches
            include_folders: Whether to include folder matches
            search_in_path: Whether to search in file paths

        Returns:
            List of search results with content, path, and folder matches
        """
        results = []

        # 1. First get regular content search results
        content_results = await self._search_notes_content(query, limit * 2, context_length)
        results.extend(content_results)

        # 2. If enabled, search in file paths and folder names
        if search_in_path or include_folders:
            try:
                # Get all notes to search in paths
                all_notes = await self.list_notes()
                path_matches = []

                for note_path in all_notes:
                    # Check if query matches in the path
                    if query.lower() in note_path.lower():
                        # Avoid duplicates from content search
                        if not any(r.note.path == note_path for r in results):
                            try:
                                note = await self.get_note(note_path)

                                # Create match context showing the path match
                                path_parts = note_path.split('/')
                                folder_match = ""
                                if len(path_parts) > 1:
                                    folder_match = f"文件夹: {'/'.join(path_parts[:-1])}"

                                matches = [f"路径匹配: {note_path}"]
                                if folder_match:
                                    matches.append(folder_match)

                                search_result = SearchResult(
                                    note=note,
                                    score=0.8,  # High score for path matches
                                    matches=matches,
                                )
                                path_matches.append(search_result)

                            except Exception as e:
                                logger.warning(f"Failed to get note {note_path}: {e}")

                # Add path matches to results
                results.extend(path_matches)

            except Exception as e:
                logger.warning(f"Failed to search in paths: {e}")

        # 3. If enabled, search for folder matches
        if include_folders:
            try:
                # Get unique folders from all notes
                all_notes = await self.list_notes()
                folders = set()

                for note_path in all_notes:
                    path_parts = note_path.split('/')
                    if len(path_parts) > 1:
                        # Add all folder levels
                        for i in range(1, len(path_parts)):
                            folder_path = '/'.join(path_parts[:i])
                            if folder_path and query.lower() in folder_path.lower():
                                folders.add(folder_path)

                # For each matching folder, get some representative notes
                for folder in folders:
                    try:
                        folder_notes = await self.list_notes(folder=folder)
                        if folder_notes:
                            # Get the first note as representative
                            representative_note = await self.get_note(folder_notes[0])

                            matches = [
                                f"文件夹匹配: {folder}",
                                f"包含 {len(folder_notes)} 个笔记",
                                f"示例笔记: {folder_notes[0]}"
                            ]

                            search_result = SearchResult(
                                note=Note(
                                    path=f"{folder}/",
                                    name=folder.split('/')[-1],
                                    content=f"文件夹: {folder}\n包含笔记: {', '.join(folder_notes[:5])}"
                                ),
                                score=0.9,  # Very high score for folder matches
                                matches=matches,
                            )
                            results.append(search_result)

                    except Exception as e:
                        logger.warning(f"Failed to process folder {folder}: {e}")

            except Exception as e:
                logger.warning(f"Failed to search folders: {e}")

        # Sort by score (descending) and apply limit
        results.sort(key=lambda x: x.score or 0, reverse=True)
        return results[:limit]

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
