"""
Definition for the send_media_message tool.
"""

import asyncio
import logging
from typing import Optional

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from kapso.runner.channels.models import ChannelMessage, MessageChannelType, MessageContentType
from kapso.runner.channels.factory import send_message
from kapso.runner.channels.exceptions import (
    ChannelError,
    MessageSendError,
    ChannelUnavailableError,
    ChannelAuthenticationError,
)

logger = logging.getLogger(__name__)


@tool
async def send_media_message(
    media_url: str,
    media_type: str,
    caption: Optional[str] = None,
    filename: Optional[str] = None,
    config: RunnableConfig = None
) -> str:
    """
    Send a media message (image, video, audio, or document) to the user via WhatsApp.
    
    This function allows agents to share visual content, audio files, videos, and documents with users.
    The media must be accessible via a public URL or a URL that the WhatsApp servers can access.
    
    Guidelines:
    - Ensure the media_url is publicly accessible or properly authenticated
    - Use appropriate media_type: "image", "video", "audio", or "document"
    - Captions are supported for images, videos, and documents (not audio)
    - For documents, provide a filename to help users identify the file
    - Maximum file sizes vary by type (check WhatsApp documentation)
    
    Example Usage:
      - Image: media_url="https://example.com/chart.png", media_type="image", caption="Sales chart for Q4"
      - Video: media_url="https://example.com/demo.mp4", media_type="video", caption="Product demo"
      - Audio: media_url="https://example.com/recording.mp3", media_type="audio"
      - Document: media_url="https://example.com/report.pdf", media_type="document", caption="Monthly report", filename="report.pdf"
    
    Args:
        media_url (str): The URL of the media file to send. Must be accessible by WhatsApp servers.
        media_type (str): The type of media - must be one of: "image", "video", "audio", "document"
        caption (str, optional): A caption for the media (not supported for audio files)
        filename (str, optional): The filename to display (only used for documents)
        config (RunnableConfig): Runtime configuration containing channel details
    
    Returns:
        str: Confirmation that the media was sent successfully.
    """
    # Validate media type
    valid_media_types = ["image", "video", "audio", "document"]
    if media_type.lower() not in valid_media_types:
        raise ValueError(f"Invalid media_type '{media_type}'. Must be one of: {', '.join(valid_media_types)}")
    
    # Audio files don't support captions
    if media_type.lower() == "audio" and caption:
        logger.warning("Audio messages don't support captions. Ignoring caption parameter.")
        caption = None
    
    # Map media type to content type enum
    media_type_mapping = {
        "image": MessageContentType.IMAGE,
        "video": MessageContentType.VIDEO,
        "audio": MessageContentType.AUDIO,
        "document": MessageContentType.DOCUMENT
    }
    
    # Get channel configuration
    configurable = config.get("configurable", {}) if config else {}
    recipient_id = configurable.get("phone_number")
    thread_id = configurable.get("thread_id")
    test_mode = configurable.get("test_mode", False)
    channel_type = configurable.get("channel_type", "whatsapp")
    
    # Build content dictionary
    content = {
        "media_url": media_url,
        "media_type": media_type.lower()
    }
    if caption:
        content["caption"] = caption
    
    # Build metadata
    metadata = {
        "test_mode": test_mode,
        "media_type": media_type.lower()
    }
    if filename and media_type.lower() == "document":
        metadata["filename"] = filename
    
    # Create channel message
    channel_message = ChannelMessage(
        content=content,
        channel_type=MessageChannelType(channel_type),
        recipient_id=recipient_id,
        thread_id=thread_id,
        content_type=media_type_mapping[media_type.lower()],
        metadata=metadata
    )
    
    if test_mode:
        return f"Media sent: {media_type} from {media_url}" + (f" with caption: {caption}" if caption else "")
    else:
        # Send via factory function with retry logic
        max_retries = 3
        retry_delay = 1.0  # Initial delay in seconds
        
        for attempt in range(max_retries):
            try:
                result = await send_message(channel_message)
                return result
            except ChannelUnavailableError as e:
                if attempt < max_retries - 1:
                    # Use retry_after if provided, otherwise exponential backoff
                    wait_time = e.retry_after or (retry_delay * (2 ** attempt))
                    logger.warning(
                        "Channel unavailable for media message (attempt %d/%d), retrying in %s seconds: %s",
                        attempt + 1, max_retries, wait_time, str(e)
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Failed to send media message after %d attempts: %s", max_retries, str(e))
                    raise
            except (ChannelAuthenticationError, MessageSendError, ChannelError) as e:
                # Don't retry for authentication or other errors
                logger.error("Error sending media message: %s", str(e))
                raise