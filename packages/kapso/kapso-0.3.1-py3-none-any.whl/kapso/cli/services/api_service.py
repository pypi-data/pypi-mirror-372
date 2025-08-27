"""
API service for interacting with the Kapso Cloud API.
"""

import json
import os
import requests
from typing import Dict, Optional, Any, Union

from kapso.cli.services.auth_service import AuthService


class GenerationLimitError(Exception):
    """
    Custom error for when generations are not allowed due to free limit.
    """
    
    def __init__(self, message: str, free_generations_remaining: int, project_id: str):
        super().__init__(message)
        self.free_generations_remaining = free_generations_remaining
        self.project_id = project_id


class UserApiClient:
    """
    API client for user-context operations (authentication, API key generation).
    """

    def __init__(
        self,
        auth_service: Optional[AuthService] = None,
        api_url: str = "https://app.kapso.ai/api/cli",
    ):
        """
        Initialize the user API client.
        
        Args:
            auth_service: Authentication service to use for getting tokens.
            api_url: Base URL for the API.
        """
        self.api_url = api_url
        self.auth_service = auth_service or AuthService()

    def generate_project_api_key(self, project_id: str) -> Dict[str, Any]:
        """
        Generate a new API key for a project.
        
        Args:
            project_id: ID of the project to generate an API key for.
            
        Returns:
            Response data including the generated API key.
        """
        url = f"{self.api_url}/projects/{project_id}/generate_api_key"
        headers = self._get_auth_headers()

        response = requests.post(url, json={}, headers=headers)
        response.raise_for_status()
        data = response.json()["data"]

        # Check if the response has the expected key
        if not data.get("key"):
            raise Exception("Invalid API key response format")

        return data

    def list_projects(self) -> Dict[str, Any]:
        """
        List all projects.
        
        Returns:
            List of projects.
        """
        url = f"{self.api_url}/projects"
        headers = self._get_auth_headers()

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["data"]
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get project details by ID.
        
        Args:
            project_id: ID of the project to retrieve.
            
        Returns:
            Project details.
        """
        url = f"{self.api_url}/projects/{project_id}"
        headers = self._get_auth_headers()

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["data"]

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Headers dictionary with authentication token.
        """
        token = self.auth_service.get_token()
        if not token:
            raise Exception("Not authenticated. Please run 'kapso login' first.")

        return {
            "Content-Type": "application/json",
            "X-CLI-Token": token
        }


