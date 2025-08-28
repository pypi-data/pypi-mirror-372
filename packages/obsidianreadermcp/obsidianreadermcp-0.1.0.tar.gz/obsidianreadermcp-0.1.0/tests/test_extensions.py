"""
Tests for ObsidianExtensions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from obsidianreadermcp.extensions import ObsidianExtensions
from obsidianreadermcp.client import ObsidianClient
from obsidianreadermcp.config import ObsidianConfig
from obsidianreadermcp.models import Note, NoteMetadata, Template


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


@pytest.fixture
def extensions(client):
    """Create test extensions."""
    return ObsidianExtensions(client)


@pytest.mark.asyncio
async def test_batch_create_notes_success(extensions):
    """Test successful batch note creation."""
    notes_data = [
        {"path": "note1.md", "content": "Content 1"},
        {"path": "note2.md", "content": "Content 2"},
    ]
    
    with patch.object(extensions.client, 'create_note', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = Note(path="test.md", name="test", content="test")
        
        result = await extensions.batch_create_notes(notes_data)
        
        assert result["total"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
        assert len(result["errors"]) == 0
        assert mock_create.call_count == 2


@pytest.mark.asyncio
async def test_batch_create_notes_with_errors(extensions):
    """Test batch note creation with some errors."""
    notes_data = [
        {"path": "note1.md", "content": "Content 1"},
        {"path": "note2.md", "content": "Content 2"},
    ]
    
    with patch.object(extensions.client, 'create_note', new_callable=AsyncMock) as mock_create:
        # First call succeeds, second fails
        mock_create.side_effect = [
            Note(path="note1.md", name="note1", content="Content 1"),
            Exception("Creation failed")
        ]
        
        result = await extensions.batch_create_notes(notes_data)
        
        assert result["total"] == 2
        assert result["successful"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["path"] == "note2.md"


def test_create_template(extensions):
    """Test template creation."""
    template = extensions.create_template(
        name="daily_note",
        content="# {{date}}\n\n## Tasks\n- {{task}}",
        description="Daily note template"
    )
    
    assert template.name == "daily_note"
    assert "{{date}}" in template.content
    assert "date" in template.variables
    assert "task" in template.variables
    assert template.description == "Daily note template"
    
    # Check template is stored
    stored_template = extensions.get_template("daily_note")
    assert stored_template == template


def test_create_template_auto_extract_variables(extensions):
    """Test automatic variable extraction from template content."""
    template = extensions.create_template(
        name="meeting_note",
        content="# Meeting with {{attendee}}\n\nDate: {{date}}\nTopic: {{topic}}"
    )
    
    assert len(template.variables) == 3
    assert "attendee" in template.variables
    assert "date" in template.variables
    assert "topic" in template.variables


@pytest.mark.asyncio
async def test_create_note_from_template(extensions):
    """Test creating a note from a template."""
    # Create template
    extensions.create_template(
        name="test_template",
        content="# {{title}}\n\nAuthor: {{author}}"
    )
    
    with patch.object(extensions.client, 'create_note', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = Note(
            path="test_note.md",
            name="test_note",
            content="# Test Note\n\nAuthor: John Doe"
        )
        
        variables = {"title": "Test Note", "author": "John Doe"}
        result = await extensions.create_note_from_template(
            "test_template",
            "test_note.md",
            variables
        )
        
        # Check that create_note was called with processed content
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert "Test Note" in call_args[0][1]  # content argument
        assert "John Doe" in call_args[0][1]


@pytest.mark.asyncio
async def test_analyze_links(extensions):
    """Test link analysis."""
    notes = [
        Note(
            path="note1.md",
            name="note1",
            content="This links to [[note2]] and [external](note3.md)"
        ),
        Note(
            path="note2.md",
            name="note2",
            content="This links to [[note1]]"
        ),
    ]
    
    with patch.object(extensions.client, 'list_notes', new_callable=AsyncMock) as mock_list:
        with patch.object(extensions.client, 'get_note', new_callable=AsyncMock) as mock_get:
            mock_list.return_value = ["note1.md", "note2.md"]
            mock_get.side_effect = notes
            
            links = await extensions.analyze_links()
            
            assert len(links) >= 2  # At least wikilinks
            
            # Check for wikilink
            wikilinks = [link for link in links if link.link_type == "wikilink"]
            assert len(wikilinks) >= 2
            
            # Check for markdown link
            markdown_links = [link for link in links if link.link_type == "markdown"]
            assert len(markdown_links) >= 1


@pytest.mark.asyncio
async def test_find_orphaned_notes(extensions):
    """Test finding orphaned notes."""
    with patch.object(extensions, 'analyze_links', new_callable=AsyncMock) as mock_analyze:
        with patch.object(extensions.client, 'list_notes', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = ["note1.md", "note2.md", "note3.md"]
            mock_analyze.return_value = [
                MagicMock(target="note1"),
                MagicMock(target="note2.md"),
            ]
            
            orphaned = await extensions.find_orphaned_notes()
            
            # note3.md should be orphaned (not linked to)
            assert "note3.md" in orphaned


@pytest.mark.asyncio
async def test_generate_vault_stats(extensions):
    """Test vault statistics generation."""
    notes = [
        Note(
            path="note1.md",
            name="note1",
            content="This is a test note with some words.",
            metadata=NoteMetadata(tags=["test", "example"])
        ),
        Note(
            path="note2.md",
            name="note2",
            content="Another note with different content.",
            metadata=NoteMetadata(tags=["test", "other"])
        ),
    ]
    
    with patch.object(extensions.client, 'list_notes', new_callable=AsyncMock) as mock_list:
        with patch.object(extensions.client, 'get_note', new_callable=AsyncMock) as mock_get:
            with patch.object(extensions, 'analyze_links', new_callable=AsyncMock) as mock_analyze:
                with patch.object(extensions, 'find_orphaned_notes', new_callable=AsyncMock) as mock_orphaned:
                    mock_list.return_value = ["note1.md", "note2.md"]
                    mock_get.side_effect = notes
                    mock_analyze.return_value = []
                    mock_orphaned.return_value = []
                    
                    stats = await extensions.generate_vault_stats()
                    
                    assert stats.total_notes == 2
                    assert stats.total_words > 0
                    assert stats.total_characters > 0
                    assert "test" in stats.tag_distribution
                    assert stats.tag_distribution["test"] == 2  # appears in both notes


@pytest.mark.asyncio
async def test_search_by_word_count(extensions):
    """Test searching notes by word count."""
    notes = [
        Note(path="short.md", name="short", content="Short note."),
        Note(path="long.md", name="long", content="This is a much longer note with many more words than the short one."),
    ]
    
    with patch.object(extensions.client, 'list_notes', new_callable=AsyncMock) as mock_list:
        with patch.object(extensions.client, 'get_note', new_callable=AsyncMock) as mock_get:
            mock_list.return_value = ["short.md", "long.md"]
            mock_get.side_effect = notes
            
            # Search for notes with at least 10 words
            result = await extensions.search_by_word_count(min_words=10)
            
            assert len(result) == 1
            assert result[0].path == "long.md"
