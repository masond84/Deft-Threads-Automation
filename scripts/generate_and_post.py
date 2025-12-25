import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from automation.post_generator import PostGenerator  # type: ignore

def display_preview(results: list):
    """
    Display generated posts for review
    """
    print("\n" + "="*70)
    print("📋 GENERATED POSTS PREVIEW")
    print("="*70 + "\n")
    
    valid_posts = [r for r in results if r["valid"]]
    invalid_posts = [r for r in results if not r["valid"]]
    
    for i, result in enumerate(valid_posts, 1):
        brief = result["brief"]
        post = result["generated_post"]
        
        print(f"\n{'─'*70}")
        print(f"Post #{i}")
        print(f"{'─'*70}")
        print(f"📌 Topic: {brief.get('topic', 'N/A')}")
        print(f"📂 Pillar: {brief.get('pillar', 'N/A')}")
        print(f"📱 Post Type: {', '.join(brief.get('post_type', []))}")
        print(f"📊 Status: {brief.get('status', 'N/A')}")
        print(f"\n💬 Generated Post ({len(post)} chars):")
        print(f"\n{post}\n")
        print(f"{'─'*70}\n")
    
    if invalid_posts:
        print(f"\n⚠️  {len(invalid_posts)} posts failed to generate:\n")
        for result in invalid_posts:
            print(f"  ❌ {result['brief'].get('topic', 'Unknown')}: {result.get('error', 'Unknown error')}")
    
    print(f"\n✅ Summary: {len(valid_posts)} posts generated, {len(invalid_posts)} failed")
    print("\n" + "="*70)
    
    return valid_posts

def get_approval(valid_posts: list) -> list:
    """
    Get user approval for posts
    
    Args:
        valid_posts: List of valid post results
        
    Returns:
        List of approved posts to post
    """
    if not valid_posts:
        return []
    
    print("\n" + "="*70)
    print("📝 POST APPROVAL")
    print("="*70 + "\n")
    print("Review the posts above and approve which ones to post.\n")
    
    approved = []
    
    for i, result in enumerate(valid_posts, 1):
        brief = result["brief"]
        post = result["generated_post"]
        
        print(f"\nPost #{i}: {brief.get('topic', 'Unknown')}")
        print(f"Preview: {post[:100]}...")
        
        while True:
            response = input(f"\nApprove Post #{i}? (y/n/skip): ").strip().lower()
            
            if response in ['y', 'yes']:
                approved.append(result)
                print("✅ Approved")
                break
            elif response in ['n', 'no']:
                print("❌ Rejected")
                break
            elif response in ['s', 'skip']:
                print("⏭️  Skipped")
                break
            else:
                print("Please enter 'y' (yes), 'n' (no), or 's' (skip)")
    
    return approved

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Threads posts from Notion briefs")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of briefs to process (default: 5)"
    )
    parser.add_argument(
        "--status",
        type=str,
        default=None,
        help="Filter briefs by status (e.g., 'Ready')"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve all generated posts (use with caution!)"
    )
    parser.add_argument(
        "--post-delay",
        type=int,
        default=60,
        help="Delay between posts in seconds (default: 60)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = PostGenerator()
        
        # Step 1: Fetch briefs
        print("📥 Fetching briefs from Notion...")
        briefs = generator.fetch_briefs(
            status_filter=args.status,
            limit=args.limit
        )
        
        if not briefs:
            print("❌ No briefs found matching criteria")
            return
        
        print(f"✅ Found {len(briefs)} brief(s)\n")
        
        # Step 2: Generate posts
        print("🤖 Generating posts...")
        results = generator.generate_posts_for_briefs(briefs)
        
        # Step 3: Show preview
        valid_posts = display_preview(results)
        
        if not valid_posts:
            print("\n❌ No valid posts to approve")
            return
        
        # Step 4: Get approval
        if args.auto_approve:
            print("\n⚠️  AUTO-APPROVE MODE: All posts will be posted automatically")
            approved = valid_posts
        else:
            approved = get_approval(valid_posts)
        
        if not approved:
            print("\n⏭️  No posts approved. Exiting.")
            return
        
        # Step 5: Confirm before posting
        print(f"\n📤 Ready to post {len(approved)} approved post(s)")
        if not args.auto_approve:
            confirm = input("Proceed with posting? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("❌ Posting cancelled")
                return
        
        # Step 6: Post approved content
        print("\n🚀 Posting to Threads...")
        posting_results = generator.post_multiple_approved(
            approved,
            delay_seconds=args.post_delay
        )
        
        # Step 7: Summary
        successful = [r for r in posting_results if r.get("success")]
        failed = [r for r in posting_results if not r.get("success")]
        
        print("\n" + "="*70)
        print("📊 POSTING SUMMARY")
        print("="*70)
        print(f"✅ Successfully posted: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        if successful:
            print("\n✅ Posted Threads:")
            for result in successful:
                brief = result["result"]["brief"]
                thread_url = result.get("thread_url", "N/A")
                print(f"  • {brief.get('topic', 'Unknown')}: {thread_url}")
        
        if failed:
            print("\n❌ Failed Posts:")
            for result in failed:
                brief = result["result"]["brief"]
                error = result.get("error", "Unknown error")
                print(f"  • {brief.get('topic', 'Unknown')}: {error}")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()