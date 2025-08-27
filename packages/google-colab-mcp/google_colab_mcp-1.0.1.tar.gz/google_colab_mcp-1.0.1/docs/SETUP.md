# Google Colab MCP Server Setup Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Cloud Project** with Drive API enabled
3. **Chrome or Firefox browser** installed
4. **VS Code** with Cline extension (for MCP integration)

## Step 1: Google Cloud Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 1.2 Enable APIs

1. Navigate to "APIs & Services" > "Library"
2. Search for and enable:
   - Google Drive API
   - Google Sheets API (optional, for enhanced functionality)

### 1.3 Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Download the credentials JSON file
5. Rename it to `credentials.json`

## Step 2: Installation

### 2.1 Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd google-colab-mcp

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 2.2 Configuration

1. Copy the credentials file:
   ```bash
   cp /path/to/your/credentials.json config/credentials.json
   ```

2. Copy and customize environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your preferences
   ```

3. Customize server configuration:
   ```bash
   # Edit config/server_config.json as needed
   ```

## Step 3: WebDriver Setup

### For Chrome (Recommended)

The server will automatically download ChromeDriver using webdriver-manager.

### For Firefox

```bash
# Install Firefox if not already installed
# The server will automatically download GeckoDriver
```

### Manual WebDriver Installation (Optional)

If automatic download fails:

1. **ChromeDriver**: Download from [ChromeDriver](https://chromedriver.chromium.org/)
2. **GeckoDriver**: Download from [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
3. Add to your system PATH

## Step 4: First Run and Authentication

### 4.1 Test Authentication

```bash
python -c "
from src.auth_manager import AuthManager
auth = AuthManager()
if auth.authenticate():
    print('Authentication successful!')
    user = auth.get_user_info()
    print(f'Logged in as: {user.get(\"displayName\", \"Unknown\")}')
else:
    print('Authentication failed!')
"
```

### 4.2 Start the Server

```bash
# Using the entry point script (recommended)
python run_server.py

# Or on Windows
run_server.bat

# Test components first (optional)
python test_components.py
```

On first run:
1. A browser window will open for Google OAuth
2. Sign in with your Google account
3. Grant permissions to access Drive
4. The browser will show a success message
5. Return to the terminal - authentication is complete

## Step 5: VS Code Integration

### 5.1 Configure Cline Extension

Add to your VS Code settings or workspace settings:

```json
{
  "cline.mcpServers": {
    "google-colab-mcp": {
      "command": "google-colab-mcp",
      "args": [],
      "cwd": "/path/to/google-colab-mcp",
      "env": {}
    }
  }
}
```

Or create a `.kiro/settings/mcp.json` file in your workspace:

```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "google-colab-mcp",
      "args": [],
      "cwd": "C:/path/to/google-colab-mcp",
      "env": {}
    }
  }
}
```

### 5.2 Test Integration

1. Open VS Code with Cline extension
2. Start a new Cline session
3. Try commands like:
   - "List my Colab notebooks"
   - "Create a new notebook called 'Test'"
   - "Run some Python code in Colab"

## Step 6: Verification

### 6.1 Test Basic Functionality

```python
# Test script - save as test_server.py
import asyncio
import json
from src.mcp_server import ColabMCPServer

async def test_server():
    server = ColabMCPServer()
    
    # Test authentication
    await server._ensure_authenticated()
    print("✓ Authentication successful")
    
    # Test listing notebooks
    result = await server._list_notebooks({"max_results": 5})
    print(f"✓ Found {result['count']} notebooks")
    
    print("Server is working correctly!")

if __name__ == "__main__":
    asyncio.run(test_server())
```

Run the test:
```bash
python test_server.py
```

## Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Check credentials.json is in the correct location
   - Verify Google Cloud project has Drive API enabled
   - Ensure OAuth consent screen is configured

2. **WebDriver Issues**
   - Update Chrome/Firefox to latest version
   - Check if webdriver-manager can access the internet
   - Try manual WebDriver installation

3. **Selenium Timeouts**
   - Increase timeout values in config/server_config.json
   - Check if Colab is accessible in your region
   - Verify Google account has access to Colab

4. **Permission Errors**
   - Ensure the token.json file is writable
   - Check file permissions on config directory

### Debug Mode

Enable debug logging:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Getting Help

1. Check the logs in `logs/colab_mcp.log`
2. Enable debug mode for detailed output
3. Verify all prerequisites are met
4. Test each component individually

## Security Notes

- Keep `credentials.json` and `token.json` secure
- Don't commit these files to version control
- Regularly review OAuth permissions in your Google account
- Use environment variables for sensitive configuration

## Next Steps

Once setup is complete:
1. Explore the available tools and their capabilities
2. Integrate with your development workflow
3. Customize configuration for your needs
4. Consider setting up automated testing