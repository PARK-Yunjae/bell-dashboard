# Bell V3 Hybrid Consensus Research Report - 2026-05-28

## Summary

- generated_at: 2026-05-28T19:52:25
- operation_touched: false
- webhook_send: false
- scheduler_changed: false
- order_or_account_api: false
- active_route_changed: false
- display_scope: read-only research parallel view
- candidate_pool_rows: 3888
- score_rows: 23328
- selected_rows: 5076
- latest_signal_date: 2026-05-28
- top3_bad_group_count: 0

V3 Consensus는 연구용 종합 후보입니다. 현재 운영 웹훅 선정식에는 아직 반영되지 않았습니다.

## Latest V3 Top3

| variant | rank | code | name | score | sources | eval_source | data_quality |
|---|---:|---|---|---:|---|---|---|
| V3_A_CONSENSUS_WEIGHTED | 1 | 001740 | SK네트웍스 | 40.87 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_A_CONSENSUS_WEIGHTED | 2 | 080220 | 제주반도체 | 36.97 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_A_CONSENSUS_WEIGHTED | 3 | 010170 | 대한광통신 | 33.82 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_B_WINRATE_ORIENTED | 1 | 001740 | SK네트웍스 | 39.90 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_B_WINRATE_ORIENTED | 2 | 080220 | 제주반도체 | 37.30 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_B_WINRATE_ORIENTED | 3 | 010170 | 대한광통신 | 35.20 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_C_RISK_CONTROL | 1 | 001740 | SK네트웍스 | 51.37 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_C_RISK_CONTROL | 2 | 080220 | 제주반도체 | 43.22 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_C_RISK_CONTROL | 3 | 010170 | 대한광통신 | 42.27 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_D_V2_CONFIRM | 1 | 001740 | SK네트웍스 | 42.37 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_D_V2_CONFIRM | 2 | 080220 | 제주반도체 | 37.84 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_D_V2_CONFIRM | 3 | 010170 | 대한광통신 | 36.14 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_E_EOD_FIRST_STABLE | 1 | 001740 | SK네트웍스 | 54.37 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_E_EOD_FIRST_STABLE | 2 | 080220 | 제주반도체 | 51.47 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_E_EOD_FIRST_STABLE | 3 | 010170 | 대한광통신 | 47.82 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_F_V2_AGGRESSIVE | 1 | 001740 | SK네트웍스 | 36.10 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_F_V2_AGGRESSIVE | 2 | 080220 | 제주반도체 | 34.60 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |
| V3_F_V2_AGGRESSIVE | 3 | 010170 | 대한광통신 | 31.55 | eod_active | EOD_ACTIVE_WATCH_LATEST_TOP3 | MISSING_FUTURE |

## Overall Performance

| variant | rows | D5 rows | days | D5 avg | D5 median | D5 win | D+1 day +1.3 | D+5 day +1.3 | D1-D5 cum +1.3 | +1.3 before -2 | -2 before +1.3 | ambiguous | sample |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| V3_D_V2_CONFIRM | 846 | 831 | 282 | 5.35% | 1.35% | 58.00% | 69.63% | 63.90% | 89.65% | 58.48% | 22.86% | 18.53% | OK |
| V3_C_RISK_CONTROL | 846 | 831 | 282 | 5.06% | 1.65% | 58.97% | 71.53% | 64.62% | 91.10% | 57.52% | 21.66% | 20.70% | OK |
| V3_F_V2_AGGRESSIVE | 846 | 831 | 282 | 5.35% | 1.38% | 58.36% | 69.99% | 63.42% | 89.65% | 57.28% | 22.14% | 20.46% | OK |
| V3_B_WINRATE_ORIENTED | 846 | 831 | 282 | 5.04% | 1.35% | 58.12% | 69.75% | 63.54% | 90.13% | 55.48% | 23.23% | 21.18% | OK |
| V3_A_CONSENSUS_WEIGHTED | 846 | 831 | 282 | 4.80% | 1.49% | 58.24% | 69.75% | 63.30% | 90.49% | 55.23% | 23.10% | 21.54% | OK |
| V3_E_EOD_FIRST_STABLE | 846 | 831 | 282 | 3.13% | 1.02% | 54.63% | 70.46% | 60.77% | 89.53% | 50.18% | 23.47% | 26.23% | OK |

## Latest Rolling

