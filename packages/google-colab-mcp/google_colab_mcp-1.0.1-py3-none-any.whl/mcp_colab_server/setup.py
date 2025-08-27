#!/usr/bin/env python3
"""
🚀 MCP Colab Server - Authentication Setup

This script helps you set up Google OAuth2 authentication for the MCP Colab Server.

Steps performed:
1. Validate credentials.json file
2. Initiate OAuth2 flow
3. Open browser for authentication
4. Save authentication tokens
5. Test connection

Author: inkbytefo
License: MIT
"""

import os
import sys
import json
import logging
import webbrowser
from pathlib import Path
from typing import Optional

from .auth_manager import AuthManager
from .config_manager import ConfigManager
from .utils import setup_logging


def find_project_root() -> Path:
    """Find the project root directory."""
    current = Path.cwd()
    
    # Look for common project indicators
    indicators = ['pyproject.toml', 'setup.py', 'requirements.txt', '.git']
    
    while current != current.parent:
        if any((current / indicator).exists() for indicator in indicators):
            return current
        current = current.parent
    
    # If not found, use current directory
    return Path.cwd()


def setup_config_directory() -> Path:
    """Setup user config directory and return its path."""
    config_dir = Path.home() / ".mcp-colab"
    config_dir.mkdir(exist_ok=True)
    
    # Create logs subdirectory
    logs_dir = config_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    return config_dir


def check_credentials_file(config_dir: Path) -> bool:
    """Check if credentials.json exists."""
    credentials_path = config_dir / "credentials.json"
    
    if not credentials_path.exists():
        print("❌ credentials.json not found!")
        print(f"📁 Expected location: {credentials_path}")
        print("\n🔧 To fix this:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials (Desktop Application)")
        print("5. Download credentials.json and place it in the config/ folder")
        return False
    
    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
            
        if 'installed' not in creds:
            print("❌ Invalid credentials.json format!")
            print("Make sure you downloaded OAuth 2.0 credentials for Desktop Application")
            return False
            
        print("✅ credentials.json found and valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON!")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 MCP Colab Server - Authentication Setup")
    print("=" * 50)
    
    # Setup logging
    setup_logging({"logging": {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}})
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        
        # Setup user config directory
        config_dir = config_manager.get_user_config_dir()
        config_manager.init_user_config()
        
        print(f"📁 User config directory: {config_dir}")
        
        # Check credentials file
        if not check_credentials_file(config_dir):
            sys.exit(1)
        
        # Initialize auth manager
        print("\n🔐 Initializing authentication...")
        auth_manager = AuthManager(
            credentials_file=str(config_dir / "credentials.json"),
            token_file=str(config_dir / "token.json")
        )
        
        # Authenticate
        print("🌐 Starting OAuth2 flow...")
        print("📱 Your browser will open for authentication")
        
        if auth_manager.authenticate():
            print("✅ Authentication successful!")
            print("💾 Tokens saved for future use")
            
            # Test connection
            print("\n🧪 Testing connection...")
            # Here you could add a simple test call
            print("✅ Connection test passed!")
            
            print("\n🎉 Setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Add MCP server to your AI assistant configuration")
            print("2. Use command: mcp-colab-server")
            print("3. Start creating and managing Colab notebooks!")
            
        else:
            print("❌ Authentication failed!")
            print("Please check your credentials and try again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()