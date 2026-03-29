"""Unit tests for the WordlistManager class."""

import pytest
from pathlib import Path

from robotbuster.utils.wordlist import WordlistManager


def test_wordlist_sync_load(temp_wordlist):
    """Test synchronous wordlist loading."""
    manager = WordlistManager()
    routes = manager._sync_load_wordlist(temp_wordlist)
    
    assert len(routes) == 4
    assert "admin" in routes
    assert "test" in routes
    assert "api" in routes
    assert "backup" in routes
    # Verify sorted/unique
    assert routes == sorted(list(set(routes)))


@pytest.mark.asyncio
async def test_wordlist_async_load(temp_wordlist):
    """Test asynchronous wordlist loading."""
    manager = WordlistManager()
    routes = await manager.load_wordlist(temp_wordlist)
    
    assert len(routes) == 4
    assert "admin" in routes


def test_append_extensions():
    """Test appending extensions to routes."""
    manager = WordlistManager()
    routes = ["admin", "test"]
    extensions = [".php", "html"]
    
    expanded = manager.append_extensions(routes, extensions)
    
    assert "admin.php" in expanded
    assert "admin.html" in expanded
    assert "test.php" in expanded
    assert "test.html" in expanded
    assert len(expanded) == 6 # 2 base + 4 with extensions


def test_filter_extensions():
    """Test filtering routes by extensions."""
    manager = WordlistManager()
    routes = ["admin", "admin.php", "test.html", "config.json", "css/style.css"]
    
    # Filter only .php and .html
    filtered = manager.filter_extensions(routes, {".php", "html"})
    
    assert "admin.php" in filtered
    assert "test.html" in filtered
    assert "admin" in filtered # Directories usually kept
    assert "config.json" not in filtered
    assert "css/style.css" not in filtered
