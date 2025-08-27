"""
Definition for the Abort tool.
"""

from pydantic import BaseModel, Field


class Abort(BaseModel):
    """
    Immediately ends the conversation by transitioning to the END node.
    Use this tool when multiple attempts to get valid input have been unsuccessful.

    Guidelines:
    - Use after making multiple attempts to get valid input without success
    - Use when the user is unresponsive or repeatedly fails to provide necessary information
    - This will terminate the current conversation flow

    Examples:
    - After asking for an email address three times with invalid responses
    - When a user has stopped responding after multiple prompts
    - When required information cannot be obtained despite repeated attempts
    - When you have repeated the same message multiple times and the user has not responded

    Attributes:
        reason (str): A brief explanation of why the conversation is being aborted.
    """

    reason: str = Field(
        description="A brief explanation of why the conversation is being aborted (e.g., 'User unresponsive after multiple attempts')."
    )
