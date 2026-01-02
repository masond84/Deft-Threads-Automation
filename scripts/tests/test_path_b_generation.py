"""
Test script for Path B: Post generation using style analysis
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from automation.post_generator import PostGenerator  # type: ignore


def main():
    try:
        generator = PostGenerator()
        
        # Test Path B: Generate post from style analysis
        print("="*70)
        print("PATH B: STYLE-BASED POST GENERATION")
        print("="*70)
        print()
        
        # Option 1: Generate without a specific topic
        print("Test 1: Generate post without specific topic")
        print("-" * 70)
        result = generator.generate_post_from_analysis(topic=None, limit=25)
        
        if result.get("valid"):
            print(f"\n✅ Generated post ({len(result['generated_post'])} chars):")
            print("-" * 70)
            print(result['generated_post'])
            print("-" * 70)
        else:
            print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*70)
        
        # Option 2: Generate with a specific topic
        print("\nTest 2: Generate post with specific topic")
        print("-" * 70)
        result2 = generator.generate_post_from_analysis(
            topic="AI automation tools for small businesses",
            limit=25
        )
        
        if result2.get("valid"):
            print(f"\n✅ Generated post ({len(result2['generated_post'])} chars):")
            print("-" * 70)
            print(result2['generated_post'])
            print("-" * 70)
        else:
            print(f"\n❌ Failed: {result2.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()





