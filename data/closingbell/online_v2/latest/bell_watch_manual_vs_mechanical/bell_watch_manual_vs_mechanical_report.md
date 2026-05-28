# Bell Watch Manual vs Mechanical Read-only Report

- generated_at: 2026-05-27T21:55:24
- baseline_model: BASELINE_EOD_VALUE_TOP3
- signal_date_range: 2025-04-02 ~ 2026-05-19
- eligible_signal_days: 275
- guard: 운영 웹훅/스케줄러/주문/계좌 API 변경 없음. 자동매매 연결 없음.
- label rule: D+5 종가/고저가가 모두 확인된 신호일만 주 비교에 사용.

## 결론

- 기계 Top1: 관찰/비교 유지. avg H5 close 3.24%, MDD -67.23%.
- 기계 Top2/Top3: 현재 기계 후보 중 우선 비교 대상은 `MECHANICAL_TOP1`입니다. Top3 avg H5 close 1.80%, MDD -66.01%.
- 수동 proxy: 수동 선택 보조 후보. HUMAN_PROXY_A avg H5 close 4.81%, best-hit 40.00%, worst-hit 23.64%.
- risk-off/no-trade: risk-off=방어형 위험 경고 배지 후보, no-trade filter=방어형 안 사는 날 보조 후보. risk-off buy days 162/275, no-trade filter buy days 175/275.
- Oracle 전략은 사람이 얼마나 맞혀야 하는지 보는 참고 상한/하한이며 운영 후보가 아닙니다.
- 최신 20거래일 카드: +1.3 먼저 26.67%, -2 먼저 33.33%, -2 touch 84.44%, median H5 close -5.63% (MEDIUM_SAMPLE).

## 전체 요약

| strategy | buy_days | no_trade_days | avg_ret_h5_close | median_ret_h5_close | h5_close_win_rate | h5_close_mdd_pct | d1_plus13_before_minus2_rate | d1_minus2_before_plus13_rate | cum_d5_plus13_touch_rate | cum_d5_minus2_touch_rate | max_losing_streak_buy_days | hit_best_of_top3_rate | hit_worst_of_top3_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BEST_OF_TOP3_ORACLE | 275 | 0 | 12.88 | 7.57 | 86.91 | -32.92 | 66.55 | 26.55 | 98.18 | 54.55 | 4 | 100.00 | 0.00 |
| HUMAN_PROXY_A | 275 | 0 | 4.81 | 1.55 | 56.73 | -66.76 | 59.64 | 26.91 | 87.64 | 64.36 | 7 | 40.00 | 23.64 |
| HUMAN_PROXY_RISK_OFF | 162 | 113 | 3.76 | 1.10 | 56.17 | -56.75 | 54.32 | 26.54 | 85.19 | 61.73 | 7 | 38.89 | 24.69 |
| MECHANICAL_TOP1 | 275 | 0 | 3.24 | 1.69 | 59.27 | -67.23 | 54.55 | 29.09 | 88.00 | 63.27 | 7 | 40.73 | 24.73 |
| MECHANICAL_TOP2 | 275 | 0 | 1.90 | 0.91 | 56.00 | -63.93 | 59.09 | 30.73 | 88.00 | 69.45 | 11 | 35.64 | 30.55 |
| MECHANICAL_TOP3 | 275 | 0 | 1.80 | 0.94 | 56.00 | -66.01 | 61.21 | 30.91 | 89.33 | 71.76 | 9 | 33.33 | 33.33 |
| NO_TRADE_BAD_DAY_FILTER | 175 | 100 | 1.61 | 0.91 | 53.71 | -49.41 | 60.57 | 30.67 | 88.95 | 70.48 | 7 | 33.33 | 33.33 |
| WORST_OF_TOP3_ORACLE | 275 | 0 | -8.33 | -7.38 | 16.73 | -100.00 | 53.45 | 41.09 | 81.09 | 90.55 | 25 | 0.00 | 100.00 |

## 최근 구간

