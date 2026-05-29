# Bell V3 Promotion Deep Dive - 2026-05-28

## Scope

- 목적: V3_D/V3_C를 대시보드 핵심 후보와 향후 웹훅 전환 후보로 더 파고들기
- 운영 변경: 없음
- 주문/계좌 API 변경: 없음
- 핵심 결론: V3_D/V3_C 성과는 유망하지만 V2/Human 최신 source stale 문제가 있어 운영 전환은 아직 보류

## Promotion Gates

| gate | status | evidence | impact |
|---|---|---|---|
| top3_fixed | PASS | top3_bad_group_count=0 | 필수 |
| core_source_freshness | FAIL | V2 Hybrid max=2026-05-14 vs EOD=2026-05-28; Human Proxy max=2026-05-19 vs EOD=2026-05-28 | 운영 전환 전 해결 필요 |
| V3_D_V2_CONFIRM_latest20_fallback_rate | FAIL | latest20 all_eod_only_day_rate=30.00% | fallback 비율이 높으면 진짜 V3가 아님 |
| V3_C_RISK_CONTROL_latest20_fallback_rate | FAIL | latest20 all_eod_only_day_rate=30.00% | fallback 비율이 높으면 진짜 V3가 아님 |
| V3_D_V2_CONFIRM_latest60_common_performance | OBSERVE | first=49.44 vs EOD 31.67; minus2first=25.56 vs EOD 25.00; median=0.95 vs EOD -2.17 | 성과 기준 |
| V3_C_RISK_CONTROL_latest60_common_performance | PASS | first=47.78 vs EOD 31.67; minus2first=23.89 vs EOD 25.00; median=0.62 vs EOD -2.17 | 성과 기준 |

## Core Comparison

| strategy | D+1 +1.3 | D+1 -1 | D+1 -2 | D+1 -3 | D1-D5 +1 | D1-D5 +2 | D1-D5 +3 | +1.3 first | -2 first | D5 avg | D5 median | D5 win |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V3-D V2 확인 | 69.63% | 54.33% | 38.20% | 25.50% | 91.46% | 83.75% | 73.65% | 58.48% | 22.86% | 5.35% | 1.35% | 58.00% |
| V3-C 리스크 | 71.53% | 54.57% | 39.15% | 26.81% | 92.42% | 86.40% | 77.14% | 57.52% | 21.66% | 5.06% | 1.65% | 58.97% |
| 현재 EOD웹훅 Top3 | 72.74% | 64.05% | 51.55% | 39.05% | 90.70% | 84.42% | 77.66% | 46.14% | 22.22% | 1.79% | 0.41% | 51.21% |
| EOD Top1 | 64.73% | 51.64% | 41.45% | 29.82% | 90.91% | 79.64% | 71.64% | 52.73% | 24.73% | 3.24% | 1.69% | 59.27% |
| EOD Top3 | 72.36% | 64.12% | 51.39% | 38.79% | 90.67% | 84.36% | 77.58% | 45.94% | 22.30% | 1.80% | 0.38% | 51.15% |
| V2 하이브리드 | 67.19% | 56.13% | 37.68% | 25.30% | 90.65% | 82.48% | 71.67% | 57.71% | 25.96% | 9.54% | 1.11% | 55.99% |

## Source Freshness

| source | max date | latest rows | status | stale days |
|---|---|---:|---|---:|
| EOD Active | 2026-05-28 | 3 | OK | 0 |
| V2 Hybrid | 2026-05-14 | 0 | STALE_OR_MISSING | 14 |
| Human Proxy | 2026-05-19 | 0 | STALE_OR_MISSING | 9 |
| Daily3 | 2026-05-19 | 0 | STALE_OR_MISSING | 9 |
| P0 | 2026-05-13 | 0 | STALE_OR_MISSING | 15 |

## Latest 20 Source Composition

| variant | all EOD-only day | any V2 day | any Human day | avg EOD count | avg V2 count | avg Human count |
|---|---:|---:|---:|---:|---:|---:|
| V3_C_RISK_CONTROL | 30.00% | 55.00% | 35.00% | 1.50 | 1.10 | 0.35 |
| V3_D_V2_CONFIRM | 30.00% | 55.00% | 20.00% | 1.15 | 1.55 | 0.20 |

