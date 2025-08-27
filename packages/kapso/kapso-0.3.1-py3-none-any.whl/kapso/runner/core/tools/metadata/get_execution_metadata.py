"""
Definition for the get_execution_metadata tool.
"""

from typing import Dict, Any
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig


@tool
def get_execution_metadata(config: RunnableConfig) -> Dict[str, Any]:
    """
    Get the execution metadata for the current agent execution.
    
    This tool provides access to contextual information about the current execution,
    including agent details, conversation identifiers, and contact information.
    
    Returns:
        Dict containing:
        - agent_id: The ID of the agent being executed
        - agent_execution_id: The ID of the current agent execution (if available)
        - contact_information: Details about the contact (phone number, name, etc.)
        - whatsapp_conversation_id: The ID of the WhatsApp conversation (if applicable)
    """
    configurable = config.get("configurable", {})
    execution_metadata = configurable.get("execution_metadata", {})
    
    # Return the execution metadata or empty dict if not available
    return execution_metadata or {
        "agent_id": None,
        "agent_execution_id": None,
        "contact_information": None,
        "whatsapp_conversation_id": None
    }