"""Unit tests for data models."""

import pytest
from robotbuster.core.models import RateLimitInfo, WildcardInfo, ScanStats, ScanResult


class TestRateLimitInfo:
    """Tests for RateLimitInfo class."""

    def test_handle_429_sets_detected(self):
        """Test that handle_429 sets detected flag."""
        rate_limit = RateLimitInfo()
        rate_limit.handle_429()
        assert rate_limit.detected is True
        assert rate_limit.consecutive_429s == 1

    def test_handle_429_with_retry_after(self):
        """Test handle_429 with retry-after header."""
        rate_limit = RateLimitInfo()
        backoff = rate_limit.handle_429(retry_after=30)
        assert backoff == 30.0
        assert rate_limit.retry_after == 30

    def test_handle_429_increments_backoff(self):
        """Test that handle_429 increments backoff factor."""
        rate_limit = RateLimitInfo()
        rate_limit.handle_429()
        first_backoff = rate_limit.backoff_factor
        rate_limit.handle_429()
        assert rate_limit.backoff_factor > first_backoff

    def test_reset_clears_all_state(self):
        """Test that reset clears all rate limit state."""
        rate_limit = RateLimitInfo()
        rate_limit.handle_429(retry_after=30)
        rate_limit.reset()

        assert rate_limit.detected is False
        assert rate_limit.consecutive_429s == 0
        assert rate_limit.backoff_factor == 1.0
        assert rate_limit.retry_after is None

    def test_get_backoff_uses_retry_after(self):
        """Test get_backoff uses retry_after when set."""
        rate_limit = RateLimitInfo()
        rate_limit.handle_429(retry_after=60)
        backoff = rate_limit.get_backoff()
        assert backoff == 60.0


class TestWildcardInfo:
    """Tests for WildcardInfo class."""

    def test_matches_returns_false_when_not_detected(self):
        """Test matches returns False when wildcard not detected."""
        wildcard = WildcardInfo()
        assert wildcard.matches(200, 1000) is False

    def test_matches_returns_true_on_match(self):
        """Test matches returns True when status and content match."""
        wildcard = WildcardInfo(status_code=200, content_length=1000, detected=True)
        assert wildcard.matches(200, 1000) is True

    def test_matches_returns_false_on_mismatch(self):
        """Test matches returns False when status or content differs."""
        wildcard = WildcardInfo(status_code=200, content_length=1000, detected=True)
        assert wildcard.matches(200, 500) is False
        assert wildcard.matches(404, 1000) is False


class TestScanStats:
    """Tests for ScanStats class."""

    def test_duration_returns_time_when_not_ended(self):
        """Test duration returns current elapsed time when scan not ended."""
        import time
        stats = ScanStats()
        time.sleep(0.01)  # Small delay
        duration = stats.duration
        assert duration > 0

    def test_requests_per_second_calculates_correctly(self):
        """Test requests per second calculation."""
        stats = ScanStats()
        stats.total_requests = 100
        stats.start_time = stats.start_time - 10  # 10 seconds ago
        assert stats.requests_per_second == 10.0

    def test_success_rate_calculates_correctly(self):
        """Test success rate calculation."""
        stats = ScanStats()
        stats.total_requests = 100
        stats.successful_requests = 75
        assert stats.success_rate == 75.0