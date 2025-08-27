"""
Utility functions for handling message objects and conversions.
"""

import logging
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    convert_to_openai_messages,
)

# Create a logger for this module
logger = logging.getLogger(__name__)


def recursively_convert_messages_to_openai_format(state_values: Any) -> Any:
    """
    Recursively transform state values by converting message objects to OpenAI format.

    This function traverses the input data structure (dict, list, etc.) and converts
    any arrays containing at least one HumanMessage, AIMessage, or SystemMessage object to
    OpenAI format using convert_to_openai_messages.

    Args:
        state_values: Any data structure that might contain message objects

    Returns:
        A new data structure with message objects converted to OpenAI format
    """
    # Base case: None
    if state_values is None:
        return None

    # Handle dictionaries
    if isinstance(state_values, dict):
        transformed_dict = {}
        for key, value in state_values.items():
            transformed_dict[key] = recursively_convert_messages_to_openai_format(value)
        return transformed_dict

    # Handle lists/arrays
    if isinstance(state_values, list):
        # Check if this is a list containing any message objects
        if state_values and any(
            isinstance(item, (HumanMessage, AIMessage, SystemMessage))
            for item in state_values
            if item is not None
        ):
            # This list contains at least one message object, convert it
            return convert_to_openai_messages(state_values)
        else:
            # Regular list, process each element
            return [recursively_convert_messages_to_openai_format(item) for item in state_values]

    # For all other types (int, str, etc.), return as is
    return state_values