| variant | window | as_of | D5 rows | D5 win | +1.3 before -2 | sample | partial |
|---|---|---|---:|---:|---:|---|---|
| V3_A_CONSENSUS_WEIGHTED | ROLLING_120TD | 2026-05-28 | 345 | 62.61% | 48.70% | OK | False |
| V3_B_WINRATE_ORIENTED | ROLLING_120TD | 2026-05-28 | 345 | 61.74% | 50.43% | OK | False |
| V3_C_RISK_CONTROL | ROLLING_120TD | 2026-05-28 | 345 | 61.74% | 51.88% | OK | False |
| V3_D_V2_CONFIRM | ROLLING_120TD | 2026-05-28 | 345 | 63.19% | 53.91% | OK | False |
| V3_E_EOD_FIRST_STABLE | ROLLING_120TD | 2026-05-28 | 345 | 55.65% | 42.90% | OK | False |
| V3_F_V2_AGGRESSIVE | ROLLING_120TD | 2026-05-28 | 345 | 61.74% | 53.62% | OK | False |
| V3_A_CONSENSUS_WEIGHTED | ROLLING_20TD | 2026-05-28 | 45 | 44.44% | 46.67% | LOW_SAMPLE | False |
| V3_B_WINRATE_ORIENTED | ROLLING_20TD | 2026-05-28 | 45 | 44.44% | 46.67% | LOW_SAMPLE | False |
| V3_C_RISK_CONTROL | ROLLING_20TD | 2026-05-28 | 45 | 48.89% | 48.89% | LOW_SAMPLE | False |
| V3_D_V2_CONFIRM | ROLLING_20TD | 2026-05-28 | 45 | 51.11% | 44.44% | LOW_SAMPLE | False |
| V3_E_EOD_FIRST_STABLE | ROLLING_20TD | 2026-05-28 | 45 | 35.56% | 35.56% | LOW_SAMPLE | False |
| V3_F_V2_AGGRESSIVE | ROLLING_20TD | 2026-05-28 | 45 | 46.67% | 46.67% | LOW_SAMPLE | False |
| V3_A_CONSENSUS_WEIGHTED | ROLLING_60TD | 2026-05-28 | 165 | 55.76% | 42.42% | OK | False |
| V3_B_WINRATE_ORIENTED | ROLLING_60TD | 2026-05-28 | 165 | 55.15% | 45.45% | OK | False |
| V3_C_RISK_CONTROL | ROLLING_60TD | 2026-05-28 | 165 | 56.36% | 47.27% | OK | False |
| V3_D_V2_CONFIRM | ROLLING_60TD | 2026-05-28 | 165 | 57.58% | 49.70% | OK | False |
| V3_E_EOD_FIRST_STABLE | ROLLING_60TD | 2026-05-28 | 165 | 47.27% | 35.15% | OK | False |
| V3_F_V2_AGGRESSIVE | ROLLING_60TD | 2026-05-28 | 165 | 55.15% | 49.09% | OK | False |

## Daily Success Count

| variant | metric | complete days | avg count | zero day | two+ day | three day |
|---|---|---:|---:|---:|---:|---:|
| V3_A_CONSENSUS_WEIGHTED | plus13_before_minus2_success_count | 277 | 1.66 | 16.97% | 59.57% | 23.10% |
| V3_A_CONSENSUS_WEIGHTED | plus13_touch_count | 277 | 2.71 | 0.72% | 96.39% | 75.81% |
| V3_B_WINRATE_ORIENTED | plus13_before_minus2_success_count | 277 | 1.66 | 16.97% | 59.93% | 23.47% |
| V3_B_WINRATE_ORIENTED | plus13_touch_count | 277 | 2.70 | 0.72% | 96.39% | 74.73% |
| V3_C_RISK_CONTROL | plus13_before_minus2_success_count | 277 | 1.73 | 15.16% | 61.37% | 26.35% |
| V3_C_RISK_CONTROL | plus13_touch_count | 277 | 2.73 | 1.44% | 96.39% | 78.34% |
| V3_D_V2_CONFIRM | plus13_before_minus2_success_count | 277 | 1.75 | 15.16% | 64.26% | 26.35% |
| V3_D_V2_CONFIRM | plus13_touch_count | 277 | 2.69 | 0.72% | 94.22% | 75.45% |
| V3_E_EOD_FIRST_STABLE | plus13_before_minus2_success_count | 277 | 1.51 | 20.58% | 49.10% | 22.02% |
| V3_E_EOD_FIRST_STABLE | plus13_touch_count | 277 | 2.69 | 1.08% | 96.03% | 73.65% |
| V3_F_V2_AGGRESSIVE | plus13_before_minus2_success_count | 277 | 1.72 | 14.80% | 62.82% | 23.83% |
| V3_F_V2_AGGRESSIVE | plus13_touch_count | 277 | 2.69 | 0.72% | 95.31% | 74.37% |

## Outlier Audit

| variant | rows | mean | median | gap | max winner | worst | loss rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| V3_A_CONSENSUS_WEIGHTED | 831 | 4.80% | 1.49% | 3.31pp | 614.67% | -34.66% | 40.55% |
| V3_B_WINRATE_ORIENTED | 831 | 5.04% | 1.35% | 3.69pp | 645.94% | -34.59% | 40.79% |
| V3_C_RISK_CONTROL | 831 | 5.06% | 1.65% | 3.41pp | 614.67% | -34.66% | 40.07% |
| V3_D_V2_CONFIRM | 831 | 5.35% | 1.35% | 4.00pp | 645.94% | -28.21% | 41.03% |
| V3_E_EOD_FIRST_STABLE | 831 | 3.13% | 1.02% | 2.11pp | 508.75% | -34.66% | 44.16% |
| V3_F_V2_AGGRESSIVE | 831 | 5.35% | 1.38% | 3.97pp | 645.94% | -28.21% | 40.55% |

## Validation

- variants: 6
- candidate_days: 282
- top3_group_count: 1692
- top3_bad_group_count: 0
- selection_uses_outcome_columns: false
- D+ outcome columns are retained only after selection for evaluation.
- latest pending rows are displayed but excluded from complete D+5 denominators.

## Output Interpretation

- `bell_v3_consensus_score_detail.csv` is the main score audit table.
- `bell_v3_consensus_selected_top3.csv` is the dashboard-facing selected table.
- `bell_v3_vs_legacy_strategy_compare.csv` lets ChatGPT compare V3 variants with EOD/V2/BellGuard/Daily3 baselines.
- This report is research-only and does not change the operating EOD webhook route.
