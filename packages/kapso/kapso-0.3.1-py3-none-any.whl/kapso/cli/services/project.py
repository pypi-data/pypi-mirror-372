"""
Project service for the Kapso CLI.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Callable

from kapso.cli.utils.metadata import create_agent_metadata, write_metadata, create_flow_metadata

class ProjectService:
    """
    Service for managing Kapso projects.
    """

    def __init__(self):
        """Initialize the project service."""
        self.agent_templates = {
            "basic": self._get_basic_agent_template,
            "support": self._get_support_agent_template,
            "knowledge-base": self._get_knowledge_base_agent_template,
        }

    def create_example_agent(self, project_path: Path, template: str) -> None:
        """
        Create an example agent file based on the specified template.

        Args:
            project_path: Path to the project directory
            template: Template to use (basic, support, knowledge-base)
        """
        agent_file = project_path / "agent.py"

        template_func = self.agent_templates.get(template, self._get_basic_agent_template)
        content = template_func()

        with open(agent_file, "w") as f:
            f.write(content)

    def create_agent_directory(self, project_path: Path, agent_name: str, template: str) -> None:
        """
        Create an agent directory with agent.py and metadata.yaml files.

        Args:
            project_path: Path to the project directory
            agent_name: Name of the agent (e.g., "customer_support")
            template: Template to use (basic, support, knowledge-base)
        """
        # Create agent directory
        agent_dir = project_path / "agents" / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Create agent.py file
        agent_file = agent_dir / "agent.py"
        template_func = self.agent_templates.get(template, self._get_basic_agent_template)
        display_name = agent_name.replace('_', ' ').replace('-', ' ').title()
        content = template_func(display_name)
        with open(agent_file, "w") as f:
            f.write(content)
        
        # Create metadata.yaml file
        display_name = agent_name.replace('_', ' ').replace('-', ' ').title()
        description = f"Generated {template} agent" if template != "default" else ""
        metadata = create_agent_metadata(
            name=display_name,
            description=description,
            agent_id=None  # Will be set when pushed to cloud
        )
        write_metadata(agent_dir, metadata)
    
    def create_flow_directory(self, project_path: Path, flow_name: str) -> None:
        """
        Create a flow directory with flow.py and metadata.yaml files.

        Args:
            project_path: Path to the project directory
            flow_name: Name of the flow (e.g., "onboarding_flow")
        """
        # Create flow directory
        flow_dir = project_path / "flows" / flow_name
        flow_dir.mkdir(parents=True, exist_ok=True)
        
        # Create flow.py file
        flow_file = flow_dir / "flow.py"
        content = self._get_basic_flow_template(flow_name)
        with open(flow_file, "w") as f:
            f.write(content)
        
        # Create metadata.yaml file
        metadata_file = flow_dir / "metadata.yaml"
        display_name = flow_name.replace('_', ' ').replace('-', ' ').title()
        current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        metadata_content = f"""name: {display_name}
description: Generated flow
created_at: "{current_time}"
updated_at: "{current_time}"
"""
        with open(metadata_file, "w") as f:
            f.write(metadata_content)
    
    def create_function_file(self, project_path: Path, function_name: str) -> None:
        """
        Create a JavaScript function file.

        Args:
            project_path: Path to the project directory
            function_name: Name of the function (e.g., "validate_email")
        """
        # Create functions directory
        functions_dir = project_path / "functions"
        functions_dir.mkdir(parents=True, exist_ok=True)
        
        # Create function file
        function_file = functions_dir / f"{function_name}.js"
        content = self._get_basic_function_template(function_name)
        with open(function_file, "w") as f:
            f.write(content)

    def create_project_kapso_yaml(self, project_path: Path, project_name: str) -> None:
        """
        Create a project-level kapso.yaml configuration file.

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
        """
        config_file = project_path / "kapso.yaml"

        content = f"""# Kapso project configuration
name: "{project_name}"
version: "0.1.0"
"""

        with open(config_file, "w") as f:
            f.write(content)

    def create_env_example(self, project_path: Path) -> None:
        """
        Create a .env.example file.

        Args:
            project_path: Path to the project directory
        """
        env_file = project_path / ".env.example"

        content = """# Kapso environment variables

# LLM Configuration
LLM_PROVIDER_NAME=Anthropic
LLM_PROVIDER_MODEL_NAME=claude-sonnet-4-20250514
LLM_API_KEY=your-llm-api-key
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=8096

# OpenAI API key (used for embeddings in knowledge bases)
OPENAI_API_KEY=your-openai-api-key

# Kapso API key (for cloud deployment)
KAPSO_API_KEY=your-kapso-api-key

# Test evaluation configuration
JUDGE_LLM_API_KEY=your-judge-llm-api-key
JUDGE_LLM_PROVIDER=Anthropic
"""

        with open(env_file, "w") as f:
            f.write(content)

    def _get_basic_flow_template(self, flow_name: str) -> str:
        """Get the basic flow template."""
        display_name = flow_name.replace('_', ' ').replace('-', ' ').title()
        return f"""from kapso.builder.flows import Flow
from kapso.builder.flows.nodes import StartNode, SendTextNode, WaitForResponseNode

# Replace with your WhatsApp config ID from Kapso
WHATSAPP_CONFIG_ID = 'replace_with_your_whatsapp_config_id_from_kapso'

# Create the flow
flow = Flow(
    name="{display_name}",
    description="A basic flow template"
)

# Add nodes
start_node = StartNode(
    id="start"
)

