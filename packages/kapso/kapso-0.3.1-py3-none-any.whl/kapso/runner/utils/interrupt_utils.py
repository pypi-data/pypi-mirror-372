"""
Utilities for handling interrupts in conversation state.
"""

import logging
from typing import Dict, Any, Optional

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

# Create a logger for this module
logger = logging.getLogger(__name__)

async def is_redundant_retry_input(
    graph: CompiledStateGraph, config: Dict[str, Any], resume_interrupt_id: Optional[str], is_new_conversation: bool
) -> bool:
    """
    Checks if the input for a retried message is redundant based on checkpoint state.
    Uses LangGraph's interrupt tracking features for precise detection.

    Args:
        graph: The compiled LangGraph application.
        config: The configuration for the current thread.
        resume_interrupt_id: The interrupt ID we're attempting to resume.

    Returns:
        bool: True if the input is redundant, False otherwise.
    """
    thread_id = config["configurable"]["thread_id"]
    logger.info(f"Performing retry check for thread {thread_id}")

    try:
        # Get the current state from the checkpointer
        state = await graph.aget_state(config)

        # If we're attempting to resume an interrupt, check if it's still active
        if resume_interrupt_id:
            # If the interrupt is NO LONGER active, the previous attempt must have
            # successfully processed it already, so this retry is redundant
            if not is_interrupt_active(state, resume_interrupt_id):
                logger.info(
                    f"Interrupt {resume_interrupt_id} is no longer active in thread {thread_id}, "
                    "treating as redundant retry"
                )
                return True

        if is_new_conversation:
            # If this is a new conversation, we need to check if there is an item in the conversation history
            if (len(state.values.get('conversation', [])) > 0):
                return True

        return False

    except Exception as e:
        logger.error(f"Error checking for redundant retry: {str(e)}", exc_info=True)
        # Default to non-redundant if we cannot determine
        return False

def is_interrupt_active(state: StateSnapshot, interrupt_id: str) -> bool:
    """
    Check if a specific interrupt is active in the current state.

    Args:
        state: The current state snapshot
        interrupt_id: The ID of the interrupt to check

    Returns:
        bool: True if the interrupt is active, False otherwise
    """
    if not hasattr(state, "interrupts"):
        return False

    for interrupt in state.interrupts:
        if interrupt.interrupt_id == interrupt_id:
            return True

    return False