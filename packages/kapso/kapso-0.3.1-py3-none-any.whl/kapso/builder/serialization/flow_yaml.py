"""
YAML serialization and deserialization for Flow objects.
"""

import yaml
from typing import Dict, Any, Union

from kapso.builder.flows.flow import Flow
from kapso.builder.flows.edges.edge import Edge
from kapso.builder.flows.nodes.start import StartNode
from kapso.builder.flows.nodes.send_text import SendTextNode
from kapso.builder.flows.nodes.wait_for_response import WaitForResponseNode
from kapso.builder.flows.nodes.decide import DecideNode, Condition
from kapso.builder.flows.nodes.agent import AgentNode, FlowAgentWebhook, FlowAgentMcpServer, FlowAgentKnowledgeBase
from kapso.builder.flows.nodes.send_template import SendTemplateNode
from kapso.builder.flows.nodes.send_interactive import SendInteractiveNode
from kapso.builder.flows.nodes.function import FunctionNode
from kapso.builder.flows.nodes.handoff import HandoffNode
from kapso.builder.ai.field import AIField


def serialize_to_dict(flow: Flow) -> Dict[str, Any]:
    """
    Convert flow to dictionary for YAML serialization.
    
    Args:
        flow: The Flow object to serialize
        
    Returns:
        Dictionary representation of the flow
    """
    return {
        "name": flow.name,
        "description": flow.description,
        "nodes": [node.to_dict() for node in flow.nodes],
        "edges": [edge.to_dict() for edge in flow.edges]
    }


def serialize_to_yaml(flow: Flow) -> str:
    """
    Serialize flow to YAML string.
    
    Args:
        flow: The Flow object to serialize
        
    Returns:
        YAML string representation of the flow
    """
    flow_dict = serialize_to_dict(flow)
    # Remove None values
    flow_dict = _clean_dict(flow_dict)
    return yaml.dump(flow_dict, sort_keys=False, default_flow_style=False)


def deserialize_from_dict(flow_dict: Dict[str, Any]) -> Flow:
    """
    Deserialize flow from dictionary representation.
    
    Args:
        flow_dict: Dictionary representation of a flow
        
    Returns:
        Flow object instance
        
    Raises:
        KeyError: If required fields are missing
        ValueError: If unknown node types are encountered
    """
    name = flow_dict["name"]
    description = flow_dict.get("description")
    
    flow = Flow(name=name, description=description)
    
    # Deserialize nodes
    nodes_data = flow_dict.get("nodes", [])
    for node_data in nodes_data:
        node = _deserialize_node(node_data)
        flow.add_node(node)
    
    # Deserialize edges
    edges_data = flow_dict.get("edges", [])
    for edge_data in edges_data:
        edge = _deserialize_edge(edge_data)
        flow.edges.append(edge)
    
    return flow


def deserialize_from_yaml(yaml_content: str) -> Flow:
    """
    Deserialize flow from YAML string.
    
    Args:
        yaml_content: YAML string representation of a flow
        
    Returns:
        Flow object instance
        
    Raises:
        yaml.YAMLError: If YAML is malformed
    """
    flow_dict = yaml.safe_load(yaml_content)
    return deserialize_from_dict(flow_dict)


