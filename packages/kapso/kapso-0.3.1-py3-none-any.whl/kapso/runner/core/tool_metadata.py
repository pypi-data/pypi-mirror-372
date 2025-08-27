from typing import Any, Dict, Optional, List
from dataclasses import dataclass
@dataclass
class ToolMetadata:
    """
    Metadata for tools, including information about their origin and type.
    
    This metadata helps with tool identification and debugging.
    """
    
    name: str
    is_dynamic: bool
    node_type: str
    requires_interrupt: bool = False
    interrupt_handler: Optional[str] = None
    node_name: Optional[str] = None
    creation_context: Optional[Dict[str, Any]] = None
    is_mcp_tool: bool = False  # New field for MCP tools
    mcp_spec: Optional[Dict[str, Any]] = None  # New field for MCP tools
    jmespath_queries: Optional[List[Dict[str, str]]] = None  # List of objects with tool_name and jmespath_query
    
    def __repr__(self) -> str:
        """String representation of tool metadata."""
        return (
            f"ToolMetadata(name='{self.name}', is_dynamic={self.is_dynamic}, "
            f"node_type='{self.node_type}', requires_interrupt={self.requires_interrupt})"
        )

def attach_metadata_to_tool(tool: Any, metadata: ToolMetadata) -> Any:
    """
    Attach metadata to a tool.
    
    Args:
        tool: The tool to attach metadata to
        metadata: The metadata to attach
        
    Returns:
        The tool with metadata attached
    """
    # Add metadata as a property of the tool
    tool.metadata = metadata
    return tool