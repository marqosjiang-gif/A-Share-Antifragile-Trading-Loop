#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a key-free weekly market snapshot for configurable A-share symbols."""

from __future__ import annotations

import json
import os
import re
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from antifragile.cftc import fetch_gold_positioning
from antifragile.earnings_calendar import get_upcoming, load_calendar
from antifragile.market_context import fetch_brent_weekly, fetch_dxy_weekly


BASE_DIR = Path(__file__).resolve().parent
WATCH_TICKERS = os.environ.get("WATCH_TICKERS", "")
ENABLE_CFTC_GOLD = os.environ.get("ENABLE_CFTC_GOLD", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}
ENABLE_MACRO_CONTEXT = os.environ.get(
    "ENABLE_MACRO_CONTEXT", "1"
).strip().lower() not in {"0", "false", "no"}
EARNINGS_CALENDAR_PATH = os.environ.get("EARNINGS_CALENDAR_PATH", "").strip()

_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def parse_watch_tickers(raw: str) -> list[str]:
    """Return unique Yahoo-style A-share symbols from a comma/space list."""
    symbols: list[str] = []
    for token in re.split(r"[\s,;]+", raw.strip().upper()):
        if not token:
            continue
        token = token.replace(".SH", ".SS")
        if not re.fullmatch(r"\d{6}\.(SS|SZ)", token):
            raise ValueError(
                f"Unsupported ticker '{token}'. Use six digits plus .SS or .SZ."
            )
        if token not in symbols:
            symbols.append(token)
    return symbols


def eastmoney_secid(symbol: str) -> str:
    """Convert an A-share symbol into an Eastmoney secid."""
    code, market = symbol.split(".", 1)
    return f"{'1' if market == 'SS' else '0'}.{code}"


def http_get(url: str, timeout: int = 15, codec: str = "utf-8") -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://quote.eastmoney.com/",
        },
    )
    with urllib.request.urlopen(
        req, timeout=timeout, context=_SSL_CONTEXT
    ) as response:
        return response.read().decode(codec, errors="ignore")


def fetch_index(secid: str) -> tuple[str, float, float]:
    url = (
        "https://push2.eastmoney.com/api/qt/stock/get?"
        + urllib.parse.urlencode(
            {"secid": secid, "fields": "f58,f43,f170"}
        )
    )
    payload = json.loads(http_get(url)).get("data") or {}
    if not payload:
        raise ValueError("index data unavailable")
    return (
        str(payload.get("f58") or secid),
        float(payload["f43"]) / 100,
        float(payload["f170"]) / 100,
    )


def fetch_us_snapshot(
    codes: Iterable[str],
) -> dict[str, tuple[str, str, float, datetime]]:
    text = http_get(
        "https://qt.gtimg.cn/q=" + ",".join(codes), codec="gbk"
    )
    result: dict[str, tuple[str, str, float]] = {}
    for segment in text.split(";"):
        if "=" not in segment:
            continue
        raw_key, raw_value = segment.split("=", 1)
        key = raw_key.strip().removeprefix("v_")
        fields = raw_value.strip().strip('"').split("~")
        if len(fields) < 33:
            continue
        try:
            result[key] = (
                fields[1],
                fields[3],
                float(fields[32]),
                datetime.strptime(fields[30], "%Y-%m-%d %H:%M:%S"),
            )
        except (TypeError, ValueError):
            continue
    return result


def fetch_weekly_move(symbol: str) -> dict[str, object]:
    """Use the latest represented trading week: first open to last close."""
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get?"
        + urllib.parse.urlencode(
            {
                "secid": eastmoney_secid(symbol),
                "fields1": "f1,f2,f3",
                "fields2": "f51,f52,f53,f56",
                "klt": "101",
                "fqt": "0",
                "end": "20500101",
                "lmt": "12",
            }
        )
    )
    rows = (json.loads(http_get(url)).get("data") or {}).get("klines") or []
    parsed = []
    for row in rows:
        fields = row.split(",")
        if len(fields) < 3:
            continue
        day = datetime.strptime(fields[0], "%Y-%m-%d").date()
        parsed.append(
            {
                "date": day,
                "open": float(fields[1]),
                "close": float(fields[2]),
                "volume": float(fields[5]) if len(fields) > 5 else 0,
            }
        )
    if not parsed:
        raise ValueError("daily kline unavailable")

    latest_week = parsed[-1]["date"].isocalendar()[:2]
    week = [
        row for row in parsed
        if row["date"].isocalendar()[:2] == latest_week
    ]
    first, last = week[0], week[-1]
    change_pct = (last["close"] / first["open"] - 1) * 100
    return {
        "start": first["date"].isoformat(),
        "end": last["date"].isoformat(),
        "close": last["close"],
        "change_pct": change_pct,
        "volume": sum(float(row["volume"]) for row in week),
    }


def direction(value: float) -> str:
    return "▲" if value >= 0 else "▼"


def _format_weekly_metric(metric) -> str:
    note = f" ({metric.note})" if metric.note else ""
    return (
        f"| {metric.name} | {metric.end_value:.2f} | "
        f"{direction(metric.change_pct)} {abs(metric.change_pct):.2f}% | "
        f"{metric.start.isoformat()} to {metric.end.isoformat()} | "
        f"{metric.source}{note} |"
    )


