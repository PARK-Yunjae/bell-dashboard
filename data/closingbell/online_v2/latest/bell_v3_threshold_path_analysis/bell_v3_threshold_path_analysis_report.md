# Bell V3 Threshold Path Analysis - 2026-05-28

목적: +1.3/+2/+3/-1/-2/-3 기준을 D+1~D+5 기간별로 보고, V3/EOD/교집합 그룹의 경로 특성을 비교한다.

## 읽는 법

- `single_day_touch_rate_pct`: 해당 D+n 하루에 기준 고가/저가를 찍은 비율.
- `cum_touch_rate_pct`: D+1부터 해당 D+n까지 한 번이라도 기준을 찍은 비율.
- `plus_first_day_order_rate_pct`: +기준을 -기준보다 먼저 찍은 비율. D+2~D+5는 일 단위 순서 기준이다.
- `same_day_ambiguous_rate_pct`: 같은 거래일에 +와 -가 모두 찍혀 선후를 단정하기 어려운 비율.
- `up_then_close_negative_rate_pct`: 기간 중 +기준을 찍었지만 D+5 종가가 0% 아래로 끝난 비율.
- `up_then_close_below_target_rate_pct`: 기간 중 +기준을 찍었지만 D+5 종가가 그 +기준 아래로 끝난 비율.

## Focus Snapshot

| strategy | D+1 +1.3 single | D+5 +1.3 cumulative | D+5 -2 cumulative | +1.3 first vs -2 | -2 first vs +1.3 | up +1.3 then D5 negative | D5 close >= +1.3 | D5 close <= -2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 현재 EOD웹훅 Top3 | 72.74% | 89.37% | 71.74% | 46.14% | 22.22% | 37.32% | 44.81% | 38.04% |
| V3-C 리스크 | 71.53% | 91.10% | 62.70% | 57.52% | 21.66% | 31.53% | 51.62% | 28.40% |
| V3-C 리스크 ∩ EOD | 69.86% | 88.67% | 62.07% | 53.69% | 22.66% | 28.82% | 53.20% | 27.83% |
| V3-D V2 확인 | 69.63% | 89.65% | 62.94% | 58.48% | 22.86% | 30.69% | 50.42% | 29.60% |
| V3-D V2 확인 ∩ EOD | 68.86% | 88.12% | 62.07% | 53.64% | 22.99% | 27.59% | 52.49% | 27.59% |
| EOD ∩ V3-C ∩ V3-D | 67.97% | 87.70% | 60.66% | 54.51% | 23.36% | 26.64% | 52.46% | 26.23% |

## Files

- `bell_v3_threshold_horizon_matrix.csv`: D+1~D+5 단일/누적/종가 기준 도달률.
- `bell_v3_first_touch_pair_matrix.csv`: +기준과 -기준의 일 단위 우선 도달률.
- `bell_v3_up_then_fall_matrix.csv`: 올랐다가 되밀리는 비율과 D+5 최종 종가 기준.
- `bell_v3_strategy_denominators.csv`: 전략별 표본 수와 eligible rows.

## Caution

D+2~D+5는 분 단위 선후가 아니라 일 단위 고가/저가 기준이다. 같은 날 +와 -가 모두 찍힌 경우는 ambiguous로 별도 계산했다.
현재 V3의 운영 승격 여부는 이 표만으로 결정하면 안 되며, V2/Human source freshness 복구가 먼저다.
