#!/usr/bin/env python3
"""
🔧 Chrome Profile Manager for MCP Colab Server

This module manages Chrome profiles for Selenium automation, storing them
in the user's .mcp-colab directory for consistency and persistence.

Features:
- User-specific profile management
- Profile creation and cleanup
- Profile size monitoring
- Session persistence
- Anti-detection optimizations

Author: inkbytefo
License: MIT
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


class ChromeProfileManager:
    """Manages Chrome profiles for Selenium automation."""
    
    def __init__(self, user_config_dir: Optional[str] = None):
        """Initialize the Chrome profile manager."""
        if user_config_dir:
            self.user_config_dir = Path(user_config_dir)
        else:
            self.user_config_dir = Path.home() / ".mcp-colab"
        
        self.profiles_dir = self.user_config_dir / "chrome_profiles"
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Profile metadata file
        self.metadata_file = self.profiles_dir / "profiles_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load profile metadata from file."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.warning(f"Failed to load profile metadata: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save profile metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save profile metadata: {e}")
    
    def get_default_profile_path(self) -> str:
        """Get the default Chrome profile path."""
        profile_path = self.profiles_dir / "default"
        profile_path.mkdir(exist_ok=True)
        return str(profile_path)
    
    def get_profile_path(self, profile_name: str = "default") -> str:
        """Get path for a specific profile."""
        profile_path = self.profiles_dir / profile_name
        profile_path.mkdir(exist_ok=True)
        
        # Update metadata
        if profile_name not in self.metadata:
            self.metadata[profile_name] = {
                "created_at": self._get_current_timestamp(),
                "last_used": self._get_current_timestamp(),
                "usage_count": 0
            }
        
        self.metadata[profile_name]["last_used"] = self._get_current_timestamp()
        self.metadata[profile_name]["usage_count"] += 1
        self._save_metadata()
        
        return str(profile_path)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all available profiles with their information."""
        profiles = []
        
        for profile_dir in self.profiles_dir.iterdir():
            if profile_dir.is_dir() and profile_dir.name != "__pycache__":
                profile_name = profile_dir.name
                profile_info = {
                    "name": profile_name,
                    "path": str(profile_dir),
                    "size_mb": self._get_directory_size(profile_dir),
                    "exists": profile_dir.exists(),
                    "metadata": self.metadata.get(profile_name, {})
                }
                profiles.append(profile_info)
        
        return profiles
    
    def _get_directory_size(self, directory: Path) -> float:
        """Get directory size in MB."""
        try:
            total_size = 0
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0
    
    def clear_profile(self, profile_name: str = "default") -> bool:
        """Clear a specific profile."""
        try:
            profile_path = self.profiles_dir / profile_name
            if profile_path.exists():
                shutil.rmtree(profile_path, ignore_errors=True)
                
                # Remove from metadata
                if profile_name in self.metadata:
                    del self.metadata[profile_name]
                    self._save_metadata()
                
                self.logger.info(f"Cleared Chrome profile: {profile_name}")
                return True
            else:
                self.logger.info(f"Profile {profile_name} does not exist")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing profile {profile_name}: {e}")
            return False
    
    def clear_all_profiles(self) -> bool:
        """Clear all profiles."""
        try:
            if self.profiles_dir.exists():
                shutil.rmtree(self.profiles_dir, ignore_errors=True)
                self.profiles_dir.mkdir(parents=True, exist_ok=True)
                
                # Clear metadata
                self.metadata = {}
                self._save_metadata()
                
                self.logger.info("Cleared all Chrome profiles")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing all profiles: {e}")
            return False
    
    def get_profile_info(self, profile_name: str = "default") -> Dict[str, Any]:
        """Get detailed information about a profile."""
        profile_path = self.profiles_dir / profile_name
        
        return {
            "name": profile_name,
            "path": str(profile_path),
            "exists": profile_path.exists(),
            "size_mb": self._get_directory_size(profile_path) if profile_path.exists() else 0,
            "metadata": self.metadata.get(profile_name, {}),
            "files_count": len(list(profile_path.rglob('*'))) if profile_path.exists() else 0
        }
    
    def optimize_profile(self, profile_name: str = "default") -> bool:
        """Optimize a profile by cleaning temporary files."""
        try:
            profile_path = self.profiles_dir / profile_name
            if not profile_path.exists():
                return True
            
            # Files and directories to clean
            cleanup_patterns = [
                "*/Cache/*",
                "*/Code Cache/*",
                "*/GPUCache/*",
                "*/Service Worker/CacheStorage/*",
                "*/Service Worker/ScriptCache/*",
                "*/blob_storage/*",
                "*/File System/*",
                "*/IndexedDB/*",
                "*/Local Storage/*",
                "*/Session Storage/*",
                "*/WebStorage/*",
                "*/logs/*",
                "*/crash_dumps/*",
                "*/.tmp*",
                "*/Temp/*"
            ]
            
            cleaned_size = 0
            for pattern in cleanup_patterns:
                try:
                    for path in profile_path.glob(pattern):
                        if path.is_file():
                            size = path.stat().st_size
                            path.unlink(missing_ok=True)
                            cleaned_size += size
                        elif path.is_dir():
                            size = self._get_directory_size(path) * 1024 * 1024
                            shutil.rmtree(path, ignore_errors=True)
                            cleaned_size += size
                except Exception as e:
                    self.logger.debug(f"Error cleaning {pattern}: {e}")
                    continue
            
            cleaned_mb = cleaned_size / (1024 * 1024)
            self.logger.info(f"Optimized profile {profile_name}, cleaned {cleaned_mb:.2f} MB")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing profile {profile_name}: {e}")
            return False
    
    def create_chrome_options(self, profile_name: str = "default", 
                            additional_options: Optional[List[str]] = None) -> 'ChromeOptions':
        """Create Chrome options with the specified profile."""
        try:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            
            options = ChromeOptions()
            
            # Set user data directory
            profile_path = self.get_profile_path(profile_name)
            options.add_argument(f"--user-data-dir={profile_path}")
            
            # Basic Chrome options for stability and anti-detection
            basic_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # Faster loading
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            
            for option in basic_options:
                options.add_argument(option)
            
            # Add additional options if provided
            if additional_options:
                for option in additional_options:
                    options.add_argument(option)
            
            # Experimental options for anti-detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.media_stream_mic": 2,
                "profile.default_content_setting_values.media_stream_camera": 2,
                "profile.default_content_setting_values.geolocation": 2
            })
            
            self.logger.info(f"Created Chrome options with profile: {profile_name}")
            return options
            
        except ImportError:
            self.logger.error("Selenium ChromeOptions not available")
            raise
        except Exception as e:
            self.logger.error(f"Error creating Chrome options: {e}")
            raise
    
    def backup_profile(self, profile_name: str = "default", 
                      backup_name: Optional[str] = None) -> bool:
        """Create a backup of a profile."""
        try:
            if backup_name is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{profile_name}_backup_{timestamp}"
            
            source_path = self.profiles_dir / profile_name
            backup_path = self.profiles_dir / backup_name
            
            if not source_path.exists():
                self.logger.warning(f"Profile {profile_name} does not exist")
                return False
            
            shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
            
            # Update metadata
            self.metadata[backup_name] = {
                "created_at": self._get_current_timestamp(),
                "last_used": self._get_current_timestamp(),
                "usage_count": 0,
                "is_backup": True,
                "backup_of": profile_name
            }
            self._save_metadata()
            
            self.logger.info(f"Created backup of profile {profile_name} as {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up profile {profile_name}: {e}")
            return False
    
    def restore_profile(self, backup_name: str, target_name: str = "default") -> bool:
        """Restore a profile from backup."""
        try:
            backup_path = self.profiles_dir / backup_name
            target_path = self.profiles_dir / target_name
            
            if not backup_path.exists():
                self.logger.error(f"Backup {backup_name} does not exist")
                return False
            
            # Remove existing target if it exists
            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)
            
            shutil.copytree(backup_path, target_path, dirs_exist_ok=True)
            
            # Update metadata
            if target_name in self.metadata:
                del self.metadata[target_name]
            
            self.metadata[target_name] = {
                "created_at": self._get_current_timestamp(),
                "last_used": self._get_current_timestamp(),
                "usage_count": 0,
                "restored_from": backup_name
            }
            self._save_metadata()
            
            self.logger.info(f"Restored profile {target_name} from backup {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring profile from {backup_name}: {e}")
            return False
    
    def get_total_profiles_size(self) -> float:
        """Get total size of all profiles in MB."""
        return self._get_directory_size(self.profiles_dir)
    
    def cleanup_old_profiles(self, days_old: int = 30) -> int:
        """Clean up profiles that haven't been used for specified days."""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for profile_name, metadata in list(self.metadata.items()):
                try:
                    last_used_str = metadata.get("last_used")
                    if last_used_str:
                        last_used = datetime.fromisoformat(last_used_str)
                        if last_used < cutoff_date and not metadata.get("is_backup", False):
                            if self.clear_profile(profile_name):
                                cleaned_count += 1
                                self.logger.info(f"Cleaned up old profile: {profile_name}")
                except Exception as e:
                    self.logger.debug(f"Error checking profile {profile_name}: {e}")
                    continue
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old profiles: {e}")
            return 0