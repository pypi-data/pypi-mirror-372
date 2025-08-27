"""
Contains node agent creation and configuration functions.
"""

import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command

from kapso.runner.core.cache_utils import optimize_messages_for_provider
from kapso.runner.core.flow_state import State
from kapso.runner.core.flow_utils import get_next_pending_tool_call
from kapso.runner.core.llm_factory import initialize_llm
from kapso.runner.core.node_types.base import node_type_registry
from kapso.runner.core.tool_generator import (
    generate_tools_for_node,
    get_interrupt_handler,
    tool_requires_interrupt,
)

# Create a logger for this module
logger = logging.getLogger(__name__)

# Try to import message_store (optional for cloud features)
try:
    from app.core.message_store import message_store
    HAS_MESSAGE_STORE = True
except ImportError:
    message_store = None
    HAS_MESSAGE_STORE = False


async def check_and_inject_new_messages(
    state: State, config: RunnableConfig
) -> Optional[Dict[str, Any]]:
    """
    Check Rails database for new WhatsApp messages and inject handle_user_message tool call.

    Args:
        state: Current agent state
        config: Runtime configuration

    Returns:
        Updates dict with handle_user_message tool call, or None if no messages
    """
    thread_id = config.get("configurable", {}).get("thread_id")
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    if not thread_id:
        return None

    if not HAS_MESSAGE_STORE:
        return None

    try:
        # Atomically fetch and mark messages as processed
        pending_messages = await message_store.fetch_and_mark_messages(thread_id)

        if not pending_messages:
            return None

        logger.info(f"Found {len(pending_messages)} pending messages for thread {thread_id}")

        # Combine all message contents (matching current Rails behavior)
        combined_content = "\n".join(msg["content"] for msg in pending_messages)

        # Log message injection
        message_ids = [str(msg["id"]) for msg in pending_messages]
        logger.info(f"MSG_INJECT: count={len(pending_messages)}, ids={message_ids}, content_length={len(combined_content)}")

        if agent_version == 2:
            # V2: Add messages directly to conversation
            return {
                "full_history": [HumanMessage(content=combined_content)],
                "conversation": [HumanMessage(content=combined_content)]
            }
        else:
            # V1: Original behavior with tool calls
            # Create handle_user_message tool call (matching existing pattern)
            tool_call_id = str(uuid.uuid4())
            tool_call = {"id": tool_call_id, "name": "handle_user_message", "args": {}}

            # Create AI message with the tool call
            ai_message = AIMessage(content="", tool_calls=[tool_call])

            # Create the tool response message
            tool_message = ToolMessage(content=combined_content, tool_call_id=tool_call_id)

            logger.info(
                f"Injected handle_user_message for {len(pending_messages)} messages in thread {thread_id}"
            )

            # Return updates to add both messages to full_history
            # The conversation update will be handled by the handle_user_message handler
            return {"full_history": [ai_message, tool_message]}

    except Exception as e:
        logger.error(f"Error checking for new messages: {e}")
        return None


