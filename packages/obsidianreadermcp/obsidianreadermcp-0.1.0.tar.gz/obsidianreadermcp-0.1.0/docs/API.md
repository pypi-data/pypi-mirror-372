# ObsidianReaderMCP API Documentation

## Overview

ObsidianReaderMCP provides a comprehensive Python API for managing Obsidian vaults through the obsidian-local-rest-api plugin. The API is built with async/await support and includes both basic CRUD operations and advanced features.

## Core Classes

### ObsidianClient

The main client class for interacting with Obsidian vaults.

#### Initialization

```python
from obsidianreadermcp import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig

config = ObsidianConfig(
    host="localhost",
    port=27123,
    api_key="your_api_key",
    use_https=False,
    timeout=30,
    max_retries=3,
    rate_limit=10
)

client = ObsidianClient(config)
```

#### Context Manager Usage

```python
async with ObsidianClient(config) as client:
    # Client is automatically connected and disconnected
    note = await client.get_note("example.md")
```

#### Methods

##### `async create_note(path: str, content: str = "", metadata: Optional[NoteMetadata] = None) -> Note`

Creates a new note in the vault.

**Parameters:**
- `path`: Note path relative to vault root (e.g., "folder/note.md")
- `content`: Note content as markdown text
- `metadata`: Optional metadata including tags and frontmatter

**Returns:** Created `Note` object

**Example:**
```python
metadata = NoteMetadata(
    tags=["project", "meeting"],
    frontmatter={"title": "Project Meeting", "date": "2024-01-15"}
)

note = await client.create_note(
    path="meetings/project-kickoff.md",
    content="# Project Kickoff\n\nDiscussed project timeline and goals.",
    metadata=metadata
)
```

##### `async get_note(path: str) -> Note`

Retrieves a note by its path.

**Parameters:**
- `path`: Note path relative to vault root

**Returns:** `Note` object with content and metadata

**Raises:** `NotFoundError` if note doesn't exist

**Example:**
```python
note = await client.get_note("meetings/project-kickoff.md")
print(f"Note content: {note.content}")
print(f"Tags: {note.metadata.tags}")
```

##### `async update_note(path: str, content: Optional[str] = None, metadata: Optional[NoteMetadata] = None) -> Note`

Updates an existing note.

**Parameters:**
- `path`: Note path relative to vault root
- `content`: New content (if None, keeps existing content)
- `metadata`: New metadata (if None, keeps existing metadata)

**Returns:** Updated `Note` object

**Example:**
```python
# Update only content
await client.update_note("note.md", content="New content")

# Update only metadata
new_metadata = NoteMetadata(tags=["updated", "important"])
await client.update_note("note.md", metadata=new_metadata)

# Update both
await client.update_note("note.md", content="New content", metadata=new_metadata)
```

##### `async delete_note(path: str) -> bool`

Deletes a note from the vault.

**Parameters:**
- `path`: Note path relative to vault root

**Returns:** `True` if deletion was successful

**Example:**
```python
success = await client.delete_note("old-note.md")
if success:
    print("Note deleted successfully")
```

##### `async list_notes(folder: str = "") -> List[str]`

Lists all notes in the vault or a specific folder.

**Parameters:**
- `folder`: Folder path to list (empty string for root)

**Returns:** List of note paths

**Example:**
```python
# List all notes
all_notes = await client.list_notes()

# List notes in specific folder
meeting_notes = await client.list_notes("meetings")
```

##### `async search_notes(query: str, limit: int = 50, context_length: int = 100) -> List[SearchResult]`

Searches for notes containing the query text.

**Parameters:**
- `query`: Search query string
- `limit`: Maximum number of results to return
- `context_length`: Length of context around matches

**Returns:** List of `SearchResult` objects

**Example:**
```python
results = await client.search_notes("project timeline", limit=10)
for result in results:
    print(f"Found in: {result.note.path}")
    print(f"Score: {result.score}")
    for match in result.matches:
        print(f"Match: {match}")
```

##### `async get_vault_info() -> VaultInfo`

Gets information about the vault.

**Returns:** `VaultInfo` object with vault statistics

**Example:**
```python
info = await client.get_vault_info()
print(f"Vault: {info.name}")
print(f"Notes: {info.note_count}")
print(f"Plugins: {info.plugins}")
```

##### `async get_tags() -> List[str]`

Gets all tags used in the vault.

**Returns:** List of unique tag names

**Example:**
```python
tags = await client.get_tags()
print(f"Available tags: {tags}")
```

##### `async get_notes_by_tag(tag: str) -> List[Note]`

Gets all notes that have a specific tag.

**Parameters:**
- `tag`: Tag name to search for

**Returns:** List of `Note` objects

**Example:**
```python
project_notes = await client.get_notes_by_tag("project")
print(f"Found {len(project_notes)} project notes")
```

## Data Models

### Note

Represents an Obsidian note.

**Attributes:**
- `path: str` - File path relative to vault root
- `name: str` - Note name without extension
- `content: str` - Note content
- `metadata: NoteMetadata` - Note metadata
- `size: Optional[int]` - File size in bytes

### NoteMetadata

Metadata for an Obsidian note.

**Attributes:**
- `tags: List[str]` - List of tags
- `aliases: List[str]` - List of aliases
- `created: Optional[datetime]` - Creation timestamp
- `modified: Optional[datetime]` - Last modification timestamp
- `frontmatter: Dict[str, Any]` - YAML frontmatter

### SearchResult

Search result for notes.

**Attributes:**
- `note: Note` - The found note
- `score: Optional[float]` - Search relevance score
- `matches: List[str]` - Matching text snippets

### VaultInfo

Information about the Obsidian vault.

**Attributes:**
- `name: str` - Vault name
- `path: str` - Vault path
- `note_count: int` - Total number of notes
- `total_size: int` - Total vault size in bytes
- `plugins: List[str]` - Installed plugins

## Configuration

### ObsidianConfig

Configuration for Obsidian API connection.

**Attributes:**
- `host: str` - Obsidian API host (default: "localhost")
- `port: int` - Obsidian API port (default: 27123)
- `api_key: str` - Obsidian API key (required)
- `use_https: bool` - Whether to use HTTPS (default: False)
- `timeout: int` - Request timeout in seconds (default: 30)
- `max_retries: int` - Maximum retries for failed requests (default: 3)
- `rate_limit: int` - Maximum requests per second (default: 10)

**Properties:**
- `base_url: str` - Complete base URL for API requests
- `headers: dict` - HTTP headers for API requests

## Error Handling

### Exception Hierarchy

- `ObsidianError` - Base exception for all Obsidian-related errors
  - `ConnectionError` - Connection to Obsidian API failed
  - `AuthenticationError` - API authentication failed
  - `NotFoundError` - Requested resource not found
  - `ValidationError` - Input validation failed
  - `RateLimitError` - API rate limit exceeded
  - `ServerError` - Obsidian API server error
  - `TimeoutError` - Operation timed out

### Error Handling Example

```python
from obsidianreadermcp.exceptions import NotFoundError, ConnectionError

try:
    note = await client.get_note("nonexistent.md")
except NotFoundError:
    print("Note not found")
except ConnectionError:
    print("Failed to connect to Obsidian")
except Exception as e:
    print(f"Unexpected error: {e}")
```