| window_id | strategy | buy_days | avg_ret_h5_close | h5_close_mdd_pct | d1_plus13_before_minus2_rate | d1_minus2_before_plus13_rate | cum_d5_minus2_touch_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RECENT_20_SIGNAL_DAYS | MECHANICAL_TOP1 | 20 | 2.09 | -67.23 | 50.00 | 45.00 | 95.00 |
| RECENT_20_SIGNAL_DAYS | MECHANICAL_TOP2 | 20 | 5.01 | -52.24 | 60.00 | 37.50 | 80.00 |
| RECENT_20_SIGNAL_DAYS | MECHANICAL_TOP3 | 20 | 2.81 | -51.04 | 51.67 | 46.67 | 83.33 |
| RECENT_20_SIGNAL_DAYS | HUMAN_PROXY_A | 20 | 8.14 | -66.76 | 50.00 | 50.00 | 75.00 |
| RECENT_20_SIGNAL_DAYS | HUMAN_PROXY_RISK_OFF | 7 | -4.77 | -56.75 | 42.86 | 57.14 | 100.00 |
| RECENT_20_SIGNAL_DAYS | NO_TRADE_BAD_DAY_FILTER | 10 | 4.98 | -37.02 | 53.33 | 43.33 | 83.33 |
| RECENT_20_SIGNAL_DAYS | BEST_OF_TOP3_ORACLE | 20 | 18.57 | -32.92 | 60.00 | 35.00 | 65.00 |
| RECENT_20_SIGNAL_DAYS | WORST_OF_TOP3_ORACLE | 20 | -10.06 | -87.65 | 30.00 | 70.00 | 100.00 |
| RECENT_60_SIGNAL_DAYS | MECHANICAL_TOP1 | 60 | 4.10 | -67.23 | 55.00 | 43.33 | 85.00 |
| RECENT_60_SIGNAL_DAYS | MECHANICAL_TOP2 | 60 | 2.89 | -52.24 | 59.17 | 40.00 | 84.17 |
| RECENT_60_SIGNAL_DAYS | MECHANICAL_TOP3 | 60 | 2.65 | -51.04 | 57.22 | 42.22 | 83.33 |
| RECENT_60_SIGNAL_DAYS | HUMAN_PROXY_A | 60 | 5.96 | -66.76 | 56.67 | 43.33 | 83.33 |
| RECENT_60_SIGNAL_DAYS | HUMAN_PROXY_RISK_OFF | 17 | 1.74 | -56.75 | 41.18 | 58.82 | 88.24 |
| RECENT_60_SIGNAL_DAYS | NO_TRADE_BAD_DAY_FILTER | 27 | 0.77 | -49.41 | 61.73 | 37.04 | 87.65 |
| RECENT_60_SIGNAL_DAYS | BEST_OF_TOP3_ORACLE | 60 | 17.71 | -32.92 | 63.33 | 35.00 | 68.33 |
| RECENT_60_SIGNAL_DAYS | WORST_OF_TOP3_ORACLE | 60 | -10.56 | -99.91 | 48.33 | 51.67 | 98.33 |
| RECENT_120_SIGNAL_DAYS | MECHANICAL_TOP1 | 120 | 5.31 | -67.23 | 56.67 | 40.00 | 75.83 |
| RECENT_120_SIGNAL_DAYS | MECHANICAL_TOP2 | 120 | 3.15 | -55.25 | 60.42 | 37.50 | 78.33 |
| RECENT_120_SIGNAL_DAYS | MECHANICAL_TOP3 | 120 | 3.36 | -51.04 | 60.00 | 38.61 | 78.89 |
| RECENT_120_SIGNAL_DAYS | HUMAN_PROXY_A | 120 | 6.19 | -66.76 | 60.00 | 39.17 | 78.33 |
| RECENT_120_SIGNAL_DAYS | HUMAN_PROXY_RISK_OFF | 53 | 5.92 | -56.75 | 54.72 | 43.40 | 79.25 |
| RECENT_120_SIGNAL_DAYS | NO_TRADE_BAD_DAY_FILTER | 68 | 2.39 | -49.41 | 60.29 | 37.25 | 78.43 |
| RECENT_120_SIGNAL_DAYS | BEST_OF_TOP3_ORACLE | 120 | 17.09 | -32.92 | 64.17 | 35.00 | 65.83 |
| RECENT_120_SIGNAL_DAYS | WORST_OF_TOP3_ORACLE | 120 | -8.42 | -100.00 | 49.17 | 50.83 | 93.33 |

## 사람이 얼마나 맞혀야 하나

| metric | value | note |
| --- | --- | --- |
| avg_best_of_top3_return | 12.88 | Post-outcome upper bound; not usable live |
| avg_top3_equal_weight_return | 1.80 | Mechanical Top3 equal-weight H5 close return |
| avg_top1_return | 3.24 | Mechanical rank1 H5 close return |
| avg_worst_of_top3_return | -8.33 | Post-outcome downside reference |
| human_proxy_best_hit_rate | 40.00 | How often HUMAN_PROXY_A picked the best H5 close result |
| human_proxy_worst_hit_rate | 23.64 | How often HUMAN_PROXY_A picked the worst H5 close result |
| best_pick_rate_needed_to_match_top3 | 33.33 | Assumes non-best picks are random among the other two |
| best_pick_rate_needed_to_match_top1 | 42.00 | Assumes non-best picks are random among the other two |

