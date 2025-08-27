"""
Schemas for runner messages.
"""

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field, validator

class MessagePayload(BaseModel):
    """
    Model for structured message payloads.
    Supports user input text and structured data payloads.
    """
    type: Literal["user_input", "payload"] = Field(..., description="Message type: user_input or payload")
    content: Dict[str, Any] = Field(..., description="Message content as a dictionary")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional message metadata")

    @validator('content')
    def content_must_be_dict(cls, v):
        if not isinstance(v, dict):
            raise ValueError('content must be a dictionary')
        return v

class AgentInvocationRequest(BaseModel):
    """
    Model for agent invocation requests received via runner.
    This should match the structure of ConversationRequest but with additional
    fields specific to runner communication.
    """

    graph: Dict[str, Any] = Field(..., description="The graph definition")
    thread_id: Optional[str] = Field(None, description="The thread ID")
    message: Optional[MessagePayload] = Field(None, description="The message payload")
    is_new_conversation: Optional[bool] = Field(
        False, description="Whether this is a new conversation"
    )
    phone_number: Optional[str] = Field(None, description="DEPRECATED: The phone number (use contact_information)")
    contact_information: Optional[Dict[str, Any]] = Field(
        None, description="Contact information including phone number, profile name, and metadata"
    )
    correlation_id: Optional[str] = Field(
        None, description="Correlation ID for tracking the request"
    )
    test_mode: Optional[bool] = Field(
        False, description="Whether to run in test mode (no WhatsApp messages)"
    )
    agent_prompt: Optional[str] = Field(None, description="The system prompt for the agent")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="The LLM configuration")
    last_interrupt_tool_call_id: Optional[str] = Field(None, description="The last tool call ID")
    resume_interrupt_id: Optional[str] = Field(None, description="The interrupt ID to resume")
    agent_version: Optional[int] = Field(None, description="The agent engine version (1 or 2)")


class AgentResultResponse(BaseModel):
    """
    Model for agent result responses sent via runner.
    This should match the structure of ConversationResponse but with additional
    fields specific to runner communication.
    """

    status: str = Field(..., description="The status of the operation")
    thread_id: Optional[str] = Field(None, description="The thread ID")
    state: Optional[Dict[str, Any]] = Field(None, description="The state of the conversation")
    correlation_id: Optional[str] = Field(
        None, description="Correlation ID for tracking the request"
    )
    interrupt_tool_call: Optional[Dict[str, Any]] = Field(
        None, description="The interrupt tool call"
    )
    active_interrupts: Optional[List[Dict[str, Any]]] = Field(
        None, description="The active interrupts"
    )


class TestCase(BaseModel):
    """Model for a test case."""

    id: str = Field(..., description="The test case ID")
    name: str = Field(..., description="The test case name")
    script: str = Field(..., description="The test script with user interaction instructions")
    rubric: str = Field(..., description="The evaluation rubric for scoring the conversation")


class AgentTestRequest(BaseModel):
    """
    Model for agent test requests received via runner.
    """

    graph: Dict[str, Any] = Field(..., description="The graph definition")
    thread_id: Optional[str] = Field(None, description="The thread ID")
    test_case: TestCase = Field(..., description="The test case details")
    phone_number: Optional[str] = Field(None, description="DEPRECATED: The phone number (use contact_information)")
    contact_information: Optional[Dict[str, Any]] = Field(
        None, description="Contact information including phone number, profile name, and metadata"
    )
    agent_prompt: Optional[str] = Field(None, description="The system prompt for the agent")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="The LLM configuration")
    judge_llm_config: Optional[Dict[str, Any]] = Field(
        None, description="The LLM configuration for the judge"
    )
    agent_version: Optional[int] = Field(None, description="The agent engine version (1 or 2)")


class AgentChatRequest(BaseModel):
    """
    Model for agent chat requests received via runner.
    """

    graph: Dict[str, Any] = Field(..., description="The graph definition")
    thread_id: Optional[str] = Field(None, description="The thread ID")
    message: Optional[MessagePayload] = Field(None, description="The message payload")
    is_new_conversation: Optional[bool] = Field(
        False, description="Whether this is a new conversation"
    )
    phone_number: Optional[str] = Field(None, description="DEPRECATED: The phone number (use contact_information)")
    contact_information: Optional[Dict[str, Any]] = Field(
        None, description="Contact information including phone number, profile name, and metadata"
    )
    test_mode: Optional[bool] = Field(
        False, description="Whether to run in test mode (no WhatsApp messages)"
    )
    agent_prompt: Optional[str] = Field(None, description="The system prompt for the agent")
    llm_config: Optional[Dict[str, Any]] = Field(None, description="The LLM configuration")
    last_interrupt_tool_call_id: Optional[str] = Field(None, description="The last tool call ID")
    agent_test_chat_id: Optional[str] = Field(None, description="The agent test chat ID")
    checkpoint_id: Optional[str] = Field(None, description="The checkpoint ID to replay from")
    agent_version: Optional[int] = Field(None, description="The agent engine version (1 or 2)")
