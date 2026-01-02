"""
Vercel-compatible handler for FastAPI app
"""
from api.index import app
from mangum import Mangum

# Export handler for Vercel
handler = Mangum(app, lifespan="off")