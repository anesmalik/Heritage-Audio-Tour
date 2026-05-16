"""
streaming.py — SSE event formatting helpers.

Responsibility: Format pipeline progress events as properly structured
Server-Sent Events that the browser's EventSource API can parse.

SSE format (required by spec):
    data: {"key": "value"}\n\n

The double newline is mandatory — it signals end of event to the client.
"""

import json
from enum import Enum


class EventType(str, Enum):
    """
    Event types emitted during pipeline execution.
    The frontend uses these to update the UI appropriately.
    """
    PROGRESS  = "progress"   # a node started or completed
    SUCCESS   = "success"    # full pipeline completed
    ERROR     = "error"      # something went wrong
    CACHED    = "cached"     # tour was served from cache


def format_sse(event_type: EventType, message: str, data: dict = None) -> str:
    """
    Format a progress update as an SSE event string.

    Args:
        event_type: One of EventType values
        message:    Human-readable status message for the UI
        data:       Optional extra payload (e.g. stop names, file list)

    Returns:
        A properly formatted SSE string with double newline terminator.
    """
    payload = {
        "type":    event_type.value,
        "message": message,
    }
    if data:
        payload["data"] = data

    return json.dumps(payload)


def progress(message: str, data: dict = None) -> str:
    """Shorthand for a progress event."""
    return format_sse(EventType.PROGRESS, message, data)


def success(message: str, data: dict = None) -> str:
    """Shorthand for a success event."""
    return format_sse(EventType.SUCCESS, message, data)


def error(message: str) -> str:
    """Shorthand for an error event."""
    return format_sse(EventType.ERROR, message)


def cached(message: str, data: dict = None) -> str:
    """Shorthand for a cached tour event."""
    return format_sse(EventType.CACHED, message, data)
