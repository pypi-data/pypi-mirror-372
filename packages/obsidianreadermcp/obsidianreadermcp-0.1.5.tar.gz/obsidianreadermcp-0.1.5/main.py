"""
Main entry point for ObsidianReaderMCP.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidianreadermcp.server import main as server_main


def main():
    """Main entry point."""
    print("ObsidianReaderMCP - Obsidian Vault Management MCP Server")
    print("Starting MCP server...")

    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
