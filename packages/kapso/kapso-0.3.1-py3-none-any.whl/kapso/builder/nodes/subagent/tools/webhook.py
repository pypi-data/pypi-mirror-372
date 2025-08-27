"""
Webhook tool implementation for SubagentNode.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from kapso.builder.nodes.subagent.tools.base import SubagentTool


@dataclass(kw_only=True)
class WebhookTool(SubagentTool):
    """Webhook tool for making HTTP requests."""
    
    url: str
    http_method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    body_schema: Optional[Dict[str, Any]] = None
    mock_response: Optional[Dict[str, Any]] = None
    mock_response_enabled: bool = False
    jmespath_query: Optional[str] = None
    
    def __post_init__(self):
        """Validate webhook tool after initialization."""
        super().__post_init__()
        
        if not self.url:
            raise ValueError(f"Webhook tool '{self.name}' must have a URL")
            
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
        if self.http_method.upper() not in valid_methods:
            raise ValueError(
                f"Invalid HTTP method '{self.http_method}' for webhook tool '{self.name}'. "
                f"Must be one of: {', '.join(valid_methods)}"
            )
    
    def tool_type(self) -> str:
        """Return the tool type for serialization."""
        return "webhook"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        import json
        
        # Convert complex fields to JSON strings for Rails compatibility
        result = {
            "name": self.name,
            "url": self.url,
            "http_method": self.http_method.upper(),
            "headers": json.dumps(self.headers) if self.headers else "{}",
            "body": json.dumps(self.body) if self.body else "{}",
            "body_schema": json.dumps(self.body_schema) if self.body_schema else None,
            "mock_response": json.dumps(self.mock_response) if self.mock_response else "{}",
            "mock_response_enabled": self.mock_response_enabled,
            "description": self.description,
            "jmespath_query": self.jmespath_query
        }
        
        # Remove None values to avoid sending null body_schema
        return {k: v for k, v in result.items() if v is not None}