async def check_and_inject_external_messages(state: State, config: RunnableConfig) -> Optional[Dict[str, Any]]:
    """Check for externally sent messages and inject as tool calls."""
    thread_id = config.get("configurable", {}).get("thread_id")
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    conversation_id = config.get("configurable", {}).get("execution_metadata", {}).get("whatsapp_conversation_id")

    if not thread_id or not conversation_id or not HAS_MESSAGE_STORE:
        return None

    try:
        # Get last processed timestamp from state
        last_timestamp = state.get("last_processed_timestamp")

        # If no timestamp is set, this is an existing conversation from before the feature
        # Don't fetch any messages to avoid injecting old messages
        if not last_timestamp:
            logger.info(f"No last_processed_timestamp for thread {thread_id}, skipping external message check for existing conversation")
            return None

        # Fetch external messages sent after that timestamp (only outbound for mid-conversation)
        messages = await message_store.fetch_recent_external_messages(conversation_id, last_timestamp)

        if not messages:
            return None

        logger.info(f"Checking for external messages after timestamp: {state.get('last_processed_timestamp')}")
        logger.info(f"Found {len(messages)} external messages to inject")

        updates = []
        newest_timestamp = last_timestamp

        if agent_version == 2:
            # V2: Add messages directly as AI messages
            for message in messages:
                updates.append(AIMessage(content=message.get('content', '')))

                # Track the newest timestamp
                message_timestamp = message["created_at"]
                try:
                    from dateutil import parser
                    message_dt = parser.isoparse(message_timestamp)
                    newest_dt = parser.isoparse(newest_timestamp) if newest_timestamp else None

                    if not newest_dt or message_dt > newest_dt:
                        newest_timestamp = message_timestamp
                except Exception as e:
                    logger.warning(f"Error parsing timestamp {message_timestamp}: {e}")
                    if not newest_timestamp or message_timestamp > newest_timestamp:
                        newest_timestamp = message_timestamp
        else:
            # V1: Original behavior with tool calls
            for message in messages:
                tool_call_id = str(uuid.uuid4())
                tool_call = {
                    "id": tool_call_id,
                    "name": "send_external_message",
                    "args": { "message": message.get('content', '') }
                }

                ai_message = AIMessage(content="", tool_calls=[tool_call])
                tool_response = ToolMessage(
                    content="Message sent",
                    tool_call_id=tool_call_id
                )

                updates.extend([ai_message, tool_response])

                # Track the newest timestamp - parse to ensure proper comparison
                message_timestamp = message["created_at"]
                try:
                    # Parse both timestamps to datetime for accurate comparison
                    from dateutil import parser
                    message_dt = parser.isoparse(message_timestamp)
                    newest_dt = parser.isoparse(newest_timestamp) if newest_timestamp else None

                    if not newest_dt or message_dt > newest_dt:
                        newest_timestamp = message_timestamp
                except Exception as e:
                    logger.warning(f"Error parsing timestamp {message_timestamp}: {e}")
                    # Fallback to string comparison
                    if not newest_timestamp or message_timestamp > newest_timestamp:
                        newest_timestamp = message_timestamp

        # Return updates including the new timestamp
        return {
            "full_history": updates,
            "last_processed_timestamp": newest_timestamp
        }

    except Exception as e:
        logger.error(f"Error checking for external messages: {e}")
        return None


async def check_for_interruptions(
    state: State, config: RunnableConfig, current_node_name: str
) -> Optional[Command]:
    """
    Check for stop signals, sent templates, or new messages.
    """
    # Check for stop status first (highest priority)
    stop_updates = await check_and_inject_stop_if_needed(state, config)
    if stop_updates:
        return Command(update=stop_updates, goto=current_node_name)

    # Check for external messages
    external_message_updates = await check_and_inject_external_messages(state, config)
    if external_message_updates:
        return Command(update=external_message_updates, goto=current_node_name)

    # Check for new messages
    message_updates = await check_and_inject_new_messages(state, config)
    if message_updates:
        return Command(update=message_updates, goto=current_node_name)

    return None


async def check_and_inject_stop_if_needed(
    state: State, config: RunnableConfig
) -> Optional[Dict[str, Any]]:
    """Check if execution has been stopped and inject StopExecution tool call."""
    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        return None

    if not HAS_MESSAGE_STORE:
        return None

    status = await message_store.check_execution_status(thread_id)
    if status == "stopped":
        logger.info(f"Stop detected for thread {thread_id}")

        # Create stop tool call
        tool_call_id = str(uuid.uuid4())
        tool_call = {
            "id": tool_call_id,
            "name": "StopExecution",
            "args": {"reason": "Execution stopped by user"},
        }

        ai_message = AIMessage(content="", tool_calls=[tool_call])

        # Return updates to add to full_history
        return {"full_history": [ai_message]}

    return None


