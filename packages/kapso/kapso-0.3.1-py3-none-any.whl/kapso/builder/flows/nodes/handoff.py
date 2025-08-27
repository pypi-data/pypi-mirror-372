"""
HandoffNode for transferring conversations to human agents.
"""

from .base import Node


class HandoffNode(Node):
    """Node representing a handoff to a human agent."""
    
    def __init__(
        self,
        id: str
    ):
        # Handoff nodes have no configuration - they only trigger the handoff
        config = {}
            
        super().__init__(
            id=id,
            node_type="handoff",
            config=config
        )