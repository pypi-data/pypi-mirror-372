"""
Definition for the EnterIdleState tool.
"""

from typing import Optional

from pydantic import BaseModel, Field


class EnterIdleState(BaseModel):
    """
    Use this function when you've completed the main task and want to gracefully end the conversation.
    This function sends a message and pauses the execution until the user sends a final reply.
    If no message is provided, then we just enter idle state without sending a message.

    Guidelines:
    - Use this tool at the end of a conversation to allow for a friendly closing.
    - This is specifically for "WarmEndNode" type nodes to provide a more natural conversation ending.

    Examples:
    - EnterIdleState("Thank you for using our service! Is there anything else you'd like to know before we finish?")
    - EnterIdleState("It was great helping you today. Feel free to share any last thoughts before we wrap up.")
    - EnterIdleState()
    """

    message: Optional[str] = Field(
        description="A warm message to send to the user before entering idle state, inviting any final questions or feedback."
    )
