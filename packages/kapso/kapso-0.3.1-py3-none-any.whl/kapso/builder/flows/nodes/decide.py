"""
DecideNode for AI-powered decision branching in flows.
"""

from typing import List, Optional
from dataclasses import dataclass

from .base import Node


@dataclass
class Condition:
    """Condition for decision branching."""
    label: str
    description: str
    id: Optional[str] = None  # Set by backend


class DecideNode(Node):
    """Node for AI-powered decision making and flow routing."""
    
    def __init__(
        self,
        id: str,
        provider_model_name: str,
        conditions: List[Condition],
        decision_type: str = "ai",
        llm_temperature: float = 0.0,
        llm_max_tokens: int = 10000
    ):
        config = {
            "decision_type": decision_type,
            "provider_model_name": provider_model_name,
            "conditions": [
                {"label": c.label, "description": c.description}
                for c in conditions
            ],
            "llm_temperature": llm_temperature,
            "llm_max_tokens": llm_max_tokens
        }
        
        # Store conditions for property access
        self._conditions = conditions
        
        super().__init__(
            id=id,
            node_type="decide",
            config=config
        )
    
    @property
    def provider_model_name(self) -> str:
        """Get the provider model name."""
        return self.config["provider_model_name"]
    
    @property
    def conditions(self) -> List[Condition]:
        """Get the conditions list."""
        return self._conditions
    
    @property
    def decision_type(self) -> str:
        """Get the decision type."""
        return self.config["decision_type"]
    
    @property
    def llm_temperature(self) -> float:
        """Get the LLM temperature."""
        return self.config["llm_temperature"]
    
    @property
    def llm_max_tokens(self) -> int:
        """Get the LLM max tokens."""
        return self.config["llm_max_tokens"]