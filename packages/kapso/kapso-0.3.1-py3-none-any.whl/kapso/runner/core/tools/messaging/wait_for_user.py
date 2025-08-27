"""
Definition for the WaitForUser tool (v2 agents).
"""

from pydantic import BaseModel


class WaitForUser(BaseModel):
    """
    Use this when you need the user to respond before continuing.
    Your message has already been sent. This just pauses to wait for their reply.
    
    Examples:
    - After asking "What would you like help with?" → WaitForUser()
    - After saying "Please tell me more about your issue" → WaitForUser()
    - After providing options and asking for choice → WaitForUser()
    
    DO NOT use this when:
    - You're providing information and don't need a response
    - The conversation is complete and no response is expected
    """
    pass  # No parameters - intentionally simple