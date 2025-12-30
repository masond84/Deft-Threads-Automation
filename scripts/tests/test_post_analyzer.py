"""
Test script to verify post analysis functionality
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent  
sys.path.insert(0, str(project_root / "src"))

from api.threads_api import ThreadsAPI  # type: ignore
from utils.post_analyzer import PostAnalyzer  # type: ignore


def main():
    try:
        api = ThreadsAPI()
        analyzer = PostAnalyzer()
        
        # Fetch posts
        print("📥 Fetching posts from Threads...")
        posts = api.get_user_threads(limit=25)
        
        if not posts:
            print("❌ No posts found")
            return
        
        print(f"✅ Fetched {len(posts)} posts\n")
        
        # Analyze posts
        print("📊 Analyzing posts...")
        analysis = analyzer.analyze_posts(posts)
        
        if not analysis:
            print("❌ Analysis failed")
            return
        
        # Display results
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        print(f"\nTotal posts analyzed: {analysis.get('total_posts', 0)}")
        print(f"Average length: {analysis.get('avg_length', 0):.0f} characters")
        print(f"Length range: {analysis.get('min_length', 0)} - {analysis.get('max_length', 0)} chars")
        
        print(f"\n📝 Structure Patterns:")
        struct = analysis.get('structure_patterns', {})
        for key, value in struct.items():
            if isinstance(value, float):
                print(f"  • {key}: {value*100:.0f}%")
        
        print(f"\n🎯 Tone Indicators:")
        tone = analysis.get('tone_indicators', {})
        for key, value in tone.items():
            if isinstance(value, float):
                print(f"  • {key}: {value*100:.0f}%")
        
        print(f"\n💬 Common Starters ({len(analysis.get('common_starters', []))}):")
        for starter in analysis.get('common_starters', [])[:3]:
            print(f"  • {starter[:80]}...")
        
        print(f"\n❓ Common Endings ({len(analysis.get('common_endings', []))}):")
        for ending in analysis.get('common_endings', [])[:3]:
            print(f"  • {ending[:80]}...")
        
        # Test prompt formatting
        print("\n" + "="*70)
        print("PROMPT FORMAT PREVIEW")
        print("="*70)
        prompt_section = analyzer.format_for_prompt(analysis)
        print(prompt_section[:500] + "..." if len(prompt_section) > 500 else prompt_section)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()