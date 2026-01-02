"""
Test script to test publishing a post to Threads
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Get project root
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Load environment variables
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add to path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from storage.post_storage import PostStorage
from automation.post_generator import PostGenerator

def test_publish():
    """Test publishing a post"""
    storage = PostStorage()
    generator = PostGenerator()
    
    # Get approved posts
    approved_posts = storage.get_approved_posts()
    
    if not approved_posts:
        print("❌ No approved posts found. Please approve a post first.")
        return
    
    # Use the first approved post
    post = approved_posts[0]
    print(f"📋 Testing publish for post: {post['id']}")
    print(f"📝 Post text: {post['post_text'][:100]}...")
    print(f"📊 Status: {post['status']}")
    print()
    
    # Create result dict
    result = {
        "valid": True,
        "generated_post": post["post_text"],
        "brief": post.get("metadata", {}).get("brief"),
        "analysis": post.get("metadata", {}).get("analysis"),
        "type": post.get("mode")
    }
    
    # Try to post
    print("📤 Attempting to post to Threads...")
    print("-" * 60)
    
    try:
        post_result = generator.post_approved_post(result)
        
        print("-" * 60)
        
        if post_result.get("success"):
            print(f"✅ Success! Post published to Threads")
            print(f"🆔 Thread ID: {post_result.get('thread_id')}")
            print(f"🔗 Thread URL: {post_result.get('thread_url')}")
        else:
            print(f"❌ Failed to publish")
            print(f"📋 Error: {post_result.get('error')}")
            if post_result.get('api_response'):
                print(f"📋 API Response: {post_result.get('api_response')}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_publish()

