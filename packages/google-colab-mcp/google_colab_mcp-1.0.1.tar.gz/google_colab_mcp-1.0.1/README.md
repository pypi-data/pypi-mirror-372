# Google Colab MCP Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A **Model Context Protocol (MCP)** server that enables AI assistants to interact directly with Google Colab notebooks. This server provides seamless integration between AI assistants (Claude, ChatGPT, etc.) and Google Colab environments for automated notebook creation, code execution, and data science workflows.

**Key Updates**: Enhanced timeout handling, robust error management, and non-blocking code execution. The system provides comprehensive error reporting and stable performance during long-running operations.

## Features

**Core Capabilities**
- **Automatic OAuth2 Authentication** - One-time setup with secure Google authentication
- **Persistent Chrome Profile Management** - Maintains login sessions across restarts
- **Complete Notebook Operations** - Create, read, update, list, and manage Colab notebooks
- **Code Execution Engine** - Execute Python code directly in Colab environments with real-time feedback
- **Package Management** - Install and manage Python packages in Colab runtime environments
- **File Operations** - Upload and manage files within Colab environments
- **Session Management** - Handle Colab runtime sessions with automatic cleanup
- **Enhanced Error Handling** - Comprehensive error reporting with detailed troubleshooting
- **Smart Timeout Management** - Non-blocking execution with configurable timeout handling
- **Profile Optimization** - Tools to manage Chrome profiles and session data efficiently
- **Execution Monitoring** - Real-time tracking of code execution status and performance
- **Background Processing** - Support for long-running operations without blocking the main process

## Use Cases

- **AI-Powered Data Science**: Enable AI assistants to create and execute data analysis notebooks
- **Automated ML Workflows**: Build machine learning pipelines through natural language interactions
- **Educational Tools**: Create interactive coding tutorials and examples with AI assistance
- **Research Automation**: Automate repetitive research tasks and data processing in Colab
- **Code Generation**: Generate, test, and validate code snippets in a cloud environment
- **Collaborative Development**: Share and manage notebooks through AI-driven conversations

## Getting Started

### Installation

**Install from PyPI (Recommended):**
```bash
pip install google-colab-mcp
```

**Install from Source:**
```bash
git clone https://github.com/inkbytefo/google-colab-mcp.git
cd google-colab-mcp
pip install -e .
```

### Configuration Setup

**Automated Initialization (Recommended):**

Use the AI assistant for setup:
```
"Initialize my Google Colab MCP configuration"
```

**Manual Initialization:**
```bash
python -m mcp_colab_server.config_manager --init
```

This command creates your configuration directory at `~/.mcp-colab/` containing:
- Server configuration files
- Logs directory for troubleshooting
- Credentials template for Google API setup

### Google Cloud Setup

**Required Steps:**
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Enable the **Google Drive API** for your project
4. Create **OAuth 2.0 credentials** (select "Desktop Application" type)
5. Download the credentials file as `credentials.json`
6. Place `credentials.json` in your `~/.mcp-colab/` directory

**Important Notes:**
- Ensure you select "Desktop Application" when creating OAuth 2.0 credentials
- The credentials file must be named exactly `credentials.json`
- Keep your credentials file secure and never commit it to version control

### Authentication Setup

**Run the setup script:**
```bash
python -m mcp_colab_server.setup
```

**The setup process will:**
- Validate your credentials file format and content
- Launch a browser window for Google OAuth authentication
- Save authentication tokens to `~/.mcp-colab/token.json`
- Perform a connection test to verify everything works

**Check configuration status:**
```bash
python -m mcp_colab_server.config_manager --status
```

This command displays your current configuration status, authentication state, and any potential issues.

### Chrome Profile Management

The system automatically manages Chrome browser profiles to maintain persistent Google login sessions:

**Profile Management Commands:**
```bash
# View all Chrome profiles and their status
python -m mcp_colab_server.config_manager --profile-summary

# Optimize profiles by cleaning cache and temporary files
python -m mcp_colab_server.config_manager --optimize-profiles

# Remove old or unused profiles
python -m mcp_colab_server.config_manager --clean-profiles
```