welcome_node = SendTextNode(
    id="welcome",
    whatsapp_config_id=WHATSAPP_CONFIG_ID,
    text="Welcome! How can I help you today?"
)

wait_node = WaitForResponseNode(
    id="wait_response",
    timeout_seconds=300
)

# Add nodes to flow
flow.add_node(start_node)
flow.add_node(welcome_node)
flow.add_node(wait_node)

# Add edges
flow.add_edge("start", "welcome")
flow.add_edge("welcome", "wait_response")

# Validate the flow configuration
flow.validate()
"""

    def _get_basic_function_template(self, function_name: str) -> str:
        """Get the basic function template."""
        return f"""/**
 * {function_name.replace('_', ' ').replace('-', ' ').title()} Function
 * 
 * @param {{object}} input - The input parameters
 * @returns {{object}} The result of the function
 */
function {function_name}(input) {{
    // TODO: Implement your function logic here
    return {{
        success: true,
        message: "Function executed successfully",
        data: input
    }};
}}

export default {function_name};
"""

    def _get_basic_agent_template(self, agent_name: str = "Basic Agent") -> str:
        """Get the basic agent template."""
        return f"""from kapso.builder import Agent
from kapso.builder.nodes import SubagentNode, WarmEndNode, HandoffNode
from kapso.builder.nodes.subagent import WebhookTool, KnowledgeBaseTool
from kapso.builder.agent.constants import START_NODE, END_NODE

# Create the agent
agent = Agent(
    name="{agent_name}",
    system_prompt="You are a helpful assistant that can look up information and answer questions."
)

# Create a subagent node with basic tools
subagent = SubagentNode(
    name="subagent",
    prompt="Help the user with their questions using the available tools when needed."
)

# Add a simple webhook tool
api_tool = WebhookTool(
    name="get_data",
    url="https://api.example.com/data",
    http_method="GET",
    headers={{"Authorization": "Bearer {{{{api_key}}}}"}},
    description="Retrieve data from the external API"
)
subagent.add_tool(api_tool)

# Add a knowledge base tool
kb_tool = KnowledgeBaseTool(
    name="info",
    knowledge_base_text="Our service hours are 9 AM to 5 PM EST, Monday through Friday.",
    description="General information about our service"
)
subagent.add_tool(kb_tool)

# Global handoff node for escalation
human_handoff = HandoffNode(
    name="human_handoff",
    global_=True,
    global_condition="user explicitly requests human agent OR conversation requires human assistance"
)

# Warm end node for conversation closure
end_conversation = WarmEndNode(
    name="end_conversation",
    timeout_minutes=30,
    prompt="Thank you for chatting with me! I'll be here for another 30 minutes if you have any follow-up questions."
)

# Add nodes to the agent
agent.add_node(START_NODE)
agent.add_node(subagent)
agent.add_node(human_handoff)
agent.add_node(end_conversation)
agent.add_node(END_NODE)

# Create the conversation flow
agent.add_edge(START_NODE, "subagent")
agent.add_edge("subagent", "end_conversation", condition="user says goodbye or conversation is complete")
agent.add_edge("end_conversation", END_NODE)
"""

    def _get_support_agent_template(self, agent_name: str = "Support Agent") -> str:
        """Get the support agent template."""
        return f"""from kapso.builder.agent import Agent
from kapso.builder.nodes import DefaultNode, HandoffNode, WarmEndNode
from kapso.builder.edges import Edge

agent = Agent(
    name="{agent_name}",
    system_prompt="You are a helpful customer support agent."
)

start_node = DefaultNode(
    name="start",
    prompt="You are a customer support agent for a software company. Help users with their questions and issues."
)

handoff_node = HandoffNode(
    name="handoff"
)

end_node = WarmEndNode(
    name="end",
    prompt="Thank you for contacting our support. Is there anything else I can help you with?",
    timeout_minutes=60
)

agent.add_node(start_node)
agent.add_node(handoff_node)
agent.add_node(end_node)

agent.add_edge(source="START", target="start")
agent.add_edge(source="start", target="handoff", condition="user has a complex issue that requires human assistance")
agent.add_edge(source="start", target="end", condition="user's issue is resolved")
agent.add_edge(source="end", target="END")
"""

    def _get_knowledge_base_agent_template(self, agent_name: str = "Knowledge Base Agent") -> str:
        """Get the knowledge base agent template."""
        return f"""from kapso.builder.agent import Agent
from kapso.builder.nodes import DefaultNode, KnowledgeBaseNode, WarmEndNode
from kapso.builder.edges import Edge

agent = Agent(
    name="{agent_name}",
    system_prompt="You are a helpful assistant with access to a knowledge base."
)

start_node = DefaultNode(
    name="start",
    prompt="You are an assistant with access to a knowledge base. Help users find information."
)

kb_node = KnowledgeBaseNode(
    name="knowledge",
    key="default",
    prompt="Use the knowledge base to answer the user's question accurately."
)

end_node = WarmEndNode(
    name="end",
    prompt="Thank you for your questions. Is there anything else I can help you with?",
    timeout_minutes=60
)

agent.add_node(start_node)
agent.add_node(kb_node)
agent.add_node(end_node)

agent.add_edge(source="START", target="start")
agent.add_edge(source="start", target="knowledge", condition="user asks a question that requires knowledge base lookup")
agent.add_edge(source="knowledge", target="end", condition="user's question is answered")
agent.add_edge(source="end", target="END")
"""

