"""
Package for node type implementations.
"""

from kapso.runner.core.node_types.base import NodeType, NodeTypeRegistry, node_type_registry
from kapso.runner.core.node_types.default_node import DefaultNodeType
from kapso.runner.core.node_types.handoff_node import HandoffNodeType
from kapso.runner.core.node_types.knowledge_base_node import KnowledgeBaseNodeType
from kapso.runner.core.node_types.subagent_node import SubagentNodeType
from kapso.runner.core.node_types.warm_end_node import WarmEndNodeType
from kapso.runner.core.node_types.webhook_node import WebhookNodeType
from kapso.runner.core.node_types.whatsapp_template_node import WhatsappTemplateNodeType

# Register all node types
node_type_registry.register(DefaultNodeType)
node_type_registry.register(WebhookNodeType)
node_type_registry.register(WhatsappTemplateNodeType)
node_type_registry.register(KnowledgeBaseNodeType)
node_type_registry.register(HandoffNodeType)
node_type_registry.register(WarmEndNodeType)
node_type_registry.register(SubagentNodeType)

__all__ = [
    "NodeType",
    "NodeTypeRegistry",
    "node_type_registry",
    "DefaultNodeType",
    "WebhookNodeType",
    "WhatsappTemplateNodeType",
    "KnowledgeBaseNodeType",
    "HandoffNodeType",
    "WarmEndNodeType",
    "SubagentNodeType",
]
