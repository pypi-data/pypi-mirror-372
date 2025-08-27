"""
Knowledge base tool implementation for SubagentNode.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from kapso.builder.nodes.subagent.tools.base import SubagentTool


@dataclass(kw_only=True)
class KnowledgeBaseTool(SubagentTool):
    """Knowledge base tool for accessing information sources."""
    
    knowledge_base_text: Optional[str] = None
    knowledge_base_file: Optional[str] = None
    
    def __post_init__(self):
        """Validate knowledge base tool after initialization."""
        super().__post_init__()
        
        if not self.knowledge_base_text and not self.knowledge_base_file:
            raise ValueError(
                f"Knowledge base tool '{self.name}' must have either "
                "knowledge_base_text or knowledge_base_file"
            )
    
    def tool_type(self) -> str:
        """Return the tool type for serialization."""
        return "knowledge_base"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "name": self.name,
            "description": self.description
        }
        
        # If we have a file, read its content and include it as text
        if self.knowledge_base_file is not None:
            try:
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                # Always serialize file content as knowledge_base_text
                result["knowledge_base_text"] = file_content
            except Exception as e:
                # If file can't be read, include the file path and existing text if any
                result["knowledge_base_file"] = self.knowledge_base_file
                if self.knowledge_base_text is not None:
                    result["knowledge_base_text"] = self.knowledge_base_text
        elif self.knowledge_base_text is not None:
            result["knowledge_base_text"] = self.knowledge_base_text
            
        return result
    
    @classmethod
    def from_file(cls, name: str, file_path: str, description: str = "") -> "KnowledgeBaseTool":
        """
        Create a knowledge base tool from file content.
        
        Args:
            name: Tool name
            file_path: Path to the knowledge base file
            description: Tool description
            
        Returns:
            KnowledgeBaseTool instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return cls(
            name=name,
            knowledge_base_text=content,
            description=description
        )