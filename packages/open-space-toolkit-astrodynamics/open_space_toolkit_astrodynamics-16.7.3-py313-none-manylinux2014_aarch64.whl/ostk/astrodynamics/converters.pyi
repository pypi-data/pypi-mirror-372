from __future__ import annotations
from datetime import datetime
from datetime import timezone
from ostk.physics.time import Instant
from ostk.physics.time import Interval
from ostk.physics.time import Scale
import re as re
import typing
__all__ = ['Instant', 'Interval', 'Scale', 'coerce_to_datetime', 'coerce_to_instant', 'coerce_to_interval', 'coerce_to_iso', 'datetime', 're', 'timezone']
def coerce_to_datetime(value: Instant | datetime | str) -> datetime:
    """
    
    Return datetime from value.
    
    Args:
        value (Instant | datetime | str): A value to coerce.
    
    Returns:
        datetime: The coerced datetime.
    """
def coerce_to_instant(value: Instant | datetime | str) -> Instant:
    """
    
    Return Instant from value.
    
    Args:
        value (Instant | datetime | str): A value to coerce.
    
    Returns:
        Instant: The coerced Instant.
    """
def coerce_to_interval(value: Interval | tuple[Instant, Instant] | tuple[datetime, datetime] | tuple[str, str] | str) -> Interval:
    """
    
    Return Interval from value.
    
    Args:
        value (Interval | tuple[Instant, Instant] | tuple[datetime, datetime] | tuple[str, str]): A value to coerce.
    
    Returns:
        Interval: The coerced Interval.
    """
def coerce_to_iso(value: Instant | datetime | str, timespec: str = 'microseconds') -> str:
    """
    
    Return an ISO string from value.
    
    Args:
        value (Instant | datetime | str): A value to coerce.
        timespec (str): A time resolution. Defaults to "microseconds".
    
    Returns:
        str: The coerced ISO string.
    """
