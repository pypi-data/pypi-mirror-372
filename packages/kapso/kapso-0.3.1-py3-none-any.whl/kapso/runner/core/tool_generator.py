import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from kapso.runner.core.mcp_security import validate_mcp_entry
# from langchain_sandbox import PyodideSandboxTool

from langchain_anthropic.chat_models import convert_to_anthropic_tool

from kapso.runner.core.tool_metadata import ToolMetadata, attach_metadata_to_tool
from kapso.runner.core.tools.file_ops.file_operations import (
    file_find_by_name,
    file_find_in_content,
    file_read,
    file_str_replace,
    file_write,
)
from kapso.runner.core.tools.knowledge_base.kb_retrieval import kb_retrieval
from kapso.runner.core.tools.messaging.ask_user_for_input import AskUserForInput
from kapso.runner.core.tools.messaging.enter_idle_state import EnterIdleState
from kapso.runner.core.tools.messaging.wait_for_user import WaitForUser
from kapso.runner.core.tools.messaging.send_notification_to_user import send_notification_to_user
from kapso.runner.core.tools.messaging.send_media_message import send_media_message
from kapso.runner.core.tools.messaging.send_whatsapp_template import SendWhatsappTemplateMessage
from kapso.runner.core.tools.messaging.stop_execution import StopExecution
from kapso.runner.core.tools.routing.move_to_next_node import MoveToNextNode
from kapso.runner.core.tools.webhook.webhook_request import webhook_request
from kapso.runner.core.tools.webhook.webhook_tool_factory import WebhookToolFactory
from kapso.runner.core.tools.metadata.get_execution_metadata import get_execution_metadata

from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_core.tools import BaseTool
from langchain_core.runnables.config import RunnableConfig

async def load_mcp_tools(node_config: dict) -> list[BaseTool]:
    mcp_servers = node_config.get("subagent", {}).get("mcp_servers", [])
    spec = {}

    # Extract JMESPath queries if they exist
    jmespath_queries = []
    for mcp in mcp_servers:
        if mcp.get("jmespath_queries"):
            jmespath_queries.extend(mcp.get("jmespath_queries", []))

        if mcp.get("id") and mcp.get("url"):
            raw_cfg = {
                "transport": mcp.get("transport_kind", "sse"),
                "url": mcp["url"],
            }
            try:
                #  ➜ validate & pin
                safe_cfg = await validate_mcp_entry(raw_cfg)
            except ValueError as err:
                logger.warning(f"Skipping MCP server {mcp['url']}: {err}")
                continue
            name = mcp.get("name", f"server_{mcp['id']}")
            if mcp.get("jmespath_query"):
                safe_cfg["jmespath_query"] = mcp["jmespath_query"]
            spec[name] = safe_cfg

            # Add optional jmespath_query if present
            if mcp.get("jmespath_query"):
                spec[mcp.get("name", f"server_{mcp.get('id')}")]["jmespath_query"] = mcp.get("jmespath_query")
    if not spec:
        logger.info("No MCP server specification found in node_config.")
        return []
    client = MultiServerMCPClient(spec)
    loaded_mcp_tools = []
    try:
        raw_tools = await client.get_tools()
        for raw_tool in raw_tools:
            tool_name = getattr(raw_tool, "name", "unknown_mcp_tool")
            mcp_metadata = ToolMetadata(
                name=tool_name,
                is_dynamic=True,
                node_type=node_config.get("type", DEFAULT_NODE_TYPE),
                requires_interrupt=False,
                is_mcp_tool=True,
                mcp_spec=spec,
                jmespath_queries=jmespath_queries if jmespath_queries else None
            )
            attach_metadata_to_tool(raw_tool, mcp_metadata)
            loaded_mcp_tools.append(raw_tool)
        logger.info(f"Loaded {len(loaded_mcp_tools)} MCP tools.")
    except Exception as e:
        logger.error(f"Failed to load MCP tools: {e}", exc_info=True)
        return []
    return loaded_mcp_tools

logger = logging.getLogger(__name__)

# Mapping of tool names to interrupt handlers
INTERRUPT_HANDLERS = {
    "AskUserForInput": "ask_user_for_input",
    "MoveToNextNode": "subgraph_router",
    "EnterIdleState": "enter_idle_state",
    "WaitForUser": "wait_for_user",  # Has its own dedicated handler
    "SendWhatsappTemplateMessage": "send_whatsapp_template_message",
    "StopExecution": "stop_execution",
}

@dataclass
class ToolConfig:
    """Configuration for a tool with its interrupt handling properties."""
    tool: Any  # Can be a function or class
    requires_interrupt: bool = False
    interrupt_handler: Optional[str] = None

