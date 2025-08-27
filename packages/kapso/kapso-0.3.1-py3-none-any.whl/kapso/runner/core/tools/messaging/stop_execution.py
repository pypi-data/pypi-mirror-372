"""
Definition for the StopExecution tool.
"""

from pydantic import BaseModel, Field


class StopExecution(BaseModel):
    """
    Internal tool used to handle stop signal interruptions during agent execution.
    This tool is automatically triggered when a stop signal is detected.
    It gracefully terminates the execution and performs cleanup.
    
    This tool should not be used directly by agents - it's automatically injected when needed.
    """
    reason: str = Field(
        default="Stop signal received",
        description="The reason for stopping the execution"
    )