**Profile Management Benefits:**
- **Persistent Authentication**: Google login sessions are remembered between server restarts
- **Faster Startup Times**: No need to re-authenticate for each session
- **Automatic Cleanup**: Profiles are automatically optimized to minimize disk usage
- **User Isolation**: Each user maintains their own separate profile directory
- **Session Recovery**: Ability to recover from browser crashes or unexpected shutdowns

### MCP Integration

**For Claude Desktop Application:**

Add the following configuration to your Claude desktop settings:

```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "google-colab-mcp",
      "args": [],
      "env": {
        "MCP_COLAB_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**For Development or Custom Setup:**

```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "python",
      "args": ["-m", "mcp_colab_server.server"],
      "cwd": "/path/to/your/google-colab-mcp",
      "env": {
        "MCP_COLAB_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Available Tools

| Tool Name | Function | Example Usage |
|-----------|----------|---------------|
| `init_user_config` | Initialize user configuration directory | "Initialize my Google Colab MCP configuration" |
| `check_auth_status` | Verify authentication and connection status | "Check my Google authentication status" |
| `setup_google_credentials` | Get step-by-step setup instructions | "How do I set up Google credentials?" |
| `authenticate_google` | Complete Google OAuth authentication flow | "Authenticate with Google" |
| `create_colab_notebook` | Create a new Colab notebook | "Create a notebook called 'Data Analysis'" |
| `list_notebooks` | List all accessible Colab notebooks | "Show me my Colab notebooks" |
| `get_notebook_content` | Retrieve notebook content and structure | "Show me the content of my latest notebook" |
| `run_code_cell` | Execute Python code in Colab runtime | "Run this code: import pandas as pd" |
| `install_package` | Install Python packages in Colab | "Install matplotlib in my notebook" |
| `upload_file_to_colab` | Upload files to Colab environment | "Upload data.csv to my notebook" |
| `get_runtime_info` | Get Colab runtime status and information | "What's the status of my Colab runtime?" |
| `get_session_info` | Get current session details | "Show me my current Colab session" |
| `get_chrome_profile_info` | Get Chrome profile status and metrics | "Check my browser profile status" |
| `clear_chrome_profile` | Reset Chrome profile and clear data | "Clear my browser data and reset login" |

## Example Conversations

**Working with AI Assistants (Claude/ChatGPT):**

**Notebook Creation:**
```
User: "Create a new Colab notebook for analyzing sales data"
AI: Creates notebook and responds with notebook URL and ID
```

**Package Installation and Code Execution:**
```
User: "Install pandas and matplotlib, then create a simple plot"
AI: Installs packages and generates plotting code in your Colab
```

**Notebook Management:**
```
User: "List all my notebooks and show me the most recent one"
AI: Lists notebooks and displays the content of the latest one
```

**Complex Data Analysis:**
```
User: "Load my sales data, calculate monthly trends, and create a visualization"
AI: Executes multi-step data analysis workflow in Colab
```

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│  MCP Server      │◄──►│  Google Colab   │
│  (Claude, etc.) │    │  (This Project)  │    │   Notebooks     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Google Drive    │
                       │      API         │
                       └──────────────────┘
```

**Component Overview:**
The server functions as a bridge between AI assistants and Google Colab, utilizing:
- **Google Drive API** for notebook management and storage operations
- **Selenium WebDriver** for browser automation and code execution
- **MCP Protocol** for standardized communication with AI assistants
- **Chrome Profile Management** for persistent authentication sessions

**Data Flow:**
1. AI Assistant sends requests through MCP protocol
2. Server processes requests and manages authentication
3. Server interacts with Google Colab via Selenium automation
4. Results are returned to AI Assistant through MCP protocol

## Configuration

### Server Configuration

The server uses a configuration file located at `~/.mcp-colab/server_config.json`:

```json
{
  "selenium": {
    "browser": "chrome",
    "headless": false,
    "timeout": 30,
    "profile": {
      "use_persistent_profile": true,
      "profile_directory": null,
      "auto_create_profile": true
    }
  },
  "colab": {
    "execution_timeout": 300,
    "max_retries": 3
  },
  "logging": {
    "level": "INFO"
  }
}
```

### Chrome Profile Configuration

The server supports persistent Chrome profiles to maintain Google login sessions:

**Key Features:**
- **Automatic Login**: No need to sign in repeatedly
- **Session Persistence**: Login data saved securely between sessions
- **Profile Management**: Built-in tools to manage and clear profile data

**Configuration Options:**
- `use_persistent_profile`: Enable/disable persistent profiles (default: true)
- `profile_directory`: Custom profile location (default: `~/.mcp-colab/chrome_profiles/default`)
- `auto_create_profile`: Automatically create profile directory (default: true)

**Management Commands:**
- `get_chrome_profile_info`: Check profile status and disk usage
- `clear_chrome_profile`: Clear profile data (requires re-authentication)

### MCP Configuration Options

**Advanced Configuration Example:**
```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "google-colab-mcp",
      "args": [],
      "env": {
        "MCP_COLAB_LOG_LEVEL": "INFO",
        "MCP_COLAB_HEADLESS": "false"
      },
      "autoApprove": [
        "list_notebooks",
        "get_notebook_content",
        "get_runtime_info"
      ]
    }
  }
}
```

**Environment Variables:**
- `MCP_COLAB_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_COLAB_HEADLESS`: Run Chrome in headless mode (true/false)
- `MCP_COLAB_TIMEOUT`: Default timeout for operations (seconds)

## Troubleshooting

### Common Issues and Solutions

**Authentication Problems**
```bash
# Re-run the setup script to fix authentication issues
python -m mcp_colab_server.setup

