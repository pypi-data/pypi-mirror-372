"""Utility functions for the Google Colab MCP server."""

import json
import logging
import os
import time
from typing import Any, Dict, Optional
from pathlib import Path


def safe_message_format(message: str) -> str:
    """Format message safely for different console encodings."""
    try:
        # Try to encode with current console encoding
        import sys
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
            message.encode(sys.stdout.encoding)
        return message
    except (UnicodeEncodeError, AttributeError):
        # Fallback: replace problematic Unicode characters
        replacements = {
            '✅': '[OK]',
            '❌': '[ERROR]', 
            '🔐': '[AUTH]',
            '🚀': '[START]',
            '📝': '[NOTE]',
            '🔧': '[SETUP]',
            '⚠️': '[WARNING]',
            '🌐': '[WEB]',
            '📱': '[DEVICE]',
            '💾': '[SAVE]',
            '🧪': '[TEST]',
            '📋': '[LIST]',
            '💡': '[TIP]',
            '🎉': '[SUCCESS]',
            '📁': '[FOLDER]',
            '🔄': '[REFRESH]',
            '🔗': '[LINK]'
        }
        
        for unicode_char, replacement in replacements.items():
            message = message.replace(unicode_char, replacement)
        
        return message


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    # If no config path provided, use user config directory
    if config_path is None:
        user_config_dir = os.path.expanduser("~/.mcp-colab")
        config_path = os.path.join(user_config_dir, "server_config.json")
    
    try:
        # If path is relative, make it absolute relative to user config directory
        if not os.path.isabs(config_path):
            user_config_dir = os.path.expanduser("~/.mcp-colab")
            config_path = os.path.join(user_config_dir, config_path)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        # Expand user paths in config
        if "google_api" in config:
            for key in ["credentials_file", "token_file"]:
                if key in config["google_api"]:
                    config["google_api"][key] = os.path.expanduser(config["google_api"][key])
        
        if "logging" in config and "file" in config["logging"]:
            config["logging"]["file"] = os.path.expanduser(config["logging"]["file"])
            # Ensure log directory exists
            log_dir = os.path.dirname(config["logging"]["file"])
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
        
        return config
        
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        # Return default configuration with user home paths
        user_config_dir = os.path.expanduser("~/.mcp-colab")
        return {
            "server": {"host": "localhost", "port": 8080, "debug": True},
            "selenium": {"browser": "chrome", "headless": False, "timeout": 30, "implicit_wait": 10, "page_load_timeout": 30},
            "colab": {"base_url": "https://colab.research.google.com", "execution_timeout": 300, "max_retries": 3, "retry_delay": 5},
            "google_api": {
                "scopes": ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"],
                "credentials_file": os.path.join(user_config_dir, "credentials.json"),
                "token_file": os.path.join(user_config_dir, "token.json")
            },
            "logging": {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "file": os.path.join(user_config_dir, "logs", "colab_mcp.log")}
        }
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return {}


def setup_logging(config: Dict[str, Any]) -> None:
    """Set up logging configuration."""
    log_config = config.get("logging", {})
    level = getattr(logging, log_config.get("level", "INFO"))
    format_str = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get("file")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=level, format=format_str)


def retry_with_backoff(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logging.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logging.warning(f"Function {func.__name__} failed (attempt {retries}/{max_retries}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator


def validate_notebook_id(notebook_id: str) -> bool:
    """Validate Google Drive file ID format."""
    if not notebook_id or not isinstance(notebook_id, str):
        return False
    
    # Google Drive file IDs are typically 33-44 characters long
    # and contain alphanumeric characters, hyphens, and underscores
    import re
    pattern = r'^[a-zA-Z0-9_-]{25,50}$'
    return bool(re.match(pattern, notebook_id))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    return sanitized


def create_notebook_content(cells: list = None) -> Dict[str, Any]:
    """Create a basic Colab notebook structure."""
    if cells is None:
        cells = []
    
    return {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "provenance": [],
                "collapsed_sections": []
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": cells
    }


def create_code_cell(source: str, outputs: list = None) -> Dict[str, Any]:
    """Create a code cell for a notebook."""
    if outputs is None:
        outputs = []
    
    return {
        "cell_type": "code",
        "source": source.split('\n') if isinstance(source, str) else source,
        "metadata": {},
        "execution_count": None,
        "outputs": outputs
    }


def create_text_cell(source: str, cell_type: str = "markdown") -> Dict[str, Any]:
    """Create a text cell (markdown or raw) for a notebook."""
    return {
        "cell_type": cell_type,
        "source": source.split('\n') if isinstance(source, str) else source,
        "metadata": {}
    }


def extract_error_message(error: Exception) -> str:
    """Extract a clean error message from an exception."""
    error_msg = str(error)
    # Remove common prefixes that aren't useful for users
    prefixes_to_remove = [
        "Message: ",
        "selenium.common.exceptions.",
        "googleapiclient.errors.",
    ]
    
    for prefix in prefixes_to_remove:
        if error_msg.startswith(prefix):
            error_msg = error_msg[len(prefix):]
    
    return error_msg


def ensure_directory_exists(path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def is_valid_python_code(code: str) -> bool:
    """Check if the provided string is valid Python code."""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False


def format_execution_time(seconds: float) -> str:
    """Format execution time in a human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"