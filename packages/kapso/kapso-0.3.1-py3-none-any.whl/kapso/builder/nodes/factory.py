"""
Factory functions for creating nodes in the Kapso SDK.
"""

from typing import Dict, List, Optional, Any, Union

from kapso.builder.nodes.base import (
    Node,
    NodeType,
    WebhookConfig,
    KnowledgeBaseConfig,
    HandoffConfig,
    WarmEndConfig,
    WhatsAppTemplateConfig
)
from kapso.builder.nodes.subagent import (
    SubagentNode,
    SubagentTool,
    WebhookTool,
    KnowledgeBaseTool,
    McpServerTool,
    WhatsappTemplateTool,
)


def DefaultNode(
    name: str,
    prompt: Optional[str] = None,
    global_: bool = False,
    global_condition: Optional[str] = None
) -> Node:
    """
    Create a default node.
    
    Args:
        name: Node name
        prompt: Node prompt
        global_: Whether the node is global
        global_condition: Condition for global node
        
    Returns:
        A Node instance
    """
    return Node(
        name=name,
        type=NodeType.DEFAULT,
        prompt=prompt,
        global_=global_,
        global_condition=global_condition
    )


def WebhookNode(
    name: str,
    url: str,
    http_method: str,
    prompt: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
    body_schema: Optional[Dict[str, Any]] = None,
    jmespath_query: Optional[str] = None,
    mock_response: Optional[Dict[str, Any]] = None,
    mock_response_enabled: bool = False,
    global_: bool = False,
    global_condition: Optional[str] = None
) -> Node:
    """
    Create a webhook node.
    
    Args:
        name: Node name
        url: Webhook URL
        http_method: HTTP method (GET, POST, etc.)
        prompt: Node prompt
        headers: HTTP headers
        body: HTTP request body
        body_schema: JSON Schema for request body validation
        jmespath_query: JMESPath query to filter/transform the response
        mock_response: Mock response for testing
        mock_response_enabled: Whether to use mock response
        global_: Whether the node is global
        global_condition: Condition for global node
        
    Returns:
        A Node instance
    """
    webhook_config = WebhookConfig(
        url=url,
        http_method=http_method,
        headers=headers,
        body=body,
        body_schema=body_schema,
        jmespath_query=jmespath_query,
        mock_response=mock_response,
        mock_response_enabled=mock_response_enabled
    )
    
    return Node(
        name=name,
        type=NodeType.WEBHOOK,
        prompt=prompt,
        global_=global_,
        global_condition=global_condition,
        webhook=webhook_config
    )


def KnowledgeBaseNode(
    name: str,
    knowledge_base_text: Optional[str] = None,
    knowledge_base_file: Optional[str] = None,
    prompt: Optional[str] = None,
    global_: bool = False,
    global_condition: Optional[str] = None
) -> Node:
    """
    Create a knowledge base node.
    
    Args:
        name: Node name
        knowledge_base_text: Knowledge base text content
        knowledge_base_file: Knowledge base file path
        prompt: Node prompt
        global_: Whether the node is global
        global_condition: Condition for global node
        
    Returns:
        A Node instance
    """
    if not knowledge_base_text and not knowledge_base_file:
        raise ValueError("Either knowledge_base_text or knowledge_base_file must be provided")
        
    kb_config = KnowledgeBaseConfig(
        knowledge_base_text=knowledge_base_text,
        knowledge_base_file=knowledge_base_file
    )
    
    return Node(
        name=name,
        type=NodeType.KNOWLEDGE_BASE,
        prompt=prompt,
        global_=global_,
        global_condition=global_condition,
        knowledge_base=kb_config
    )


def HandoffNode(
    name: str,
    global_: bool = False,
    global_condition: Optional[str] = None
) -> Node:
    """
    Create a handoff node.
    
    Args:
        name: Node name
        global_: Whether the node is global
        global_condition: Condition for global node
        
    Returns:
        A Node instance
    """
    handoff_config = HandoffConfig()
    
    return Node(
        name=name,
        type=NodeType.HANDOFF,
        prompt=None,  # HandoffNode doesn't use a prompt
        global_=global_,
        global_condition=global_condition,
        handoff=handoff_config
    )


