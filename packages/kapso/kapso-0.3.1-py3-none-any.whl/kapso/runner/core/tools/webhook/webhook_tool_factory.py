"""
Factory for creating dynamic, self-contained webhook tools based on node configuration.
"""

import re
import logging
import json
from typing import Dict, List, Any, Type, Optional, Tuple, Set
from types import FunctionType

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import create_model, BaseModel, Field

# Assuming do_webhook_request is accessible/imported correctly
from kapso.runner.core.tools.webhook.webhook_request import do_webhook_request

logger = logging.getLogger(__name__)


class WebhookToolExecutionError(Exception):
    """Exception raised when a dynamic webhook tool fails to execute."""
    pass


class WebhookToolFactory:
    """Factory for creating dynamic webhook tools."""

    @staticmethod
    def extract_template_variables(webhook_config: Dict[str, Any]) -> List[str]:
        """
        Extract unique variables in the format #{variable_name} from webhook configuration.
        Searches URL, headers (keys and values), and body (recursively in strings).
        """
        variables = set()
        pattern = r'#{([a-zA-Z0-9_]+)}'

        def find_vars_in_obj(obj):
            if isinstance(obj, str):
                for match in re.finditer(pattern, obj):
                    variables.add(match.group(1))
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    find_vars_in_obj(k)  # Search in keys
                    find_vars_in_obj(v)  # Search in values
            elif isinstance(obj, list):
                for item in obj:
                    find_vars_in_obj(item)

        # Search URL and headers
        config_subset = {
            k: v for k, v in webhook_config.items()
            if k in ["url", "headers", "http_method"]
        }

        # Only include body if body_schema is not present
        if "body" in webhook_config and ("body_schema" not in webhook_config or webhook_config["body_schema"] is None):
            config_subset["body"] = webhook_config["body"]

        find_vars_in_obj(config_subset)  # Search the filtered config structure
        return sorted(list(variables))  # Return sorted list for consistent ordering

    @staticmethod
    def extract_schema_properties(body_schema: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
        """
        Extract properties and required fields from a JSON Schema definition.

        Args:
            body_schema: A JSON Schema object definition

        Returns:
            Tuple containing:
            - Dictionary of property name to property definition
            - List of required property names
        """
        if not body_schema or not isinstance(body_schema, dict):
            return {}, []

        properties = body_schema.get("properties", {})
        required = body_schema.get("required", [])

        return properties, required

    @staticmethod
    def apply_variables(template_structure: Any, variables: Dict[str, Any]) -> Any:
        """
        Recursively apply variable values to a nested structure (str, dict, list).
        Replaces #{var_name} with the value from the variables dict.
        If a variable is not found, the placeholder remains.
        """
        if isinstance(template_structure, str):
            pattern = r'#{([a-zA-Z0-9_]+)}'
            def replace_match(match):
                var_name = match.group(1)
                # Use get to avoid KeyError, keep placeholder if var not provided
                return str(variables.get(var_name, match.group(0)))
            return re.sub(pattern, replace_match, template_structure)
        elif isinstance(template_structure, dict):
            return {
                WebhookToolFactory.apply_variables(k, variables): WebhookToolFactory.apply_variables(v, variables)
                for k, v in template_structure.items()
            }
        elif isinstance(template_structure, list):
            return [WebhookToolFactory.apply_variables(item, variables) for item in template_structure]
        else:
            # Return non-str/dict/list types (like numbers, booleans) as is
            return template_structure

    @staticmethod
    def _get_pydantic_type(schema_type: str) -> Any:
        """Convert JSON Schema type to Python/Pydantic type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return type_mapping.get(schema_type, str)  # Default to str for unknown types

    @staticmethod
    def _create_dynamic_args_schema(
        tool_name: str,
        template_variables: List[str],
        body_schema: Optional[Dict[str, Any]] = None
    ) -> Type[BaseModel]:
        """
        Creates a Pydantic model dynamically for tool arguments.

        Combines template variables from URL/headers with body schema properties.
        """
        fields = {}

        # First add template variables (for URL/headers)
        for var_name in template_variables:
            fields[var_name] = (str, Field(description=f"Value for variable {var_name} in URL or headers"))

        # Then add body schema properties if provided
        if body_schema and isinstance(body_schema, dict):
            properties, required_props = WebhookToolFactory.extract_schema_properties(body_schema)

            for prop_name, prop_def in properties.items():
                prop_type = WebhookToolFactory._get_pydantic_type(prop_def.get("type", "string"))
                description = prop_def.get("description", f"Value for {prop_name}")

                # Check if property is required
                is_required = prop_name in required_props

                # For optional fields, wrap the type in Optional
                if is_required:
                    fields[prop_name] = (prop_type, Field(description=description))
                else:
                    fields[prop_name] = (Optional[prop_type], Field(description=description, default=None))

        model_name = f"{tool_name.capitalize().replace('_','')}{len(fields)}Args"

        return create_model(model_name, **fields)

    @staticmethod
    def create_tool(node_name: str, webhook_config: Dict[str, Any], description_override: Optional[str] = None) -> BaseTool:
        """
        Creates a self-contained, functional LangChain tool for a specific webhook.

        Args:
            node_name: Name of the node (used for generating tool name/description).
            webhook_config: The webhook configuration dictionary from the node.
            description_override: Optional custom description to use for the tool.

        Returns:
            A BaseTool instance ready to be used by LangChain.
        """
        # Extract template variables (for URL and headers)
        template_variables = WebhookToolFactory.extract_template_variables(webhook_config)

                # Get body schema if present
        body_schema = webhook_config.get("body_schema")
        
        # If body_schema is a string, try to parse it as JSON
        if isinstance(body_schema, str):
            try:
                body_schema = json.loads(body_schema)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse body_schema as JSON: {e}")
                body_schema = None
        
        # Get schema properties and required fields
        schema_properties, required_props = ({}, []) if not body_schema else WebhookToolFactory.extract_schema_properties(body_schema)

        # Sanitize node_name for use in tool_name
        safe_node_name = re.sub(r'\W|^(?=\d)', '_', node_name.lower())
        tool_name = f"{safe_node_name}_request"

        # Use provided description if available, otherwise generate one
        if description_override:
            description = description_override
        else:
            # Build more informative description based on schema properties if available
            if body_schema:
                param_descriptions = []
                for prop_name in schema_properties:
                    req_status = "(required)" if prop_name in required_props else "(optional)"
                    param_descriptions.append(f"{prop_name} {req_status}")

                # Also add template variables if any
                for var_name in template_variables:
                    param_descriptions.append(f"{var_name} (for URL/headers)")

                description = (f"Execute the API request for the '{node_name}' step. "
                              f"Parameters: {', '.join(param_descriptions) if param_descriptions else 'None'}.")
            else:
                description = (f"Execute the API request for the '{node_name}' step. "
                              f"Required parameters: {', '.join(template_variables) if template_variables else 'None'}.")

        # Create the dynamic Pydantic model for arguments
        args_schema = WebhookToolFactory._create_dynamic_args_schema(tool_name, template_variables, body_schema)

        # Capture the webhook config for use inside the execution function
        # Make a deep copy to prevent modification issues if config is reused
        import copy
        _config_capture = copy.deepcopy(webhook_config)

        async def _execute_dynamic_webhook(**kwargs):
            """
            The actual execution logic embedded within the created tool.
            It uses the captured webhook config and the arguments provided (**kwargs).
            """
            logger.debug(f"Executing dynamic tool {tool_name} with args: {kwargs}")
            try:
                # Apply the provided variables (**kwargs) to the captured config template for URL and headers
                processed_config = WebhookToolFactory.apply_variables(_config_capture, kwargs)

                # Extract parameters for do_webhook_request from the processed config
                url = processed_config.get("url")
                method = processed_config.get("http_method", processed_config.get("method", "GET"))  # Default to GET
                headers = processed_config.get("headers")

                # Handle body based on whether body_schema is present
                body_schema = processed_config.get("body_schema")
                
                # If body_schema is a string, try to parse it as JSON
                if isinstance(body_schema, str):
                    try:
                        body_schema = json.loads(body_schema)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse body_schema as JSON in execution: {e}")
                        body_schema = None
                
                if body_schema:
                    # When body_schema is present, construct body from kwargs based on schema properties
                    schema_properties, _ = WebhookToolFactory.extract_schema_properties(body_schema)
                    body_data = {}

                    # Extract only the schema-defined properties from kwargs
                    for prop_name in schema_properties:
                        if prop_name in kwargs:
                            body_data[prop_name] = kwargs[prop_name]

                    # Convert to JSON string
                    body = json.dumps(body_data)
                else:
                    # Use the template-processed body if no schema
                    body = processed_config.get("body")

                # Mock settings are read directly from the processed (static) config
                mock_enabled = processed_config.get("mock_response_enabled", False)
                mock_response = processed_config.get("mock_response", None)

                if not url:
                    # Raise an exception instead of returning an error dictionary
                    raise WebhookToolExecutionError(f"URL is missing in configuration for tool {tool_name}")

                # Call the core async request function directly
                result = await do_webhook_request(
                    url=url,
                    method=method,
                    headers=headers,
                    body=body,
                    mock_response_enabled=mock_enabled,
                    mock_response=mock_response
                )
                logger.debug(f"Dynamic tool {tool_name} result: {result}")
                return result

            except Exception as e:
                # Log the error
                logger.exception(f"Error executing dynamic tool {tool_name}")
                # Raise a more informative exception that wraps the original one
                # This preserves the original traceback via the "from e" syntax
                raise WebhookToolExecutionError(f"Failed to execute {tool_name}: {str(e)}") from e

        # Create the LangChain StructuredTool
        dynamic_tool = StructuredTool.from_function(
            # Don't use func for async functions
            # func=_execute_dynamic_webhook,
            # Use coroutine for async functions instead
            coroutine=_execute_dynamic_webhook,
            name=tool_name,
            description=description,
            args_schema=args_schema,  # Use the dynamically created Pydantic model
        )

        logger.info(f"Created dynamic tool: {tool_name} with args: {list(args_schema.__annotations__.keys())}")

        return dynamic_tool