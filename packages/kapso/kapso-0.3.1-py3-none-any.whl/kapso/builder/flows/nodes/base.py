"""
Base Node class for flows.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Node:
    """Base class for all flow nodes."""
    
    id: str  # Format: {node_type}_{timestamp}
    node_type: str  # e.g., "send_text", "wait_for_response", "decide"
    config: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to backend compatible format."""
        return {
            "id": self.id,
            "type": "flow-node",
            "data": {
                "node_type": self.node_type,  # Keep snake_case - Rails handles conversion
                "config": self.config
            }
        }
    
