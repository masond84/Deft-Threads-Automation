import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict
import time

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

class GPTClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the GPTClient

        Args: 
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def remove_emojis(self, text: str) -> str:
        """
        Remove all emojis from text
        
        Args:
            text: Text that may contain emojis
            
        Returns:
            Text with all emojis removed
        """
        # Remove emojis using regex
        # This pattern matches most emoji ranges
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U00002700-\U000027BF"  # dingbats
            "]+",
            flags=re.UNICODE
        )
        
        return emoji_pattern.sub('', text).strip()

    def truncate_to_limit(self, text: str, max_chars: int = 500) -> str:
        """
        Truncate text to max characters, preserving the last sentence/question/CTA
        
        Args:
            text: Text to truncate
            max_chars: Maximum characters allowed
            
        Returns:
            Truncated text with preserved CTA/question
        """
        if len(text) <= max_chars:
            return text
        
        # Split by lines to find the last line (often contains CTA/question)
        lines = text.split('\n')
        
        # Find the last line that might be a CTA/question
        last_line = None
        last_line_index = -1
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and (line.endswith('?') or line.endswith('!') or 
                        line.lower().startswith('what') or 
                        line.lower().startswith('how') or
                        line.lower().startswith('why') or
                        'share' in line.lower() or
                        'thoughts' in line.lower()):
                last_line = line
                last_line_index = i
                break
        
        # If we found a CTA/question line, try to preserve it
        if last_line and last_line_index >= 0:
            # Calculate text before the last line
            text_before_last_line = '\n'.join(lines[:last_line_index])
            text_before_length = len(text_before_last_line)
            last_line_length = len(last_line)
            
            # If we can fit the last line, include it
            if text_before_length + last_line_length + 1 <= max_chars:
                # We have room for the last line
                # Truncate the text before if needed
                if text_before_length + last_line_length + 1 > max_chars:
                    available_chars = max_chars - last_line_length - 10  # Reserve space for last line + newline
                    if available_chars > 0:
                        truncated_before = self._truncate_text_smart(text_before_last_line, available_chars)
                        return truncated_before + '\n\n' + last_line
                    else:
                        # Not enough room, just return the last line if it fits
                        if last_line_length <= max_chars:
                            return last_line
                else:
                    return text_before_last_line + '\n\n' + last_line
        
        # No CTA/question found, use smart truncation
        return self._truncate_text_smart(text, max_chars)
    
    def _truncate_text_smart(self, text: str, max_chars: int) -> str:
        """
        Smart truncation that preserves sentence endings
        
        Args:
            text: Text to truncate
            max_chars: Maximum characters
            
        Returns:
            Truncated text
        """
        if len(text) <= max_chars:
            return text
        
        # Look for sentence endings near the limit
        truncated = text[:max_chars]
        
        # Find the last sentence ending (., ?, !) within reasonable distance
        for end_char in ['?', '!', '.']:
            last_sentence_end = truncated.rfind(end_char)
            if last_sentence_end > max_chars * 0.7:  # If found reasonably close to limit
                return text[:last_sentence_end + 1].strip()
        
        # No sentence ending found, try word boundary
        last_space = truncated.rfind(' ')
        last_newline = truncated.rfind('\n')
        last_break = max(last_space, last_newline)
        
        if last_break > max_chars * 0.8:
            return text[:last_break].strip()
        else:
            return truncated.strip()

    def generate_post(
        self,
        prompt: str,
        max_tokens: int = 100,  # Reduced to 100 - ~100 tokens ≈ 350-400 chars (leaves room for CTA)
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Generate a post using GPT

        Args:
            prompt: The prompt to send to GPT
            max_tokens: Maximum tokens for response (default 100 for ~350-400 chars, leaving room for CTA)
            temperature: Creativity level (0.0-2.0, default: 0.7)
        
        Returns:
            Generated post text or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a social media content creator specializing in engaging, authentic Threads posts. NEVER use emojis - only use plain text and simple symbols like bullets (•), arrows (→), and stars (★). Keep posts STRICTLY under 500 characters (aim for 400-450). ALWAYS end with a complete question or call-to-action. Be concise and conversational."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                generated_text = response.choices[0].message.content.strip()
                
                # Remove quotes if GPT wrapped the text
                if generated_text.startswith('"') and generated_text.endswith('"'):
                    generated_text = generated_text[1:-1]
                
                # Remove any emojis that GPT might have used despite instructions
                generated_text = self.remove_emojis(generated_text)
                
                # Safety net: truncate if still over 500 chars, but preserve CTA/question
                if len(generated_text) > 500:
                    generated_text = self.truncate_to_limit(generated_text, max_chars=500)
                
                return generated_text
                
            except Exception as e:
                print(f"⚠️  GPT API error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    print(f"❌ Failed to generate post after {self.max_retries} attempts")
                    return None
        
        return None
    
    def validate_content(self, text: str) -> tuple[bool, str]:
        """
        Validate generated content
        
        Args:
            text: The generated text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Content is empty"
        
        if len(text) > 500:
            return False, f"Content too long ({len(text)} chars, max 500)"
        
        if len(text) < 10:
            return False, "Content too short"
        
        # Check for emojis (should not have any)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002600-\U000026FF"
            "\U00002700-\U000027BF"
            "]+",
            flags=re.UNICODE
        )
        
        if emoji_pattern.search(text):
            return False, "Content contains emojis (not allowed)"
        
        # Check for common GPT artifacts
        if text.startswith("Here's") and len(text) < 50:
            return False, "Content appears incomplete"
        
        return True, ""