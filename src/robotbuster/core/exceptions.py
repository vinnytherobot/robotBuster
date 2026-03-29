"""Custom exceptions for RobotBuster."""


class RobotBusterError(Exception):
    """Base exception for RobotBuster errors."""
    pass


class ConfigurationError(RobotBusterError):
    """Raised when there's an error in configuration."""
    pass


class NetworkError(RobotBusterError):
    """Raised when network-related errors occur."""
    pass


class WordlistError(RobotBusterError):
    """Raised when there's an error with the wordlist."""
    pass


class ScanError(RobotBusterError):
    """Raised when scanning fails."""
    pass


class TimeoutError(NetworkError):
    """Raised when a request times out."""
    pass


class ConnectionError(NetworkError):
    """Raised when connection fails."""
    pass


class HTTPError(NetworkError):
    """Raised when HTTP error occurs."""
    pass


class WildcardDetected(RobotBusterError):
    """Warning raised when wildcard responses are detected."""
    pass