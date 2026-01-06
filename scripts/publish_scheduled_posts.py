"""
Background job to publish scheduled posts
Run this as a cron job every minute or use a scheduler like Vercel Cron
"""
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Load environment variables
env_path = project_root / ".env"
load_dotenv(env_path)

from storage.post_storage import PostStorage
from automation.post_generator import PostGenerator

def publish_scheduled_posts():
    """Check for and publish scheduled posts"""
    try:
        storage = PostStorage()
        generator = PostGenerator()
        
        # Get posts scheduled for now or earlier
        scheduled_posts = storage.get_scheduled_posts()
        
        if not scheduled_posts:
            print("No scheduled posts to publish")
            return
        
        print(f"Found {len(scheduled_posts)} scheduled post(s) to check")
        
        for post in scheduled_posts:
            # Parse scheduled_at (handle both with and without timezone)
            scheduled_at_str = post['scheduled_at']
            if scheduled_at_str.endswith('Z'):
                scheduled_at_str = scheduled_at_str.replace('Z', '+00:00')
            elif '+' not in scheduled_at_str and scheduled_at_str.count(':') > 1:
                # Assume UTC if no timezone specified
                scheduled_at_str = scheduled_at_str + '+00:00'
            
            scheduled_time = datetime.fromisoformat(scheduled_at_str)
            # Make current_time timezone-aware for comparison
            from datetime import timezone
            current_time = datetime.now(timezone.utc)
            
            # Convert scheduled_time to UTC if it's not already
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            else:
                scheduled_time = scheduled_time.astimezone(timezone.utc)
            
            # If scheduled time has passed, publish it
            if scheduled_time <= current_time:
                try:
                    print(f"Publishing scheduled post {post['id']} (scheduled for {post['scheduled_at']})")
                    
                    result = {
                        "valid": True,
                        "generated_post": post["post_text"],
                        "brief": post.get("metadata", {}).get("brief"),
                        "analysis": post.get("metadata", {}).get("analysis"),
                        "type": post.get("mode")
                    }
                    
                    post_result = generator.post_approved_post(result)
                    
                    if post_result and post_result.get("success"):
                        storage.update_status(
                            post["id"],
                            "published",
                            thread_id=post_result.get("thread_id"),
                            thread_url=post_result.get("thread_url")
                        )
                        print(f"✅ Published scheduled post {post['id']}")
                    else:
                        error_msg = post_result.get("error", "Unknown error") if post_result else "No response"
                        print(f"❌ Failed to publish scheduled post {post['id']}: {error_msg}")
                except Exception as e:
                    print(f"❌ Error publishing scheduled post {post['id']}: {e}")
            else:
                print(f"Post {post['id']} scheduled for {post['scheduled_at']} - not yet time to publish")
    except Exception as e:
        print(f"❌ Error in publish_scheduled_posts: {e}")
        raise

if __name__ == "__main__":
    publish_scheduled_posts()

