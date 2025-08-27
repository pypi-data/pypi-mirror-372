"""
Base node definitions for the Kapso SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

from kapso.builder.agent.constants import START_NODE, END_NODE


class NodeType(str, Enum):
    """Enum for node types."""
    DEFAULT = "DefaultNode"
    WEBHOOK = "WebhookNode"
    KNOWLEDGE_BASE = "KnowledgeBaseNode"
    HANDOFF = "HandoffNode"
    WARM_END = "WarmEndNode"
    SUBAGENT = "SubagentNode"
    WHATSAPP_TEMPLATE = "WhatsappTemplateNode"


@dataclass
class WebhookConfig:
    """Configuration for webhook nodes."""
    url: str
    http_method: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    body_schema: Optional[Dict[str, Any]] = None  # JSON Schema for request body validation
    jmespath_query: Optional[str] = None  # JMESPath query for response filtering
    mock_response: Optional[Dict[str, Any]] = None
    mock_response_enabled: bool = False


@dataclass
class KnowledgeBaseConfig:
    """Configuration for knowledge base nodes."""
    knowledge_base_text: Optional[str] = None
    knowledge_base_file: Optional[str] = None


@dataclass
class WarmEndConfig:
    """Configuration for warm end nodes."""
    timeout_minutes: int


@dataclass
class HandoffConfig:
    """Configuration for handoff nodes."""
    pass


@dataclass
class WhatsAppTemplateConfig:
    """Configuration for WhatsApp template nodes."""
    template_name: str
    phone_number: str
    template_parameters: Dict[str, str] = field(default_factory=dict)
    wait_for_response: bool = False
    whatsapp_config_id: Optional[str] = None
    whatsapp_template_id: Optional[str] = None


@dataclass
class Node:
    """Base node in agent graph."""
    name: str
    type: NodeType
    prompt: Optional[str] = None
    global_: bool = False
    global_condition: Optional[str] = None
    
    webhook: Optional[WebhookConfig] = None
    knowledge_base: Optional[KnowledgeBaseConfig] = None
    warm_end: Optional[WarmEndConfig] = None
    handoff: Optional[HandoffConfig] = None
    whatsapp_template: Optional[WhatsAppTemplateConfig] = None
    
    def __post_init__(self):
        """Validate node properties after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Invalid node name: {self.name}. Node name must be a non-empty string.")
            
        if self.name != START_NODE and self.name != END_NODE:
            if not all(c.isalnum() or c == '_' for c in self.name):
                raise ValueError(
                    f"Invalid node name: {self.name}. Node names can only use letters, numbers, or underscores."
                )
        
        if self.global_ and not self.global_condition:
            raise ValueError(f"Global nodes must have a global condition: {self.name}")
        
        if not self.global_ and self.global_condition:
            raise ValueError(f"Non-global nodes cannot have a global condition: {self.name}")
        
        if self.type == NodeType.WEBHOOK and not self.webhook:
            raise ValueError(f"WebhookNode requires webhook configuration: {self.name}")
            
        if self.type == NodeType.KNOWLEDGE_BASE and not self.knowledge_base:
            raise ValueError(f"KnowledgeBaseNode requires knowledge_base configuration: {self.name}")
            
        if self.type == NodeType.WARM_END and not self.warm_end:
            raise ValueError(f"WarmEndNode requires warm_end configuration: {self.name}")
            
        if self.type == NodeType.HANDOFF and not self.handoff:
            raise ValueError(f"HandoffNode requires handoff configuration: {self.name}")
            
        if self.type == NodeType.WHATSAPP_TEMPLATE and not self.whatsapp_template:
            raise ValueError(f"WhatsappTemplateNode requires whatsapp_template configuration: {self.name}")
