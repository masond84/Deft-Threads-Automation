from typing import List, Dict, Optional
from ai.gpt_client import GPTClient
from ai.prompt_builder import PromptBuilder
from database.notion_client import NotionClient
from utils.brand_profile import BrandProfile
from utils.post_analyzer import PostAnalyzer
from api.threads_api import ThreadsAPI

class PostGenerator:
    def __init__(self, use_brand_profile: bool = True):
        """
        Initialize post generator
        
        Args:
            use_brand_profile: Load brand profile from config file (default: True)
        """
        self.gpt_client = GPTClient()
        self.notion_client = NotionClient()
        self.threads_api = ThreadsAPI()  # Add Threads API for posting
        
        # Load brand profile
        brand_profile = None
        if use_brand_profile:
            try:
                brand_profile = BrandProfile()
                if brand_profile.is_loaded():
                    print("✅ Loaded brand profile")
                else:
                    print("⚠️  Brand profile file not found - using default prompts")
            except Exception as e:
                print(f"⚠️  Could not load brand profile: {e}")
        
        self.prompt_builder = PromptBuilder(brand_profile=brand_profile)
        self.post_analyzer = PostAnalyzer()
    
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
        max_attempts = 2 if retry_on_length_error else 1
        
        for attempt in range(max_attempts):
            # Build prompt - use stricter length requirement on retry
            strict_length = (attempt > 0)  # Stricter on retry attempts
            prompt = self.prompt_builder.build_post_prompt(brief, strict_length=strict_length)
            
            # Generate post
            if attempt == 0:
                print(f"🤖 Generating post for: {brief.get('topic', 'Unknown')}")
            else:
                print(f"🔄 Retrying generation with stricter length requirements (attempt {attempt + 1}/{max_attempts})...")
            
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
    
    def post_approved_post(self, result: Dict) -> Dict:
        """
        Post an approved generated post to Threads
        
        Args:
            result: Result dictionary from generate_post_for_brief
            
        Returns:
            Dictionary with posting result
        """
        if not result.get("valid") or not result.get("generated_post"):
            return {
                "success": False,
                "error": "Post is not valid or missing",
                "result": result
            }
        
        post_text = result["generated_post"]
        brief = result["brief"]
        
        print(f"📤 Posting to Threads: {brief.get('topic', 'Unknown')}")
        
        # Post to Threads
        post_result = self.threads_api.post_thread(post_text, auto_publish=True)
        
        if post_result:
            thread_id = post_result.get('id') or post_result.get('thread_id')
            return {
                "success": True,
                "thread_id": thread_id,
                "thread_url": f"https://www.threads.net/t/{thread_id}/" if thread_id else None,
                "result": result
            }
        else:
            return {
                "success": False,
                "error": "Failed to post to Threads",
                "result": result
            }
    
    def post_multiple_approved(self, results: List[Dict], delay_seconds: int = 60) -> List[Dict]:
        """
        Post multiple approved posts with delay between each
        
        Args:
            results: List of result dictionaries to post
            delay_seconds: Delay between posts (default: 60 seconds)
            
        Returns:
            List of posting results
        """
        import time
        
        posting_results = []
        valid_posts = [r for r in results if r.get("valid")]
        
        for i, result in enumerate(valid_posts, 1):
            print(f"\n[{i}/{len(valid_posts)}] Posting...")
            post_result = self.post_approved_post(result)
            posting_results.append(post_result)
            
            if post_result["success"]:
                print(f"✅ Posted successfully!")
                if post_result.get("thread_url"):
                    print(f"   View at: {post_result['thread_url']}")
            else:
                print(f"❌ Failed to post: {post_result.get('error', 'Unknown error')}")
            
            # Wait before next post (except for last one)
            if i < len(valid_posts):
                print(f"⏳ Waiting {delay_seconds} seconds before next post...")
                time.sleep(delay_seconds)
        
        return posting_results
    
    def generate_post_from_analysis(
        self,
        topic: Optional[str] = None,
        limit: int = 25,
        retry_on_length_error: bool = True
    ) -> Dict:
        """
        Generate a post using style analysis from past posts (Path B)
        
        Args:
            topic: Optional topic to write about (if None, generate general post)
            limit: Number of past posts to analyze (default: 25)
            retry_on_length_error: Whether to retry once if post is too long
            
        Returns:
            Dictionary with generated post and analysis info
        """
        max_attempts = 2 if retry_on_length_error else 1
        
        # Step 1: Fetch past posts
        print(f"📥 Fetching {limit} past posts for analysis...")
        posts = self.threads_api.get_user_threads(limit=limit)
        
        if not posts:
            return {
                "generated_post": None,
                "error": "Could not fetch posts for analysis",
                "valid": False,
                "analysis": None
            }
        
        # Step 2: Analyze posts
        print("📊 Analyzing post patterns...")
        analysis = self.post_analyzer.analyze_posts(posts)
        
        if not analysis:
            return {
                "generated_post": None,
                "error": "Post analysis failed",
                "valid": False,
                "analysis": None
            }
        
        # Step 3: Format analysis for prompt
        style_analysis = self.post_analyzer.format_for_prompt(analysis)
        
        # Step 4: Generate post
        for attempt in range(max_attempts):
            strict_length = (attempt > 0)
            prompt = self.prompt_builder.build_style_based_prompt(
                topic=topic,
                style_analysis=style_analysis,
                strict_length=strict_length
            )
            
            if attempt == 0:
                print(f"🤖 Generating post{' about: ' + topic if topic else ''}...")
            else:
                print(f"🔄 Retrying generation with stricter length requirements (attempt {attempt + 1}/{max_attempts})...")
            
            generated_text = self.gpt_client.generate_post(prompt)
            
            if not generated_text:
                return {
                    "generated_post": None,
                    "error": "Failed to generate post",
                    "valid": False,
                    "analysis": analysis,
                    "attempts": attempt + 1
                }
            
            # Validate
            is_valid, error_msg = self.gpt_client.validate_content(generated_text)
            
            if is_valid:
                return {
                    "generated_post": generated_text,
                    "error": None,
                    "valid": True,
                    "prompt_used": prompt,
                    "analysis": analysis,
                    "attempts": attempt + 1
                }
            
            # If invalid due to length and we haven't retried yet, retry
            if retry_on_length_error and "too long" in error_msg.lower() and attempt < max_attempts - 1:
                continue
            
            return {
                "generated_post": generated_text,
                "error": error_msg,
                "valid": False,
                "prompt_used": prompt,
                "analysis": analysis,
                "attempts": attempt + 1
            }
        
        return {
            "generated_post": None,
            "error": "Failed after all retry attempts",
            "valid": False,
            "analysis": analysis,
            "attempts": max_attempts
        }