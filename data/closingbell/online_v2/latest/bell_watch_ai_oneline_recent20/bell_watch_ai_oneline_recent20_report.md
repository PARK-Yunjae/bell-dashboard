# Bell Watch AI One-line Recent20 Test - 2026-05-27

## Summary

- generated_at: 2026-05-27T23:20:21
- ai_engine: CODEX_RULED_ONELINE_V0
- target: recent 20 signal dates Top3
- signal_date_range: 2026-04-27 ~ 2026-05-27
- candidate_rows: 60
- h5_evaluable_rows: 45
- operation_touched: false
- webhook_send: false
- scheduler_changed: false
- order_or_account_api: false

## Important Scope Note

This is a research-only, local ruled one-line test. It does not call an external LLM/API and does not change ranking, webhook, scheduler, order, or account paths.
The outputs are useful for checking the dashboard/data contract and for a small manual-review proxy test, not for operating a new model.

## Grade Summary

| grade | rows | h5 rows | +1.3 before -2 | -2 before +1.3 | avg H5 close | expected-path hit |
|---|---:|---:|---:|---:|---:|---:|
| A | 19 | 16 | 50.0% | 25.0% | +8.32% | 50.0% |
| B | 8 | 6 | 33.3% | 16.7% | -4.34% | 66.7% |
| C | 6 | 6 | 0.0% | 66.7% | -1.27% | 66.7% |
| D | 27 | 17 | 11.8% | 35.3% | -4.10% | 76.5% |

## Expected Path Summary

| path | rows | h5 rows | +1.3 before -2 | -2 before +1.3 | -2 touch |
|---|---:|---:|---:|---:|---:|
| MINUS_FIRST | 9 | 7 | 14.3% | 28.6% | 100.0% |
| NO_TRADE | 20 | 12 | 8.3% | 41.7% | 100.0% |
| PLUS_FIRST | 22 | 18 | 44.4% | 27.8% | 61.1% |
| VOLATILE | 9 | 8 | 25.0% | 37.5% | 100.0% |

## Interpretation

- Recent rows include dates newer than the H5 label horizon, so H5 evaluation is partial.
- Same-day D+5 high/low ambiguity remains a daily-data limitation and is preserved in the output columns.
- Use these files as a small learning memo layer. Keep the baseline EOD Top3 operating logic unchanged.
