# ObsidianReaderMCP

[![GitHub](https://img.shields.io/badge/GitHub-QianJue--CN%2FObsidianReaderMCP-blue?logo=github)](https://github.com/QianJue-CN/ObsidianReaderMCP)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A comprehensive Python MCP (Model Context Protocol) server for managing Obsidian vaults through the obsidian-local-rest-api plugin.

## Features

### Core CRUD Operations
- **Create**: Create new notes with content, metadata, and tags
- **Read**: Retrieve note content and metadata by path
- **Update**: Modify existing notes (content, metadata, tags)
- **Delete**: Remove notes from the vault

### Extended Functionality
- **Batch Operations**: Create, update, or delete multiple notes at once
- **Template System**: Create and use note templates with variables
- **Link Analysis**: Analyze relationships between notes
- **Search & Filter**: Advanced search by content, tags, date range, word count
- **Vault Statistics**: Generate comprehensive vault analytics
- **Backup Management**: Create and manage vault backups

### MCP Server Integration
- Full MCP protocol support for AI assistant integration
- Async/await support for high performance
- Comprehensive error handling and logging
- Rate limiting and connection management

## Installation

### Prerequisites
1. **Obsidian** with the **obsidian-local-rest-api** plugin installed and configured
2. **Python 3.10+**

### Method 1: Using uvx (Recommended)

The easiest way to use ObsidianReaderMCP is with `uvx`, which allows you to run it without installation:

```bash
# Run directly without installation
uvx obsidianreadermcp

# Or install as a tool
uv tool install obsidianreadermcp
obsidianreadermcp
```

### Method 2: Using pip

```bash
# Install from PyPI
pip install obsidianreadermcp

# Run the server
obsidianreadermcp
```

### Method 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/QianJue-CN/ObsidianReaderMCP.git
cd ObsidianReaderMCP

# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
# Obsidian API Configuration
OBSIDIAN_HOST=localhost
OBSIDIAN_PORT=27123
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_USE_HTTPS=false
OBSIDIAN_TIMEOUT=30
OBSIDIAN_MAX_RETRIES=3
OBSIDIAN_RATE_LIMIT=10

# MCP Server Configuration
LOG_LEVEL=INFO
ENABLE_DEBUG=false
```

### Obsidian Setup

1. Install the **obsidian-local-rest-api** plugin from the Community Plugins
2. Enable the plugin in Obsidian settings
3. Configure the plugin:
   - Set API port (default: 27123)
   - Generate an API key
   - Enable CORS if needed
4. Start the local REST API server

## Usage

### As a Python Library

```python
import asyncio
from obsidianreadermcp import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig
from obsidianreadermcp.models import NoteMetadata

async def main():
    # Create configuration
    config = ObsidianConfig()  # Uses environment variables

    # Create and connect client
    async with ObsidianClient(config) as client:
        # Create a note
        metadata = NoteMetadata(
            tags=["example", "demo"],
            frontmatter={"title": "My Note", "author": "Me"}
        )

        note = await client.create_note(
            path="my_note.md",
            content="# My Note\n\nThis is my note content.",
            metadata=metadata
        )

        # Read the note
        retrieved_note = await client.get_note("my_note.md")
        print(f"Note content: {retrieved_note.content}")

        # Update the note
        await client.update_note(
            path="my_note.md",
            content="# Updated Note\n\nThis content has been updated."
        )

        # Search notes
        results = await client.search_notes("updated")
        print(f"Found {len(results)} matching notes")

        # Delete the note
        await client.delete_note("my_note.md")

asyncio.run(main())
```

### As an MCP Server

```bash
# Method 1: Using uvx (recommended)
uvx obsidianreadermcp

# Method 2: Using installed package
obsidianreadermcp

# Method 3: Using Python module
python -m obsidianreadermcp.server

# Method 4: Programmatically
python -c "
import asyncio
from obsidianreadermcp.server import main
asyncio.run(main())
"
```

### Claude Desktop Integration

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["obsidianreadermcp"],
      "env": {
        "OBSIDIAN_HOST": "localhost",
        "OBSIDIAN_PORT": "27123",
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or if you have it installed globally:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "obsidianreadermcp",
      "env": {
        "OBSIDIAN_HOST": "localhost",
        "OBSIDIAN_PORT": "27123",
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Extended Features

```python
from obsidianreadermcp.extensions import ObsidianExtensions

async with ObsidianClient(config) as client:
    extensions = ObsidianExtensions(client)

    # Create a template
    template = extensions.create_template(
        name="daily_note",
        content="# {{date}}\n\n## Tasks\n- {{task}}\n\n## Notes\n{{notes}}",
        description="Daily note template"
    )

    # Create note from template
    note = await extensions.create_note_from_template(
        template_name="daily_note",
        path="daily/2024-01-15.md",
        variables={
            "date": "2024-01-15",
            "task": "Review project status",
            "notes": "All systems operational"
        }
    )

    # Batch operations
    batch_notes = [
        {"path": "note1.md", "content": "Content 1", "tags": ["batch"]},
        {"path": "note2.md", "content": "Content 2", "tags": ["batch"]},
    ]
    result = await extensions.batch_create_notes(batch_notes)

    # Analyze vault
    stats = await extensions.generate_vault_stats()
    print(f"Vault has {stats.total_notes} notes with {stats.total_words} words")

    # Find orphaned notes
    orphaned = await extensions.find_orphaned_notes()
    print(f"Found {len(orphaned)} orphaned notes")
```

## MCP Tools

When running as an MCP server, the following tools are available:

### Core Operations
- `create_note`: Create a new note with content and metadata
- `get_note`: Retrieve a note by path
- `update_note`: Update an existing note
- `delete_note`: Delete a note
- `list_notes`: List all notes in vault or folder
- `search_notes`: Search notes by content

### Vault Management
- `get_vault_info`: Get vault information and statistics
- `get_tags`: List all tags used in the vault
- `get_notes_by_tag`: Find notes with specific tags

## API Reference

### ObsidianClient

The main client class for interacting with Obsidian.

#### Methods

- `async create_note(path: str, content: str = "", metadata: Optional[NoteMetadata] = None) -> Note`
- `async get_note(path: str) -> Note`
- `async update_note(path: str, content: Optional[str] = None, metadata: Optional[NoteMetadata] = None) -> Note`
- `async delete_note(path: str) -> bool`
- `async list_notes(folder: str = "") -> List[str]`
- `async search_notes(query: str, limit: int = 50, context_length: int = 100) -> List[SearchResult]`
- `async get_vault_info() -> VaultInfo`
- `async get_tags() -> List[str]`
- `async get_notes_by_tag(tag: str) -> List[Note]`

### ObsidianExtensions

Extended functionality for advanced vault management.

#### Methods

- `async batch_create_notes(notes_data: List[Dict], continue_on_error: bool = True) -> Dict`
- `async batch_update_notes(updates: List[Dict], continue_on_error: bool = True) -> Dict`
- `async batch_delete_notes(paths: List[str], continue_on_error: bool = True) -> Dict`
- `create_template(name: str, content: str, variables: Optional[List[str]] = None, description: Optional[str] = None) -> Template`
- `async create_note_from_template(template_name: str, path: str, variables: Optional[Dict[str, str]] = None, metadata: Optional[NoteMetadata] = None) -> Note`
- `async create_backup(backup_path: str, include_attachments: bool = True) -> BackupInfo`
- `async analyze_links() -> List[LinkInfo]`
- `async find_orphaned_notes() -> List[str]`
- `async find_broken_links() -> List[LinkInfo]`
- `async generate_vault_stats() -> VaultStats`
- `async search_by_date_range(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, date_field: str = "created") -> List[Note]`
- `async search_by_word_count(min_words: Optional[int] = None, max_words: Optional[int] = None) -> List[Note]`

## Testing

Run the test suite:

```bash
# With uv
uv run pytest

# With pip
pytest

# With coverage
pytest --cov=obsidianreadermcp --cov-report=html
```

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_usage.py`: Demonstrates core CRUD operations
- `advanced_features.py`: Shows extended functionality
- `mcp_integration.py`: MCP server integration examples

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Issues and Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/QianJue-CN/ObsidianReaderMCP/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/QianJue-CN/ObsidianReaderMCP/issues)
- 📖 **Documentation**: [API Documentation](docs/API.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api) - The Obsidian plugin that makes this possible
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) - The protocol for AI assistant integration
- [Obsidian](https://obsidian.md/) - The knowledge management application

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=QianJue-CN/ObsidianReaderMCP&type=Date)](https://star-history.com/#QianJue-CN/ObsidianReaderMCP&Date)