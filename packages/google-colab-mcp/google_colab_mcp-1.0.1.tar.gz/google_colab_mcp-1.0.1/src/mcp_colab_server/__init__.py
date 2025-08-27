"""
MCP Colab Server - Model Context Protocol server for Google Colab integration.

This package provides a comprehensive MCP server that enables AI assistants
to interact with Google Colab notebooks seamlessly.

Author: inkbytefo
License: MIT
"""

__version__ = "1.0.1"
__author__ = "inkbytefo"
__email__ = "contact@inkbytefo.dev"

from .server import main as server_main
from .auth_manager import AuthManager
from .config_manager import ConfigManager
from .utils import setup_logging

__all__ = [
    "server_main",
    "AuthManager",
    "ConfigManager",
    "setup_logging",
    "__version__",
    "__author__",
    "__email__",
]