"""Freshness and coverage gates for event-driven claims."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class ScanCoverage:
    required: tuple[str, ...]
    completed: tuple[str, ...]
    failed: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing and not self.failed

    @property
    def missing(self) -> tuple[str, ...]:
        completed = set(self.completed)
        return tuple(item for item in self.required if item not in completed)


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


def evaluate_scan_coverage(
    required: Iterable[str],
    completed: Iterable[str],
    failed: Iterable[str] = (),
) -> ScanCoverage:
    """Return an auditable scan state; no-event is valid only when complete."""
    required_items = tuple(dict.fromkeys(required))
    completed_items = tuple(
        item for item in dict.fromkeys(completed) if item in required_items
    )
    failed_items = tuple(
        item for item in dict.fromkeys(failed) if item in required_items
    )
    return ScanCoverage(required_items, completed_items, failed_items)
