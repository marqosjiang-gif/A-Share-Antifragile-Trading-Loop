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
from datetime import datetime
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
WATCH_TICKERS = os.environ.get("WATCH_TICKERS", "")

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


def fetch_us_snapshot(codes: Iterable[str]) -> dict[str, tuple[str, str, float]]:
    text = http_get(
        "https://qt.gtimg.cn/q=" + ",".join(codes), codec="gbk"
    )
    result: dict[str, tuple[str, str, float]] = {}
    for segment in text.split(";"):
        if "=" not in segment:
            continue
        fields = segment.split("=", 1)[1].strip().strip('"').split("~")
        if len(fields) < 5:
            continue
        try:
            result[fields[0]] = (fields[1], fields[3], float(fields[4]))
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
            "| Symbol | Last | Change |",
            "|---|---:|---:|",
        ]
    )
    try:
        us = fetch_us_snapshot(("usSPY", "usQQQ", "usVIX"))
        for code in ("usSPY", "usQQQ", "usVIX"):
            if code not in us:
                continue
            name, price, change = us[code]
            lines.append(
                f"| {name} | {price} | "
                f"{direction(change)} {abs(change):.2f}% |"
            )
    except Exception:
        lines.append("| SPY / QQQ / VIX | -- | data unavailable |")

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

    lines.extend(
        [
            "",
            "## Research guardrails",
            "",
            "- Verify price, date, and volume before interpretation.",
            "- Remove unsupported narratives before adding a directional view.",
            "- Treat missing or conflicting data as lower confidence.",
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
