"""
WaitForResponseNode for waiting for user responses in flows.
"""

from typing import Optional

from .base import Node


class WaitForResponseNode(Node):
    """Node for waiting for user responses with optional timeout."""
    
    def __init__(
        self,
        id: str,
        timeout_seconds: Optional[int] = None
    ):
        config = {}
        
        if timeout_seconds:
            config["timeout_seconds"] = timeout_seconds
            
        super().__init__(
            id=id,
            node_type="wait_for_response",
            config=config
        )