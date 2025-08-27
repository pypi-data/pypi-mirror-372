"""
AgentNode for embedded AI agents in flows.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import json

from .base import Node


@dataclass
class FlowAgentWebhook:
    """Webhook tool configuration for flow agents."""
    name: str
    url: str
    description: str = ""
    http_method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    body_schema: Optional[str] = None  # JSON schema as string
    jmespath_query: Optional[str] = None


@dataclass
class FlowAgentMcpServer:
    """MCP server tool configuration for flow agents."""
    name: str
    url: str
    description: str = ""
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class FlowAgentKnowledgeBase:
    """Knowledge base tool configuration for flow agents."""
    name: str
    knowledge_base_text: str
    description: str = ""


class AgentNode(Node):
    """Node for embedded AI agents with webhook, MCP server, and knowledge base tools."""
    
    def __init__(
        self,
        id: str,
        system_prompt: str,
        provider_model_name: str,
        temperature: float = 0.0,
        max_iterations: int = 80,
        max_tokens: int = 8192,
        reasoning_effort: Optional[str] = None,
        webhooks: Optional[List[FlowAgentWebhook]] = None,
        mcp_servers: Optional[List[FlowAgentMcpServer]] = None,
        knowledge_bases: Optional[List[FlowAgentKnowledgeBase]] = None
    ):
        config = {
            "system_prompt": system_prompt,
            "provider_model_name": provider_model_name,
            "temperature": temperature,
            "max_iterations": max_iterations,
            "max_tokens": max_tokens
        }
        
        if reasoning_effort:
            config["reasoning_effort"] = reasoning_effort
            
        if webhooks:
            config["flow_agent_webhooks"] = [
                {
                    "name": w.name,
                    "description": w.description,
                    "url": w.url,
                    "http_method": w.http_method,
                    "headers": json.dumps(w.headers) if w.headers else "{}",
                    "body": json.dumps(w.body) if w.body else "{}",
                    "body_schema": w.body_schema or '{"type":"object","properties":{},"required":[]}',
                    "jmespath_query": w.jmespath_query
                }
                for w in webhooks
            ]
        
        if mcp_servers:
            config["flow_agent_mcp_servers"] = [
                {
                    "name": m.name,
                    "description": m.description,
                    "url": m.url,
                    "headers": json.dumps(m.headers) if m.headers else "{}"
                }
                for m in mcp_servers
            ]
        
        if knowledge_bases:
            config["flow_agent_knowledge_bases"] = [
                {
                    "name": k.name,
                    "description": k.description,
                    "knowledge_base_text": k.knowledge_base_text
                }
                for k in knowledge_bases
            ]
        
        # Store tools for property access
        self._webhooks = webhooks or []
        self._mcp_servers = mcp_servers or []
        self._knowledge_bases = knowledge_bases or []
        
        super().__init__(
            id=id,
            node_type="agent",
            config=config
        )
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt."""
        return self.config["system_prompt"]
    
    @property
    def provider_model_name(self) -> str:
        """Get the provider model name."""
        return self.config["provider_model_name"]
    
    @property
    def temperature(self) -> float:
        """Get the temperature setting."""
        return self.config["temperature"]
    
    @property
    def max_iterations(self) -> int:
        """Get the maximum iterations."""
        return self.config["max_iterations"]
    
    @property
    def max_tokens(self) -> int:
        """Get the maximum tokens."""
        return self.config["max_tokens"]
    
    @property
    def reasoning_effort(self) -> Optional[str]:
        """Get the reasoning effort setting."""
        return self.config.get("reasoning_effort")
    
    @property
    def webhooks(self) -> List[FlowAgentWebhook]:
        """Get the webhooks list."""
        return self._webhooks
    
    @property
    def mcp_servers(self) -> List[FlowAgentMcpServer]:
        """Get the MCP servers list."""
        return self._mcp_servers
    
    @property
    def knowledge_bases(self) -> List[FlowAgentKnowledgeBase]:
        """Get the knowledge bases list."""
        return self._knowledge_bases