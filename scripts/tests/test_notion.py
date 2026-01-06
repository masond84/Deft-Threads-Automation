import sys
from pathlib import Path
import json

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from database.notion_client import NotionClient  # type: ignore

def main():
    try:
        client = NotionClient()
        print("✅ Connected to Notion!\n")
        
        # DEBUG: First, get ALL rows without filter to see what we have
        print("🔍 DEBUG: Fetching ALL rows (no filter)...")
        all_results = client.query_database()
        print(f"Found {len(all_results)} total rows in database\n")
        
        if len(all_results) == 0:
            print("❌ No rows found in database. Check:")
            print("  1. Database ID is correct")
            print("  2. Database is shared with your integration")
            return
        
        # Show first row's structure to understand field names
        print("📋 First row structure (to see field names):")
        if all_results:
            first_row = all_results[0]
            properties = first_row.get("properties", {})
            print("\nAvailable fields:")
            for field_name, field_data in properties.items():
                field_type = field_data.get("type", "unknown")
                print(f"  - {field_name} (type: {field_type})")
                
                # Show sample value
                if field_type == "title":
                    title_array = field_data.get("title", [])
                    if title_array:
                        print(f"    Value: {title_array[0].get('plain_text', '')}")
                elif field_type == "select":
                    select_obj = field_data.get("select")
                    if select_obj:
                        print(f"    Value: {select_obj.get('name', '')}")
                elif field_type == "multi_select":
                    multi_array = field_data.get("multi_select", [])
                    values = [item.get("name", "") for item in multi_array]
                    print(f"    Values: {', '.join(values) if values else 'None'}")
            
            print("\n" + "="*50)
            print("Sample extracted data from first row:")
            sample_brief = client.extract_brief_data(first_row)
            print(json.dumps(sample_brief, indent=2))
            print("="*50 + "\n")
        
        # Now try with filter
        print("📋 Fetching briefs for Threads (with filter)...")
        briefs = client.get_briefs_for_threads()
        print(f"Found {len(briefs)} briefs with Threads filter\n")
        
        # Show all platforms found in database
        print("🔍 All unique platforms found in database:")
        all_platforms = set()
        for row in all_results:
            brief_data = client.extract_brief_data(row)
            if brief_data:
                platforms = brief_data.get("platforms", [])
                all_platforms.update(platforms)
        print(f"  {', '.join(sorted(all_platforms)) if all_platforms else 'None found'}\n")
        
        # Display first few briefs
        if briefs:
            print("✅ Briefs found:")
            for i, brief in enumerate(briefs[:5], 1):
                print(f"\nBrief {i}:")
                print(f"  Topic: {brief.get('topic')}")
                print(f"  Pillar: {brief.get('pillar')}")
                print(f"  Platforms: {', '.join(brief.get('platforms', []))}")
                print(f"  Post Type: {brief.get('post_type')}")
                print(f"  Status: {brief.get('status', 'N/A')}")
            
            if len(briefs) > 5:
                print(f"\n... and {len(briefs) - 5} more briefs")
        else:
            print("⚠️  No briefs found with 'Threads' in Platform field.")
            print("   Check if your Platform field contains 'Threads' exactly.")
            print("   Or the field name might be different.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()