# Core tools grouped by functionality for reuse
CORE_TOOLS = {
    "messaging": [
        ToolConfig(send_notification_to_user),
        ToolConfig(send_media_message),
        ToolConfig(AskUserForInput, True, "ask_user_for_input"),
    ],
    "messaging_v2": [
        # V2-specific messaging tools (send_notification_to_user is already in base messaging)
    ],
    "file_ops": [
        ToolConfig(file_read),
        ToolConfig(file_write),
        ToolConfig(file_str_replace),
        ToolConfig(file_find_in_content),
        ToolConfig(file_find_by_name),
    ],
    "routing": [
        ToolConfig(MoveToNextNode, True, "subgraph_router"),
        ToolConfig(StopExecution, True, "stop_execution"),
    ],
    "idle": [
        ToolConfig(EnterIdleState, True, "enter_idle_state"),
    ],
    "idle_v2": [
        ToolConfig(WaitForUser, True, "wait_for_user"),  # Uses dedicated wait_for_user handler
    ],
    "knowledge_base": [
        ToolConfig(kb_retrieval),
    ],
    "webhook": [
        ToolConfig(webhook_request),
    ],
    "whatsapp": [
        ToolConfig(SendWhatsappTemplateMessage, True, "send_whatsapp_template_message"),
    ],
    "metadata": [
        ToolConfig(get_execution_metadata),
    ],
    # "code_execution": [
    #     ToolConfig(PyodideSandboxTool(timeout_seconds=15))
    # ]
}

# Node tools defined by composing from core tools
NODE_TOOLS: Dict[str, List[ToolConfig]] = {
    "DefaultNode": [
        *CORE_TOOLS["messaging"],
        *CORE_TOOLS["routing"],
        *CORE_TOOLS["idle"],
        *CORE_TOOLS["metadata"],
    ],
    "WebhookNode": [
        *CORE_TOOLS["messaging"],
        *CORE_TOOLS["routing"],
        *CORE_TOOLS["idle"],
        *CORE_TOOLS["webhook"],
        *CORE_TOOLS["metadata"],
    ],
    "WhatsappTemplateNode": [
        *CORE_TOOLS["messaging"],
        *CORE_TOOLS["routing"],
        *CORE_TOOLS["idle"],
        *CORE_TOOLS["whatsapp"],
        *CORE_TOOLS["metadata"],
    ],
    "KnowledgeBaseNode": [
        *CORE_TOOLS["messaging"],
        *CORE_TOOLS["routing"],
        *CORE_TOOLS["idle"],
        *CORE_TOOLS["knowledge_base"],
        *CORE_TOOLS["metadata"],
    ],
    "WarmEndNode": [
        *CORE_TOOLS["messaging"],  # Now includes AskUserForInput
        *CORE_TOOLS["idle"],
        *CORE_TOOLS["routing"],
        *CORE_TOOLS["metadata"],
    ],
    "SubagentNode": [
        *CORE_TOOLS["messaging"],
        *CORE_TOOLS["routing"],
        *CORE_TOOLS["idle"],
        *CORE_TOOLS["knowledge_base"],
        *CORE_TOOLS["whatsapp"],
        *CORE_TOOLS["metadata"],
        # *CORE_TOOLS["code_execution"],
    ],
    "HandoffNode": [],  # Handoff node doesn't need tools as it just forwards control
}

# Default node type to use if the provided type is not recognized
DEFAULT_NODE_TYPE = "DefaultNode"

def generate_standard_tools_for_node_type(node_type: str, agent_version: int = 1) -> List[Any]:
    """
    Generate standard tools for a specific node type.

    Args:
        node_type: The type of node

    Returns:
        List of standard tools with metadata attached
    """
    tools = []

    # Handle the case where node_type is not recognized
    if node_type not in NODE_TOOLS:
        logger.warning(f"Unknown node type: {node_type}, using {DEFAULT_NODE_TYPE} tools")
        node_type = DEFAULT_NODE_TYPE

    # Create tools with proper metadata
    tools_list = NODE_TOOLS[node_type]
    
    # For v2 agents, filter out certain messaging tools and replace idle tools
    if agent_version == 2:
        # Create a modified tools list for v2 agents
        filtered_tools = []
        for tool_config in tools_list:
            tool_name = getattr(tool_config.tool, "name", None) or getattr(tool_config.tool, "__name__", None) or tool_config.tool.__class__.__name__
            # Skip these tools for v2 agents (but keep send_notification_to_user)
            if tool_name in ["AskUserForInput", "EnterIdleState"]:
                continue
            filtered_tools.append(tool_config)
        
        # Add v2-specific messaging tools if any
        if CORE_TOOLS["messaging_v2"]:
            filtered_tools.extend(CORE_TOOLS["messaging_v2"])
        
        # Add v2-specific idle tool if this node type includes idle tools
        if any(getattr(tc.tool, "__name__", "") == "EnterIdleState" for tc in NODE_TOOLS[node_type]):
            filtered_tools.extend(CORE_TOOLS["idle_v2"])
            
        tools_list = filtered_tools
    
    for tool_config in tools_list:
        tool = tool_config.tool

        # Get tool name - handle both function tools and class-based tools
        if hasattr(tool, "name"):
            tool_name = tool.name
        elif hasattr(tool, "__name__"):
            tool_name = tool.__name__
        else:
            tool_name = tool.__class__.__name__

        # Create metadata
        metadata = ToolMetadata(
            name=tool_name,
            is_dynamic=False,
            node_type=node_type,
            requires_interrupt=tool_config.requires_interrupt,
            interrupt_handler=tool_config.interrupt_handler,
        )

        # Attach metadata and add to list
        attach_metadata_to_tool(tool, metadata)
        tools.append(tool)

    return tools

