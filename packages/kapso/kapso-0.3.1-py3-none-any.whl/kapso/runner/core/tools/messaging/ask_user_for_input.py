"""
Definition for the AskUserForInput tool.
"""

from pydantic import BaseModel, Field


class AskUserForInput(BaseModel):
    """
    Use this function when you need to ask something to the user.
    This function pauses the execution until the user answers. The message sent must end with
    a single, clear question mark '?' explicitly requesting the user's input or decision.
    Never use this function for notifications or messages that do not require user input.

    Guidelines:
    - Use this tool as the final call since it halts execution until a reply is received.
    - You must include a message when calling this tool.

    Examples:
    - AskUserForInput("Hello! How can I help you today?")
    - AskUserForInput("Choose an option: 1) Pizza 2) Burger?")
    - AskUserForInput("What time works for your appointment?")

    Attributes:
        message (str). The question you want the user to answer. The text must end with a question mark '?'.
    """

    message: str = Field(
        description="The clear and explicit question you want the user to answer. The text must end with a question mark '?'."
    )
