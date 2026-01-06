import os
import requests
from notion_client import Client
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Optional

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

class NotionClient:
    def __init__(self):
        api_key = os.getenv("NOTION_API_KEY")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not api_key:
            raise ValueError("NOTION_API_KEY not found in .env file")
        if not database_id:
            raise ValueError("NOTION_DATABASE_ID not found in .env file")
        
        self.client = Client(auth=api_key)
        self.database_id = database_id
    
    def get_database(self) -> Dict:
        """Get database information"""
        return self.client.databases.retrieve(database_id=self.database_id)
    
    def query_database(
        self, 
        filter_conditions: Optional[Dict] = None,
        sort_conditions: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Query the database for rows using direct API calls
        """
        import requests
        
        results = []
        has_more = True
        start_cursor = None
        
        api_key = os.getenv("NOTION_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        while has_more:
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            
            payload = {}
            
            if filter_conditions:
                payload["filter"] = filter_conditions
            
            if sort_conditions:
                payload["sorts"] = sort_conditions
            
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise error if request failed
            data = response.json()
            
            results.extend(data.get("results", []))
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
        
        return results
    
    def extract_brief_data(self, page: Dict) -> Optional[Dict]:
        """
        Extract structured data from a Notion page/row
        
        Based on your database structure:
        - Aa Topic/Keyword (title)
        - Pillar (select)
        - Platform (multi-select)
        - Post Type (select)
        - Status (optional)
        """
        properties = page.get("properties", {})
        
        # Extract Topic/Keyword (title field)
        topic_field = properties.get("Topic/Keyword", {})
        topic = ""
        if topic_field.get("type") == "title":
            title_array = topic_field.get("title", [])
            if title_array:
                topic = title_array[0].get("plain_text", "")
        
        # Extract Pillar (select field)
        pillar_field = properties.get("Pillar", {})
        pillar = None
        if pillar_field.get("type") == "select":
            pillar_obj = pillar_field.get("select")
            if pillar_obj:
                pillar = pillar_obj.get("name")
        
        # Extract Platform (multi-select field)
        platform_field = properties.get("Platform", {})
        platforms = []
        if platform_field.get("type") == "multi_select":
            platform_array = platform_field.get("multi_select", [])
            platforms = [p.get("name") for p in platform_array]
        
        # Extract Post Type (select field)
        post_type_field = properties.get("Post Type", {})
        post_types = []
        if post_type_field.get("type") == "multi_select":
            post_type_array = post_type_field.get("multi_select", [])
            post_types = [pt.get("name") for pt in post_type_array ]
        
        # Extract Status (if exists)
        status_field = properties.get("Status", {})
        status = None
        if status_field.get("type") == "select":
            status_obj = status_field.get("select")
            if status_obj:
                status = status_obj.get("name")
        
        return {
            "page_id": page.get("id"),
            "topic": topic,
            "pillar": pillar,
            "platforms": platforms,
            "post_type": post_types,
            "status": status,
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time")
        }
    
    def get_all_briefs(
        self, 
        status_filter: Optional[str] = None,
        post_type_filter: Optional[List[str]] = None,
        platform_filter: Optional[str] = None,
        limit: Optional[int] = None,
        debug: bool = False
    ) -> List[Dict]:
        """
        Get all briefs from the database (no platform filter)
        
        Args:
            status_filter: Filter by status (e.g., "Ready", "Draft")
            post_type_filter: Filter by post type(s) - list of post type names
            platform_filter: Filter by platform (e.g., "Threads")
            limit: Maximum number of briefs to return
            
        Returns:
            List of extracted brief data
        """
        # Build filter conditions - combine multiple filters with "and"
        filter_conditions = None
        filters = []
        
        if status_filter:
            filters.append({
                "property": "Status",
                "select": {
                    "equals": status_filter
                }
            })
        
        if post_type_filter and len(post_type_filter) > 0:
            # For multiple post types, use "or" condition to match any of them
            if len(post_type_filter) == 1:
                # Single post type filter
                filters.append({
                    "property": "Post Type",
                    "multi_select": {
                        "contains": post_type_filter[0]
                    }
                })
            else:
                # Multiple post types - use "or" to match any of them
                post_type_or_filters = [
                    {
                        "property": "Post Type",
                        "multi_select": {
                            "contains": post_type
                        }
                    }
                    for post_type in post_type_filter
                ]
                filters.append({
                    "or": post_type_or_filters
                })
        
        if platform_filter:
            filters.append({
                "property": "Platform",
                "multi_select": {
                    "contains": platform_filter
                }
            })
        
        # Combine filters with "and" if multiple filters exist
        if len(filters) == 1:
            filter_conditions = filters[0]
        elif len(filters) > 1:
            filter_conditions = {
                "and": filters
            }
        
        results = self.query_database(filter_conditions=filter_conditions)

        if debug:
            print(f"🔍 DEBUG: Found {len(results)} raw rows from Notion")
        
        # Extract structured data
        briefs = []
        skipped_no_topic = 0

        for page in results:
            brief_data = self.extract_brief_data(page)
            if brief_data:
                topic = brief_data.get("topic", "")
                if topic:
                    briefs.append(brief_data)
                else:
                    skipped_no_topic += 1
                    if debug:
                        print(f"Skipped row(no topic): {brief_data.get('page_id', 'unknown')[:8]}...")
            
            if limit and len(briefs) >= limit:
                break
        
        return briefs
    
    # Keep the old method for backward compatibility, but update it to use the new one
    def get_briefs_for_threads(
        self, 
        status_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get briefs that are suitable for Threads posting
        (DEPRECATED: Use get_all_briefs() instead)
        """
        # For now, just return all briefs (no platform filter)
        return self.get_all_briefs(status_filter=status_filter, limit=limit)