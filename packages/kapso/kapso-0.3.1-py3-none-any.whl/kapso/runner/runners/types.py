"""
Type definitions for runners.
"""

from typing import Callable, Dict, Any, Optional, Awaitable

# Type alias for error callback function
ErrorCallback = Callable[
    [str, Exception, int, Dict[str, Any]],  # thread_id, error, delivery_attempt, context
    Awaitable[None]
]