class ApiService:
    """
    Service for making API requests to the Kapso Cloud API.
    Handles authentication and provides methods for common API operations.
    """

    def __init__(
        self,
        auth_service: Optional[AuthService] = None,
        api_url: str = "https://app.kapso.ai/api/v1",
    ):
        """
        Initialize the API service.

        Args:
            auth_service: Authentication service to use for getting tokens.
            api_url: Base URL for the API.
        """
        self.api_url = api_url
        self.auth_service = auth_service or AuthService()
        self.project_id = None
        
    def set_project_id(self, project_id: str) -> None:
        """
        Set the current project ID for API key usage.
        
        Args:
            project_id: ID of the project to use for API key authentication.
        """
        self.project_id = project_id

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint to call.
            params: Optional query parameters.

        Returns:
            Response data as a dictionary.
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                self._handle_generation_limit_error(e.response)
            raise

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint to call.
            data: Optional request body.

        Returns:
            Response data as a dictionary.
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = self._get_auth_headers()

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                self._handle_generation_limit_error(e.response)
            # Try to extract a more meaningful error message
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    raise Exception(f"API Error: {error_data['error']}")
                elif 'errors' in error_data:
                    # Handle Rails-style error format
                    error_messages = []
                    for field, messages in error_data['errors'].items():
                        if isinstance(messages, list):
                            for msg in messages:
                                error_messages.append(f"{field}: {msg}")
                        else:
                            error_messages.append(f"{field}: {messages}")
                    raise Exception(f"API Error: {'; '.join(error_messages)}")
                else:
                    raise Exception(f"API Error ({e.response.status_code}): {error_data}")
            except (ValueError, KeyError):
                # If we can't parse the error response, use the HTTP status
                raise Exception(f"API Error ({e.response.status_code}): {e.response.text}")

    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a PATCH request to the API.

        Args:
            endpoint: API endpoint to call.
            data: Optional request body.

        Returns:
            Response data as a dictionary.
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = self._get_auth_headers()

        try:
            response = requests.patch(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                self._handle_generation_limit_error(e.response)
            # Try to extract a more meaningful error message
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    raise Exception(f"API Error: {error_data['error']}")
                elif 'errors' in error_data:
                    # Handle Rails-style error format
                    error_messages = []
                    for field, messages in error_data['errors'].items():
                        if isinstance(messages, list):
                            for msg in messages:
                                error_messages.append(f"{field}: {msg}")
                        else:
                            error_messages.append(f"{field}: {messages}")
                    raise Exception(f"API Error: {'; '.join(error_messages)}")
                else:
                    raise Exception(f"API Error ({e.response.status_code}): {error_data}")
            except (ValueError, KeyError):
                # If we can't parse the error response, use the HTTP status
                raise Exception(f"API Error ({e.response.status_code}): {e.response.text}")

    def _handle_generation_limit_error(self, response):
        """
        Handle generation limit error response.
        
        Args:
            response: HTTP response to check for generation limit error.
            
        Raises:
            GenerationLimitError: If the response contains generation limit error data.
        """
        try:
            data = response.json()
            if data and 'error' in data and 'free_generations_remaining' in data and 'project_id' in data:
                raise GenerationLimitError(
                    data['error'],
                    data['free_generations_remaining'],
                    data['project_id']
                )
        except:
            # If we can't parse the error, just let the original exception propagate
            pass

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for the current project.
        
        Returns:
            API key if found, None otherwise.
        """
        if self.project_id:
            return self.auth_service.get_project_api_key(self.project_id)
        return None

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        Check for KAPSO_API_KEY environment variable first,
        then try project API key, finally fall back to user token.
        
        Returns:
            Headers dictionary with appropriate authentication.
        """
        headers = {"Content-Type": "application/json"}
        
        # Check for KAPSO_API_KEY environment variable first
        if "KAPSO_API_KEY" in os.environ:
            headers["X-API-Key"] = os.environ["KAPSO_API_KEY"]
            return headers
        
        # Try to use project API key if project_id is set
        api_key = self._get_api_key()
        if api_key:
            headers["X-API-Key"] = api_key
            return headers
        
        # Fall back to user token
        token = self.auth_service.get_token()
        if not token:
            raise Exception("Not authenticated. Please run 'kapso login' first.")
        
        headers["X-CLI-Token"] = token
        return headers

    # Agent methods
    def list_agents(self) -> Dict[str, Any]:
        """
        List all agents in the current project.

        Returns:
            List of agents.
        """
        return self.get("agents")
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new agent.

        Args:
            agent_data: Agent data including name and system_prompt.

        Returns:
            Created agent details.
        """
        return self.post("agents", {"agent": agent_data})
        
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent details by ID.

        Args:
            agent_id: ID of the agent to retrieve.

        Returns:
            Agent details.
        """
        return self.get(f"agents/{agent_id}")

    def get_agent_with_graph(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent details including the graph structure.

        Args:
            agent_id: ID of the agent to retrieve.

        Returns:
            Agent details with graph.
        """
        response = self.get(f"agents/{agent_id}/graph")
        # The response should already be the data portion
        return response

    def update_agent(
        self, agent_id: str, agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an agent.

        Args:
            agent_id: ID of the agent to update.
            agent_data: Agent data to update.

        Returns:
            Updated agent details.
        """
        return self.patch(f"agents/{agent_id}", {"agent": agent_data})

    # Test suite methods
    def list_agent_test_suites(self, agent_id: str) -> Dict[str, Any]:
        """
        List test suites for an agent.

        Args:
            agent_id: ID of the agent to get test suites for.

        Returns:
            List of test suites.
        """
        return self.get(f"agents/{agent_id}/test_suites")

    def get_test_suite(self, test_suite_id: str) -> Dict[str, Any]:
        """
        Get test suite details by ID.

        Args:
            test_suite_id: ID of the test suite to retrieve.

        Returns:
            Test suite details.
        """
        return self.get(f"test_suites/{test_suite_id}")

    # Test case methods
    def list_test_cases(self, test_suite_id: str) -> Dict[str, Any]:
        """
        List test cases for a test suite.

        Args:
            test_suite_id: ID of the test suite to get test cases for.

        Returns:
            List of test cases.
        """
        return self.get(f"test_suites/{test_suite_id}/test_cases")
    
    def create_test_case(
        self, test_suite_id: str, test_case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a test case in a test suite.

        Args:
            test_suite_id: ID of the test suite to create the test case in.
            test_case_data: Test case data.

        Returns:
            Created test case details.
        """
        return self.post(
            f"test_suites/{test_suite_id}/test_cases",
            {"test_case": test_case_data}
        )

    def update_test_case(
        self, test_case_id: str, test_case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a test case.

        Args:
            test_case_id: ID of the test case to update.
            test_case_data: Test case data to update.

        Returns:
            Updated test case details.
        """
        return self.patch(
            f"test_cases/{test_case_id}",
            {"test_case": test_case_data}
        )

    def get_test_case(self, test_case_id: str) -> Dict[str, Any]:
        """
        Get test case details by ID.

        Args:
            test_case_id: ID of the test case to retrieve.

        Returns:
            Test case details.
        """
        return self.get(f"test_cases/{test_case_id}")

    # Agent snapshot methods
    def create_agent_snapshot(self, agent_id: str, graph: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a snapshot of an agent with optional graph.
        
        Args:
            agent_id: ID of the agent to create a snapshot for
            graph: Optional graph structure to use
            
        Returns:
            Response data including the snapshot ID
        """
        payload = {}
        if graph:
            payload["graph"] = graph
        return self.post(f"agents/{agent_id}/agent_snapshots", payload)
    
    # Agent test chat methods
    def create_agent_test_chat(self, agent_id: str, test_chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or continue a test chat with an agent.
        
        Args:
            agent_id: ID of the agent to test
            test_chat_data: Test chat data including message and optional agent_test_chat_id
            
        Returns:
            Response data including the test chat
        """
        return self.post(f"agents/{agent_id}/test_chats", test_chat_data)
    
    def create_agent_test_chat_from_snapshot(
        self, 
        agent_snapshot_id: str, 
        test_chat_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create or continue a test chat using an agent snapshot.
        
        Args:
            agent_snapshot_id: ID of the agent snapshot to test
            test_chat_data: Test chat data including message and optional agent_test_chat_id
            
        Returns:
            Response data including the test chat
        """
        return self.post(f"agent_snapshots/{agent_snapshot_id}/test_chats", test_chat_data)
    
    def get_agent_test_chat(self, test_chat_id: str) -> Dict[str, Any]:
        """
        Get the current state of a test chat.
        
        Args:
            test_chat_id: ID of the test chat to retrieve
            
        Returns:
            Response data including the test chat
        """
        return self.get(f"test_chats/{test_chat_id}")

    # Flow methods
    def list_flows(self) -> Dict[str, Any]:
        """
        List all flows in the current project.

        Returns:
            List of flows.
        """
        return self.get("flows")
    
    def create_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new flow.

        Args:
            flow_data: Flow data including name and definition.

        Returns:
            Created flow details.
        """
        return self.post("flows", {"flow": flow_data})
        
    def get_flow(self, flow_id: str) -> Dict[str, Any]:
        """
        Get flow details by ID.

        Args:
            flow_id: ID of the flow to retrieve.

        Returns:
            Flow details.
        """
        return self.get(f"flows/{flow_id}")

    def get_flow_with_definition(self, flow_id: str) -> Dict[str, Any]:
        """
        Get flow details including the definition structure.

        Args:
            flow_id: ID of the flow to retrieve.

        Returns:
            Flow details with definition.
        """
        response = self.get(f"flows/{flow_id}/definition")
        return response

    def update_flow(
        self, flow_id: str, flow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a flow.

        Args:
            flow_id: ID of the flow to update.
            flow_data: Flow data to update.

        Returns:
            Updated flow details.
        """
        return self.patch(f"flows/{flow_id}", {"flow": flow_data})


class ApiManager:
    """
    Main API manager for switching between user and project contexts.
    """
    
    def __init__(
        self,
        auth_service: Optional[AuthService] = None
    ):
        """
        Initialize the API manager.
        
        Args:
            auth_service: Authentication service to use for getting tokens/keys.
        """
        self.auth_service = auth_service or AuthService()
        self.project_api = ApiService(auth_service=self.auth_service)
        self.user_api = UserApiClient(auth_service=self.auth_service)
        
    def project(self, project_id: Optional[str] = None) -> ApiService:
        """
        Get the project API client.
        
        Args:
            project_id: Optional project ID to use for API key authentication.
            
        Returns:
            ApiService instance configured for project operations.
        """
        if project_id:
            self.project_api.set_project_id(project_id)
        return self.project_api
    
    def user(self) -> UserApiClient:
        """
        Get the user API client.
        
        Returns:
            UserApiClient instance for user-context operations.
        """
        return self.user_api 