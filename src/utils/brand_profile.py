from pathlib import Path
from typing import Optional, Dict

class BrandProfile:
    def __init__(self, profile_path: Optional[Path] = None):
        """
        Load brand profile from file
        
        Args:
            profile_path: Path to brand profile file (default: src/config/brand_profile.md)
        """
        if profile_path is None:
            # Check multiple possible locations
            project_root = Path(__file__).parent.parent.parent
            src_dir = Path(__file__).parent.parent  # src/ directory
            
            # Try src/config/ first (where file actually is)
            possible_paths = [
                src_dir / "config" / "brand_profile.md",  # src/config/brand_profile.md
                project_root / "config" / "brand_profile.md",  # config/brand_profile.md (project root)
            ]
            
            # Use the first path that exists, or default to src/config/
            profile_path = None
            for path in possible_paths:
                if path.exists():
                    profile_path = path
                    break
            
            if profile_path is None:
                # Default to src/config/ if neither exists
                profile_path = src_dir / "config" / "brand_profile.md"
        
        self.profile_path = profile_path
        self.profile_data = self._load_profile()
    
    def _load_profile(self) -> Dict:
        """Load brand profile from markdown file"""
        if not self.profile_path.exists():
            return {}
        
        content = self.profile_path.read_text(encoding='utf-8')
        
        # Initialize profile structure
        profile = {
            "brand_name": "",
            "tone": "",
            "voice": "",
            "audience": "",
            "key_topics": [],
            "style_guidelines": [],
            "example_posts": [],
            "do_not_use": []
        }
        
        # Parse markdown-style profile
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Main heading
            if line.startswith('# '):
                profile["brand_name"] = line[2:].strip()
            # Section heading
            elif line.startswith('## '):
                section_name = line[3:].strip().lower()
                # Map section names to profile keys
                section_map = {
                    "tone": "tone",
                    "voice": "voice",
                    "audience": "audience",
                    "target audience": "audience",
                    "key topics": "key_topics",
                    "topics": "key_topics",
                    "style guidelines": "style_guidelines",
                    "guidelines": "style_guidelines",
                    "example posts": "example_posts",
                    "examples": "example_posts",
                    "do not use": "do_not_use",
                    "avoid": "do_not_use",
                    "positioning": "voice",  # Map positioning to voice
                    "one-liner": "voice",  # Map one-liner to voice
                    "core capabilities": "key_topics",  # Map capabilities to topics
                    "supporting services": "key_topics"
                }
                current_section = section_map.get(section_name)
            # List items
            elif (line.startswith('- ') or line.startswith('* ')) and current_section:
                item = line[2:].strip()
                if current_section in ["key_topics", "style_guidelines", "example_posts", "do_not_use"]:
                    profile[current_section].append(item)
            # Regular text lines (for positioning, one-liner, etc.)
            elif current_section == "voice" and line and not line.startswith('#') and not line.startswith('-'):
                # Append to voice if it's a text line in voice section
                if profile["voice"]:
                    profile["voice"] += " " + line
                else:
                    profile["voice"] = line
        
        return profile
    
    def get_context_for_prompt(self) -> str:
        """Get formatted context string for GPT prompts"""
        if not self.profile_data:
            return ""
        
        parts = []
        
        if self.profile_data.get("brand_name"):
            parts.append(f"Brand: {self.profile_data['brand_name']}")
        
        if self.profile_data.get("tone"):
            parts.append(f"Tone: {self.profile_data['tone']}")
        
        if self.profile_data.get("voice"):
            parts.append(f"Voice: {self.profile_data['voice']}")
        
        if self.profile_data.get("audience"):
            parts.append(f"Target Audience: {self.profile_data['audience']}")
        
        if self.profile_data.get("style_guidelines"):
            parts.append("\nStyle Guidelines:")
            for guideline in self.profile_data["style_guidelines"]:
                parts.append(f"- {guideline}")
        
        if self.profile_data.get("example_posts"):
            parts.append("\nExample Post Styles:")
            for example in self.profile_data["example_posts"][:3]:  # Limit to 3 examples
                parts.append(f"- {example}")
        
        if self.profile_data.get("do_not_use"):
            parts.append("\nAvoid:")
            for item in self.profile_data["do_not_use"]:
                parts.append(f"- {item}")
        
        return "\n".join(parts) if parts else ""
    
    def is_loaded(self) -> bool:
        """Check if profile was successfully loaded"""
        return bool(self.profile_data and self.profile_path.exists())