#!/usr/bin/env python3
"""
Demo script for ObsidianReaderMCP.

This script demonstrates the core functionality of the ObsidianReaderMCP library.
Make sure you have Obsidian running with the obsidian-local-rest-api plugin enabled.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidianreadermcp import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig
from obsidianreadermcp.models import NoteMetadata
from obsidianreadermcp.extensions import ObsidianExtensions
from obsidianreadermcp.exceptions import ObsidianError


async def demo_basic_operations():
    """Demonstrate basic CRUD operations."""
    print("🚀 ObsidianReaderMCP Demo")
    print("=" * 50)
    
    try:
        # Create configuration from environment variables
        config = ObsidianConfig(
            host=os.getenv("OBSIDIAN_HOST", "192.168.0.104"),
            port=int(os.getenv("OBSIDIAN_PORT", "27123")),
            api_key=os.getenv("OBSIDIAN_API_KEY", "1fb6e1d89dacb6eb84a6aa5e1d238faa67b8ddbefeac90b895aeab32e0657b5f"),
            use_https=os.getenv("OBSIDIAN_USE_HTTPS", "false").lower() == "true",
        )
        
        print(f"📡 Connecting to Obsidian at {config.base_url}")
        
        async with ObsidianClient(config) as client:
            print("✅ Connected successfully!")
            
            # Get vault info
            print("\n📊 Vault Information:")
            vault_info = await client.get_vault_info()
            print(f"   Name: {vault_info.name}")
            print(f"   Notes: {vault_info.note_count}")
            
            # Create a demo note
            print("\n📝 Creating demo note...")
            demo_path = "demo/obsidian-reader-mcp-demo.md"
            metadata = NoteMetadata(
                tags=["demo", "obsidian-reader-mcp", "test"],
                frontmatter={
                    "title": "ObsidianReaderMCP Demo",
                    "author": "ObsidianReaderMCP",
                    "created": "2024-01-01T10:00:00Z",
                    "type": "demo"
                }
            )
            
            demo_content = """# ObsidianReaderMCP Demo

This note was created by the ObsidianReaderMCP demo script!

## Features Demonstrated

- ✅ Note creation with metadata
- ✅ Content management
- ✅ Tag support
- ✅ Frontmatter handling

## Links

This note links to [[another-note]] and demonstrates wikilink support.

## Code Example

```python
from obsidianreadermcp import ObsidianClient

async with ObsidianClient(config) as client:
    note = await client.create_note("demo.md", "Hello World!")
    print(f"Created: {note.path}")
```

## Conclusion

ObsidianReaderMCP makes it easy to programmatically manage your Obsidian vault!
"""
            
            note = await client.create_note(demo_path, demo_content, metadata)
            print(f"✅ Created note: {note.path}")
            
            # Read the note back
            print("\n📖 Reading note back...")
            retrieved_note = await client.get_note(demo_path)
            print(f"   Content length: {len(retrieved_note.content)} characters")
            print(f"   Tags: {retrieved_note.metadata.tags}")
            
            # Search for notes
            print("\n🔍 Searching for 'demo' notes...")
            search_results = await client.search_notes("demo", limit=5)
            print(f"   Found {len(search_results)} matching notes")
            for result in search_results[:3]:
                print(f"   - {result.note.path} (score: {result.score})")
            
            # List all tags
            print("\n🏷️  Getting all tags...")
            tags = await client.get_tags()
            print(f"   Found {len(tags)} unique tags")
            if tags:
                print(f"   Sample tags: {tags[:5]}")
            
            # Demonstrate extensions
            print("\n🔧 Testing Extensions...")
            extensions = ObsidianExtensions(client)
            
            # Create a template
            template = extensions.create_template(
                name="daily_note",
                content="""# Daily Note - {{date}}

## Weather
{{weather}}

## Tasks
- [ ] {{task1}}
- [ ] {{task2}}

## Notes
{{notes}}

---
Tags: #daily #{{date}}
""",
                description="Daily note template"
            )
            print(f"✅ Created template: {template.name}")
            
            # Create note from template
            template_note_path = "demo/daily-note-demo.md"
            template_variables = {
                "date": "2024-01-15",
                "weather": "Sunny, 22°C",
                "task1": "Review ObsidianReaderMCP documentation",
                "task2": "Test all features",
                "notes": "Everything working perfectly!"
            }
            
            template_note = await extensions.create_note_from_template(
                "daily_note",
                template_note_path,
                template_variables
            )
            print(f"✅ Created note from template: {template_note.path}")
            
            # Batch operations demo
            print("\n📦 Testing batch operations...")
            batch_notes = [
                {
                    "path": "demo/batch-note-1.md",
                    "content": "# Batch Note 1\n\nThis is the first batch note.",
                    "tags": ["batch", "demo", "test"]
                },
                {
                    "path": "demo/batch-note-2.md",
                    "content": "# Batch Note 2\n\nThis is the second batch note.",
                    "tags": ["batch", "demo", "test"]
                }
            ]
            
            batch_result = await extensions.batch_create_notes(batch_notes)
            print(f"✅ Batch creation: {batch_result['successful']}/{batch_result['total']} successful")
            
            # Generate vault statistics
            print("\n📈 Generating vault statistics...")
            stats = await extensions.generate_vault_stats()
            print(f"   Total notes: {stats.total_notes}")
            print(f"   Total words: {stats.total_words}")
            print(f"   Total links: {stats.total_links}")
            print(f"   Orphaned notes: {stats.orphaned_notes}")
            
            if stats.tag_distribution:
                top_tags = sorted(stats.tag_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
                print(f"   Top tags: {dict(top_tags)}")
            
            # Clean up demo notes
            print("\n🧹 Cleaning up demo notes...")
            cleanup_paths = [
                demo_path,
                template_note_path,
                "demo/batch-note-1.md",
                "demo/batch-note-2.md"
            ]
            
            cleanup_result = await extensions.batch_delete_notes(cleanup_paths)
            print(f"✅ Cleanup: {cleanup_result['successful']}/{cleanup_result['total']} deleted")
            
            print("\n🎉 Demo completed successfully!")
            print("\nObsidianReaderMCP is ready for use!")
            
    except ObsidianError as e:
        print(f"❌ Obsidian error: {e.message}")
        if hasattr(e, 'status_code') and e.status_code:
            print(f"   Status code: {e.status_code}")
        print("\n💡 Make sure:")
        print("   1. Obsidian is running")
        print("   2. obsidian-local-rest-api plugin is installed and enabled")
        print("   3. API server is started in the plugin settings")
        print("   4. Environment variables are set correctly")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n💡 Check your configuration and try again.")


if __name__ == "__main__":
    print("ObsidianReaderMCP Demo Script")
    print("Make sure Obsidian is running with obsidian-local-rest-api plugin enabled.")
    print()
    
    try:
        asyncio.run(demo_basic_operations())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