# Clear existing tokens and re-authenticate
rm ~/.mcp-colab/token.json
python -m mcp_colab_server.setup

# Check current authentication status
python -m mcp_colab_server.config_manager --status
```

**Browser and WebDriver Issues**
```bash
# Update Chrome/Firefox to the latest version
# Install or update WebDriver dependencies
pip install webdriver-manager --upgrade
pip install selenium --upgrade

# Clear Chrome profiles if having persistent issues
python -m mcp_colab_server.config_manager --clean-profiles
```

**MCP Server Connection Problems**
```bash
# Test if the server starts correctly
google-colab-mcp

# Verify installation
pip show google-colab-mcp

# Reinstall if necessary
pip install --force-reinstall google-colab-mcp
```

### Debug Mode Configuration

Enable detailed logging for troubleshooting:

```json
{
  "env": {
    "MCP_COLAB_LOG_LEVEL": "DEBUG",
    "MCP_COLAB_HEADLESS": "false"
  }
}
```

### Performance Optimization

**For Better Performance:**
- Use headless mode (`MCP_COLAB_HEADLESS": "true"`) in production
- Regularly optimize Chrome profiles using `--optimize-profiles`
- Increase timeout values for slower network connections
- Monitor log files for performance bottlenecks

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for detailed information.

**Development Workflow:**
1. Fork the repository on GitHub
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/your-feature-name`
6. Open a Pull Request with a detailed description

**Development Setup:**
```bash
# Clone the repository
git clone https://github.com/inkbytefo/google-colab-mcp.git
cd google-colab-mcp

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest tests/
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for providing the communication standard
- [Google Colab](https://colab.research.google.com/) for the cloud-based notebook platform
- [Anthropic](https://www.anthropic.com/) for Claude and MCP development
- The open-source community for valuable contributions and feedback

## Support and Resources

**Documentation and Help:**
- [Project Documentation](docs/)
- [Issue Tracker](https://github.com/inkbytefo/google-colab-mcp/issues)
- [Community Discussions](https://github.com/inkbytefo/google-colab-mcp/discussions)
- [Changelog and Updates](CHANGELOG.md)

**Getting Help:**
- Search existing issues before creating new ones
- Provide detailed information when reporting bugs
- Include log files and configuration details for faster resolution

---

**Project Information:**
- **Author:** inkbytefo
- **Version:** 1.0.1
- **Repository:** [github.com/inkbytefo/google-colab-mcp](https://github.com/inkbytefo/google-colab-mcp)
- **License:** MIT
- **Python Version:** 3.8+

*Built for the AI and Data Science community*