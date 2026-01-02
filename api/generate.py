"""
API endpoints for post generation (all 3 paths)
"""
import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from automation.post_generator import PostGenerator
from storage.post_storage import PostStorage
from utils.email_notifier import EmailNotifier

app = FastAPI(title="Threads Automation API")

# Initialize components
post_generator = PostGenerator()
post_storage = PostStorage()
email_notifier = EmailNotifier()

# Request models
class GenerateBriefsRequest(BaseModel):
    limit: int = 5
    status_filter: Optional[str] = None

class GenerateAnalysisRequest(BaseModel):
    limit: int = 25
    topic: Optional[str] = None

class GenerateConnectionRequest(BaseModel):
    connection_type: Optional[str] = None

# Response model
class PostResponse(BaseModel):
    id: str
    post_text: str
    mode: str
    status: str
    created_at: str
    approval_url: str
    metadata: dict

@app.post("/api/generate/briefs", response_model=PostResponse)
async def generate_briefs(request: GenerateBriefsRequest):
    """
    Generate posts from Notion briefs (Path A)
    """
    try:
        # Fetch briefs
        briefs = post_generator.fetch_briefs(
            status_filter=request.status_filter,
            limit=request.limit
        )
        
        if not briefs:
            raise HTTPException(status_code=404, detail="No briefs found")
        
        # Generate post for first brief (for simplicity, can extend to multiple)
        result = post_generator.generate_post_for_brief(briefs[0])
        
        if not result.get("valid"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        # Store in database
        stored_post = post_storage.create_post(
            post_text=result["generated_post"],
            mode="briefs",
            metadata={
                "brief": result.get("brief", {}),
                "attempts": result.get("attempts", 1)
            }
        )
        
        # Send notification email
        recipient = os.getenv("NOTIFICATION_EMAIL", post_generator.threads_api.get_user_info().get("username", "") + "@gmail.com")
        email_notifier.send_notification(
            recipient=recipient,
            post_id=stored_post["id"],
            post_text=result["generated_post"],
            mode="briefs"
        )
        
        app_base_url = os.getenv("APP_BASE_URL", "https://your-app.vercel.app")
        
        return PostResponse(
            id=stored_post["id"],
            post_text=stored_post["post_text"],
            mode=stored_post["mode"],
            status=stored_post["status"],
            created_at=stored_post["created_at"],
            approval_url=f"{app_base_url}/approve/{stored_post['id']}",
            metadata=stored_post.get("metadata", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/analysis", response_model=PostResponse)
async def generate_analysis(request: GenerateAnalysisRequest):
    """
    Generate post from style analysis (Path B)
    """
    try:
        result = post_generator.generate_post_from_analysis(
            topic=request.topic,
            limit=request.limit
        )
        
        if not result.get("valid"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        # Store in database
        stored_post = post_storage.create_post(
            post_text=result["generated_post"],
            mode="analysis",
            metadata={
                "analysis": result.get("analysis", {}),
                "topic": request.topic,
                "attempts": result.get("attempts", 1)
            }
        )
        
        # Send notification
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            email_notifier.send_notification(
                recipient=recipient,
                post_id=stored_post["id"],
                post_text=result["generated_post"],
                mode="analysis"
            )
        
        app_base_url = os.getenv("APP_BASE_URL", "https://your-app.vercel.app")
        
        return PostResponse(
            id=stored_post["id"],
            post_text=stored_post["post_text"],
            mode=stored_post["mode"],
            status=stored_post["status"],
            created_at=stored_post["created_at"],
            approval_url=f"{app_base_url}/approve/{stored_post['id']}",
            metadata=stored_post.get("metadata", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/connection", response_model=PostResponse)
async def generate_connection(request: GenerateConnectionRequest):
    """
    Generate connection post (Path C)
    """
    try:
        result = post_generator.generate_connection_post(
            connection_type=request.connection_type
        )
        
        if not result.get("valid"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        # Store in database
        stored_post = post_storage.create_post(
            post_text=result["generated_post"],
            mode="connection",
            metadata={
                "connection_type": request.connection_type,
                "attempts": result.get("attempts", 1)
            }
        )
        
        # Send notification
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            email_notifier.send_notification(
                recipient=recipient,
                post_id=stored_post["id"],
                post_text=result["generated_post"],
                mode="connection"
            )
        
        app_base_url = os.getenv("APP_BASE_URL", "https://your-app.vercel.app")
        
        return PostResponse(
            id=stored_post["id"],
            post_text=stored_post["post_text"],
            mode=stored_post["mode"],
            status=stored_post["status"],
            created_at=stored_post["created_at"],
            approval_url=f"{app_base_url}/approve/{stored_post['id']}",
            metadata=stored_post.get("metadata", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel serverless handler
handler = Mangum(app)

