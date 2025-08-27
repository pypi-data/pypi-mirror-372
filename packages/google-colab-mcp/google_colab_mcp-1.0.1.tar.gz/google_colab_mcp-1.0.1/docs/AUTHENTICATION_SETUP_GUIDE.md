# 🔐 Google Colab MCP Server - Complete Authentication Setup Guide

## 📋 **Overview**
This guide walks you through setting up Google authentication for the MCP Colab Server step-by-step.

## 🛠️ **Prerequisites**
- Python 3.8+ installed
- Chrome browser
- Google account
- Internet connection

---

## 📁 **File Locations**

### **User Configuration Directory:** 
`C:\Users\{username}\.mcp-colab\`

### **Required Files:**
- **`credentials.json`** - Google OAuth2 credentials from Google Cloud Console
- **`token.json`** - Generated automatically after successful authentication
- **`server_config.json`** - Server configuration (created automatically)

---

## 🚀 **Step-by-Step Setup**

### **Step 1: Initialize Configuration**
```bash
# Run the MCP server to create initial config
python -m mcp_colab_server.server --setup
```

This creates:
- `C:\Users\{username}\.mcp-colab\server_config.json`
- `C:\Users\{username}\.mcp-colab\credentials.json.template`
- `C:\Users\{username}\.mcp-colab\logs\` directory

### **Step 2: Google Cloud Console Setup**

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create or Select Project**
   - Create a new project or select existing one
   - Note the project ID for reference

3. **Enable Google Drive API**
   - Go to: `APIs & Services` > `Library`
   - Search for "Google Drive API"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to: `APIs & Services` > `Credentials`
   - Click: `Create Credentials` > `OAuth 2.0 Client ID`
   - Choose: `Desktop Application`
   - Name: `MCP Colab Server`

5. **Download Credentials**
   - Click the download button next to your credentials
   - Save as: `C:\Users\{username}\.mcp-colab\credentials.json`

### **Step 3: Authentication**

1. **Run Authentication Setup**
   ```bash
   python -m mcp_colab_server.setup
   ```

2. **Complete OAuth Flow**
   - Browser will open automatically
   - Sign in with your Google account
   - Grant permissions to the application
   - You should see "Authentication successful!"

3. **Verify Setup**
   - Check that `token.json` was created in user directory
   - Test with: `check_auth_status` tool in Claude Desktop

---

## 🔧 **Claude Desktop Configuration**

### **Config File Location:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### **Example Configuration:**
```json
{
  "mcpServers": {
    "google-colab-mcp": {
      "command": "python",
      "args": [
        "-m",
        "mcp_colab_server.server"
      ],
      "env": {
        "PYTHONPATH": "c:\\Users\\tpoyr\\OneDrive\\Desktop\\google-colab-mcp\\src"
      }
    }
  }
}
```

---

## 🧪 **Testing & Verification**

### **1. Test Authentication Status**
In Claude Desktop, try:
- `check_auth_status` - Should show authenticated: true
- `list_notebooks` - Should list your Colab notebooks

### **2. Test Basic Operations**
- `create_colab_notebook` with name "Test MCP"
- `run_code_cell` with simple Python code
- `list_chrome_profiles` - Should show Chrome profile info

---

## ❌ **Troubleshooting**

### **Common Issues:**

#### **"Credentials file not found"**
- Ensure `credentials.json` is in: `C:\Users\{username}\.mcp-colab\`
- Check file is valid JSON (not the template)

#### **"Authentication failed"**
- Re-run setup: `python -m mcp_colab_server.setup`
- Delete `token.json` and re-authenticate
- Ensure Google Drive API is enabled

#### **"Unicode encoding error"**
- Fixed in latest version with safe message formatting
- Restart Claude Desktop after updating

#### **"Module not found"**
- Ensure server is installed: `pip install -e .`
- Check PYTHONPATH in Claude Desktop config

### **Manual Reset:**
```bash
# Delete all authentication data
rmdir /s "C:\Users\%USERNAME%\.mcp-colab"

# Re-run setup
python -m mcp_colab_server.server --setup
python -m mcp_colab_server.setup
```

---

## 📞 **Support**

If you encounter issues:
1. Check logs in: `C:\Users\{username}\.mcp-colab\logs\colab_mcp.log`
2. Use `check_auth_status` tool for diagnosis
3. Re-run setup if needed

**Happy coding with AI-powered Google Colab! 🎉**