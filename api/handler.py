"""
Vercel-compatible handler for FastAPI app
Vercel natively supports ASGI apps
"""
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
api_dir = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(api_dir))
sys.path.insert(0, str(project_root / "src"))

# Import and export app directly
from mangum import Mangum
import index

handler = Mangum(index.app)