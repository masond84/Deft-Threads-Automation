"""
API endpoints for post approval and publishing
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from storage.post_storage import PostStorage
from automation.post_generator import PostGenerator
from utils.email_notifier import EmailNotifier

app = FastAPI(title="Threads Automation API - Approval")

post_storage = PostStorage()
post_generator = PostGenerator()
email_notifier = EmailNotifier()

class ApprovalResponse(BaseModel):
    success: bool
    message: str
    post_id: str
    status: str

class PublishResponse(BaseModel):
    success: bool
    message: str
    post_id: str
    thread_id: Optional[str] = None
    thread_url: Optional[str] = None

@app.post("/api/posts/{post_id}/approve", response_model=ApprovalResponse)
async def approve_post(post_id: str):
    """
    Approve a pending post
    """
    try:
        post = post_storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Post is already {post['status']}")
        
        updated = post_storage.update_status(post_id, "approved")
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update post status")
        
        return ApprovalResponse(
            success=True,
            message="Post approved successfully",
            post_id=post_id,
            status="approved"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/{post_id}/reject", response_model=ApprovalResponse)
async def reject_post(post_id: str):
    """
    Reject a pending post
    """
    try:
        post = post_storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Post is already {post['status']}")
        
        updated = post_storage.update_status(post_id, "rejected")
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update post status")
        
        return ApprovalResponse(
            success=True,
            message="Post rejected",
            post_id=post_id,
            status="rejected"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/posts/{post_id}/publish", response_model=PublishResponse)
async def publish_post(post_id: str):
    """
    Publish an approved post to Threads
    """
    try:
        post = post_storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["status"] != "approved":
            raise HTTPException(status_code=400, detail=f"Post must be approved to publish. Current status: {post['status']}")
        
        # Create result dict for posting
        result = {
            "valid": True,
            "generated_post": post["post_text"],
            "brief": post.get("metadata", {}).get("brief"),
            "analysis": post.get("metadata", {}).get("analysis"),
            "type": post.get("mode")
        }
        
        # Post to Threads
        post_result = post_generator.post_approved_post(result)
        
        if not post_result.get("success"):
            raise HTTPException(status_code=500, detail=post_result.get("error", "Failed to post to Threads"))
        
        # Update status in database
        thread_id = post_result.get("thread_id")
        thread_url = post_result.get("thread_url")
        
        updated = post_storage.update_status(
            post_id,
            "published",
            thread_id=thread_id,
            thread_url=thread_url
        )
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update post status")
        
        # Send confirmation email
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            email_notifier.send_confirmation(
                recipient=recipient,
                post_text=post["post_text"],
                thread_url=thread_url
            )
        
        return PublishResponse(
            success=True,
            message="Post published successfully",
            post_id=post_id,
            thread_id=thread_id,
            thread_url=thread_url
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel serverless handler
handler = Mangum(app)




