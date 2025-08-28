"""
Tests for ObsidianClient.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response

from obsidianreadermcp.client import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig
from obsidianreadermcp.exceptions import ConnectionError, NotFoundError
from obsidianreadermcp.models import Note, NoteMetadata


@pytest.fixture
def config():
    """Create a test configuration."""
    return ObsidianConfig(
        host="localhost",
        port=27123,
        api_key="test_key",
        use_https=False,
        timeout=30,
        max_retries=3,
        rate_limit=10,
    )


@pytest.fixture
def client(config):
    """Create a test client."""
    return ObsidianClient(config)


@pytest.mark.asyncio
async def test_client_initialization(client, config):
    """Test client initialization."""
    assert client.config == config
    assert client._client is None


@pytest.mark.asyncio
async def test_connect_success(client):
    """Test successful connection."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_client.request.return_value = mock_response
        
        await client.connect()
        
        assert client._client is not None
        mock_client.request.assert_called_once()


@pytest.mark.asyncio
async def test_connect_failure(client):
    """Test connection failure."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock connection error
        mock_client.request.side_effect = Exception("Connection failed")
        
        with pytest.raises(ConnectionError):
            await client.connect()


@pytest.mark.asyncio
async def test_create_note(client):
    """Test note creation."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        with patch.object(client, 'get_note', new_callable=AsyncMock) as mock_get:
            # Mock responses
            mock_request.return_value = {}
            mock_get.return_value = Note(
                path="test.md",
                name="test",
                content="Test content",
                metadata=NoteMetadata(),
            )
            
            result = await client.create_note("test", "Test content")
            
            assert result.path == "test.md"
            assert result.content == "Test content"
            mock_request.assert_called_once()
            mock_get.assert_called_once_with("test.md")


@pytest.mark.asyncio
async def test_get_note(client):
    """Test getting a note."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        # Mock response
        mock_request.return_value = {
            "content": "# Test Note\n\nThis is a test note."
        }
        
        result = await client.get_note("test.md")
        
        assert result.path == "test.md"
        assert result.name == "test"
        assert "Test Note" in result.content


@pytest.mark.asyncio
async def test_get_note_not_found(client):
    """Test getting a non-existent note."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = NotFoundError("Note not found")
        
        with pytest.raises(NotFoundError):
            await client.get_note("nonexistent.md")


@pytest.mark.asyncio
async def test_update_note(client):
    """Test updating a note."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        with patch.object(client, 'get_note', new_callable=AsyncMock) as mock_get:
            # Mock current note
            current_note = Note(
                path="test.md",
                name="test",
                content="Old content",
                metadata=NoteMetadata(),
            )
            
            # Mock updated note
            updated_note = Note(
                path="test.md",
                name="test",
                content="New content",
                metadata=NoteMetadata(),
            )
            
            mock_get.side_effect = [current_note, updated_note]
            mock_request.return_value = {}
            
            result = await client.update_note("test.md", "New content")
            
            assert result.content == "New content"
            mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_delete_note(client):
    """Test deleting a note."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {}
        
        result = await client.delete_note("test.md")
        
        assert result is True
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_list_notes(client):
    """Test listing notes."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "files": ["note1.md", "note2.md", "image.png", "note3.md"]
        }
        
        result = await client.list_notes()
        
        assert len(result) == 3
        assert "note1.md" in result
        assert "note2.md" in result
        assert "note3.md" in result
        assert "image.png" not in result


@pytest.mark.asyncio
async def test_search_notes(client):
    """Test searching notes."""
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = [
            {
                "filename": "note1.md",
                "score": 0.95,
                "matches": [{"context": "This is a test match"}]
            },
            {
                "filename": "note2.md",
                "score": 0.85,
                "matches": [{"context": "Another test match"}]
            }
        ]
        
        results = await client.search_notes("test")
        
        assert len(results) == 2
        assert results[0].note.path == "note1.md"
        assert results[0].score == 0.95
        assert len(results[0].matches) == 1


@pytest.mark.asyncio
async def test_parse_metadata_with_frontmatter(client):
    """Test parsing metadata from content with frontmatter."""
    content = """---
tags: [test, example]
title: Test Note
---

# Test Note

This is the content."""
    
    metadata = client._parse_metadata(content)
    
    assert "tags" in metadata.frontmatter
    assert "title" in metadata.frontmatter
    assert metadata.frontmatter["title"] == "Test Note"


@pytest.mark.asyncio
async def test_parse_metadata_without_frontmatter(client):
    """Test parsing metadata from content without frontmatter."""
    content = "# Test Note\n\nThis is just content."
    
    metadata = client._parse_metadata(content)
    
    assert len(metadata.frontmatter) == 0
    assert len(metadata.tags) == 0
