# Google Colab MCP Server API Documentation

## Overview

The Google Colab MCP Server provides tools for interacting with Google Colab notebooks through the Model Context Protocol (MCP). It combines Google Drive API for notebook management with Selenium automation for code execution.

## Available Tools

### 1. create_colab_notebook

Creates a new Google Colab notebook.

**Parameters:**
- `name` (string, required): Name of the notebook
- `content` (string, optional): Initial notebook content in JSON format

**Returns:**
```json
{
  "success": true,
  "notebook": {
    "id": "1ABC123...",
    "name": "My Notebook.ipynb",
    "url": "https://drive.google.com/file/d/1ABC123.../view",
    "colab_url": "https://colab.research.google.com/drive/1ABC123..."
  }
}
```

**Example Usage:**
```python
# Create a simple notebook
result = await call_tool("create_colab_notebook", {
    "name": "Data Analysis Project"
})

# Create notebook with initial content
content = {
    "cells": [
        {
            "cell_type": "code",
            "source": ["print('Hello, World!')"],
            "metadata": {},
            "execution_count": None,
            "outputs": []
        }
    ]
}
result = await call_tool("create_colab_notebook", {
    "name": "Custom Notebook",
    "content": json.dumps(content)
})
```

### 2. run_code_cell

Executes Python code in a Colab notebook using Selenium automation.

**Parameters:**
- `code` (string, required): Python code to execute
- `notebook_id` (string, required): ID of the target notebook

**Returns:**
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "execution_time": 1.23,
  "cell_type": "code"
}
```

**Example Usage:**
```python
# Execute simple code
result = await call_tool("run_code_cell", {
    "code": "print('Hello from Colab!')\nprint(2 + 2)",
    "notebook_id": "1ABC123..."
})

# Execute data analysis code
code = """
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100)
})

print(f"Data shape: {data.shape}")
print(data.head())
"""
result = await call_tool("run_code_cell", {
    "code": code,
    "notebook_id": "1ABC123..."
})
```

### 3. install_package

Installs a Python package in the Colab environment.

**Parameters:**
- `package_name` (string, required): Name of the package to install
- `notebook_id` (string, required): ID of the target notebook

**Returns:**
```json
{
  "success": true,
  "output": "Successfully installed package-name-1.0.0\n",
  "error": null,
  "execution_time": 15.67,
  "cell_type": "code"
}
```

**Example Usage:**
```python
# Install a single package
result = await call_tool("install_package", {
    "package_name": "seaborn",
    "notebook_id": "1ABC123..."
})

# Install package with version
result = await call_tool("install_package", {
    "package_name": "tensorflow==2.13.0",
    "notebook_id": "1ABC123..."
})
```

### 4. get_notebook_content

Retrieves the complete content of a Colab notebook via Drive API.

**Parameters:**
- `notebook_id` (string, required): ID of the notebook

**Returns:**
```json
{
  "success": true,
  "content": {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {...},
    "cells": [...]
  }
}
```

**Example Usage:**
```python
result = await call_tool("get_notebook_content", {
    "notebook_id": "1ABC123..."
})

# Access specific cells
content = result["content"]
for i, cell in enumerate(content["cells"]):
    print(f"Cell {i}: {cell['cell_type']}")
    if cell["cell_type"] == "code":
        print(f"  Source: {cell['source']}")
```

### 5. list_notebooks

Lists the user's Colab notebooks from Google Drive.

**Parameters:**
- `max_results` (integer, optional): Maximum number of notebooks to return (default: 50)

**Returns:**
```json
{
  "success": true,
  "notebooks": [
    {
      "id": "1ABC123...",
      "name": "My Notebook.ipynb",
      "modified": "2024-01-15T10:30:00.000Z",
      "url": "https://drive.google.com/file/d/1ABC123.../view",
      "colab_url": "https://colab.research.google.com/drive/1ABC123...",
      "size": "12345"
    }
  ],
  "count": 1
}
```

**Example Usage:**
```python
# List all notebooks
result = await call_tool("list_notebooks", {})

# List recent notebooks only
result = await call_tool("list_notebooks", {
    "max_results": 10
})

# Process results
for notebook in result["notebooks"]:
    print(f"{notebook['name']} - Modified: {notebook['modified']}")
