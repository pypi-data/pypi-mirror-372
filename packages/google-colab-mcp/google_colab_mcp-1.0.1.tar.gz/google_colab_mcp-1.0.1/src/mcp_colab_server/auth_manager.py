"""Google OAuth2 authentication manager for the Colab MCP server."""

import json
import logging
import os
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .utils import load_config


class AuthManager:
    """Manages Google OAuth2 authentication for Drive API access."""
    
    # Configuration Constants
    DEFAULT_OAUTH_PORT = 8080
    DEFAULT_REDIRECT_URI = 'http://localhost:8080'
    DEFAULT_SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file"
    ]
    
    def __init__(self, credentials_file: str = None, token_file: str = None, config_path: str = None):
        """Initialize the authentication manager."""
        if config_path:
            self.config = load_config(config_path)
            self.google_config = self.config.get("google_api", {})
        else:
            self.google_config = {}
        
        self.scopes = self.google_config.get("scopes", self.DEFAULT_SCOPES)
        
        # Get user config directory
        user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        os.makedirs(user_config_dir, exist_ok=True)
        
        # Use provided paths or fall back to user config directory
        if credentials_file:
            self.credentials_file = os.path.expanduser(credentials_file)
        else:
            credentials_file = self.google_config.get("credentials_file", os.path.join(user_config_dir, "credentials.json"))
            if not os.path.isabs(credentials_file):
                credentials_file = os.path.join(user_config_dir, credentials_file)
            self.credentials_file = credentials_file
        
        if token_file:
            self.token_file = os.path.expanduser(token_file)
        else:
            token_file = self.google_config.get("token_file", os.path.join(user_config_dir, "token.json"))
            if not os.path.isabs(token_file):
                token_file = os.path.join(user_config_dir, token_file)
            self.token_file = token_file
        self.credentials: Optional[Credentials] = None
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self, auto_open_browser: bool = True) -> bool:
        """Authenticate with Google APIs and return success status."""
        try:
            self.logger.info("Starting Google authentication process...")
            
            # Load existing credentials if available
            if os.path.exists(self.token_file):
                self.logger.info("Loading existing credentials...")
                try:
                    self.credentials = Credentials.from_authorized_user_file(
                        self.token_file, self.scopes
                    )
                    if self.credentials and self.credentials.valid:
                        self.logger.info("Existing credentials are valid!")
                        return True
                except Exception as e:
                    self.logger.warning(f"Failed to load existing credentials: {e}")
            
            # If credentials are not valid, refresh or re-authenticate
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.logger.info("🔄 Refreshing expired credentials...")
                    try:
                        self.credentials.refresh(Request())
                        self._save_credentials()
                        self.logger.info("✅ Credentials refreshed successfully!")
                        return True
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to refresh credentials: {e}")
                        # Continue to re-authentication
                
                # Start new OAuth flow
                return self._start_oauth_flow(auto_open_browser)
            
            self.logger.info("✅ Authentication successful!")
            return True
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Authentication failed: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _start_oauth_flow(self, auto_open_browser: bool = True) -> bool:
        """Start OAuth2 flow for new authentication."""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                self.logger.error(f"❌ Credentials file not found: {self.credentials_file}")
                self._create_credentials_template()
                return False
            
            self.logger.info("🌐 Starting OAuth2 authentication flow...")
            self.logger.info("📱 Your browser will open for Google authentication")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes
            )
            
            # Configure flow for better user experience
            oauth_port = self.google_config.get("oauth_port", self.DEFAULT_OAUTH_PORT)
            redirect_uri = self.google_config.get("redirect_uri", self.DEFAULT_REDIRECT_URI)
            flow.redirect_uri = redirect_uri
            
            if auto_open_browser:
                self.logger.info("🔗 Opening browser for authentication...")
                self.credentials = flow.run_local_server(
                    port=oauth_port,
                    prompt='select_account',
                    open_browser=True
                )
            else:
                # Manual flow for headless environments
                auth_url, _ = flow.authorization_url(prompt='select_account')
                self.logger.info(f"🔗 Please visit this URL to authorize: {auth_url}")
                auth_code = input("Enter the authorization code: ")
                flow.fetch_token(code=auth_code)
                self.credentials = flow.credentials
            
            # Save credentials for future use
            self._save_credentials()
            
            # Get user info for confirmation
            user_info = self.get_user_info()
            if user_info:
                email = user_info.get('emailAddress', 'Unknown')
                name = user_info.get('displayName', 'Unknown')
                self.logger.info(f"✅ Successfully authenticated as: {name} ({email})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ OAuth flow failed: {e}")
            return False
    
    def _create_credentials_template(self):
        """Create a template credentials file with instructions."""
        template_path = os.path.join(os.path.dirname(self.credentials_file), "credentials.json.template")
        
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
        
        try:
            with open(template_path, 'w') as f:
                json.dump(template_content, f, indent=2)
            
            self.logger.error("📝 Created credentials template file")
            self.logger.error("🔧 Setup Instructions:")
            self.logger.error("1. Go to https://console.cloud.google.com/")
            self.logger.error("2. Create a new project or select existing one")
            self.logger.error("3. Enable Google Drive API")
            self.logger.error("4. Create OAuth 2.0 credentials (Desktop Application)")
            self.logger.error("5. Download credentials.json and place it in config/ folder")
            self.logger.error(f"6. Replace the template file: {template_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid credentials."""
        if not self.credentials:
            return False
        
        # Check if credentials are valid
        if not self.credentials.valid:
            # Try to refresh if possible
            if self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    return True
                except Exception as e:
                    self.logger.warning(f"Failed to refresh credentials: {e}")
                    return False
            return False
        
        return True

    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            
            with open(self.token_file, 'w') as token:
                token.write(self.credentials.to_json())
            
            self.logger.info(f"Credentials saved to {self.token_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def get_drive_service(self):
        """Get authenticated Google Drive service."""
        if not self.credentials or not self.credentials.valid:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Google APIs")
        
        try:
            service = build('drive', 'v3', credentials=self.credentials)
            return service
        except Exception as e:
            self.logger.error(f"Failed to build Drive service: {e}")
            raise
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self.credentials is not None and self.credentials.valid
    
    def get_user_info(self):
        """Get authenticated user information from Google Drive API."""
        if not self.credentials or not self.credentials.valid:
            return None
        
        try:
            # Use the Drive service to get user info
            service = build('drive', 'v3', credentials=self.credentials)
            about = service.about().get(fields='user').execute()
            return about.get('user', {})
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            return None

    def revoke_credentials(self) -> bool:
        """Revoke current credentials."""
        try:
            if self.credentials:
                self.credentials.revoke(Request())
            
            # Remove token file
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            
            self.credentials = None
            self.logger.info("Credentials revoked successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke credentials: {e}")
            return False
    
    def get_user_info(self) -> Optional[dict]:
        """Get information about the authenticated user."""
        if not self.is_authenticated():
            return None
        
        try:
            service = self.get_drive_service()
            about = service.about().get(fields="user").execute()
            return about.get('user', {})
            
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            return None