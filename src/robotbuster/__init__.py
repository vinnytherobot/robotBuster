"""
RobotBuster - Modern, fast, and professional directory brute-force tool.
"""

__version__ = "2.1.0"
__author__ = "vinnytherobot"

from .core.scanner import RobotScanner
from .core.models import ScanConfig, ScanResult, ScanStats
from .core.exceptions import RobotBusterError, NetworkError, TimeoutError, ConfigurationError

__all__ = [
    "RobotScanner",
    "ScanConfig",
    "ScanResult",
    "ScanStats",
    "RobotBusterError",
    "NetworkError",
    "TimeoutError",
    "ConfigurationError",
]