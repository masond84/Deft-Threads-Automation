"""
Vercel-compatible handler for FastAPI app
Vercel natively supports ASGI apps, so we don't need Mangum
"""
import sys
import importlib.util
from pathlib import Path

# Add project root to path (important for src imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import index.py directly using importlib
index_path = Path(__file__).parent / "index.py"
spec = importlib.util.spec_from_file_location("index", index_path)
index_module = importlib.util.module_from_spec(spec)
sys.modules["index"] = index_module
spec.loader.exec_module(index_module)

# Export the FastAPI app directly - Vercel handles ASGI natively
handler = index_module.app