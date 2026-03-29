"""Data models for RobotBuster."""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Set, Dict, Any
from pydantic import BaseModel, Field, field_validator

from .exceptions import ConfigurationError


@dataclass
class ScanResult:
    """Represents a single scan result."""

    url: str
    status_code: int
    content_length: int
    response_time: float
    title: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    body_preview: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.headers is None:
            self.headers = {}
        if self.body_preview and len(self.body_preview) > 200:
            self.body_preview = self.body_preview[:200] + "..."


class ScanConfig(BaseModel):
    """Configuration for scanning operations."""

    target: str = Field(..., description="Target URL to scan")
    wordlist: Path = Field(..., description="Path to wordlist file")
    concurrency: int = Field(default=20, ge=1, le=1000, description="Number of concurrent requests")
    timeout: float = Field(default=10.0, ge=1.0, le=300.0, description="Request timeout in seconds")
    status_codes: Set[int] = Field(
        default={200, 204, 301, 302, 307, 401, 403},
        description="Status codes to consider as findings"
    )
    output_file: Optional[Path] = Field(default=None, description="Output file for results")
    verbose: bool = Field(default=False, description="Enable verbose output")
    follow_redirects: bool = Field(default=False, description="Follow HTTP redirects")
    user_agent: str = Field(default="RobotBuster/2.1", description="Custom User-Agent string")
    delay: float = Field(default=0.0, ge=0.0, description="Delay between requests in seconds")
    max_redirects: int = Field(default=5, ge=0, description="Maximum redirects to follow")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")

    @field_validator('target')
    def validate_target(cls, v):
        """Validate target URL."""
        if not v.startswith(('http://', 'https://')):
            raise ConfigurationError("Target must start with http:// or https://")
        return v.rstrip('/')

    @field_validator('wordlist')
    def validate_wordlist(cls, v):
        """Validate wordlist file exists."""
        if not v.exists():
            raise ConfigurationError(f"Wordlist file not found: {v}")
        if not v.is_file():
            raise ConfigurationError(f"Wordlist path is not a file: {v}")
        return v

    @field_validator('headers')
    def validate_headers(cls, v):
        """Validate headers don't contain forbidden keys."""
        forbidden = {'host', 'connection', 'content-length'}
        for key in v:
            if key.lower() in forbidden:
                raise ConfigurationError(f"Header '{key}' is not allowed")
        return v

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Path: str,
            set: list,
        }


@dataclass
class ScanStats:
    """Statistics for a scan operation."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    findings: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        """Get scan duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def requests_per_second(self) -> float:
        """Get requests per second."""
        duration = self.duration
        if duration > 0:
            return self.total_requests / duration
        return 0.0

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_requests > 0:
            return (self.successful_requests / self.total_requests) * 100
        return 0.0


@dataclass
class WildcardInfo:
    """Information about wildcard responses."""

    status_code: Optional[int] = None
    content_length: Optional[int] = None
    content: Optional[str] = None
    detected: bool = False

    def matches(self, status_code: int, content_length: int) -> bool:
        """Check if a response matches the wildcard pattern."""
        if not self.detected:
            return False
        return (
            self.status_code == status_code
            and self.content_length == content_length
        )