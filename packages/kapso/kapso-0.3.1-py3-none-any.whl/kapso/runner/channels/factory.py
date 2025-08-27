import logging
from typing import Dict, Type, Any

from kapso.runner.channels.base import BaseChannelAdapter
from kapso.runner.channels.models import MessageChannelType, ChannelMessage

logger = logging.getLogger(__name__)

# Registry of adapter classes
_adapter_registry: Dict[MessageChannelType, Type[BaseChannelAdapter]] = {}
# Cache of configured adapters
_configured_adapters: Dict[MessageChannelType, BaseChannelAdapter] = {}

def register_adapter(channel_type: MessageChannelType,
                     adapter_class: Type[BaseChannelAdapter]) -> None:
    """
    Register an adapter class for a specific channel type.

    Args:
        channel_type: The channel type to register for
        adapter_class: The adapter class to register
    """
    _adapter_registry[channel_type] = adapter_class
    logger.info(f"Registered adapter class for channel: {channel_type}")

def configure_adapter(channel_type: MessageChannelType,
                      config: Dict[str, Any]) -> None:
    """
    Configure and instantiate an adapter for a specific channel type.

    Args:
        channel_type: The channel type to configure
        config: Configuration dictionary for the adapter

    Raises:
        ValueError: If no adapter is registered for the channel type
    """
    if channel_type not in _adapter_registry:
        raise ValueError(f"No adapter registered for channel type: {channel_type}")

    adapter_class = _adapter_registry[channel_type]
    _configured_adapters[channel_type] = adapter_class.from_config(config)
    logger.info(f"Configured adapter for channel: {channel_type}")

def get_adapter(channel_type: MessageChannelType) -> BaseChannelAdapter:
    """
    Get a configured adapter for a specific channel type.

    Args:
        channel_type: The channel type to get an adapter for

    Returns:
        A configured adapter instance

    Raises:
        ValueError: If no adapter is configured for the channel type
    """
    if channel_type not in _configured_adapters:
        raise ValueError(f"No configured adapter for channel type: {channel_type}")

    return _configured_adapters[channel_type]

async def send_message(message: ChannelMessage) -> str:
    """
    Send a message through the appropriate channel adapter.

    Args:
        message: The channel-agnostic message to send

    Returns:
        A string indicating success

    Raises:
        ValueError: If no adapter is configured for the channel type
        ChannelError: Base exception for all channel-related errors
        MessageSendError: If the message fails to send
        ChannelUnavailableError: If the channel service is unavailable
        ChannelAuthenticationError: If authentication fails
        MessageFormatError: If the message format is invalid
    """
    adapter = get_adapter(message.channel_type)
    return await adapter.send_message(message)
