"""
Authentication service for the Kapso CLI.
"""

import time
import json
import keyring
import os
from pathlib import Path
import requests
from typing import Dict, Optional, Any, Union, Tuple

class AuthService:
    def __init__(
        self,
        api_url: str = "https://app.kapso.ai/api/cli",
        service_name: str = "kapso-cli",
    ):
        self.api_url = api_url
        self.service_name = service_name
        self.config_dir = Path.home() / ".kapso"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def is_authenticated(self) -> Union[Dict[str, Any], bool]:
        """Check if user is already authenticated and verify token."""
        token = self.get_token()

        if not token:
            return False

        verify_result = self.verify_token()
        return verify_result if verify_result.get("valid", False) else False

    def get_token(self) -> Optional[str]:
        """Get stored token."""
        try:
            # Try to get from keyring
            token_data = keyring.get_password(self.service_name, "token")
            if token_data:
                return token_data

            # Fall back to file storage
            token_file = self.config_dir / "token.txt"
            if token_file.exists():
                with open(token_file, "r") as f:
                    return f.read().strip()

            return None
        except Exception:
            return None

    def get_project_api_key(self, project_id: str) -> Optional[str]:
        """
        Get stored API key for a project.
        
        Args:
            project_id: ID of the project to get the API key for.
            
        Returns:
            API key if found, None otherwise.
        """
        try:
            # Check simple KAPSO_API_KEY environment variable first
            if "KAPSO_API_KEY" in os.environ:
                return os.environ["KAPSO_API_KEY"]

            # Try to get from keyring
            key_name = f"project-{project_id}"
            api_key = keyring.get_password(self.service_name, key_name)
            if api_key:
                return api_key

            # Fall back to file storage
            api_key_file = self.config_dir / f"project-{project_id}.txt"
            if api_key_file.exists():
                with open(api_key_file, "r") as f:
                    return f.read().strip()

            return None
        except Exception:
            return None

    def store_project_api_key(self, project_id: str, api_key: str) -> bool:
        """
        Store project API key securely.
        
        Args:
            project_id: ID of the project to store the API key for.
            api_key: API key to store.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Try to store in keyring
            key_name = f"project-{project_id}"
            keyring.set_password(self.service_name, key_name, api_key)
            return True
        except Exception:
            # Fall back to file storage
            try:
                api_key_file = self.config_dir / f"project-{project_id}.txt"
                with open(api_key_file, "w") as f:
                    f.write(api_key)
                return True
            except Exception:
                return False

    def delete_project_api_key(self, project_id: str) -> bool:
        """
        Delete stored project API key.
        
        Args:
            project_id: ID of the project to delete the API key for.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Clear from keyring
            key_name = f"project-{project_id}"
            keyring.delete_password(self.service_name, key_name)
        except Exception:
            pass

        try:
            # Clear from file
            api_key_file = self.config_dir / f"project-{project_id}.txt"
            if api_key_file.exists():
                api_key_file.unlink()
        except Exception:
            pass

        return True

    def store_token(self, token: str) -> bool:
        """Store token securely."""
        try:
            # Try to store in keyring
            keyring.set_password(self.service_name, "token", token)
            return True
        except Exception:
            # Fall back to file storage
            try:
                token_file = self.config_dir / "token.txt"
                with open(token_file, "w") as f:
                    f.write(token)
                return True
            except Exception:
                return False

    def delete_token(self) -> bool:
        """Delete stored token."""
        try:
            # Clear from keyring
            keyring.delete_password(self.service_name, "token")
        except Exception:
            pass

        try:
            # Clear from file
            token_file = self.config_dir / "token.txt"
            if token_file.exists():
                token_file.unlink()
        except Exception:
            pass

        return True

    def request_auth_token(self) -> Dict[str, str]:
        """Request an authentication URL and code from the server."""
        try:
            response = requests.post(f"{self.api_url}/auth/request", json={})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to request authentication: {str(e)}")

    def poll_for_token_exchange(self, auth_code: str, max_attempts: int = 60, interval: int = 2) -> Dict[str, Any]:
        """Poll for authentication completion."""
        attempts = 0

        while attempts < max_attempts:
            try:
                response = requests.post(
                    f"{self.api_url}/auth/exchange",
                    json={"auth_code": auth_code}
                )

                # If successful, authentication is complete
                if response.status_code == 200:
                    data = response.json()
                    if data.get("token"):
                        return data

            except requests.exceptions.RequestException as e:
                # If it's a 404, the token is not ready yet, so we continue polling
                if getattr(e.response, "status_code", None) == 404:
                    pass
                else:
                    # For other errors, stop polling and raise an exception
                    raise Exception(f"Authentication failed: {str(e)}")

            time.sleep(interval)
            attempts += 1

        raise Exception("Authentication timed out. Please try again.")

    def verify_token(self) -> Dict[str, Any]:
        """Verify if the current token is valid."""
        token = self.get_token()

        if not token:
            return {"valid": False}

        try:
            response = requests.get(
                f"{self.api_url}/auth/verify",
                headers={"X-CLI-Token": token}
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return {"valid": False}

    def revoke_token(self) -> None:
        """Revoke the current token."""
        token = self.get_token()

        if not token:
            return

        try:
            requests.post(
                f"{self.api_url}/auth/revoke",
                json={},
                headers={"X-CLI-Token": token}
            )
        finally:
            # Always delete the token locally, even if server revocation fails
            self.delete_token()

    def open_browser(self, url: str) -> None:
        """Open the browser to the authentication URL."""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            # We'll continue even if browser opening fails
            pass