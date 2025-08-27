"""
Base class for SubagentNode tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(kw_only=True)
class SubagentTool(ABC):
    """Abstract base class for all subagent tools."""
    
    name: str
    description: str = ""
    
    def __post_init__(self):
        """Validate tool after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Invalid tool name: {self.name}. Tool name must be a non-empty string.")
            
        if not all(c.isalnum() or c == '_' for c in self.name):
            raise ValueError(
                f"Invalid tool name: {self.name}. Tool names can only use letters, numbers, or underscores."
            )
    
    @abstractmethod
    def tool_type(self) -> str:
        """Return the tool type for serialization."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        pass