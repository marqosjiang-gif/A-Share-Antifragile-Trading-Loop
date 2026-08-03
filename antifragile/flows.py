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


def classify_stock_flow(
    net_amount: float,
    market_cap_cny: float,
) -> str:
    """Classify 20-day flow using liquidity-aware public thresholds.

    Large-cap and smaller-cap stocks must not share one absolute threshold.
    The output is research context, not a standalone trade instruction.
    """
    if market_cap_cny <= 0:
        raise ValueError("market_cap_cny must be positive")
    if market_cap_cny >= 100_000_000_000:
        inflow, outflow, neutral = 3_000_000_000, -3_000_000_000, 1_000_000_000
    else:
        inflow, outflow, neutral = 150_000_000, -150_000_000, 50_000_000
    if net_amount > inflow:
        return "persistent_inflow"
    if net_amount < outflow:
        return "persistent_outflow"
    if abs(net_amount) < neutral:
        return "range_bound"
    return "mixed"


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
