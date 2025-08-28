"""
Basic usage examples for ObsidianReaderMCP.
"""

import asyncio
import os
from obsidianreadermcp import ObsidianClient, ObsidianMCPServer
from obsidianreadermcp.config import ObsidianConfig
from obsidianreadermcp.models import NoteMetadata
from obsidianreadermcp.extensions import ObsidianExtensions


async def basic_crud_example():
    """Demonstrate basic CRUD operations."""
    print("=== Basic CRUD Operations ===")
    
    # Create configuration
    config = ObsidianConfig(
        host=os.getenv("OBSIDIAN_HOST", "localhost"),
        port=int(os.getenv("OBSIDIAN_PORT", "27123")),
        api_key=os.getenv("OBSIDIAN_API_KEY", "your_api_key_here"),
        use_https=os.getenv("OBSIDIAN_USE_HTTPS", "false").lower() == "true",
    )
    
    # Create and connect client
    async with ObsidianClient(config) as client:
        # Create a new note
        print("Creating a new note...")
        metadata = NoteMetadata(
            tags=["example", "demo"],
            frontmatter={
                "title": "Example Note",
                "author": "ObsidianReaderMCP",
                "created": "2024-01-01T10:00:00Z"
            }
        )
        
        note = await client.create_note(
            path="examples/demo_note.md",
            content="# Example Note\n\nThis is a demonstration note created by ObsidianReaderMCP.\n\n## Features\n\n- Create notes\n- Read notes\n- Update notes\n- Delete notes",
            metadata=metadata
        )
        print(f"Created note: {note.path}")
        
        # Read the note
        print("\nReading the note...")
        retrieved_note = await client.get_note("examples/demo_note.md")
        print(f"Note content length: {len(retrieved_note.content)} characters")
        print(f"Note tags: {retrieved_note.metadata.tags}")
        
        # Update the note
        print("\nUpdating the note...")
        updated_note = await client.update_note(
            path="examples/demo_note.md",
            content=retrieved_note.content + "\n\n## Updated\n\nThis note has been updated!"
        )
        print(f"Updated note content length: {len(updated_note.content)} characters")
        
        # List notes
        print("\nListing notes...")
        notes = await client.list_notes()
        print(f"Total notes in vault: {len(notes)}")
        
        # Search notes
        print("\nSearching notes...")
        search_results = await client.search_notes("demonstration")
        print(f"Found {len(search_results)} notes matching 'demonstration'")
        
        # Get vault info
        print("\nGetting vault info...")
        vault_info = await client.get_vault_info()
        print(f"Vault: {vault_info.name} ({vault_info.note_count} notes)")
        
        # Clean up - delete the demo note
        print("\nCleaning up...")
        await client.delete_note("examples/demo_note.md")
        print("Demo note deleted")


async def extensions_example():
    """Demonstrate extended functionality."""
    print("\n=== Extended Functionality ===")
    
    config = ObsidianConfig(
        host=os.getenv("OBSIDIAN_HOST", "localhost"),
        port=int(os.getenv("OBSIDIAN_PORT", "27123")),
        api_key=os.getenv("OBSIDIAN_API_KEY", "your_api_key_here"),
        use_https=os.getenv("OBSIDIAN_USE_HTTPS", "false").lower() == "true",
    )
    
    async with ObsidianClient(config) as client:
        extensions = ObsidianExtensions(client)
        
        # Create a template
        print("Creating a template...")
        template = extensions.create_template(
            name="meeting_notes",
            content="""# Meeting: {{meeting_title}}

**Date:** {{date}}
**Attendees:** {{attendees}}

## Agenda
{{agenda}}

## Notes
{{notes}}

## Action Items
{{action_items}}

## Next Steps
{{next_steps}}

---
Tags: #meeting #{{project}}
""",
            description="Template for meeting notes"
        )
        print(f"Created template: {template.name}")
        
        # Create a note from template
        print("\nCreating note from template...")
        variables = {
            "meeting_title": "Project Kickoff",
            "date": "2024-01-15",
            "attendees": "Alice, Bob, Charlie",
            "agenda": "- Project overview\n- Timeline discussion\n- Resource allocation",
            "notes": "Great enthusiasm from the team. Clear objectives defined.",
            "action_items": "- Alice: Create project plan\n- Bob: Set up development environment",
            "next_steps": "Schedule weekly check-ins",
            "project": "obsidian-mcp"
        }
        
        meeting_note = await extensions.create_note_from_template(
            template_name="meeting_notes",
            path="meetings/project_kickoff.md",
            variables=variables
        )
        print(f"Created meeting note: {meeting_note.path}")
        
        # Batch operations
        print("\nPerforming batch operations...")
        batch_notes = [
            {
                "path": "batch/note1.md",
                "content": "# Batch Note 1\n\nThis is the first batch note.",
                "tags": ["batch", "test"]
            },
            {
                "path": "batch/note2.md", 
                "content": "# Batch Note 2\n\nThis is the second batch note.",
                "tags": ["batch", "test"]
            },
            {
                "path": "batch/note3.md",
                "content": "# Batch Note 3\n\nThis is the third batch note.",
                "tags": ["batch", "test"]
            }
        ]
        
        batch_result = await extensions.batch_create_notes(batch_notes)
        print(f"Batch creation result: {batch_result['successful']}/{batch_result['total']} successful")
        
        # Analyze links
        print("\nAnalyzing links...")
        links = await extensions.analyze_links()
        print(f"Found {len(links)} links in the vault")
        
        # Find orphaned notes
        orphaned = await extensions.find_orphaned_notes()
        print(f"Found {len(orphaned)} orphaned notes")
        
        # Generate vault statistics
        print("\nGenerating vault statistics...")
        stats = await extensions.generate_vault_stats()
        print(f"Vault stats:")
        print(f"  - Total notes: {stats.total_notes}")
        print(f"  - Total words: {stats.total_words}")
        print(f"  - Total links: {stats.total_links}")
        print(f"  - Orphaned notes: {stats.orphaned_notes}")
        print(f"  - Top tags: {list(stats.tag_distribution.keys())[:5]}")
        
        # Clean up batch notes
        print("\nCleaning up batch notes...")
        cleanup_result = await extensions.batch_delete_notes([
            "batch/note1.md",
            "batch/note2.md", 
            "batch/note3.md",
            "meetings/project_kickoff.md"
        ])
        print(f"Cleanup result: {cleanup_result['successful']}/{cleanup_result['total']} deleted")


async def mcp_server_example():
    """Demonstrate MCP server usage."""
    print("\n=== MCP Server Example ===")
    print("To run the MCP server, use:")
    print("python -m obsidianreadermcp.server")
    print("\nOr programmatically:")
    
    # This would normally run the server
    # server = ObsidianMCPServer()
    # await server.run()
    
    print("Server would start and listen for MCP protocol messages...")


async def main():
    """Run all examples."""
    try:
        await basic_crud_example()
        await extensions_example()
        await mcp_server_example()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("\nMake sure you have:")
        print("1. Obsidian running with obsidian-local-rest-api plugin")
        print("2. Correct environment variables set:")
        print("   - OBSIDIAN_HOST")
        print("   - OBSIDIAN_PORT") 
        print("   - OBSIDIAN_API_KEY")


if __name__ == "__main__":
    asyncio.run(main())
