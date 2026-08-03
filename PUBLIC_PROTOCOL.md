# Public Research Protocol

## Scope

This repository supports medium-low frequency A-share research. It does not execute orders or manage brokerage accounts.

## Evidence and timing

- Record `report_generated_at` and `evidence_cutoff` in every report.
- Use only information public and reasonably obtainable before `evidence_cutoff` to assess that report.
- Treat disclosures after the cutoff as `post_report_event`, never as retroactive evidence of an earlier mistake.
- Validate a weekend report from the next actual trading open to the final actual close of that trading week. Use one adjusted-price series for return and drawdown.
- Compute a weekly move as `(last actual close / first actual open - 1) * 100`.

## Decision hierarchy

1. Data integrity and survival-risk gates
2. Historical BOLL evidence with sufficient completed observations
3. Price-volume confirmation
4. Individual 5/10/20-trading-day capital flow
5. Company disclosures and fundamentals
6. Verified macro or geopolitical context

A lower layer cannot manufacture a directional conclusion when a higher gate fails. An incomplete scan, stale data, source conflict, or low-sample backtest must be visible in the output.

## Review loop

Classify each observed difference as exactly one of: `judgment_error`, `information_omission`, `post_report_event`, or `data_or_execution_error`. Promote only recurring, decision-relevant, automation-stability rules. Keep weekly opinions and generated reports local.

## Privacy

Never commit a personal watchlist, position quantity, cost basis, account information, email address, API key, token, local absolute path, cached market data, generated report, or transaction record.
