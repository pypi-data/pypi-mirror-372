"""Basic usage examples for the Google Colab MCP server."""

import asyncio
import json
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

from mcp_colab_server.server import ColabMCPServer


async def example_create_and_run_notebook():
    """Example: Create a notebook and run code in it."""
    print("=== Creating and Running Notebook Example ===")
    
    server = ColabMCPServer()
    
    try:
        # Ensure authentication
        await server._ensure_authenticated()
        print("✓ Authentication successful")
        
        # Create a new notebook
        create_result = await server._create_notebook({
            "name": "Example Data Analysis"
        })
        
        if create_result["success"]:
            notebook_id = create_result["notebook"]["id"]
            print(f"✓ Created notebook: {create_result['notebook']['name']}")
            print(f"  Colab URL: {create_result['notebook']['colab_url']}")
            
            # Install required packages
            print("\n--- Installing packages ---")
            install_result = await server._install_package({
                "package_name": "pandas matplotlib seaborn",
                "notebook_id": notebook_id
            })
            
            if install_result["success"]:
                print("✓ Packages installed successfully")
            else:
                print(f"✗ Package installation failed: {install_result.get('error')}")
            
            # Run some data analysis code
            print("\n--- Running analysis code ---")
            analysis_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create sample data
np.random.seed(42)
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

print("Dataset created:")
print(f"Shape: {data.shape}")
print(f"Columns: {list(data.columns)}")
print("\\nFirst 5 rows:")
print(data.head())

# Basic statistics
print("\\nBasic statistics:")
print(data.describe())

# Create a simple plot
plt.figure(figsize=(8, 6))
for cat in data['category'].unique():
    subset = data[data['category'] == cat]
    plt.scatter(subset['x'], subset['y'], label=f'Category {cat}', alpha=0.7)

plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Sample Data Visualization')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print("\\nAnalysis complete!")
"""
            
            run_result = await server._run_code_cell({
                "code": analysis_code,
                "notebook_id": notebook_id
            })
            
            if run_result["success"]:
                print("✓ Code executed successfully")
                print(f"  Execution time: {run_result.get('execution_time', 0):.2f} seconds")
                if run_result.get('output'):
                    print("  Output:")
                    print("  " + "\n  ".join(run_result['output'].split('\n')[:10]))  # First 10 lines
            else:
                print(f"✗ Code execution failed: {run_result.get('error')}")
            
            # Get runtime information
            print("\n--- Runtime Information ---")
            runtime_result = await server._get_runtime_info({
                "notebook_id": notebook_id
            })
            
            if runtime_result["success"]:
                print("✓ Runtime info retrieved")
                if runtime_result.get('output'):
                    print("  " + "\n  ".join(runtime_result['output'].split('\n')[:5]))  # First 5 lines
            
            return notebook_id
            
        else:
            print(f"✗ Failed to create notebook: {create_result.get('error')}")
            return None
            
    except Exception as e:
        print(f"✗ Example failed: {e}")
        return None


async def example_list_and_manage_notebooks():
    """Example: List existing notebooks and manage them."""
    print("\n=== Listing and Managing Notebooks Example ===")
    
    server = ColabMCPServer()
    
    try:
        await server._ensure_authenticated()
        
        # List existing notebooks
        list_result = await server._list_notebooks({"max_results": 10})
        
        if list_result["success"]:
            notebooks = list_result["notebooks"]
            print(f"✓ Found {len(notebooks)} notebooks")
            
            for i, notebook in enumerate(notebooks[:5], 1):  # Show first 5
                print(f"  {i}. {notebook['name']}")
                print(f"     ID: {notebook['id']}")
                print(f"     Modified: {notebook['modified']}")
                print(f"     Colab URL: {notebook['colab_url']}")
                print()
            
            # Get content of the first notebook (if any)
            if notebooks:
                first_notebook = notebooks[0]
                print(f"--- Content of '{first_notebook['name']}' ---")
                
                content_result = await server._get_notebook_content({
                    "notebook_id": first_notebook["id"]
                })
                
                if content_result["success"]:
                    content = content_result["content"]
                    print(f"✓ Notebook has {len(content.get('cells', []))} cells")
                    
                    # Show cell types
                    cell_types = {}
                    for cell in content.get('cells', []):
                        cell_type = cell.get('cell_type', 'unknown')
                        cell_types[cell_type] = cell_types.get(cell_type, 0) + 1
                    
                    print("  Cell types:")
                    for cell_type, count in cell_types.items():
                        print(f"    {cell_type}: {count}")
                
                else:
                    print(f"✗ Failed to get notebook content: {content_result.get('error')}")
        
        else:
            print(f"✗ Failed to list notebooks: {list_result.get('error')}")
            
    except Exception as e:
        print(f"✗ Example failed: {e}")


async def example_session_management():
    """Example: Session management and monitoring."""
    print("\n=== Session Management Example ===")
    
    server = ColabMCPServer()
    
    try:
        await server._ensure_authenticated()
        
        # Create a test notebook for session management
        create_result = await server._create_notebook({
            "name": "Session Test Notebook"
        })
        
        if create_result["success"]:
            notebook_id = create_result["notebook"]["id"]
            print(f"✓ Created test notebook: {notebook_id}")
            
            # Get initial session info
            session_result = await server._get_session_info({
                "notebook_id": notebook_id
            })
            
            if session_result["success"]:
                session = session_result["session"]
                if session:
                    print("✓ Session information:")
                    print(f"  Status: {session['status']}")
                    print(f"  Runtime type: {session['runtime_type']}")
                    print(f"  Is connected: {session['is_connected']}")
                    print(f"  Is idle: {session['is_idle']}")
                else:
                    print("  No active session found")
            
            # Run a simple command to establish session
            print("\n--- Establishing session ---")
            run_result = await server._run_code_cell({
                "code": "print('Session established!')\nimport sys\nprint(f'Python version: {sys.version}')",
                "notebook_id": notebook_id
            })
            
            if run_result["success"]:
                print("✓ Session established")
                print(f"  Output: {run_result.get('output', '')[:100]}...")
                
                # Get updated session info
                session_result = await server._get_session_info({
                    "notebook_id": notebook_id
                })
                
                if session_result["success"] and session_result["session"]:
                    session = session_result["session"]
                    print("✓ Updated session information:")
                    print(f"  Status: {session['status']}")
                    print(f"  Is connected: {session['is_connected']}")
                    print(f"  Connection duration: {session.get('connection_duration', 0):.1f}s")
            
            return notebook_id
            
        else:
            print(f"✗ Failed to create test notebook: {create_result.get('error')}")
            return None
            
    except Exception as e:
        print(f"✗ Session management example failed: {e}")
        return None


async def main():
    """Run all examples."""
    print("Google Colab MCP Server - Usage Examples")
    print("=" * 50)
    
    try:
        # Example 1: Create and run notebook
        notebook_id1 = await example_create_and_run_notebook()
        
        # Example 2: List and manage notebooks
        await example_list_and_manage_notebooks()
        
        # Example 3: Session management
        notebook_id2 = await example_session_management()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        
        if notebook_id1:
            print(f"Created notebook 1: https://colab.research.google.com/drive/{notebook_id1}")
        if notebook_id2:
            print(f"Created notebook 2: https://colab.research.google.com/drive/{notebook_id2}")
        
        print("\nYou can now open these notebooks in Colab to see the results.")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nExamples failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())