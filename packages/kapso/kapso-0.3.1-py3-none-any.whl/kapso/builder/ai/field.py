"""
AI Field marker for fields that should be resolved by AI at runtime.
"""

from typing import Dict, Any


class AIField:
    """Marker for fields that should be resolved by AI at runtime with inline configuration."""
    
    def __init__(self, prompt: str = ""):
        """
        Initialize an AIField with configuration.
        
        Args:
            prompt: The prompt text for AI generation
        """
        self.prompt = prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to backend compatible format with $ai marker."""
        return {"$ai": {}}
    
    def to_config(self) -> Dict[str, Any]:
        """
        Generate the AI field configuration.
        
        Returns:
            Dictionary with the AI field configuration for the backend
        """
        return {
            "mode": "prompt",
            "prompt": self.prompt
        }
    
    @classmethod
    def prompt(cls, text: str) -> 'AIField':
        """
        Create an AIField with prompt mode.
        
        Args:
            text: The prompt text
            
        Returns:
            AIField instance configured for prompt mode
        """
        return cls(prompt=text)