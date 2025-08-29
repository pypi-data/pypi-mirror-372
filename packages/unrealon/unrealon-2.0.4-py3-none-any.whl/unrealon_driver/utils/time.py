"""
Time utilities for UnrealOn Driver.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)
