"""
YAML serialization and deserialization for the Kapso SDK.
"""

import json
import yaml
from typing import Dict, Any

from kapso.builder.agent.agent import Agent
from kapso.builder.nodes.factory import (
    DefaultNode,
    WebhookNode,
    KnowledgeBaseNode,
    HandoffNode,
    WarmEndNode,
    WhatsAppTemplateNode
)
from kapso.builder.nodes.subagent import (
    SubagentNode,
    WebhookTool,
    KnowledgeBaseTool,
    McpServerTool,
    WhatsappTemplateTool,
    JmespathQuery
)


def serialize_to_dict(agent: Agent) -> Dict[str, Any]:
    """
    Serialize an agent to a dictionary with snake_case keys.
    
    Args:
        agent: The agent to serialize
        
    Returns:
        A dictionary representation of the agent
    """
    agent_dict = {
        "name": agent.name,
        "system_prompt": agent.system_prompt if agent.system_prompt else None,
        "message_debounce_seconds": agent.message_debounce_seconds,
        "graph": {
            "nodes": [],
            "edges": []
        }
    }
    
    # Add description if present
    if hasattr(agent, 'description') and agent.description:
        agent_dict["description"] = agent.description
    
    for node in agent.nodes:
        # Create base node dictionary
        node_dict = {
            "name": node.name,
            "type": node.type.value if hasattr(node.type, 'value') else str(node.type),
            "prompt": node.prompt,
            "global": node.global_,
            "global_condition": node.global_condition
        }
        
        # Add description if it exists
        if hasattr(node, 'description') and node.description:
            node_dict["description"] = node.description
        
        if node.webhook:
            node_dict["webhook"] = {
                "url": node.webhook.url,
                "http_method": node.webhook.http_method,
                "jmespath_query": node.webhook.jmespath_query,
                "mock_response_enabled": node.webhook.mock_response_enabled
            }
            
            # Serialize these fields as JSON strings
            if node.webhook.headers:
                node_dict["webhook"]["headers"] = json.dumps(node.webhook.headers)
            if node.webhook.body:
                node_dict["webhook"]["body"] = json.dumps(node.webhook.body)
            if node.webhook.body_schema:
                node_dict["webhook"]["body_schema"] = json.dumps(node.webhook.body_schema)
            if node.webhook.mock_response:
                node_dict["webhook"]["mock_response"] = json.dumps(node.webhook.mock_response)
        
        if node.knowledge_base:
            node_dict["knowledge_base"] = {}
            
            # If file is specified, read its content and serialize as text
            if node.knowledge_base.knowledge_base_file:
                try:
                    with open(node.knowledge_base.knowledge_base_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    node_dict["knowledge_base"]["knowledge_base_text"] = file_content
                except Exception:
                    # If file can't be read, fall back to original behavior
                    if node.knowledge_base.knowledge_base_text:
                        node_dict["knowledge_base"]["knowledge_base_text"] = node.knowledge_base.knowledge_base_text
                    node_dict["knowledge_base"]["knowledge_base_file"] = node.knowledge_base.knowledge_base_file
            elif node.knowledge_base.knowledge_base_text:
                node_dict["knowledge_base"]["knowledge_base_text"] = node.knowledge_base.knowledge_base_text
        
        if node.warm_end:
            node_dict["warm_end"] = {
                "timeout_minutes": node.warm_end.timeout_minutes
            }
        
        if node.handoff:
            node_dict["handoff"] = {}
        
        if node.whatsapp_template:
            node_dict["whatsapp_template"] = {
                "template_name": node.whatsapp_template.template_name,
                "phone_number": node.whatsapp_template.phone_number,
                "template_parameters": node.whatsapp_template.template_parameters,
                "wait_for_response": node.whatsapp_template.wait_for_response
            }
            
            if node.whatsapp_template.whatsapp_config_id:
                node_dict["whatsapp_template"]["whatsapp_config_id"] = node.whatsapp_template.whatsapp_config_id
                
            if node.whatsapp_template.whatsapp_template_id:
                node_dict["whatsapp_template"]["whatsapp_template_id"] = node.whatsapp_template.whatsapp_template_id
        
        # Handle SubagentNode
        if isinstance(node, SubagentNode):
            # Group tools by type for serialization
            webhooks = []
            knowledge_bases = []
            mcp_servers = []
            whatsapp_templates = []
            
            for tool in node.tools:
                if isinstance(tool, WebhookTool):
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "url": tool.url,
                        "http_method": tool.http_method,
                        "mock_response_enabled": tool.mock_response_enabled,
                        "jmespath_query": tool.jmespath_query
                    }
                    
                    # Serialize these fields as JSON strings
                    if tool.headers:
                        tool_dict["headers"] = json.dumps(tool.headers)
                    if tool.body:
                        tool_dict["body"] = json.dumps(tool.body)
                    if tool.body_schema:
                        tool_dict["body_schema"] = json.dumps(tool.body_schema)
                    if tool.mock_response:
                        tool_dict["mock_response"] = json.dumps(tool.mock_response)
                    
                    webhooks.append(tool_dict)
                elif isinstance(tool, KnowledgeBaseTool):
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                    }
                    # Only add text/file fields if they have values
                    if tool.knowledge_base_text:
                        tool_dict["knowledge_base_text"] = tool.knowledge_base_text
                    if tool.knowledge_base_file:
                        tool_dict["knowledge_base_file"] = tool.knowledge_base_file
                    knowledge_bases.append(tool_dict)
                elif isinstance(tool, McpServerTool):
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "url": tool.url,
                        "transport_kind": tool.transport_kind,
                        "jmespath_queries": [
                            {
                                "tool_name": q.tool_name,
                                "jmespath_query": q.jmespath_query
                            } for q in tool.jmespath_queries
                        ]
                    }
                    mcp_servers.append(tool_dict)
                elif isinstance(tool, WhatsappTemplateTool):
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "template_name": tool.template_name,
                        "phone_number": tool.phone_number,
                        "wait_for_response": tool.wait_for_response
                    }
                    # Only add optional fields if they have values
                    if tool.template_parameters:
                        tool_dict["template_parameters"] = tool.template_parameters
                    if tool.whatsapp_config_id:
                        tool_dict["whatsapp_config_id"] = tool.whatsapp_config_id
                    if tool.whatsapp_template_id:
                        tool_dict["whatsapp_template_id"] = tool.whatsapp_template_id
                    whatsapp_templates.append(tool_dict)
            
            node_dict["subagent"] = {
                "webhooks": webhooks,
                "knowledge_bases": knowledge_bases,
                "mcp_servers": mcp_servers,
                "whatsapp_templates": whatsapp_templates
            }
        
        agent_dict["graph"]["nodes"].append(node_dict)
    
    for edge in agent.edges:
        # Extract node names from source and target
        # Handle both string names and node objects
        source_name = edge.source if isinstance(edge.source, str) else edge.source.name
        target_name = edge.target if isinstance(edge.target, str) else edge.target.name
        
        edge_dict = {
            "from": source_name,
            "to": target_name
        }
        
        if edge.condition:
            edge_dict["condition"] = edge.condition
            edge_dict["label"] = edge.condition
        
        agent_dict["graph"]["edges"].append(edge_dict)
    
    return agent_dict


