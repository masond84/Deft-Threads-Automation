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
        display_preview(results)
        
        # Note: Posting and Notion updates will be added in next step
        print("\n💡 Next: Review posts above, then approve for posting")
        print("   (Posting functionality coming next)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()