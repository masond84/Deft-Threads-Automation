"""
Vercel-compatible handler for FastAPI app
Vercel natively supports ASGI apps - no Mangum needed
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
import index

# Export as a callable function
def handler(request):
    return index.app(request)

# Also try exporting the app directly as a fallback
handler = index.app