"""
SendTemplateNode for sending WhatsApp templates in flows.
"""

from typing import Optional, Dict, Any, Union

from .base import Node
from kapso.builder.ai.field import AIField


class SendTemplateNode(Node):
    """Node for sending WhatsApp message templates."""
    
    def __init__(
        self,
        id: str,
        whatsapp_config_id: str,
        template_id: str,
        template_params: Optional[Union[Dict[str, str], AIField]] = None,
        provider_model_name: Optional[str] = None
    ):
        config = {
            "whatsapp_config_id": whatsapp_config_id,
            "template_id": template_id
        }
        
        # Build ai_field_config for AI fields
        ai_config = {}
        has_ai_fields = False
        
        # Handle template_params (can be AIField or dict)
        if template_params is not None:
            config["template_params"] = template_params.to_dict() if isinstance(template_params, AIField) else template_params
            if isinstance(template_params, AIField):
                ai_config["template_params"] = template_params.to_config()
                has_ai_fields = True
        
        # Auto-generate ai_field_config if any AI fields are used
        if has_ai_fields:
            config["ai_field_config"] = ai_config
            if not provider_model_name:
                raise ValueError("provider_model_name required when using AIField")
            config["provider_model_name"] = provider_model_name
        elif provider_model_name:
            config["provider_model_name"] = provider_model_name
            
        super().__init__(
            id=id,
            node_type="send_template",
            config=config
        )
    
    @property
    def whatsapp_config_id(self) -> str:
        """Get the WhatsApp config ID."""
        return self.config["whatsapp_config_id"]
    
    @property
    def template_id(self) -> str:
        """Get the template ID."""
        return self.config["template_id"]
    
    @property
    def template_params(self) -> Optional[Union[Dict[str, str], AIField]]:
        """Get the template parameters."""
        params = self.config.get("template_params")
        if isinstance(params, dict) and params == {"$ai": {}}:
            # Reconstruct AIField from ai_field_config if available
            ai_config = self.config.get("ai_field_config", {}).get("template_params", {})
            prompt = ai_config.get("prompt", "")
            return AIField(prompt)
        return params
    
    @property
    def provider_model_name(self) -> Optional[str]:
        """Get the provider model name."""
        return self.config.get("provider_model_name")