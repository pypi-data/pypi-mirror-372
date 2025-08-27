"""
Updated utility functions shared across flow modules.
"""

import logging

# For future regex needs
# import re
from typing import Any, List, Optional

# Create a logger for this module
logger = logging.getLogger(__name__)


def get_next_pending_tool_call(
    full_history, tool_call_name: Optional[str] = None, processed_ids: Optional[List[str]] = None
):
    """
    Find the next pending tool call that hasn't been responded to yet.

    Args:
        full_history: The complete conversation history
        tool_call_name: Optional name of the tool call to filter by
        processed_ids: Optional list of tool call IDs that have already been processed

    Returns:
        The next pending tool call or None if all tool calls have been responded to
    """
    # Initialize processed_ids if not provided
    if processed_ids is None:
        processed_ids = []

    # Only log essential information about what we're looking for
    if tool_call_name:
        logger.debug("Checking for pending tool calls with name: %s", tool_call_name)
    else:
        logger.debug("Checking for any pending tool calls")

    # Find the last assistant message
    last_assistant_message = None
    for i, message in enumerate(reversed(full_history)):
        if hasattr(message, "type") and message.type == "ai":
            last_assistant_message = message
            break

    if not last_assistant_message:
        logger.debug("No assistant message found in history")
        return None

    if not hasattr(last_assistant_message, "tool_calls"):
        logger.debug("Last assistant message has no tool_calls")
        return None

    # Get tool calls from the last assistant message
    tool_calls = last_assistant_message.tool_calls
    if not tool_calls:
        logger.debug("No tool calls found in last assistant message")
        return None

    # Check if each tool call has a corresponding tool response
    for tool_call in tool_calls:
        # Skip if we're filtering by name and this doesn't match
        if tool_call_name and tool_call["name"] != tool_call_name:
            continue

        # Skip if this tool call ID has already been processed
        tool_call_id = tool_call["id"]
        if tool_call_id in processed_ids:
            continue

        has_response = False

        for message in full_history:
            if (
                hasattr(message, "tool_call_id")
                and message.tool_call_id == tool_call_id
                and hasattr(message, "type")
                and message.type == "tool"
            ):
                has_response = True
                break

        if not has_response:
            logger.info(f"PENDING_TOOL: tool={tool_call['name']}, id={tool_call_id}")
            logger.info("Found pending tool call: %s with id: %s", tool_call["name"], tool_call_id)
            return tool_call

    logger.debug(
        "All tool calls have responses"
        + (" for tool name: " + tool_call_name if tool_call_name else "")
    )
    return None


def is_interrupt_active(state_snapshot: Any, interrupt_id_to_check: Optional[str]) -> bool:
    """
    Check if a specific interrupt is still active in the state.

    Args:
        state_snapshot: The StateSnapshot object from LangGraph
        interrupt_id_to_check: The interrupt ID to check for

    Returns:
        bool: True if the interrupt is active, False otherwise
    """
    if not interrupt_id_to_check:
        return False

    # Access the 'interrupts' property of the StateSnapshot (new in LangGraph update)
    active_interrupts = getattr(state_snapshot, "interrupts", [])

    for interrupt in active_interrupts:
        if interrupt.interrupt_id == interrupt_id_to_check:
            logger.debug(f"Found active interrupt with ID: {interrupt_id_to_check}")
            return True

    logger.debug(f"No active interrupt found with ID: {interrupt_id_to_check}")
    return False
