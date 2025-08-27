#!/usr/bin/env python3
"""
🔧 MCP Colab Server - Configuration Manager

This script helps manage user configuration for the MCP Colab Server.

Features:
- Initialize user config directory
- Create default configuration files
- Copy credentials from project to user directory
- Validate configuration
- Reset configuration

Author: inkbytefo
License: MIT
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from .utils import safe_message_format
except ImportError:
    # Fallback if utils is not available
    def safe_message_format(message: str) -> str:
        """Fallback safe message formatter."""
        replacements = {
            '\u2705': '[OK]',
            '\u274c': '[ERROR]', 
            '\ud83d\udd10': '[AUTH]',
            '\ud83d\ude80': '[START]',
            '\ud83d\udcdd': '[NOTE]',
            '\ud83d\udd27': '[SETUP]',
        }
        for unicode_char, replacement in replacements.items():
            message = message.replace(unicode_char, replacement)
        return message


class ConfigManager:
    """Manages user configuration for MCP Colab Server."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.user_config_dir = Path.home() / ".mcp-colab"
        self.logger = logging.getLogger(__name__)
        
    def get_user_config_dir(self) -> Path:
        """Get the user configuration directory."""
        return self.user_config_dir
    
    def init_user_config(self, force: bool = False) -> bool:
        """Initialize user configuration directory and files."""
        try:
            # Create user config directory
            self.user_config_dir.mkdir(exist_ok=True)
            
            # Create logs subdirectory
            logs_dir = self.user_config_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Create default server config if it doesn't exist or force is True
            config_file = self.user_config_dir / "server_config.json"
            if not config_file.exists() or force:
                self._create_default_config(config_file)
            
            # Create credentials template if credentials.json doesn't exist
            credentials_file = self.user_config_dir / "credentials.json"
            if not credentials_file.exists():
                self._create_credentials_template(credentials_file)
            
            print(safe_message_format(f"✅ User configuration initialized at: {self.user_config_dir}"))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize user config: {e}")
            print(safe_message_format(f"❌ Failed to initialize user config: {e}"))
            return False
    
    def _create_default_config(self, config_file: Path) -> None:
        """Create default server configuration."""
        # Try to use the packaged template first
        packaged_template = Path(__file__).parent / "templates" / "server_config.json"
        
        if packaged_template.exists():
            with open(packaged_template, 'r') as f:
                template_config = json.load(f)
            
            # Update paths to use user config directory
            template_config["google_api"]["credentials_file"] = str(self.user_config_dir / "credentials.json")
            template_config["google_api"]["token_file"] = str(self.user_config_dir / "token.json")
            template_config["logging"]["file"] = str(self.user_config_dir / "logs" / "colab_mcp.log")
            
            with open(config_file, 'w') as f:
                json.dump(template_config, f, indent=2)
            
            print(safe_message_format(f"📝 Created configuration from template: {config_file}"))
        else:
            # Fallback to creating default config directly
            default_config = self._get_fallback_config()
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(safe_message_format(f"📝 Created default configuration: {config_file}"))
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration when template is not available."""
        return {
            "server": {
                "host": "localhost",
                "port": 8080,
                "debug": True
            },
            "selenium": {
                "browser": "chrome",
                "headless": False,
                "timeout": 30,
                "implicit_wait": 10,
                "page_load_timeout": 30,
                "use_undetected_chrome": False,
                "use_stealth": False,
                "profile": {
                    "use_persistent_profile": True,
                    "profile_name": "default",
                    "auto_create_profile": True
                },
                "anti_detection": {
                    "disable_automation_indicators": True,
                    "custom_user_agent": True,
                    "disable_images": False,
                    "random_delays": True
                },
                "retry_config": {
                    "max_retries": 3,
                    "retry_delay": 2,
                    "exponential_backoff": True
                }
            },
            "colab": {
                "base_url": "https://colab.research.google.com",
                "execution_timeout": 300,
                "max_retries": 3,
                "retry_delay": 5
            },
            "google_api": {
                "scopes": [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/drive.file"
                ],
                "credentials_file": str(self.user_config_dir / "credentials.json"),
                "token_file": str(self.user_config_dir / "token.json")
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": str(self.user_config_dir / "logs" / "colab_mcp.log")
            }
        }
    
    def _create_credentials_template(self, credentials_file: Path) -> None:
        """Create credentials template file."""
        # Try to use the packaged template first
        packaged_template = Path(__file__).parent / "templates" / "credentials_template.json"
        
        if packaged_template.exists():
            template_file = self.user_config_dir / "credentials.json.template"
            shutil.copy2(packaged_template, template_file)
            print(safe_message_format(f"📝 Created credentials template from package: {template_file}"))
        else:
            # Fallback to creating template content directly
            template_content = {
                "installed": {
                    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                    "project_id": "your-project-id",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "YOUR_CLIENT_SECRET",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            template_file = self.user_config_dir / "credentials.json.template"
            with open(template_file, 'w') as f:
                json.dump(template_content, f, indent=2)
            print(safe_message_format(f"📝 Created credentials template: {template_file}"))
        
        print(safe_message_format("🔧 Setup Instructions:"))
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials (Desktop Application)")
        print("5. Download credentials.json and replace the template file")
    
    def copy_project_credentials(self, project_path: Optional[str] = None) -> bool:
        """Copy credentials from project directory to user directory."""
        try:
            if project_path is None:
                # Try to find project credentials in common locations
                possible_paths = [
                    Path.cwd() / "credentials.json",
                    Path(__file__).parent / "templates" / "credentials_template.json",
                ]
            else:
                possible_paths = [Path(project_path) / "credentials.json"]
            
            source_file = None
            for path in possible_paths:
                if path.exists():
                    source_file = path
                    break
            
            if source_file is None:
                print(safe_message_format("❌ No project credentials.json found"))
                print(safe_message_format("💡 Use the template at ~/.mcp-colab/credentials.json.template"))
                return False
            
            dest_file = self.user_config_dir / "credentials.json"
            shutil.copy2(source_file, dest_file)
            
            print(safe_message_format(f"✅ Copied credentials from {source_file} to {dest_file}"))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy credentials: {e}")
            print(safe_message_format(f"❌ Failed to copy credentials: {e}"))
            return False
    
    def validate_config(self) -> bool:
        """Validate user configuration."""
        try:
            config_file = self.user_config_dir / "server_config.json"
            credentials_file = self.user_config_dir / "credentials.json"
            
            # Check if config file exists and is valid JSON
            if not config_file.exists():
                print("❌ server_config.json not found")
                return False
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ["server", "google_api", "logging"]
            for section in required_sections:
                if section not in config:
                    print(f"❌ Missing required section: {section}")
                    return False
            
            print("✅ server_config.json is valid")
            
            # Check credentials file
            if not credentials_file.exists():
                print("❌ credentials.json not found")
                print("Run 'python -m mcp_colab_server.config_manager --init' to create template")
                return False
            
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
            
            if 'installed' not in creds:
                print("❌ Invalid credentials.json format")
                return False
            
            # Check if it's still a template
            if creds['installed']['client_id'].startswith('YOUR_'):
                print("⚠️  credentials.json is still a template - please update with real values")
                return False
            
            print("✅ credentials.json is valid")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            print(f"❌ Validation failed: {e}")
            return False
    
    def reset_config(self, confirm: bool = False) -> bool:
        """Reset user configuration (removes all files)."""
        if not confirm:
            response = input(f"⚠️  This will delete all files in {self.user_config_dir}. Continue? (y/N): ")
            if response.lower() != 'y':
                print("❌ Reset cancelled")
                return False
        
        try:
            if self.user_config_dir.exists():
                shutil.rmtree(self.user_config_dir)
            
            print(f"✅ Configuration reset. Directory {self.user_config_dir} removed.")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset config: {e}")
            print(f"❌ Failed to reset config: {e}")
            return False
    
    def show_status(self) -> None:
        """Show current configuration status."""
        print("🔧 MCP Colab Server - Configuration Status")
        print("=" * 50)
        print(f"📁 User config directory: {self.user_config_dir}")
        print(f"📁 Directory exists: {'✅' if self.user_config_dir.exists() else '❌'}")
        
        files_to_check = [
            ("server_config.json", "Server configuration"),
            ("credentials.json", "Google API credentials"),
            ("token.json", "OAuth2 tokens"),
            ("logs/colab_mcp.log", "Log file")
        ]
        
        for filename, description in files_to_check:
            file_path = self.user_config_dir / filename
            exists = file_path.exists()
            print(f"📄 {description}: {'✅' if exists else '❌'} ({file_path})")
        
        # Check Chrome profiles
        chrome_profiles_dir = self.user_config_dir / "chrome_profiles"
        print(f"\n🌐 Chrome Profiles:")
        print(f"📁 Profiles directory: {'✅' if chrome_profiles_dir.exists() else '❌'} ({chrome_profiles_dir})")
        
        if chrome_profiles_dir.exists():
            try:
                from .chrome_profile_manager import ChromeProfileManager
                profile_manager = ChromeProfileManager(str(self.user_config_dir))
                profiles = profile_manager.list_profiles()
                total_size = profile_manager.get_total_profiles_size()
                
                print(f"📊 Total profiles: {len(profiles)}")
                print(f"📊 Total size: {total_size:.2f} MB")
                
                for profile in profiles[:5]:  # Show first 5 profiles
                    print(f"   📂 {profile['name']}: {profile['size_mb']:.2f} MB")
                
                if len(profiles) > 5:
                    print(f"   ... and {len(profiles) - 5} more profiles")
                    
            except Exception as e:
                print(f"   ❌ Error reading profiles: {e}")
        
        print(f"\n💡 Use 'python -m mcp_colab_server.config_manager --help' for more options")
    
    def clean_chrome_profiles(self) -> None:
        """Clean up old Chrome profiles."""
        try:
            from .chrome_profile_manager import ChromeProfileManager
            profile_manager = ChromeProfileManager(str(self.user_config_dir))
            
            print("🧹 Cleaning up old Chrome profiles...")
            cleaned_count = profile_manager.cleanup_old_profiles(days_old=30)
            
            if cleaned_count > 0:
                print(f"✅ Cleaned up {cleaned_count} old profiles")
            else:
                print("✅ No old profiles to clean up")
                
        except Exception as e:
            print(f"❌ Error cleaning profiles: {e}")
    
    def optimize_chrome_profiles(self) -> None:
        """Optimize all Chrome profiles."""
        try:
            from .chrome_profile_manager import ChromeProfileManager
            profile_manager = ChromeProfileManager(str(self.user_config_dir))
            
            profiles = profile_manager.list_profiles()
            if not profiles:
                print("ℹ️  No Chrome profiles found to optimize")
                return
            
            print(f"🔧 Optimizing {len(profiles)} Chrome profiles...")
            
            total_saved = 0
            for profile in profiles:
                profile_name = profile['name']
                size_before = profile['size_mb']
                
                print(f"   Optimizing {profile_name}... ", end="")
                
                if profile_manager.optimize_profile(profile_name):
                    # Get size after optimization
                    profile_info_after = profile_manager.get_profile_info(profile_name)
                    size_after = profile_info_after['size_mb']
                    saved = max(0, size_before - size_after)
                    total_saved += saved
                    
                    print(f"✅ Saved {saved:.2f} MB")
                else:
                    print("❌ Failed")
            
            print(f"\n✅ Optimization complete! Total saved: {total_saved:.2f} MB")
            
        except Exception as e:
            print(f"❌ Error optimizing profiles: {e}")
    
    def show_chrome_profiles_summary(self) -> None:
        """Show Chrome profiles summary."""
        try:
            from .chrome_profile_manager import ChromeProfileManager
            profile_manager = ChromeProfileManager(str(self.user_config_dir))
            
            profiles = profile_manager.list_profiles()
            total_size = profile_manager.get_total_profiles_size()
            
            print("🌐 Chrome Profiles Summary")
            print("=" * 50)
            print(f"📊 Total profiles: {len(profiles)}")
            print(f"📊 Total size: {total_size:.2f} MB")
            print(f"📁 Profiles directory: {profile_manager.profiles_dir}")
            
            if profiles:
                print("\n📂 Profile Details:")
                for profile in profiles:
                    metadata = profile.get('metadata', {})
                    usage_count = metadata.get('usage_count', 0)
                    last_used = metadata.get('last_used', 'Never')
                    is_backup = metadata.get('is_backup', False)
                    
                    status = "🔄 Backup" if is_backup else "📂 Active"
                    print(f"   {status} {profile['name']}: {profile['size_mb']:.2f} MB")
                    print(f"      Used {usage_count} times, Last: {last_used[:10] if last_used != 'Never' else 'Never'}")
            else:
                print("\nℹ️  No Chrome profiles found")
                print("Profiles will be created automatically when using Selenium")
            
        except Exception as e:
            print(f"❌ Error getting profiles summary: {e}")


def main():
    """Main CLI function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Colab Server Configuration Manager")
    parser.add_argument("--init", action="store_true", help="Initialize user configuration")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing files")
    parser.add_argument("--copy-credentials", metavar="PATH", help="Copy credentials from project path")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--reset", action="store_true", help="Reset configuration (removes all files)")
    parser.add_argument("--status", action="store_true", help="Show configuration status")
    parser.add_argument("--clean-profiles", action="store_true", help="Clean up old Chrome profiles")
    parser.add_argument("--optimize-profiles", action="store_true", help="Optimize all Chrome profiles")
    parser.add_argument("--profile-summary", action="store_true", help="Show Chrome profiles summary")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    config_manager = ConfigManager()
    
    if args.init:
        config_manager.init_user_config(force=args.force)
    elif args.copy_credentials:
        config_manager.copy_credentials(args.copy_credentials)
    elif args.validate:
        config_manager.validate_config()
    elif args.reset:
        config_manager.reset_config()
    elif args.clean_profiles:
        config_manager.clean_chrome_profiles()
    elif args.optimize_profiles:
        config_manager.optimize_chrome_profiles()
    elif args.profile_summary:
        config_manager.show_chrome_profiles_summary()
    elif args.status:
        config_manager.show_status()
    else:
        config_manager.show_status()


if __name__ == "__main__":
    main()