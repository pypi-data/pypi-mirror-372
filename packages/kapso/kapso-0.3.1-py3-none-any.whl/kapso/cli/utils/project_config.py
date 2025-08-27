"""
Utilities for handling project configuration.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def find_kapso_yaml() -> Optional[Path]:
    """
    Find kapso.yaml file starting from current directory and moving up.
    
    Returns:
        Path to kapso.yaml if found, None otherwise.
    """
    current_dir = Path.cwd()
    
    while current_dir.parent != current_dir:  # Stop at filesystem root
        config_file = current_dir / "kapso.yaml"
        if config_file.exists():
            return config_file
        current_dir = current_dir.parent
    
    return None


def load_project_config() -> Dict[str, Any]:
    """
    Load project configuration from kapso.yaml.
    
    Returns:
        Project configuration as a dictionary.
    """
    config_file = find_kapso_yaml()
    if not config_file:
        return {}
    
    try:
        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def save_project_config(config: Dict[str, Any]) -> bool:
    """
    Save project configuration to kapso.yaml.
    
    Args:
        config: Project configuration to save.
        
    Returns:
        True if successful, False otherwise.
    """
    config_file = find_kapso_yaml()
    if not config_file:
        # Create in current directory if not found
        config_file = Path.cwd() / "kapso.yaml"
    
    try:
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception:
        return False


def get_project_id() -> Optional[str]:
    """
    Get project ID from configuration.
    
    Returns:
        Project ID if found, None otherwise.
    """
    config = load_project_config()
    return config.get("project_id")


def set_project_id(project_id: str) -> bool:
    """
    Set project ID in configuration.
    
    Args:
        project_id: Project ID to set.
        
    Returns:
        True if successful, False otherwise.
    """
    config = load_project_config()
    config["project_id"] = project_id
    return save_project_config(config)


def update_env_file(project_id: str, api_key: str) -> bool:
    """
    Update .env file with API key.
    
    Args:
        project_id: Project ID to set the API key for.
        api_key: API key to set.
        
    Returns:
        True if successful, False otherwise.
    """
    env_file = Path.cwd() / ".env"
    
    # Read existing content
    lines = []
    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()
    
    # Create or update API key entry
    key_name = f"KAPSO_PROJECT_{project_id}_API_KEY"
    key_line = f"\n{key_name}={api_key}\n"
    
    # Check if key already exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key_name}="):
            lines[i] = key_line
            key_exists = True
            break
    
    # Add key if it doesn't exist
    if not key_exists:
        lines.append(key_line)
    
    # Write updated content
    try:
        with open(env_file, "w") as f:
            f.writelines(lines)
        return True
    except Exception:
        return False


def ensure_project_api_key(project_id: str, auth_service, api_manager) -> bool:
    """
    Ensure that we have an API key for the given project, generating one if needed.
    
    Args:
        project_id: ID of the project to ensure API key for.
        auth_service: Authentication service instance.
        api_manager: API manager instance.
        
    Returns:
        True if API key is available, False otherwise.
    """
    # Check if we have an API key for this project
    api_key = auth_service.get_project_api_key(project_id)
    
    # If no API key, generate one
    if not api_key:
        try:
            print("[cyan]Generating API key for the project...[/cyan]")
            api_key_result = api_manager.user().generate_project_api_key(project_id)
            
            if api_key_result and api_key_result.get("key"):
                # Store the API key
                api_key = api_key_result["key"]
                auth_service.store_project_api_key(project_id, api_key)
                update_env_file(project_id, api_key)
                print("[green]API key generated and stored successfully.[/green]")
                return True
            else:
                print("[red]Failed to generate API key.[/red]")
                return False
                
        except Exception as e:
            print(f"[red]Error generating API key: {str(e)}[/red]")
            return False
    
    return True 