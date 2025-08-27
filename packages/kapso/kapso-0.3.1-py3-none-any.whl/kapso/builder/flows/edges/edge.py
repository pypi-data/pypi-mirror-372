"""
Edge class for flows.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Edge:
    """Edge connecting nodes in a flow."""
    
    source: str  # Node ID
    target: str  # Node ID
    label: str = "next"
    flow_condition_id: Optional[str] = None  # Set by backend for decide nodes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to backend compatible format."""
        result = {
            "source": self.source,
            "target": self.target,
            "label": self.label
        }
        if self.flow_condition_id:
            result["flow_condition_id"] = self.flow_condition_id
        return result