"""Unit tests for the RobotScanner class."""

import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path

from robotbuster.core.scanner import RobotScanner
from robotbuster.core.models import ScanConfig, ScanResult


@pytest.mark.asyncio
async def test_scanner_init(mock_config):
    """Test scanner initialization."""
    async with RobotScanner(mock_config) as scanner:
        assert scanner.config == mock_config
        assert scanner.stats.total_requests == 0
        assert scanner.stats.findings == 0
        assert scanner.client is not None


@pytest.mark.asyncio
async def test_calibrate_no_wildcard(mock_config):
    """Test calibration when no wildcard is detected."""
    async with RobotScanner(mock_config) as scanner:
        # Mock httpx client response
        with patch.object(scanner.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.content = b"Not Found"
            
            wildcard = await scanner.calibrate()
            
            assert not wildcard.detected
            assert wildcard.status_code is None


@pytest.mark.asyncio
async def test_calibrate_with_wildcard(mock_config):
    """Test calibration when a wildcard is detected."""
    async with RobotScanner(mock_config) as scanner:
        with patch.object(scanner.client, 'get', new_callable=AsyncMock) as mock_get:
            # Server returns 200 for everything
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"Wildcard Page"
            mock_get.return_value.text = "Wildcard Page"
            
            wildcard = await scanner.calibrate()
            
            assert wildcard.detected
            assert wildcard.status_code == 200
            assert wildcard.content_length == len(b"Wildcard Page")


@pytest.mark.asyncio
async def test_check_route_finding(mock_config):
    """Test checking a route that exists."""
    async with RobotScanner(mock_config) as scanner:
        with patch.object(scanner.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"Admin Panel"
            mock_get.return_value.text = "Admin Panel"
            mock_get.return_value.headers = {"content-type": "text/html"}
            
            result = await scanner.check_route("admin")
            
            assert result is not None
            assert result.status_code == 200
            assert "admin" in result.url
            assert scanner.stats.findings == 1


@pytest.mark.asyncio
async def test_check_route_not_found(mock_config):
    """Test checking a route that doesn't exist."""
    async with RobotScanner(mock_config) as scanner:
        with patch.object(scanner.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.content = b"Not Found"
            
            result = await scanner.check_route("nonexistent")
            
            assert result is None
            assert scanner.stats.findings == 0
