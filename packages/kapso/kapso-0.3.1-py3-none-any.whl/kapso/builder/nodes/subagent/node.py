"""
SubagentNode implementation for the Kapso SDK.
"""

from dataclasses import dataclass, field
from typing import List

from kapso.builder.nodes.base import Node, NodeType
from kapso.builder.nodes.subagent.tools import SubagentTool


@dataclass
class SubagentNode(Node):
    """
    SubagentNode that can contain multiple tools (webhooks, knowledge bases, MCP servers, WhatsApp templates).

    This node type provides a unified interface for adding various tool types that work together
    within a single node.
    """

    # Override type field to always be SUBAGENT
    type: NodeType = field(default=NodeType.SUBAGENT, init=False)

    # Tools list - can be provided during initialization
    tools: List[SubagentTool] = field(default_factory=list)

    def __post_init__(self):
        """Initialize and validate SubagentNode after dataclass initialization."""
        # Call parent validation
        super().__post_init__()

        # Validate tool name uniqueness if tools exist
        if self.tools:
            tool_names = [tool.name for tool in self.tools]
            if len(tool_names) != len(set(tool_names)):
                raise ValueError("All tools in a SubagentNode must have unique names")

    def add_tool(self, tool: SubagentTool) -> None:
        """
        Add a tool to the subagent node.

        Args:
            tool: The tool to add

        Raises:
            ValueError: If a tool with the same name already exists
        """
        # Check for duplicate names across all tools
        existing_names = {t.name for t in self.tools}
        if tool.name in existing_names:
            raise ValueError(f"Tool with name '{tool.name}' already exists in this SubagentNode")

        self.tools.append(tool)