async def handle_tool_call_routing(tool_call, current_node_name, node_type, node_name, node_config, agent_version=1):
    """
    Determine routing for a tool call based on whether it requires a interrupt node.

    Args:
        tool_call: The tool call to handle
        current_node_name: The name of the current node
        node_type: The type of node
        node_name: The name of the node
        node_config: The configuration for the node

    Returns:
        A tuple of (state_update, next_node) where:
        - state_update is a dictionary of state updates to apply
        - next_node is the name of the node to route to, or None to stay in the current node
    """
    tool_name = tool_call["name"]

    # Initialize state update
    state_update = {}
    next_node = None

    # Generate tools to check for interrupt
    node_tools = await generate_tools_for_node(
        node_type=node_type, node_name=node_name, node_config=node_config, agent_version=agent_version
    )

    # Find the tool in all_tools
    tool = None
    for t in node_tools.get("all", []):
        if hasattr(t, "metadata") and hasattr(t.metadata, "name") and t.metadata.name == tool_name:
            tool = t
            break

    # Check if this tool requires a interrupt node
    if tool and tool_requires_interrupt(tool):
        logger.info(f"Tool {tool_name} requires a interrupt node")

        # Get handler name
        handler = get_interrupt_handler(tool)
        if handler:
            # Determine the next node based on the handler
            snake_case_tool_name = "".join(
                ["_" + c.lower() if c.isupper() else c for c in tool_name]
            ).lstrip("_")

            if tool_name == "AskUserForInput":
                message = tool_call.get("args", {}).get("message", "")
                logger.info("Routing to AskUserForInput with message: %s", message)
                state_update["conversation"] = [AIMessage(content=message)]
                next_node = f"{snake_case_tool_name}_{current_node_name}"
            elif tool_name == "SendWhatsappTemplateMessage":
                logger.info("Routing to SendWhatsappTemplateMessage")
                next_node = f"{snake_case_tool_name}_{current_node_name}"
            elif tool_name == "EnterIdleState":
                message = tool_call.get("args", {}).get("message", "")
                logger.info("Routing to EnterIdleState with message: %s", message)
                if message:
                    state_update["conversation"] = [AIMessage(content=message)]
                next_node = f"{snake_case_tool_name}_{current_node_name}"
            elif tool_name == "WaitForUser":
                # WaitForUser has no parameters and routes to its own handler
                logger.info("Routing to WaitForUser handler")
                next_node = f"wait_for_user_{current_node_name}"
            elif tool_name == "StopExecution":
                logger.info("Routing to StopExecution")
                next_node = f"{snake_case_tool_name}_{current_node_name}"
            elif tool_name == "MoveToNextNode":
                logger.info("Routing to MoveToNextNode")
                next_node = "subgraph_router"
    else:
        # Route to generic tool node for non-interrupt tools
        logger.info(f"Routing to generic tool node for {tool_name}")
        next_node = f"generic_tool_node_{current_node_name}"

    return state_update, next_node


