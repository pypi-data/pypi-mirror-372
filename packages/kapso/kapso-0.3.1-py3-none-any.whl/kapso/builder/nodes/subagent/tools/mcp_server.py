"""
MCP server tool implementation for SubagentNode.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

from kapso.builder.nodes.subagent.tools.base import SubagentTool


@dataclass
class JmespathQuery:
    """Structure for JMESPath queries used by MCP servers."""
    
    tool_name: str
    jmespath_query: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            "tool_name": self.tool_name,
            "jmespath_query": self.jmespath_query
        }


@dataclass(kw_only=True)
class McpServerTool(SubagentTool):
    """MCP server tool for connecting to Model Context Protocol servers."""
    
    url: str
    transport_kind: Literal["streamable_http", "sse"] = "streamable_http"
    jmespath_queries: List[JmespathQuery] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate MCP server tool after initialization."""
        super().__post_init__()
        
        if not self.url:
            raise ValueError(f"MCP server tool '{self.name}' must have a URL")
            
        if self.transport_kind not in ["streamable_http", "sse"]:
            raise ValueError(
                f"Invalid transport kind '{self.transport_kind}' for MCP server tool '{self.name}'. "
                "Must be either 'streamable_http' or 'sse'"
            )
    
    def tool_type(self) -> str:
        """Return the tool type for serialization."""
        return "mcp_server"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "url": self.url,
            "transport_kind": self.transport_kind,
            "jmespath_queries": [q if isinstance(q, dict) else q.to_dict() for q in self.jmespath_queries],
            "description": self.description
        }