```

### 6. upload_file_to_colab

Uploads a file to the Colab environment (triggers file upload dialog).

**Parameters:**
- `file_path` (string, required): Path to the file to upload
- `notebook_id` (string, required): ID of the target notebook

**Returns:**
```json
{
  "success": true,
  "output": "Uploaded: data.csv (1024 bytes)\n",
  "error": null,
  "execution_time": 5.43,
  "cell_type": "code"
}
```

**Example Usage:**
```python
result = await call_tool("upload_file_to_colab", {
    "file_path": "/path/to/local/data.csv",
    "notebook_id": "1ABC123..."
})
```

### 7. get_runtime_info

Gets information about the Colab runtime environment.

**Parameters:**
- `notebook_id` (string, required): ID of the target notebook

**Returns:**
```json
{
  "success": true,
  "output": "System Information:\nPlatform: Linux-5.4.0-...\nPython version: 3.10.12\nCPU count: 2\nMemory: 12.7 GB\nGPU: Tesla T4\nGPU Memory: 15.0 GB\n",
  "error": null,
  "execution_time": 2.15,
  "cell_type": "code"
}
```

**Example Usage:**
```python
result = await call_tool("get_runtime_info", {
    "notebook_id": "1ABC123..."
})

# Parse the output to extract system info
output_lines = result["output"].split('\n')
for line in output_lines:
    if line.startswith("GPU:"):
        print(f"Available GPU: {line}")
```

### 8. get_session_info

Gets information about the current session for a notebook.

**Parameters:**
- `notebook_id` (string, required): ID of the notebook

**Returns:**
```json
{
  "success": true,
  "session": {
    "notebook_id": "1ABC123...",
    "session_id": "session_456",
    "status": "connected",
    "runtime_type": "cpu",
    "idle_time": 120.5,
    "connection_duration": 1800.0,
    "is_idle": false,
    "is_connected": true,
    "error_message": null
  }
}
```

**Example Usage:**
```python
result = await call_tool("get_session_info", {
    "notebook_id": "1ABC123..."
})

session = result["session"]
if session["is_connected"]:
    print(f"Session active for {session['connection_duration']:.0f} seconds")
else:
    print("Session is not connected")
```

## Error Handling

All tools return a consistent error format when operations fail:

```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

Common error scenarios:
- **Authentication failures**: Invalid or expired Google credentials
- **Network issues**: Unable to reach Google services or Colab
- **Notebook not found**: Invalid notebook ID
- **Selenium timeouts**: Colab interface not responding
- **Code execution errors**: Python syntax errors or runtime exceptions

## Session Management

The server automatically manages Colab sessions:

- **Session Creation**: Automatically created when first accessing a notebook
- **Connection Management**: Handles reconnection when sessions expire
- **Idle Detection**: Tracks activity and cleans up idle sessions
- **Error Recovery**: Attempts to recover from connection issues

## Rate Limits and Quotas

Be aware of Google API and Colab limitations:

- **Drive API**: 1000 requests per 100 seconds per user
- **Colab Runtime**: May disconnect after periods of inactivity
- **Execution Time**: Long-running code may timeout
- **File Size**: Large file uploads may fail

## Best Practices

1. **Error Handling**: Always check the `success` field in responses
2. **Session Reuse**: Reuse notebook sessions when possible
3. **Code Chunking**: Break large code blocks into smaller cells
4. **Resource Management**: Monitor memory and compute usage
5. **Authentication**: Keep credentials secure and refresh tokens regularly

## Integration Examples

### With VS Code Cline

```typescript
// Example Cline integration
const result = await mcp.callTool("create_colab_notebook", {
  name: "AI Analysis Project"
});

if (result.success) {
  const notebookId = result.notebook.id;
  
  // Install required packages
  await mcp.callTool("install_package", {
    package_name: "transformers torch",
    notebook_id: notebookId
  });
  
  // Run analysis code
  await mcp.callTool("run_code_cell", {
    code: `
      from transformers import pipeline
      classifier = pipeline("sentiment-analysis")
      result = classifier("I love this MCP server!")
      print(result)
    `,
    notebook_id: notebookId
  });
}
```

### Batch Operations

```python
# Process multiple notebooks
notebooks = await call_tool("list_notebooks", {"max_results": 10})

for notebook in notebooks["notebooks"]:
    # Get runtime info for each
    runtime_info = await call_tool("get_runtime_info", {
        "notebook_id": notebook["id"]
    })
    
    # Install common packages
    await call_tool("install_package", {
        "package_name": "pandas numpy matplotlib",
        "notebook_id": notebook["id"]
    })
```