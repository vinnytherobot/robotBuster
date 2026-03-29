"""Pytest configuration and fixtures for RobotBuster tests."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from robotbuster.core.models import ScanConfig, ScanResult


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Create a mock ScanConfig for testing."""
    return ScanConfig(
        target="http://example.com",
        wordlist=Path("tests/fixtures/test_wordlist.txt"),
        concurrency=10,
        timeout=5.0,
        status_codes=[200, 403],
        output_file=None,
        verbose=False,
        follow_redirects=False,
        user_agent="RobotBuster/2.1-test",
    )


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    client = AsyncMock()
    client.get.return_value.status_code = 200
    client.get.return_value.content = b"OK"
    client.get.return_value.headers = {"content-length": "2"}
    return client


@pytest.fixture
def sample_scan_results():
    """Create sample scan results for testing."""
    return [
        ScanResult(
            url="http://example.com/admin",
            status_code=200,
            content_length=1024,
            response_time=0.123,
        ),
        ScanResult(
            url="http://example.com/backup",
            status_code=403,
            content_length=512,
            response_time=0.089,
        ),
    ]


@pytest.fixture
def config_dict():
    """Sample configuration dictionary."""
    return {
        "target": "http://example.com",
        "wordlist": "common.txt",
        "concurrency": 20,
        "timeout": 10.0,
        "status_codes": [200, 204, 301, 302, 307, 401, 403],
        "output_file": None,
        "verbose": False,
        "follow_redirects": False,
        "user_agent": "RobotBuster/2.1",
    }


@pytest.fixture
def temp_wordlist(tmp_path):
    """Create a temporary wordlist file for testing."""
    wordlist_path = tmp_path / "test_wordlist.txt"
    wordlist_path.write_text("\n".join(["admin", "test", "api", "backup"]))
    return wordlist_path