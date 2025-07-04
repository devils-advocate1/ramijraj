"""
EthicalDRM - A lightweight content protection toolkit for independent creators.
"""

__version__ = "1.0.0"
__author__ = "Ramij Raj"
__email__ = "ramijraj31@gmail.com"

from .core.encryption import VideoEncryption
from .core.token_manager import TokenManager
from .core.stream_server import StreamServer
from .utils.security import SecurityUtils
from .detectors.leak_detector import LeakDetector

__all__ = [
    "VideoEncryption",
    "TokenManager", 
    "StreamServer",
    "SecurityUtils",
    "LeakDetector",
]