def build_report(symbols: list[str]) -> str:
    now = datetime.now()
    lines = [
        f"# A-Share Antifragile Weekly Snapshot · {now:%Y-%m-%d}",
        "",
        "> Runtime market data only. Missing sources are shown explicitly.",
        "",
        "## Market environment",
        "",
        "### China A-share indices",
        "",
        "| Index | Last | Change |",
        "|---|---:|---:|",
    ]

    for secid, label in (
        ("1.000001", "SSE Composite"),
        ("0.399001", "SZSE Component"),
        ("1.000688", "STAR 50"),
    ):
        try:
            _, price, change = fetch_index(secid)
            lines.append(
                f"| {label} | {price:.2f} | "
                f"{direction(change)} {abs(change):.2f}% |"
            )
        except Exception:
            lines.append(f"| {label} | -- | data unavailable |")

    lines.extend(
        [
            "",
            "### US market context",
            "",
            "| Symbol | Last | Change | As of |",
            "|---|---:|---:|---|",
        ]
    )
    try:
        us = fetch_us_snapshot(("usSPY", "usQQQ", "usVIX"))
        for code in ("usSPY", "usQQQ", "usVIX"):
            if code not in us:
                continue
            name, price, change, as_of = us[code]
            if as_of < datetime.now() - timedelta(days=7):
                lines.append(f"| {name} | -- | stale data rejected | {as_of:%Y-%m-%d} |")
                continue
            lines.append(
                f"| {name} | {price} | "
                f"{direction(change)} {abs(change):.2f}% | {as_of:%Y-%m-%d} |"
            )
    except Exception:
        lines.append("| SPY / QQQ / VIX | -- | data unavailable | -- |")

    lines.extend(
        [
            "",
            "### Weekly macro context",
            "",
            "| Metric | Last | Weekly move | Window | Source |",
            "|---|---:|---:|---|---|",
        ]
    )
    if not ENABLE_MACRO_CONTEXT:
        lines.append("| DXY / Brent crude | -- | disabled | -- | configuration |")
    else:
        for fetcher, label in (
            (fetch_dxy_weekly, "DXY"),
            (fetch_brent_weekly, "Brent crude"),
        ):
            try:
                lines.append(_format_weekly_metric(fetcher()))
            except Exception as exc:
                lines.append(
                    f"| {label} | -- | data unavailable | -- | "
                    f"{type(exc).__name__} |"
                )

    lines.extend(["", "## Configured A-share watchlist", ""])
    if not symbols:
        lines.extend(
            [
                "No stock symbols configured.",
                "",
                "Set `WATCH_TICKERS` with comma-separated `.SS` / `.SZ` symbols,",
                "then run the script again.",
            ]
        )
    else:
        lines.extend(
            [
                "| Symbol | Week | Last close | Weekly move | Weekly volume |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for symbol in symbols:
            try:
                item = fetch_weekly_move(symbol)
                period = f"{item['start']} to {item['end']}"
                change = float(item["change_pct"])
                lines.append(
                    f"| {symbol} | {period} | {float(item['close']):.2f} | "
                    f"{direction(change)} {abs(change):.2f}% | "
                    f"{float(item['volume']):.0f} |"
                )
            except Exception:
                lines.append(
                    f"| {symbol} | -- | -- | data unavailable | -- |"
                )

    lines.extend(["", "## Forward disclosure calendar", ""])
    try:
        calendar = load_calendar(EARNINGS_CALENDAR_PATH or None)
        focus, extended, _, pending = get_upcoming(
            calendar, datetime.now().strftime("%Y%m%d")
        )
        upcoming = focus + extended
        if upcoming:
            lines.extend(
                [
                    "| Symbol | Scheduled date | Days ahead | Source |",
                    "|---|---|---:|---|",
                ]
            )
            for item in upcoming:
                lines.append(
                    f"| {item['code']} | {item['scheduled_date']} | "
                    f"{item['days']} | {item.get('source') or 'local calendar'} |"
                )
        elif pending:
            lines.append(
                "Earnings dates are incomplete; no disclosure conclusion was generated."
            )
        else:
            lines.append(
                "No configured disclosures fall inside the next 30 days, "
                "or the local calendar is empty."
            )
    except Exception as exc:
        lines.append(
            "Earnings calendar unavailable; no date was inferred "
            f"({type(exc).__name__})."
        )

    lines.extend(["", "## Public positioning context", ""])
    if not ENABLE_CFTC_GOLD:
        lines.append("CFTC gold positioning is disabled by configuration.")
    else:
        try:
            gold = fetch_gold_positioning()
            lines.extend(
                [
                    "### COMEX gold managed-money positioning",
                    "",
                    "| As of | Long | Short | Net | Prior-week net | Weekly change |",
                    "|---|---:|---:|---:|---:|---:|",
                    f"| {gold.as_of} | {gold.managed_money_long:,} | "
                    f"{gold.managed_money_short:,} | {gold.managed_money_net:,} | "
                    f"{gold.prior_week_net:,} | {gold.weekly_net_change:+,} |",
                    "",
                    f"Source: {gold.source}. This is a weekly positioning context signal, not a trade trigger.",
                ]
            )
        except Exception as exc:
            lines.append(
                "CFTC gold positioning unavailable; no positioning conclusion was generated "
                f"({type(exc).__name__})."
            )

    lines.extend(
        [
            "",
            "## Research guardrails",
            "",
            "- Verify price, date, and volume before interpretation.",
            "- Remove unsupported narratives before adding a directional view.",
            "- Treat missing or conflicting data as lower confidence.",
            "- Require event claims to pass a 168-hour freshness gate.",
            "- A no-event conclusion requires every configured event dimension to complete its scan.",
            "- Keep sector five-day flow separate from stock 5/10/20-day flow and print exact dates.",
            "- Let an adequately sampled historical BOLL signal lead; use lower-priority evidence to confirm or constrain it.",
            "- This snapshot does not place orders or provide investment advice.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    try:
        symbols = parse_watch_tickers(WATCH_TICKERS)
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return 2

    report = build_report(symbols)
    output = BASE_DIR / f"antifragile_weekly_{datetime.now():%Y%m%d}.md"
    output.write_text(report, encoding="utf-8")
    print(f"Report generated: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
