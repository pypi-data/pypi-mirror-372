"""
SendInteractiveNode for sending interactive WhatsApp messages in flows.
"""

from typing import Union, Optional, Dict, Any

from .base import Node
from kapso.builder.ai.field import AIField


class SendInteractiveNode(Node):
    """Node for sending interactive WhatsApp messages (lists, buttons)."""
    
    def __init__(
        self,
        id: str,
        whatsapp_config_id: str,
        interactive_type: str,  # "list" or "button"
        body_text: Union[str, AIField],
        header_text: Optional[Union[str, AIField]] = None,
        footer_text: Optional[Union[str, AIField]] = None,
        provider_model_name: Optional[str] = None
    ):
        config = {
            "whatsapp_config_id": whatsapp_config_id,
            "interactive_type": interactive_type,
            "body_text": body_text.to_dict() if isinstance(body_text, AIField) else body_text
        }
        
        # Build ai_field_config for all AI fields
        ai_config = {}
        has_ai_fields = False
        
        # Handle body_text AI field
        if isinstance(body_text, AIField):
            ai_config["body_text"] = body_text.to_config()
            has_ai_fields = True
        
        if header_text is not None:
            config["header_text"] = header_text.to_dict() if isinstance(header_text, AIField) else header_text
            if isinstance(header_text, AIField):
                ai_config["header_text"] = header_text.to_config()
                has_ai_fields = True
            
        if footer_text is not None:
            config["footer_text"] = footer_text.to_dict() if isinstance(footer_text, AIField) else footer_text
            if isinstance(footer_text, AIField):
                ai_config["footer_text"] = footer_text.to_config()
                has_ai_fields = True
        
        # Auto-generate ai_field_config if any AI fields are used
        if has_ai_fields:
            config["ai_field_config"] = ai_config
            if not provider_model_name:
                raise ValueError("provider_model_name required when using AIField")
            
        if provider_model_name:
            config["provider_model_name"] = provider_model_name
        
        # Store original values for property access
        self._body_text = body_text
        self._header_text = header_text
        self._footer_text = footer_text
            
        super().__init__(
            id=id,
            node_type="send_interactive",
            config=config
        )
    
    @property
    def whatsapp_config_id(self) -> str:
        """Get the WhatsApp config ID."""
        return self.config["whatsapp_config_id"]
    
    @property
    def interactive_type(self) -> str:
        """Get the interactive type."""
        return self.config["interactive_type"]
    
    @property
    def body_text(self) -> Union[str, AIField]:
        """Get the body text."""
        return self._body_text
    
    @property
    def header_text(self) -> Optional[Union[str, AIField]]:
        """Get the header text."""
        return self._header_text
    
    @property
    def footer_text(self) -> Optional[Union[str, AIField]]:
        """Get the footer text."""
        return self._footer_text
    
    @property
    def provider_model_name(self) -> Optional[str]:
        """Get the provider model name."""
        return self.config.get("provider_model_name")
    
    @property
    def ai_field_config(self) -> Optional[Dict[str, Any]]:
        """Get the AI field configuration."""
        return self.config.get("ai_field_config")