## 최근 월별 스냅샷

| signal_month | strategy | buy_days | avg_ret_h5_close | h5_close_mdd_pct | d1_minus2_before_plus13_rate |
| --- | --- | --- | --- | --- | --- |
| 2025-12 | MECHANICAL_TOP1 | 21 | 6.46 | -50.32 | 28.57 |
| 2025-12 | MECHANICAL_TOP3 | 21 | 2.89 | -31.57 | 31.75 |
| 2025-12 | HUMAN_PROXY_A | 21 | 10.15 | -25.38 | 23.81 |
| 2026-01 | MECHANICAL_TOP1 | 21 | 1.97 | -21.33 | 47.62 |
| 2026-01 | MECHANICAL_TOP3 | 21 | 2.95 | -10.40 | 34.92 |
| 2026-01 | HUMAN_PROXY_A | 21 | 3.54 | -30.84 | 47.62 |
| 2026-02 | MECHANICAL_TOP1 | 17 | 4.13 | -43.14 | 41.18 |
| 2026-02 | MECHANICAL_TOP3 | 17 | 1.81 | -43.82 | 47.06 |
| 2026-02 | HUMAN_PROXY_A | 17 | 2.24 | -40.87 | 47.06 |
| 2026-03 | MECHANICAL_TOP1 | 21 | 3.56 | -58.83 | 33.33 |
| 2026-03 | MECHANICAL_TOP3 | 21 | 2.85 | -39.36 | 36.51 |
| 2026-03 | HUMAN_PROXY_A | 21 | 5.91 | -44.80 | 33.33 |
| 2026-04 | MECHANICAL_TOP1 | 22 | 12.60 | -24.23 | 50.00 |
| 2026-04 | MECHANICAL_TOP3 | 22 | 9.14 | -2.47 | 40.91 |
| 2026-04 | HUMAN_PROXY_A | 22 | 16.56 | -47.97 | 36.36 |
| 2026-05 | MECHANICAL_TOP1 | 11 | -5.08 | -57.07 | 45.45 |
| 2026-05 | MECHANICAL_TOP3 | 11 | -4.50 | -51.04 | 48.48 |
| 2026-05 | HUMAN_PROXY_A | 11 | -7.58 | -64.12 | 63.64 |

## Human Proxy A 정의

- 사용 feature: D0 고가 대비 위치, D0 종가 대비 위치, D0 거래량 대비 15시 거래량 잔존, 15시 등락률, 감시일차, risk badge count.
- 사용하지 않은 feature: D+1/H5 사후 결과, 수익률, oracle 결과.
- 점수 비중: high hold 22, close hold 18, volume retention 18, signal strength 15, fresh age 15, low risk 12.

## No-trade 처리

- `HUMAN_PROXY_RISK_OFF`: 최근 20거래일 as-of 카드가 위험 상태면 해당 신호일은 0% 수익률/no-trade로 자본곡선에 반영.
- `NO_TRADE_BAD_DAY_FILTER`: Top3 equal weight가 기본이나, 약한 후보가 2개 이상이거나 거래량 잔존/고가 이탈/오래된 감시일차/최근 20일 위험이 겹치면 no-trade.
- no-trade day는 매수일 성과 평균에서는 제외하고, 자본곡선에서는 0% 일수로 포함.

## 한계

- D+5 first-touch order는 일봉 기준입니다. 같은 날 +1.3과 -2가 함께 닿은 경우 장중 선후는 ambiguous로 분리했습니다.
- H5 자본곡선은 각 신호일 basket을 같은 크기의 paper unit으로 복리 비교한 것입니다. 실제 5일 보유 겹침/현금제약 포트폴리오가 아닙니다.
- 수동 proxy는 실제 사용자의 판단을 완전히 재현하지 못합니다. 체크리스트가 평균적으로 유효한지 보는 보수적 대리 지표입니다.
- 최근 20 신호일은 표본이 작으므로 운영 교체보다는 경고 배지/수동 복기 보조로 해석해야 합니다.

## 출력 파일

- csv/bell_watch_manual_vs_mechanical_summary.csv
- csv/bell_watch_manual_vs_mechanical_by_month.csv
- csv/bell_watch_manual_vs_mechanical_by_recent_window.csv
- csv/bell_watch_manual_vs_mechanical_equity_curve.csv
- csv/bell_watch_manual_vs_mechanical_daily.csv
- csv/bell_watch_manual_vs_mechanical_trades.csv
- csv/bell_watch_manual_proxy_scores.csv

## 검증

- input rows baseline top3: 825
- eligible D+5 signal days: 275
- trade exposure rows: 3162
- operation_touched: false
- webhook_send: false
- scheduler_changed: false
- order_or_account_api: false
