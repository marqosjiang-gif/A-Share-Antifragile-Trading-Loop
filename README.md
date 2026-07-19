<div align="center">

# A-Share Antifragile Trading Loop

### A privacy-first weekly market snapshot for China A-share research

Verify the data. Remove unsupported stories. Make the next decision auditable.

[English](README.md) | [Español](docs/README.es.md) | [简体中文](docs/README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Market: A-shares](https://img.shields.io/badge/Market-A--shares-C81E1E.svg)](#what-it-produces)
[![Core: key-free](https://img.shields.io/badge/Core-Key--free-059669.svg)](#quick-start)
[![Privacy: no defaults](https://img.shields.io/badge/Privacy-No_personal_defaults-0A0B0D.svg)](#privacy-by-design)

<img src="assets/readme/hero.png" alt="A-Share Antifragile Trading Loop workflow" width="100%" />

</div>

> [!IMPORTANT]
> This project is for education and quantitative research. It does not place orders or provide financial advice.

## Why it exists

Weekly reviews often mix fresh prices, stale headlines, and personal conviction. This project starts with a smaller, safer loop:

1. Fetch runtime market data.
2. Make the time window explicit.
3. Show missing data instead of inventing a fallback.
4. Apply antifragile research guardrails.
5. Produce a Markdown snapshot that can be reviewed and extended.

## Core capabilities

| Capability | Behavior |
|---|---|
| A-share market context | SSE Composite, SZSE Component, and STAR 50 snapshots |
| Global context | SPY, QQQ, and VIX reference snapshot |
| Configurable watchlist | Reads stock symbols only from WATCH_TICKERS |
| Weekly return window | Uses the first open and last close of the latest represented trading week |
| Explicit degradation | Marks unavailable sources without simulated prices |
| Portable output | Produces one local Markdown report |

## Privacy by design

- The repository contains no default stock watchlist.
- It does not require position size, purchase cost, account, or email data.
- Local environment files, portfolio files, reports, charts, logs, and exports are ignored by Git.
- Generated research stays local unless the user deliberately publishes it.

## Quick start

~~~bash
git clone https://github.com/marqosjiang-gif/A-Share-Antifragile-Trading-Loop.git
cd A-Share-Antifragile-Trading-Loop

python3 -m venv .venv
source .venv/bin/activate
python3 run_weekly_report.py
~~~

With no watchlist configured, the report contains index context only.

To research your own symbols:

~~~bash
export WATCH_TICKERS="<six-digit-symbol>.SS,<six-digit-symbol>.SZ"
python3 run_weekly_report.py
~~~

Shanghai symbols use .SS; Shenzhen symbols use .SZ.

## What it produces

~~~text
antifragile_weekly_YYYYMMDD.md
~~~

The report contains China A-share index context, US-market reference context, optional watchlist weekly moves, data-availability labels, and antifragile research guardrails.

## How it works

~~~mermaid
flowchart TD
    A["Optional WATCH_TICKERS"] --> B["Public runtime market endpoints"]
    B --> C["Validate symbol and time window"]
    C --> D{"Data available?"}
    D -- No --> E["Mark unavailable"]
    D -- Yes --> F["Calculate first-open to last-close move"]
    E --> G["Markdown snapshot"]
    F --> G
    G --> H["Review, remove unsupported narratives, decide"]
~~~

## Configuration

| Variable | Purpose | Required |
|---|---|---|
| WATCH_TICKERS | Comma-separated A-share symbols | No |
| TA_VENV | Optional TradingAgents Python path | No |
| TA_RUN_WEBUI_TOOLS | Optional TradingAgents adapter | No |
| TA_CWD | Optional TradingAgents working directory | No |

The public core uses only the Python standard library.

## Project structure

~~~text
.
├── run_weekly_report.py
├── test_public_snapshot.py
├── config.yaml
├── requirements.txt
├── DESIGN.md
├── assets/readme/
└── docs/
~~~

## Verification

~~~bash
python3 -m py_compile run_weekly_report.py
python3 -m unittest test_public_snapshot -v
~~~

## Extending the loop

Keep advanced strategy modules separate from personal data. A safe extension may add BOLL research, capital-flow confirmation, event verification, or decision logs, but should accept symbols through configuration and preserve explicit source/time labels.

## Contributing

Issues and pull requests are welcome. Do not commit credentials, personal financial data, generated reports, or proprietary source material.

## License

Released under the [MIT License](LICENSE).

## Disclaimer

Market data can be delayed, incomplete, or unavailable. This repository does not guarantee signal accuracy, trading performance, or future returns. Every user remains responsible for their own research and decisions.