## EOD/V3 Overlap Metrics

| bucket | rows | +1.3 first | -2 first | D5 median | D5 win |
|---|---:|---:|---:|---:|---:|
| V3_D_V2_CONFIRM ∩ EOD | 276 | 53.64% | 22.99% | 1.85% | 59.77% |
| V3_D_V2_CONFIRM only | 570 | 60.70% | 22.81% | 1.19% | 57.19% |
| V3_C_RISK_CONTROL ∩ EOD | 421 | 53.69% | 22.66% | 1.83% | 59.36% |
| V3_C_RISK_CONTROL only | 425 | 61.18% | 20.71% | 1.32% | 58.59% |

## Score Buckets

점수 자체는 쓸모가 있지만, 최신 source stale 상태에서는 운영 승격 근거로 쓰면 안 됩니다. 아래 bucket은 V3_D/V3_C 내부에서 score가 높을수록 실제 결과도 좋아지는지 보는 용도입니다.

| variant | score bucket | rows | +1.3 first | -2 first | D5 median |
|---|---|---:|---:|---:|---:|
| V3_D_V2_CONFIRM | (21.410999999999998, 60.52] | 167 | 35.33% | 40.12% | -2.00% |
| V3_D_V2_CONFIRM | (60.52, 62.621] | 166 | 66.27% | 12.65% | 2.27% |
| V3_D_V2_CONFIRM | (62.621, 65.322] | 166 | 68.67% | 18.67% | 2.06% |
| V3_D_V2_CONFIRM | (65.322, 68.629] | 166 | 50.60% | 28.92% | 0.59% |
| V3_D_V2_CONFIRM | (68.629, 96.838] | 166 | 71.69% | 13.86% | 3.05% |
| V3_C_RISK_CONTROL | (19.448999999999998, 55.495] | 167 | 43.71% | 27.54% | -0.73% |
| V3_C_RISK_CONTROL | (55.495, 57.603] | 166 | 57.23% | 25.30% | 2.56% |
| V3_C_RISK_CONTROL | (57.603, 60.516] | 166 | 60.84% | 17.47% | 1.07% |
| V3_C_RISK_CONTROL | (60.516, 66.267] | 166 | 71.08% | 12.65% | 3.59% |
| V3_C_RISK_CONTROL | (66.267, 82.312] | 166 | 54.82% | 25.30% | 1.92% |

## Files

- summary_compact: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_promotion_summary_compact.csv`
- threshold_matrix: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_promotion_d1_d5_threshold_matrix.csv`
- individual_day_plus13: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_promotion_individual_day_plus13.csv`
- source_freshness: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_source_freshness.csv`
- source_composition_by_date: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_source_composition_by_date.csv`
- latest20_source_composition: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_latest20_source_composition.csv`
- eod_overlap_daily: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_eod_overlap_daily.csv`
- eod_overlap_strategy_metrics: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_eod_overlap_strategy_metrics.csv`
- score_bucket_analysis: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_score_bucket_analysis.csv`
- common20_compare: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_common20_compare.csv`
- common60_compare: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_common60_compare.csv`
- common120_compare: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_common120_compare.csv`
- promotion_readiness_gates: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\csv\bell_v3_promotion_readiness_gates.csv`
- report: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\reports\bell_v3_promotion_deep_dive_report.md`
- manifest: `C:\Coding\data\closingbell\research_index\bell_v3_promotion_deep_dive_20260528\manifest.json`

## Recommendation

1. 대시보드는 V3_D와 V3_C 중심으로 더 정리해도 됩니다.
2. 웹훅은 아직 EOD 운영 유지가 맞습니다.
3. 웹훅에 V3를 넣는다면 먼저 `[연구] V3 Consensus` 섹션으로 병렬 표시만 해야 합니다.
4. V2/Human source가 매일 최신일까지 갱신되고 fallback 비율이 낮아진 뒤에 active route 전환을 검토해야 합니다.
