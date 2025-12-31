import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from automation.post_generator import PostGenerator  # type: ignore

# Update the display_preview function to handle both modes
def display_preview(results: list, mode: str = "briefs"):
    """
    Display generated posts for review
    
    Args:
        results: List of result dictionaries
        mode: Generation mode ("briefs" or "analysis")
    """
    print("\n" + "="*70)
    print("📋 GENERATED POSTS PREVIEW")
    print("="*70 + "\n")
    
    valid_posts = [r for r in results if r["valid"]]
    invalid_posts = [r for r in results if not r["valid"]]
    
    for i, result in enumerate(valid_posts, 1):
        post = result["generated_post"]
        
        print(f"\n{'─'*70}")
        print(f"Post #{i}")
        print(f"{'─'*70}")
        
        if mode == "briefs":
            brief = result.get("brief", {})
            print(f"📌 Topic: {brief.get('topic', 'N/A')}")
            print(f"📂 Pillar: {brief.get('pillar', 'N/A')}")
            print(f"📱 Post Type: {', '.join(brief.get('post_type', []))}")
            print(f"📊 Status: {brief.get('status', 'N/A')}")
        elif mode == "connection":
            print(f"🤝 Connection Post")
            if result.get("connection_type"):
                print(f"📌 Connection Type: {result.get('connection_type', 'General')}")
        else:  # mode == "analysis"
            analysis = result.get("analysis", {})
            print(f"📊 Analysis: {analysis.get('total_posts', 0)} posts analyzed")
            print(f"📏 Avg Length: {analysis.get('avg_length', 0):.0f} chars")
        
        print(f"\n💬 Generated Post ({len(post)} chars):")
        print(f"\n{post}\n")
        print(f"{'─'*70}\n")
    
    if invalid_posts:
        print(f"\n⚠️  {len(invalid_posts)} posts failed to generate:\n")
        for result in invalid_posts:
            if mode == "briefs":
                topic = result.get('brief', {}).get('topic', 'Unknown')
            elif mode == "connection":
                topic = "Connection post"
            else:  # mode == "analysis"
                topic = "Analysis-based post"
            print(f"  ❌ {topic}: {result.get('error', 'Unknown error')}")
    
    print(f"\n✅ Summary: {len(valid_posts)} posts generated, {len(invalid_posts)} failed")
    print("\n" + "="*70)
    
    return valid_posts

# Update get_approval function
def get_approval(valid_posts: list, mode: str = "briefs") -> list:
    """
    Get user approval for posts
    
    Args:
        valid_posts: List of valid post results
        mode: Generation mode ("briefs" or "analysis")
        
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
        post = result["generated_post"]
        
        if mode == "briefs":
            topic = result.get("brief", {}).get('topic', 'Unknown')
        elif mode == "connection":
            topic = "Connection post"
        else:  # mode == "analysis"
            topic = "Analysis-based post"
        
        print(f"\nPost #{i}: {topic}")
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

# Update main() function - add mode argument and Path B logic
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Threads posts from Notion briefs or post analysis"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["briefs", "analysis", "connection"],
        default="briefs",
        help="Generation mode: 'briefs' (from Notion), 'analysis' (from past posts), or 'connection' (short networking posts) (default: briefs)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of briefs to process (Path A) or posts to analyze (Path B) (default: 5)"
    )
    parser.add_argument(
        "--status",
        type=str,
        default=None,
        help="Filter briefs by status (Path A only, e.g., 'Ready')"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Optional topic for analysis mode (Path B only)"
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
    parser.add_argument(
        "--connection-type",
        type=str,
        default=None,
        help="Type of people to connect with for connection mode (Path C only, e.g., 'founders', 'developers', 'SMBs')"
    )
    
    args = parser.parse_args()
    
    try:
        generator = PostGenerator()
        
        # Path A: Notion Briefs (default)
        if args.mode == "briefs":
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
            valid_posts = display_preview(results, mode="briefs")
        
        # Path C: Connection Posts
        elif args.mode == "connection":
            # Step 1: Generate connection post
            print(f"🤝 Generating connection post...")
            result = generator.generate_connection_post(
                connection_type=args.connection_type
            )
            
            if not result.get("valid"):
                print(f"❌ Failed to generate post: {result.get('error', 'Unknown error')}")
                return
            
            results = [result]
            valid_posts = display_preview(results, mode="connection")

        # Path B: Post Analysis
        elif args.mode == "analysis":  # args.mode == "analysis"
            # Step 1: Generate post from analysis
            print(f"📊 Generating post from style analysis...")
            result = generator.generate_post_from_analysis(
                topic=args.topic,
                limit=args.limit
            )
            
            if not result.get("valid"):
                print(f"❌ Failed to generate post: {result.get('error', 'Unknown error')}")
                return
            
            results = [result]
            valid_posts = display_preview(results, mode="analysis")
        
        if not valid_posts:
            print("\n❌ No valid posts to approve")
            return
        
        # Step 4: Get approval
        if args.auto_approve:
            print("\n⚠️  AUTO-APPROVE MODE: All posts will be posted automatically")
            approved = valid_posts
        else:
            approved = get_approval(valid_posts, mode=args.mode)
        
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
                thread_url = result.get("thread_url", "N/A")
                if args.mode == "briefs":
                    topic = result["result"].get("brief", {}).get('topic', 'Unknown')
                elif args.mode == "connection":
                    topic = "Connection post"
                else:  # args.mode == "analysis"
                    topic = "Analysis-based post"
                print(f"  • {topic}: {thread_url}")
        
        if failed:
            print("\n❌ Failed Posts:")
            for result in failed:
                error = result.get("error", "Unknown error")
                if args.mode == "briefs":
                    topic = result["result"].get("brief", {}).get('topic', 'Unknown')
                elif args.mode == "connection":
                    topic = "Connection post"
                else:  # args.mode == "analysis"
                    topic = "Analysis-based post"
                print(f"  • {topic}: {error}")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()