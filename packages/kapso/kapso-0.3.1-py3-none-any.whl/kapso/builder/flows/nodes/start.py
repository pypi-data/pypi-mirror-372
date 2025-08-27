"""
StartNode for flow entry points.
"""

from typing import Optional

from .base import Node


class StartNode(Node):
    """Node representing the starting point of a flow."""
    
    def __init__(
        self,
        id: str
    ):
        # Start nodes have no configuration
        config = {}
            
        super().__init__(
            id=id,
            node_type="start",
            config=config
        )