def _clean_dict(obj):
    """Recursively clean a dictionary to ensure it's serializable."""
    if isinstance(obj, dict):
        return {k: _clean_dict(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [_clean_dict(item) for item in obj if item is not None]
    elif isinstance(obj, str):
        # Return strings as-is to preserve newlines and Unicode
        return obj
    elif isinstance(obj, (int, float, bool)):
        return obj
    elif obj is None:
        return None
    else:
        # For any other type, convert to string
        return str(obj)


def serialize_to_yaml(agent: Agent) -> str:
    """
    Serialize an agent to YAML.
    
    Args:
        agent: The agent to serialize
        
    Returns:
        A YAML string representation of the agent
    """
    agent_dict = serialize_to_dict(agent)
    
    # Clean the dictionary to ensure all values are serializable
    agent_dict = _clean_dict(agent_dict)
    
    # Custom YAML representer for multiline strings
    def str_representer(dumper, data):
        # Debug: Check what we're getting
        # print(f"String repr called with: {repr(data[:50])}" if len(data) > 50 else f"String repr called with: {repr(data)}")
        
        # Use literal block scalar style for multiline strings
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    # Create a custom YAML dumper
    class LiteralDumper(yaml.SafeDumper):
        pass
    
    # Add the custom string representer
    LiteralDumper.add_representer(str, str_representer)
    
    # Add a custom representer for any object that shouldn't be in the final dict
    def fallback_representer(dumper, data):
        # This should not happen if serialize_to_dict works correctly
        # But if it does, convert the object to a string representation
        return dumper.represent_str(str(data))
    
    # Add fallback for all node types and tool types
    from kapso.builder.nodes.subagent import SubagentNode, WebhookTool, KnowledgeBaseTool, McpServerTool, WhatsappTemplateTool
    from kapso.builder.nodes.factory import DefaultNode, WebhookNode, KnowledgeBaseNode, HandoffNode, WarmEndNode, WhatsAppTemplateNode
    
    # Register all node types
    for node_type in [SubagentNode, DefaultNode, WebhookNode, KnowledgeBaseNode, HandoffNode, WarmEndNode, WhatsAppTemplateNode]:
        LiteralDumper.add_representer(node_type, fallback_representer)
    
    # Register all tool types
    for tool_type in [WebhookTool, KnowledgeBaseTool, McpServerTool, WhatsappTemplateTool]:
        LiteralDumper.add_representer(tool_type, fallback_representer)
    
    try:
        return yaml.dump(
            agent_dict, 
            Dumper=LiteralDumper, 
            sort_keys=False, 
            default_flow_style=False, 
            width=120,
            allow_unicode=True  # Ensure proper Unicode handling
        )
    except Exception as e:
        # Debug: Print the problematic data
        import json
        print(f"Error serializing to YAML: {e}")
        print("Agent dict structure:")
        print(json.dumps(agent_dict, indent=2, default=str))
        raise


def deserialize_from_dict(agent_dict: Dict[str, Any]) -> Agent:
    """
    Deserialize an agent from a dictionary.
    
    Args:
        agent_dict: Dictionary representation of an agent
        
    Returns:
        An Agent instance
    """
    name = agent_dict.get("name") or ""
    system_prompt = agent_dict.get("system_prompt")
    message_debounce_seconds = agent_dict.get("message_debounce_seconds")
    
    agent = Agent(
        name=name,
        system_prompt=system_prompt,
        message_debounce_seconds=message_debounce_seconds
    )
    
    graph = agent_dict.get("graph", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    
    for node_dict in nodes:
        node_name = node_dict.get("name")
        node_type = node_dict.get("type", "DefaultNode")
        prompt = node_dict.get("prompt")
        global_ = node_dict.get("global", False)
        global_condition = node_dict.get("global_condition")
        
        if node_type == "WebhookNode":
            webhook = node_dict.get("webhook", {})
            
            # Parse JSON strings back to objects
            headers = webhook.get("headers")
            if headers and isinstance(headers, str):
                headers = json.loads(headers)
            
            body = webhook.get("body")
            if body and isinstance(body, str):
                body = json.loads(body)
            
            body_schema = webhook.get("body_schema")
            if body_schema and isinstance(body_schema, str):
                body_schema = json.loads(body_schema)
            
            mock_response = webhook.get("mock_response")
            if mock_response and isinstance(mock_response, str):
                mock_response = json.loads(mock_response)
            
            node = WebhookNode(
                name=node_name,
                url=webhook.get("url", ""),
                http_method=webhook.get("http_method", "GET"),
                prompt=prompt,
                headers=headers,
                body=body,
                body_schema=body_schema,
                jmespath_query=webhook.get("jmespath_query"),
                mock_response=mock_response,
                mock_response_enabled=webhook.get("mock_response_enabled", False),
                global_=global_,
                global_condition=global_condition
            )
            
        elif node_type == "KnowledgeBaseNode":
            kb = node_dict.get("knowledge_base", {})
            node = KnowledgeBaseNode(
                name=node_name,
                knowledge_base_text=kb.get("knowledge_base_text"),
                knowledge_base_file=kb.get("knowledge_base_file"),
                prompt=prompt,
                global_=global_,
                global_condition=global_condition
            )
            
        elif node_type == "HandoffNode":
            node = HandoffNode(
                name=node_name,
                global_=global_,
                global_condition=global_condition
            )
            
        elif node_type == "WarmEndNode":
            warm_end = node_dict.get("warm_end", {})
            node = WarmEndNode(
                name=node_name,
                timeout_minutes=warm_end.get("timeout_minutes", 60),
                prompt=prompt,
                global_=global_,
                global_condition=global_condition
            )
            
        elif node_type == "WhatsappTemplateNode":
            whatsapp = node_dict.get("whatsapp_template", {})
            node = WhatsAppTemplateNode(
                name=node_name,
                template_name=whatsapp.get("template_name", ""),
                phone_number=whatsapp.get("phone_number", ""),
                template_parameters=whatsapp.get("template_parameters", {}),
                wait_for_response=whatsapp.get("wait_for_response", False),
                whatsapp_config_id=whatsapp.get("whatsapp_config_id"),
                whatsapp_template_id=whatsapp.get("whatsapp_template_id"),
                prompt=prompt,
                global_=global_,
                global_condition=global_condition
            )
            
        elif node_type == "SubagentNode":
            subagent_data = node_dict.get("subagent", {})
            node = SubagentNode(
                name=node_name,
                prompt=prompt,
                global_=global_,
                global_condition=global_condition
            )
            
            # Add webhooks
            for webhook_dict in subagent_data.get("webhooks", []):
                # Parse JSON strings back to objects
                headers = webhook_dict.get("headers")
                if headers and isinstance(headers, str):
                    headers = json.loads(headers)
                
                body = webhook_dict.get("body")
                if body and isinstance(body, str):
                    body = json.loads(body)
                
                body_schema = webhook_dict.get("body_schema")
                if body_schema and isinstance(body_schema, str):
                    body_schema = json.loads(body_schema)
                
                mock_response = webhook_dict.get("mock_response")
                if mock_response and isinstance(mock_response, str):
                    mock_response = json.loads(mock_response)
                
                tool = WebhookTool(
                    name=webhook_dict.get("name", ""),
                    url=webhook_dict.get("url", ""),
                    http_method=webhook_dict.get("http_method", "POST"),
                    headers=headers,
                    body=body,
                    body_schema=body_schema,
                    mock_response=mock_response,
                    mock_response_enabled=webhook_dict.get("mock_response_enabled", False),
                    description=webhook_dict.get("description", ""),
                    jmespath_query=webhook_dict.get("jmespath_query")
                )
                node.add_tool(tool)
            
            # Add knowledge bases
            for kb_dict in subagent_data.get("knowledge_bases", []):
                # Build kwargs based on what's provided
                kb_kwargs = {
                    "name": kb_dict.get("name", ""),
                    "description": kb_dict.get("description", "")
                }
                
                # Add either text or file
                if "knowledge_base_text" in kb_dict:
                    kb_kwargs["knowledge_base_text"] = kb_dict["knowledge_base_text"]
                if "knowledge_base_file" in kb_dict:
                    kb_kwargs["knowledge_base_file"] = kb_dict["knowledge_base_file"]
                
                tool = KnowledgeBaseTool(**kb_kwargs)
                node.add_tool(tool)
            
            # Add MCP servers
            for mcp_dict in subagent_data.get("mcp_servers", []):
                jmespath_queries = []
                for query_dict in mcp_dict.get("jmespath_queries", []):
                    jmespath_queries.append(JmespathQuery(
                        tool_name=query_dict.get("tool_name", ""),
                        jmespath_query=query_dict.get("jmespath_query", "")
                    ))
                
                tool = McpServerTool(
                    name=mcp_dict.get("name", ""),
                    url=mcp_dict.get("url", ""),
                    transport_kind=mcp_dict.get("transport_kind", "streamable_http"),
                    jmespath_queries=jmespath_queries,
                    description=mcp_dict.get("description", "")
                )
                node.add_tool(tool)
            
            # Add WhatsApp templates
            for wt_dict in subagent_data.get("whatsapp_templates", []):
                tool = WhatsappTemplateTool(
                    name=wt_dict.get("name", ""),
                    template_name=wt_dict.get("template_name", ""),
                    phone_number=wt_dict.get("phone_number", ""),
                    template_parameters=wt_dict.get("template_parameters"),
                    whatsapp_config_id=wt_dict.get("whatsapp_config_id"),
                    whatsapp_template_id=wt_dict.get("whatsapp_template_id"),
                    wait_for_response=wt_dict.get("wait_for_response", False),
                    description=wt_dict.get("description", "")
                )
                node.add_tool(tool)
            
        else:
            node = DefaultNode(
                name=node_name,
                prompt=prompt,
                global_=global_,
                global_condition=global_condition
            )
            
        agent.add_node(node)
        
    for edge_dict in edges:
        agent.add_edge(
            source=edge_dict.get("from", ""),
            target=edge_dict.get("to", ""),
            condition=edge_dict.get("label") or edge_dict.get("condition")
        )
        
    return agent


def deserialize_from_yaml(yaml_str: str) -> Agent:
    """
    Deserialize an agent from a YAML string.
    
    Args:
        yaml_str: YAML representation of an agent
        
    Returns:
        An Agent instance
    """
    agent_dict = yaml.safe_load(yaml_str)
    return deserialize_from_dict(agent_dict)


def load_agent(file_path: str) -> Agent:
    """
    Load an agent from a file.
    
    Args:
        file_path: Path to the agent file (YAML)
        
    Returns:
        An Agent instance
    """
    with open(file_path, "r") as f:
        content = f.read()
        
    if file_path.endswith(".yaml") or file_path.endswith(".yml"):
        return deserialize_from_yaml(content)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
