#!/usr/bin/env python3
"""Create a private, auditable weekly A-share research scaffold.

The public runner intentionally stops before any order recommendation. It proves
the timing and evidence contract while leaving a user's live data integrations
and private watchlist outside the repository.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a weekly research scaffold.")
    parser.add_argument("--watchlist", default="watchlist.local.json")
    parser.add_argument("--as-of", help="Report date in YYYY-MM-DD; defaults to today.")
    parser.add_argument("--output-dir", default=".")
    return parser.parse_args()


def load_watchlist(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    universe = data.get("universe")
    if not isinstance(universe, list) or not universe:
        raise ValueError("watchlist needs a non-empty 'universe' array")
    required = {"code", "exchange", "name"}
    for item in universe:
        if not isinstance(item, dict) or not required.issubset(item):
            raise ValueError("each watchlist item needs code, exchange, and name")
        forbidden = {"shares", "quantity", "cost", "cost_basis", "account", "email"}
        if forbidden.intersection(item):
            raise ValueError("watchlist is research-only; remove position or personal fields")
    return universe


def next_monday(day: date) -> date:
    return day + timedelta(days=(7 - day.weekday()) % 7 or 7)


def build_report(as_of: date, watchlist: list[dict[str, str]], source: Path) -> str:
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    start = next_monday(as_of)
    end = start + timedelta(days=4)
    rows = "\n".join(
        f"| {item['code']}.{item['exchange']} | {item['name']} | pending live-data validation |"
        for item in watchlist
    )
    return f"""# Weekly Quant Research Scaffold: {as_of:%Y-%m-%d}

```yaml
report_generated_at: {generated_at}
evidence_cutoff: {generated_at}
decision_status: research_only
watchlist_source: {source.name}
validation_window: {start:%Y-%m-%d} open to {end:%Y-%m-%d} close, subject to exchange holidays
```

## Research Universe

| Symbol | Display name | Data status |
|---|---|---|
{rows}

## Required Evidence Before Any Directional Conclusion

- Verify price, volume, timestamp, and source agreement.
- Evaluate BOLL only after data-integrity and survival-risk gates pass; require enough completed historical observations.
- Confirm with price-volume behavior and separately labelled 5/10/20-trading-day flows.
- Link company facts to a dated primary disclosure. Delete unverified narratives.
- Treat anything disclosed after `evidence_cutoff` as a new event, not a revision of this report.

## Review Rule

Assess this report only in the validation window above. The executable reference point is the next actual market open, never a prior report-day close.
"""


def main() -> int:
    args = parse_args()
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    watchlist_path = (ROOT / args.watchlist).resolve() if not Path(args.watchlist).is_absolute() else Path(args.watchlist)
    universe = load_watchlist(watchlist_path)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"weekly_quant_research_{as_of:%Y%m%d}.md"
    output.write_text(build_report(as_of, universe, watchlist_path), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
