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
        strict_length: bool = False,
        style_analysis: Optional[Dict] = None
    ) -> str:
        """
        Build a prompt for GPT to generate a Threads post from a brief
        
        Args:
            brief: Brief data from Notion (topic, pillar, post_type, etc.)
            brand_voice: Optional brand voice/style guide (overrides brand_profile)
            strict_length: If True, emphasize length constraint even more
            style_analysis: Optional style analysis string from PostAnalyzer

            
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

        if style_analysis:
            prompt_parts.append(style_analysis)
        
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
            "- ALWAYS end with a complete question or call-to-action - this is REQUIRED",
            "- Ensure the final question/CTA is complete and not cut off",
            "",
            "Examples of allowed formatting:",
            "• Point one",
            "→ Point two",
            "★ Key insight",
            "",
            "Generate ONLY the post text, nothing else. No quotes, no explanations. NO EMOJIS. MAX 500 CHARACTERS. MUST end with a complete question or CTA."
        ])
        
        if brand_voice:
            prompt_parts.insert(1, f"Brand voice: {brand_voice}")
        
        return "\n".join(prompt_parts)
    
    def build_enhanced_prompt(self, brief: Dict, context: Optional[Dict] = None) -> str:
        """
        Build an enhanced prompt with additional context
        
        Args:
            brief: Brief data from Notion
            context: Optional additional context (past posts, audience, etc.)
            
        Returns:
            Enhanced prompt string
        """
        base_prompt = self.build_post_prompt(brief)
        
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

    def build_style_based_prompt(
        self,
        topic: Optional[str] = None,
        style_analysis: Optional[str] = None,
        strict_length: bool = False
    ) -> str:
        """
        Build a prompt for GPT using style analysis (Path B - no brief needed)
        
        Args:
            topic: Optional topic to write about (if None, generate general post)
            style_analysis: Style analysis string from PostAnalyzer
            strict_length: If True, emphasize length constraint even more
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        if topic:
            prompt_parts.append(f"Create an engaging Threads post about: {topic}")
        else:
            prompt_parts.append("Create an engaging Threads post that matches your authentic style")
        
        # Add style analysis (required for Path B)
        if style_analysis:
            prompt_parts.append(style_analysis)
        else:
            prompt_parts.append("\n⚠️  No style analysis provided - using default style")
        
        # Add brand context if available
        if self.brand_profile and self.brand_profile.is_loaded():
            brand_context = self.brand_profile.get_context_for_prompt()
            if brand_context:
                prompt_parts.append("\nBrand Context:")
                prompt_parts.append(brand_context)
        
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
            "- ALWAYS end with a complete question or call-to-action - this is REQUIRED",
            "- Ensure the final question/CTA is complete and not cut off",
            "",
            "Examples of allowed formatting:",
            "• Point one",
            "→ Point two",
            "★ Key insight",
            "",
            "Generate ONLY the post text, nothing else. No quotes, no explanations. NO EMOJIS. MAX 500 CHARACTERS. MUST end with a complete question or CTA."
        ])
        
        return "\n".join(prompt_parts)
    
    def build_connection_prompt(
        self,
        connection_type: Optional[str] = None,
        strict_length: bool = False
    ) -> str:
        """
        Build a prompt for short, casual networking/connection posts (Path C)
        
        Args:
            connection_type: Optional specific type (e.g., "founders", "developers", "SMBs")
            strict_length: If True, emphasize length constraint even more
            
        Returns:
            Formatted prompt string for connection posts
        """
        prompt_parts = []
        
        # Base instruction
        if connection_type:
            prompt_parts.append(f"Create a short, casual Threads post looking to connect with {connection_type}")
        else:
            prompt_parts.append("Create a short, casual Threads post looking to connect with others in your space")
        
        # Add brand context if available
        if self.brand_profile and self.brand_profile.is_loaded():
            brand_context = self.brand_profile.get_context_for_prompt()
            if brand_context:
                prompt_parts.append("\nBrand Context:")
                prompt_parts.append(brand_context)
                
                # Extract audience from brand profile for connection targeting
                profile_data = self.brand_profile.profile_data
                if profile_data.get("audience"):
                    audience = profile_data.get("audience", "")
                    if isinstance(audience, list):
                        audience = ", ".join(audience[:2])  # Use first 2 audience types
                    prompt_parts.append(f"\nTarget audience to connect with: {audience}")
        
        # Shorter length requirement for connection posts (100-200 chars)
        length_requirement = "- MAXIMUM 200 characters - keep it short and casual (aim for 100-150 characters)"
        if strict_length:
            length_requirement = "- CRITICAL: MAXIMUM 200 characters - MUST be under 200. Keep it very short and casual (aim for 100-150 characters)."
        
        prompt_parts.extend([
            "",
            "POST TYPE: Short, casual networking/connection post",
            "",
            "CRITICAL REQUIREMENTS:",
            "- NEVER use emojis (🚀, 🤔, 🔒, 👇, etc.) - they are STRICTLY FORBIDDEN",
            "- Use ONLY plain text - no symbols needed for this type of post",
            length_requirement,
            "- Be casual, conversational, and direct",
            "- Keep it simple and authentic",
            "- Focus on connection/networking",
            "- Use first person (I, me, my) or second person (you, your)",
            "- End with a question to encourage engagement",
            "",
            "STYLE EXAMPLES:",
            "- 'Looking for other founders in the SaaS space. Here?'",
            "- 'Startup founders. Here?'",
            "- 'Threads. I am looking to connect with developers building API integrations. Anyone?'",
            "- 'Hey, I am looking to connect with SMBs modernizing their operations. Who else is in this space?'",
            "- 'Anyone out there building internal tools for service companies? Would love to connect.'",
            "",
            "Generate ONLY the post text, nothing else. No quotes, no explanations. NO EMOJIS. MAX 200 CHARACTERS. Keep it short and casual."
        ])
        
        return "\n".join(prompt_parts)