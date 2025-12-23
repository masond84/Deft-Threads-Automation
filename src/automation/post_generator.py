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
    
    def generate_post_for_brief(self, brief: Dict, retry_on_length_error: bool = True) -> Dict:
        """
        Generate a post for a single brief with retry logic for length errors
        
        Args:
            brief: Brief data from Notion
            retry_on_length_error: Whether to retry once if post is too long
            
        Returns:
            Dictionary with brief info and generated post
        """
        # Build prompt from brief
        prompt = self.prompt_builder.build_post_prompt(brief)
        
        max_attempts = 2 if retry_on_length_error else 1
        
        for attempt in range(max_attempts):
            # Generate post
            if attempt == 0:
                print(f"🤖 Generating post for: {brief.get('topic', 'Unknown')}")
            else:
                print(f"🔄 Retrying generation (attempt {attempt + 1}/{max_attempts})...")
            
            generated_text = self.gpt_client.generate_post(prompt)
            
            if not generated_text:
                return {
                    "brief": brief,
                    "generated_post": None,
                    "error": "Failed to generate post",
                    "valid": False,
                    "attempts": attempt + 1
                }
            
            # Validate
            is_valid, error_msg = self.gpt_client.validate_content(generated_text)
            
            # If valid, return success
            if is_valid:
                return {
                    "brief": brief,
                    "generated_post": generated_text,
                    "error": None,
                    "valid": True,
                    "prompt_used": prompt,
                    "attempts": attempt + 1
                }
            
            # If invalid due to length and we haven't retried yet, retry
            if retry_on_length_error and "too long" in error_msg.lower() and attempt < max_attempts - 1:
                continue  # Retry the generation
            
            # If invalid for other reasons or we've exhausted retries, return failure
            return {
                "brief": brief,
                "generated_post": generated_text,
                "error": error_msg,
                "valid": False,
                "prompt_used": prompt,
                "attempts": attempt + 1
            }
        
        # Should never reach here, but just in case
        return {
            "brief": brief,
            "generated_post": None,
            "error": "Failed after all retry attempts",
            "valid": False,
            "attempts": max_attempts
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
                    attempts_str = f" (attempt {result.get('attempts', 1)})" if result.get('attempts', 1) > 1 else ""
                    print(f"✅ Generated ({len(result['generated_post'])} chars){attempts_str}")
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        return results