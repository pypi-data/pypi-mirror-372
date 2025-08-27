"""
Utility functions for metadata.yaml operations.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

logger = logging.getLogger(__name__)


class LiteralDumper(yaml.SafeDumper):
    """YAML dumper that preserves string formatting for timestamps."""
    pass


def str_representer(dumper, data):
    """Custom string representer to ensure timestamps are quoted."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


LiteralDumper.add_representer(str, str_representer)


def create_agent_metadata(
    name: str,
    description: str = "",
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create agent metadata dictionary.
    
    Args:
        name: Agent name.
        description: Agent description.
        agent_id: Agent ID (optional for new agents).
        
    Returns:
        Metadata dictionary.
    """
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    return {
        'agent_id': agent_id,
        'name': name,
        'description': description,
        'created_at': current_time,
        'updated_at': current_time
    }


def create_flow_metadata(
    name: str,
    description: str = "",
    flow_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create flow metadata dictionary.
    
    Args:
        name: Flow name.
        description: Flow description.
        flow_id: Flow ID (optional for new flows).
        
    Returns:
        Metadata dictionary.
    """
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    metadata = {
        'name': name,
        'description': description,
        'created_at': current_time,
        'updated_at': current_time
    }
    
    # Only add flow_id if it's provided
    if flow_id is not None:
        metadata['flow_id'] = flow_id
        
    return metadata


def read_metadata(resource_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Read metadata.yaml from a resource directory.
    
    Args:
        resource_dir: Path to the resource directory.
        
    Returns:
        Metadata dictionary if successful, None if file doesn't exist or is invalid.
    """
    metadata_file = resource_dir / 'metadata.yaml'
    
    if not metadata_file.exists():
        return None
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Error reading metadata.yaml: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading metadata.yaml: {e}")
        return None


def write_metadata(resource_dir: Path, metadata: Dict[str, Any]) -> None:
    """
    Write metadata.yaml to a resource directory.
    
    Args:
        resource_dir: Path to the resource directory.
        metadata: Metadata dictionary to write.
    """
    # Create directory if it doesn't exist
    resource_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_file = resource_dir / 'metadata.yaml'
    
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                metadata,
                f,
                Dumper=LiteralDumper,
                default_flow_style=False,
                sort_keys=False,
                width=120,
                allow_unicode=True
            )
    except Exception as e:
        logger.error(f"Error writing metadata.yaml: {e}")
        raise


def update_metadata_timestamps(
    resource_dir: Path,
    updated_at: str,
    created_at: Optional[str] = None
) -> None:
    """
    Update timestamps in metadata.yaml.
    
    Args:
        resource_dir: Path to the resource directory.
        updated_at: New updated_at timestamp.
        created_at: New created_at timestamp (optional).
    """
    metadata = read_metadata(resource_dir)
    
    if metadata is None:
        # No metadata file exists, skip update
        return
    
    metadata['updated_at'] = updated_at
    if created_at:
        metadata['created_at'] = created_at
    
    write_metadata(resource_dir, metadata)