"""
Time utilities for UnrealOn.

Provides timezone-aware datetime functions to replace deprecated datetime.utc_now().
"""

from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """
    Get current UTC time as timezone-aware datetime.
    
    Replacement for deprecated datetime.utc_now().
    
    Returns:
        datetime: Current UTC time with timezone info
    """
    return datetime.now(timezone.utc)


def utc_timestamp() -> str:
    """
    Get current UTC time as ISO format string.
    
    Returns:
        str: Current UTC time in ISO format
    """
    return utc_now().isoformat()


def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to ISO format string.
    
    Args:
        dt: Datetime to convert (can be None)
        
    Returns:
        str or None: ISO format string or None if input was None
    """
    if dt is None:
        return None
    return dt.isoformat()


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is timezone-aware and in UTC.
    
    Args:
        dt: Datetime to convert
        
    Returns:
        datetime: UTC timezone-aware datetime
    """
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
