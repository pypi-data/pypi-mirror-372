"""
Utilities for optimizing message caching and token usage.
"""

import copy
import logging
from typing import List

from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


def add_cache_control_to_message(message: BaseMessage) -> BaseMessage:
    """
    Add cache_control to a message for Anthropic caching.

    Args:
        message: The message to add cache control to

    Returns:
        A copy of the message with cache_control added
    """
    # Make a copy to avoid modifying the original
    message_copy = copy.deepcopy(message)

    # Handle different content formats
    if isinstance(message_copy.content, list):
        if len(message_copy.content) > 0:
            # Add cache_control to the last block
            last_block = message_copy.content[-1]
            if isinstance(last_block, dict):
                last_block["cache_control"] = {"type": "ephemeral"}
    # If content is a string, convert to a block
    elif isinstance(message_copy.content, str):
        message_copy.content = [
            {"type": "text", "text": message_copy.content, "cache_control": {"type": "ephemeral"}}
        ]

    return message_copy


def optimize_messages_for_provider(
    messages: List[BaseMessage], provider: str = ""
) -> List[BaseMessage]:
    """
    Optimize a list of messages for a specific provider.
    For Anthropic, adds cache_control to the last message.

    Args:
        messages: List of messages to optimize
        provider: LLM provider name

    Returns:
        Optimized list of messages
    """
    if not messages or provider != "Anthropic":
        return messages

    # Copy all messages except the last one
    optimized_messages = messages[:-1].copy()

    # Add the last message with cache control
    if messages:
        optimized_messages.append(add_cache_control_to_message(messages[-1]))

    return optimized_messages
