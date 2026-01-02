"""
Storage layer for managing pending posts using Supabase
"""
import os
from typing import Optional, List, Dict
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

class PostStorage:
    """
    Manages post storage in Supabase database
    """
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.table_name = "pending_posts"
    
    def create_post(
        self,
        post_text: str,
        mode: str,
        metadata: Optional[Dict] = None,
        status: str = "pending"
    ) -> Dict:
        """
        Create a new pending post
        
        Args:
            post_text: The generated post text
            mode: Generation mode ('briefs', 'analysis', 'connection')
            metadata: Additional metadata (brief, analysis, connection_type, etc.)
            status: Initial status (default: 'pending')
            
        Returns:
            Dictionary with created post data including id
        """
        data = {
            "post_text": post_text,
            "mode": mode,
            "metadata": metadata or {},
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table(self.table_name).insert(data).execute()
        
        if result.data:
            return result.data[0]
        raise Exception("Failed to create post in database")
    
    def get_post(self, post_id: str) -> Optional[Dict]:
        """
        Get a post by ID
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Post dictionary or None if not found
        """
        result = self.supabase.table(self.table_name).select("*").eq("id", post_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def get_pending_posts(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all pending posts
        
        Args:
            limit: Optional limit on number of posts to return
            
        Returns:
            List of pending post dictionaries
        """
        query = self.supabase.table(self.table_name).select("*").eq("status", "pending").order("created_at", desc=True)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data or []
    
    def update_status(
        self,
        post_id: str,
        status: str,
        thread_id: Optional[str] = None,
        thread_url: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update post status
        
        Args:
            post_id: UUID of the post
            status: New status ('pending', 'approved', 'rejected', 'published')
            thread_id: Optional Threads thread ID if published
            thread_url: Optional Threads URL if published
            
        Returns:
            Updated post dictionary or None if not found
        """
        update_data = {
            "status": status
        }
        
        if status == "approved":
            update_data["approved_at"] = datetime.utcnow().isoformat()
        elif status == "published":
            update_data["published_at"] = datetime.utcnow().isoformat()
            if thread_id:
                update_data["thread_id"] = thread_id
            if thread_url:
                update_data["thread_url"] = thread_url
        
        result = self.supabase.table(self.table_name).update(update_data).eq("id", post_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    def get_approved_posts(self) -> List[Dict]:
        """
        Get all approved but not yet published posts
        
        Returns:
            List of approved post dictionaries
        """
        result = self.supabase.table(self.table_name).select("*").eq("status", "approved").order("approved_at", desc=True).execute()
        return result.data or []
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post (for cleanup)
        
        Args:
            post_id: UUID of the post
            
        Returns:
            True if deleted, False otherwise
        """
        result = self.supabase.table(self.table_name).delete().eq("id", post_id).execute()
        return result.data is not None




