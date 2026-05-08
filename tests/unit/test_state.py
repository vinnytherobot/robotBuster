"""Tests for state management (resume functionality)."""

import json
import pytest
from pathlib import Path

from robotbuster.core.state import ScanState, StateManager
from robotbuster.core.models import ScanConfig


class TestScanState:
    """Tests for ScanState class."""

    def test_scan_state_creation(self):
        """Test ScanState creation."""
        state = ScanState(total_routes=100)
        assert state.total_routes == 100
        assert state.completed_routes == 0
        assert state.wildcard_detected is False
        assert len(state.scanned_routes) == 0

    def test_add_scanned_route(self):
        """Test adding scanned route."""
        state = ScanState(total_routes=100)
        state.add_scanned_route("/admin")
        assert "/admin" in state.scanned_routes
        assert state.completed_routes == 1

    def test_is_route_scanned(self):
        """Test checking if route was scanned."""
        state = ScanState(total_routes=100)
        state.add_scanned_route("/admin")
        assert state.is_route_scanned("/admin") is True
        assert state.is_route_scanned("/api") is False

    def test_get_progress(self):
        """Test progress calculation."""
        state = ScanState(total_routes=100)
        assert state.get_progress() == 0.0
        state.completed_routes = 50
        assert state.get_progress() == 50.0
        state.total_routes = 0
        assert state.get_progress() == 0.0

    def test_serialization(self):
        """Test state serialization."""
        state = ScanState(total_routes=100)
        state.add_scanned_route("/admin")

        data = state.to_dict()
        assert "scanned_routes" in data
        assert "/admin" in data["scanned_routes"]

    def test_deserialization(self):
        """Test state deserialization."""
        data = {
            "scanned_routes": ["/admin", "/api"],
            "found_routes": [],
            "total_routes": 100,
            "completed_routes": 2,
            "wildcard_detected": False,
        }
        state = ScanState.from_dict(data)
        assert "/admin" in state.scanned_routes
        assert "/api" in state.scanned_routes


class TestStateManager:
    """Tests for StateManager class."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for tests."""
        return tmp_path

    @pytest.fixture
    def test_wordlist(self):
        """Get test wordlist path."""
        return Path("tests/fixtures/test_wordlist.txt")

    def test_create_state(self, temp_dir, test_wordlist):
        """Test creating new state."""
        manager = StateManager(temp_dir)
        config = ScanConfig(
            target="http://example.com",
            wordlist=test_wordlist,
        )
        state = manager.create_state(config, total_routes=100)

        assert state.total_routes == 100
        assert manager.current_state is not None

    def test_save_and_load_state(self, temp_dir, test_wordlist):
        """Test saving and loading state."""
        manager = StateManager(temp_dir)
        config = ScanConfig(
            target="http://example.com",
            wordlist=test_wordlist,
        )
        state = manager.create_state(config, total_routes=100)
        state.add_scanned_route("/admin")

        saved_path = manager.save_state()
        assert saved_path.exists()

        # Load state
        manager2 = StateManager(temp_dir)
        loaded_state = manager2.load_state(saved_path)
        assert "/admin" in loaded_state.scanned_routes

    def test_get_state_file_for_target(self, temp_dir):
        """Test state file path generation."""
        manager = StateManager(temp_dir)
        path = manager.get_state_file_for_target("http://example.com")
        assert "example.com" in str(path)

    def test_has_previous_state(self, temp_dir, test_wordlist):
        """Test checking for previous state."""
        manager = StateManager(temp_dir)
        config = ScanConfig(
            target="http://example.com",
            wordlist=test_wordlist,
        )
        state = manager.create_state(config, total_routes=100)
        manager.save_state()

        manager2 = StateManager(temp_dir)
        assert manager2.has_previous_state("http://example.com") is True
        assert manager2.has_previous_state("http://other.com") is False