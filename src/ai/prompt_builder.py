from typing import Dict, Optional
from utils.symbols import LIST_MARKERS, ALLOWED_SYMBOLS

class PromptBuilder:
    def __init__(self, brand_profile=None):
        """
        Initialize prompt builder with brand context
        
        Args:
            brand_profile: BrandProfile instance (optional)
        """
        self.brand_profile = brand_profile
    
    def build_post_prompt(
        self, 
        brief: Dict, 
        brand_voice: Optional[str] = None,
        strict_length: bool = False
    ) -> str:
        """
        Build a prompt for GPT to generate a Threads post from a brief
        
        Args:
            brief: Brief data from Notion (topic, pillar, post_type, etc.)
            brand_voice: Optional brand voice/style guide (overrides brand_profile)
            strict_length: If True, emphasize length constraint even more
            
        Returns:
            Formatted prompt string
        """
        topic = brief.get("topic", "")
        pillar = brief.get("pillar", "")
        post_types = brief.get("post_type", [])
        post_type_str = ", ".join(post_types) if post_types else "Text"
        
        # Build the prompt
        prompt_parts = [
            f"Create an engaging Threads post about: {topic}",
        ]
        
        # Add brand context if available
        if self.brand_profile and self.brand_profile.is_loaded():
            brand_context = self.brand_profile.get_context_for_prompt()
            if brand_context:
                prompt_parts.append("\nBrand Context:")
                prompt_parts.append(brand_context)
        
        if pillar:
            prompt_parts.append(f"\nContent pillar: {pillar}")
        
        if post_type_str and post_type_str != "Text":
            prompt_parts.append(f"Post type: {post_type_str}")
        
        # Add extra emphasis on length if strict_length is True
        length_requirement = "- MAXIMUM 500 characters - aim for 400-450 characters to be safe"
        if strict_length:
            length_requirement = "- CRITICAL: MAXIMUM 500 characters - MUST be under 500. Aim for 400-450 characters. Be very concise."
        
        prompt_parts.extend([
            "",
            "CRITICAL REQUIREMENTS:",
            "- NEVER use emojis (🚀, 🤔, 🔒, 👇, etc.) - they are STRICTLY FORBIDDEN",
            "- Use ONLY plain text and simple symbols for decoration",
            "- Allowed symbols: • → ➤ ▸ ▪ ★ ✧ ✦ (bullets, arrows, stars only)",
            length_requirement,
            "- Be concise and direct - every word counts",
            "- Make it conversational and authentic",
            "- Add value or insight",
            "- Use engaging language",
            "- No hashtags unless natural",
            "- Write in first or second person when appropriate",
            "- End with a question or call-to-action when natural",
            "",
            "Examples of allowed formatting:",
            "• Point one",
            "→ Point two",
            "★ Key insight",
            "",
            "Generate ONLY the post text, nothing else. No quotes, no explanations. NO EMOJIS. MAX 500 CHARACTERS."
        ])
        
        if brand_voice:
            prompt_parts.insert(1, f"Brand voice: {brand_voice}")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_enhanced_prompt(brief: Dict, context: Optional[Dict] = None) -> str:
        """
        Build an enhanced prompt with additional context
        
        Args:
            brief: Brief data from Notion
            context: Optional additional context (past posts, audience, etc.)
            
        Returns:
            Enhanced prompt string
        """
        base_prompt = PromptBuilder.build_post_prompt(brief)
        
        if context:
            context_parts = ["\nAdditional context:"]
            
            if context.get("audience"):
                context_parts.append(f"Target audience: {context['audience']}")
            
            if context.get("tone"):
                context_parts.append(f"Tone: {context['tone']}")
            
            if context.get("examples"):
                context_parts.append(f"Style examples: {context['examples']}")
            
            if context_parts:
                base_prompt += "\n" + "\n".join(context_parts)
        
        return base_prompt