from typing import List, Dict, Optional
from ai.gpt_client import GPTClient
from ai.prompt_builder import PromptBuilder
from database.notion_client import NotionClient

class PostGenerator:
    def __init__(self):
        self.gpt_client = GPTClient()
        self.notion_client = NotionClient()
        self.prompt_builder = PromptBuilder()
    
    def fetch_briefs(
        self, 
        status_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Fetch all briefs from Notion (no platform filter)
        
        Args:
            status_filter: Filter by status (e.g., "Ready")
            limit: Maximum number of briefs to fetch
            
        Returns:
            List of brief dictionaries
        """
        # Use the new method that doesn't filter by platform
        return self.notion_client.get_all_briefs(
            status_filter=status_filter,
            limit=limit,
            debug=True
        )
    
    def generate_post_for_brief(self, brief: Dict) -> Dict:
        """
        Generate a post for a single brief
        
        Args:
            brief: Brief data from Notion
            
        Returns:
            Dictionary with brief info and generated post
        """
        # Build prompt from brief
        prompt = self.prompt_builder.build_post_prompt(brief)
        
        # Generate post
        print(f"🤖 Generating post for: {brief.get('topic', 'Unknown')}")
        generated_text = self.gpt_client.generate_post(prompt)
        
        if not generated_text:
            return {
                "brief": brief,
                "generated_post": None,
                "error": "Failed to generate post",
                "valid": False
            }
        
        # Validate
        is_valid, error_msg = self.gpt_client.validate_content(generated_text)
        
        return {
            "brief": brief,
            "generated_post": generated_text,
            "error": error_msg if not is_valid else None,
            "valid": is_valid,
            "prompt_used": prompt
        }
    
    def generate_posts_for_briefs(
        self, 
        briefs: List[Dict],
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Generate posts for multiple briefs
        
        Args:
            briefs: List of brief dictionaries
            show_progress: Whether to show progress messages
            
        Returns:
            List of generation results
        """
        results = []
        
        for i, brief in enumerate(briefs, 1):
            if show_progress:
                print(f"\n[{i}/{len(briefs)}] Processing: {brief.get('topic', 'Unknown')}")
            
            result = self.generate_post_for_brief(brief)
            results.append(result)
            
            if show_progress:
                if result["valid"]:
                    print(f"✅ Generated ({len(result['generated_post'])} chars)")
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        return results