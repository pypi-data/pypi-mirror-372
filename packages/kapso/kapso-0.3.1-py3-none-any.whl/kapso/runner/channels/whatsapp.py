import logging
from typing import Dict, Any, Optional, ClassVar

from kapso.runner.channels.base import BaseChannelAdapter
from kapso.runner.channels.models import ChannelMessage

logger = logging.getLogger(__name__)

class WhatsAppAdapter(BaseChannelAdapter):
    """
    Adapter for WhatsApp messaging.

    This is an empty implementation. Use a custom adapter for actual WhatsApp messaging.
    """

    DEFAULT_API_URL: ClassVar[str] = "http://localhost:3000"

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        self.api_url = api_url
        self.api_key = api_key

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'WhatsAppAdapter':
        """Create an adapter instance from a configuration dict."""
        api_url = config.get("api_url", cls.DEFAULT_API_URL)
        api_key = config.get("api_key")
        instance = cls(api_url=api_url, api_key=api_key)
        
        # Set mock mode if specified in config
        if config.get("mock", False):
            instance._mock = True
            
        return instance

    async def send_message(self, message: ChannelMessage) -> str:
        """
        Send a message via WhatsApp.

        Note: This is an empty implementation.
        Implement a custom adapter for actual WhatsApp messaging.
        """
        # Check if we're in mock/test mode
        if hasattr(self, '_mock') and self._mock:
            logger.debug(f"Mock WhatsApp message sent to {message.recipient_id}: {message.content}")
            return f"Mock message sent: {message.content}"
        
        raise NotImplementedError(
            "WhatsAppAdapter is an empty implementation. "
            "Use a custom adapter for actual WhatsApp messaging."
        )