def _deserialize_node(node_data: Dict[str, Any]):
    """
    Deserialize a single node from dictionary data.
    
    Args:
        node_data: Dictionary representation of a node
        
    Returns:
        Node instance of appropriate type
        
    Raises:
        ValueError: If node type is unknown
    """
    node_id = node_data["id"]
    data = node_data["data"]
    node_type = data["node_type"]
    config = data["config"]
    
    if node_type == "start":
        return StartNode(
            id=node_id,
        )
    
    elif node_type == "send_text":
        message = config["message"]
        if isinstance(message, dict) and message == {"$ai": {}}:
            # Extract prompt from ai_field_config if available
            ai_field_config = config.get("ai_field_config", {})
            message_config = ai_field_config.get("message", {})
            prompt = message_config.get("prompt", "")
            message = AIField(prompt)
        
        return SendTextNode(
            id=node_id,
            whatsapp_config_id=config["whatsapp_config_id"],
            message=message,
            provider_model_name=config.get("provider_model_name"),
        )
    
    elif node_type == "wait_for_response":
        return WaitForResponseNode(
            id=node_id,
            timeout_seconds=config.get("timeout_seconds"),
        )
    
    elif node_type == "decide":
        # Deserialize conditions
        conditions = []
        for cond_data in config.get("conditions", []):
            conditions.append(Condition(
                label=cond_data["label"],
                description=cond_data["description"]
            ))
        
        return DecideNode(
            id=node_id,
            provider_model_name=config["provider_model_name"],
            conditions=conditions,
            llm_temperature=config.get("llm_temperature"),
            llm_max_tokens=config.get("llm_max_tokens"),
        )
    
    elif node_type == "agent":
        # Deserialize webhooks
        webhooks = []
        for webhook_data in config.get("flow_agent_webhooks", []):
            webhooks.append(FlowAgentWebhook(
                name=webhook_data["name"],
                url=webhook_data["url"],
                headers=webhook_data.get("headers"),
                body=webhook_data.get("body")
            ))
        
        # Deserialize MCP servers
        mcp_servers = []
        for mcp_data in config.get("flow_agent_mcp_servers", []):
            # Handle headers - parse JSON string if needed
            headers = mcp_data.get("headers", {})
            if isinstance(headers, str):
                try:
                    import json
                    headers = json.loads(headers) if headers else {}
                except (json.JSONDecodeError, ValueError):
                    headers = {}
                    
            mcp_servers.append(FlowAgentMcpServer(
                name=mcp_data["name"],
                url=mcp_data["url"],
                description=mcp_data.get("description", ""),
                headers=headers
            ))
        
        # Deserialize knowledge bases
        knowledge_bases = []
        for kb_data in config.get("flow_agent_knowledge_bases", []):
            knowledge_bases.append(FlowAgentKnowledgeBase(
                name=kb_data["name"],
                knowledge_base_text=kb_data["knowledge_base_text"],
                description=kb_data.get("description", "")
            ))
        
        return AgentNode(
            id=node_id,
            system_prompt=config["system_prompt"],
            provider_model_name=config["provider_model_name"],
            temperature=config.get("temperature", 0.0),
            max_iterations=config.get("max_iterations", 80),
            max_tokens=config.get("max_tokens", 8192),
            webhooks=webhooks,
            mcp_servers=mcp_servers,
            knowledge_bases=knowledge_bases,
            reasoning_effort=config.get("reasoning_effort"),
        )
    
    elif node_type == "send_template":
        # Handle AI fields in template_params
        ai_field_config = config.get("ai_field_config", {})
        
        # Handle template_params (can be AIField or dict)
        template_params = config.get("template_params")
        if isinstance(template_params, dict) and template_params == {"$ai": {}}:
            params_config = ai_field_config.get("template_params", {})
            prompt = params_config.get("prompt", "")
            template_params = AIField(prompt)
        
        return SendTemplateNode(
            id=node_id,
            whatsapp_config_id=config["whatsapp_config_id"],
            template_id=config["template_id"],
            template_params=template_params,
            provider_model_name=config.get("provider_model_name"),
        )
    
    elif node_type == "send_interactive":
        # Handle AI fields in body_text, header_text and footer_text
        ai_field_config = config.get("ai_field_config", {})
        
        # Handle body_text (can be AIField or string)
        body_text = config["body_text"]
        if isinstance(body_text, dict) and body_text == {"$ai": {}}:
            body_config = ai_field_config.get("body_text", {})
            prompt = body_config.get("prompt", "")
            body_text = AIField(prompt)
        
        header_text = config.get("header_text")
        if isinstance(header_text, dict) and header_text == {"$ai": {}}:
            header_config = ai_field_config.get("header_text", {})
            prompt = header_config.get("prompt", "")
            header_text = AIField(prompt)
        
        footer_text = config.get("footer_text")
        if isinstance(footer_text, dict) and footer_text == {"$ai": {}}:
            footer_config = ai_field_config.get("footer_text", {})
            prompt = footer_config.get("prompt", "")
            footer_text = AIField(prompt)
        
        return SendInteractiveNode(
            id=node_id,
            whatsapp_config_id=config["whatsapp_config_id"],
            interactive_type=config["interactive_type"],
            body_text=body_text,
            header_text=header_text,
            footer_text=footer_text,
            provider_model_name=config.get("provider_model_name"),
        )
    
    elif node_type == "function":
        return FunctionNode(
            id=node_id,
            function_id=config["function_id"],
            save_response_to=config.get("save_response_to"),
        )
    
    elif node_type == "handoff":
        return HandoffNode(
            id=node_id,
        )
    
    else:
        raise ValueError(f"Unknown node type: {node_type}")


def _deserialize_edge(edge_data: Dict[str, Any]) -> Edge:
    """
    Deserialize a single edge from dictionary data.
    
    Args:
        edge_data: Dictionary representation of an edge
        
    Returns:
        Edge instance
    """
    return Edge(
        source=edge_data["source"],
        target=edge_data["target"],
        label=edge_data["label"],
        flow_condition_id=edge_data.get("flow_condition_id")
    )


def _clean_dict(obj):
    """
    Remove None values from dictionary structures.
    
    Args:
        obj: Object to clean (dict, list, or other)
        
    Returns:
        Cleaned object with None values removed
    """
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if v is not None:
                cleaned[k] = _clean_dict(v)
        return cleaned
    elif isinstance(obj, list):
        return [_clean_dict(item) for item in obj]
    return obj