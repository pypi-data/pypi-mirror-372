"""
Handlers for messaging tools.
"""

import asyncio
import logging

from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END
from langgraph.types import Command, interrupt

from kapso.runner.channels.models import ChannelMessage, MessageChannelType, MessageContentType
from kapso.runner.channels.factory import send_message as channel_send_message
from kapso.runner.channels.exceptions import (
    ChannelError,
    MessageSendError,
    ChannelUnavailableError,
    ChannelAuthenticationError,
)
from kapso.runner.core.flow_utils import get_next_pending_tool_call
logger = logging.getLogger(__name__)


async def ask_user_for_input(state, config: RunnableConfig):
    """
    Handler for the AskUserForInput tool.

    This function processes requests for user input, sends the question to the user,
    and waits for their response before continuing execution.

    Args:
        state: The current state
        config: Configuration for the runnable

    Returns:
        Updated state after handling the tool call
    """
    logger.info("Processing ask_user_for_input function")
    configurable = config.get("configurable", {})  # Default to empty dict if None
    resume_tool_call_id = configurable.get("resume_tool_call_id") if configurable else None
    tool_call = get_next_pending_tool_call(state["full_history"], "AskUserForInput")

    if not tool_call:
        logger.warning("No AskUserForInput tool call found in state history")
        return state

    arguments = tool_call["args"]
    message = arguments.get("message", "")

    if resume_tool_call_id is None or resume_tool_call_id != tool_call["id"]:
        test_mode = configurable.get("test_mode", False) if configurable else False
        # Get required parameters with defaults to avoid None
        recipient_id = configurable.get("phone_number", "") if configurable else ""
        thread_id = configurable.get("thread_id", "") if configurable else ""
        # Get channel type from configurable if present, default to whatsapp
        channel_type = configurable.get("channel_type", "whatsapp") if configurable else "whatsapp"

        # Validate required parameters
        if not recipient_id or not thread_id:
            logger.warning("Missing required parameters: phone_number or thread_id")

        # Create channel message
        channel_message = ChannelMessage(
            content=message,
            channel_type=MessageChannelType(channel_type),
            recipient_id=recipient_id,
            thread_id=thread_id,
            content_type=MessageContentType.TEXT,
            metadata={"test_mode": test_mode}
        )

        if test_mode:
            logger.info("TEST MODE: Would have sent message to %s via %s: %s", recipient_id, channel_type, message)
        elif message:  # Only send if message is not empty
            # Send message via the channel factory with retry logic
            max_retries = 3
            retry_delay = 1.0  # Initial delay in seconds
            
            for attempt in range(max_retries):
                try:
                    await channel_send_message(channel_message)
                    logger.info("Message sent to %s via %s: %s", recipient_id, channel_type, message)
                    break  # Success, exit retry loop
                except ChannelUnavailableError as e:
                    if attempt < max_retries - 1:
                        # Use retry_after if provided, otherwise exponential backoff
                        wait_time = e.retry_after or (retry_delay * (2 ** attempt))
                        logger.warning(
                            "Channel unavailable (attempt %d/%d), retrying in %s seconds: %s",
                            attempt + 1, max_retries, wait_time, str(e)
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("Failed to send message after %d attempts: %s", max_retries, str(e))
                        raise
                except ChannelAuthenticationError as e:
                    # Authentication errors are not retryable
                    logger.error("Authentication error sending message: %s", str(e))
                    raise
                except MessageSendError as e:
                    # For other send errors, log and re-raise
                    logger.error("Error sending message to %s: %s", recipient_id, str(e))
                    raise
                except ChannelError as e:
                    # Catch any other channel errors
                    logger.error("Unexpected channel error: %s", str(e))
                    raise

    answer = interrupt({"message": message, "tool_call": tool_call})
    logger.info("User response received: %s", str(answer)[:50] + ("..." if len(answer) > 50 else ""))

    # Get agent version from config
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    
    return _get_state_update_from_answer(answer, tool_call["id"], agent_version)


async def send_whatsapp_template_message(state, config: RunnableConfig):
    """
    Handler for the SendWhatsappTemplateMessage tool.

    Args:
        state: The current state
        config: Configuration for the runnable

    Returns:
        Updated state after handling the tool call
    """
    logger.info("Processing send_whatsapp_template_message function")
    tool_call = get_next_pending_tool_call(state["full_history"], "SendWhatsappTemplateMessage")

    if not tool_call:
        logger.warning("No SendWhatsappTemplateMessage tool call found in state history")
        return state
    node_config = state.get("current_node", {})

    configurable = config.get("configurable", {})  # Default to empty dict if None
    arguments = tool_call["args"]
    logger.info("SendWhatsappTemplateMessage arguments: %s", arguments)
    template_name = arguments["template_name"]
    template_parameters = arguments["template_parameters"]

    # Get whatsapp_node_id and wait_for_response from registry
    try:
        template_data = get_whatsapp_template_data(node_config, template_name) or {}
        whatsapp_template_id = template_data.get("whatsapp_template_id", "")
        wait_for_response = template_data.get("wait_for_response", False)
    except ValueError as e:
        logger.warning(f"Failed to get template data from registry: {e}")
        # Fallback to default values
        whatsapp_template_id = ""
        wait_for_response = False

    resume_tool_call_id = configurable.get("resume_tool_call_id") if configurable else None

    # Get required parameters with defaults to avoid None
    recipient_id = configurable.get("phone_number", "") if configurable else ""
    thread_id = configurable.get("thread_id", "") if configurable else ""
    test_mode = configurable.get("test_mode", False) if configurable else False
    # Get channel type from configurable if present, default to whatsapp
    channel_type = configurable.get("channel_type", "whatsapp") if configurable else "whatsapp"

    # Skip sending if we're resuming from an interruption
    if resume_tool_call_id is None or resume_tool_call_id != tool_call["id"]:
        if test_mode:
            logger.info("TEST MODE: Would have sent template %s to %s", template_name, recipient_id)
            result = f"Template message not sent (test mode): {template_name}"
        else:
            result = await do_template_message_request(
                template_name,
                recipient_id,
                template_parameters,
                whatsapp_template_id,
                thread_id,
                test_mode,
                channel_type
            )
            logger.info("Template message result: %s", result)

    if wait_for_response:
        # Content for the interrupt
        content = f"Sent template: {template_name}" if not test_mode else f"Template message not sent (test mode): {template_name}"
        answer = interrupt(
            {"message": content, "tool_call": tool_call, "wait_for_response": wait_for_response}
        )

        # Get agent version from config
        agent_version = config.get("configurable", {}).get("agent_version", 1)
        
        return _get_state_update_from_answer(answer, tool_call["id"], agent_version)
    else:
        # No response expected, continue execution
        message_content = f"Sent template: {template_name}" if not test_mode else f"Template message not sent (test mode): {template_name}"
        return {"full_history": [{"tool_call_id": tool_call["id"], "type": "tool", "content": message_content}]}


async def do_template_message_request(
    template_name,
    recipient_id,
    template_parameters,
    whatsapp_template_id,
    thread_id,
    test_mode=False,
    channel_type="whatsapp"
):
    """
    Send a template message to the user through the appropriate channel.

    Args:
        template_name: The name of the template to send
        recipient_id: The recipient's ID (e.g., phone number)
        template_parameters: The parameters to send to the template
        node_id: The ID of the node to send the message to
        thread_id: The ID of the thread to send the message to
        test_mode: Whether to run in test mode
        channel_type: The channel type to use (default: whatsapp)
    """
    # If in test mode, don't actually send the message
    if test_mode:
        logger.info(f"TEST MODE: Would have sent template {template_name} to {recipient_id}")
        return f"Template message not sent (test mode): {template_name}"

    # Create channel message
    channel_message = ChannelMessage(
        content={
            "template_name": template_name,
            "parameters": template_parameters
        },
        channel_type=MessageChannelType(channel_type),
        recipient_id=recipient_id,
        thread_id=thread_id,
        content_type=MessageContentType.TEMPLATE,
        metadata={"test_mode": test_mode, "whatsapp_template_id": whatsapp_template_id}
    )

    # Send via the channel factory with retry logic for transient errors
    max_retries = 3
    retry_delay = 1.0  # Initial delay in seconds
    
    for attempt in range(max_retries):
        try:
            result = await channel_send_message(channel_message)
            return result
        except ChannelUnavailableError as e:
            if attempt < max_retries - 1:
                # Use retry_after if provided, otherwise exponential backoff
                wait_time = e.retry_after or (retry_delay * (2 ** attempt))
                logger.warning(
                    "Channel unavailable for template (attempt %d/%d), retrying in %s seconds: %s",
                    attempt + 1, max_retries, wait_time, str(e)
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error("Failed to send template message after %d attempts: %s", max_retries, str(e))
                raise
        except (ChannelAuthenticationError, MessageSendError, ChannelError) as e:
            # Don't retry for authentication or other errors
            logger.error("Error sending template message: %s", str(e))
            raise


async def abort(state, config: RunnableConfig):
    """
    Handler for the Abort tool.

    Args:
        state: The current state

    Returns:
        Command to route directly to the END node
    """
    logger.info("Processing abort function")
    tool_call = get_next_pending_tool_call(state["full_history"], "Abort")

    if not tool_call:
        logger.warning("No Abort tool call found in state history")
        return state

    arguments = tool_call["args"]
    reason = arguments["reason"]

    logger.info("Aborting conversation. Reason: %s", reason)

    # Create a tool message with the abort reason
    tool_message = {
        "tool_call_id": tool_call["id"],
        "type": "tool",
        "content": f"Conversation aborted: {reason}",
    }

    # Return a Command to route to the END node
    return Command(
        update={
            "full_history": [tool_message],
        },
        goto=END,
    )


async def enter_idle_state(state, config: RunnableConfig):
    """
    Handler for the EnterIdleState tool.

    This function processes requests to enter an idle state, sends a farewell message to the user,
    and waits for their final response before ending the conversation.

    Args:
        state: The current state
        config: Configuration for the runnable

    Returns:
        Updated state after handling the tool call
    """
    logger.info("Processing enter_idle_state function")
    configurable = config.get("configurable", {})  # Default to empty dict if None
    resume_tool_call_id = configurable.get("resume_tool_call_id") if configurable else None
    tool_call = get_next_pending_tool_call(state["full_history"], "EnterIdleState")

    if not tool_call:
        logger.warning("No EnterIdleState tool call found in state history")
        return state

    arguments = tool_call["args"]
    message = arguments.get("message", "")

    if (resume_tool_call_id is None or resume_tool_call_id != tool_call["id"]) and message:
        test_mode = configurable.get("test_mode", False) if configurable else False
        # Get required parameters with defaults to avoid None
        recipient_id = configurable.get("phone_number", "") if configurable else ""
        thread_id = configurable.get("thread_id", "") if configurable else ""
        # Get channel type from configurable if present, default to whatsapp
        channel_type = configurable.get("channel_type", "whatsapp") if configurable else "whatsapp"

        # Validate required parameters
        if not recipient_id or not thread_id:
            logger.warning("Missing required parameters: phone_number or thread_id")

        # Create channel message
        channel_message = ChannelMessage(
            content=message,
            channel_type=MessageChannelType(channel_type),
            recipient_id=recipient_id,
            thread_id=thread_id,
            content_type=MessageContentType.TEXT,
            metadata={"test_mode": test_mode}
        )

        if message:  # Only send if message is not empty
            # Send message via the channel factory with retry logic
            max_retries = 3
            retry_delay = 1.0  # Initial delay in seconds
            
            for attempt in range(max_retries):
                try:
                    await channel_send_message(channel_message)
                    logger.info("Idle state message sent to %s via %s: %s", recipient_id, channel_type, message)
                    break  # Success, exit retry loop
                except ChannelUnavailableError as e:
                    if attempt < max_retries - 1:
                        # Use retry_after if provided, otherwise exponential backoff
                        wait_time = e.retry_after or (retry_delay * (2 ** attempt))
                        logger.warning(
                            "Channel unavailable (attempt %d/%d), retrying in %s seconds: %s",
                            attempt + 1, max_retries, wait_time, str(e)
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("Failed to send idle state message after %d attempts: %s", max_retries, str(e))
                        raise
                except ChannelAuthenticationError as e:
                    # Authentication errors are not retryable
                    logger.error("Authentication error sending idle state message: %s", str(e))
                    raise
                except MessageSendError as e:
                    # For other send errors, log and re-raise
                    logger.error("Error sending idle state message to %s: %s", recipient_id, str(e))
                    raise
                except ChannelError as e:
                    # Catch any other channel errors
                    logger.error("Unexpected channel error in idle state: %s", str(e))
                    raise

    answer = interrupt({"message": message, "tool_call": tool_call})
    logger.info("User response received: %s", str(answer)[:50] + ("..." if len(answer) > 50 else ""))

    # Get agent version from config
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    
    state_update = _get_state_update_from_answer(answer, tool_call["id"], agent_version)

    return Command(
        update=state_update,
        goto=END,
    )

def _get_state_update_from_answer(answer, tool_call_id, agent_version=1):
    answer_type =  answer.get("type", None)
    answer_content = answer.get("content", {})
    
    if answer_type == 'user_input':
        text_answer = answer_content.get("text", None)
        
        if agent_version == 2:
            # For v2: tool message contains the user message, and we also add a HumanMessage
            tool_message = {"tool_call_id": tool_call_id, "type": "tool", "content": text_answer}
            return {
                "full_history": [tool_message, HumanMessage(content=text_answer)], 
                "conversation": [HumanMessage(content=text_answer)]
            }
        else:
            # For v1: original behavior - tool message contains the full answer_content dict
            tool_message = {"tool_call_id": tool_call_id, "type": "tool", "content": answer_content}
            return {"full_history": [tool_message], "conversation": [HumanMessage(content=text_answer)]}
    elif answer_type == 'payload':
        # Payload behavior is the same for both versions
        tool_message = {"tool_call_id": tool_call_id, "type": "tool", "content": answer_content}
        return {"full_history": [tool_message]}
    else:
        raise ValueError(f"Invalid answer type: {answer_type}")


async def stop_execution(state, config: RunnableConfig):
    """
    Handler for the StopExecution tool.

    This function is triggered when a stop signal is detected.
    It gracefully terminates the execution and routes to the END node.

    Args:
        state: The current state
        config: Configuration for the runnable

    Returns:
        Command to route to the END node with stop status
    """
    logger.info("Processing stop_execution function")
    # Log thread_id from config if available for debugging
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")
    logger.info(f"Stop signal received for thread {thread_id}")

    tool_call = get_next_pending_tool_call(state["full_history"], "StopExecution")

    if not tool_call:
        logger.warning("No StopExecution tool call found in state history")
        return state

    arguments = tool_call["args"]
    reason = arguments.get("reason", "Stop signal received")

    logger.info("Stopping execution. Reason: %s", reason)

    answer = interrupt({"tool_call": tool_call})
    logger.info("User message interrupt resolved, continuing execution")

    # Get agent version from config
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    
    return _get_state_update_from_answer(answer, tool_call["id"], agent_version)

async def wait_for_user(state, config: RunnableConfig):
    """
    Handler for the WaitForUser tool (v2 agents).

    This function simply pauses execution and waits for user input.
    Unlike EnterIdleState, it assumes the message has already been sent
    via the agent's regular text response.

    Args:
        state: The current state
        config: Configuration for the runnable

    Returns:
        Updated state after handling the tool call
    """
    logger.info("Processing wait_for_user function")
    
    tool_call = get_next_pending_tool_call(state["full_history"], "WaitForUser")
    
    if not tool_call:
        logger.warning("No WaitForUser tool call found in state history")
        return state
    
    # Get agent version from config
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    
    # WaitForUser has no parameters - just interrupt and wait
    answer = interrupt({"tool_call": tool_call})
    logger.info("User response received: %s", str(answer)[:50] + ("..." if len(answer) > 50 else ""))
    
    return _get_state_update_from_answer(answer, tool_call["id"], agent_version)


def get_whatsapp_template_data(node_config, template_name):
    """
    Get the WhatsApp template data for a given template name.
    """
    if "whatsapp_templates" in node_config:
        for template in node_config["whatsapp_templates"]:
            if template["template_name"] == template_name:
                return template
    if "subagent" in node_config and "whatsapp_templates" in node_config["subagent"]:
        for template in node_config["subagent"]["whatsapp_templates"]:
            if template["template_name"] == template_name:
                return template
    return None