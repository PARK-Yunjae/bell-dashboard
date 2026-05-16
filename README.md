# ClosingBell Paper Watch Dashboard

ClosingBell 패턴 분석 / 복기 워크플로우의 **읽기 전용 Streamlit 대시보드**.

`data/` 아래의 가공된 CSV/parquet만 읽으며, 주문·계좌·스케줄러·키움 쓰기·웹훅 전송 API를 일절 호출하지 않습니다.

## 실행 (로컬)

```powershell
# 더블클릭 가능
C:\Coding\projects\bell-dashboard\run_dashboard.bat
```

또는:

```powershell
cd C:\Coding\projects\bell-dashboard
.\scripts\run_dashboard.ps1
```

공유 가상환경을 직접 지정해서 실행하려면:

```powershell
C:\Coding\projects\_venvs\closingbell-py312\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

ClosingBell 프로젝트는 `C:\Coding\projects\_venvs\closingbell-py312` 공유 venv를 사용합니다. 프로젝트별 `.venv`는 새로 만들지 않습니다.

데이터 루트는 환경변수로 바꿀 수 있습니다 (Streamlit Cloud / 다른 머신용):
- `BELL_DATA_ROOT` env var → `st.secrets["bell_data_root"]` → 기본값 `C:\Coding` 순

## 탭 구조 (4탭, 2026-05-16 reorg)

| 탭 | 내용 |
|---|---|
| **오늘** | 오늘 후보 확인 — 매수 추천 아님 / Paper Watch. 현행 V2 본진 + HYBRID shadow + D0 감시 풀 |
| **복기** | V2 vs HYBRID 신호등 (본진) / 색깔 복기 (1개월) / 1년 차트 복기 / 1년치 통합 |
| **연구실** | Sweet Spot · 전날 패턴 실험실 · 눌림 회복 · V2 차트 검증 · 통계 (하위 탭) |
| **메모** | 사전 느낌 / 사후 생각 / 패턴 / 놓친 점 / 다음 룰 아이디어 / 확신도 (사용자 기록) |

### 본진 / shadow 분리

- **운영 본진**: 현행 V2 웹훅 (변경 없음, bell-webhook이 발송)
- **복기/연구 본진**: V2 vs HYBRID 비교 (이 대시보드 안에서만)
- **HYBRID**: shadow 후보 — 2~4주 검증 후 운영 전환 별도 검토

## 결과 색깔 약속

- 후보 구분: 🟢 본문 후보 / 🟡 참고 후보 / ⚪ 보조 후보
- 신호등 5색 (D0 ~ D+5): G=강세 / Y=회복 / O=실패 / R=약세 / X=보합·결측
- D+1~D+5 결과: 🟢 +3% 먼저 도달 / 🔴 -2% 먼저 터치 / 🟡 +1·+2까지만 또는 같은 날 / ⚪ 미도달

## 데이터 의존성 (주요)

### 온라인용 (GitHub 동봉, < 60 MB)
- `data/closingbell/online_v2/latest/v2_top3_latest.csv` — 오늘 V2 Top3
- `data/closingbell/online_v2/latest/v2_hybrid_signal_wide_by_date_1y.csv` — V2 vs HYBRID 1년 비교
- `data/closingbell/online_v2/latest/v2_hybrid_signal_version_summary_1y.csv` — 1년 KPI
- `data/closingbell/online_v2/latest/v2_hybrid_signal_month_summary_1y.csv` — 월별 안정성
- `data/closingbell/online_v2/latest/v2_hybrid_1y/v2_hybrid_chart_review_*.parquet` — 차트 복기 (일봉/분봉 캔들)
- `data/closingbell/online_v2/latest/pattern_prefix_*.parquet` — 신호등 prefix 통계
- `data/closingbell/online_v2/latest/v2_backdata_1y_*.csv` — 1년 백데이터

### 로컬 전용 (raw, GitHub 절대 금지)
- `data/market/daily_ohlcv/{code}.parquet` — 일봉
- `data/market/minute_ohlcv/{code}.parquet` — 분봉
- `data/market/supply/inst_trade/{code}.parquet` — 외국인·기관 일별 순매수
- `data/market/supply/program_per_code/{code}.parquet` — 프로그램 일별 순매수
- `data/dart/finstate_ts/{corp_code}/{year}_{CFS|OFS}.json` — DART 재무

## 온라인화 (계획)

1. **로컬 → GitHub repo (private)**: `online_v2/latest/`만 push
2. **Streamlit Cloud**: GitHub repo 연결, 무료 public 한도 = 메모리 200MB / repo 1GB
3. **매일 갱신**: 17:05 PostClose → publish 스크립트 → git push → Cloud 자동 reload

세부는 `docs/closingbell/specs/DASHBOARD_ONLINE_PLAN.md` 참고.

## 가드레일 (절대 변경 금지)

- V2 점수 산식 (Codex 영역)
- D0 후보군 필터
- bell-webhook 발송 코드
- 14:15 / 15:00 / 17:05 스케줄러
- 주문 / 계좌 / 자동매매 / yj_bot
- 현재일 후보에 미래 D+1~D+5 결과 노출 (look-ahead 누수)

대시보드는 읽기 전용입니다. 메모 저장만 쓰기 허용 (`user_notes/`).

## 보안 / 민감정보 정책

GitHub에 push하지 않는 것:
- `.streamlit/secrets.toml` — API key, Discord webhook URL
- `data/market/`, `data/dart/`, `data/closingbell/research_index/` 등 raw
- `data/closingbell/user_notes/` — 사용자 개인 메모
- `*sent_log*`, `*paper_watch_sent_log*` — 발송 기록

`.gitignore`가 자동으로 막아줍니다. push 전 `git status`로 한 번 더 확인하세요.

## 관련 문서

- `docs/closingbell/reports_summary/dashboard_uiux_next_plan_20260511.md` — UI/UX 작업 계획
- `docs/closingbell/specs/DASHBOARD_ONLINE_PLAN.md` — 온라인화 3단계
- `docs/closingbell/handoff/CLAUDE_20260511_BELL_PIPELINE_AUTOMATION_PROGRESS.md` — 전체 파이프라인 진행
- `C:\Users\PYJ\Downloads\BELL_DASHBOARD_REORG_PLAN_20260516.md` — 4탭 reorg 기획
