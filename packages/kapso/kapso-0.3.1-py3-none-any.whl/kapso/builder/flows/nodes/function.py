"""
FunctionNode for executing custom JavaScript functions in flows.
"""

from typing import Optional

from .base import Node


class FunctionNode(Node):
    """Node for executing deployed custom functions."""
    
    def __init__(
        self,
        id: str,
        function_id: str,
        save_response_to: Optional[str] = None
    ):
        config = {
            "function_id": function_id
        }
        
        if save_response_to:
            config["save_response_to"] = save_response_to
            
        super().__init__(
            id=id,
            node_type="function",
            config=config
        )
    
    @property
    def function_id(self) -> str:
        """Get the function ID."""
        return self.config["function_id"]
    
    @property
    def save_response_to(self) -> Optional[str]:
        """Get the response save location."""
        return self.config.get("save_response_to")