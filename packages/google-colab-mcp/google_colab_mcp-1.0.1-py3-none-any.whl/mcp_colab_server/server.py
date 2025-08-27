"""Main MCP server implementation for Google Colab integration."""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ServerCapabilities,
    ToolsCapability
)

from .auth_manager import AuthManager
from .colab_drive import ColabDriveManager
from .colab_selenium import ColabSeleniumManager
from .session_manager import SessionManager, RuntimeType
from .utils import load_config, setup_logging, extract_error_message, safe_message_format


class ColabMCPServer:
    """MCP Server for Google Colab integration."""
    
    # Constants
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    DEFAULT_PROFILE_NAME = "default"
    DANGEROUS_CODE_PATTERNS = ['rm -rf', 'del ', 'os.system', 'subprocess', 'eval(', 'exec(']
    SYSTEM_PACKAGES = ['sudo', 'apt-get', 'yum', 'pip install --upgrade pip']
    
    def __init__(self, config_path: str = None):
        """Initialize the MCP server."""
        if config_path is None:
            # Try multiple locations for config file
            config_path = self._find_config_file()
        
        self.config = load_config(config_path)
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        credentials_path = self._get_credentials_path()
        # Ensure token path uses the same directory as credentials
        user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        token_path = self.config.get("google_api", {}).get("token_file", 
                                   os.path.join(user_config_dir, "token.json"))
        # Make sure token path is absolute and in user config directory
        if not os.path.isabs(token_path):
            token_path = os.path.join(user_config_dir, token_path)
        self.auth_manager = AuthManager(credentials_file=credentials_path, token_file=token_path)
        self.session_manager = SessionManager(self.config)
        self.drive_manager = None
        self.selenium_manager = None
        
        # MCP Server
        self.server = Server("google-colab-mcp")
        self._setup_handlers()
        
        self.logger.info("Colab MCP Server initialized")
    
    def _find_config_file(self) -> str:
        """Find the configuration file in various possible locations."""
        # Prioritize user config directory
        user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        user_config_path = os.path.join(user_config_dir, "server_config.json")
        
        # Check if user config exists first
        if os.path.exists(user_config_path):
            return user_config_path
        
        # Fallback to other locations for development/testing
        possible_paths = [
            # 1. Current working directory
            os.path.join(os.getcwd(), "config", "server_config.json"),
            # 2. Relative to the script location (development)
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "server_config.json"),
            # 3. Package data location
            os.path.join(os.path.dirname(__file__), "config", "server_config.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no config file found, create a default one in user's home directory
        user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        os.makedirs(user_config_dir, exist_ok=True)
        default_config_path = os.path.join(user_config_dir, "server_config.json")
        
        # Copy the default config from the package
        package_config = os.path.join(os.path.dirname(__file__), "..", "..", "config", "server_config.json")
        if os.path.exists(package_config):
            import shutil
            shutil.copy2(package_config, default_config_path)
        else:
            # Create a minimal default config
            default_config = {
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
            with open(default_config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        return default_config_path
    
    def _get_credentials_path(self) -> str:
        """Get the path to the credentials file."""
        # Prioritize user config directory
        user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        user_credentials_path = os.path.join(user_config_dir, "credentials.json")
        
        # Check if credentials_file is specified in config
        credentials_file = self.config.get("google_api", {}).get("credentials_file")
        if credentials_file and os.path.exists(credentials_file):
            return credentials_file
        
        # Check user config directory first
        if os.path.exists(user_credentials_path):
            return user_credentials_path
        
        # Fallback to other locations for development/testing
        possible_paths = [
            os.path.join(os.getcwd(), "config", "credentials.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "credentials.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return the user config directory path (even if file doesn't exist yet)
        return user_credentials_path
    
    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="create_colab_notebook",
                    description="Create a new Google Colab notebook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the notebook"
                            },
                            "content": {
                                "type": "string",
                                "description": "Optional initial content (JSON format)"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="run_code_cell",
                    description="⚠️ Execute Python code in a Colab notebook (CAUTION: Arbitrary code execution)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute (will run in Colab environment)"
                            },
                            "notebook_id": {
                                "type": "string",
                                "description": "ID of the notebook"
                            },
                            "confirm_execution": {
                                "type": "boolean",
                                "description": "Confirm that you understand this will execute arbitrary code",
                                "default": False
                            }
                        },
                        "required": ["code", "notebook_id"]
                    }
                ),
                Tool(
                    name="install_package",
                    description="⚠️ Install a Python package in Colab (CAUTION: System modification)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Name of the package to install (e.g., 'pandas', 'numpy')"
                            },
                            "notebook_id": {
                                "type": "string",
                                "description": "ID of the notebook"
                            },
                            "confirm_install": {
                                "type": "boolean",
                                "description": "Confirm that you understand this will install packages in the runtime",
                                "default": False
                            }
                        },
                        "required": ["package_name", "notebook_id"]
                    }
                ),
                Tool(
                    name="get_notebook_content",
                    description="Retrieve the content of a Colab notebook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "notebook_id": {
                                "type": "string",
                                "description": "ID of the notebook"
                            }
                        },
                        "required": ["notebook_id"]
                    }
                ),
                Tool(
                    name="list_notebooks",
                    description="List user's Colab notebooks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of notebooks to return",
                                "default": 50
                            }
                        }
                    }
                ),
                Tool(
                    name="upload_file_to_colab",
                    description="Upload a file to Colab environment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to upload"
                            },
                            "notebook_id": {
                                "type": "string",
                                "description": "ID of the notebook"
                            }
                        },
                        "required": ["file_path", "notebook_id"]
                    }
                ),
                Tool(
                    name="get_runtime_info",
                    description="Get runtime information for a Colab notebook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "notebook_id": {
                                "type": "string",
                                "description": "ID of the notebook"
                            }
                        },
                        "required": ["notebook_id"]
                    }
                ),
                Tool(
                    name="get_session_info",
                    description="Get session information for a notebook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "notebook_id": {
                                "type": "string",
                                "description": "ID of the notebook"
                            }
                        },
                        "required": ["notebook_id"]
                    }
                ),
                Tool(
                    name="check_auth_status",
                    description="Check Google authentication status and setup requirements",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="setup_google_credentials",
                    description="Get step-by-step instructions for setting up Google credentials",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="authenticate_google",
                    description="Start Google OAuth authentication flow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "auto_open_browser": {
                                "type": "boolean",
                                "description": "Whether to automatically open browser for authentication",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="get_chrome_profile_info",
                    description="Get information about the Chrome profile used for Colab sessions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_name": {
                                "type": "string",
                                "description": "Name of the profile to get info for (default: current profile)",
                                "default": None
                            }
                        }
                    }
                ),
                Tool(
                    name="list_chrome_profiles",
                    description="List all available Chrome profiles with their information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="clear_chrome_profile",
                    description="Clear the persistent Chrome profile data (will require re-authentication)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_name": {
                                "type": "string",
                                "description": "Name of the profile to clear (default: current profile)",
                                "default": None
                            }
                        }
                    }
                ),
                Tool(
                    name="optimize_chrome_profile",
                    description="Optimize Chrome profile by cleaning temporary files and cache",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_name": {
                                "type": "string",
                                "description": "Name of the profile to optimize (default: current profile)",
                                "default": None
                            }
                        }
                    }
                ),
                Tool(
                    name="backup_chrome_profile",
                    description="Create a backup of Chrome profile",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_name": {
                                "type": "string",
                                "description": "Name of the profile to backup (default: current profile)",
                                "default": None
                            },
                            "backup_name": {
                                "type": "string",
                                "description": "Name for the backup (default: auto-generated)",
                                "default": None
                            }
                        }
                    }
                ),
                Tool(
                    name="restore_chrome_profile",
                    description="Restore Chrome profile from backup",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "backup_name": {
                                "type": "string",
                                "description": "Name of the backup to restore from"
                            },
                            "target_name": {
                                "type": "string",
                                "description": "Name for the restored profile (default: current profile)",
                                "default": None
                            }
                        },
                        "required": ["backup_name"]
                    }
                ),
                Tool(
                    name="get_profiles_summary",
                    description="Get summary of all Chrome profiles and their usage",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="init_user_config",
                    description="Initialize user configuration directory and files (creates ~/.mcp-colab/)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "force": {
                                "type": "boolean",
                                "description": "Force overwrite existing configuration files",
                                "default": False
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                # Auth tools don't require authentication
                auth_tools = ["init_user_config", "check_auth_status", "setup_google_credentials", "authenticate_google", 
                             "get_chrome_profile_info", "list_chrome_profiles", "clear_chrome_profile",
                             "optimize_chrome_profile", "backup_chrome_profile", "restore_chrome_profile",
                             "get_profiles_summary"]
                
                if name not in auth_tools:
                    # Ensure authentication for non-auth tools
                    await self._ensure_authenticated()
                
                if name == "create_colab_notebook":
                    result = await self._create_notebook(arguments)
                elif name == "run_code_cell":
                    result = await self._run_code_cell(arguments)
                elif name == "install_package":
                    result = await self._install_package(arguments)
                elif name == "get_notebook_content":
                    result = await self._get_notebook_content(arguments)
                elif name == "list_notebooks":
                    result = await self._list_notebooks(arguments)
                elif name == "upload_file_to_colab":
                    result = await self._upload_file(arguments)
                elif name == "get_runtime_info":
                    result = await self._get_runtime_info(arguments)
                elif name == "get_session_info":
                    result = await self._get_session_info(arguments)
                elif name == "check_auth_status":
                    result = await self._check_auth_status(arguments)
                elif name == "setup_google_credentials":
                    result = await self._setup_google_credentials(arguments)
                elif name == "authenticate_google":
                    result = await self._authenticate_google(arguments)
                elif name == "get_chrome_profile_info":
                    result = await self._get_chrome_profile_info(arguments)
                elif name == "list_chrome_profiles":
                    result = await self._list_chrome_profiles(arguments)
                elif name == "clear_chrome_profile":
                    result = await self._clear_chrome_profile(arguments)
                elif name == "optimize_chrome_profile":
                    result = await self._optimize_chrome_profile(arguments)
                elif name == "backup_chrome_profile":
                    result = await self._backup_chrome_profile(arguments)
                elif name == "restore_chrome_profile":
                    result = await self._restore_chrome_profile(arguments)
                elif name == "get_profiles_summary":
                    result = await self._get_profiles_summary(arguments)
                elif name == "init_user_config":
                    result = await self._init_user_config(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                # Always return TextContent format with safe formatting
                safe_result = self._safe_format_response(result)
                return [TextContent(type="text", text=json.dumps(safe_result, indent=2))]
                
            except Exception as e:
                error_msg = extract_error_message(e)
                self.logger.error(f"Tool {name} failed: {error_msg}")
                
                # Provide helpful error messages for common issues
                if "credentials not found" in error_msg.lower():
                    error_response = {
                        "success": False,
                        "error": "Google credentials not configured",
                        "message": "🔐 Google authentication setup required",
                        "next_steps": [
                            "1. Use 'setup_google_credentials' tool for detailed setup instructions",
                            "2. Use 'check_auth_status' tool to check current status",
                            "3. Use 'authenticate_google' tool after setting up credentials"
                        ],
                        "help": "These tools will guide you through the authentication setup process"
                    }
                    safe_response = self._safe_format_response(error_response)
                    return [TextContent(type="text", text=json.dumps(safe_response, indent=2))]
                elif "authentication failed" in error_msg.lower():
                    error_response = {
                        "success": False,
                        "error": "Google authentication failed",
                        "message": "🔐 Unable to authenticate with Google services",
                        "troubleshooting": [
                            "1. Use 'check_auth_status' to see what's wrong",
                            "2. Use 'authenticate_google' to retry authentication",
                            "3. Ensure you have internet connection",
                            "4. Check if credentials.json is valid"
                        ],
                        "help": "Use the authentication tools to resolve this issue"
                    }
                    safe_response = self._safe_format_response(error_response)
                    return [TextContent(type="text", text=json.dumps(safe_response, indent=2))]
                else:
                    error_response = {
                        "success": False,
                        "error": error_msg,
                        "message": f"❌ Tool '{name}' failed",
                        "help": "Use 'check_auth_status' to verify your Google authentication setup"
                    }
                    safe_response = self._safe_format_response(error_response)
                    return [TextContent(type="text", text=json.dumps(safe_response, indent=2))]
    
    async def _ensure_authenticated(self) -> None:
        """Ensure Google APIs are authenticated."""
        if not self.auth_manager.is_authenticated():
            # Check if credentials file exists
            if not os.path.exists(self.auth_manager.credentials_file):
                raise Exception(
                    "🔐 Google credentials not found!\n\n"
                    "📋 To set up authentication:\n"
                    "1. Use the 'setup_google_credentials' tool to get detailed setup instructions\n"
                    "2. Download credentials.json from Google Cloud Console\n"
                    "3. Use the 'authenticate_google' tool to complete authentication\n\n"
                    "💡 Or use 'check_auth_status' to see current authentication status"
                )
            
            self.logger.info("Authentication required - starting automatic login...")
            success = self.auth_manager.authenticate(auto_open_browser=False)
            if not success:
                raise Exception(
                    "Google authentication failed!\n\n"
                    "Troubleshooting steps:\n"
                    "1. Use 'check_auth_status' tool to check your setup\n"
                    "2. Use 'authenticate_google' tool to retry authentication\n"
                    "3. If issues persist, use 'setup_google_credentials' for help\n\n"
                    "Make sure your credentials.json file is valid and you have internet access"
                )
        
        # Initialize managers if not already done
        if self.drive_manager is None:
            self.logger.info("Initializing Google Drive manager...")
            self.drive_manager = ColabDriveManager(self.auth_manager)
        
        if self.selenium_manager is None:
            self.logger.info("Initializing Selenium automation manager...")
            self.selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
    
    def _ensure_selenium_manager(self) -> None:
        """Ensure Selenium manager is initialized."""
        if self.selenium_manager is None:
            self.logger.info("Initializing Selenium automation manager...")
            self.selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
    
    def _safe_format_response(self, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Safely format response dictionary to handle encoding issues."""
        def safe_format_recursive(obj):
            if isinstance(obj, dict):
                return {k: safe_format_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [safe_format_recursive(item) for item in obj]
            elif isinstance(obj, str):
                return safe_message_format(obj)
            else:
                return obj
        
        return safe_format_recursive(response_dict)

    def _create_error_response(self, error: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create standardized error response."""
        response = {
            "success": False,
            "error": error,
            "message": message
        }
        response.update(kwargs)
        return response
    
    def _create_success_response(self, message: str, **kwargs) -> Dict[str, Any]:
        """Create standardized success response."""
        response = {
            "success": True,
            "message": message
        }
        response.update(kwargs)
        return response
    
    async def _create_notebook(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Colab notebook."""
        name = arguments["name"]
        content_str = arguments.get("content")
        
        content = None
        if content_str:
            try:
                content = json.loads(content_str)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON content provided")
        
        result = self.drive_manager.create_notebook(name, content)
        
        # Create session for the new notebook
        self.session_manager.create_session(result["id"])
        
        return {
            "success": True,
            "notebook": result
        }
    
    async def _run_code_cell(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code in a Colab notebook with enhanced error handling and timeout management."""
        code = arguments["code"]
        notebook_id = arguments["notebook_id"]
        confirm_execution = arguments.get("confirm_execution", False)
        selenium_manager = None
        
        try:
            # Safety check for dangerous operations
            if any(pattern in code.lower() for pattern in self.DANGEROUS_CODE_PATTERNS):
                if not confirm_execution:
                    return self._create_error_response(
                        "Potentially dangerous code detected",
                        "⚠️ This code contains potentially dangerous operations. Please review and confirm execution.",
                        code_preview=code[:200] + "..." if len(code) > 200 else code,
                        safety_note="Set 'confirm_execution': true if you want to proceed"
                    )
            
            # Initialize Selenium manager if needed - use local instance to ensure cleanup
            if self.selenium_manager is None:
                self.selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
            
            selenium_manager = self.selenium_manager
            
            # Execute code with improved error handling in a separate thread
            # This prevents the async server from blocking on long-running Selenium operations
            result = await asyncio.to_thread(selenium_manager.execute_code, notebook_id, code)
            
            # Ensure we have a properly formatted response
            if not isinstance(result, dict):
                result = {
                    'success': False,
                    'output': '',
                    'error': f'Invalid result format: {str(result)}',
                    'execution_time': 0
                }
            
            # Log execution results for debugging
            if result.get('success'):
                output_length = len(str(result.get('output', '')))
                execution_time = result.get('execution_time', 0)
                self.logger.info(f"Code execution successful: {output_length} chars output in {execution_time:.2f}s")
            else:
                error_msg = result.get('error', 'Unknown error')
                self.logger.warning(f"Code execution failed: {error_msg[:100]}..." if len(str(error_msg)) > 100 else error_msg)
            
            # Format success response with additional metadata
            if result.get('success'):
                formatted_result = {
                    'success': True,
                    'output': result.get('output', ''),
                    'execution_time': result.get('execution_time', 0),
                    'cell_type': result.get('cell_type', 'code'),
                    'notebook_id': notebook_id,
                    'message': '✅ Code executed successfully'
                }
                
                # Add execution metadata if available
                if result.get('is_long_running'):
                    formatted_result['execution_type'] = 'long_running'
                    formatted_result['message'] += ' (long-running operation)'
                
                return formatted_result
            else:
                # Format error response with helpful information
                error_msg = result.get('error', 'Unknown execution error')
                return {
                    'success': False,
                    'error': error_msg,
                    'output': result.get('output', ''),
                    'execution_time': result.get('execution_time', 0),
                    'notebook_id': notebook_id,
                    'message': f'❌ Code execution failed: {error_msg}',
                    'troubleshooting': [
                        'Check if the notebook is accessible and connected',
                        'Verify that the code syntax is correct',
                        'Ensure required packages are installed',
                        'Check Colab runtime status if execution timed out'
                    ]
                }
        
        except Exception as e:
            self.logger.error(f"Unexpected error in _run_code_cell: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Server error during code execution: {str(e)}',
                'output': '',
                'execution_time': 0,
                'notebook_id': notebook_id,
                'message': f'❌ Server error: {str(e)}',
                'troubleshooting': [
                    'Check server logs for detailed error information',
                    'Verify browser and WebDriver are properly configured',
                    'Try refreshing the browser session',
                    'Check internet connection and Google Colab accessibility'
                ]
            }
        
        finally:
            # SMART CLEANUP: Keep browser session alive for better performance
            # Only cleanup on errors or when explicitly requested
            try:
                if selenium_manager and hasattr(selenium_manager, 'driver') and selenium_manager.driver:
                    # Check if driver is still responsive instead of closing it
                    try:
                        _ = selenium_manager.driver.current_url
                        self.logger.info("Browser session kept alive for next operation")
                    except Exception as driver_error:
                        # Only close if driver is unresponsive
                        selenium_manager._close_driver()
                        self.logger.warning(f"Browser session closed due to unresponsive driver: {driver_error}")
            except Exception as cleanup_error:
                self.logger.warning(f"Error during browser health check: {cleanup_error}")
                # Don't let cleanup errors affect the response
    
    async def _install_package(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Install a package in Colab."""
        package_name = arguments["package_name"]
        notebook_id = arguments["notebook_id"]
        confirm_install = arguments.get("confirm_install", False)
        selenium_manager = None
        
        try:
            # Validate package name for basic safety
            import re
            if not re.match(r'^[a-zA-Z0-9\-_\.\s]+$', package_name):
                return self._create_error_response(
                    "Invalid package name",
                    "⚠️ Package name contains invalid characters. Only alphanumeric, hyphens, underscores, dots and spaces allowed."
                )
            
            # Safety warning for system packages
            if any(pkg in package_name.lower() for pkg in self.SYSTEM_PACKAGES):
                if not confirm_install:
                    return self._create_error_response(
                        "System package installation detected",
                        "⚠️ This appears to be a system-level package installation. Please confirm if you want to proceed.",
                        package=package_name,
                        safety_note="Set 'confirm_install': true if you want to proceed"
                    )
            
            # Initialize Selenium manager if needed
            if self.selenium_manager is None:
                self.selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
            
            selenium_manager = self.selenium_manager
            
            # Install package in a separate thread to avoid blocking the async server
            result = await asyncio.to_thread(selenium_manager.install_package, notebook_id, package_name)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Unexpected error in _install_package: {e}", exc_info=True)
            return self._create_error_response(
                str(e),
                f"❌ Package installation failed: {str(e)}"
            )
        
        finally:
            # SMART CLEANUP: Keep browser session alive for package installations
            try:
                if selenium_manager and hasattr(selenium_manager, 'driver') and selenium_manager.driver:
                    try:
                        _ = selenium_manager.driver.current_url
                        self.logger.info("Browser session kept alive after package installation")
                    except Exception as driver_error:
                        selenium_manager._close_driver()
                        self.logger.warning(f"Browser session closed due to unresponsive driver: {driver_error}")
            except Exception as cleanup_error:
                self.logger.warning(f"Error during browser health check: {cleanup_error}")
    
    async def _get_notebook_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get notebook content."""
        notebook_id = arguments["notebook_id"]
        
        content = self.drive_manager.get_notebook_content(notebook_id)
        
        return self._create_success_response(
            "✅ Notebook content retrieved successfully",
            content=content
        )
    
    async def _list_notebooks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List user's notebooks."""
        max_results = arguments.get("max_results", 50)
        
        notebooks = self.drive_manager.list_notebooks(max_results)
        
        return self._create_success_response(
            f"✅ Found {len(notebooks)} notebooks",
            notebooks=notebooks,
            count=len(notebooks)
        )
    
    async def _upload_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a file to Colab environment."""
        file_path = arguments["file_path"]
        notebook_id = arguments["notebook_id"]
        selenium_manager = None
        
        try:
            # Validate file path to prevent directory traversal
            import os.path
            if '..' in file_path or file_path.startswith('/'):
                return self._create_error_response(
                    "Invalid file path",
                    "❌ Invalid file path. Directory traversal not allowed."
                )
            
            # Check if file exists
            if not os.path.exists(file_path):
                return self._create_error_response(
                    "File not found",
                    f"❌ File not found: {file_path}"
                )
            
            # Check file size (limit to 100MB)
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                return self._create_error_response(
                    "File too large",
                    f"❌ File size ({file_size / 1024 / 1024:.1f}MB) exceeds limit ({self.MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"
                )
            
            # Initialize Selenium manager if needed
            if self.selenium_manager is None:
                self.selenium_manager = ColabSeleniumManager(self.config, self.session_manager)
            
            selenium_manager = self.selenium_manager
            
            # Upload file in a separate thread to avoid blocking the async server
            result = await asyncio.to_thread(selenium_manager.upload_file, notebook_id, file_path)
            return result
        
        except Exception as e:
            self.logger.error(f"Unexpected error in _upload_file: {e}", exc_info=True)
            return self._create_error_response(
                str(e),
                f"❌ Failed to upload file: {str(e)}"
            )
        
        finally:
            # SMART CLEANUP: Keep browser session alive for file operations
            try:
                if selenium_manager and hasattr(selenium_manager, 'driver') and selenium_manager.driver:
                    try:
                        _ = selenium_manager.driver.current_url
                        self.logger.info("Browser session kept alive after file upload")
                    except Exception as driver_error:
                        selenium_manager._close_driver()
                        self.logger.warning(f"Browser session closed due to unresponsive driver: {driver_error}")
            except Exception as cleanup_error:
                self.logger.warning(f"Error during browser health check: {cleanup_error}")
    
    async def _get_runtime_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get runtime information for a Colab notebook."""
        notebook_id = arguments["notebook_id"]
        
        try:
            # Get session info from session manager
            session_info = self.session_manager.get_session_info(notebook_id)
            runtime_info = self.session_manager.get_runtime_info(notebook_id)
            
            # Get additional runtime info from Selenium if available
            selenium_info = {}
            if self.selenium_manager:
                try:
                    # Run Selenium operation in a separate thread to avoid blocking
                    selenium_info = await asyncio.to_thread(self.selenium_manager.get_runtime_status, notebook_id)
                except Exception as e:
                    self.logger.warning(f"Could not get Selenium runtime info: {e}")
            
            return {
                "success": True,
                "runtime_info": {
                    **runtime_info,
                    "session_info": session_info,
                    "selenium_info": selenium_info
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Failed to get runtime info: {str(e)}"
            }
    
    async def _get_session_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get session information for a notebook."""
        notebook_id = arguments["notebook_id"]
        
        try:
            session_info = self.session_manager.get_session_info(notebook_id)
            
            if session_info is None:
                return {
                    "success": False,
                    "error": "Session not found",
                    "message": f"❌ No session found for notebook: {notebook_id}"
                }
            
            return {
                "success": True,
                "session_info": session_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Failed to get session info: {str(e)}"
            }
    
    async def _check_auth_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Check Google authentication status and setup requirements."""
        try:
            status = {
                "authenticated": False,
                "credentials_file_exists": False,
                "token_file_exists": False,
                "user_info": None,
                "setup_required": True,
                "next_steps": []
            }
            
            # Check credentials file
            credentials_path = self.auth_manager.credentials_file
            status["credentials_file_exists"] = os.path.exists(credentials_path)
            status["credentials_file_path"] = credentials_path
            
            # Check token file
            token_path = self.auth_manager.token_file
            status["token_file_exists"] = os.path.exists(token_path)
            status["token_file_path"] = token_path
            
            # Check authentication status
            status["authenticated"] = self.auth_manager.is_authenticated()
            
            if status["authenticated"]:
                # Get user info if authenticated
                try:
                    user_info = self.auth_manager.get_user_info()
                    if user_info:
                        status["user_info"] = {
                            "email": user_info.get("emailAddress", "Unknown"),
                            "name": user_info.get("displayName", "Unknown")
                        }
                except Exception as e:
                    self.logger.warning(f"Could not get user info: {e}")
                
                status["setup_required"] = False
                status["next_steps"] = ["✅ Authentication is working! You can start using Colab tools."]
            else:
                # Determine next steps based on what's missing
                if not status["credentials_file_exists"]:
                    status["next_steps"].extend([
                        "1. Use 'setup_google_credentials' tool for detailed setup instructions",
                        "2. Download credentials.json from Google Cloud Console",
                        f"3. Place credentials.json in: {credentials_path}"
                    ])
                else:
                    status["next_steps"].extend([
                        "1. Use 'authenticate_google' tool to start authentication",
                        "2. Complete OAuth flow in browser",
                        "3. Tokens will be saved automatically"
                    ])
            
            return {
                "success": True,
                "status": status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Failed to check auth status: {str(e)}"
            }
    
    async def _setup_google_credentials(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get step-by-step instructions for setting up Google credentials."""
        user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        credentials_path = os.path.join(user_config_dir, "credentials.json")
        
        instructions = {
            "title": "🔧 Google Cloud Setup Instructions",
            "steps": [
                {
                    "step": 1,
                    "title": "Go to Google Cloud Console",
                    "action": "Visit https://console.cloud.google.com/",
                    "details": "Open Google Cloud Console in your browser"
                },
                {
                    "step": 2,
                    "title": "Create or Select Project",
                    "action": "Create a new project or select an existing one",
                    "details": "You need a Google Cloud project to create credentials"
                },
                {
                    "step": 3,
                    "title": "Enable Google Drive API",
                    "action": "Go to APIs & Services > Library > Search for 'Google Drive API' > Enable",
                    "details": "This API is required to access Colab notebooks"
                },
                {
                    "step": 4,
                    "title": "Create OAuth 2.0 Credentials",
                    "action": "Go to APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID",
                    "details": "Choose 'Desktop Application' as the application type"
                },
                {
                    "step": 5,
                    "title": "Download Credentials",
                    "action": "Download the credentials.json file",
                    "details": f"Save it to: {credentials_path}"
                },
                {
                    "step": 6,
                    "title": "Complete Authentication",
                    "action": "Use 'authenticate_google' tool to complete setup",
                    "details": "This will open browser for OAuth flow"
                }
            ],
            "file_locations": {
                "user_config_directory": user_config_dir,
                "credentials_file": credentials_path,
                "token_file": os.path.join(user_config_dir, "token.json")
            },
            "troubleshooting": [
                "If you get 'access_denied' error, make sure you're using the correct Google account",
                "If credentials.json is invalid, re-download from Google Cloud Console",
                "Make sure Google Drive API is enabled in your project"
            ]
        }
        
        return {
            "success": True,
            "instructions": instructions
        }
    
    async def _authenticate_google(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Start Google OAuth authentication flow."""
        auto_open_browser = arguments.get("auto_open_browser", True)
        
        try:
            # Check if credentials file exists
            if not os.path.exists(self.auth_manager.credentials_file):
                return {
                    "success": False,
                    "error": "Credentials file not found",
                    "message": "🔐 credentials.json not found. Use 'setup_google_credentials' tool first.",
                    "next_steps": [
                        "1. Use 'setup_google_credentials' tool for setup instructions",
                        "2. Download credentials.json from Google Cloud Console",
                        f"3. Place it in: {self.auth_manager.credentials_file}"
                    ]
                }
            
            # Start authentication
            success = self.auth_manager.authenticate(auto_open_browser=auto_open_browser)
            
            if success:
                # Get user info
                user_info = self.auth_manager.get_user_info()
                user_display = "Unknown User"
                if user_info:
                    name = user_info.get("displayName", "")
                    email = user_info.get("emailAddress", "")
                    user_display = f"{name} ({email})" if name and email else email or name
                
                return {
                    "success": True,
                    "message": f"✅ Authentication successful! Logged in as: {user_display}",
                    "user_info": user_info,
                    "token_saved": os.path.exists(self.auth_manager.token_file)
                }
            else:
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "message": "❌ OAuth authentication failed. Please try again.",
                    "troubleshooting": [
                        "Make sure you complete the OAuth flow in browser",
                        "Check that credentials.json is valid",
                        "Ensure you have internet connection",
                        "Try using 'check_auth_status' to diagnose issues"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Authentication error: {str(e)}"
            }
    
    async def _init_user_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize user configuration directory and files."""
        force = arguments.get("force", False)
        
        try:
            from .config_manager import ConfigManager
            
            config_manager = ConfigManager()
            success = config_manager.init_user_config(force=force)
            
            if success:
                user_config_dir = config_manager.get_user_config_dir()
                return self._create_success_response(
                    "✅ User configuration initialized successfully!",
                    config_directory=str(user_config_dir),
                    files_created=[
                        "server_config.json - Server configuration",
                        "credentials.json.template - Google credentials template",
                        "logs/ - Log files directory"
                    ],
                    next_steps=[
                        "1. Download credentials.json from Google Cloud Console",
                        f"2. Place credentials.json in: {user_config_dir}",
                        "3. Use 'authenticate_google' tool to complete setup",
                        "4. Start using Colab tools!"
                    ]
                )
            else:
                return self._create_error_response(
                    "Initialization failed",
                    "❌ Failed to initialize user configuration"
                )
                
        except Exception as e:
            return self._create_error_response(
                str(e),
                f"❌ Failed to initialize user config: {str(e)}"
            )

    
    async def _get_chrome_profile_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get Chrome profile information."""
        try:
            self._ensure_selenium_manager()
            
            profile_name = arguments.get("profile_name")
            if profile_name:
                profile_info = self.selenium_manager.profile_manager.get_profile_info(profile_name)
            else:
                profile_info = self.selenium_manager.get_profile_info()
            
            return self._create_success_response(
                "✅ Chrome profile information retrieved successfully",
                profile_info=profile_info,
                details={
                    "name": profile_info.get("name", "unknown"),
                    "persistent_profile_enabled": profile_info.get("persistent_profile_enabled", True),
                    "profile_directory": profile_info.get("path") or profile_info.get("profile_directory"),
                    "profile_exists": profile_info.get("profile_exists", False),
                    "profile_size_mb": profile_info.get("profile_size_mb", 0),
                    "files_count": profile_info.get("files_count", 0),
                    "metadata": profile_info.get("metadata", {})
                },
                recommendations=[
                    "If profile exists, your Google login should be remembered",
                    "If profile is large (>100MB), consider optimizing it",
                    "Profile stores cookies, login data, and browser preferences",
                    "Use backup_chrome_profile before major changes"
                ]
            )
            
        except Exception as e:
            return self._create_error_response(
                str(e),
                f"❌ Failed to get profile info: {str(e)}"
            )
    
    async def _list_chrome_profiles(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all Chrome profiles."""
        try:
            self._ensure_selenium_manager()
            
            profiles = self.selenium_manager.list_profiles()
            total_size = sum(profile.get("size_mb", 0) for profile in profiles)
            
            return self._create_success_response(
                f"✅ Found {len(profiles)} Chrome profiles (Total: {total_size:.2f} MB)",
                profiles=profiles,
                summary={
                    "total_profiles": len(profiles),
                    "total_size_mb": round(total_size, 2),
                    "current_profile": self.selenium_manager.profile_name if self.selenium_manager.use_persistent_profile else "temporary"
                }
            )
            
        except Exception as e:
            return self._create_error_response(
                str(e),
                f"❌ Failed to list profiles: {str(e)}"
            )
    
    async def _clear_chrome_profile(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Clear Chrome profile data."""
        try:
            self._ensure_selenium_manager()
            
            profile_name = arguments.get("profile_name")
            
            # Get profile info before clearing
            if profile_name:
                profile_info = self.selenium_manager.profile_manager.get_profile_info(profile_name)
            else:
                profile_info = self.selenium_manager.get_profile_info()
                profile_name = profile_info.get("name", self.DEFAULT_PROFILE_NAME)
            
            if not self.selenium_manager.use_persistent_profile:
                return {
                    "success": False,
                    "error": "Persistent profile not enabled",
                    "message": "❌ Persistent Chrome profile is not enabled in configuration"
                }
            
            if not profile_info.get("exists", profile_info.get("profile_exists", False)):
                return self._create_success_response(
                    f"✅ Profile '{profile_name}' already clean (doesn't exist)",
                    profile_name=profile_name
                )
            
            # Clear the profile
            success = self.selenium_manager.clear_profile(profile_name)
            
            if success:
                return self._create_success_response(
                    f"✅ Chrome profile '{profile_name}' cleared successfully",
                    details={
                        "profile_name": profile_name,
                        "profile_directory": profile_info.get("path") or profile_info.get("profile_directory"),
                        "size_cleared_mb": profile_info.get("size_mb", profile_info.get("profile_size_mb", 0))
                    },
                    next_steps=[
                        "You will need to sign in to Google again",
                        "Your login will be remembered for future sessions",
                        "All browser data (cookies, cache, etc.) has been cleared"
                    ]
                )
            else:
                return self._create_error_response(
                    "Failed to clear profile",
                    f"❌ Failed to clear Chrome profile '{profile_name}'. Check logs for details."
                )
            
        except Exception as e:
            return self._create_error_response(
                str(e),
                f"❌ Failed to clear profile: {str(e)}"
            )
    
    async def _optimize_chrome_profile(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize Chrome profile by cleaning temporary files."""
        try:
            self._ensure_selenium_manager()
            
            profile_name = arguments.get("profile_name")
            
            if not self.selenium_manager.use_persistent_profile:
                return {
                    "success": False,
                    "error": "Persistent profile not enabled",
                    "message": "❌ Persistent Chrome profile is not enabled in configuration"
                }
            
            # Get profile info before optimization
            if profile_name:
                profile_info_before = self.selenium_manager.profile_manager.get_profile_info(profile_name)
            else:
                profile_info_before = self.selenium_manager.get_profile_info()
                profile_name = profile_info_before.get("name", self.DEFAULT_PROFILE_NAME)
            
            size_before = profile_info_before.get("size_mb", profile_info_before.get("profile_size_mb", 0))
            
            # Optimize the profile
            success = self.selenium_manager.optimize_profile(profile_name)
            
            if success:
                # Get profile info after optimization
                if profile_name:
                    profile_info_after = self.selenium_manager.profile_manager.get_profile_info(profile_name)
                else:
                    profile_info_after = self.selenium_manager.get_profile_info()
                
                size_after = profile_info_after.get("size_mb", profile_info_after.get("profile_size_mb", 0))
                size_saved = max(0, size_before - size_after)
                
                return {
                    "success": True,
                    "message": f"✅ Chrome profile '{profile_name}' optimized successfully",
                    "details": {
                        "profile_name": profile_name,
                        "size_before_mb": size_before,
                        "size_after_mb": size_after,
                        "size_saved_mb": round(size_saved, 2),
                        "optimization_percentage": round((size_saved / size_before * 100) if size_before > 0 else 0, 1)
                    },
                    "benefits": [
                        "Removed temporary files and cache",
                        "Improved browser startup time",
                        "Freed up disk space",
                        "Login data and preferences preserved"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to optimize profile",
                    "message": f"❌ Failed to optimize Chrome profile '{profile_name}'. Check logs for details."
                }
            
        except Exception as e:
            error_msg = str(e)
            return {
                "success": False,
                "error": error_msg,
                "message": f"❌ Failed to optimize profile: {error_msg}"
            }
    
    async def _backup_chrome_profile(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup of Chrome profile."""
        try:
            self._ensure_selenium_manager()
            
            profile_name = arguments.get("profile_name")
            backup_name = arguments.get("backup_name")
            
            if not self.selenium_manager.use_persistent_profile:
                return {
                    "success": False,
                    "error": "Persistent profile not enabled",
                    "message": "❌ Persistent Chrome profile is not enabled in configuration"
                }
            
            # Get current profile name if not specified
            if not profile_name:
                profile_info = self.selenium_manager.get_profile_info()
                profile_name = profile_info.get("name", self.DEFAULT_PROFILE_NAME)
            
            # Create backup
            success = self.selenium_manager.backup_profile(profile_name, backup_name)
            
            if success:
                # Generate backup name if it was auto-generated
                if not backup_name:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{profile_name}_backup_{timestamp}"
                
                return {
                    "success": True,
                    "message": f"✅ Chrome profile '{profile_name}' backed up successfully",
                    "details": {
                        "source_profile": profile_name,
                        "backup_name": backup_name,
                        "backup_created": True
                    },
                    "next_steps": [
                        f"Backup saved as '{backup_name}'",
                        "Use restore_chrome_profile to restore from this backup",
                        "Backups are stored in the same profiles directory"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create backup",
                    "message": f"❌ Failed to backup Chrome profile '{profile_name}'. Check logs for details."
                }
            
        except Exception as e:
            error_msg = str(e)
            return {
                "success": False,
                "error": error_msg,
                "message": f"❌ Failed to backup profile: {error_msg}"
            }
    
    async def _restore_chrome_profile(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Restore Chrome profile from backup."""
        try:
            self._ensure_selenium_manager()
            
            backup_name = arguments["backup_name"]
            target_name = arguments.get("target_name")
            
            if not self.selenium_manager.use_persistent_profile:
                return {
                    "success": False,
                    "error": "Persistent profile not enabled",
                    "message": "❌ Persistent Chrome profile is not enabled in configuration"
                }
            
            # Get current profile name if target not specified
            if not target_name:
                profile_info = self.selenium_manager.get_profile_info()
                target_name = profile_info.get("name", self.DEFAULT_PROFILE_NAME)
            
            # Restore profile
            success = self.selenium_manager.restore_profile(backup_name, target_name)
            
            if success:
                return {
                    "success": True,
                    "message": f"✅ Chrome profile '{target_name}' restored from backup '{backup_name}'",
                    "details": {
                        "backup_name": backup_name,
                        "target_profile": target_name,
                        "restore_completed": True
                    },
                    "next_steps": [
                        f"Profile '{target_name}' now contains data from backup",
                        "Your previous login state should be restored",
                        "Browser preferences and settings are restored"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to restore from backup",
                    "message": f"❌ Failed to restore profile from backup '{backup_name}'. Check if backup exists."
                }
            
        except Exception as e:
            error_msg = str(e)
            return {
                "success": False,
                "error": error_msg,
                "message": f"❌ Failed to restore profile: {error_msg}"
            }
    
    async def _get_profiles_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of all Chrome profiles."""
        try:
            self._ensure_selenium_manager()
            
            summary = self.selenium_manager.get_profiles_summary()
            
            return {
                "success": True,
                "summary": summary,
                "message": f"✅ Profiles summary: {summary['total_profiles']} profiles, {summary['total_size_mb']:.2f} MB total",
                "recommendations": [
                    "Regularly optimize profiles to save disk space",
                    "Create backups before major changes",
                    "Clean up old unused profiles",
                    "Monitor profile sizes to prevent excessive growth"
                ]
            }
            
        except Exception as e:
            error_msg = str(e)
            return {
                "success": False,
                "error": error_msg,
                "message": f"❌ Failed to get profiles summary: {error_msg}"
            }

    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        try:
            # Set server capabilities
            server_capabilities = ServerCapabilities(
                tools=ToolsCapability()
            )
            
            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                self.logger.info("Starting MCP server with stdio transport")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="google-colab-mcp",
                        server_version="1.0.1",
                        capabilities=server_capabilities
                    )
                )
        except Exception as e:
            self.logger.error(f"Server run error: {e}")
            raise
        finally:
            await self._cleanup()

    async def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.selenium_manager:
                self.selenium_manager.close()
            
            # Cleanup idle sessions
            cleaned = self.session_manager.cleanup_idle_sessions()
            if cleaned > 0:
                self.logger.info(f"Cleaned up {cleaned} idle sessions")
            
            self.logger.info("Server cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


async def async_main(config_path: str = None):
    """Async main entry point."""
    try:
        server = ColabMCPServer(config_path=config_path)
        await server.run()
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)


def main():
    """Main entry point for console script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Colab Server - Google Colab integration for AI assistants")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--setup", action="store_true", help="Run initial setup")
    parser.add_argument("--version", action="version", version="google-colab-mcp 1.0.1")
    
    args = parser.parse_args()
    
    if args.setup:
        from .setup import main as setup_main
        setup_main()
        return
    
    asyncio.run(async_main(args.config))


if __name__ == "__main__":
    main()