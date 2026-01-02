"""
Test script for local API testing
"""
import sys
import os
from pathlib import Path
import importlib.util

# Get project root
project_root = Path(__file__).parent.parent

# Change to project root
os.chdir(project_root)

# Add to path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

if __name__ == "__main__":
    import uvicorn
    
    # Use importlib to load the module
    spec = importlib.util.spec_from_file_location(
        "api.index",
        project_root / "api" / "index.py"
    )
    api_index = importlib.util.module_from_spec(spec)
    sys.modules["api.index"] = api_index
    spec.loader.exec_module(api_index)
    
    app = api_index.app
    
    print("Starting local API server...")
    print("Visit http://localhost:8000 for the web UI")
    print("API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Changed to False
    )
