"""
Kapso SDK package.

Provides a clean API for building conversational agents with Kapso.
"""

# Core Agent class
from kapso.builder.agent.agent import Agent

# Node factory functions
from kapso.builder.nodes.factory import (
    DefaultNode,
    WebhookNode,
    KnowledgeBaseNode,
    HandoffNode,
    WarmEndNode,
    WhatsAppTemplateNode,
    create_subagent_node,
)

# SubagentNode and tools
from kapso.builder.nodes.subagent.node import SubagentNode
from kapso.builder.nodes.subagent.tools import (
    SubagentTool,
    WebhookTool,
    KnowledgeBaseTool,
    McpServerTool,
    WhatsappTemplateTool,
    JmespathQuery,
)

# Edge creation
from kapso.builder.edges.edge import Edge, create_edge

# Constants
from kapso.builder.agent.constants import START_NODE, END_NODE


# Base classes and enums (for advanced users)
from kapso.builder.nodes.base import (
    Node,
    NodeType,
    WebhookConfig,
    KnowledgeBaseConfig,
    HandoffConfig,
    WarmEndConfig,
    WhatsAppTemplateConfig,
)

__all__ = [
    # Core
    "Agent",
    
    # Node factory functions
    "DefaultNode",
    "WebhookNode",
    "KnowledgeBaseNode",
    "HandoffNode",
    "WarmEndNode",
    "WhatsAppTemplateNode",
    "create_subagent_node",
    
    # SubagentNode and tools
    "SubagentNode",
    "SubagentTool",
    "WebhookTool",
    "KnowledgeBaseTool",
    "McpServerTool",
    "WhatsappTemplateTool",
    "JmespathQuery",
    
    # Edges
    "Edge",
    "create_edge",
    
    # Constants
    "START_NODE",
    "END_NODE",
    
    # Base classes and enums
    "Node",
    "NodeType",
    "WebhookConfig",
    "KnowledgeBaseConfig",
    "HandoffConfig",
    "WarmEndConfig",
    "WhatsAppTemplateConfig",
]
