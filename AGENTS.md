# AGENTS.md

## Purpose

Maintain the public A-share research core without introducing personal portfolio data or unsupported market claims.

## Non-negotiable rules

- Use runtime data, never silent mock prices, volumes, funds, or events.
- Mark unavailable, stale, incomplete, or conflicting inputs explicitly.
- Keep price/volume validation ahead of technical interpretation.
- Give historical BOLL the highest technical weight only after hard data and survival-risk gates pass; require at least three completed historical trades.
- Keep sector 5-day flow separate from stock 5/10/20-day flow.
- Do not turn broad policy, macro headlines, or unverified news into direct trade conclusions.
- Preserve the 168-hour event freshness rule unless a report labels an item as historical background.
- Do not place orders or send email from the public core.

## Privacy and publication

- Never commit account data, position size, purchase cost, portfolio history, report output, email addresses, API keys, tokens, local paths, caches, or WorkBuddy/automation state.
- Keep credentials in environment variables or ignored local files only.
- Before publishing, run a sensitive-data scan, review the staged file list, and stage explicit paths rather than `git add -A`.

## Verification

```bash
python3 -m py_compile run_weekly_report.py antifragile/*.py
python3 -m unittest test_public_snapshot -v
git diff --check
```

Public behavior and the full research protocol are documented in `A股反脆弱策略SKILL.md` and `docs/RESEARCH_PROTOCOL.md`.
