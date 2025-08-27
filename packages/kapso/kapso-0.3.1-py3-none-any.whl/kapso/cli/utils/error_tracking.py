"""
Error tracking utilities for Kapso CLI.
"""

import os
import platform
from typing import Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.excepthook import ExcepthookIntegration
    from sentry_sdk.integrations.atexit import AtexitIntegration
    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False


def init_error_tracking(version: str, debug: bool = False) -> None:
    """
    Initialize error tracking with Sentry.

    Args:
        version: The CLI version
        debug: Whether to enable debug mode
    """
    if not HAS_SENTRY:
        return

    # Allow users to opt out via environment variable
    if os.getenv("KAPSO_DISABLE_ERROR_TRACKING", "").lower() in ("true", "1", "yes"):
        return

    # Hardcoded DSN for CLI - this is safe to expose since it's client-side
    # This should be different from your server-side DSN
    CLI_SENTRY_DSN = "https://c0158f8f356ee909a1a49d1f44b4823e@o4507091170885632.ingest.us.sentry.io/4509464347541504"

    # Allow override for testing
    dsn = os.getenv("KAPSO_SENTRY_DSN", CLI_SENTRY_DSN)

    if not dsn or dsn.startswith("https://YOUR_PUBLIC_KEY"):
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            release=f"kapso-cli@{version}",
            environment="cli-production" if not debug else "cli-development",
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,  # 10% of transactions
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
            integrations=[
                ExcepthookIntegration(always_run=True),
                AtexitIntegration(callback=None),
            ],
            before_send=before_send_filter,
        )
        
        # Set global tags after initialization
        sentry_sdk.set_tag("python_version", platform.python_version())
        sentry_sdk.set_tag("platform", platform.system())
        sentry_sdk.set_tag("platform_version", platform.version())
        
    except Exception as e:
        # Only fail silently in production
        if debug:
            print(f"Failed to initialize Sentry: {e}")
        pass


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.

    This function allows you to:
    - Filter out certain types of errors
    - Remove sensitive data
    - Add additional context
    """
    # Filter out KeyboardInterrupt (Ctrl+C)
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if exc_type == KeyboardInterrupt:
            return None

    # Remove any potential sensitive data from breadcrumbs
    if "breadcrumbs" in event:
        for crumb in event["breadcrumbs"]:
            if "data" in crumb:
                # Remove potential API keys or tokens
                for key in list(crumb["data"].keys()):
                    if any(sensitive in key.lower() for sensitive in ["key", "token", "password", "secret"]):
                        crumb["data"][key] = "[REDACTED]"

    # Add CLI-specific context
    if "contexts" not in event:
        event["contexts"] = {}

    event["contexts"]["cli"] = {
        "cwd": os.getcwd(),
        "has_kapso_yaml": os.path.exists("kapso.yaml"),
        "has_agent_yaml": os.path.exists("agent.yaml"),
    }

    return event


def capture_exception(error: Exception, extra_context: Optional[dict] = None) -> None:
    """
    Manually capture an exception with additional context.

    Args:
        error: The exception to capture
        extra_context: Additional context to include
    """
    if not HAS_SENTRY:
        return

    try:
        with sentry_sdk.push_scope() as scope:
            if extra_context:
                for key, value in extra_context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    except Exception:
        # Silently fail if capture fails
        pass


def set_user_context(user_id: Optional[str] = None, project_id: Optional[str] = None) -> None:
    """
    Set user context for error tracking.

    Args:
        user_id: Anonymous user identifier
        project_id: Current project ID
    """
    if not HAS_SENTRY:
        return

    try:
        sentry_sdk.set_user({
            "id": user_id or "anonymous",
            "project_id": project_id,
        })
    except Exception:
        pass