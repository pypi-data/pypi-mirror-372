"""
Generic handler for tools that don't require interrupt nodes.
"""

import json
import logging
import jmespath
from typing import Any
from langchain_core.messages import AIMessage
from langchain_core.runnables.config import RunnableConfig

from kapso.runner.core.tool_metadata import ToolMetadata
from kapso.runner.core.flow_utils import get_next_pending_tool_call
from kapso.runner.core.tool_generator import (
    generate_tools_for_node,
    tool_requires_interrupt,
    find_tool_by_name,
    invoke_mcp_tool,
)
from kapso.runner.core.tools.file_ops.file_operations import (
    file_find_by_name,
    file_find_in_content,
    file_read,
    file_str_replace,
    file_write,
)
from kapso.runner.core.tools.knowledge_base.kb_retrieval import kb_retrieval
from kapso.runner.core.tools.messaging.send_notification_to_user import send_notification_to_user
from kapso.runner.core.tools.messaging.send_media_message import send_media_message
from kapso.runner.core.tools.webhook.webhook_request import webhook_request

logger = logging.getLogger(__name__)

# Define a mapping of tools to their required injected arguments
TOOL_INJECTED_ARGS = {
    "webhook_request": lambda state: {
        "mock_response_enabled": state.get("current_node", {})
        .get("webhook", {})
        .get("mock_response_enabled", False),
        "mock_response": state.get("current_node", {})
        .get("webhook", {})
        .get("mock_response", None),
    },
    # Additional tools with injected args can be added here
}

async def get_tools_for_current_node(state, config):
    """
    Generate tools for the current node.
    
    Args:
        state: The current state
        config: The runnable configuration
        
    Returns:
        Dictionary of tools for the current node
    """
    current_node = state.get("current_node", {})
    node_type = current_node.get("type", "DefaultNode")
    node_name = current_node.get("name", "unknown")
    
    # Get LLM provider information
    llm_config = config.get("configurable", {}).get("llm_config", {})
    provider = llm_config.get("provider_name", "")
    
    # Get agent version from config
    agent_version = config.get("configurable", {}).get("agent_version", 1)
    
    # Generate tools using tool generator
    return await generate_tools_for_node(
        node_type=node_type,
        node_name=node_name,
        node_config=current_node,
        provider=provider,
        agent_version=agent_version
    )

def apply_jmespath_query(tool_name: str, result: Any, tool_instance: Any) -> Any:
    """
    Apply JMESPath query to the tool result if a query exists for this tool.
    
    Args:
        tool_name: The name of the tool
        result: The original result from the tool
        tool_instance: The tool instance that may have JMESPath queries
        
    Returns:
        Transformed result if a query exists, otherwise the original result
    """
    if not hasattr(tool_instance, 'metadata'):
        return result
        
    metadata = tool_instance.metadata
    jmespath_queries = None
    
    # Extract jmespath_queries from metadata
    if isinstance(metadata, ToolMetadata):
        jmespath_queries = metadata.jmespath_queries
    elif isinstance(metadata, dict) and 'jmespath_queries' in metadata:
        jmespath_queries = metadata['jmespath_queries']
    
    if not jmespath_queries:
        return result
    
    # Find a matching query for this tool
    matching_query = None
    for query_obj in jmespath_queries:
        if query_obj.get("tool_name") == tool_name:
            matching_query = query_obj.get("jmespath_query")
            break
    if matching_query:
        logger.info(f"Applying JMESPath query '{matching_query}' to result of tool '{tool_name}'")
        try:
            # If the result is a string that looks like JSON, parse it first
            if isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    # Try to apply query to content first if it exists
                    if isinstance(parsed_result, dict) and 'content' in parsed_result:
                        content_result = jmespath.search(matching_query, parsed_result['content'])
                        if content_result is not None:
                            return content_result
                    # If no content or query returned None, try on full result
                    transformed_result = jmespath.search(matching_query, parsed_result)
                    return transformed_result
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse tool result as JSON, skipping JMESPath query: {result}")
                    return result
            else:
                # Try to apply query to content first if it exists
                if isinstance(result, dict) and 'content' in result:
                    content_result = jmespath.search(matching_query, result['content'])
                    if content_result is not None:
                        return content_result
                # If no content or query returned None, try on full result
                transformed_result = jmespath.search(matching_query, result)
                return transformed_result
        except Exception as e:
            logger.error(f"Error applying JMESPath query: {e}", exc_info=True)
    
    return result

