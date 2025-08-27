"""
Simple thread-aware logging using contextvars.
"""

import contextvars
import logging

# Global context variables
message_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "message_id", default="no-message"
)
thread_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "thread_id", default="no-thread"
)


class ThreadFormatter(logging.Formatter):
    """Custom formatter that adds message_id and thread_id to log records."""

    def format(self, record: logging.LogRecord) -> str:
        # Add message_id to the record if it doesn't exist
        if not hasattr(record, "message_id"):
            record.message_id = message_context.get()
        # Add thread_id to the record if it doesn't exist
        if not hasattr(record, "thread_id"):
            record.thread_id = thread_context.get()
        return super().format(record)


def set_message_context(message_id: str) -> None:
    """Set the message_id in the context."""
    message_context.set(message_id)


def set_thread_context(thread_id: str) -> None:
    """Set the thread_id in the context."""
    thread_context.set(thread_id)


def clear_thread_context() -> None:
    """Clear the thread_id from context."""
    thread_context.set("no-thread")


def clear_message_context() -> None:
    """Clear the message_id from context."""
    message_context.set("no-message")
