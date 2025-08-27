"""
Utility functions for working with knowledge bases.
"""

from typing import Any, Dict, List


def extract_knowledge_base_text(node_config: Dict[str, Any], kb_key: str) -> str:
    """
    Extract knowledge base text from node config on demand.
    
    Args:
        node_config: Node configuration containing knowledge base definitions
        kb_key: Key identifying which knowledge base to extract
        
    Returns:
        The knowledge base text if found, empty string otherwise
    """
    # Check main knowledge base config
    if "knowledge_base" in node_config:
        kb_config = node_config["knowledge_base"]
        if kb_config.get("key", f"kb_{node_config.get('name', '')}") == kb_key:
            if "knowledge_base_text" in kb_config:
                return kb_config["knowledge_base_text"]
    
    # Check subagent knowledge bases
    if "subagent" in node_config and "knowledge_bases" in node_config["subagent"]:
        for kb in node_config["subagent"]["knowledge_bases"]:
            if kb.get("key", "") == kb_key and "knowledge_base_text" in kb:
                return kb["knowledge_base_text"]
    
    return ""


def list_available_knowledge_bases(node_config: Dict[str, Any]) -> List[str]:
    """
    List all available knowledge base keys in a node config.
    
    Args:
        node_config: Node configuration containing knowledge base definitions
        
    Returns:
        List of knowledge base keys
    """
    kb_keys = []
    
    # Check main knowledge base config
    if "knowledge_base" in node_config and "knowledge_base_text" in node_config["knowledge_base"]:
        kb_key = node_config["knowledge_base"].get("key", f"kb_{node_config.get('name', '')}")
        kb_keys.append(kb_key)
    
    # Check subagent knowledge bases
    if "subagent" in node_config and "knowledge_bases" in node_config["subagent"]:
        for kb in node_config["subagent"]["knowledge_bases"]:
            if "knowledge_base_text" in kb:
                kb_key = kb.get("key", "")
                if kb_key:
                    kb_keys.append(kb_key)
    
    return kb_keys 