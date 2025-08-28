"""
Extended functionality for ObsidianReaderMCP.
"""

import asyncio
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict, Counter

from .client import ObsidianClient
from .models import (
    Note,
    NoteMetadata,
    BatchOperation,
    Template,
    BackupInfo,
    LinkInfo,
    VaultStats,
)
from .exceptions import ObsidianError, ValidationError


logger = logging.getLogger(__name__)


class ObsidianExtensions:
    """Extended functionality for Obsidian vault management."""

    def __init__(self, client: ObsidianClient):
        """Initialize extensions with an Obsidian client.

        Args:
            client: Connected ObsidianClient instance
        """
        self.client = client
        self.templates: Dict[str, Template] = {}

    # Batch Operations

    async def batch_create_notes(
        self,
        notes_data: List[Dict[str, Any]],
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """Create multiple notes in batch.

        Args:
            notes_data: List of note data dictionaries
            continue_on_error: Whether to continue if one note fails

        Returns:
            Results summary with success/failure counts
        """
        results = {
            "total": len(notes_data),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for i, note_data in enumerate(notes_data):
            try:
                path = note_data["path"]
                content = note_data.get("content", "")
                metadata = None

                if "tags" in note_data or "frontmatter" in note_data:
                    metadata = NoteMetadata(
                        tags=note_data.get("tags", []),
                        frontmatter=note_data.get("frontmatter", {}),
                    )

                await self.client.create_note(path, content, metadata)
                results["successful"] += 1

            except Exception as e:
                results["failed"] += 1
                error_info = {
                    "index": i,
                    "path": note_data.get("path", "unknown"),
                    "error": str(e),
                }
                results["errors"].append(error_info)

                if not continue_on_error:
                    break

        return results

    async def batch_update_notes(
        self,
        updates: List[Dict[str, Any]],
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """Update multiple notes in batch.

        Args:
            updates: List of update dictionaries with path and changes
            continue_on_error: Whether to continue if one update fails

        Returns:
            Results summary with success/failure counts
        """
        results = {
            "total": len(updates),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for i, update_data in enumerate(updates):
            try:
                path = update_data["path"]
                content = update_data.get("content")
                metadata = None

                if "tags" in update_data or "frontmatter" in update_data:
                    metadata = NoteMetadata(
                        tags=update_data.get("tags"),
                        frontmatter=update_data.get("frontmatter"),
                    )

                await self.client.update_note(path, content, metadata)
                results["successful"] += 1

            except Exception as e:
                results["failed"] += 1
                error_info = {
                    "index": i,
                    "path": update_data.get("path", "unknown"),
                    "error": str(e),
                }
                results["errors"].append(error_info)

                if not continue_on_error:
                    break

        return results

    async def batch_delete_notes(
        self,
        paths: List[str],
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        """Delete multiple notes in batch.

        Args:
            paths: List of note paths to delete
            continue_on_error: Whether to continue if one deletion fails

        Returns:
            Results summary with success/failure counts
        """
        results = {
            "total": len(paths),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for i, path in enumerate(paths):
            try:
                await self.client.delete_note(path)
                results["successful"] += 1

            except Exception as e:
                results["failed"] += 1
                error_info = {
                    "index": i,
                    "path": path,
                    "error": str(e),
                }
                results["errors"].append(error_info)

                if not continue_on_error:
                    break

        return results

    # Template System

    def create_template(
        self,
        name: str,
        content: str,
        variables: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Template:
        """Create a new note template.

        Args:
            name: Template name
            content: Template content with variables as {{variable_name}}
            variables: List of variable names
            description: Template description

        Returns:
            Created template
        """
        if variables is None:
            # Extract variables from content
            import re

            variables = re.findall(r"\{\{(\w+)\}\}", content)

        template = Template(
            name=name,
            content=content,
            variables=variables,
            description=description,
        )

        self.templates[name] = template
        return template

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            Template if found, None otherwise
        """
        return self.templates.get(name)

    def list_templates(self) -> List[Template]:
        """List all available templates.

        Returns:
            List of templates
        """
        return list(self.templates.values())

    async def create_note_from_template(
        self,
        template_name: str,
        path: str,
        variables: Optional[Dict[str, str]] = None,
        metadata: Optional[NoteMetadata] = None,
    ) -> Note:
        """Create a note from a template.

        Args:
            template_name: Name of the template to use
            path: Path for the new note
            variables: Values for template variables
            metadata: Additional metadata for the note

        Returns:
            Created note

        Raises:
            ValidationError: If template not found or variables missing
        """
        template = self.get_template(template_name)
        if not template:
            raise ValidationError(f"Template '{template_name}' not found")

        if variables is None:
            variables = {}

        # Check for missing variables
        missing_vars = set(template.variables) - set(variables.keys())
        if missing_vars:
            raise ValidationError(f"Missing template variables: {missing_vars}")

        # Replace variables in content
        content = template.content
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{{{var_name}}}}}", var_value)

        # Create the note
        return await self.client.create_note(path, content, metadata)

    # Backup and Version Management

    async def create_backup(
        self,
        backup_path: str,
        include_attachments: bool = True,
    ) -> BackupInfo:
        """Create a backup of the vault.

        Args:
            backup_path: Path where to save the backup
            include_attachments: Whether to include attachment files

        Returns:
            Backup information
        """
        import hashlib

        timestamp = datetime.now()
        note_paths = await self.client.list_notes()

        # Create backup directory
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_file = (
            backup_dir / f"vault_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip"
        )

        total_size = 0
        checksum_data = []

        with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for note_path in note_paths:
                try:
                    note = await self.client.get_note(note_path)
                    content_bytes = note.content.encode("utf-8")

                    zipf.writestr(note_path, content_bytes)
                    total_size += len(content_bytes)
                    checksum_data.append(content_bytes)

                except Exception as e:
                    logger.warning(f"Failed to backup note {note_path}: {e}")

        # Calculate checksum
        hasher = hashlib.sha256()
        for data in checksum_data:
            hasher.update(data)
        checksum = hasher.hexdigest()

        return BackupInfo(
            timestamp=timestamp,
            path=str(backup_file),
            size=backup_file.stat().st_size,
            note_count=len(note_paths),
            checksum=checksum,
        )

    # Link Analysis

    async def analyze_links(self) -> List[LinkInfo]:
        """Analyze links between notes.

        Returns:
            List of link information
        """
        import re

        note_paths = await self.client.list_notes()
        links = []

        # Patterns for different link types
        wikilink_pattern = r"\[\[([^\]]+)\]\]"
        markdown_link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        for note_path in note_paths:
            try:
                note = await self.client.get_note(note_path)
                content = note.content

                # Find wikilinks
                for match in re.finditer(wikilink_pattern, content):
                    target = match.group(1)
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(content), match.end() + 50)
                    context = content[context_start:context_end]

                    links.append(
                        LinkInfo(
                            source=note_path,
                            target=target,
                            link_type="wikilink",
                            context=context,
                        )
                    )

                # Find markdown links
                for match in re.finditer(markdown_link_pattern, content):
                    target = match.group(2)
                    if target.endswith(".md"):  # Only internal links
                        context_start = max(0, match.start() - 50)
                        context_end = min(len(content), match.end() + 50)
                        context = content[context_start:context_end]

                        links.append(
                            LinkInfo(
                                source=note_path,
                                target=target,
                                link_type="markdown",
                                context=context,
                            )
                        )

            except Exception as e:
                logger.warning(f"Failed to analyze links in {note_path}: {e}")

        return links

    async def find_orphaned_notes(self) -> List[str]:
        """Find notes that have no incoming links.

        Returns:
            List of orphaned note paths
        """
        links = await self.analyze_links()
        note_paths = set(await self.client.list_notes())

        # Get all notes that are targets of links
        linked_notes = set()
        for link in links:
            target = link.target
            if not target.endswith(".md"):
                target += ".md"
            linked_notes.add(target)

        # Find orphaned notes
        orphaned = note_paths - linked_notes
        return list(orphaned)

    async def find_broken_links(self) -> List[LinkInfo]:
        """Find links that point to non-existent notes.

        Returns:
            List of broken links
        """
        links = await self.analyze_links()
        note_paths = set(await self.client.list_notes())

        broken_links = []
        for link in links:
            target = link.target
            if not target.endswith(".md"):
                target += ".md"

            if target not in note_paths:
                broken_links.append(link)

        return broken_links

    # Statistics and Analysis

    async def generate_vault_stats(self) -> VaultStats:
        """Generate comprehensive vault statistics.

        Returns:
            Vault statistics
        """
        note_paths = await self.client.list_notes()
        links = await self.analyze_links()

        total_notes = len(note_paths)
        total_words = 0
        total_characters = 0
        tag_counter = Counter()
        creation_dates = defaultdict(int)
        link_counter = defaultdict(int)

        for note_path in note_paths:
            try:
                note = await self.client.get_note(note_path)
                content = note.content

                # Count words and characters
                words = len(content.split())
                total_words += words
                total_characters += len(content)

                # Count tags
                for tag in note.metadata.tags:
                    tag_counter[tag] += 1

                # Extract creation date (if available in frontmatter)
                if note.metadata.frontmatter.get("created"):
                    try:
                        created_str = str(note.metadata.frontmatter["created"])
                        if created_str:
                            # Try to parse date (basic implementation)
                            date_part = (
                                created_str.split("T")[0]
                                if "T" in created_str
                                else created_str.split(" ")[0]
                            )
                            if len(date_part) >= 7:  # YYYY-MM format at minimum
                                month_key = date_part[:7]  # YYYY-MM
                                creation_dates[month_key] += 1
                    except Exception:
                        pass

            except Exception as e:
                logger.warning(f"Failed to analyze note {note_path}: {e}")

        # Count links per note
        for link in links:
            link_counter[link.source] += 1

        # Find most linked notes (notes that are targets of many links)
        target_counter = Counter()
        for link in links:
            target_counter[link.target] += 1

        most_linked = [
            {"note": note, "link_count": count}
            for note, count in target_counter.most_common(10)
        ]

        # Find orphaned notes
        orphaned_notes = await self.find_orphaned_notes()

        return VaultStats(
            total_notes=total_notes,
            total_words=total_words,
            total_characters=total_characters,
            total_links=len(links),
            orphaned_notes=len(orphaned_notes),
            most_linked_notes=most_linked,
            tag_distribution=dict(tag_counter),
            creation_timeline=dict(creation_dates),
        )

    # Advanced Search

    async def search_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        date_field: str = "created",
    ) -> List[Note]:
        """Search notes by date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            date_field: Field to search in ("created" or "modified")

        Returns:
            List of notes in the date range
        """
        note_paths = await self.client.list_notes()
        matching_notes = []

        for note_path in note_paths:
            try:
                note = await self.client.get_note(note_path)

                # Get date from frontmatter
                date_value = note.metadata.frontmatter.get(date_field)
                if not date_value:
                    continue

                # Parse date (basic implementation)
                try:
                    if isinstance(date_value, str):
                        # Try to parse ISO format
                        note_date = datetime.fromisoformat(
                            date_value.replace("Z", "+00:00")
                        )
                    elif isinstance(date_value, datetime):
                        note_date = date_value
                    else:
                        continue

                    # Check if in range
                    if start_date and note_date < start_date:
                        continue
                    if end_date and note_date > end_date:
                        continue

                    matching_notes.append(note)

                except Exception:
                    continue

            except Exception as e:
                logger.warning(f"Failed to check date for note {note_path}: {e}")

        return matching_notes

    async def search_by_word_count(
        self,
        min_words: Optional[int] = None,
        max_words: Optional[int] = None,
    ) -> List[Note]:
        """Search notes by word count.

        Args:
            min_words: Minimum word count
            max_words: Maximum word count

        Returns:
            List of notes matching word count criteria
        """
        note_paths = await self.client.list_notes()
        matching_notes = []

        for note_path in note_paths:
            try:
                note = await self.client.get_note(note_path)
                word_count = len(note.content.split())

                if min_words and word_count < min_words:
                    continue
                if max_words and word_count > max_words:
                    continue

                matching_notes.append(note)

            except Exception as e:
                logger.warning(f"Failed to count words for note {note_path}: {e}")

        return matching_notes
