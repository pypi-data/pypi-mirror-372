# This file is kept for backward compatibility
# The main configuration is now in pyproject.toml

from setuptools import setup

# Import version from package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from mcp_colab_server import __version__
except ImportError:
    __version__ = "1.0.0"

setup(
    name="google-colab-mcp",
    version=__version__,
    author="inkbytefo",
    description="Model Context Protocol server for Google Colab integration",
    long_description="Please see pyproject.toml for full configuration",
    python_requires=">=3.8",
)