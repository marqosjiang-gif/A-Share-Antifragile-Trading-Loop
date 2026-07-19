"""Capital-flow window calculations with explicit trading-date coverage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping


@dataclass(frozen=True)
class FlowWindow:
    trading_days: int
    start: date
    end: date
    net_amount: float


def aggregate_flows(
    rows: Iterable[Mapping[str, object]], windows: tuple[int, ...] = (5, 10, 20)
) -> dict[int, FlowWindow]:
    """Aggregate verified daily flows and retain the exact date range.

    Each row requires ``date`` (ISO date or ``date``) and ``net_amount``.
    Duplicate trading dates are rejected to prevent accidental double counting.
    """
    parsed: dict[date, float] = {}
    for row in rows:
        raw_date = row.get("date")
        day = raw_date if isinstance(raw_date, date) else date.fromisoformat(str(raw_date))
        if day in parsed:
            raise ValueError(f"duplicate trading date: {day.isoformat()}")
        parsed[day] = float(row["net_amount"])

    ordered = sorted(parsed.items())
    result: dict[int, FlowWindow] = {}
    for size in windows:
        if size <= 0:
            raise ValueError("flow window must be positive")
        if len(ordered) < size:
            continue
        sample = ordered[-size:]
        result[size] = FlowWindow(
            trading_days=size,
            start=sample[0][0],
            end=sample[-1][0],
            net_amount=sum(amount for _, amount in sample),
        )
    return result
