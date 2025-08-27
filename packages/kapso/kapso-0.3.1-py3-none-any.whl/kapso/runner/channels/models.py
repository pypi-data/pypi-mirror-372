from enum import Enum
from typing import Dict, Any, Optional, Union
import uuid
import time

class MessageChannelType(str, Enum):
    """Supported messaging channels."""
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEB = "web"
    # Add more channels as needed

class MessageContentType(str, Enum):
    """Types of message content."""
    TEXT = "text"
    TEMPLATE = "template"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    # Add more content types as needed

class ChannelMessage:
    """A channel-agnostic message representation."""

    def __init__(
        self,
        content: Union[str, Dict[str, Any]],
        channel_type: MessageChannelType,
        recipient_id: str,
        thread_id: str,
        content_type: MessageContentType = MessageContentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
    ):
        self.content = content
        self.channel_type = channel_type
        self.recipient_id = recipient_id
        self.thread_id = thread_id
        self.content_type = content_type
        self.metadata = metadata or {}
        self.message_id = message_id or str(uuid.uuid4())
        self.timestamp = time.time()