"""
Vercel-compatible handler for FastAPI app
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from api.index import app
from mangum import Mangum

# Create Mangum instance
asgi_app = Mangum(app, lifespan="off")

# Export as a callable function for Vercel
def handler(event, context):
    """Vercel-compatible handler function"""
    return asgi_app(event, context)