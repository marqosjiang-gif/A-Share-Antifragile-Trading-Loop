# Research Protocol

## Evidence before narrative

The public project accepts a conclusion only when its inputs state their source and time window. A failed source is a result, not an invitation to fabricate a replacement.

| Evidence | Required window | Allowed role |
|---|---|---|
| Weekly price movement | First represented market open to Friday close | Market context and price confirmation |
| Sector flow | Five trading days | Confirmation only; never replace with a single-day figure |
| Stock flow | 5, 10, and 20 trading days | Short, medium, and long-horizon context |
| Company events | Freshness threshold shown in the report | Constraint or catalyst only after verification |
| Historical BOLL | At least three completed historical trades | Highest technical decision weight after hard gates |
| DXY and commodities | Explicit weekly dates and source | Context or risk constraint only |
| Earnings calendar | Next 7 and 30 calendar days | Forward disclosure risk; never infer a missing date |

## Via Negativa

Remove a claim when it is unsupported, stale, materially ambiguous, or cannot be linked to the configured symbol. A popular headline, a policy slogan, or a single price move is not sufficient evidence for a directional action.

## Consistency gates

- A BOLL position above 100% is an active upper-band sell region; below 0% is an active lower-band buy region.
- A "no material event" statement is valid only after every configured scan dimension completes.
- Sector five-day flow and stock 5/10/20-day flow are separate datasets and must show exact dates.
- Stock-flow interpretation uses liquidity-aware thresholds rather than one absolute number for the whole market.
- DXY, oil, metals, policy, and geopolitical context cannot create a standalone stock action.

## Evolution loop

Each review compares a prior rule with an observed result. Keep an evolution note local by default. Promote a rule only when it recurs across weeks, changes a real decision, and can be expressed without personal account data.

## Public/private boundary

The public repository contains generic research logic. Personal symbols may be supplied at runtime with `WATCH_TICKERS`; holdings, costs, quantities, generated reports, local automation state, provider tokens, and proprietary data remain local and are ignored by Git.
