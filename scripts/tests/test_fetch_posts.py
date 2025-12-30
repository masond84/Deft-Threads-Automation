"""
Test script to verify post fetching from Threads API
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from api.threads_api import ThreadsAPI  # type: ignore

def main():
    try:
        api = ThreadsAPI()
        
        # Show which profile is connected
        print("🔍 Checking connected profile...")
        user_info = api.get_user_info()
        if user_info:
            username = user_info.get('username', 'N/A')
            user_id = user_info.get('id', 'N/A')
            print(f"✅ Connected to profile: @{username} (ID: {user_id})\n")
        
        # Test fetching posts
        print("📥 Fetching posts from Threads...")
        posts = api.get_user_threads(limit=10)
        
        if posts:
            print(f"\n✅ Successfully fetched {len(posts)} posts\n")
            print("="*70)
            print("SAMPLE POSTS:")
            print("="*70)
            
            for i, post in enumerate(posts[:3], 1):  # Show first 3
                text = post.get('text', 'N/A')
                post_id = post.get('id', 'N/A')
                print(f"\nPost #{i} (ID: {post_id}):")
                print(f"{text[:200]}..." if len(text) > 200 else text)
                print("-" * 70)
        else:
            print("\n❌ No posts fetched. Check:")
            print("  1. Do you have posts on your Threads account?")
            print("  2. Does your access token have 'threads_basic' permission?")
            print("  3. Is the API endpoint correct?")
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease make sure you have:")
        print("1. Created a .env file")
        print("2. Added your THREADS_ACCESS_TOKEN to the .env file")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()