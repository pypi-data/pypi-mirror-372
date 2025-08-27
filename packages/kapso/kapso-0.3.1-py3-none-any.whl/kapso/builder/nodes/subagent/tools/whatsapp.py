"""
WhatsApp template tool implementation for SubagentNode.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from kapso.builder.nodes.subagent.tools.base import SubagentTool


@dataclass(kw_only=True)
class WhatsappTemplateTool(SubagentTool):
    """WhatsApp template tool for sending structured messages."""

    template_name: str
    phone_number: str
    template_parameters: Optional[Dict[str, str]] = None
    whatsapp_config_id: Optional[str] = None
    whatsapp_template_id: Optional[str] = None
    wait_for_response: bool = False

    def __post_init__(self):
        """Validate WhatsApp template tool after initialization."""
        super().__post_init__()

        if not self.template_name:
            raise ValueError(f"WhatsApp template tool '{self.name}' must have a template name")

        if not self.phone_number:
            raise ValueError(f"WhatsApp template tool '{self.name}' must have a phone number")

    def tool_type(self) -> str:
        """Return the tool type for serialization."""
        return "whatsapp_template"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "template_name": self.template_name,
            "phone_number": self.phone_number,
            "template_parameters": self.template_parameters or {},
            "whatsapp_config_id": self.whatsapp_config_id,
            "whatsapp_template_id": self.whatsapp_template_id,
            "wait_for_response": self.wait_for_response,
            "description": self.description
        }