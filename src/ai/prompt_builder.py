from typing import Dict, Optional
from utils.symbols import LIST_MARKERS, ALLOWED_SYMBOLS
class PromptBuilder:
    @staticmethod
    def build_post_prompt(brief: Dict, brand_voice: Optional[str] = None) -> str:
        """
        Build a prompt for GPT to generate a Threads post from a brief
        
        Args:
            brief: Brief data from Notion (topic, pillar, post_type, etc.)
            brand_voice: Optional brand voice/style guide
            
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
        
        if pillar:
            prompt_parts.append(f"Content pillar: {pillar}")
        
        if post_type_str and post_type_str != "Text":
            prompt_parts.append(f"Post type: {post_type_str}")
        
        prompt_parts.extend([
            "",
            "CRITICAL REQUIREMENTS:",
            "- NEVER use emojis (🚀, 🤔, 🔒, 👇, etc.) - they are STRICTLY FORBIDDEN",
            "- Use ONLY plain text and simple symbols for decoration",
            "- Allowed symbols: • → ➤ ▸ ▪ ★ ✧ ✦ (bullets, arrows, stars only)",
            "- MAXIMUM 500 characters - aim for 400-450 characters to be safe",
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
            "Generate ONLY the post text, nothing else. No quotes, no explanations. NO EMOJIS."
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