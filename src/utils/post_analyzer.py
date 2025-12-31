from typing import List, Dict, Optional
import re


class PostAnalyzer:
    """
    Analyzes posts to extract patterns, style, and structure
    """
    
    def __init__(self):
        pass
    
    def analyze_posts(self, posts: List[Dict]) -> Dict:
        """
        Analyze a collection of posts to extract patterns
        
        Args:
            posts: List of post dictionaries with 'text' field
            
        Returns:
            Dictionary with analysis results
        """
        if not posts:
            return {}
        
        # Extract text content
        texts = [p.get("text", "") for p in posts if p.get("text")]
        
        if not texts:
            return {}
        
        analysis = {
            "total_posts": len(texts),
            "avg_length": sum(len(t) for t in texts) / len(texts),
            "min_length": min(len(t) for t in texts),
            "max_length": max(len(t) for t in texts),
            "common_starters": self._extract_starters(texts),
            "common_endings": self._extract_endings(texts),
            "structure_patterns": self._analyze_structure(texts),
            "tone_indicators": self._analyze_tone(texts),
            "common_questions": self._extract_questions(texts),
            "example_posts": texts[:5]  # Top 5 examples
        }
        
        return analysis
    
    def _extract_starters(self, texts: List[str]) -> List[str]:
        """Extract common opening phrases"""
        starters = []
        for text in texts:
            # Get first sentence (up to first period, question mark, or exclamation)
            first_sentence = re.split(r'[.!?]+', text)[0].strip()
            if len(first_sentence) > 10 and len(first_sentence) < 150:
                starters.append(first_sentence)
        return starters[:5]  # Top 5
    
    def _extract_endings(self, texts: List[str]) -> List[str]:
        """Extract common ending phrases/questions"""
        endings = []
        for text in texts:
            # Get last sentence
            sentences = re.split(r'[.!?]+', text)
            last_sentence = sentences[-1].strip() if sentences else ""
            if len(last_sentence) > 10:
                endings.append(last_sentence)
        return endings[:5]  # Top 5
    
    def _analyze_structure(self, texts: List[str]) -> Dict:
        """Analyze common structural patterns"""
        total = len(texts)
        if total == 0:
            return {}
        
        patterns = {
            "uses_bullets": sum(1 for t in texts if '•' in t or '-' in t or '*' in t) / total,
            "uses_questions": sum(1 for t in texts if '?' in t) / total,
            "uses_numbers": sum(1 for t in texts if re.search(r'\d+\.', t)) / total,
            "paragraph_breaks": sum(1 for t in texts if '\n\n' in t) / total,
            "uses_line_breaks": sum(1 for t in texts if '\n' in t) / total,
        }
        return patterns
    
    def _analyze_tone(self, texts: List[str]) -> Dict:
        """Analyze tone indicators"""
        total = len(texts)
        if total == 0:
            return {}
        
        all_text = " ".join(texts).lower()
        
        tone_indicators = {
            "conversational": sum(1 for word in ["you", "your", "we", "our", "i", "my"] if word in all_text) / (total * 10),  # Normalize
            "direct": sum(1 for t in texts if t.startswith(("Here", "This", "That", "The", "Most", "Many"))) / total,
            "question_heavy": sum(1 for t in texts if t.count('?') > 1) / total,
            "uses_imperative": sum(1 for t in texts if re.search(r'\b(Let\'s|Try|Start|Build|Create)', t, re.IGNORECASE)) / total,
        }
        return tone_indicators
    
    def _extract_questions(self, texts: List[str]) -> List[str]:
        """Extract questions used in posts"""
        questions = []
        for text in texts:
            # Find sentences ending with ?
            question_sentences = re.findall(r'[^.!?]*\?', text)
            questions.extend([q.strip() for q in question_sentences if len(q.strip()) > 10])
        return questions[:10]  # Top 10 questions
    
    def format_for_prompt(self, analysis: Dict) -> str:
        """
        Format analysis results for GPT prompt
        
        Args:
            analysis: Analysis dictionary from analyze_posts
            
        Returns:
            Formatted string for prompt
        """
        if not analysis:
            return ""
        
        parts = ["\n📊 POST STYLE ANALYSIS:"]
        
        if analysis.get("example_posts"):
            parts.append("\nExample posts to match style:")
            for i, post in enumerate(analysis["example_posts"], 1):
                parts.append(f"\nExample {i}:")
                parts.append(post[:300] + "..." if len(post) > 300 else post)
        
        if analysis.get("common_starters"):
            parts.append(f"\nCommon opening patterns:")
            for starter in analysis["common_starters"][:3]:
                parts.append(f"  • {starter}")
        
        if analysis.get("common_endings"):
            parts.append(f"\nCommon ending patterns:")
            for ending in analysis["common_endings"][:3]:
                parts.append(f"  • {ending}")
        
        if analysis.get("structure_patterns"):
            struct = analysis["structure_patterns"]
            parts.append(f"\nStructure preferences:")
            if struct.get("uses_bullets", 0) > 0.3:
                parts.append("  • Often uses bullet points")
            if struct.get("uses_questions", 0) > 0.5:
                parts.append("  • Frequently ends with questions")
            if struct.get("uses_line_breaks", 0) > 0.5:
                parts.append("  • Uses line breaks for structure")
        
        parts.append("\nGenerate a post that matches this style and structure.")
        
        return "\n".join(parts)