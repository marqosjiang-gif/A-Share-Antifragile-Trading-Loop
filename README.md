<div align="center">

# A-Share Antifragile Trading Loop

### A weekly evidence loop for disciplined A-share research

Verify the data. Filter the story. Decide with evidence. Learn from the result.

[English](README.md) | [Español](docs/README.es.md) | [简体中文](docs/README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Market: A-shares](https://img.shields.io/badge/Market-A--shares-C81E1E.svg)](#what-this-project-does)
[![Cadence: Weekly](https://img.shields.io/badge/Cadence-Weekly-059669.svg)](#quick-start)
[![Core: Key-free](https://img.shields.io/badge/Core-Key--free-7C3AED.svg)](#configuration)

<img src="assets/readme/hero.png" alt="A-Share Antifragile Trading Loop workflow" width="100%" />

**[What it does](#what-this-project-does) · [Install](#installation) · [Quick start](#quick-start) · [Example](#usage-example) · [Configuration](#configuration) · [FAQ](#faq)**

</div>

> [!IMPORTANT]
> This is an A-share research and decision-support project. It never places orders, and it is not financial advice.

## What This Project Does

**A-Share Antifragile Trading Loop** turns a weekly market review into an auditable research routine. It creates a Markdown strategy report from public market data, then makes the quality of the evidence visible instead of hiding missing, stale, or conflicting inputs.

The core workflow is defined in [`6只持仓股信息筛选SKILL.md`](6只持仓股信息筛选SKILL.md) and implemented by [`Weekly_strategy.py`](skills/市场消息求真去伪skill/Weekly_strategy.py). The root runner, [`run_weekly_report.py`](run_weekly_report.py), starts the workflow and writes `反脆弱周盘策略_YYYYMMDD.md` to the project root.

It is designed for investors who want to separate facts from narratives before making a weekly swing-trading decision:

- Verify price, volume, dates, and source agreement before interpretation.
- Prioritize historical BOLL evidence after hard risk and data-quality gates.
- Distinguish 5-day sector-flow confirmation from 5/10/20-day individual-stock flow.
- Surface earnings dates, announcements, event risks, and fresh geopolitical checks.
- Apply *Via Negativa*: unsupported narratives cannot become trading reasons.
- Record recurring errors in an evolution log so the next report improves without rewriting history.

<img src="assets/readme/research-loop.png" alt="Evidence-led weekly research loop: verified data, risk filters, BOLL evidence, flow confirmation, and learning log" width="100%" />

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/marqosjiang-gif/A-Share-Antifragile-Trading-Loop.git
cd A-Share-Antifragile-Trading-Loop
```

### 2. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

The base workflow needs `pandas`. `yfinance`, `matplotlib`, and `akshare` are optional enhancements for cross-checking, charts, and selected data paths.

## Quick Start

Run the weekly report generator from the repository root:

```bash
python3 run_weekly_report.py
```

The runner first builds a key-free market snapshot with public endpoints. When the full strategy engine is available, it then adds evidence validation, capital-flow radar, historical BOLL analysis, event monitoring, Taleb-style audit, and a next-week decision section.

The result is saved as:

```text
反脆弱周盘策略_YYYYMMDD.md
```

Before using the output for research, replace the sample watchlist with your own A-share codes. Review `WATCH_TICKERS`, `_TICKER_SECID`, and `_TICKER_NAME` in [`run_weekly_report.py`](run_weekly_report.py), then keep the portfolio definitions used by the strategy modules consistent with that list. Do not commit personal portfolio quantities, costs, reports, email addresses, or credentials.

## Usage Example

### Generate a report

```bash
python3 run_weekly_report.py
```

### Validate the Python entry points after a workflow change

```bash
python3 -m py_compile \
  run_weekly_report.py \
  skills/市场消息求真去伪skill/Weekly_strategy.py
```

### Run the focused decision-rule tests

```bash
python3 -m unittest \
  test_boll_decision_priority \
  test_fund_flow_skill_rules \
  test_geopolitical_freshness
```

### Read the generated report correctly

| Report area | Question it answers | Guardrail |
|---|---|---|
| Sector strength + 5-day flow | Is a concept sector rising with capital confirmation? | Price-only momentum stays observation-only. |
| H20 capital-flow radar | Is a stock move short-term or persistent across 5/10/20 trading days? | Unverified flow cannot support a directional claim. |
| Historical BOLL | Does the current location match a tested weekly/monthly strategy? | BOLL has the highest decision weight after hard gates pass. |
| Event and earnings monitor | Is there a near-term disclosure or material event? | Incomplete scans are labeled, not silently treated as clear. |
| Evolution log | What failed or drifted last week? | Only recurring, decision-relevant rules are promoted. |

## Configuration

[`config.yaml`](config.yaml) documents optional integrations. The default path uses public, key-free market endpoints; unavailable optional services should degrade visibly rather than stop the report.

| Setting | Purpose | Required |
|---|---|---|
| `TA_VENV`, `TA_RUN_WEBUI_TOOLS`, `TA_CWD` | Optional TradingAgents market snapshot | No |
| `WESTOCK_CLI`, `YAHOO_FINANCE_SKILL`, `TA_PYTHON` | Optional cross-source validation paths | No |
| `JIAOZHEN_API_KEY` | Optional third-source geopolitical fact check | No |
| `BOLL_BACKTEST_SCRIPT`, `PYTHON_ENV` | Historical BOLL backtest integration | No |
| `NEODATA_QUERY_SCRIPT`, `NEODATA_SKILL_DIR` | Optional financial-search fallback | No |
| `ASTOCK_TDX_CACHE` | Optional local TDX cache | No |

Example of enabling a local BOLL backtest:

```bash
export BOLL_BACKTEST_SCRIPT="/absolute/path/to/boll_backtest.py"
export PYTHON_ENV="/absolute/path/to/python"
python3 run_weekly_report.py
```

The weekly report uses explicit time windows:

- Weekly price movement: first actual A-share market open to Friday close.
- Sector capital confirmation: cumulative five trading days.
- Individual-stock H20 radar: 5, 10, and 20 trading days, each labeled separately.
- Event monitoring: recent and forward-looking windows are printed in the report.

## FAQ

### Does it trade automatically or send orders to a broker?

No. It only generates research output and risk-aware action suggestions.

### Do I need an API key?

No for the basic report path. Optional integrations may need local tools, environment variables, or credentials. Leave unavailable integrations blank; the report should state any resulting degradation.

### Why does the report show a warning instead of a conclusion?

That is deliberate. A missing source, stale event, price disagreement, incomplete scan, or unverified capital-flow reading must not be converted into a confident trading narrative.

### How should I change the watchlist?

Update the stock code, exchange mapping, and display name maps in [`run_weekly_report.py`](run_weekly_report.py). Keep related strategy-module portfolio definitions aligned. Use only your own local configuration and keep personal position information outside Git.

### What should be committed to a public fork?

Source code, generic configuration templates, tests, documentation, and non-sensitive visual assets. Do not commit generated reports, local caches, portfolio quantities or costs, personal email addresses, API keys, tokens, or local absolute paths.

## License

Released under the [MIT License](LICENSE).

## Disclaimer

This repository is for education and quantitative research only. Market data can be delayed, incomplete, or unavailable. No signal, backtest, or report guarantees future performance. You are responsible for your own investment decisions.
