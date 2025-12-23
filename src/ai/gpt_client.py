import os
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

    def generate_post(
        self,
        prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Generate a post using GPT

        Args:
            prompt: The prompt to send to GPT
            max_tokens: Maxiumum tokens for response (default 200 for ~500 chars)
            temperature: Creativity level (0.0-2.0, default: 0.7)
        
        returns:
            Generated post text or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a social media content creator specializing in engaging, authentic Threads posts. Keep posts under 500 characters, conversational, and valuable."
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
        
        # Check for common GPT artifacts
        if text.startswith("Here's") and len(text) < 50:
            return False, "Content appears incomplete"
        
        return True, ""