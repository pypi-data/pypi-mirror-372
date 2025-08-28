"""
Data models for ObsidianReaderMCP.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field, field_validator


class NoteMetadata(BaseModel):
    """Metadata for an Obsidian note."""

    tags: List[str] = Field(default_factory=list, description="List of tags")
    aliases: List[str] = Field(default_factory=list, description="List of aliases")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    modified: Optional[datetime] = Field(
        None, description="Last modification timestamp"
    )
    frontmatter: Dict[str, Any] = Field(
        default_factory=dict, description="YAML frontmatter"
    )

    @field_validator("tags", "aliases", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v or []


class Note(BaseModel):
    """Represents an Obsidian note."""

    path: str = Field(..., description="File path relative to vault root")
    name: str = Field(..., description="Note name without extension")
    content: str = Field(default="", description="Note content")
    metadata: NoteMetadata = Field(
        default_factory=NoteMetadata, description="Note metadata"
    )
    size: Optional[int] = Field(None, description="File size in bytes")

    @field_validator("name", mode="before")
    @classmethod
    def extract_name_from_path(cls, v, info):
        if hasattr(info, "data") and "path" in info.data and not v:
            path = info.data["path"]
            return path.split("/")[-1].replace(".md", "")
        return v


class SearchResult(BaseModel):
    """Search result for notes."""

    note: Note = Field(..., description="The found note")
    score: Optional[float] = Field(None, description="Search relevance score")
    matches: List[str] = Field(
        default_factory=list, description="Matching text snippets"
    )


class VaultInfo(BaseModel):
    """Information about the Obsidian vault."""

    name: str = Field(..., description="Vault name")
    path: str = Field(..., description="Vault path")
    note_count: int = Field(0, description="Total number of notes")
    total_size: int = Field(0, description="Total vault size in bytes")
    plugins: List[str] = Field(default_factory=list, description="Installed plugins")


class BatchOperation(BaseModel):
    """Represents a batch operation on notes."""

    operation: str = Field(..., description="Operation type: create, update, delete")
    notes: List[Note] = Field(..., description="Notes to operate on")
    options: Dict[str, Any] = Field(
        default_factory=dict, description="Operation options"
    )


class Template(BaseModel):
    """Represents a note template."""

    name: str = Field(..., description="Template name")
    content: str = Field(..., description="Template content")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    description: Optional[str] = Field(None, description="Template description")


class BackupInfo(BaseModel):
    """Information about a vault backup."""

    timestamp: datetime = Field(..., description="Backup timestamp")
    path: str = Field(..., description="Backup file path")
    size: int = Field(..., description="Backup size in bytes")
    note_count: int = Field(..., description="Number of notes in backup")
    checksum: str = Field(..., description="Backup checksum")


class LinkInfo(BaseModel):
    """Information about links between notes."""

    source: str = Field(..., description="Source note path")
    target: str = Field(..., description="Target note path")
    link_type: str = Field(..., description="Type of link: wikilink, markdown, etc.")
    context: Optional[str] = Field(None, description="Context around the link")


class VaultStats(BaseModel):
    """Statistics about the vault."""

    total_notes: int = Field(0, description="Total number of notes")
    total_words: int = Field(0, description="Total word count")
    total_characters: int = Field(0, description="Total character count")
    total_links: int = Field(0, description="Total number of links")
    orphaned_notes: int = Field(0, description="Number of orphaned notes")
    most_linked_notes: List[Dict[str, Union[str, int]]] = Field(default_factory=list)
    tag_distribution: Dict[str, int] = Field(default_factory=dict)
    creation_timeline: Dict[str, int] = Field(default_factory=dict)