def log_llm_response(response):
    logger.info("LLM Response:")
    if hasattr(response, "content") and response.content:
        logger.info(f"  Content: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        logger.info(f"  Tool calls: {response.tool_calls}")


def generate_recovery_message(error_description: str) -> str:
    """
    Generate a recovery message for error situations.

    Args:
        error_description: Description of the error that occurred

    Returns:
        A formatted recovery message string
    """
    recovery_message = f"{error_description} "
    recovery_message += (
        f"I will generate relevant and helpful content based on the provided instructions. "
    )
    recovery_message += "Now I will continue the execution."
    return recovery_message


def _extract_text_content(response: Any) -> str:
    """
    Extract text content from LLM response, handling different formats.

    Args:
        response: The LLM response

    Returns:
        Extracted text content or empty string
    """
    if not hasattr(response, "content") or not response.content:
        return ""

    content_text = ""
    if isinstance(response.content, str):
        content_text = response.content.strip()
    elif isinstance(response.content, list) and len(response.content) > 0:
        # Some providers send content as array, first element is text
        if isinstance(response.content[0], str):
            content_text = response.content[0].strip()
        elif isinstance(response.content[0], dict) and "text" in response.content[0]:
            content_text = response.content[0]["text"].strip()

    return content_text


async def _send_v2_message_to_user(
    content_text: str,
    test_mode: bool,
    recipient_id: str,
    thread_id: str,
    channel_type: str
) -> None:
    """
    Send message to user for v2 agents.

    Args:
        content_text: The message content
        test_mode: Whether in test mode
        recipient_id: Recipient ID (phone number)
        thread_id: Thread ID
        channel_type: Channel type (e.g., whatsapp)
    """
    if test_mode:
        logger.info("TEST MODE: Would have sent message to %s via %s: %s", recipient_id, channel_type, content_text)
    elif recipient_id and thread_id:
        # Import here to avoid circular dependency
        from kapso.runner.channels.models import ChannelMessage, MessageChannelType, MessageContentType
        from kapso.runner.channels.factory import send_message as channel_send_message

        try:
            channel_message = ChannelMessage(
                content=content_text,
                channel_type=MessageChannelType(channel_type),
                recipient_id=recipient_id,
                thread_id=thread_id,
                content_type=MessageContentType.TEXT,
                metadata={"test_mode": test_mode}
            )
            await channel_send_message(channel_message)
            logger.info("V2 agent sent message to %s via %s: %s", recipient_id, channel_type, content_text)
        except Exception as e:
            logger.error(f"Error sending V2 agent message: {e}")


def _create_wait_for_user_response(content_text: str, current_node_name: str, provider: str = "") -> Command:
    """
    Create a response with WaitForUser tool call injection.

    Args:
        content_text: The message content
        current_node_name: Name of the current node
        provider: The LLM provider name

    Returns:
        Command with WaitForUser injection
    """
    logger.info("V2 agent sent message without tool calls, injecting WaitForUser")

    # Create WaitForUser tool call
    tool_call_id = str(uuid.uuid4())
    wait_tool_call = {
        "id": tool_call_id,
        "name": "WaitForUser",
        "args": {}
    }

    # Providers that require content and tool calls in the same message
    if provider.lower() in ["google", "gemini", "google-genai", "google-generativeai"]:
        logger.info(f"Using combined message format for {provider} provider")
        # Create single AIMessage with both content and tool call
        combined_response = AIMessage(
            content=content_text,
            tool_calls=[wait_tool_call]
        )
        return Command(
            update={
                "full_history": [combined_response],
                "conversation": [AIMessage(content=content_text)]
            },
            goto=current_node_name
        )
    else:
        # Default behavior: separate messages for other providers
        logger.info(f"Using separate messages format for {provider or 'default'} provider")
        # Create the original response without tool calls first
        original_response = AIMessage(content=content_text)

        # Create new AIMessage with the WaitForUser tool call
        injected_response = AIMessage(content="", tool_calls=[wait_tool_call])

        # Return both messages: the original content message and the WaitForUser tool call
        return Command(
            update={
                "full_history": [original_response, injected_response],
                "conversation": [AIMessage(content=content_text)]
            },
            goto=current_node_name
        )


def _fix_duplicate_tool_call_ids(response: Any, full_history: List[Any]) -> Any:
    """
    Fix duplicate tool call IDs by checking against existing tool calls in history.
    
    Args:
        response: The LLM response that may contain tool calls
        full_history: The full conversation history
        
    Returns:
        Response with fixed tool call IDs if duplicates were found
    """
    if not hasattr(response, "tool_calls") or not response.tool_calls:
        return response
    
    # Collect all existing tool call IDs from history
    existing_tool_call_ids = set()
    for message in full_history:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                existing_tool_call_ids.add(tool_call.get("id"))
    
    # Check and fix duplicate IDs in the current response
    modified = False
    fixed_tool_calls = []
    
    for tool_call in response.tool_calls:
        tool_call_id = tool_call.get("id")
        tool_name = tool_call.get("name", "unknown")
        
        # If this ID already exists in history, generate a new one
        if tool_call_id in existing_tool_call_ids:
            new_id = f"tool_{str(uuid.uuid4())[:8]}_{tool_name}"
            logger.warning(
                f"Duplicate tool call ID detected: {tool_call_id} for {tool_name}. "
                f"Replacing with: {new_id}"
            )
            # Create a new tool call dict with the updated ID
            fixed_tool_call = {**tool_call, "id": new_id}
            fixed_tool_calls.append(fixed_tool_call)
            modified = True
        else:
            fixed_tool_calls.append(tool_call)
            existing_tool_call_ids.add(tool_call_id)
    
    # If we modified any tool calls, create a new response with the fixed IDs
    if modified:
        # Create a new AIMessage with the same content but fixed tool calls
        return AIMessage(
            content=response.content,
            tool_calls=fixed_tool_calls,
            additional_kwargs=getattr(response, "additional_kwargs", {}),
            response_metadata=getattr(response, "response_metadata", {}),
            usage_metadata=getattr(response, "usage_metadata", None)
        )
    
    return response


def validate_and_handle_empty_response(response: Any, agent_version: int = 1) -> Any:
    """
    Validate LLM response and handle empty responses by creating a self-recovery message or WaitForUser.

    Args:
        response: The LLM response to validate
        agent_version: The agent version (1 or 2)

    Returns:
        The original response if valid, or a new AIMessage with recovery content or WaitForUser
    """
    # Check if response is None or doesn't have the expected attributes
    if response is None:
        logger.warning("Received None response from LLM")
        if agent_version == 2:
            # For v2, inject WaitForUser instead of recovery message
            tool_call_id = str(uuid.uuid4())
            wait_tool_call = {
                "id": tool_call_id,
                "name": "WaitForUser",
                "args": {}
            }
            return AIMessage(content="", tool_calls=[wait_tool_call])
        else:
            recovery_message = generate_recovery_message("I received a None response from the LLM.")
            return AIMessage(content=recovery_message)

    # Check if response has no content and no tool calls (empty response)
    has_content = False
    if hasattr(response, "content") and response.content:
        if isinstance(response.content, str):
            has_content = response.content.strip() != ""
        elif isinstance(response.content, list):
            has_content = len(response.content) > 0 and any(
                (hasattr(block, "text") and block.text.strip())
                or (isinstance(block, dict) and block.get("text", "").strip())
                or (isinstance(block, str) and block.strip())
                for block in response.content
            )

    has_tool_calls = hasattr(response, "tool_calls") and response.tool_calls

    if not has_content and not has_tool_calls:
        logger.warning("LLM generated an empty response with no content and no tool calls")
        if agent_version == 2:
            # For v2, inject WaitForUser instead of recovery message
            tool_call_id = str(uuid.uuid4())
            wait_tool_call = {
                "id": tool_call_id,
                "name": "WaitForUser",
                "args": {}
            }
            return AIMessage(content="", tool_calls=[wait_tool_call])
        else:
            recovery_message = generate_recovery_message(
                "I generated an empty response and no tool calls."
            )
            return AIMessage(content=recovery_message)

    # Response is valid, return as-is
    return response


def new_node_agent(current_node: dict, node_edges: list) -> Callable:
    """
    Create a new agent with the given prompt and tools.

    Args:
        current_node: The current node information
        node_edges: The edges for the current node

    Returns:
        A callable function that processes the state
    """
    # Get node type, default to "DefaultNode" if not specified
    node_type = current_node.get("type", "DefaultNode")
    node_name = current_node.get("name", "unknown_name")

    # Get the node type instance from the registry
    node_type_instance = node_type_registry.create(node_type)

    async def execute_node_action(state: State, config: RunnableConfig):
        """
        Execute the action for the current node using the node type's execute method.

        Args:
            state: The current state
            config: The runnable configuration

        Returns:
            The result of the node execution
        """
        logger.info(f"Executing action for node: {current_node['name']} of type: {node_type}")

        try:
            # Get LLM configuration from config if available
            llm_config = config.get("configurable", {}).get("llm_config")
            provider = llm_config.get("provider_name", "") if llm_config else ""
            
            # Get agent version from config
            agent_version = config.get("configurable", {}).get("agent_version", 1)

            # Initialize LLM based on configuration
            try:
                llm_without_tools = initialize_llm(llm_config)
            except Exception as e:
                error_message = f"Error initializing LLM: {str(e)}"
                logger.error(error_message)
                
                if agent_version == 2:
                    # For v2, inject WaitForUser instead of recovery message
                    tool_call_id = str(uuid.uuid4())
                    wait_tool_call = {
                        "id": tool_call_id,
                        "name": "WaitForUser",
                        "args": {}
                    }
                    return AIMessage(content="", tool_calls=[wait_tool_call])
                else:
                    recovery_message = generate_recovery_message(
                        f"I encountered an error while initializing the LLM: {error_message}."
                    )
                    return AIMessage(content=recovery_message)

            # Generate tools for this node using the tool generator
            node_tools = await generate_tools_for_node(
                node_type=node_type,
                node_name=node_name,
                node_config=current_node,
                provider=provider,
                agent_version=agent_version,
            )

            # Bind tools to LLM
            llm = llm_without_tools.bind_tools(node_tools["formatted"])

            # Optimize history for the specific provider
            optimized_history = optimize_messages_for_provider(
                state.get("full_history", []), provider
            )

            # Create a new modified state with the optimized history
            optimized_state = {**state, "full_history": optimized_history}

            # Use the node type's execute method with the optimized state
            response = await node_type_instance.execute(
                state=optimized_state,
                node_config=current_node,
                node_edges=node_edges,
                llm=llm,
                llm_without_tools=llm_without_tools,
                config=config,
            )

            # Fix duplicate tool call IDs if any
            response = _fix_duplicate_tool_call_ids(response, state.get("full_history", []))

            # Validate and handle empty responses
            response = validate_and_handle_empty_response(response, agent_version)

            # Log token usage if available
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                logger.info(f"Token usage: {response.usage_metadata}")
                input_details = response.usage_metadata.get("input_token_details")
                if input_details:
                    logger.info(
                        f"  Input details: Cache Read={input_details.get('cache_read', 'N/A')}, "
                        f"Cache Creation={input_details.get('cache_creation', 'N/A')}"
                    )

            return response

        except Exception as e:
            # Handle any other unexpected errors
            error_message = str(e)
            logger.error(f"Unexpected error during node execution: {error_message}")
            raise e

    async def node_fn(state: State, config: RunnableConfig):
        thread_id = config.get("configurable", {}).get("thread_id", "unknown_thread")
        agent_version = config.get("configurable", {}).get("agent_version", 1)
        logger.info("Executing node: %s of thread %s", current_node["name"], thread_id)

        # Check for pending tool calls first
        pending_tool_call = get_next_pending_tool_call(state["full_history"])

        # Log pending tool call if found
        if pending_tool_call:
            logger.info(f"FOUND_PENDING: tool={pending_tool_call['name']}, id={pending_tool_call['id']}")

        # If no pending tool calls, check for interruptions
        if not pending_tool_call:
            interruption_command = await check_for_interruptions(state, config, current_node["name"])
            if interruption_command:
                return interruption_command

        if pending_tool_call:
            # Use the helper function to determine routing with node type info
            tool_state_update, next_node = await handle_tool_call_routing(
                pending_tool_call, current_node["name"], node_type, node_name, current_node, agent_version
            )
            if next_node:
                return Command(update=tool_state_update, goto=next_node)

        # Handle initial step_prompt if current_node is not set
        if not state.get("current_node"):
            step_prompt = node_type_instance.generate_step_prompt(current_node, node_edges, agent_version)

            step_prompt = f"{step_prompt}\n\nThe user just sent a message with content: {state.get('full_history', [])[-1].content}"

            if agent_version == 2:
                # For v2: Simulate a MoveToNextNode tool call
                tool_call_id = str(uuid.uuid4())
                move_tool_call = {
                    "id": tool_call_id,
                    "name": "MoveToNextNode",
                    "args": {
                        "next_node": current_node["name"],
                        "reason": "Starting execution, moving to first node"
                    }
                }

                # Create AI message with the tool call
                ai_message = AIMessage(content="", tool_calls=[move_tool_call])

                # Create tool response with the step prompt
                tool_message = ToolMessage(
                    content=step_prompt,
                    tool_call_id=tool_call_id
                )

                return Command(
                    update={
                        "current_node": current_node,
                        "full_history": [ai_message, tool_message],
                    },
                    goto=current_node["name"],
                )
            else:
                # For v1: Original behavior
                return Command(
                    update={
                        "current_node": current_node,
                        "full_history": [AIMessage(content=step_prompt)],
                    },
                    goto=current_node["name"],
                )

        # Execute node action
        response = await execute_node_action(state, config)

        # After execution, check again for interruptions
        # This ensures we process any messages that arrived during node execution
        interruption_command = await check_for_interruptions(state, config, current_node["name"])
        if interruption_command:
            return interruption_command


        # In V2, if the AI responds with text content, send it as a message
        if agent_version == 2:
            # Extract text content from response
            content_text = _extract_text_content(response)

            if content_text:  # Only proceed if we have non-empty text
                # Get configuration values
                configurable = config.get("configurable", {})
                test_mode = configurable.get("test_mode", False)
                recipient_id = configurable.get("phone_number", "")
                thread_id = configurable.get("thread_id", "")
                channel_type = configurable.get("channel_type", "whatsapp")

                # Send message to user
                await _send_v2_message_to_user(
                    content_text, test_mode, recipient_id, thread_id, channel_type
                )

                # Check if response has tool calls
                has_tool_calls = hasattr(response, "tool_calls") and response.tool_calls

                if not has_tool_calls:
                    # For v2 agents, if there's content but no tool calls, inject a WaitForUser tool call
                    # Get provider from llm_config
                    llm_config = configurable.get("llm_config", {})
                    provider = llm_config.get("provider_name", "") if llm_config else ""
                    return _create_wait_for_user_response(content_text, current_node["name"], provider)
                else:
                    # Has tool calls, use the response as-is
                    return Command(
                        update={"full_history": [response], "conversation": [AIMessage(content=content_text)]},
                        goto=current_node["name"]
                    )
        # No interruptions, use the normal response
        return Command(update={"full_history": [response]}, goto=current_node["name"])

    return node_fn
