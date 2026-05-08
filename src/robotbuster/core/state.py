"""Scan state management for resume functionality."""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Set, List
from datetime import datetime

from .models import ScanConfig, ScanResult


@dataclass
class ScanState:
    """Manages scan state for resume functionality."""

    config: Optional[dict] = None
    scanned_routes: Set[str] = field(default_factory=set)
    found_routes: List[dict] = field(default_factory=list)
    wildcard_status: Optional[int] = None
    wildcard_content_length: Optional[int] = None
    wildcard_detected: bool = False
    total_routes: int = 0
    completed_routes: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_scanned_route(self, route: str) -> None:
        """Mark a route as scanned."""
        self.scanned_routes.add(route)
        self.completed_routes += 1
        self.updated_at = datetime.now().isoformat()

    def add_finding(self, result: ScanResult) -> None:
        """Add a finding to the state."""
        self.found_routes.append(asdict(result))
        self.updated_at = datetime.now().isoformat()

    def is_route_scanned(self, route: str) -> bool:
        """Check if a route has been scanned."""
        return route in self.scanned_routes

    def get_progress(self) -> float:
        """Get scan progress as percentage."""
        if self.total_routes > 0:
            return (self.completed_routes / self.total_routes) * 100
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        # Handle non-serializable config fields
        config_serializable: Optional[dict[str, Any]] = None
        if self.config:
            config_serializable = {}
            for k, v in self.config.items():
                if hasattr(v, '__class__') and v.__class__.__name__ == 'WindowsPath':
                    config_serializable[k] = str(v)
                elif isinstance(v, set):
                    config_serializable[k] = list(v)
                else:
                    config_serializable[k] = v

        return {
            "config": config_serializable,
            "scanned_routes": list(self.scanned_routes),
            "found_routes": self.found_routes,
            "wildcard_status": self.wildcard_status,
            "wildcard_content_length": self.wildcard_content_length,
            "wildcard_detected": self.wildcard_detected,
            "total_routes": self.total_routes,
            "completed_routes": self.completed_routes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScanState":
        """Create state from dictionary."""
        state = cls()
        state.config = data.get("config")
        state.scanned_routes = set(data.get("scanned_routes", []))
        state.found_routes = data.get("found_routes", [])
        state.wildcard_status = data.get("wildcard_status")
        state.wildcard_content_length = data.get("wildcard_content_length")
        state.wildcard_detected = data.get("wildcard_detected", False)
        state.total_routes = data.get("total_routes", 0)
        state.completed_routes = data.get("completed_routes", 0)
        state.created_at = data.get("created_at", datetime.now().isoformat())
        state.updated_at = data.get("updated_at", datetime.now().isoformat())
        return state


class StateManager:
    """Manages saving and loading scan state."""

    def __init__(self, state_dir: Optional[Path] = None):
        """Initialize state manager.

        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = state_dir or Path.cwd()
        self._current_state: Optional[ScanState] = None

    def create_state(self, config: ScanConfig, total_routes: int) -> ScanState:
        """Create a new scan state.

        Args:
            config: Scan configuration
            total_routes: Total number of routes to scan

        Returns:
            New ScanState instance
        """
        self._current_state = ScanState(
            config=config.model_dump(),
            total_routes=total_routes,
        )
        return self._current_state

    def load_state(self, state_file: Path) -> ScanState:
        """Load scan state from file.

        Args:
            state_file: Path to state file

        Returns:
            Loaded ScanState
        """
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._current_state = ScanState.from_dict(data)
        return self._current_state

    def save_state(self, state_file: Optional[Path] = None) -> Path:
        """Save current state to file.

        Args:
            state_file: Optional custom state file path

        Returns:
            Path to saved state file
        """
        if not self._current_state:
            raise ValueError("No current state to save")

        if state_file is None:
            # Use target-based state file
            if self._current_state.config:
                target = self._current_state.config.get("target", "")
                state_file = self.get_state_file_for_target(target)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                state_file = self.state_dir / f"scan_state_{timestamp}.json"

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self._current_state.to_dict(), f, indent=2)

        return state_file

    def get_state_file_for_target(self, target: str) -> Path:
        """Get state file path for a target.

        Args:
            target: Target URL

        Returns:
            Path to state file
        """
        # Extract domain from target
        from urllib.parse import urlparse
        domain = urlparse(target).netloc.replace(":", "_")
        return self.state_dir / f"scan_state_{domain}.json"

    def has_previous_state(self, target: str) -> bool:
        """Check if there's a previous state for target.

        Args:
            target: Target URL

        Returns:
            True if state exists
        """
        state_file = self.get_state_file_for_target(target)
        return state_file.exists()

    def load_previous_state(self, target: str) -> Optional[ScanState]:
        """Load previous state for target if exists.

        Args:
            target: Target URL

        Returns:
            ScanState if exists, None otherwise
        """
        state_file = self.get_state_file_for_target(target)
        if state_file.exists():
            return self.load_state(state_file)
        return None

    @property
    def current_state(self) -> Optional[ScanState]:
        """Get current state."""
        return self._current_state