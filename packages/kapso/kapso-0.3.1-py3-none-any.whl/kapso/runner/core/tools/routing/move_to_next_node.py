"""
Definition for the MoveToNextNode tool.
"""

from pydantic import BaseModel, Field


class MoveToNextNode(BaseModel):
    """ "
    Use this function when you must move to the next node.
    This function must be used if the current node instructions are completed.
    The next node must be decided based on the edge conditions.

    Guidelines:
    - If you use this tool, the process will move to the next node.
    - If you use this tool, it must be the last tool called in the list.
    """

    next_node: str = Field(description="The name of the next node to move to.")
    reason: str = Field(description="The reason for moving to the selected next node specifically.")
