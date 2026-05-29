# Bell V3 Aligned Operational QA Report - 2026-05-29

## Verdict

- source_freshness: PASS
- operational_switch_allowed_now: YES
- active_variant: V3_C_RISK_CONTROL
- fallback_route: EOD_D0_BASE_VALUE_TOP3__WATCH10D__D0_VALUE_DESC

## Source Freshness

| source_name   | date_max   |   latest_date_rows | status   | note   |
|:--------------|:-----------|-------------------:|:---------|:-------|
| EOD           | 2026-05-29 |                  3 | OK       |        |
| V2            | 2026-05-29 |                  3 | OK       |        |
| Human         | 2026-05-29 |                  3 | OK       |        |
| V3            | 2026-05-29 |                  3 | OK       |        |

## Summary

| strategy_key      |   rows |   complete_d5_rows | date_min   | date_max   |   h5_plus1_touch_rate_pct |   h5_plus2_touch_rate_pct |   h5_plus3_touch_rate_pct |   h5_minus1_touch_rate_pct |   h5_minus2_touch_rate_pct |   h5_minus3_touch_rate_pct |   avg_ret_d5_close_pct |   median_ret_d5_close_pct |
|:------------------|-------:|-------------------:|:-----------|:-----------|--------------------------:|--------------------------:|--------------------------:|---------------------------:|---------------------------:|---------------------------:|-----------------------:|--------------------------:|
| V3_C_RISK_CONTROL |    846 |                831 | 2025-04-02 | 2026-05-29 |                   90.1324 |                   85.1986 |                   79.7834 |                    85.5596 |                    78.7004 |                    72.3225 |                1.94099 |                 -0.679117 |
| V3_D_V2_CONFIRM   |    846 |                831 | 2025-04-02 | 2026-05-29 |                   89.7714 |                   84.4765 |                   78.941  |                    87.846  |                    81.1071 |                    75.0903 |                1.39992 |                 -0.921332 |

## Integrity

| check_name           | status   | evidence         |
|:---------------------|:---------|:-----------------|
| common_latest_exists | PASS     | latest_rows=58   |
| eod_top3_each_day    | PASS     | bad_days=0       |
| v2_top3_each_day     | PASS     | bad_days=0       |
| human_top3_each_day  | PASS     | bad_days=0       |
| v3_top3_each_day     | PASS     | bad_days=0       |
| v3_latest_top3       | PASS     | latest_v3_rows=3 |

## Guard

- No order/account API touched.
- No Discord send executed by this builder.
- Scheduler not changed by this builder.
- If a later guarded webhook run sees source_freshness != PASS, it must use EOD fallback.
