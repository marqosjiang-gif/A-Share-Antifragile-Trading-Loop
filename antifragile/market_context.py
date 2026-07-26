"""Key-free weekly macro context with explicit date windows."""

from __future__ import annotations

import csv
import io
import json
import ssl
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime


_SSL_CONTEXT = ssl.create_default_context()


@dataclass(frozen=True)
class WeeklyMetric:
    name: str
    start: date
    end: date
    start_value: float
    end_value: float
    change_pct: float
    source: str
    note: str = ""


def _weekly_metric(
    name: str,
    points: list[tuple[date, float]],
    source: str,
    *,
    prefer_fridays: bool = False,
) -> WeeklyMetric:
    if len(points) < 2:
        raise ValueError(f"{name}: fewer than two valid observations")
    ordered = sorted(dict(points).items())
    note = ""
    if prefer_fridays:
        fridays = [(day, value) for day, value in ordered if day.weekday() == 4]
        if len(fridays) >= 2:
            sample = fridays[-2:]
        else:
            sample = ordered[-2:]
            note = "Friday observations unavailable; used the latest two trading days."
    else:
        sample = ordered[-5:] if len(ordered) >= 5 else ordered
        if len(sample) < 5:
            note = f"Degraded to {len(sample)} available observations."

    (start, start_value), (end, end_value) = sample[0], sample[-1]
    if start_value == 0:
        raise ValueError(f"{name}: zero start value")
    return WeeklyMetric(
        name=name,
        start=start,
        end=end,
        start_value=start_value,
        end_value=end_value,
        change_pct=(end_value / start_value - 1) * 100,
        source=source,
        note=note,
    )


def _http_get(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(
        request, timeout=timeout, context=_SSL_CONTEXT
    ) as response:
        return response.read().decode("utf-8")


def fetch_dxy_weekly() -> WeeklyMetric:
    """Fetch DXY and compare the latest two Friday closes."""
    errors: list[str] = []
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        try:
            payload = json.loads(
                _http_get(
                    f"https://{host}/v8/finance/chart/"
                    "DX-Y.NYB?range=2mo&interval=1d"
                )
            )
            result = (payload.get("chart", {}).get("result") or [])[0]
            timestamps = result.get("timestamp") or []
            closes = (
                result.get("indicators", {})
                .get("quote", [{}])[0]
                .get("close")
                or []
            )
            points = [
                (datetime.utcfromtimestamp(timestamp).date(), float(close))
                for timestamp, close in zip(timestamps, closes)
                if close is not None
            ]
            return _weekly_metric(
                "DXY",
                points,
                f"Yahoo Finance v8 ({host}, DX-Y.NYB)",
                prefer_fridays=True,
            )
        except Exception as exc:
            errors.append(f"{host}: {type(exc).__name__}")
    raise ValueError("; ".join(errors) or "DXY unavailable")


def parse_fred_series(text: str, value_column: str) -> list[tuple[date, float]]:
    """Parse a FRED CSV response without silently filling missing values."""
    points: list[tuple[date, float]] = []
    for row in csv.DictReader(io.StringIO(text)):
        raw_value = row.get(value_column)
        if raw_value in (None, "", "."):
            continue
        raw_date = row.get("observation_date") or row.get("DATE")
        if not raw_date:
            continue
        points.append((date.fromisoformat(raw_date), float(raw_value)))
    return points


def fetch_brent_weekly() -> WeeklyMetric:
    """Fetch the latest five valid Brent observations from FRED."""
    series = "DCOILBRENTEU"
    text = _http_get(
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}",
        timeout=25,
    )
    return _weekly_metric(
        "Brent crude",
        parse_fred_series(text, series),
        f"FRED {series}",
    )
