"""
Custom exceptions for channel operations.
"""

from typing import Optional, Dict, Any


class ChannelError(Exception):
    """Base exception for all channel-related errors."""
    
    def __init__(self, message: str, channel_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.channel_type = channel_type
        self.details = details or {}


class MessageSendError(ChannelError):
    """Raised when a message fails to send."""
    
    def __init__(self, message: str, channel_type: Optional[str] = None, 
                 recipient_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, channel_type, details)
        self.recipient_id = recipient_id


class ChannelUnavailableError(ChannelError):
    """Raised when a channel service is temporarily unavailable."""
    
    def __init__(self, message: str, channel_type: Optional[str] = None, 
                 retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, channel_type, details)
        self.retry_after = retry_after  # Seconds to wait before retrying


class ChannelAuthenticationError(ChannelError):
    """Raised when channel authentication fails."""
    pass


class InvalidRecipientError(MessageSendError):
    """Raised when the recipient is invalid or unreachable."""
    pass


class MessageFormatError(ChannelError):
    """Raised when the message format is invalid for the channel."""
    pass


class RateLimitExceededError(ChannelError):
    """Raised when the channel's rate limit is exceeded."""
    
    def __init__(self, message: str, channel_type: Optional[str] = None, 
                 retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, channel_type, details)
        self.retry_after = retry_after  # Seconds to wait before retrying