def WarmEndNode(
    name: str,
    timeout_minutes: int,
    prompt: Optional[str] = None,
    global_: bool = False,
    global_condition: Optional[str] = None
) -> Node:
    """
    Create a warm end node.
    
    Args:
        name: Node name
        timeout_minutes: Timeout in minutes
        prompt: Node prompt
        global_: Whether the node is global
        global_condition: Condition for global node
        
    Returns:
        A Node instance
    """
    warm_end_config = WarmEndConfig(
        timeout_minutes=timeout_minutes
    )
    
    return Node(
        name=name,
        type=NodeType.WARM_END,
        prompt=prompt,
        global_=global_,
        global_condition=global_condition,
        warm_end=warm_end_config
    )


def create_subagent_node(
    name: str,
    prompt: Optional[str] = None,
    global_: bool = False,
    global_condition: Optional[str] = None,
    tools: Optional[List[SubagentTool]] = None,
    tools_dict: Optional[List[Dict[str, Any]]] = None
) -> SubagentNode:
    """
    Create a subagent node with tools.
    
    Args:
        name: Node name
        prompt: Node prompt
        global_: Whether the node is global
        global_condition: Condition for global node
        tools: List of SubagentTool instances
        tools_dict: List of tool dictionaries for simpler creation
        
    Returns:
        A SubagentNode instance
        
    Example:
        # Using tool objects
        node = create_subagent_node(
            name="helper",
            tools=[
                WebhookTool(name="api", url="https://api.example.com"),
                KnowledgeBaseTool(name="docs", knowledge_base_text="...")
            ]
        )
        
        # Using dictionaries
        node = create_subagent_node(
            name="helper",
            tools_dict=[
                {"type": "webhook", "name": "api", "url": "https://api.example.com"},
                {"type": "knowledge_base", "name": "docs", "knowledge_base_text": "..."}
            ]
        )
    """
    if tools and tools_dict:
        raise ValueError("Provide either 'tools' or 'tools_dict', not both")
    
    subagent = SubagentNode(
        name=name,
        prompt=prompt,
        global_=global_,
        global_condition=global_condition
    )
    
    # Add tools from list
    if tools:
        for tool in tools:
            subagent.add_tool(tool)
    
    # Create tools from dictionaries
    elif tools_dict:
        for tool_dict in tools_dict:
            # Make a copy to avoid modifying the original
            tool_dict_copy = tool_dict.copy()
            tool_type = tool_dict_copy.pop("type", None)
            if not tool_type:
                raise ValueError("Tool dictionary must have a 'type' field")
            
            if tool_type == "webhook":
                tool = WebhookTool(**tool_dict_copy)
            elif tool_type == "knowledge_base":
                tool = KnowledgeBaseTool(**tool_dict_copy)
            elif tool_type == "mcp_server":
                tool = McpServerTool(**tool_dict_copy)
            elif tool_type == "whatsapp_template":
                tool = WhatsappTemplateTool(**tool_dict_copy)
            else:
                raise ValueError(f"Unknown tool type: {tool_type}")
            
            subagent.add_tool(tool)
    
    return subagent


def WhatsAppTemplateNode(
    name: str,
    template_name: str,
    phone_number: str,
    template_parameters: Optional[Dict[str, str]] = None,
    wait_for_response: bool = False,
    whatsapp_config_id: Optional[str] = None,
    whatsapp_template_id: Optional[str] = None,
    prompt: Optional[str] = None,
    global_: bool = False,
    global_condition: Optional[str] = None
) -> Node:
    """
    Create a WhatsApp template node.
    
    Args:
        name: Node name
        template_name: WhatsApp template name
        phone_number: Recipient phone number (can use placeholders like {{phone}})
        template_parameters: Parameters for the template
        wait_for_response: Whether to wait for user response
        whatsapp_config_id: WhatsApp configuration ID (required for deployment)
        whatsapp_template_id: WhatsApp template ID (required for deployment)
        prompt: Node prompt
        global_: Whether the node is global
        global_condition: Condition for global node
        
    Returns:
        A Node instance
    """
    whatsapp_config = WhatsAppTemplateConfig(
        template_name=template_name,
        phone_number=phone_number,
        template_parameters=template_parameters or {},
        wait_for_response=wait_for_response,
        whatsapp_config_id=whatsapp_config_id,
        whatsapp_template_id=whatsapp_template_id
    )
    
    return Node(
        name=name,
        type=NodeType.WHATSAPP_TEMPLATE,
        prompt=prompt,
        global_=global_,
        global_condition=global_condition,
        whatsapp_template=whatsapp_config
    )
