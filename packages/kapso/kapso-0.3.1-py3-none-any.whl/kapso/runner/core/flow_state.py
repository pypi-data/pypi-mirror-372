from typing import Annotated, Any, Dict, Optional

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    full_history: Annotated[
        list, add_messages
    ]  # Complete interaction history including LLM reasoning
    conversation: Annotated[list, add_messages]  # Conversation history (what the user sees)
    current_node: Dict[str, Any]  # The current node
    handoff_reason: Optional[str]  # The reason from moving to handoff node
    last_processed_timestamp: Optional[str]  # Track last processed message timestamp (ISO format)
