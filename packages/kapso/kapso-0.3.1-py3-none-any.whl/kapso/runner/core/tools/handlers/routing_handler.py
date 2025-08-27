import logging

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from kapso.runner.core.flow_utils import get_next_pending_tool_call
from kapso.runner.core.node_types.base import node_type_registry

logger = logging.getLogger(__name__)


async def subgraph_router(state, config: RunnableConfig):
    """
    Handler for the MoveToNextNode tool.
    """
    logger.info("Processing subgraph_router")

    configurable = config.get("configurable") or {}

    tool_call = get_next_pending_tool_call(state["full_history"], "MoveToNextNode")

    if not tool_call:
        logger.warning("No MoveToNextNode tool call found in state history")
        return state

    arguments = tool_call["args"]
    next_node = arguments["next_node"]
    reason = arguments["reason"]

    current_node = state.get("current_node")
    logger.info("Moving to next node: %s", next_node)

    tool_message = {
        "tool_call_id": tool_call["id"],
        "type": "tool",
        "content": {"next_node": next_node, "reason": reason},
    }

    nodes_by_name = configurable.get("nodes_by_name") or {}
    node_edges = configurable.get("node_edges") or {}
    node_config = nodes_by_name.get(next_node)

    if next_node == "__end__" or next_node == "end" or next_node == "END":
        return Command(
            update={"full_history": [tool_message], "current_node": nodes_by_name[next_node]},
            goto="__end__",
        )

    if node_config is None:
        # Get available nodes from current node's edges
        if current_node and current_node.get("name"):
            current_node_name = current_node["name"]
            available_edges = node_edges.get(current_node_name, [])
            # Extract just the "to" node names from the edge dictionaries
            available_nodes = [edge["to"] for edge in available_edges]
            reason = f"The next node was not found. Must only use connected nodes: {', '.join(available_nodes)}"
            tool_message["content"] = {
                "next_node": "NOT_FOUND",
                "reason": reason,
            }
            return Command(update={"full_history": [tool_message]}, goto=current_node_name)
        else:
            tool_message["content"] = {
                "next_node": "NOT_FOUND",
                "reason": "The next node was not found. Must only use available nodes.",
            }
            return Command(update={"full_history": [tool_message]})

    # Get agent version from config
    agent_version = configurable.get("agent_version", 1)
    
    node_type = node_config.get("type")
    node_type_instance = node_type_registry.create(node_type)
    step_prompt_text = node_type_instance.generate_step_prompt(node_config, node_edges.get(next_node, []), agent_version)

    if agent_version == 2:
        # For v2: Put the step prompt in the tool message content
        tool_message["content"] = step_prompt_text
        state_update = {
            "full_history": [tool_message],
            "current_node": nodes_by_name[next_node],
        }
    else:
        # For v1: Original behavior with separate AIMessage
        step_prompt = AIMessage(content=step_prompt_text)
        state_update = {
            "full_history": [tool_message, step_prompt],
            "current_node": nodes_by_name[next_node],
        }

    if node_type == "HandoffNode":
        state_update["handoff_reason"] = reason

    return Command(update=state_update, goto=next_node)
