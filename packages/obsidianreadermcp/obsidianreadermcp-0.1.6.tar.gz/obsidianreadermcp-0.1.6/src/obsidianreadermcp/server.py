"""
MCP Server implementation for Obsidian Vault management.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp.server.lowlevel.server import NotificationOptions

from .client import ObsidianClient
from .config import get_config
from .exceptions import ObsidianError
from .models import Note, NoteMetadata, SearchResult


logger = logging.getLogger(__name__)


class ObsidianMCPServer:
    """MCP Server for Obsidian Vault management."""

    def __init__(self):
        """Initialize the MCP server."""
        self.obsidian_config, self.mcp_config = get_config()
        self.server = Server(self.mcp_config.server_name)
        self.client: Optional[ObsidianClient] = None

        # Register handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="create_note",
                    description="Create a new note in the Obsidian vault",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Note path relative to vault root",
                            },
                            "content": {
                                "type": "string",
                                "description": "Note content",
                                "default": "",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags for the note",
                                "default": [],
                            },
                            "frontmatter": {
                                "type": "object",
                                "description": "YAML frontmatter as key-value pairs",
                                "default": {},
                            },
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="get_note",
                    description="Get a note from the Obsidian vault",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Note path relative to vault root",
                            }
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="update_note",
                    description="Update an existing note in the Obsidian vault",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Note path relative to vault root",
                            },
                            "content": {
                                "type": "string",
                                "description": "New note content",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags for the note",
                            },
                            "frontmatter": {
                                "type": "object",
                                "description": "YAML frontmatter as key-value pairs",
                            },
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="delete_note",
                    description="Delete a note from the Obsidian vault",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Note path relative to vault root",
                            }
                        },
                        "required": ["path"],
                    },
                ),
                Tool(
                    name="list_notes",
                    description="List all notes in the vault or a specific folder",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "folder": {
                                "type": "string",
                                "description": "Folder path to list (empty for root)",
                                "default": "",
                            }
                        },
                    },
                ),
                Tool(
                    name="search_notes",
                    description="Search for notes with enhanced folder and path matching",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 50,
                            },
                            "context_length": {
                                "type": "integer",
                                "description": "Length of context around matches",
                                "default": 100,
                            },
                            "include_folders": {
                                "type": "boolean",
                                "description": "Whether to include folder matches",
                                "default": True,
                            },
                            "search_in_path": {
                                "type": "boolean",
                                "description": "Whether to search in file paths",
                                "default": True,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="get_vault_info",
                    description="Get information about the Obsidian vault",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="get_tags",
                    description="Get all tags used in the vault",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="get_notes_by_tag",
                    description="Get all notes with a specific tag",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tag": {
                                "type": "string",
                                "description": "Tag to search for",
                            }
                        },
                        "required": ["tag"],
                    },
                ),
                Tool(
                    name="list_folders",
                    description="List all folders in the vault",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="get_folder_info",
                    description="Get detailed information about a specific folder",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "folder_path": {
                                "type": "string",
                                "description": "Path to the folder",
                            }
                        },
                        "required": ["folder_path"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool calls."""
            if not self.client:
                self.client = ObsidianClient(self.obsidian_config)
                await self.client.connect()

            try:
                if name == "create_note":
                    return await self._handle_create_note(arguments)
                elif name == "get_note":
                    return await self._handle_get_note(arguments)
                elif name == "update_note":
                    return await self._handle_update_note(arguments)
                elif name == "delete_note":
                    return await self._handle_delete_note(arguments)
                elif name == "list_notes":
                    return await self._handle_list_notes(arguments)
                elif name == "search_notes":
                    return await self._handle_search_notes(arguments)
                elif name == "get_vault_info":
                    return await self._handle_get_vault_info(arguments)
                elif name == "get_tags":
                    return await self._handle_get_tags(arguments)
                elif name == "get_notes_by_tag":
                    return await self._handle_get_notes_by_tag(arguments)
                elif name == "list_folders":
                    return await self._handle_list_folders(arguments)
                elif name == "get_folder_info":
                    return await self._handle_get_folder_info(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except ObsidianError as e:
                return [TextContent(type="text", text=f"Error: {e.message}")]
            except Exception as e:
                logger.error(f"Unexpected error in {name}: {e}")
                return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]

    async def _handle_create_note(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle create_note tool call."""
        path = arguments["path"]
        content = arguments.get("content", "")
        tags = arguments.get("tags", [])
        frontmatter = arguments.get("frontmatter", {})

        # Add tags to frontmatter if provided
        if tags:
            frontmatter["tags"] = tags

        metadata = NoteMetadata(tags=tags, frontmatter=frontmatter)
        note = await self.client.create_note(path, content, metadata)

        return [
            TextContent(
                type="text",
                text=f"Successfully created note: {note.path}\nContent length: {len(note.content)} characters",
            )
        ]

    async def _handle_get_note(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_note tool call."""
        path = arguments["path"]
        note = await self.client.get_note(path)

        result = {
            "path": note.path,
            "name": note.name,
            "content": note.content,
            "tags": note.metadata.tags,
            "frontmatter": note.metadata.frontmatter,
        }

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_update_note(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle update_note tool call."""
        path = arguments["path"]
        content = arguments.get("content")
        tags = arguments.get("tags")
        frontmatter = arguments.get("frontmatter")

        metadata = None
        if tags is not None or frontmatter is not None:
            # Get current metadata if not fully specified
            current_note = await self.client.get_note(path)
            current_metadata = current_note.metadata

            metadata = NoteMetadata(
                tags=tags if tags is not None else current_metadata.tags,
                frontmatter=frontmatter
                if frontmatter is not None
                else current_metadata.frontmatter,
            )

            # Update frontmatter with tags if provided
            if tags is not None:
                metadata.frontmatter["tags"] = tags

        note = await self.client.update_note(path, content, metadata)

        return [
            TextContent(
                type="text",
                text=f"Successfully updated note: {note.path}\nContent length: {len(note.content)} characters",
            )
        ]

    async def _handle_delete_note(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle delete_note tool call."""
        path = arguments["path"]
        success = await self.client.delete_note(path)

        if success:
            return [TextContent(type="text", text=f"Successfully deleted note: {path}")]
        else:
            return [TextContent(type="text", text=f"Failed to delete note: {path}")]

    async def _handle_list_notes(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle list_notes tool call."""
        folder = arguments.get("folder", "")
        notes = await self.client.list_notes(folder)

        if not notes:
            return [TextContent(type="text", text="No notes found.")]

        result = {"folder": folder or "root", "count": len(notes), "notes": notes}

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_search_notes(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle search_notes tool call."""
        query = arguments["query"]
        limit = arguments.get("limit", 50)
        context_length = arguments.get("context_length", 100)
        include_folders = arguments.get("include_folders", True)
        search_in_path = arguments.get("search_in_path", True)

        results = await self.client.search_notes(
            query, limit, context_length, include_folders, search_in_path
        )

        if not results:
            return [TextContent(type="text", text=f"No notes found for query: {query}")]

        search_results = []
        for result in results:
            # Determine result type
            result_type = "content"
            if result.note.path.endswith("/"):
                result_type = "folder"
            elif any("路径匹配" in match for match in result.matches):
                result_type = "path"
            elif any("文件夹匹配" in match for match in result.matches):
                result_type = "folder"

            search_results.append(
                {
                    "path": result.note.path,
                    "name": result.note.name,
                    "type": result_type,
                    "score": result.score,
                    "matches": result.matches,
                }
            )

        result_data = {
            "query": query,
            "count": len(search_results),
            "search_options": {
                "include_folders": include_folders,
                "search_in_path": search_in_path,
            },
            "results": search_results,
        }

        return [
            TextContent(
                type="text", text=json.dumps(result_data, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_get_vault_info(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_vault_info tool call."""
        vault_info = await self.client.get_vault_info()

        result = {
            "name": vault_info.name,
            "path": vault_info.path,
            "note_count": vault_info.note_count,
            "total_size": vault_info.total_size,
            "plugins": vault_info.plugins,
        }

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_get_tags(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_tags tool call."""
        tags = await self.client.get_tags()

        result = {"count": len(tags), "tags": sorted(tags)}

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_get_notes_by_tag(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_notes_by_tag tool call."""
        tag = arguments["tag"]
        notes = await self.client.get_notes_by_tag(tag)

        if not notes:
            return [TextContent(type="text", text=f"No notes found with tag: {tag}")]

        note_list = []
        for note in notes:
            note_list.append(
                {
                    "path": note.path,
                    "name": note.name,
                    "tags": note.metadata.tags,
                }
            )

        result = {"tag": tag, "count": len(note_list), "notes": note_list}

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_list_folders(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle list_folders tool call."""
        folders = await self.client.list_folders()

        if not folders:
            return [TextContent(type="text", text="No folders found in the vault")]

        result = {
            "count": len(folders),
            "folders": folders
        }

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    async def _handle_get_folder_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_folder_info tool call."""
        folder_path = arguments["folder_path"]

        folder_info = await self.client.get_folder_info(folder_path)

        return [
            TextContent(
                type="text", text=json.dumps(folder_info, indent=2, ensure_ascii=False)
            )
        ]

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info(
            f"Starting {self.mcp_config.server_name} v{self.mcp_config.version}"
        )

        try:
            # Initialize Obsidian client
            self.client = ObsidianClient(self.obsidian_config)
            await self.client.connect()
            logger.info("Connected to Obsidian API")

            # Run the server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.mcp_config.server_name,
                        server_version=self.mcp_config.version,
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        ),
                    ),
                )
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            if self.client:
                await self.client.disconnect()
            logger.info("Server stopped")


async def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    server = ObsidianMCPServer()
    await server.run()


def cli_main():
    """CLI entry point that handles the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
