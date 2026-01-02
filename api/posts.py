"""
API endpoints for post management
"""
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from storage.post_storage import PostStorage

app = FastAPI(title="Threads Automation API - Posts")

post_storage = PostStorage()

class PostDetailResponse(BaseModel):
    id: str
    post_text: str
    mode: str
    status: str
    created_at: str
    approved_at: Optional[str] = None
    published_at: Optional[str] = None
    thread_id: Optional[str] = None
    thread_url: Optional[str] = None
    metadata: dict

class PendingPostsResponse(BaseModel):
    posts: list
    count: int

@app.get("/api/posts/pending", response_model=PendingPostsResponse)
async def get_pending_posts():
    """
    Get all pending posts
    """
    try:
        posts = post_storage.get_pending_posts()
        return PendingPostsResponse(posts=posts, count=len(posts))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/{post_id}", response_model=PostDetailResponse)
async def get_post(post_id: str):
    """
    Get a specific post by ID
    """
    try:
        post = post_storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return PostDetailResponse(
            id=post["id"],
            post_text=post["post_text"],
            mode=post["mode"],
            status=post["status"],
            created_at=post["created_at"],
            approved_at=post.get("approved_at"),
            published_at=post.get("published_at"),
            thread_id=post.get("thread_id"),
            thread_url=post.get("thread_url"),
            metadata=post.get("metadata", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel serverless handler
handler = Mangum(app)

