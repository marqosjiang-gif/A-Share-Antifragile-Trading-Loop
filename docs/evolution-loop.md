# Autonomous evolution loop

This project treats improvement as a controlled weekly loop, not as unrestricted self-modification.

## W1 → W2 → W3

```mermaid
flowchart LR
    W1["W1 Generate\ncreate report with cutoff"] --> W2["W2 Review\ncompare forecast, evidence and actual path"]
    W2 --> T{"Recurring and decision-relevant?"}
    T -- "No" --> K["Keep as local note\nno rule promotion"]
    T -- "Yes" --> H["Human / policy gate\nreview proposed change"]
    H --> W3["W3 Evolve\npromote tested rule or prompt"]
    W3 --> W1
```

## Promotion rules

1. Use only information that was available by the original report's `evidence_cutoff` when judging the report.
2. Classify the difference as `judgment_error`, `information_omission`, `post_report_event`, or `data_or_execution_error`.
3. Promote only a recurring, decision-relevant rule that improves auditability or execution safety.
4. Keep one-off market opinions, private portfolio details and generated reports local.
5. Require a human or explicit policy gate before a rule changes the public behavior.

## What “autonomous” means here

The loop can detect repeated failure modes, propose a rule change, update a local experiment, and run tests. It cannot place orders, change a brokerage account, or silently publish private data. Autonomy is bounded by evidence, reproducibility and reversible promotion.

## Minimal review record

```yaml
report_id: weekly-YYYYMMDD
evidence_cutoff: YYYY-MM-DDTHH:MM:SS+TZ
classification: data_or_execution_error
observed_gap: "source timestamp was missing"
proposed_rule: "block directional output when timestamp is absent"
status: proposed
```