def generate_dynamic_tools_for_node(
    node_type: str,
    node_name: str,
    node_config: Dict[str, Any]
) -> List[Any]:
    """
    Generate dynamic tools based on node type and configuration.

    Args:
        node_type: The type of node
        node_name: The name of the node
        node_config: The node configuration

    Returns:
        List of dynamically generated tools with metadata attached
    """
    dynamic_tools = []

    # Generate webhook tools for WebhookNode
    if node_type == "WebhookNode" and "webhook" in node_config:
        webhook_config = node_config["webhook"]

        # Create webhook tool
        webhook_tool = WebhookToolFactory.create_tool(
            node_name=node_name,
            webhook_config=webhook_config,
            description_override=node_config.get("description")
        )

        # Create and attach metadata
        metadata = ToolMetadata(
            name=webhook_tool.name,
            is_dynamic=True,
            node_type=node_type,
            node_name=node_name,
            creation_context={"webhook_config": webhook_config},
            requires_interrupt=False,
            jmespath_queries=[{"tool_name": webhook_tool.name, "jmespath_query": webhook_config.get("jmespath_query")}] if webhook_config.get("jmespath_query") else None
        )

        attach_metadata_to_tool(webhook_tool, metadata)
        dynamic_tools.append(webhook_tool)

        if node_config.get("global"):
            original_name = node_config.get("original_name", "global_node_tool")
            global_webhook_tool = WebhookToolFactory.create_tool(
                node_name=original_name,
                webhook_config=webhook_config,
                description_override=node_config.get("description")
            )
            global_metadata = ToolMetadata(
                name=node_config.get("original_name", "global_node_tool"),
                is_dynamic=True,
                node_type=node_type,
                node_name=node_name,
                creation_context={"webhook_config": webhook_config},
                requires_interrupt=False,
                jmespath_queries=[{"tool_name": global_webhook_tool.name, "jmespath_query": webhook_config.get("jmespath_query")}] if webhook_config.get("jmespath_query") else None
            )
            attach_metadata_to_tool(global_webhook_tool, global_metadata)
            dynamic_tools.append(global_webhook_tool)

    # Generate webhook tools for SubagentNode
    elif node_type == "SubagentNode" and "subagent" in node_config and "webhooks" in node_config["subagent"]:
        for webhook_spec in node_config["subagent"]["webhooks"]:
            webhook_config = {
                "url": webhook_spec.get("url"),
                "method": webhook_spec.get("http_method", "GET"),
                "headers": webhook_spec.get("headers", {}),
                "body": webhook_spec.get("body", ""),
                "body_schema": webhook_spec.get("body_schema", {}),
                "mock_response_enabled": webhook_spec.get("mock_response_enabled", False),
                "mock_response": webhook_spec.get("mock_response"),
                "jmespath_query": webhook_spec.get("jmespath_query"),
            }

            webhook_name = webhook_spec.get("name", "subagent_webhook")

            # Create webhook tool
            webhook_tool = WebhookToolFactory.create_tool(
                node_name=webhook_name,
                webhook_config=webhook_config,
                description_override=webhook_spec.get("description")
            )

            # Create and attach metadata
            metadata = ToolMetadata(
                name=webhook_tool.name,
                is_dynamic=True,
                node_type=node_type,
                node_name=node_name,
                creation_context={"webhook_config": webhook_config},
                requires_interrupt=False,
                jmespath_queries=[{"tool_name": webhook_tool.name, "jmespath_query": webhook_spec.get("jmespath_query")}] if webhook_spec.get("jmespath_query") else None
            )
            attach_metadata_to_tool(webhook_tool, metadata)

            dynamic_tools.append(webhook_tool)

    return dynamic_tools

