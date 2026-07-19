"""Key-free parsing and fetching of public CFTC COMEX gold positioning."""

from __future__ import annotations

import csv
import io
import ssl
import urllib.request
from dataclasses import dataclass


GOLD_MARKET_CODE = "088691"
DISAGGREGATED_URL = "https://www.cftc.gov/dea/newcot/f_disagg.txt"


@dataclass(frozen=True)
class GoldPositioning:
    as_of: str
    managed_money_long: int
    managed_money_short: int
    managed_money_net: int
    prior_week_net: int
    weekly_net_change: int
    source: str = "CFTC Disaggregated Futures-Only (COMEX 088691)"


def parse_disaggregated_gold(raw: str) -> GoldPositioning:
    """Parse the COMEX gold row from CFTC's Disaggregated Futures-Only file."""
    for row in csv.reader(io.StringIO(raw)):
        if len(row) <= 63 or row[3].strip() != GOLD_MARKET_CODE:
            continue
        long_now = int(row[13])
        short_now = int(row[14])
        long_change = int(row[62])
        short_change = int(row[63])
        net_now = long_now - short_now
        net_change = long_change - short_change
        return GoldPositioning(
            as_of=row[2].strip(),
            managed_money_long=long_now,
            managed_money_short=short_now,
            managed_money_net=net_now,
            prior_week_net=net_now - net_change,
            weekly_net_change=net_change,
        )
    raise ValueError("COMEX gold row 088691 unavailable or malformed")


def fetch_gold_positioning(timeout: int = 20) -> GoldPositioning:
    """Fetch current public CFTC data; callers must surface failures explicitly."""
    request = urllib.request.Request(
        DISAGGREGATED_URL, headers={"User-Agent": "Mozilla/5.0"}
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return parse_disaggregated_gold(response.read().decode("latin-1"))