async def generic_tool_handler(state, config: RunnableConfig):
    """
    Generic handler for tool calls that don't require interrupt nodes.
    This handler processes multiple non-interrupt tool calls in sequence,
    and routes to a interrupt node when necessary.

    Args:
        state: The current state

    Returns:
        Updated state after handling the tool calls
    """
    logger.info("Processing generic tool handler")

    # Get agent version first
    agent_version = config.get("configurable", {}).get("agent_version", 1)

    # Standard tools mapping - tools we can directly invoke here
    tools_by_name = {
        "webhook_request": webhook_request,
        "file_read": file_read,
        "file_write": file_write,
        "file_str_replace": file_str_replace,
        "file_find_in_content": file_find_in_content,
        "file_find_by_name": file_find_by_name,
        "kb_retrieval": kb_retrieval,
        "send_media_message": send_media_message,
        "send_notification_to_user": send_notification_to_user,
    }

    # Generate tools for the current node
    node_tools = await get_tools_for_current_node(state, config)
    all_node_tools = node_tools.get("all", [])

    # Track which tool call IDs we've processed in this execution
    processed_ids = []

    # Initialize state updates
    state_update = {"full_history": [], "conversation": []}

    # Keep processing tool calls until we find one that requires a interrupt node
    # or until there are no more pending tool calls
    while True:
        # Get the next pending tool call, excluding ones we've already processed
        pending_tool_call = get_next_pending_tool_call(
            state["full_history"], processed_ids=processed_ids
        )

        if not pending_tool_call:
            logger.info("No more pending tool calls to process")
            break

        tool_name = pending_tool_call["name"]
        tool_id = pending_tool_call["id"]
        tool_args = pending_tool_call["args"]

        # Find the tool in all_node_tools
        tool_instance = find_tool_by_name(tool_name, all_node_tools)
        
        # Check if this tool requires a interrupt node
        if tool_instance and tool_requires_interrupt(tool_instance):
            logger.info(f"Tool {tool_name} requires a interrupt node, returning state update")
            # We'll let the node_fn handle the routing to the interrupt node
            break
            
        # Fallback check for standard tools
        if tool_name in ["AskUserForInput", "MoveToNextNode", "EnterIdleState", "WaitForUser", "SendWhatsappTemplateMessage"]:
            logger.info(f"Standard interrupt tool {tool_name} detected, returning state update")
            break

        # If we reach here, this is a non-interrupt tool that we can handle directly
        logger.info(f"Processing non-interrupt tool: {tool_name}")

        result = None
        error_occurred = False
        try:
            # Check if this tool requires injected arguments
            tool_args_to_inject = TOOL_INJECTED_ARGS.get(tool_name, lambda _: {})(state)
            # Only inject state for non-MCP tools
            is_mcp_tool = False
            if tool_instance:
                if hasattr(tool_instance, 'metadata'):
                    metadata = tool_instance.metadata
                    if isinstance(metadata, ToolMetadata):
                        is_mcp_tool = metadata.is_mcp_tool
                    elif isinstance(metadata, dict):
                        is_mcp_tool = metadata.get('is_mcp_tool', False)

            if is_mcp_tool:
                if not tool_instance:
                    raise ValueError(f"Tool instance for MCP tool {tool_name} is unexpectedly None.")
                result = await invoke_mcp_tool(tool_instance, tool_args, config)
            else:
                tool_func = tools_by_name.get(tool_name) or tool_instance
                if not tool_func:
                    raise ValueError(f"Unknown tool: {tool_name}")
                tool_args_to_inject["state"] = state
                if tool_args_to_inject:
                    logger.info(f"Injecting arguments for {tool_name}: {tool_args_to_inject.keys()}")
                if hasattr(tool_func, "metadata") and isinstance(tool_func.metadata, ToolMetadata):
                    tool_func.metadata = tool_func.metadata.__dict__.copy()
                result = await tool_func.ainvoke({**tool_args, **tool_args_to_inject}, config=config)
            result = apply_jmespath_query(tool_name, result, tool_instance)
            tool_message_content = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            tool_message = {
                "tool_call_id": tool_id,
                "type": "tool",
                "content": tool_message_content,
            }
            # Track sent messages in conversation history for both v1 and v2
            if tool_name == "send_notification_to_user":
                message_content = tool_args.get("message", str(result))
                state_update["conversation"].append(AIMessage(content=message_content))
            elif tool_name == "send_media_message":
                message_content = tool_args.get("message", str(result))
                state_update["conversation"].append(AIMessage(content=message_content))
        except Exception as e:
            error_message = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_message, exc_info=True)
            tool_message = {"tool_call_id": tool_id, "type": "tool", "content": error_message}
            error_occurred = True
        state_update["full_history"].append(tool_message)
        processed_ids.append(tool_id)

    # Return the accumulated state updates
    return state_update
