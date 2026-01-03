"""
Main API entry point for Vercel serverless functions
"""
import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from mangum import Mangum

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Don't import these at module level - import them lazily
# from automation.post_generator import PostGenerator
# from storage.post_storage import PostStorage
# from utils.email_notifier import EmailNotifier

app = FastAPI(title="Threads Automation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (lazy loading to avoid errors if env vars missing)
post_generator = None
post_storage = None
email_notifier = None

# Mount static files for CSS
web_dir = project_root / "web"
static_dir = web_dir / "static"

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve web UI pages
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main web UI page"""
    index_path = web_dir / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/posts", response_class=HTMLResponse)
async def serve_posts():
    """Serve the pending posts page"""
    posts_path = web_dir / "posts.html"
    if posts_path.exists():
        with open(posts_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="posts.html not found")

@app.get("/approve/{post_id}", response_class=HTMLResponse)
async def serve_approve(post_id: str):
    """Serve the approval page"""
    approve_path = web_dir / "approve.html"
    if approve_path.exists():
        with open(approve_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="approve.html not found")
    
def get_generator():
    global post_generator
    if post_generator is None:
        from automation.post_generator import PostGenerator
        post_generator = PostGenerator()
    return post_generator

def get_storage():
    global post_storage
    if post_storage is None:
        from storage.post_storage import PostStorage
        post_storage = PostStorage()
    return post_storage

def get_email():
    global email_notifier
    if email_notifier is None:
        from utils.email_notifier import EmailNotifier
        email_notifier = EmailNotifier()
    return email_notifier

# Request models
class GenerateBriefsRequest(BaseModel):
    limit: int = 5
    status_filter: Optional[str] = None

class GenerateAnalysisRequest(BaseModel):
    limit: int = 25
    topic: Optional[str] = None

class GenerateConnectionRequest(BaseModel):
    connection_type: Optional[str] = None

class UpdatePostTextRequest(BaseModel):
    post_text: str

# Response models
class PostResponse(BaseModel):
    id: str
    post_text: str
    mode: str
    status: str
    created_at: str
    approval_url: str
    metadata: dict

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

# Generation endpoints
@app.post("/api/generate/briefs", response_model=PostResponse)
async def generate_briefs(request: GenerateBriefsRequest):
    """Generate posts from Notion briefs (Path A)"""
    try:
        generator = get_generator()
        storage = get_storage()
        email = get_email()
        
        briefs = generator.fetch_briefs(
            status_filter=request.status_filter,
            limit=request.limit
        )
        
        if not briefs:
            raise HTTPException(status_code=404, detail="No briefs found")
        
        result = generator.generate_post_for_brief(briefs[0])
        
        if not result.get("valid"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        stored_post = storage.create_post(
            post_text=result["generated_post"],
            mode="briefs",
            metadata={
                "brief": result.get("brief", {}),
                "attempts": result.get("attempts", 1)
            }
        )
        
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            email.send_notification(
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/analysis", response_model=PostResponse)
async def generate_analysis(request: GenerateAnalysisRequest):
    """Generate post from style analysis (Path B)"""
    try:
        generator = get_generator()
        storage = get_storage()
        email = get_email()
        
        result = generator.generate_post_from_analysis(
            topic=request.topic,
            limit=request.limit
        )
        
        if not result.get("valid"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        stored_post = storage.create_post(
            post_text=result["generated_post"],
            mode="analysis",
            metadata={
                "analysis": result.get("analysis", {}),
                "topic": request.topic,
                "attempts": result.get("attempts", 1)
            }
        )
        
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            email.send_notification(
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/connection", response_model=PostResponse)
async def generate_connection(request: GenerateConnectionRequest):
    """Generate connection post (Path C)"""
    try:
        generator = get_generator()
        storage = get_storage()
        email = get_email()
        
        result = generator.generate_connection_post(
            connection_type=request.connection_type
        )
        
        if not result.get("valid"):
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        stored_post = storage.create_post(
            post_text=result["generated_post"],
            mode="connection",
            metadata={
                "connection_type": request.connection_type,
                "attempts": result.get("attempts", 1)
            }
        )
        
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            email.send_notification(
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Post management endpoints
@app.get("/api/posts/pending", response_model=PendingPostsResponse)
async def get_pending_posts():
    """Get all pending posts (and approved posts that haven't been published yet)"""
    try:
        storage = get_storage()
        # Get both pending and approved posts
        pending = storage.get_pending_posts()
        approved = storage.get_approved_posts()
        all_posts = pending + approved
        return PendingPostsResponse(posts=all_posts, count=len(all_posts))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts/{post_id}", response_model=PostDetailResponse)
async def get_post(post_id: str):
    """Get a specific post by ID"""
    try:
        storage = get_storage()
        post = storage.get_post(post_id)
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

@app.put("/api/posts/{post_id}/text", response_model=PostDetailResponse)
async def update_post_text(post_id: str, request: UpdatePostTextRequest):
    """Update the text content of a post"""
    try:
        storage = get_storage()
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Don't allow editing published posts
        if post["status"] == "published":
            raise HTTPException(status_code=400, detail="Cannot edit a published post")
        
        updated = storage.update_post_text(post_id, request.post_text)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update post text")
        
        return PostDetailResponse(
            id=updated["id"],
            post_text=updated["post_text"],
            mode=updated["mode"],
            status=updated["status"],
            created_at=updated["created_at"],
            approved_at=updated.get("approved_at"),
            published_at=updated.get("published_at"),
            thread_id=updated.get("thread_id"),
            thread_url=updated.get("thread_url"),
            metadata=updated.get("metadata", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Approval endpoints
@app.post("/api/posts/{post_id}/approve", response_model=ApprovalResponse)
async def approve_post(post_id: str):
    """Approve a pending post (or re-approve an approved post)"""
    try:
        storage = get_storage()
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["status"] == "published":
            raise HTTPException(status_code=400, detail="Post is already published")
        
        if post["status"] == "rejected":
            raise HTTPException(status_code=400, detail="Cannot approve a rejected post")
        
        # Allow approving pending posts or re-approving approved posts
        updated = storage.update_status(post_id, "approved")
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
    """Reject a pending post"""
    try:
        storage = get_storage()
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Post is already {post['status']}")
        
        updated = storage.update_status(post_id, "rejected")
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
    """Publish an approved post to Threads"""
    try:
        storage = get_storage()
        generator = get_generator()
        email = get_email()
        
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post["status"] not in ["approved", "pending"]:
            raise HTTPException(status_code=400, detail=f"Post must be approved or pending to publish. Current status: {post['status']}")
        
        result = {
            "valid": True,
            "generated_post": post["post_text"],
            "brief": post.get("metadata", {}).get("brief"),
            "analysis": post.get("metadata", {}).get("analysis"),
            "type": post.get("mode")
        }
        
        try:
            post_result = generator.post_approved_post(result)
        except Exception as e:
            # If posting fails, keep post as approved but return error
            error_msg = str(e) if str(e) else "Unknown error occurred while posting to Threads"
            raise HTTPException(status_code=500, detail=f"Failed to post to Threads: {error_msg}")
        
        if not post_result or not post_result.get("success"):
            error_msg = post_result.get("error", "Unknown error") if post_result else "No response from Threads API"
            raise HTTPException(status_code=500, detail=f"Failed to post to Threads: {error_msg}")
        
        thread_id = post_result.get("thread_id")
        thread_url = post_result.get("thread_url")
        
        updated = storage.update_status(
            post_id,
            "published",
            thread_id=thread_id,
            thread_url=thread_url
        )
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update post status")
        
        recipient = os.getenv("NOTIFICATION_EMAIL", "")
        if recipient:
            try:
                email.send_confirmation(
                    recipient=recipient,
                    post_text=post["post_text"],
                    thread_url=thread_url
                )
            except Exception as e:
                # Don't fail the whole request if email fails
                print(f"Warning: Failed to send confirmation email: {e}")
        
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
        error_msg = str(e) if str(e) else "Unknown error occurred"
        raise HTTPException(status_code=500, detail=f"Error publishing post: {error_msg}")

# Vercel serverless handler
# Handler is now exported from api/handler.py for Vercel compatibility
# handler = Mangum(app)

