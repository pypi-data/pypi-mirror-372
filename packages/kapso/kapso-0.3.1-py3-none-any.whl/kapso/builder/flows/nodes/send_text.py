"""
SendTextNode for sending text messages in flows.
"""

from typing import Union, Optional, Dict, Any

from .base import Node
from kapso.builder.ai.field import AIField


class SendTextNode(Node):
    """Node for sending text messages via WhatsApp."""
    
    def __init__(
        self,
        id: str,
        whatsapp_config_id: str,
        message: Union[str, AIField],
        provider_model_name: Optional[str] = None
    ):
        config = {
            "whatsapp_config_id": whatsapp_config_id,
            "message": message.to_dict() if isinstance(message, AIField) else message
        }
        
        # Auto-generate ai_field_config if AIField is used
        if isinstance(message, AIField):
            config["ai_field_config"] = {"message": message.to_config()}
            if not provider_model_name:
                raise ValueError("provider_model_name required when using AIField")
        
        if provider_model_name:
            config["provider_model_name"] = provider_model_name
        
        # Store original message value for property access
        self._message = message
            
        super().__init__(
            id=id,
            node_type="send_text",
            config=config
        )
    
    @property
    def whatsapp_config_id(self) -> str:
        """Get the WhatsApp config ID."""
        return self.config["whatsapp_config_id"]
    
    @property
    def message(self) -> Union[str, AIField]:
        """Get the message value."""
        return self._message
    
    @property
    def provider_model_name(self) -> Optional[str]:
        """Get the provider model name."""
        return self.config.get("provider_model_name")
    
    @property
    def ai_field_config(self) -> Optional[Dict[str, Any]]:
        """Get the AI field configuration."""
        return self.config.get("ai_field_config")