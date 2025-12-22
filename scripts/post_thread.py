import sys
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# noinspection PyUnresolvedReferences
from api.threads_api import ThreadsAPI # type: ignore

def main():
    try:
        api = ThreadsAPI()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease make sure you have:")
        print("1. Created a .env file")
        print("2. Added your THREADS_ACCESS_TOKEN to the .env file")
        return
    
    # Show which profile is connected
    print("🔍 Checking connected profile...")
    user_info = api.get_user_info()
    if user_info:
        username = user_info.get('username', 'N/A')
        user_id = user_info.get('id', 'N/A')
        print(f"✅ Connected to profile: @{username} (ID: {user_id})")
        print()
    
    # Get text from command line or prompt
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter your thread text: ")
    
    if not text.strip():
        print("❌ Error: Thread text cannot be empty")
        return
    
    # Post the thread
    result = api.post_thread(text)
    
    if result:
        print(f"\n🎉 Your thread has been posted successfully!")
        thread_id = result.get('thread_id') or result.get('id')
        if thread_id:
            print(f"View it at: https://www.threads.net/t/{thread_id}/")
            if user_info and user_info.get('username'):
                print(f"Or on your profile: https://www.threads.net/@{user_info.get('username')}")
        else:
            print(f"Thread ID: {result}")

if __name__ == "__main__":
    main()