async def generate_tools_for_node(
    node_type: str,
    node_name: str,
    node_config: Dict[str, Any],
    provider: str = "",
    agent_version: int = 1
) -> Dict[str, Any]:
    """
    Generate all tools (standard and dynamic) for a node.

    Args:
        node_type: The type of node
        node_name: The name of the node
        node_config: The node configuration
        provider: The LLM provider (e.g., "Anthropic", "OpenAI")

    Returns:
        Dictionary containing categorized tools:
        - "standard": List of standard tools
        - "dynamic": List of dynamically generated tools
        - "all": List of all tools combined
        - "formatted": List of all tools formatted for the provider
    """
    # Generate standard tools
    standard_tools = generate_standard_tools_for_node_type(node_type, agent_version)

    # Generate dynamic tools
    dynamic_tools = generate_dynamic_tools_for_node(node_type, node_name, node_config)

    # Generate MCP tools
    mcp_tools = await load_mcp_tools(node_config)

    # Combine all tools
    all_tools = standard_tools + dynamic_tools + mcp_tools

    # Format tools for the provider if needed
    formatted_tools = all_tools
    if provider.lower() == "anthropic":
        try:
            formatted_tools = [convert_to_anthropic_tool(tool) for tool in all_tools]
        except Exception as e:
            logger.error(f"Error converting tools to Anthropic format: {e}")

    return {
        "standard": standard_tools,
        "dynamic": dynamic_tools,
        "mcp": mcp_tools,
        "all": all_tools,
        "formatted": formatted_tools,
    }

def tool_requires_interrupt(tool: Any) -> bool:
    """
    Check if a tool requires interrupt handling.

    Args:
        tool: The tool to check

    Returns:
        True if the tool requires interrupt handling
    """
    if hasattr(tool, "metadata") and hasattr(tool.metadata, "requires_interrupt"):
        return tool.metadata.requires_interrupt

    # Fallback to the tool name
    tool_name = getattr(tool, "name", None)
    if tool_name:
        return tool_name in INTERRUPT_HANDLERS

    return False

def get_interrupt_handler(tool: Any) -> Optional[str]:
    """
    Get the interrupt handler for a tool.

    Args:
        tool: The tool to get the handler for

    Returns:
        The name of the handler function, or None if no handler
    """
    if hasattr(tool, "metadata") and hasattr(tool.metadata, "interrupt_handler"):
        return tool.metadata.interrupt_handler

    # Fallback to the tool name
    tool_name = getattr(tool, "name", None)
    if tool_name:
        return INTERRUPT_HANDLERS.get(tool_name)

    return None

def find_tool_by_name(tool_name: str, tools: List[Any]) -> Optional[Any]:
    """
    Find a tool by name in a list of tools.

    Args:
        tool_name: The name of the tool to find
        tools: List of tools to search

    Returns:
        The tool if found, None otherwise
    """
    for tool in tools:
        if hasattr(tool, "name") and tool.name == tool_name:
            return tool

    return None

async def invoke_mcp_tool(
    mcp_tool_instance: BaseTool,
    tool_args: Dict[str, Any],
    config: RunnableConfig
) -> Any:
    tool_name = mcp_tool_instance.name

    if not hasattr(mcp_tool_instance, 'metadata'):
        raise ValueError(f"No metadata found for tool {tool_name}")

    metadata = mcp_tool_instance.metadata
    if isinstance(metadata, ToolMetadata):
        mcp_spec = metadata.mcp_spec
    elif isinstance(metadata, dict):
        mcp_spec = metadata.get('mcp_spec')
    else:
        raise ValueError(f"Invalid metadata format for tool {tool_name}")

    if not mcp_spec:
        raise ValueError(f"MCP spec not found in metadata for tool {tool_name}")

    for server_cfg in mcp_spec.values():
        try:
            await validate_mcp_entry(server_cfg)
        except ValueError as err:
            raise ValueError(f"MCP server validation failed at runtime: {err}") from err

    logger.info(f"Invoking MCP tool {tool_name} by re-creating client with spec: {mcp_spec}")

    mcp_client = MultiServerMCPClient(mcp_spec)
    live_mcp_tools = await mcp_client.get_tools()
    actual_tool_to_invoke = find_tool_by_name(tool_name, live_mcp_tools)

    if not actual_tool_to_invoke:
        raise ValueError(f"MCP tool {tool_name} not found in re-created client context.")

    # Convert ToolMetadata → dict if needed
    if hasattr(actual_tool_to_invoke, "metadata") and \
        isinstance(actual_tool_to_invoke.metadata, ToolMetadata):
        actual_tool_to_invoke.metadata = actual_tool_to_invoke.metadata.__dict__.copy()

    return await actual_tool_to_invoke.ainvoke({**tool_args}, config=config)
