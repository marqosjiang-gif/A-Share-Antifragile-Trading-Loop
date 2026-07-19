"""Freshness gates for event-driven claims."""

from __future__ import annotations

from datetime import datetime, timezone


def is_fresh_event(
    event_time: datetime, now: datetime | None = None, max_age_hours: int = 168
) -> bool:
    """Return true only when an event falls inside the allowed lookback window."""
    if max_age_hours <= 0:
        raise ValueError("max_age_hours must be positive")
    reference = now or datetime.now(timezone.utc)
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    age_hours = (reference - event_time).total_seconds() / 3600
    return 0 <= age_hours <= max_age_hours
