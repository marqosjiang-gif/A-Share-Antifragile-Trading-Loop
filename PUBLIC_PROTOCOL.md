# Public Research Protocol

## Scope

This repository supports medium-low frequency research through market adapters.
The included examples are venue-neutral; an A-share adapter may be added locally,
but its rules must not be treated as universal. The public core does not execute
orders or manage brokerage accounts.

The public runner is deliberately data-provider-neutral. Provider clients,
credentials, private watchlists, and account-aware logic belong in local ignored
adapters rather than in the reference implementation.

## Market adapter boundary

Every venue-specific adapter must declare its own exchange calendar, settlement
cycle, price-limit behavior, short-selling rules, corporate-action treatment,
currency, liquidity assumptions, and data-source constraints. For example,
T+1 settlement, daily price limits, or a local holiday calendar must never be
silently copied into another market profile.

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

Decision-affecting changes pass through a W2.5 human/policy gate before W3
promotion. This includes signal priority, thresholds, agent roles, prompts, data
sources, fallback chains, and market-adapter rules. Presentation-only changes
may be promoted automatically when a review record is retained.

## Evolution safety

- Keep missing, stale, failed, or conflicting sources visible; do not turn them into a directional conclusion.
- Limit prompt edits to a scored add/replace/delete proposal with before/after review.
- Run structure and forbidden-wording checks after rendering, not only before generation.
- Record the previous rule, new rule, evidence, approval status, test result, and rollback path.
- Treat promotion as reversible; a failed post-promotion check returns the rule to its prior version.

## Privacy

Never commit a personal watchlist, position quantity, cost basis, account information, email address, API key, token, local absolute path, cached market data, generated report, or transaction record.
