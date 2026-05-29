from __future__ import annotations

import json
import os
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except Exception:  # pragma: no cover - Streamlit fallback when plotly is absent.
    go = None
    make_subplots = None


# 데이터 루트 — 환경변수 우선 (Streamlit Cloud / Docker / 다른 머신 대응).
# 우선순위: 1) BELL_DATA_ROOT env var, 2) st.secrets["bell_data_root"], 3) 기본값
def _resolve_root() -> Path:
    env_root = os.environ.get("BELL_DATA_ROOT", "").strip()
    if env_root:
        return Path(env_root)
    try:
        secret_root = st.secrets.get("bell_data_root", "").strip() if hasattr(st, "secrets") else ""
        if secret_root:
            return Path(secret_root)
    except Exception:
        pass
    return Path(r"C:\Coding")


ROOT = _resolve_root()
DATA = ROOT / "data"
CLOSINGBELL = DATA / "closingbell"
WATCHLISTS = CLOSINGBELL / "shared" / "watchlists"
SIM = CLOSINGBELL / "simulations"
QUALITY = CLOSINGBELL / "quality"
BACKTEST_ROOT = CLOSINGBELL / "backtests"
USER_NOTES_PATH = CLOSINGBELL / "user_notes" / "one_year_review_notes.csv"
DOCS = ROOT / "docs" / "closingbell"
DAILY = DATA / "market" / "daily_ohlcv"
MINUTE = DATA / "market" / "minute_ohlcv"
SENT_LOG = CLOSINGBELL / "shared" / "sent_log" / "paper_watch_sent_log.jsonl"

def _latest_path(parent: Path, pattern: str, fallback: Path) -> Path:
    """디렉토리 내 패턴 매칭 중 가장 최근 수정 파일/디렉토리. 없으면 fallback."""
    if not parent.exists():
        return fallback
    matches = sorted(parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else fallback


# 일일 운영 파일 — 디렉토리에서 가장 최근 파일을 자동 선택 (하드코딩 제거)
# fallback 경로는 _20260510 명시본 — 새 파일이 없을 때를 대비.
D0_POOL_PATH = _latest_path(WATCHLISTS, "d0_pool_dryrun_*.csv", WATCHLISTS / "d0_pool_dryrun_20260510.csv")
WATCHLIST_20D_PATH = _latest_path(WATCHLISTS, "watchlist_d0_20d_*.csv", WATCHLISTS / "watchlist_d0_20d_20260510.csv")
WEBHOOK_PICKS_PATH = _latest_path(WATCHLISTS, "webhook_picks_5d_*.csv", WATCHLISTS / "webhook_picks_5d_20260510.csv")
SCORE_PATH = _latest_path(WATCHLISTS, "score_breakdown_*.csv", WATCHLISTS / "score_breakdown_20260510.csv")

ENRICHED_DIR = _latest_path(SIM, "enrichment_dryrun_*", SIM / "enrichment_dryrun_20260510")
ENRICHED_PATH = ENRICHED_DIR / "enriched_candidates.csv"

V20_DIR = _latest_path(SIM, "v20_policy_month_*", SIM / "v20_policy_month_20260510")
LIVE_SAFE_PATH = V20_DIR / "live_safe_candidates.csv"
REVIEW_PATH = V20_DIR / "review_outcomes.csv"

SECRET_SCAN_DIR = _latest_path(QUALITY, "webhook_secret_scan_*", QUALITY / "webhook_secret_scan_20260510")
SECRET_SCAN_SUMMARY = SECRET_SCAN_DIR / "webhook_secret_scan_summary.json"

# 글로벌 지수 + 종목 매핑 (오늘의 웹훅 후보 패널용) — 단일 파일이라 자동탐지 불필요
GLOBAL_PATH = DATA / "market" / "global" / "global_merged.csv"
STOCK_MAPPING_PATH = DATA / "market" / "universe" / "stock_mapping.csv"

# DART 재무 데이터 (영업이익/매출/순이익 패널용)
DART_DIR = DATA / "dart"
DART_COMPANY_DIR = DART_DIR / "company"
DART_FINSTATE_DIR = DART_DIR / "finstate_ts"

# 데이터 품질 (0값/거래정지/시장조치 — Codex 산출)
STATUS_EVENTS_PATH = DATA / "market" / "events" / "stock_status_events.csv"
RESEARCH_INDEX_DIR = CLOSINGBELL / "research_index"
WHOLE_MARKET_PATTERN_DIR = RESEARCH_INDEX_DIR / "whole_market_next_green_daily_probe_20260516"
WHOLE_MARKET_PATTERN_CLOSE_UP_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_close_up_positive_20260516.parquet"
WHOLE_MARKET_PATTERN_CLOSE_UP_SAMPLE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_close_up_positive_sample_20260516.csv"
WHOLE_MARKET_PATTERN_POSITIVE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_full_above_positive_20260516.parquet"
WHOLE_MARKET_PATTERN_SAMPLE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_full_above_positive_sample_20260516.csv"
WHOLE_MARKET_PATTERN_YELLOW_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_yellow_recovery_20260516.parquet"
WHOLE_MARKET_PATTERN_YELLOW_SAMPLE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_yellow_recovery_sample_20260516.csv"
WHOLE_MARKET_PATTERN_ORANGE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_orange_failed_20260516.parquet"
WHOLE_MARKET_PATTERN_ORANGE_SAMPLE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_orange_failed_sample_20260516.csv"
WHOLE_MARKET_PATTERN_RED_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_red_weak_20260516.parquet"
WHOLE_MARKET_PATTERN_RED_SAMPLE_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_red_weak_sample_20260516.csv"
WHOLE_MARKET_PATTERN_COLOR_COUNTS_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d1_color_counts_20260516.csv"
WHOLE_MARKET_PATTERN_LABELED_PATH = WHOLE_MARKET_PATTERN_DIR / "whole_market_d0_labeled_10y_20260516.parquet"
WHOLE_MARKET_PATTERN_NOTES_PATH = CLOSINGBELL / "user_notes" / "whole_market_pattern_lab_notes.csv"

# ONLINE V2 스냅샷 — repo 동봉 우선 (GitHub/Streamlit Cloud 호환), 환경변수 경로 fallback.
# 우선순위: 1) repo 안의 ./data/closingbell/online_v2/latest/
#           2) BELL_DATA_ROOT/data/closingbell/online_v2/latest/
_REPO_BUNDLED_ONLINE_V2 = Path(__file__).resolve().parent / "data" / "closingbell" / "online_v2" / "latest"
_ENV_ONLINE_V2 = CLOSINGBELL / "online_v2" / "latest"
ONLINE_V2_DIR = _REPO_BUNDLED_ONLINE_V2 if _REPO_BUNDLED_ONLINE_V2.exists() else _ENV_ONLINE_V2
DAILY3_POOL_PREVIEW_DIR = ONLINE_V2_DIR / "daily3_pool_preview"
EOD_ACTIVE_WATCH_PREVIEW_DIR = ONLINE_V2_DIR / "eod_d0_active_watch_preview"
EOD_ACTIVE_WATCH_1Y_DIR = ONLINE_V2_DIR / "eod_d0_active_watch_1y"
# Bell Watch 수동검증 read-only 연구 데이터 (Codex 2026-05-26 산출)
BELL_WATCH_ASOF_DIR = ONLINE_V2_DIR / "bell_watch_asof_performance"
BELL_WATCH_MANUAL_VS_MECH_DIR = ONLINE_V2_DIR / "bell_watch_manual_vs_mechanical"
BELL_V3_CONSENSUS_DIR = ONLINE_V2_DIR / "bell_v3_consensus"
BELL_V3_PROMOTION_DIR = ONLINE_V2_DIR / "bell_v3_promotion_deep_dive"
BELL_V3_OPERATIONAL_DIR = ONLINE_V2_DIR / "bell_v3_operational_switch"
# Paper Watch 사후 라벨링 데이터 — Codex retro labeling 산출 (2026-05-20)
# online 사본 우선, 없으면 shared 원본 fallback (publish 시 동기화될 예정)
EOD_PAPER_WATCH_DIRS: list[Path] = [
    ONLINE_V2_DIR / "eod_d0_active_watch_paper",
    Path(r"C:\Coding\data\closingbell\shared\eod_d0_active_watch_paper"),
]

# Online 모드 감지 — 큰 원본 데이터 (daily/minute parquet, DART) 없으면 GitHub 배포 환경으로 간주.
# 이때는 메인 탭들이 깨지지 않게 안내만 보여주고 "온라인 V2" 탭만 동작시킴.
IS_ONLINE_MODE = (not DAILY.exists()) or (len(list(DAILY.glob("*.parquet"))[:1]) == 0)

MA_WINDOWS = [5, 8, 20, 33, 60, 120]

POLICY_LABELS = {
    "NO_TRADE_REVIEW": "관망 우선",
    "SCALP_WATCH_ONLY": "짧은 관찰만",
    "WAIT_PULLBACK_OR_D1_CONFIRM": "눌림 또는 다음날 확인",
    "RANK1_D1_CONFIRM_REQUIRED": "다음날 확인 필요",
    "RANK2_MAIN_BODY_CONFIRM_FIRST": "2순위 안정 후보",
    "RANK2_STABLE": "2순위 안정 후보",
    "RANK2_STABLE_BUT_STALE_CHECK": "2순위이나 오래된 후보",
    "RANK3_REFERENCE_CONDITIONAL": "참고 관찰",
    "REFERENCE_CONDITIONAL": "참고 관찰",
    "LOG_ONLY_REVIEW": "보조 검토",
    "STALE_BUT_WATCHABLE": "오래됐지만 관찰 가능",
    "STALE_WATCH": "오래된 감시 후보",
}

ROLE_LABELS = {
    "BODY_TOP2": "본문 후보",
    "REFERENCE_RANK3": "참고 후보",
    "LOG_ONLY": "보조 후보",
}

SCORE_REASON_LABELS = {
    "rank2_stability_bonus": "2순위 안정 가설 보너스",
    "rank1_overheat_check": "1순위 과열 확인 필요",
    "rank3_reference_only": "3순위는 참고 전용",
    "log_only_rank4_5": "보조 후보로만 기록",
    "d0_age_over_20_exit": "D0 20거래일 초과",
    "d0_age_stale": "D0 신선도 저하",
    "near_d0_high_overheat_check": "D0 고점 부근이라 과열 점검",
    "pullback_from_d0_high": "D0 고점 대비 눌림",
    "volume_expansion_moderate": "거래량 증가 적정",
    "volume_expansion_extreme": "거래량 과열 가능성",
    "upper_shadow_risk": "윗꼬리 부담",
    "historical_invalid_price_review": "과거 가격 이상치 확인",
    "high_plus_confidence": "데이터 확신도 높음",
    "mid_confidence": "데이터 확신도 보통",
    "low_confidence": "데이터 확신도 낮음",
    "target_first_ok": "목표 우선 도달 기대",
    "target_first_weak": "목표 우선 도달 약함",
    "high_stop_risk": "손절선 터치 위험 높음",
    "stop_risk_moderate": "손절 위험 보통",
    "extreme_stop_risk": "극단 손절 위험",
    "warning_d0_stale": "D0 오래됨 경고",
}

WARNING_LABELS = {
    "EXTREME_STOP_RISK": "손절 위험 큼",
    "HIGH_STOP_RISK": "하락 변동성 주의",
    "TARGET_FIRST_WEAK": "목표 도달 전 흔들림 가능",
    "TOUCH_HIGH_BUT_STOP_HIGH": "위로도 움직였지만 아래 변동도 큼",
    "D0_STALE": "D0 이후 시간이 길어 신선도 낮음",
    "FALLBACK_PROFILE_USED": "유사 표본 기반",
    "DATA_QUALITY_REVIEW": "가격 데이터 품질 확인 필요",
    "DATA_LATEST_PRICE_INVALID": "최신 가격 이상치",
}

# 1년치 복기 v2: 핵심 3종목 슬롯 (본문 후보 + 참고 후보)
# Log4/Log5는 보조 후보로 별도 expander에 표시.
# (slot_key, rank, role, short_label, badge_class)
SLOT_DEFINITIONS = [
    ("Top1", 1, "BODY_TOP2", "본문 1순위", "cb-top2"),
    ("Top2", 2, "BODY_TOP2", "본문 2순위", "cb-top2"),
    ("Rank3", 3, "REFERENCE_RANK3", "참고", "cb-rank3"),
]
SLOT_KEYS = [item[0] for item in SLOT_DEFINITIONS]
SLOT_BY_KEY = {item[0]: item for item in SLOT_DEFINITIONS}

LOG_SLOT_DEFINITIONS = [
    ("Log4", 4, "LOG_ONLY", "보조 1"),
    ("Log5", 5, "LOG_ONLY", "보조 2"),
]

NOTE_FIELDS = [
    ("user_view_before_result", "사전 느낌", "결과를 보기 전, 차트와 점수만 보고 든 느낌"),
    ("user_view_after_result", "사후 생각", "결과를 본 뒤 정리한 생각"),
    ("pattern_note", "패턴 메모", "반복적으로 보이는 패턴이나 시그널"),
    ("mistake_note", "놓친 점", "사전과 사후 사이 놓친 신호"),
    ("next_rule_idea", "다음 점검 아이디어", "다음 비슷한 상황에서 점검할 항목"),
]

KOREAN_COLUMNS = {
    "rank": "후보 순위",
    "role": "후보 구분",
    "role_label": "후보 구분",
    "stock_code": "종목코드",
    "stock_name": "종목명",
    "stock_label": "종목",
    "signal_date": "기준일",
    "d0_date": "D0 날짜",
    "d0_reason": "D0 사유",
    "d0_rank": "D0 순위",
    "d0_price": "D0 종가",
    "d0_high": "D0 고가",
    "d0_volume": "D0 거래량",
    "d0_trading_value": "D0 거래대금",
    "d0_volume_rank": "거래량 순위",
    "d0_trading_value_rank": "거래대금 순위",
    "d0_rank_score": "수급 순위 합",
    "current_price": "현재가",
    "distance_from_d0_high_pct": "D0 고가 대비",
    "volume_ratio_vs_d0": "D0 대비 거래량",
    "volume_ratio_vs_20d": "20일 대비 거래량",
    "policy_decision": "정책판단",
    "policy_label": "정책판단",
    "score": "점수",
    "score_reasons": "점수근거",
    "score_reason_label": "점수근거",
    "warning_codes": "경고",
    "warning_label": "경고",
    "d1_d5_tracking_saved": "D+1~D+5 저장",
    "watch_status": "감시상태",
    "is_stale": "오래됨",
    "condition_status": "조건상태",
    "tracking_days_available": "추적일수",
    "outcome_d1_d5_plus1_touch": "+1% 도달",
    "outcome_d1_d5_plus2_touch": "+2% 도달",
    "outcome_d1_d5_plus3_touch": "+3% 도달",
    "outcome_d1_d5_minus2_touch": "-2% 터치",
    "outcome_d1_plus1_touch": "D+1 +1%",
    "outcome_d1_plus2_touch": "D+1 +2%",
    "outcome_d1_plus3_touch": "D+1 +3%",
    "outcome_d1_minus2_touch": "D+1 -2%",
    "outcome_d1_high_return": "D+1 최고",
    "outcome_d1_low_return": "D+1 최저",
    "target3_vs_risk2_order": "+3/-2 순서",
    "outcome_max_high_return": "최고수익률",
    "outcome_min_low_return": "최저하락률",
    "outcome_status": "결과상태",
    "first_plus1_day": "+1% 첫날",
    "first_plus2_day": "+2% 첫날",
    "first_plus3_day": "+3% 첫날",
    "first_minus2_day": "-2% 첫날",
}


st.set_page_config(page_title="ClosingBell 수동 복기", layout="wide")

st.markdown(
    """
<style>
  .block-container { max-width: 1520px; padding-top: 2rem; }
  div[data-testid="stMetricValue"] {
    white-space: normal;
    overflow-wrap: anywhere;
    line-height: 1.12;
    font-size: 1.75rem;
  }
  div[data-testid="stMetricLabel"] p { white-space: normal; line-height: 1.25; }
  div[data-testid="stDataFrame"] { font-size: 0.94rem; }
  div[data-testid="stDataFrame"] div[role="gridcell"] { line-height: 1.35; }
  .cb-note {
    border-left: 4px solid #4f8cff;
    padding: 0.7rem 0.9rem;
    margin: 0.5rem 0 1rem 0;
    background: rgba(79, 140, 255, 0.10);
    border-radius: 6px;
    line-height: 1.55;
  }
  .cb-period {
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.35;
    white-space: normal;
  }
  .cb-subtle { color: #a8b0bd; font-size: 0.92rem; line-height: 1.45; }
  .cb-badge {
    display: inline-block;
    padding: 0.18rem 0.48rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.86rem;
    margin-right: 0.35rem;
  }
  .cb-top2 { background: rgba(56, 161, 105, 0.18); color: #7ee0a1; }
  .cb-rank3 { background: rgba(214, 158, 46, 0.18); color: #ffd166; }
  .cb-log { background: rgba(160, 174, 192, 0.18); color: #cbd5e0; }
  .cb-review { background: rgba(128, 90, 213, 0.18); color: #c4b5fd; }
  /* === 1년치 복기 v2 === */
  .cb-mini-row {
    display: flex; gap: 18px; flex-wrap: wrap;
    padding: 10px 14px;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    margin: 8px 0 14px;
    font-size: 0.95rem;
    line-height: 1.6;
  }
  .cb-mini-cell { white-space: nowrap; }
  .cb-mini-key { color:#9aa4b2; margin-right:4px; }
  .cb-result-good { color:#7ee0a1; font-weight:700; }
  .cb-result-bad { color:#ff8a8a; font-weight:700; }
  .cb-result-mixed { color:#ffd166; font-weight:700; }
  .cb-result-none { color:#a0aec0; }
  .cb-info-card {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 14px 16px;
    height: 100%;
    border: 1px solid rgba(255,255,255,0.04);
  }
  .cb-info-card h4 {
    margin: 0 0 10px 0;
    font-size: 0.95rem;
    color: #cbd5e0;
    letter-spacing: 0.2px;
  }
  .cb-row { display:flex; justify-content: space-between; padding: 4px 0; gap: 12px; }
  .cb-key { color:#9aa4b2; font-size:0.86rem; }
  .cb-val { font-weight:600; font-size:0.92rem; }
  .cb-val-pos { color:#7ee0a1; }
  .cb-val-neg { color:#ff8a8a; }
  .cb-val-warn { color:#ffd166; }
  .cb-tag {
    display:inline-block;
    background: rgba(255,255,255,0.06);
    color:#cbd5e0;
    padding: 3px 10px;
    border-radius: 999px;
    margin: 2px 4px 2px 0;
    font-size: 0.83rem;
    line-height: 1.4;
  }
  .cb-tag-warn { background: rgba(229, 62, 62, 0.18); color:#ff8a8a; }
  .cb-tag-good { background: rgba(56, 161, 105, 0.18); color:#7ee0a1; }
  .cb-tag-info { background: rgba(66, 153, 225, 0.18); color:#9ecbff; }
  .cb-tag-rec { background: rgba(221, 107, 32, 0.20); color:#f6ad55; }
  .cb-quality-bar { display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; margin:4px 0 6px; }
  .cb-date-dots {
    display: inline-block;
    margin-left: 12px;
    letter-spacing: 4px;
    font-size: 1.1rem;
    line-height: 1;
    vertical-align: middle;
  }
  .cb-overlay-card {
    background: rgba(0,0,0,0.45);
    color: #e2e8f0;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 0.84rem;
    line-height: 1.45;
    display: inline-block;
  }
  .cb-progress-wrap { background: rgba(255,255,255,0.06); border-radius:6px; height:10px; position:relative; margin: 4px 0 6px; }
  .cb-progress-bar { height:10px; border-radius:6px; }
  .cb-progress-pos { background: linear-gradient(90deg,#38a169,#7ee0a1); }
  .cb-progress-neg { background: linear-gradient(90deg,#c53030,#ff8a8a); }
  .cb-section-title { font-size: 0.95rem; color:#cbd5e0; margin: 14px 0 6px; font-weight:600; }
  .cb-toggle-note { color:#9aa4b2; font-size:0.8rem; margin-left:8px; }

  /* === Light 모드 가독성 강화 (2026-05-16) === */
  /* config.toml base=light 환경에서 회색 텍스트가 너무 연해서 읽기 어려운 문제 해결.
     본문 텍스트는 #111827, 보조 텍스트는 #4b5563~#6b7280 수준으로 강제. */
  .stApp[data-theme="light"] .cb-key,
  .stApp[data-theme="light"] .cb-mini-key,
  .stApp[data-theme="light"] .cb-subtle,
  .stApp[data-theme="light"] .cb-toggle-note { color: #4b5563 !important; }
  .stApp[data-theme="light"] .cb-val,
  .stApp[data-theme="light"] .cb-period { color: #111827 !important; }
  .stApp[data-theme="light"] .cb-section-title,
  .stApp[data-theme="light"] .cb-info-card h4 { color: #1f2937 !important; }
  .stApp[data-theme="light"] .cb-info-card,
  .stApp[data-theme="light"] .cb-mini-row {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
  }
  .stApp[data-theme="light"] .cb-note { background: rgba(37,99,235,0.06) !important; }
  /* media query fallback — data-theme attribute가 없는 경우 대비 */
  @media (prefers-color-scheme: light) {
    .cb-key, .cb-mini-key, .cb-subtle, .cb-toggle-note { color: #4b5563; }
    .cb-val, .cb-period { color: #111827; }
    .cb-section-title, .cb-info-card h4 { color: #1f2937; }
  }

  /* === 글 겹침 / 표 정렬 / 가독성 보강 (2026-05-17) === */
  /* 카드 패딩·줄간격·세로 정렬 통일 */
  .cb-info-card {
    padding: 14px 16px !important;
    min-height: 96px;
    display: flex; flex-direction: column; justify-content: space-between;
    line-height: 1.5;
    word-break: keep-all;
    overflow-wrap: anywhere;
  }
  .cb-info-card .cb-key { line-height: 1.45; margin-bottom: 4px; }
  .cb-info-card > div { white-space: normal !important; }

  /* 카드 사이 여백 보강 (Streamlit columns 의 좁은 gap 보정) */
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding-right: 6px; padding-left: 6px;
  }

  /* 테이블·DataFrame 한글 헤더 잘림 방지, 컬럼 폭 균형 */
  div[data-testid="stDataFrame"] table { table-layout: auto !important; }
  div[data-testid="stDataFrame"] th,
  div[data-testid="stDataFrame"] td {
    white-space: normal !important;
    word-break: keep-all;
    overflow-wrap: anywhere;
    line-height: 1.45 !important;
    padding: 6px 8px !important;
  }
  div[data-testid="stDataFrame"] th {
    font-weight: 700 !important;
    background: #f8fafc !important;
  }

  /* 신호등 이모지 칼럼 깨짐/짤림 방지 */
  div[data-testid="stDataFrame"] td:has(span.emoji),
  div[data-testid="stDataFrame"] td {
    font-variant-emoji: emoji;
  }

  /* sub_tabs 헤더가 줄바꿈으로 한 줄 차지 방지 + 글씨 키움 */
  div[data-baseweb="tab-list"] {
    flex-wrap: wrap !important;
    gap: 6px !important;
  }
  div[data-baseweb="tab-list"] button {
    white-space: nowrap !important;
    min-height: 42px !important;
    padding: 8px 14px !important;
  }
  div[data-baseweb="tab-list"] button p,
  div[data-baseweb="tab-list"] button div {
    font-size: 15px !important;
    font-weight: 600 !important;
  }

  /* DART 재무 카드 글씨 진하게 */
  .stApp[data-theme="light"] .cb-info-card { color: #111827; }
  .stApp[data-theme="light"] .cb-info-card .cb-row span,
  .stApp[data-theme="light"] .cb-info-card .cb-row div { color: #111827 !important; }
  .stApp[data-theme="light"] .cb-info-card .cb-key { color: #4b5563 !important; }
  .stApp[data-theme="light"] .cb-val,
  .stApp[data-theme="light"] .cb-val-pos,
  .stApp[data-theme="light"] .cb-val-neg,
  .stApp[data-theme="light"] .cb-val-warn { font-weight: 700 !important; }

  /* Plotly 차트 — Streamlit 컨테이너 안에서 가로 100% 채우기 강제 */
  .js-plotly-plot, .plotly, .plot-container {
    width: 100% !important;
  }

  /* expander 라벨 본문 진하게 */
  .stApp[data-theme="light"] summary p { color: #111827 !important; font-weight: 600; }

  /* warning/info/error 박스 본문 가독성 */
  .stApp[data-theme="light"] div[data-testid="stAlert"] p {
    color: #111827 !important; line-height: 1.55;
  }

  /* metric 값 잘림 방지 */
  div[data-testid="stMetricValue"] > div { font-variant-numeric: tabular-nums; }

  /* selectbox/text_input — 라이트 모드에서 흐릿한 placeholder 보강 */
  .stApp[data-theme="light"] input::placeholder,
  .stApp[data-theme="light"] textarea::placeholder { color: #94a3b8 !important; }

  /* === 반응형 / 모바일 보강 (2026-05-18) === */
  /* Streamlit columns 가 좁은 화면(<768px)에서 세로 stack 으로 변환됨.
     카드/표/차트가 잘리지 않게 padding/scroll 보강. */
  @media (max-width: 900px) {
    .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; max-width: 100% !important; }
    .cb-info-card { min-height: auto !important; padding: 12px 14px !important; }
    h1 { font-size: 1.75rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.15rem !important; }
    div[data-baseweb="tab-list"] button p,
    div[data-baseweb="tab-list"] button div { font-size: 13px !important; }
    .js-plotly-plot { min-height: 380px !important; }
  }

  /* 표 가로 스크롤 (모바일에서 좁은 화면 보호) */
  div[data-testid="stDataFrame"] {
    overflow-x: auto !important;
  }

  /* metric 라벨 줄바꿈 깔끔하게 */
  div[data-testid="stMetricLabel"] {
    word-break: keep-all;
    overflow-wrap: anywhere;
  }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_csv(path_text: str) -> pd.DataFrame:
    path = Path(path_text)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")


@st.cache_data(show_spinner=False)
def read_json(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def read_sent_log(path_text: str) -> list[dict[str, Any]]:
    path = Path(path_text)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


@st.cache_data(show_spinner=False)
def latest_backtest_dir() -> str:
    if not BACKTEST_ROOT.exists():
        return ""
    candidates = [path for path in BACKTEST_ROOT.glob("one_year_non_ai_*") if (path / "run_manifest.json").exists()]
    if not candidates:
        return ""
    one_year: list[Path] = []
    for path in candidates:
        try:
            manifest = json.loads((path / "run_manifest.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        if int(manifest.get("trading_days") or manifest.get("days_requested") or 0) >= 240:
            one_year.append(path)
    if one_year:
        classic = [path for path in one_year if "classic_volume10m" in path.name]
        return str(max(classic or one_year, key=lambda path: path.stat().st_mtime))
    return str(max(candidates, key=lambda path: path.stat().st_mtime))


@st.cache_data(show_spinner=False)
def load_daily(code: str) -> pd.DataFrame:
    path = DAILY / f"{normalize_code(code)}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path).copy()
    df["date"] = pd.to_datetime(df["date"])
    for window in MA_WINDOWS:
        df[f"ma{window}"] = df["close"].rolling(window).mean()
    return df


@st.cache_data(show_spinner=False)
def load_global_merged() -> pd.DataFrame:
    if not GLOBAL_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(GLOBAL_PATH, dtype=str, encoding="utf-8-sig").fillna("")


def global_row_for_date(target_date: str) -> dict[str, Any]:
    """signal_date에 해당하는 글로벌 지수 한 행. 없으면 가장 가까운 과거 영업일."""
    df = load_global_merged()
    if df.empty:
        return {}
    rows = df[df["date"] == str(target_date)]
    if rows.empty:
        rows = df[df["date"] < str(target_date)].sort_values("date").tail(1)
    return rows.iloc[0].to_dict() if not rows.empty else {}


@st.cache_data(show_spinner=False)
def load_stock_mapping() -> dict[str, dict[str, str]]:
    if not STOCK_MAPPING_PATH.exists():
        return {}
    df = pd.read_csv(STOCK_MAPPING_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    return {normalize_code(row.get("code", "")): row.to_dict() for _, row in df.iterrows()}


@st.cache_data(show_spinner="DART 회사 매핑 빌드 (최초 1회만)…")
def load_corp_mapping() -> dict[str, str]:
    """stock_code(6) → corp_code(8) 매핑. 약 2,862개 JSON 1회 스캔."""
    mapping: dict[str, str] = {}
    if not DART_COMPANY_DIR.exists():
        return mapping
    for path in DART_COMPANY_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        stock = str(data.get("stock_code", "")).strip()
        corp = str(data.get("corp_code", "")).strip()
        if stock and corp:
            mapping[normalize_code(stock)] = corp
    return mapping


def find_corp_code(stock_code: str) -> str:
    return load_corp_mapping().get(normalize_code(stock_code), "")


def latest_finstate_path(corp_code: str) -> Path | None:
    """가장 최근 연도 CFS(연결) 우선, 없으면 OFS(별도)."""
    if not corp_code:
        return None
    sub = DART_FINSTATE_DIR / corp_code
    if not sub.exists():
        return None
    cfs = sorted(sub.glob("*_CFS.json"), reverse=True)
    if cfs:
        return cfs[0]
    ofs = sorted(sub.glob("*_OFS.json"), reverse=True)
    return ofs[0] if ofs else None


# 수급(매매주체) 데이터
SUPPLY_DIR = DATA / "market" / "supply"
INST_TRADE_DIR = SUPPLY_DIR / "inst_trade"
PROGRAM_PER_CODE_DIR = SUPPLY_DIR / "program_per_code"


@st.cache_data(show_spinner=False)
def load_status_events() -> dict[str, list[dict[str, Any]]]:
    """stock_code(6) → [거래정지/투자경고/특수이벤트 dict, ...]. Codex 산출 stock_status_events.csv."""
    if not STATUS_EVENTS_PATH.exists():
        return {}
    df = pd.read_csv(STATUS_EVENTS_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    out: dict[str, list[dict[str, Any]]] = {}
    for _, row in df.iterrows():
        out.setdefault(normalize_code(row.get("stock_code", "")), []).append(row.to_dict())
    return out


@st.cache_data(show_spinner="데이터 품질 audit 로딩 (최초 1회)…")
def load_zero_value_audit() -> dict[tuple[str, str], list[dict[str, Any]]]:
    """(signal_date, stock_code(6)) → [audit row dict, ...]. Codex 산출 zero_value_root_cause_audit_*.csv 최신."""
    path = _latest_path(RESEARCH_INDEX_DIR, "zero_value_root_cause_audit_*.csv",
                        RESEARCH_INDEX_DIR / "zero_value_root_cause_audit_20260511.csv")
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    out: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for _, row in df.iterrows():
        key = (str(row.get("signal_date", "")), normalize_code(row.get("stock_code", "")))
        out.setdefault(key, []).append(row.to_dict())
    return out


def _event_in_range(ev: dict[str, Any], signal_date: str, extra_dates: list[str]) -> bool:
    start = str(ev.get("start_date", ""))[:10]
    end = str(ev.get("end_date", "") or ev.get("start_date", ""))[:10]
    targets = [str(signal_date)[:10]] + [str(d)[:10] for d in extra_dates]
    for t in targets:
        if start and end and start <= t <= end:
            return True
        if start and not end and start == t:
            return True
    return False


def status_badges_for(code: str, signal_date: str, extra_dates: list[str] | None = None) -> list[dict[str, str]]:
    """종목+신호일에 대한 데이터 품질 배지 리스트. 매칭 없으면 [데이터 정상]."""
    extra_dates = extra_dates or []
    code = normalize_code(code)
    badges: list[dict[str, str]] = []
    seen_labels: set[str] = set()

    # 1. stock_status_events
    for ev in load_status_events().get(code, []):
        if not _event_in_range(ev, signal_date, extra_dates):
            continue
        et = str(ev.get("event_type", ""))
        en = str(ev.get("event_name", ""))
        desc = str(ev.get("description", "") or ev.get("manual_note", ""))
        if et == "TRADING_HALT":
            label, emoji, cls = "거래정지 가능", "🚫", "cb-tag-warn"
        elif et == "DELISTING_RELATED":
            label, emoji, cls = "상폐 관련", "⚠️", "cb-tag-warn"
        elif et == "CORPORATE_ACTION":
            label, emoji, cls = "특수 이벤트", "🏷", "cb-tag-info"
        elif "ZERO_VALUE_OHLCV" in en or "ZERO_VALUE_OHLCV" in et:
            label, emoji, cls = "일봉 0값 관측", "⚠️", "cb-tag"
        else:  # UNKNOWN
            label, emoji, cls = "상태 확인 필요", "❓", "cb-tag"
        if label not in seen_labels:
            seen_labels.add(label)
            badges.append({"emoji": emoji, "label": label, "cls": cls, "detail": f"{en} | {desc}"[:200]})

    # 2. zero_value_root_cause_audit (signal_date 기준)
    for row in load_zero_value_audit().get((str(signal_date)[:10], code), []):
        zt = str(row.get("zero_or_missing_type", ""))
        layer = str(row.get("data_layer", ""))
        possible = str(row.get("possible_reason", ""))
        treat = str(row.get("recommended_treatment", ""))
        is_minute = "minute" in layer.lower()
        is_supply = "foreign" in layer.lower() or "institution" in layer.lower() or "supply" in layer.lower()
        if zt in ("REAL_ZERO_NO_TRADE_OR_HALTED_POSSIBLE", "MINUTE_MISSING_WITH_DAILY_ZERO_VOLUME"):
            label, emoji, cls = "거래정지 가능", "🚫", "cb-tag-warn"
        elif zt == "REAL_ZERO_SOURCE_ROW_PRESENT":
            label, emoji, cls = ("수급 실제 0" if is_supply else "실제 0값"), "💸" if is_supply else "⚠️", "cb-tag"
        elif zt in ("MINUTE_SPARSE", "MINUTE_PARTIAL"):
            label, emoji, cls = "분봉 일부 없음", "📊", "cb-tag"
        elif zt in ("MISSING_FILE", "MINUTE_COLLECTION_GAP_OR_CODE_MAPPING") and is_minute:
            label, emoji, cls = "분봉 없음", "📊", "cb-tag"
        elif zt in ("MISSING_VALUE", "PARTIAL_VALUE") and is_supply:
            label, emoji, cls = "수급 결측", "💸", "cb-tag"
        elif zt in ("MISSING_FILE", "MISSING_DATE", "MISSING_VALUE", "PARTIAL_VALUE"):
            label, emoji, cls = "데이터 일부 결측", "📁", "cb-tag"
        else:
            continue
        if label not in seen_labels:
            seen_labels.add(label)
            badges.append({"emoji": emoji, "label": label, "cls": cls, "detail": f"{layer} {zt} | {possible} | 권장: {treat}"[:200]})

    # 중요 배지 vs 흔한 결측 배지 분리 — 흔한 결측("데이터 일부 결측", "수급 결측")은
    # 다른(중요) 배지가 있으면 "외 N건"으로 요약. 너무 흔해서 노이즈가 되는 것 방지.
    common_minor = {"데이터 일부 결측", "수급 결측"}
    important = [b for b in badges if b["label"] not in common_minor]
    minor = [b for b in badges if b["label"] in common_minor]
    if important and minor:
        # 중요 배지 + minor는 한 개로 요약
        minor_labels = " · ".join(b["label"] for b in minor)
        result = important + [{"emoji": "📁", "label": f"{minor_labels} 등 (상세 expander)", "cls": "cb-tag", "detail": "수급/기타 데이터 결측 — 상세는 데이터 품질 expander 참고"}]
    elif important:
        result = important
    elif minor:
        result = minor
    else:
        result = []
    if not result:
        result.append({"emoji": "🟢", "label": "데이터 정상", "cls": "cb-tag-good", "detail": "audit·이벤트 매칭 없음"})
    return result


def zero_value_rows_for(code: str, signal_date: str) -> list[dict[str, Any]]:
    """선택 종목·신호일의 audit 행 전체 (expander 상세용)."""
    return load_zero_value_audit().get((str(signal_date)[:10], normalize_code(code)), [])


# === 데이터 품질 배지 (Codex 산출 dashboard_data_quality_badges_*.csv 우선) ===
# 데이터 레이어별 상태 텍스트 → (이모지, css 태그 클래스)
QUALITY_STATUS_STYLE: dict[str, tuple[str, str]] = {
    "정상": ("🟢", "cb-tag-good"),
    "공시 있음": ("📄", "cb-tag-info"),
    "공시 없음": ("·", "cb-tag"),
    "데이터 없음": ("⚪", "cb-tag"),
    "참고용만": ("⚪", "cb-tag"),
    "참고용": ("⚪", "cb-tag"),
    "일부 기간만 있음": ("🟡", "cb-tag"),
    "일부 없음": ("🟡", "cb-tag"),
    "일부 필드 지연": ("🟡", "cb-tag"),
    "지연": ("🟡", "cb-tag"),
    "0값 있음": ("🟡", "cb-tag"),
    "실제 0": ("✅", "cb-tag"),
    "최근 30일 범위 밖": ("·", "cb-tag"),
    "확인 중": ("🟠", "cb-tag-rec"),
    "복구 대상": ("🟠", "cb-tag-rec"),
    "복구 필요": ("🟠", "cb-tag-rec"),
    "확인 필요": ("🔴", "cb-tag-warn"),
    "거래정지 가능": ("🚫", "cb-tag-warn"),
}
# (badge CSV 컬럼, 화면 라벨) — 표시 순서
QUALITY_LAYER_LABELS: list[tuple[str, str]] = [
    ("daily_status", "일봉"),
    ("minute_status", "분봉"),
    ("supply_status", "수급"),
    ("program_status", "프로그램"),
    ("short_sale_status", "공매도"),
    ("dart_status", "DART"),
    ("global_status", "글로벌"),
]
# overall_quality_status → (이모지, css 클래스, 기본 라벨)
QUALITY_OVERALL_STYLE: dict[str, tuple[str, str, str]] = {
    "OK": ("🟢", "cb-tag-good", "데이터 정상"),
    "MISSING_MINOR": ("🟡", "cb-tag", "보조 데이터 일부 없음"),
    "CAUTION": ("🟡", "cb-tag", "주의"),
    "NEEDS_RECOVERY": ("🟠", "cb-tag-rec", "분봉 복구 필요"),
    "NEEDS_STATUS_LOOKUP": ("🔴", "cb-tag-warn", "상태 확인 필요"),
    "NEEDS_REVIEW": ("🔴", "cb-tag-warn", "확인 필요"),
}


@st.cache_data(show_spinner=False)
def load_quality_badges() -> dict[tuple[str, str], dict[str, Any]]:
    """(signal_date, stock_code(6)) → Codex dashboard_data_quality_badges_*.csv 한 행."""
    path = _latest_path(
        RESEARCH_INDEX_DIR,
        "dashboard_data_quality_badges_*.csv",
        RESEARCH_INDEX_DIR / "dashboard_data_quality_badges_20260511.csv",
    )
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for _, row in df.iterrows():
        key = (str(row.get("signal_date", ""))[:10], normalize_code(row.get("stock_code", "")))
        out[key] = row.to_dict()
    return out


@st.cache_data(show_spinner=False)
def load_minute_recovery() -> dict[str, dict[str, Any]]:
    """stock_code(6) → Codex minute_recovery_priority_*.csv 한 행 (분봉 복구 우선순위)."""
    path = _latest_path(
        RESEARCH_INDEX_DIR,
        "minute_recovery_priority_*.csv",
        RESEARCH_INDEX_DIR / "minute_recovery_priority_20260511.csv",
    )
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    out: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        out[normalize_code(row.get("stock_code", ""))] = row.to_dict()
    return out


def quality_badge_row_for(code: str, signal_date: str) -> dict[str, Any]:
    """선택 종목·신호일의 품질 배지 행. 없으면 빈 dict."""
    return load_quality_badges().get((str(signal_date)[:10], normalize_code(code)), {})


def quality_warning_text_for(code: str, signal_date: str) -> str:
    """Codex가 정리한 한글 경고 문구 (분봉 누락 / 상태 확인 등). 없으면 ''."""
    return str(quality_badge_row_for(code, signal_date).get("quality_warning_text", "")).strip()


_RECOVERY_REASON_LABELS = {
    "CODE_MAPPING_ISSUE": "코드 매핑 문제 의심",
    "FILE_MISSING": "분봉 파일 자체 없음",
    "COLLECTION_GAP": "수집 누락 구간",
    "TRADING_HALT_SUSPECTED": "거래정지 의심",
    "PARTIAL_ONLY": "일부 거래일만 수집됨",
}


def render_quality_badge_row(code: str, signal_date: str, *, extra_dates: list[str] | None = None) -> None:
    """종목 상세 상단의 데이터 품질 배지 한 줄.
    Codex dashboard_data_quality_badges_*.csv 가 있으면 그 행(레이어별 상태)을 쓰고,
    없으면 기존 status_badges_for() heuristic 으로 폴백한다.
    """
    code = normalize_code(code)
    row = quality_badge_row_for(code, signal_date)
    if not row:
        badges = status_badges_for(code, signal_date, extra_dates or [])
        badge_html = " ".join(
            f'<span class="cb-tag {b["cls"]}" title="{b["detail"].replace(chr(34), "")}">{b["emoji"]} {b["label"]}</span>'
            for b in badges
        )
        st.markdown(
            '<div class="cb-quality-bar"><span class="cb-key" style="font-size:0.8rem;">데이터 품질</span>'
            f'{badge_html}'
            '<span class="cb-key" style="font-size:0.74rem;">(audit·이벤트 기반 추정 — 정밀 배지 미생성 구간)</span></div>',
            unsafe_allow_html=True,
        )
        return

    overall = str(row.get("overall_quality_status", "")).strip()
    o_emoji, o_cls, o_label = QUALITY_OVERALL_STYLE.get(overall, ("⚪", "cb-tag", overall or "—"))
    head_label = str(row.get("quality_badge_text", "")).strip() or o_label

    chips: list[str] = [f'<span class="cb-tag {o_cls}">{o_emoji} {head_label}</span>']
    for col, label in QUALITY_LAYER_LABELS:
        status = str(row.get(col, "")).strip()
        if not status or status == "공시 없음":
            # 공시 없음/빈값은 한 줄을 짧게 — overall 옆 마이크로 칩으로 생략
            continue
        emoji, cls = QUALITY_STATUS_STYLE.get(status, ("·", "cb-tag"))
        chips.append(f'<span class="cb-tag {cls}" title="{label} 데이터: {status}">{emoji} {label}: {status}</span>')
    ev = str(row.get("stock_status_event", "")).strip()
    if ev and ev != "없음":
        ev_short = ev.split("|")[0].strip()[:48]
        ev_cls = "cb-tag-warn" if ("TRADING_HALT" in ev or "DELISTING" in ev) else "cb-tag"
        chips.append(f'<span class="cb-tag {ev_cls}" title="{ev.replace(chr(34), "")}">🏷 이벤트: {ev_short}</span>')

    st.markdown(
        '<div class="cb-quality-bar"><span class="cb-key" style="font-size:0.8rem;">데이터 품질</span>'
        + " ".join(chips)
        + '</div>',
        unsafe_allow_html=True,
    )

    warn_text = str(row.get("quality_warning_text", "")).strip()
    if warn_text:
        st.markdown(
            '<div class="cb-note" style="border-left-color:#f6ad55; background:rgba(246,173,85,0.10); '
            'padding:0.5rem 0.8rem; margin:0.2rem 0 0.6rem;">⚠️ '
            + warn_text.replace(" / ", "<br>⚠️ ")
            + '</div>',
            unsafe_allow_html=True,
        )

    action = str(row.get("recommended_dashboard_action", ""))
    minute_status = str(row.get("minute_status", "")).strip()
    if "SHOW_MISSING_MINUTE_NOTICE" in action or minute_status in ("복구 대상", "복구 필요", "데이터 없음"):
        rec = load_minute_recovery().get(code)
        if rec:
            reason_raw = str(rec.get("suspected_reason", "")).strip()
            reason = _RECOVERY_REASON_LABELS.get(reason_raw, reason_raw or "원인 미상")
            st.caption(
                f"📊 분봉 복구 우선순위 {rec.get('priority', '?')}순위 · 추정 원인 {reason} · "
                f"누락 {rec.get('missing_sessions', '?')}세션 / 본문·참고 후보 {rec.get('top2_rank3_count', '?')}건 "
                "(Codex minute_recovery_priority)"
            )


@st.cache_data(show_spinner=False)
def load_inst_trade(code: str) -> pd.DataFrame:
    """종목별 일별 외국인/기관 순매수. dt(YYYYMMDD) → datetime 변환."""
    path = INST_TRADE_DIR / f"{normalize_code(code)}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path).copy()
    df["date"] = pd.to_datetime(df["dt"].astype(str), format="%Y%m%d", errors="coerce")
    for col in ["for_daly_nettrde_qty", "orgn_daly_nettrde_qty", "trde_qty"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date")


@st.cache_data(show_spinner=False)
def load_program_per_code(code: str) -> pd.DataFrame:
    """종목별 일별 프로그램 순매수 (금액)."""
    path = PROGRAM_PER_CODE_DIR / f"{normalize_code(code)}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path).copy()
    df["date"] = pd.to_datetime(df["dt"].astype(str), format="%Y%m%d", errors="coerce")
    for col in ["prm_netprps_amt", "prm_netprps_qty"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date")


@st.cache_data(show_spinner=False)
def load_finstate(corp_code: str) -> dict[str, Any]:
    """CIS(포괄손익계산서)에서 매출/영업이익/순이익 3년치 추출."""
    path = latest_finstate_path(corp_code)
    if not path:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    target_ids = {
        "ifrs-full_Revenue": "매출액",
        "dart_OperatingIncomeLoss": "영업이익",
        "ifrs-full_ProfitLoss": "당기순이익",
        "ifrs-full_BasicEarningsLossPerShare": "기본 EPS",
        "ifrs-full_DilutedEarningsLossPerShare": "희석 EPS",
    }
    out: dict[str, Any] = {"_year": data.get("year", ""), "_fs_div": data.get("fs_div", "")}
    for item in data.get("accounts", []):
        if item.get("sj_div") != "CIS":
            continue
        aid = item.get("account_id", "")
        if aid in target_ids and target_ids[aid] not in out:
            out[target_ids[aid]] = {
                "this": item.get("thstrm_amount", ""),
                "prev": item.get("frmtrm_amount", ""),
                "prev2": item.get("bfefrmtrm_amount", ""),
                "this_label": item.get("thstrm_nm", ""),
                "prev_label": item.get("frmtrm_nm", ""),
            }
    return out


@st.cache_data(show_spinner=False)
def compute_signal_day_pct_change(
    code: str, signal_date: str, entry_price: float | None = None
) -> float | None:
    """신호일 당일 등락률 = (15:00 진입가 또는 신호일 종가) ÷ 직전 거래일 종가 - 1.

    Codex active dataset의 d0_pct_change는 D0 등장일(거래량 폭증일) 등락률이지
    신호일(웹훅 발송일) 당일 등락률이 아니라 별도 계산이 필요.
    """
    if not code or not signal_date:
        return None
    daily = load_daily(code)
    if daily.empty:
        return None
    try:
        sig_dt = pd.to_datetime(signal_date).date()
        d = daily.sort_values("date").copy()
        d["_d"] = d["date"].dt.date
        prev = d[d["_d"] < sig_dt]
        if prev.empty:
            return None
        prev_close = float(prev.iloc[-1]["close"])
        if prev_close <= 0:
            return None
        if entry_price is not None and float(entry_price) > 0:
            num = float(entry_price)
        else:
            same = d[d["_d"] == sig_dt]
            if same.empty:
                return None
            num = float(same.iloc[-1]["close"])
            if num <= 0:
                return None
        return (num / prev_close - 1) * 100.0
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(show_spinner=False)
def compute_rsi14(code: str, signal_date: str, period: int = 14) -> float | None:
    """신호일 기준 일봉 close Wilder RSI(14). 표본 부족 시 None."""
    if not code or not signal_date:
        return None
    daily = load_daily(code)
    if daily.empty or len(daily) < period + 1:
        return None
    try:
        sig_dt = pd.to_datetime(signal_date).date()
        d = daily.sort_values("date").copy()
        d["_d"] = d["date"].dt.date
        upto = d[d["_d"] <= sig_dt]
        if len(upto) < period + 1:
            return None
        closes = upto["close"].astype(float)
        delta = closes.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - 100 / (1 + rs)
        last = rsi.iloc[-1]
        return float(last) if pd.notna(last) else None
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(show_spinner=False)
def load_minute(code: str) -> pd.DataFrame:
    path = MINUTE / f"{normalize_code(code)}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path).copy()
    df["dt"] = pd.to_datetime(df["dt"])
    return df


def normalize_code(value: Any) -> str:
    text = str(value or "").strip()
    return text.zfill(6) if text else ""


def role_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return "D0 감시만"
    return ROLE_LABELS.get(text, text)


def policy_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return "판단 보류"
    return POLICY_LABELS.get(text, text.replace("_", " ").title())


def confidence_label(value: Any) -> str:
    text = str(value or "").strip()
    mapping = {
        "LOCAL_DAILY_ONLY": "일봉만 사용 (수급/외인 미반영)",
        "HIGH_PLUS": "매우 높음",
        "HIGH": "높음",
        "MID": "보통",
        "LOW": "낮음",
        "LOW_PLUS": "보통-",
    }
    if not text or text.lower() == "nan":
        return "—"
    return mapping.get(text, text)


def reason_labels(value: Any) -> str:
    parts = [p.strip() for p in str(value or "").replace(";", "|").replace(",", "|").split("|") if p.strip()]
    return "\n".join(f"- {SCORE_REASON_LABELS.get(p, p)}" for p in parts)


def warning_labels(value: Any) -> str:
    parts = [p.strip() for p in str(value or "").replace(";", "|").replace(",", "|").split("|") if p.strip()]
    return "\n".join(f"- {WARNING_LABELS.get(p, p)}" for p in parts) if parts else "특이 경고 없음"


def bool_label(value: Any, positive: str = "도달", negative: str = "미도달") -> str:
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return positive
    if text in {"false", "0", "no", "n"}:
        return negative
    return "미확인"


def order_label(value: Any) -> str:
    mapping = {
        "TARGET3_FIRST": "+3%가 먼저",
        "RISK2_FIRST": "-2%가 먼저",
        "SAME_DAY_ORDER_UNKNOWN": "같은 날 발생, 순서 미확인",
        "TARGET3_ONLY": "+3%만 도달",
        "RISK2_ONLY": "-2%만 터치",
        "NO_TARGET3_OR_RISK2": "+3/-2 모두 없음",
    }
    return mapping.get(str(value or ""), str(value or "미확인"))


def condition_label(value: Any) -> str:
    mapping = {
        "TEMP_USER_APPROVAL_REQUIRED": "임시 조건 - 사용자 승인 전",
        "SIM_LOGIC_MATCH_REVIEW_REQUIRED": "시뮬 로직 반영 - 검증 전",
        "CLASSIC_D0_BROAD_POOL_REVIEW_REQUIRED": "Classic 넓은 D0 풀 - 웹훅 선별 전",
    }
    return mapping.get(str(value or ""), str(value or ""))


def d0_reason_label(value: Any) -> str:
    mapping = {
        "TEMP_60D_HIGH_AND_TRADING_VALUE": "60일 신고가 + 거래대금 조건",
        "TEMP_DRYRUN_NEW_60D_HIGH_AND_TRADING_VALUE_100EOK_PLUS": "60일 신고가 + 거래대금 100억+ (드라이런)",
        "60D_HIGH_AND_TRADING_VALUE": "60일 신고가 + 거래대금 조건",
        "SIMLOGIC_VOLUME_VALUE_TOP200_PCT_COMMON": "거래량·거래대금 200위 교집합 + 등락률 + 보통주",
        "CLASSIC_VOLUME10M_PRICE2K_100K_COMMON": "1,000만주 이상 + 2천~10만원 + 보통주",
    }
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return "—"
    return mapping.get(text, text)


def watch_status_label(value: Any) -> str:
    mapping = {
        "NEW_D0_EVENT": "신규 D0",
        "WATCH_ACTIVE": "감시 중",
        "WATCHING": "감시 중",
        "STALE": "오래됨",
    }
    return mapping.get(str(value or ""), str(value or ""))


def stock_label(row: pd.Series | dict[str, Any]) -> str:
    name = str(row.get("stock_name", "") or "")
    code = normalize_code(row.get("stock_code", ""))
    return f"{name} ({code})" if code else name


def source_label(value: Any) -> str:
    mapping = {
        "webhook_enriched": "오늘의 웹훅 후보",
        "live_safe": "1개월 후보",
        "d0_pool": "D0 감시만",
    }
    return mapping.get(str(value or ""), str(value or ""))


def korean_table(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "stock_name" in out.columns:
        out["stock_label"] = out.apply(stock_label, axis=1)
    if "role" in out.columns:
        out["role"] = out["role"].map(role_label)
    if "policy_decision" in out.columns:
        out["policy_decision"] = out["policy_decision"].map(policy_label)
    if "candidate_policy" in out.columns:
        out["candidate_policy"] = out["candidate_policy"].map(policy_label)
    if "score_reasons" in out.columns:
        out["score_reasons"] = out["score_reasons"].map(reason_labels)
    if "warning_codes" in out.columns:
        out["warning_codes"] = out["warning_codes"].map(warning_labels)
    if "condition_status" in out.columns:
        out["condition_status"] = out["condition_status"].map(condition_label)
    if "d0_reason" in out.columns:
        out["d0_reason"] = out["d0_reason"].map(d0_reason_label)
    if "watch_status" in out.columns:
        out["watch_status"] = out["watch_status"].map(watch_status_label)
    for col in ["outcome_d1_d5_plus1_touch", "outcome_d1_d5_plus2_touch", "outcome_d1_d5_plus3_touch"]:
        if col in out.columns:
            out[col] = out[col].map(lambda value: bool_label(value, "도달", "미도달"))
    if "outcome_d1_d5_minus2_touch" in out.columns:
        out["outcome_d1_d5_minus2_touch"] = out["outcome_d1_d5_minus2_touch"].map(lambda value: bool_label(value, "터치", "미터치"))
    for col in ["outcome_d1_plus1_touch", "outcome_d1_plus2_touch", "outcome_d1_plus3_touch"]:
        if col in out.columns:
            out[col] = out[col].map(lambda value: bool_label(value, "도달", "미도달"))
    if "outcome_d1_minus2_touch" in out.columns:
        out["outcome_d1_minus2_touch"] = out["outcome_d1_minus2_touch"].map(lambda value: bool_label(value, "터치", "미터치"))
    if "target3_vs_risk2_order" in out.columns:
        out["target3_vs_risk2_order"] = out["target3_vs_risk2_order"].map(order_label)
    visible = [col for col in columns if col in out.columns]
    out = out[visible].rename(columns=KOREAN_COLUMNS)
    return out


def show_table(df: pd.DataFrame, columns: list[str], height: int = 360) -> None:
    table = korean_table(df, columns)
    if table.empty:
        st.info("표시할 행이 없습니다.")
        return
    wide_columns = {"종목", "정책판단", "점수근거", "경고", "조건상태", "+3/-2 순서", "결과상태"}
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=height,
        column_config={
            col: st.column_config.TextColumn(col, width="large" if col in wide_columns else "medium")
            for col in table.columns
        },
    )


def numeric(value: Any, default: float | None = None) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return default


def reference_price(info: dict[str, Any]) -> tuple[float | None, str]:
    """차트 기준선을 그릴 가격과 사람이 볼 라벨을 함께 고른다."""
    for key, label in [
        ("signal_price_1500", "15:00 신호가"),
        ("entry_price_1500", "15:00 진입가"),
        ("entry_price_used", "진입가"),
        ("signal_price", "신호가"),
        ("current_price", "현재가 기준"),
        ("d0_price", "D0 기준가"),
        ("d0_close", "D0 종가"),
    ]:
        value = numeric(info.get(key))
        if value and value > 0:
            return value, label
    return None, "기준가"


def latest_file_mtime(path: Path) -> str:
    if not path.exists():
        return "missing"
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def latest_date_from_daily(code: str) -> str:
    df = load_daily(code)
    if df.empty:
        return ""
    return str(df["date"].max().date())


def sent_log_summary() -> dict[str, Any]:
    rows = read_sent_log(str(SENT_LOG))
    by_mode = {"TEST": [], "PROD": []}
    for row in rows:
        mode = str(row.get("webhook_mode") or row.get("mode") or "").upper()
        if mode in by_mode:
            by_mode[mode].append(row)
    prod_sent_today = [
        row
        for row in by_mode["PROD"]
        if row.get("status") == "sent" and str(row.get("created_at", "")).startswith("2026-05-10")
    ]
    latest = rows[-1] if rows else {}
    return {
        "rows": len(rows),
        "latest_status": latest.get("status", "missing"),
        "latest_created_at": latest.get("created_at", ""),
        "test_latest": by_mode["TEST"][-1].get("status", "missing") if by_mode["TEST"] else "missing",
        "prod_latest": by_mode["PROD"][-1].get("status", "missing") if by_mode["PROD"] else "missing",
        "prod_sent_today": bool(prod_sent_today),
        "prod_sent_count_today": len(prod_sent_today),
    }


def selected_universe(enriched: pd.DataFrame, live_safe: pd.DataFrame, d0_pool: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for df, source in [(enriched, "webhook_enriched"), (live_safe, "live_safe"), (d0_pool, "d0_pool")]:
        if df.empty:
            continue
        cols = [col for col in ["rank", "role", "stock_code", "stock_name", "signal_date", "d0_date"] if col in df.columns]
        tmp = df[cols].copy()
        tmp["source"] = source
        frames.append(tmp)
    if not frames:
        return pd.DataFrame(columns=["stock_code", "stock_name", "source"])
    out = pd.concat(frames, ignore_index=True)
    out["stock_code"] = out["stock_code"].map(normalize_code)
    out = out.drop_duplicates(["stock_code", "stock_name"], keep="first")
    return out.sort_values(["source", "stock_code"])


def display_candidates(score: pd.DataFrame, picks: pd.DataFrame) -> pd.DataFrame:
    if score.empty:
        return score
    out = score.copy()
    out["role_label"] = out["role"].map(role_label)
    out["policy_label"] = out["policy_decision"].map(policy_label)
    out["score_reason_label"] = out["score_reasons"].map(reason_labels)
    out["warning_label"] = out["warning_codes"].map(warning_labels)
    if not picks.empty:
        tracked_codes = set(picks["stock_code"].map(normalize_code))
        out["d1_d5_tracking_saved"] = out["stock_code"].map(normalize_code).isin(tracked_codes).map({True: "저장됨", False: "미저장"})
    else:
        out["d1_d5_tracking_saved"] = "미확인"
    return out


def target_dates_for_code(picks: pd.DataFrame, code: str) -> list[pd.Timestamp]:
    if picks.empty or "planned_tracking_dates" not in picks.columns:
        return []
    rows = picks[picks["stock_code"].map(normalize_code) == normalize_code(code)]
    dates: list[pd.Timestamp] = []
    for text in rows["planned_tracking_dates"].tolist():
        for part in str(text).split("|"):
            if part.strip():
                dates.append(pd.to_datetime(part.strip()))
    return dates


def trading_days_after(code: str, signal_date: str, count: int = 5) -> list[pd.Timestamp]:
    df = load_daily(code)
    if df.empty:
        return []
    signal = pd.to_datetime(signal_date)
    future = df[df["date"] > signal]["date"].head(count).tolist()
    return [pd.to_datetime(value) for value in future]


def is_truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def slot_key_for_row(rank_value: Any, role_value: Any) -> str | None:
    """live_safe row의 rank+role을 5종목 슬롯 key로 매핑."""
    try:
        rank_int = int(str(rank_value).strip())
    except Exception:
        return None
    role_text = str(role_value or "").strip()
    for key, rank, role, _label, _cls in SLOT_DEFINITIONS:
        if rank_int == rank and role_text == role:
            return key
    return None


def slot_outcome_color(review_row: dict[str, Any] | None) -> tuple[str, str, str]:
    """review row → (이모지 점, 한글 요약, css 클래스)."""
    if not review_row:
        return "⚪", "결과 없음", "cb-result-none"
    plus3 = is_truthy(review_row.get("outcome_d1_d5_plus3_touch"))
    plus2 = is_truthy(review_row.get("outcome_d1_d5_plus2_touch"))
    plus1 = is_truthy(review_row.get("outcome_d1_d5_plus1_touch"))
    minus2 = is_truthy(review_row.get("outcome_d1_d5_minus2_touch"))
    order = str(review_row.get("target3_vs_risk2_order", "") or "").strip()
    if plus3 and minus2:
        if order == "TARGET3_FIRST":
            return "🟢", "+3% 먼저 도달", "cb-result-good"
        if order == "RISK2_FIRST":
            return "🔴", "-2% 먼저 터치", "cb-result-bad"
        return "🟡", "+3/-2 같은 날", "cb-result-mixed"
    if plus3:
        return "🟢", "+3% 도달", "cb-result-good"
    if minus2:
        return "🔴", "-2% 터치", "cb-result-bad"
    if plus2 or plus1:
        return "🟡", ("+2% 까지" if plus2 else "+1% 까지"), "cb-result-mixed"
    return "⚪", "미도달", "cb-result-none"


@st.cache_data(show_spinner=False)
def build_review_index(review_csv_text: str) -> dict[str, dict[str, dict[str, Any]]]:
    """signal_date → stock_code → review row dict.
    인자는 캐시 키 안정성 위해 path text. 매번 read_csv 캐시는 따로 작동."""
    review = read_csv(review_csv_text)
    out: dict[str, dict[str, dict[str, Any]]] = {}
    if review.empty:
        return out
    for _, row in review.iterrows():
        sd = str(row.get("signal_date", ""))
        code = normalize_code(row.get("stock_code", ""))
        out.setdefault(sd, {})[code] = row.to_dict()
    return out


def write_user_note_atomic(path: Path, df: pd.DataFrame) -> None:
    """메모 CSV를 안전하게 저장: tmp 파일 작성 후 atomic rename + 백업 1개 유지."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        try:
            backup.write_bytes(path.read_bytes())
        except Exception:
            pass  # 백업 실패해도 본 저장은 진행
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8-sig")
    tmp.replace(path)


def upsert_user_note(notes_path: Path, payload: dict[str, Any]) -> pd.DataFrame:
    """signal_date+stock_code 기준 upsert. 기존 행이 있으면 갱신, 없으면 신규."""
    columns = [
        "review_date", "signal_date", "stock_code", "stock_name", "rank", "role",
        "user_view_before_result", "user_view_after_result", "pattern_note",
        "mistake_note", "next_rule_idea", "confidence_by_user",
        "created_at", "updated_at",
    ]
    if notes_path.exists():
        df = pd.read_csv(notes_path, dtype=str, encoding="utf-8-sig").fillna("")
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
    else:
        df = pd.DataFrame(columns=columns)
    now_iso = datetime.now().isoformat(timespec="seconds")
    sd = str(payload.get("signal_date", ""))
    code = normalize_code(payload.get("stock_code", ""))
    mask = (df["signal_date"].astype(str) == sd) & (df["stock_code"].map(normalize_code) == code)
    if mask.any():
        for k, v in payload.items():
            if k in df.columns:
                df.loc[mask, k] = "" if v is None else str(v)
        df.loc[mask, "updated_at"] = now_iso
    else:
        new_row = {col: "" for col in columns}
        new_row.update({k: ("" if v is None else str(v)) for k, v in payload.items() if k in columns})
        new_row["stock_code"] = code
        new_row["created_at"] = now_iso
        new_row["updated_at"] = now_iso
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    write_user_note_atomic(notes_path, df)
    read_csv.clear()  # 캐시 무효화 → 다음 렌더에서 최신 메모 표시
    return df


def delete_user_note(notes_path: Path, signal_date: str, stock_code: str) -> pd.DataFrame:
    if not notes_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(notes_path, dtype=str, encoding="utf-8-sig").fillna("")
    code = normalize_code(stock_code)
    df = df[~((df["signal_date"].astype(str) == str(signal_date)) & (df["stock_code"].map(normalize_code) == code))]
    write_user_note_atomic(notes_path, df)
    read_csv.clear()
    return df


def date_navigator(dates: list[str], key_prefix: str) -> str:
    if not dates:
        return ""
    asc = sorted(set(str(d) for d in dates if str(d)))
    current_key = f"{key_prefix}_date"
    select_key = f"{key_prefix}_select"
    if current_key not in st.session_state or st.session_state[current_key] not in asc:
        st.session_state[current_key] = asc[-1]
    if select_key not in st.session_state or st.session_state[select_key] not in asc:
        st.session_state[select_key] = st.session_state[current_key]
    idx = asc.index(st.session_state[current_key])
    nav_cols = st.columns([1.2, 1.2, 2.5, 5.0])
    with nav_cols[0]:
        if st.button("이전 거래일", key=f"{key_prefix}_prev", disabled=idx == 0, use_container_width=True):
            st.session_state[current_key] = asc[max(0, idx - 1)]
            st.session_state[select_key] = st.session_state[current_key]
            idx = asc.index(st.session_state[current_key])
    with nav_cols[1]:
        if st.button("다음 거래일", key=f"{key_prefix}_next", disabled=idx == len(asc) - 1, use_container_width=True):
            st.session_state[current_key] = asc[min(len(asc) - 1, idx + 1)]
            st.session_state[select_key] = st.session_state[current_key]
            idx = asc.index(st.session_state[current_key])
    with nav_cols[2]:
        order = st.radio("정렬", ["최신순", "과거순"], horizontal=True, key=f"{key_prefix}_order")
    ordered = list(reversed(asc)) if order == "최신순" else asc
    selected = st.selectbox("날짜", ordered, index=ordered.index(st.session_state[current_key]), key=select_key)
    st.session_state[current_key] = selected
    return selected


def build_minute_windows(code: str, signal_date: str) -> list[dict[str, Any]]:
    signal = pd.to_datetime(signal_date).date()
    future_dates = trading_days_after(code, signal_date, 5)
    windows: list[dict[str, Any]] = [
        {
            "label": "당일 09:00~15:30",
            "dates": [pd.Timestamp(signal)],
            "start": time(9, 0),
            "end": time(15, 30),
            "scope": "intraday_full",
        },
        {
            "label": "당일 14:15~15:30",
            "dates": [pd.Timestamp(signal)],
            "start": time(14, 15),
            "end": time(15, 30),
            "scope": "intraday",
        },
    ]
    for idx, date_value in enumerate(future_dates, start=1):
        windows.append(
            {
                "label": f"D+{idx} 정규장",
                "dates": [date_value],
                "start": time(9, 0),
                "end": time(15, 30),
                "scope": "daily_review",
            }
        )
    windows.append(
        {
            "label": "D+1~D+5 전체",
            "dates": future_dates,
            "start": time(9, 0),
            "end": time(15, 30),
            "scope": "five_day_review",
        }
    )
    # 웹훅일+D+1~D+5 = D0~D+5 통합 흐름 (Codex 2026-05-18 권장 기본 보기)
    windows.append(
        {
            "label": "웹훅일+D+1~D+5 전체",
            "dates": [pd.Timestamp(signal)] + future_dates,
            "start": time(9, 0),
            "end": time(15, 30),
            "scope": "six_day_review",
        }
    )
    return windows


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["trade_date"] = out["dt"].dt.date
    out["turnover"] = out["close"] * out["volume"]
    out["cum_turnover"] = out.groupby("trade_date")["turnover"].cumsum()
    out["cum_volume"] = out.groupby("trade_date")["volume"].cumsum().replace(0, pd.NA)
    out["vwap"] = out["cum_turnover"] / out["cum_volume"]
    return out


def resample_minutes(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    if df.empty:
        return df
    chunks = []
    for _, day in df.groupby(df["dt"].dt.date):
        resampled = (
            day.set_index("dt")
            .resample(f"{minutes}min")
            .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum", "vwap": "last"})
            .dropna(subset=["open", "high", "low", "close"])
            .reset_index()
        )
        chunks.append(resampled)
    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()


def minute_window_data(df: pd.DataFrame, window: dict[str, Any], minutes: int) -> pd.DataFrame:
    if df.empty or not window.get("dates"):
        return pd.DataFrame()
    dates = {pd.to_datetime(value).date() for value in window["dates"]}
    day = df[df["dt"].dt.date.isin(dates)].copy()
    if day.empty:
        return day
    day = add_vwap(day)
    day = day[(day["dt"].dt.time >= window["start"]) & (day["dt"].dt.time <= window["end"])].copy()
    return resample_minutes(day, minutes)


def add_vertical_marker(fig: Any, x_value: Any, label: str, color: str) -> None:
    # Plotly's add_vline annotation path is brittle with recent pandas timestamp objects.
    fig.add_shape(
        type="line",
        x0=x_value,
        x1=x_value,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line={"color": color, "width": 1, "dash": "dash"},
    )
    fig.add_annotation(
        x=x_value,
        y=1,
        xref="x",
        yref="paper",
        text=label,
        showarrow=False,
        yanchor="bottom",
        font={"size": 11, "color": color},
    )


def _apply_light_chart_layout(fig, *, height: int = 480, legend_y: float = 1.10, top_margin: int = 70) -> None:
    """차트 공통 layout — light 테마 통일, legend·margin·grid 일관성 (2026-05-16 polish).

    - template: plotly_white (대시보드 light 테마와 일치)
    - margin top 충분히 확보(70+)해서 legend/annotation 겹침/짤림 방지
    - legend y=1.10 위치로 헤더와 분리
    - grid color, font size 통일
    """
    fig.update_layout(
        height=height,
        xaxis_rangeslider_visible=False,
        margin={"l": 16, "r": 16, "t": top_margin, "b": 28},
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"size": 12, "color": "#0f172a", "family": "Malgun Gothic, Apple SD Gothic Neo, sans-serif"},
        legend={
            "orientation": "h",
            "yanchor": "bottom", "y": legend_y,
            "xanchor": "right", "x": 1,
            "font": {"size": 11},
            "bgcolor": "rgba(255,255,255,0.85)",
            "bordercolor": "#e5e7eb",
            "borderwidth": 1,
        },
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7", linecolor="#cbd5e1", tickfont={"size": 11}, tickformat="%Y.%m.%d")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7", linecolor="#cbd5e1", tickfont={"size": 11})


def plot_daily_chart(df: pd.DataFrame, info: dict[str, Any], target_dates: list[pd.Timestamp]) -> None:
    if df.empty:
        st.warning("일봉 parquet 파일이 없습니다.")
        return
    signal_date = pd.to_datetime(info.get("signal_date") or df["date"].max())
    start = signal_date - pd.Timedelta(days=260)
    view = df[df["date"] >= start].copy()
    signal_price, signal_label = reference_price(info)

    if go and make_subplots:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.04)
        fig.add_trace(
            go.Candlestick(
                x=view["date"],
                open=view["open"],
                high=view["high"],
                low=view["low"],
                close=view["close"],
                name="OHLC",
            ),
            row=1,
            col=1,
        )
        for window in MA_WINDOWS:
            fig.add_trace(
                go.Scatter(x=view["date"], y=view[f"ma{window}"], mode="lines", name=f"MA{window}", line={"width": 1}),
                row=1,
                col=1,
            )
        fig.add_trace(go.Bar(x=view["date"], y=view["volume"], name="거래량", marker_color="#8a8f98"), row=2, col=1)
        if signal_price:
            for pct, label, color in [(0, signal_label, "#111827"), (0.01, "+1%", "#2f855a"), (0.02, "+2%", "#2b6cb0"), (0.03, "+3%", "#6b46c1"), (-0.02, "-2%", "#c53030")]:
                fig.add_hline(y=signal_price * (1 + pct), line_dash="dot", line_color=color, annotation_text=label, row=1, col=1)
        for marker_date, label, color in [
            (info.get("d0_date"), "D0", "#dd6b20"),
            (info.get("signal_date"), "웹훅일", "#2b6cb0"),
        ]:
            if marker_date:
                add_vertical_marker(fig, str(pd.to_datetime(marker_date).date()), label, color)
        for idx, date_value in enumerate(target_dates, start=1):
            add_vertical_marker(fig, str(date_value.date()), f"D+{idx}", "#718096")
        _apply_light_chart_layout(fig, height=620, legend_y=1.06, top_margin=60)
        # 가격축 auto-zoom — 0부터 시작 방지
        try:
            prices = pd.concat([view["high"], view["low"], view["close"]]).dropna()
            prices = prices[prices > 0]
            if not prices.empty:
                y_lo = float(prices.min()) * 0.97
                y_hi = float(prices.max()) * 1.03
                if y_hi > y_lo:
                    fig.update_yaxes(range=[y_lo, y_hi], row=1, col=1)
        except Exception:  # noqa: BLE001
            pass
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    else:
        chart_cols = ["close"] + [f"ma{w}" for w in MA_WINDOWS]
        st.line_chart(view.set_index("date")[chart_cols])
        st.bar_chart(view.set_index("date")["volume"])


def plot_minute_chart(
    df: pd.DataFrame,
    info: dict[str, Any],
    key_prefix: str = "minute",
    *,
    show_window_selector: bool = True,
) -> None:
    if df.empty:
        st.warning("로컬 data/market/minute_ohlcv에 이 종목 분봉 파일이 없습니다. 일봉 결과와 메모는 볼 수 있지만 분봉 복기는 데이터 갱신/수집 뒤에 가능합니다.")
        return
    signal_date = pd.to_datetime(info.get("signal_date") or df["dt"].max().date()).date()
    code = normalize_code(info.get("stock_code", ""))
    windows = build_minute_windows(code, str(signal_date))
    window_labels = [item["label"] for item in windows]
    # 기본 보기: 웹훅일+D+1~D+5 전체 (D0~D+5 흐름) — Codex 2026-05-18 권장.
    # fallback: D+1~D+5 전체 → 첫 옵션
    default_window = next(
        (lbl for lbl in ("웹훅일+D+1~D+5 전체", "D+1~D+5 전체") if lbl in window_labels),
        window_labels[0],
    )
    window_key = f"{key_prefix}_window"
    if window_key not in st.session_state or st.session_state[window_key] not in window_labels:
        st.session_state[window_key] = default_window
    interval_key = f"{key_prefix}_interval_30default"
    if interval_key not in st.session_state:
        st.session_state[interval_key] = "30분"
    rule_key = f"{key_prefix}_rule"
    if rule_key not in st.session_state:
        st.session_state[rule_key] = "기본"
    if show_window_selector:
        control_cols = st.columns([2.0, 1.4, 2.6])
        with control_cols[0]:
            window_label = st.selectbox("분봉 기간", window_labels, key=window_key)
        with control_cols[1]:
            interval_label = st.radio("분봉 단위", ["5분", "15분", "30분"], index=2, horizontal=True, key=interval_key)
        with control_cols[2]:
            rule_label = st.radio(
                "자동감시 룰",
                ["기본", "기대형", "보수형", "소익절형"],
                horizontal=True, key=rule_key,
                help="기본 = 계좌 ±1/±2/±3. 룰 선택 시 해당 룰의 목표·발동·보전·손절 라인만 강조 표시.",
            )
    else:
        # 종목 상세: 기간 selectbox 숨김. 항상 웹훅일+D+1~D+5 전체로 고정 (사용자 2026-05-18 피드백)
        st.session_state[window_key] = default_window
        window_label = default_window
        control_cols = st.columns([1.4, 2.6])
        with control_cols[0]:
            interval_label = st.radio("분봉 단위", ["5분", "15분", "30분"], index=2, horizontal=True, key=interval_key)
        with control_cols[1]:
            rule_label = st.radio(
                "자동감시 룰",
                ["기본", "기대형", "보수형", "소익절형"],
                horizontal=True, key=rule_key,
                help="기본 = 계좌 ±1/±2/±3. 룰 선택 시 해당 룰의 목표·발동·보전·손절 라인만 강조 표시.",
            )
    minutes = {"5분": 5, "15분": 15, "30분": 30}[interval_label]
    window = next(item for item in windows if item["label"] == window_label)
    if window["scope"] == "five_day_review" and minutes == 5:
        st.caption("D+1~D+5 전체는 5분봉도 가능하지만 길어질 수 있습니다. 흐름만 빠르게 볼 때는 15분/30분봉이 더 편합니다.")
    # D0/D+1~D+5 거래일 매핑 — 차트의 D+N 캔들이 어떤 날짜인지 한 줄로 표시
    # 분봉 결손/미래/오늘 표시도 함께 — "어떤 D+N 슬롯이 비어 있는지" 즉시 보이게.
    if window["scope"] in ("six_day_review", "five_day_review") and show_window_selector is False:
        try:
            _weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
            _today = pd.Timestamp.today().normalize()
            _d0_ts = pd.Timestamp(signal_date)
            # 종목 분봉 parquet에 실제로 존재하는 거래일 set (분봉 결손 판별)
            _present_days: set = set()
            try:
                _present_days = {d.date() for d in pd.to_datetime(df["dt"]).dt.normalize().unique()}
            except Exception:  # noqa: BLE001
                _present_days = set()
            _missing_slots: list[str] = []
            def _date_tag(ts: pd.Timestamp, label: str) -> str:
                wd = _weekday_kr[ts.weekday()]
                if ts.normalize() > _today:
                    tail = " · 미래"
                elif ts.normalize() == _today:
                    tail = " · 오늘"
                elif _present_days and ts.date() not in _present_days:
                    tail = " · ⚠️결손"
                    _missing_slots.append(f"{label}({ts.strftime('%m-%d')})")
                else:
                    tail = ""
                return f"**{label}** {ts.strftime('%m-%d')}({wd}){tail}"
            parts = [_date_tag(_d0_ts, "D0")]
            for _idx, _dt in enumerate(trading_days_after(code, str(signal_date), 5), start=1):
                parts.append(_date_tag(pd.Timestamp(_dt), f"D+{_idx}"))
            st.caption("📅 거래일 매핑: " + " · ".join(parts))
            if _missing_slots:
                st.warning(
                    f"⚠️ 분봉 결손 슬롯: {' · '.join(_missing_slots)} — "
                    "해당 거래일은 종목 분봉 parquet에 없습니다 (수집 실패 / 거래정지 / 시장조치 가능성). "
                    "다른 거래일 분봉은 그대로 표시되며, 차트의 x축에서는 결손일 자동 압축됩니다."
                )
        except Exception:  # noqa: BLE001
            pass
    view = minute_window_data(df, window, minutes)
    signal_price, signal_label = reference_price(info)
    if view.empty:
        if window["scope"] == "five_day_review":
            st.info("해당 종목의 D+1~D+5 분봉이 아직 없거나, 선택 날짜 이후 데이터가 부족합니다.")
        else:
            st.info(f"{window_label} 구간의 분봉 데이터가 없습니다. 휴장일, 미래 추적일, 또는 parquet 미보유 상태일 수 있습니다.")
        return

    if not show_window_selector and window["scope"] in ("six_day_review", "five_day_review"):
        try:
            future_dates_for_labels = trading_days_after(code, str(signal_date), 5)
            loaded_parts = []
            for expected_date in window.get("dates", []):
                day = pd.to_datetime(expected_date).date()
                raw_day = df[df["dt"].dt.date.eq(day)]
                future_idx = next(
                    (idx for idx, fd in enumerate(future_dates_for_labels, start=1) if fd.date() == day),
                    None,
                )
                day_label = "D0" if day == signal_date else f"D+{future_idx or '?'}"
                if raw_day.empty:
                    loaded_parts.append(f"{day_label} {pd.Timestamp(day).strftime('%m.%d')} 없음")
                    continue
                loaded_parts.append(
                    f"{day_label} {pd.Timestamp(day).strftime('%m.%d')} "
                    f"{len(raw_day):,}행({raw_day['dt'].min().strftime('%H:%M')}~{raw_day['dt'].max().strftime('%H:%M')})"
                )
            if loaded_parts:
                st.caption("분봉 로드 현황: " + " · ".join(loaded_parts))
        except Exception:  # noqa: BLE001
            pass

    if go and make_subplots:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.04)
        fig.add_trace(
            go.Candlestick(
                x=view["dt"],
                open=view["open"],
                high=view["high"],
                low=view["low"],
                close=view["close"],
                name=f"{interval_label}봉",
            ),
            row=1,
            col=1,
        )
        # VWAP 표시 옵션 (사용자 토글, 기본 OFF — 분봉 차트가 복잡해지는 것 방지)
        show_vwap_key = f"{key_prefix}_show_vwap"
        if show_vwap_key not in st.session_state:
            st.session_state[show_vwap_key] = False
        show_vwap = st.session_state.get(show_vwap_key, False)
        if show_vwap and "vwap" in view.columns:
            fig.add_trace(go.Scatter(x=view["dt"], y=view["vwap"], mode="lines", name="VWAP", line={"width": 2}), row=1, col=1)
        fig.add_trace(go.Bar(x=view["dt"], y=view["volume"], name="거래량", marker_color="#8a8f98"), row=2, col=1)
        if signal_price:
            # 계좌 체감 기준 라인 — 매수 직후 슬리피지 약 -0.3% 보정.
            # raw 변환: 계좌 +N% → 진입가 * (1 + (N+0.3)/100), 계좌 -N% → 진입가 * (1 - (N-0.3)/100)
            #   즉 계좌 +1 → raw +1.3, 계좌 -1 → raw -0.7
            base_lines = [
                (0.000, signal_label, "#111827", "dot"),
                (+0.013, "+1%", "#16a34a", "dot"),
                (+0.023, "+2%", "#16a34a", "dot"),
                (+0.033, "+3%", "#15803d", "dot"),
                (-0.007, "-1%", "#dc2626", "dot"),
                (-0.017, "-2%", "#dc2626", "dot"),
                (-0.027, "-3%", "#991b1b", "dot"),
            ]
            # 자동감시 룰 별 라인 (목표/발동/보전/손절). 굵은 dash로 강조.
            rule_lines_by_name: dict[str, list] = {
                "기본": [],
                "기대형": [
                    (+0.043, "목표 +4", "#15803d", "dash"),
                    (+0.023, "보전 +2", "#16a34a", "dash"),
                    (-0.027, "손절 -3", "#991b1b", "dash"),
                ],
                "보수형": [
                    (+0.033, "목표 +3", "#15803d", "dash"),
                    (+0.013, "발동 +1", "#22c55e", "dash"),
                    (+0.008, "보전 +0.5", "#84cc16", "dash"),
                    (-0.027, "손절 -3", "#991b1b", "dash"),
                ],
                "소익절형": [
                    (+0.023, "목표 +2", "#15803d", "dash"),
                    (+0.013, "발동 +1", "#22c55e", "dash"),
                    (+0.008, "보전 +0.5", "#84cc16", "dash"),
                    (-0.027, "손절 -3", "#991b1b", "dash"),
                ],
            }
            rule_lines = rule_lines_by_name.get(rule_label, [])
            # 룰 선택 시: 기본 ±1/±2/±3은 흐릿하게 보이도록 색 옅게, 룰 라인은 굵은 dash로 강조.
            if rule_lines:
                base_lines = [(p, l, "#cbd5e0", "dot") if l != signal_label else (p, l, "#111827", "dot") for p, l, _, _ in base_lines]
            for raw_pct, label, color, dash in base_lines + rule_lines:
                width = 2.2 if dash == "dash" else 1
                fig.add_hline(
                    y=signal_price * (1 + raw_pct),
                    line_dash=dash,
                    line_color=color,
                    line_width=width,
                    annotation_text=label,
                    annotation_position="right",
                    row=1, col=1,
                )
        if window["scope"] == "intraday":
            add_vertical_marker(fig, pd.Timestamp.combine(signal_date, time(15, 0)).isoformat(), "15:00", "#2b6cb0")
        # D0 마커 — 웹훅일+D+1~D+5 모드일 때만 (D0 캔들 위치 시각화)
        if window["scope"] == "six_day_review":
            add_vertical_marker(
                fig, pd.Timestamp.combine(signal_date, time(9, 0)).isoformat(),
                "D0", "#f97316",
            )
        for idx, date_value in enumerate(trading_days_after(code, str(signal_date), 5), start=1):
            if date_value.date() in {pd.to_datetime(value).date() for value in window.get("dates", [])}:
                add_vertical_marker(fig, pd.Timestamp.combine(date_value.date(), time(9, 0)).isoformat(), f"D+{idx}", "#718096")
        _apply_light_chart_layout(fig, height=560, legend_y=1.08, top_margin=60)
        # 가격축 auto-zoom
        try:
            prices = pd.concat([view["high"], view["low"], view["close"]]).dropna()
            prices = prices[prices > 0]
            if not prices.empty:
                y_lo = float(prices.min()) * 0.97
                y_hi = float(prices.max()) * 1.03
                if y_hi > y_lo:
                    fig.update_yaxes(range=[y_lo, y_hi], row=1, col=1)
        except Exception:  # noqa: BLE001
            pass
        # 분봉 휴장일/주말/장 외 시간 압축 — 결손 일자도 자동 감지해서 압축
        rangebreaks = [
            dict(bounds=["sat", "mon"]),
            dict(bounds=[15.5, 9], pattern="hour"),
        ]
        try:
            present_days = sorted({d.date() for d in pd.to_datetime(view["dt"]).dt.normalize().unique()})
            if len(present_days) >= 2:
                from datetime import timedelta as _td
                cur = present_days[0]
                missing: list[str] = []
                while cur <= present_days[-1]:
                    if cur.weekday() < 5 and cur not in present_days:
                        missing.append(cur.strftime("%Y-%m-%d"))
                    cur = cur + _td(days=1)
                if missing:
                    rangebreaks.append(dict(values=missing))
        except Exception:  # noqa: BLE001
            pass
        fig.update_xaxes(rangebreaks=rangebreaks, row=1, col=1)
        fig.update_xaxes(rangebreaks=rangebreaks, row=2, col=1)
        # 한국식 날짜 표기 (분봉: 월/일 시:분, 슬래시로 시간 구분과 명확히 분리)
        fig.update_xaxes(tickformat="%m/%d %H:%M", row=2, col=1)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        # 계좌/raw 라인 표시 정책 안내 (Codex 2026-05-18 압축파일 시뮬 결과 반영)
        ref_text = (
            f"**기준가**: {signal_price:,.0f}원 ({signal_label} · 신호일 15시 진입가)"
            if signal_price else "**기준가**: — (entry_price 미감지)"
        )
        st.caption(
            f"{ref_text} · 라인은 **계좌 체감 기준** ±1/±2/±3%. "
            "매수 직후 슬리피지 약 -0.3%를 반영해 내부 raw +1.3/+2.3/+3.3, -0.7/-1.7/-2.7로 계산합니다."
        )
        # VWAP 토글 (차트 아래 작은 옵션)
        st.checkbox(
            "VWAP 라인 표시",
            value=show_vwap,
            key=show_vwap_key,
            help="장중 누적 거래량 가중 평균가. 체크하면 차트에 주황선이 그려집니다.",
        )
    else:
        st.line_chart(view.set_index("dt")[["close", "vwap"]])
        st.bar_chart(view.set_index("dt")["volume"])


def plot_one_year_minute_chart(
    df: pd.DataFrame,
    info: dict[str, Any],
    review_row: dict[str, Any] | None,
    *,
    show_outcome: bool,
    key_prefix: str,
) -> None:
    """1년치 복기 전용 분봉 차트.
    - 기간 토글: 웹훅일+D+1~D+5 / 웹훅 당일 / D+1~D+5 / D+1 / ...
    - 결과 표시 토글이 켜지면 차트 우상단에 결과 오버레이 박스
    - D+ 수직 라벨 + 기준가 대비 +1/+2/+3/-2% 수평선
    """
    if df.empty:
        st.warning("로컬 data/market/minute_ohlcv에 이 종목 분봉 파일이 없습니다. 일봉 결과와 메모는 볼 수 있지만 분봉 복기는 데이터 갱신/수집 뒤에 가능합니다.")
        return
    signal_date = pd.to_datetime(info.get("signal_date") or df["dt"].max().date()).date()
    code = normalize_code(info.get("stock_code", ""))
    future_dates = trading_days_after(code, str(signal_date), 5)
    signal_ts = pd.Timestamp(signal_date)
    all_review_dates = [signal_ts] + future_dates

    # 윈도우 정의: 분봉 화면 전용 ('D+1~D+5' 통합 + 일별)
    windows: list[dict[str, Any]] = [
        {"label": "웹훅일+D+1~D+5 전체", "dates": all_review_dates, "scope": "six_day_review"},
        {"label": "웹훅 당일", "dates": [signal_ts], "scope": "webhook_day"},
        {"label": "D+1~D+5 전체", "dates": future_dates, "scope": "five_day_review"},
    ]
    for idx, date_value in enumerate(future_dates, start=1):
        windows.append({"label": f"D+{idx}", "dates": [date_value], "scope": "daily_review"})

    window_labels = [item["label"] for item in windows]
    window_key = f"{key_prefix}_window"
    if window_key not in st.session_state or st.session_state[window_key] not in window_labels:
        st.session_state[window_key] = window_labels[0]

    # 차트 상단 컨트롤: 분봉 단위 + 기간 토글 + 자동감시 룰 토글
    control_cols = st.columns([1.4, 3.4, 2.6])
    with control_cols[0]:
        interval_key = f"{key_prefix}_interval_30default"
        if interval_key not in st.session_state:
            st.session_state[interval_key] = "30분"
        interval_label = st.radio("분봉", ["5분", "15분", "30분"], index=2, horizontal=True, key=interval_key, label_visibility="collapsed")
    with control_cols[1]:
        window_label = st.radio("기간", window_labels, horizontal=True, key=window_key, label_visibility="collapsed")
    with control_cols[2]:
        rule_key = f"{key_prefix}_rule"
        if rule_key not in st.session_state:
            st.session_state[rule_key] = "기본"
        rule_label = st.radio(
            "자동감시 룰",
            ["기본", "기대형", "보수형", "소익절형"],
            horizontal=True, key=rule_key, label_visibility="collapsed",
            help="기본 = 계좌 ±1/±2/±3. 룰 선택 시 해당 룰의 목표·발동·보전·손절 라인 강조.",
        )
    minutes = {"5분": 5, "15분": 15, "30분": 30}[interval_label]
    window = next(item for item in windows if item["label"] == window_label)

    # 데이터 추출
    window_full = {"label": window["label"], "dates": window["dates"], "scope": window["scope"], "start": time(9, 0), "end": time(15, 30)}
    view = minute_window_data(df, window_full, minutes)
    signal_price, signal_label = reference_price(info)

    if view.empty:
        # 데이터 품질 안내 박스 — 단순 미수집인지, 거래정지/시장조치인지 구분
        code_l = normalize_code(info.get("stock_code", ""))
        sd = str(info.get("signal_date", ""))[:10]
        future_iso = [d.isoformat() for d in trading_days_after(code_l, sd, 5)] if code_l else []
        events = [e for e in load_status_events().get(code_l, []) if _event_in_range(e, sd, future_iso)]
        audit_rows = zero_value_rows_for(code_l, sd)
        minute_audit = [r for r in audit_rows if "minute" in str(r.get("data_layer", "")).lower()]
        halt_em = " <b style='color:#ff8a8a;'>⚠️ (이력 있음)</b>" if any(str(e.get("event_type", "")) in ("TRADING_HALT", "DELISTING_RELATED") for e in events) else ""
        mapping_em = " <b style='color:#ffd166;'>⚠️ (의심)</b>" if any("CODE_MAPPING" in str(r.get("zero_or_missing_type", "")) for r in minute_audit) else ""
        ev_names = " / ".join(sorted(set(str(e.get("event_name", "")) for e in events if e.get("event_name"))))
        st.markdown(
            '<div class="cb-note" style="border-left-color:#a0aec0; background:rgba(160,174,192,0.10);">'
            f'📊 <b>분봉 데이터 없음</b> — {window_label}<br>'
            f'<span class="cb-subtle">가능한 이유: 미수집 / 거래정지·시장조치{halt_em} / 코드 매핑 문제{mapping_em} / 수집 실패</span>'
            + (f'<br><span class="cb-subtle">관련 이벤트: {ev_names}</span>' if ev_names else '')
            + '<br><span class="cb-subtle">+3%와 -2%의 선후관계(어느 게 먼저 닿았는지)는 분봉으로 확정할 수 없습니다. 일봉 기준 결과는 REVIEW 패널에 그대로 표시됩니다.</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    compact_axis = window["scope"] in {"five_day_review", "six_day_review"}
    plot_view = view.copy()
    x_axis_title = ""
    day_slot_width = 430
    compact_day_index: dict[Any, int] = {}
    if compact_axis:
        compact_dates = [pd.to_datetime(d).date() for d in window["dates"] if pd.to_datetime(d).date() in set(plot_view["dt"].dt.date)]
        if not compact_dates:
            compact_dates = sorted(plot_view["dt"].dt.date.unique().tolist())
        compact_day_index = {day: idx for idx, day in enumerate(compact_dates)}
        plot_view["_plot_x"] = plot_view["dt"].map(
            lambda value: compact_day_index[value.date()] * day_slot_width
            + (value.hour * 60 + value.minute - 9 * 60)
        )
        plot_view["_hover_dt"] = plot_view["dt"].dt.strftime("%Y-%m-%d %H:%M")
        x_axis_title = "거래일별 압축 축"
    else:
        plot_view["_plot_x"] = plot_view["dt"]
        plot_view["_hover_dt"] = plot_view["dt"].dt.strftime("%Y-%m-%d %H:%M")

    # 분봉 누락 거래일 진단 — 통합 보기에서 일부 거래일이 빠졌으면 알려줌
    if window["scope"] in {"five_day_review", "six_day_review"} and window["dates"]:
        actual_dates = {d for d in view["dt"].dt.date.unique()}
        missing = [pd.to_datetime(d) for d in window["dates"] if pd.to_datetime(d).date() not in actual_dates]
        if missing:
            missing_text = ", ".join(
                ("웹훅일 " if d.date() == signal_date else f"D+{next((i for i, fd in enumerate(future_dates, start=1) if fd.date() == d.date()), '?')} ")
                + d.strftime("%m.%d")
                for d in missing
            )
            st.caption(f"⚠️ 분봉 데이터가 없는 거래일: {missing_text} — 해당 거래일 캔들이 비어 있습니다.")
        if not view["dt"].dt.date.unique().tolist():
            st.warning("선택한 복기 구간의 분봉이 전혀 로드되지 않았습니다. 종목 분봉 parquet 파일을 확인하세요.")
            return

    if not (go and make_subplots):
        st.line_chart(view.set_index("dt")[["close", "vwap"]])
        st.bar_chart(view.set_index("dt")["volume"])
        return

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.74, 0.26], vertical_spacing=0.04)
    fig.add_trace(
        go.Candlestick(
            x=plot_view["_plot_x"],
            open=plot_view["open"],
            high=plot_view["high"],
            low=plot_view["low"],
            close=plot_view["close"],
            text=[
                f"{dt}<br>시가 {open_v:,.0f}<br>고가 {high_v:,.0f}<br>저가 {low_v:,.0f}<br>종가 {close_v:,.0f}"
                for dt, open_v, high_v, low_v, close_v in zip(
                    plot_view["_hover_dt"],
                    plot_view["open"],
                    plot_view["high"],
                    plot_view["low"],
                    plot_view["close"],
                )
            ],
            hoverinfo="text",
            name=f"{interval_label}봉",
            increasing_line_color="#7ee0a1", decreasing_line_color="#ff8a8a",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=plot_view["_plot_x"],
            y=plot_view["vwap"],
            mode="lines",
            name="VWAP",
            line={"width": 1.6, "color": "#9ecbff"},
            customdata=plot_view["_hover_dt"],
            hovertemplate="%{customdata}<br>VWAP %{y:,.0f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=plot_view["_plot_x"],
            y=plot_view["volume"],
            name="거래량",
            marker_color="#5a6068",
            customdata=plot_view["_hover_dt"],
            hovertemplate="%{customdata}<br>거래량 %{y:,}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # 계좌 체감 기준 ±1/±2/±3 수평선 — 매수 직후 슬리피지 약 -0.3% 보정.
    # raw +1.3/+2.3/+3.3/-0.7/-1.7/-2.7로 계산해서 화면엔 계좌 라벨 표시.
    if signal_price:
        base_lines = [
            (0.000, signal_label, "#111827", "dot"),
            (+0.013, "+1%", "#16a34a", "dot"),
            (+0.023, "+2%", "#16a34a", "dot"),
            (+0.033, "+3%", "#15803d", "dot"),
            (-0.007, "-1%", "#dc2626", "dot"),
            (-0.017, "-2%", "#dc2626", "dot"),
            (-0.027, "-3%", "#991b1b", "dot"),
        ]
        rule_lines_by_name: dict[str, list] = {
            "기본": [],
            "기대형": [
                (+0.043, "목표 +4", "#15803d", "dash"),
                (+0.023, "보전 +2", "#16a34a", "dash"),
                (-0.027, "손절 -3", "#991b1b", "dash"),
            ],
            "보수형": [
                (+0.033, "목표 +3", "#15803d", "dash"),
                (+0.013, "발동 +1", "#22c55e", "dash"),
                (+0.008, "보전 +0.5", "#84cc16", "dash"),
                (-0.027, "손절 -3", "#991b1b", "dash"),
            ],
            "소익절형": [
                (+0.023, "목표 +2", "#15803d", "dash"),
                (+0.013, "발동 +1", "#22c55e", "dash"),
                (+0.008, "보전 +0.5", "#84cc16", "dash"),
                (-0.027, "손절 -3", "#991b1b", "dash"),
            ],
        }
        rule_lines = rule_lines_by_name.get(rule_label, [])
        if rule_lines:
            base_lines = [(p, l, "#cbd5e0", "dot") if l != signal_label else (p, l, "#111827", "dot") for p, l, _, _ in base_lines]
        for raw_pct, label, color, dash in base_lines + rule_lines:
            is_rule = dash == "dash"
            is_faded = color == "#cbd5e0"  # 룰 선택 시 옅어진 base 라인
            # 가독성 개선 (2026-05-21): 라인 굵게 + 라벨 박스화
            width = 2.8 if is_rule else (1.0 if is_faded else 1.8)
            font_color = "#475569" if is_faded else "white"
            bg_color = "#f1f5f9" if is_faded else color
            fig.add_hline(
                y=signal_price * (1 + raw_pct),
                line_dash=dash,
                line_color=color,
                line_width=width,
                annotation_text=f"<b>{label}</b>",
                annotation_font_size=13 if is_rule else 11,
                annotation_font_color=font_color,
                annotation_bgcolor=bg_color,
                annotation_bordercolor=color,
                annotation_borderwidth=1,
                annotation_borderpad=3,
                annotation_position="right",
                row=1, col=1,
            )

    # D+1~D+3 감시 구간 음영 (회복 트리거 핵심 관찰 구간 — 매수 신호 아님)
    window_dates_set = {pd.to_datetime(value).date() for value in window.get("dates", [])}
    d_focus = [d for d in future_dates[:3] if d.date() in window_dates_set]
    if d_focus:
        if compact_axis:
            day_indices = [compact_day_index[d.date()] for d in d_focus if d.date() in compact_day_index]
            if day_indices:
                shade_x0 = min(day_indices) * day_slot_width - 6
                shade_x1 = max(day_indices) * day_slot_width + day_slot_width + 6
                fig.add_shape(type="rect",
                              x0=shade_x0, x1=shade_x1, y0=0, y1=1,
                              xref="x", yref="paper",
                              fillcolor="rgba(159,122,234,0.10)", line=dict(width=0),
                              layer="below", row=1, col=1)
                fig.add_annotation(x=(shade_x0 + shade_x1) / 2, y=1.005,
                                   xref="x", yref="paper",
                                   text=f"D+1~D+{len(d_focus)} 감시 구간",
                                   showarrow=False, font=dict(size=10, color="#c4b5fd"),
                                   yanchor="bottom")
        else:
            shade_x0 = pd.Timestamp.combine(d_focus[0].date(), time(9, 0)).isoformat()
            shade_x1 = pd.Timestamp.combine(d_focus[-1].date(), time(15, 30)).isoformat()
            fig.add_shape(type="rect",
                          x0=shade_x0, x1=shade_x1, y0=0, y1=1,
                          xref="x", yref="paper",
                          fillcolor="rgba(159,122,234,0.10)", line=dict(width=0),
                          layer="below", row=1, col=1)
            fig.add_annotation(x=shade_x0, y=1.005, xref="x", yref="paper",
                               text=f"D+1~D+{len(d_focus)} 감시 구간",
                               showarrow=False, font=dict(size=10, color="#c4b5fd"),
                               yanchor="bottom", xanchor="left")

    # D+ 수직 라벨
    if signal_date in {pd.to_datetime(value).date() for value in window.get("dates", [])}:
        marker_x = compact_day_index[signal_date] * day_slot_width if compact_axis and signal_date in compact_day_index else pd.Timestamp.combine(signal_date, time(9, 0)).isoformat()
        add_vertical_marker(fig, marker_x, f"웹훅일 {signal_ts.strftime('%m.%d')}", "#f6ad55")
    for idx, date_value in enumerate(future_dates, start=1):
        if date_value.date() in {pd.to_datetime(value).date() for value in window.get("dates", [])}:
            marker_x: Any
            if compact_axis:
                if date_value.date() not in compact_day_index:
                    continue
                marker_x = compact_day_index[date_value.date()] * day_slot_width
            else:
                marker_x = pd.Timestamp.combine(date_value.date(), time(9, 0)).isoformat()
            add_vertical_marker(fig, marker_x, f"D+{idx} {date_value.strftime('%m.%d')}", "#a0aec0")

    # 결과 오버레이 (사후 모드에서만)
    if show_outcome and review_row:
        plus3 = is_truthy(review_row.get("outcome_d1_d5_plus3_touch"))
        plus2 = is_truthy(review_row.get("outcome_d1_d5_plus2_touch"))
        minus2 = is_truthy(review_row.get("outcome_d1_d5_minus2_touch"))
        first3 = str(review_row.get("first_plus3_day", "")).strip()
        first2 = str(review_row.get("first_plus2_day", "")).strip()
        first_minus = str(review_row.get("first_minus2_day", "")).strip()
        text_parts = []
        if plus3:
            text_parts.append(f"<span style='color:#7ee0a1'>+3% 도달 D+{first3 or '?'}</span>")
        elif plus2:
            text_parts.append(f"<span style='color:#ffd166'>+2% 도달 D+{first2 or '?'}</span>")
        else:
            text_parts.append("<span style='color:#a0aec0'>+3% 미도달</span>")
        if minus2:
            text_parts.append(f"<span style='color:#ff8a8a'>-2% 터치 D+{first_minus or '?'}</span>")
        else:
            text_parts.append("<span style='color:#a0aec0'>-2% 미터치</span>")
        fig.add_annotation(
            xref="paper", yref="paper", x=1.0, y=1.04,
            xanchor="right", yanchor="bottom",
            text=" · ".join(text_parts),
            showarrow=False,
            font={"size": 12},
            bgcolor="rgba(0,0,0,0.55)",
            bordercolor="rgba(255,255,255,0.18)",
            borderwidth=1,
            borderpad=6,
        )

    _apply_light_chart_layout(fig, height=560, legend_y=1.12, top_margin=80)
    fig.update_layout(showlegend=False)
    if compact_axis:
        tickvals = []
        ticktext = []
        for date_value in window["dates"]:
            date_value = pd.to_datetime(date_value)
            day = date_value.date()
            if day not in compact_day_index:
                continue
            tickvals.append(compact_day_index[day] * day_slot_width + 195)
            future_idx = next((idx for idx, fd in enumerate(future_dates, start=1) if fd.date() == day), None)
            day_label = "웹훅일" if day == signal_date else f"D+{future_idx}"
            ticktext.append(f"{day_label}<br>{date_value.strftime('%m.%d')}")
        x_min = float(plot_view["_plot_x"].min()) - 12
        x_max = float(plot_view["_plot_x"].max()) + 12
        fig.update_xaxes(
            type="linear",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            range=[x_min, x_max],
            title_text=x_axis_title,
            row=1,
            col=1,
        )
        fig.update_xaxes(
            type="linear",
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            range=[x_min, x_max],
            title_text=x_axis_title,
            row=2,
            col=1,
        )
    else:
        fig.update_xaxes(range=[plot_view["dt"].min(), plot_view["dt"].max()], row=1, col=1)
        fig.update_xaxes(range=[plot_view["dt"].min(), plot_view["dt"].max()], row=2, col=1)

    # 가격축 y range — 0부터가 아니라 기간 저가~고가의 ±3% 패딩으로 자동 줌
    try:
        prices = pd.concat([plot_view.get("high"), plot_view.get("low"), plot_view.get("close")]).dropna()
        prices = prices[prices > 0]
        if not prices.empty:
            y_lo = float(prices.min()) * 0.97
            y_hi = float(prices.max()) * 1.03
            if y_hi > y_lo:
                fig.update_yaxes(range=[y_lo, y_hi], row=1, col=1)
    except Exception:  # noqa: BLE001
        pass

    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    # 기준가 + 라인 표시 정책 안내
    ref_text = (
        f"**기준가**: {signal_price:,.0f}원 ({signal_label} · 신호일 15시 진입가)"
        if signal_price else "**기준가**: — (entry_price 미감지)"
    )
    st.caption(
        f"{ref_text} · 라인은 **계좌 체감 기준** ±1/±2/±3%. "
        "매수 직후 슬리피지 약 -0.3%를 반영해 내부 raw +1.3/+2.3/+3.3, -0.7/-1.7/-2.7로 계산합니다."
    )


# Shadow / 연구용 감시 데이터 (Codex paper_watch 산출)
PULLBACK_RECLAIM_DIR = CLOSINGBELL / "paper_watch" / "pullback_reclaim"


@st.cache_data(show_spinner=False)
def load_pullback_reclaim_watch(target_date: str = "") -> pd.DataFrame:
    """target_date 의 pullback_reclaim_watch_*.csv. 없으면 최신."""
    if not PULLBACK_RECLAIM_DIR.exists():
        return pd.DataFrame()
    if target_date:
        path = PULLBACK_RECLAIM_DIR / f"pullback_reclaim_watch_{target_date.replace('-', '')}.csv"
        if path.exists():
            return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    path = _latest_path(PULLBACK_RECLAIM_DIR, "pullback_reclaim_watch_*.csv", PULLBACK_RECLAIM_DIR / "pullback_reclaim_watch_20260513.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")


@st.cache_data(show_spinner=False)
def load_pullback_reclaim_result(target_date: str = "") -> pd.DataFrame:
    if not PULLBACK_RECLAIM_DIR.exists():
        return pd.DataFrame()
    if target_date:
        path = PULLBACK_RECLAIM_DIR / f"pullback_reclaim_result_{target_date.replace('-', '')}.csv"
        if path.exists():
            return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    path = _latest_path(PULLBACK_RECLAIM_DIR, "pullback_reclaim_result_*.csv", PULLBACK_RECLAIM_DIR / "pullback_reclaim_result_20260513.csv")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")


# 후보 상태/Shadow watch_type 한글 라벨 (지시서 §5 · §9)
WATCH_TYPE_LABELS = {
    "D0_STRONG_CLOSE_LIVE_TOP2": "D0 강세종가 · 본문 LIVE",
    "D0_STRONG_CLOSE_LIVE_RANK3": "D0 강세종가 · 참고 LIVE",
    "D0_STRONG_CLOSE_POOL_ONLY": "D0 강세종가 · 풀 후보 (LIVE Top5 외)",
    "D0_STRONG_CLOSE": "D0 강세종가",
    "PULLBACK_WATCH": "눌림목 감시",
    "PULLBACK_RECLAIM": "눌림 회복 확인",
    "VWAP_RECLAIM": "거래량 가중 평균가(VWAP) 회복",
    "ORB_BREAK": "장초반 고점 돌파(ORB)",
    "IPO_WATCH": "IPO 별도 감시",
    "GAP_OVERHEAT": "갭 과열",
    "PRICE_BREAKDOWN": "가격 붕괴",
    "DATA_CAUTION": "데이터 주의",
}
TRIGGER_STATUS_LABELS = {
    "WAIT_DPLUS1_DAILY_OR_INTRADAY_DATA": "D+1 일봉·분봉 데이터 대기",
    "WAIT_DPLUS1_DAILY_OR_INTRADAY": "D+1 일봉·분봉 데이터 대기",
    "PULLBACK_RECLAIM_PENDING": "눌림 회복 대기 (D+1~D+3 확인 필요)",
    "TRIGGERED": "트리거 발생",
    "NO_TRIGGER": "트리거 없음",
    "WAITING_FOR_FUTURE_DPLUS_AND_RECLAIM_TRIGGER": "다음 거래일 회복 트리거 대기",
}


def _watch_type_label(value: Any) -> str:
    text = str(value or "").strip()
    return WATCH_TYPE_LABELS.get(text, text)


def _trigger_status_label(value: Any) -> str:
    text = str(value or "").strip()
    return TRIGGER_STATUS_LABELS.get(text, text)


def render_shadow_watch_section(picks: pd.DataFrame, score: pd.DataFrame) -> None:
    """홈의 '🧪 연구용 감시 (Shadow)' 섹션 — Pullback Reclaim watch 를 우선 표시.
    LIVE 후보 미리보기와 시각적으로 분리하고, '추천 종목 아님 · 운영 미반영' 라벨 강조."""
    src = picks if (picks is not None and not picks.empty and "signal_date" in picks.columns) else score
    target_date = ""
    if src is not None and not src.empty and "signal_date" in src.columns:
        sds = [str(s) for s in src["signal_date"].dropna().tolist() if str(s).strip()]
        if sds:
            target_date = max(sds)
    watch = load_pullback_reclaim_watch(target_date)
    result = load_pullback_reclaim_result(target_date)

    st.markdown('<div class="cb-section-title">🧪 연구용 Shadow 후보 — 매수 추천 아님 · 자동매매 아님 · 운영 미반영</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cb-note" style="border-left-color:#9f7aea; background:rgba(159,122,234,0.10);">'
        '이 섹션은 Codex 의 연구용 산출물(`paper_watch/pullback_reclaim`)입니다. '
        '15:00 LIVE 웹훅과 별개이며, <b>매수 추천이 아니라 D+1~D+3에 눌림 후 회복 트리거가 실제로 발생하는지 사후 검증</b>하기 위한 감시 후보입니다. '
        '사람이 차트를 직접 보고 판단하는 단계이며 자동 진입은 없습니다.'
        '</div>',
        unsafe_allow_html=True,
    )
    if watch.empty:
        st.caption(f"Pullback Reclaim watch 파일이 없습니다. ({target_date or '대상 날짜 미확인'}) Codex paper_watch 산출 대기.")
        return

    # 결과 인덱스 (오늘 result 가 있으면 trigger / target1_before_risk1 같이)
    result_idx: dict[str, dict[str, Any]] = {}
    if not result.empty and "stock_code" in result.columns:
        for _, r in result.iterrows():
            result_idx[normalize_code(r.get("stock_code", ""))] = r.to_dict()

    def _row_for(wd: dict[str, Any]) -> dict[str, Any]:
        code = normalize_code(wd.get("stock_code", ""))
        wtype = _watch_type_label(wd.get("watch_type", ""))
        tstatus = _trigger_status_label(wd.get("trigger_status", ""))
        rr = result_idx.get(code, {})
        result_text = "—"
        if rr:
            triggered = str(rr.get("triggered", "")).lower() in {"true", "1", "yes"}
            rs = _trigger_status_label(rr.get("result_status", ""))
            t1 = str(rr.get("target1_before_risk1", "")).strip() or "—"
            if triggered:
                result_text = f"🟢 트리거 · {t1}"
            elif rs:
                result_text = f"⏳ {rs}"
        return {
            "종목": f"{wd.get('stock_name', '')} ({code})",
            "감시 유형": wtype,
            "점수": wd.get("score_total_100", ""),
            "D0 원천일": wd.get("d0_date", ""),
            "트리거 상태": tstatus,
            "결과": result_text,
            "비고": str(wd.get("notes", ""))[:80],
        }

    # LIVE Top2/Rank3 우선 표시 (사용자 관점에서 가장 중요)
    live_mask = watch["watch_type"].isin(["D0_STRONG_CLOSE_LIVE_TOP2", "D0_STRONG_CLOSE_LIVE_RANK3"])
    live_rows = watch[live_mask]
    pool_rows = watch[~live_mask]
    if not live_rows.empty:
        st.markdown('<div class="cb-key" style="margin:6px 0 4px;">🎯 LIVE 후보와 매칭된 Shadow 감시 (D0 강세종가 + Pullback Reclaim 대기)</div>', unsafe_allow_html=True)
        live_display = [_row_for(r.to_dict()) for _, r in live_rows.iterrows()]
        st.dataframe(pd.DataFrame(live_display), use_container_width=True, hide_index=True, height=44 + 38 * len(live_display))
    if not pool_rows.empty:
        with st.expander(f"📦 D0 풀 후보 (LIVE Top5 외 강세종가, {len(pool_rows)}건) — 연구용", expanded=False):
            pool_display = [_row_for(r.to_dict()) for _, r in pool_rows.iterrows()]
            st.dataframe(pd.DataFrame(pool_display), use_container_width=True, hide_index=True, height=min(420, 44 + 38 * len(pool_display)))

    # 다른 Shadow 카테고리는 데이터 준비 대기 중임을 명시
    st.caption(
        "다른 Shadow 카테고리(VWAP 회복 / 전일 눌림 고가 회복 / IPO 별도)는 Codex 가 운영 산출물로 떨궈 줄 때까지 대기. "
        "현재는 D0 강세종가 + Pullback Reclaim 감시만 표시됩니다."
    )


@st.cache_data(show_spinner=False)
def _load_krx_holidays() -> set[str]:
    """data/market/calendar/krx_holidays_manual.csv → set of 'YYYY-MM-DD'. 없으면 빈 set."""
    path = DATA / "market" / "calendar" / "krx_holidays_manual.csv"
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    except Exception:
        return set()
    return {str(row.get("date", ""))[:10] for _, row in df.iterrows() if str(row.get("date", "")).strip()}


def _busday_count(start: pd.Timestamp | None, end: pd.Timestamp) -> int:
    """주말 + KRX 휴장일을 거른 영업일 차이 (end - start). start None이면 큰 수."""
    if start is None:
        return 9_999
    if start >= end:
        return 0
    days = pd.bdate_range(start + pd.Timedelta(days=1), end, freq="B")
    holidays = _load_krx_holidays()
    if not holidays:
        return len(days)
    return sum(1 for d in days if d.strftime("%Y-%m-%d") not in holidays)


def _latest_daily_for(code: str) -> pd.Timestamp | None:
    df = load_daily(code)
    if df.empty:
        return None
    return pd.Timestamp(df["date"].max()).normalize()


def _latest_minute_for(code: str) -> pd.Timestamp | None:
    df = load_minute(code)
    if df.empty:
        return None
    return pd.Timestamp(df["dt"].max()).normalize()


def render_data_freshness_card(picks: pd.DataFrame, score: pd.DataFrame, *, compact: bool = False) -> None:
    """홈 상단 데이터 최신성 카드.
    - 웹훅 기준일 (signal_date)
    - 후보 D0 원천일 (d0_date)
    - 일봉 최신일 / 분봉 최신일 (본문+참고 후보 중 max)
    - 상태: 일봉 lag 기준 정상 🟢 / 1거래일 주의 🟡 / 2거래일+ 위험 🔴
    압축 모드(compact=True)는 종목 상세 옆에 작은 한 줄."""
    src = picks if (picks is not None and not picks.empty and "d0_date" in picks.columns) else score
    if src is None or src.empty or "signal_date" not in src.columns:
        return
    sds = [str(s) for s in src["signal_date"].dropna().tolist() if str(s).strip()]
    if not sds:
        return
    latest_sd = max(sds)
    today = pd.Timestamp.today().normalize()
    rows = src[src["signal_date"].astype(str) == latest_sd].copy()
    rows["rank_n"] = pd.to_numeric(rows.get("rank", 0), errors="coerce").fillna(99).astype(int)
    body = rows[rows["rank_n"].between(1, 3)]
    if body.empty:
        body = rows.head(3)
    d0_dates = [str(d)[:10] for d in body.get("d0_date", pd.Series([], dtype=str)).tolist() if str(d).strip()]
    d0_date = max(d0_dates) if d0_dates else ""
    latest_dailies: list[pd.Timestamp] = []
    latest_minutes: list[pd.Timestamp] = []
    for _, r in body.iterrows():
        c = normalize_code(r.get("stock_code", ""))
        ld = _latest_daily_for(c)
        lm = _latest_minute_for(c)
        if ld is not None:
            latest_dailies.append(ld)
        if lm is not None:
            latest_minutes.append(lm)
    latest_daily = max(latest_dailies) if latest_dailies else None
    latest_minute = max(latest_minutes) if latest_minutes else None
    daily_lag = _busday_count(latest_daily, today)
    if daily_lag <= 1:
        status_emoji, status_text, status_cls = "🟢", "최신", "cb-tag-good"
    elif daily_lag == 2:
        status_emoji, status_text, status_cls = "🟡", "주의 — 후보 가격 데이터가 최신이 아닐 수 있음", "cb-tag"
    else:
        status_emoji, status_text, status_cls = "🔴", "위험 — 후보 가격 데이터가 2거래일 이상 지연", "cb-tag-warn"

    def _fmt(ts: pd.Timestamp | None) -> str:
        return ts.strftime("%Y-%m-%d") if ts is not None else "—"

    if compact:
        st.markdown(
            '<div class="cb-quality-bar">'
            f'<span class="cb-key" style="font-size:0.8rem;">데이터 최신성</span>'
            f'<span class="cb-tag {status_cls}">{status_emoji} {status_text}</span>'
            f'<span class="cb-tag cb-tag-info" title="signal_date">웹훅 {latest_sd}</span>'
            f'<span class="cb-tag" title="d0_date">D0 {d0_date or "—"}</span>'
            f'<span class="cb-tag" title="일봉 최신">일봉 {_fmt(latest_daily)}</span>'
            f'<span class="cb-tag" title="분봉 최신">분봉 {_fmt(latest_minute)}</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="cb-section-title">오늘 데이터 최신성</div>', unsafe_allow_html=True)
    fcols = st.columns([1.4, 1.6, 1.2, 1.2, 1.8])
    fcols[0].metric("웹훅 기준일", latest_sd)
    fcols[1].metric("최초 거래대금 폭발일(D0)", d0_date or "—")
    fcols[2].metric("가격 데이터 최신일", _fmt(latest_daily))
    fcols[3].metric("분봉 데이터 최신일", _fmt(latest_minute))
    fcols[4].markdown(
        f'<div style="padding-top:1.0rem;"><span class="cb-tag {status_cls}" style="font-size:0.98rem; padding:0.32rem 0.8rem; white-space:normal; line-height:1.4;">{status_emoji} {status_text}</span></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "🟢 최신 · 🟡 1거래일 지연 · 🔴 2거래일 이상 지연 — 영업일(주말 + KRX 휴장일) 기준. "
        f"기준 표본: 본문+참고 후보 {len(body)}건. 오늘 장마감 17:05 PostClose 이후 자동으로 최신화됩니다."
    )


def _compute_dplus1_outcome(code: str, anchor_date: str, ref_price: float) -> dict[str, Any]:
    """anchor_date(보통 signal_date) 다음 거래일(D+1)의 일봉 기준 도달/터치 결과.
    - 일봉이 아직 없으면 status='pending' (그 거래일 장마감·수집 전).
    - +3%·-2%가 같은 날 함께 발생하고 분봉이 있으면 선후관계까지 계산.
    이 함수는 후보 선정/점수에 전혀 영향을 주지 않는 표시용 파생 계산이다."""
    code = normalize_code(code)
    daily = load_daily(code)
    if daily.empty:
        return {"status": "no_daily"}
    latest_daily = str(daily["date"].max().date())
    future = trading_days_after(code, str(anchor_date), 1)
    if not future:
        # 일봉이 anchor_date 다음 거래일까지 아직 안 들어옴 (그 거래일 장마감·수집 전)
        return {"status": "pending", "latest_daily": latest_daily}
    d1 = pd.Timestamp(future[0]).normalize()
    match = daily[daily["date"].dt.normalize() == d1]
    if match.empty:
        return {"status": "pending", "d1_date": d1.date().isoformat(), "latest_daily": latest_daily}
    r = match.iloc[0]
    try:
        hi, lo, close = float(r["high"]), float(r["low"]), float(r["close"])
    except Exception:
        return {"status": "pending", "d1_date": d1.date().isoformat(), "latest_daily": latest_daily}
    if not ref_price or ref_price <= 0:
        return {"status": "no_ref", "d1_date": d1.date().isoformat(), "high": hi, "low": lo, "close": close}
    out: dict[str, Any] = {
        "status": "ready",
        "d1_date": d1.date().isoformat(),
        "ref_price": ref_price,
        "high": hi, "low": lo, "close": close,
        "high_pct": (hi / ref_price - 1) * 100,
        "low_pct": (lo / ref_price - 1) * 100,
        "close_pct": (close / ref_price - 1) * 100,
        "plus1": hi >= ref_price * 1.01,
        "plus2": hi >= ref_price * 1.02,
        "plus3": hi >= ref_price * 1.03,
        "minus2": lo <= ref_price * 0.98,
        "order_minute": False,
    }
    if out["plus3"] and out["minus2"]:
        order = "SAME_DAY_ORDER_UNKNOWN"
        mins = load_minute(code)
        if not mins.empty:
            day = mins[mins["dt"].dt.date == d1.date()].sort_values("dt")
            if not day.empty:
                t3 = day[day["high"] >= ref_price * 1.03]["dt"].min()
                tm = day[day["low"] <= ref_price * 0.98]["dt"].min()
                if pd.notna(t3) and pd.notna(tm):
                    order = "TARGET3_FIRST" if t3 <= tm else "RISK2_FIRST"
                    out["order_minute"] = True
        out["order"] = order
    elif out["plus3"]:
        out["order"] = "TARGET3_ONLY"
    elif out["minus2"]:
        out["order"] = "RISK2_ONLY"
    else:
        out["order"] = "NO_TARGET3_OR_RISK2"
    return out


_DPLUS1_ORDER_TEXT = {
    "TARGET3_FIRST": "🟢 +3% 먼저 도달",
    "RISK2_FIRST": "🔴 -2% 먼저 터치",
    "SAME_DAY_ORDER_UNKNOWN": "🟡 +3·-2 같은 날 (순서 미확인)",
    "TARGET3_ONLY": "🟢 +3% 도달",
    "RISK2_ONLY": "🔴 -2% 터치",
    "NO_TARGET3_OR_RISK2": "⚪ +3/-2 모두 없음",
}


def render_dplus1_card(picks: pd.DataFrame, score: pd.DataFrame) -> None:
    """가장 최근 웹훅 후보(보통 어제)의 D+1 결과 카드.
    일봉 고가·저가로 +1/+2/+3% 도달과 -2% 터치를 직접 계산하고,
    같은 날 +3·-2가 함께 발생하면 분봉으로 선후관계를 시도한다.
    아직 D+1 일봉이 없으면 '결과 대기'로 안내한다 (그 거래일 장마감·수집 후 채워짐)."""
    src = picks if (picks is not None and not picks.empty and "d0_price" in picks.columns) else score
    if src is None or src.empty or "signal_date" not in src.columns:
        return
    sds = [str(s) for s in src["signal_date"].dropna().tolist() if str(s).strip()]
    if not sds:
        return
    latest_sd = max(sds)
    rows = src[src["signal_date"].astype(str) == latest_sd].copy()
    rows["rank_n"] = pd.to_numeric(rows.get("rank", 0), errors="coerce").fillna(99).astype(int)
    body = rows[rows["rank_n"].between(1, 3)].sort_values("rank_n")
    if body.empty:
        return

    st.markdown(f'<div class="cb-section-title">어제({latest_sd}) 후보 D+1 결과 — 본문 2 + 참고 1</div>', unsafe_allow_html=True)
    table_rows: list[dict[str, Any]] = []
    any_pending = False
    any_minute_gap = False
    for _, r in body.iterrows():
        rd = r.to_dict()
        code = normalize_code(rd.get("stock_code", ""))
        role_v = str(rd.get("role", ""))
        badge = "🟢" if role_v == "BODY_TOP2" else ("🟡" if role_v == "REFERENCE_RANK3" else "⚪")
        ref_price, ref_label = reference_price(rd)
        oc = _compute_dplus1_outcome(code, latest_sd, ref_price or 0.0)
        status = oc.get("status")
        if status in ("pending", "no_daily", "no_ref"):
            if status == "pending":
                any_pending = True
            judge = "⏳ 결과 대기"
            if status == "pending":
                _d1 = oc.get("d1_date")
                note = (f"D+1({_d1}) 일봉 미수집" if _d1 else "D+1 일봉 미수집") + f" · 현재 일봉 최신 {oc.get('latest_daily', '?')}"
            elif status == "no_daily":
                note = "일봉 parquet 파일 없음"
            else:
                note = "기준가 미확인"
            reach = minus = "—"
        else:
            order = oc.get("order", "")
            judge = _DPLUS1_ORDER_TEXT.get(order, "—")
            if order == "SAME_DAY_ORDER_UNKNOWN" and not oc.get("order_minute"):
                any_minute_gap = True
                note = "분봉 없음 — 선후관계는 Codex D+1~D+5 집계 대기"
            else:
                note = f"고가 {oc['high_pct']:+.1f}% · 저가 {oc['low_pct']:+.1f}% · 종가 {oc['close_pct']:+.1f}%"
                if oc.get("order_minute"):
                    note += " · 분봉 확인"
            reach = " ".join(x for x in [
                "+1✓" if oc["plus1"] else "",
                "+2✓" if oc["plus2"] else "",
                "+3✓" if oc["plus3"] else "",
            ] if x) or "미도달"
            minus = "터치" if oc["minus2"] else "미터치"
        table_rows.append({
            "순위": rd.get("rank", ""),
            "구분": f"{badge} {role_label(role_v)}",
            "종목": f"{rd.get('stock_name', '')} ({code})",
            "점수": rd.get("score", ""),
            "기준가": f"{ref_price:,.0f}" if ref_price else "—",
            "+1/+2/+3": reach,
            "-2%": minus,
            "D+1 판정": judge,
            "비고": note,
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True, height=44 + 38 * len(table_rows))
    if any_pending:
        st.caption(
            "⏳ D+1 결과는 그 거래일 장마감 후 일봉이 수집되면(예: 17:05 PostClose) 자동으로 채워집니다. "
            "+3%·-2% 중 무엇이 먼저였는지(선후관계)는 분봉이 있어야 확정되며, Codex의 D+1~D+5 outcome 집계가 붙으면 더 정확해집니다."
        )
    elif any_minute_gap:
        st.caption("※ 도달/터치는 일봉 고가·저가 기준 직접 계산값입니다. 같은 날 +3·-2가 함께 발생한 종목은 분봉이 없어 선후관계를 확정하지 못했습니다 (Codex 집계 대기).")
    else:
        st.caption("※ 도달/터치는 일봉 고가·저가 기준 직접 계산값입니다. 분봉이 있으면 +3·-2 동시 발생 시 선후관계도 표시합니다.")


def render_home(d0_pool: pd.DataFrame, score: pd.DataFrame, picks: pd.DataFrame, scan: dict[str, Any]) -> None:
    sent = sent_log_summary()
    top2 = score[score["role"] == "BODY_TOP2"] if not score.empty and "role" in score.columns else pd.DataFrame()
    rank3 = score[score["role"] == "REFERENCE_RANK3"] if not score.empty and "role" in score.columns else pd.DataFrame()
    log45 = score[score["role"] == "LOG_ONLY"] if not score.empty and "role" in score.columns else pd.DataFrame()
    today = score["signal_date"].max() if not score.empty and "signal_date" in score.columns else "미확인"

    # === 사용 가이드 (열어두면 처음 보는 사람도 따라할 수 있음) ===
    with st.expander("📖 대시보드 사용 가이드 — 처음 오신 분 / 작업 흐름", expanded=False):
        st.markdown("""
**이 대시보드는 무엇인가**

ClosingBell Paper Watch 워크플로우의 **읽기 전용 검토 화면**입니다.
- 매일 14:15~15:00 동안 D0 조건을 만족한 종목 중 **본문 후보 2개 + 참고 후보 1개**를 선정해 디스코드로 알림
- 알림 후 **D+1~D+5 안에 +3% 도달했는지 / -2% 터치했는지**를 사후에 확인하는 게 목표
- 실거래·자동매매 코드는 없음. 수동 검토만.

**탭 사용 순서**

1. **🏠 홈** — 오늘 후보를 한눈에 보고, 1년치 통계 한 줄로 점수 모델 신뢰도 확인.
2. **🔍 D0 감시 종목 전체** — 점수와 무관하게 조건 만족한 모든 종목. 점수 상위가 어떤 풀에서 추려졌는지 맥락 확인.
3. **📈 1년치 복기 (종목 상세 통합)** — **메인 작업 화면**.
   - 위쪽: 날짜 네비 → 종목 슬롯(Top1/Top2/Rank3) → 분봉 차트 + REVIEW + 메모
   - 아래쪽: 일봉(MA), 매매주체(외국인/기관/프로그램) 표·차트, 글로벌 지수, 재무
   - **오늘 날짜이면** 14:15→15:00 흐름 + 수급/공시 패널이 추가로 표시
4. **📊 통계** — 점수 구간별 +3% 도달률, 역할별 적중률, 점수 분포 히스토그램. 점수 모델 검증용.
5. **📝 메모** — 메모 모아보기. 결과 색깔/날짜/키워드로 필터링.

**복기 루틴 (권장)**

1. 1년치 복기 탭에서 날짜 선택 → 슬롯 탭에서 Top1 클릭
2. **결과 숨김** 모드로 차트 보고 사전 느낌 메모 (오른쪽 패널)
3. **결과 표시** 토글 → +3%/+2% 도달일과 -2% 터치일 확인
4. 사후 생각, 패턴, 놓친 점, 다음 점검 아이디어 메모 → 저장
5. 다음 슬롯(Top2, Rank3)으로 이동, 같은 흐름 반복
6. 다른 날짜로 이동 — 메모는 자동 저장됨

**색깔 약속**

- 🟢 본문 후보 / 🟡 참고 후보 / ⚪ 보조 후보
- 결과: 🟢 +3% 먼저 도달 / 🔴 -2% 먼저 터치 / 🟡 +1·+2까지만 또는 같은 날 / ⚪ 미도달

**주의**

- 메모 저장은 last-write-wins (백업은 `.bak` 1개 자동 유지)
- 분봉 데이터가 없는 거래일은 ⚠️ 캡션으로 표시됨
- 점수와 후보 선정은 이 화면에서 변경 불가 — 별도 백테스트/운영 코드에서만 변경
""")

    # === 헤더 메트릭 ===
    cols = st.columns(5)
    cols[0].metric("웹훅 기준일", today)
    cols[1].metric("D0 후보 풀 (전체)", len(d0_pool), help="최초 거래대금 폭발일(D0) 조건을 만족한 종목 전체 수")
    cols[2].metric("본문 후보 (Top2)", len(top2))
    cols[3].metric("참고 후보 (Rank3)", len(rank3))
    cols[4].metric("D+1~D+5 추적 저장", len(picks))

    # === 1. 오늘 데이터 최신성 ===
    render_data_freshness_card(picks, score)

    # === 2. LIVE 후보 미리보기 ===
    st.markdown('<div class="cb-section-title">✅ LIVE 후보 — 실제 웹훅 기준 (기존 거래대금 기준 P0)</div>', unsafe_allow_html=True)
    if score.empty:
        st.info("score_breakdown 파일이 없습니다.")
    else:
        score_today = score.copy()
        score_today["rank_n"] = pd.to_numeric(score_today.get("rank", 0), errors="coerce").fillna(0).astype(int)
        score_today = score_today.sort_values("rank_n")
        preview_rows = []
        for _, row in score_today[score_today["rank_n"].between(1, 3)].iterrows():
            role_v = str(row.get("role", ""))
            badge = "🟢" if role_v == "BODY_TOP2" else ("🟡" if role_v == "REFERENCE_RANK3" else "⚪")
            policy_text = policy_label(row.get("policy_decision", row.get("candidate_policy", "")))
            warnings = warning_labels(row.get("warning_codes", "")).replace("- ", "").replace("\n", " · ")
            preview_rows.append({
                "순위": row.get("rank", ""),
                "구분": f"{badge} {role_label(row.get('role', ''))}",
                "종목": f"{row.get('stock_name', '')} ({normalize_code(row.get('stock_code', ''))})",
                "점수": row.get("score", ""),
                "현재 상태": policy_text,
                "경고": warnings if warnings != "특이 경고 없음" else "—",
            })
        if preview_rows:
            st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True, height=180)
            st.caption(
                f"기준: 기존 거래대금 기준 (P0) · "
                f"보조 후보(Log4/Log5) {len(log45)}건은 [오늘의 웹훅 후보] 탭 expander에서. · "
                "주의: v2 연구 점수는 아직 운영 미반영."
            )
        else:
            st.info("Top1/Top2/Rank3 후보가 없습니다.")

    # === 3. 연구용 Shadow 후보 (Pullback Reclaim 우선) ===
    render_shadow_watch_section(picks, score)

    # === 4. 어제 후보 D+1 결과 카드 ===
    render_dplus1_card(picks, score)

    # === 1년치 backdata 통계 한 줄 ===
    backtest_dir_text = latest_backtest_dir()
    if backtest_dir_text:
        review_1y = read_csv(str(Path(backtest_dir_text) / "review_outcomes_1y.csv"))
        if not review_1y.empty:
            total_b = len(review_1y)
            p3 = review_1y["outcome_d1_d5_plus3_touch"].astype(str).str.lower().isin(["true", "1", "yes"]).sum() if "outcome_d1_d5_plus3_touch" in review_1y.columns else 0
            m2 = review_1y["outcome_d1_d5_minus2_touch"].astype(str).str.lower().isin(["true", "1", "yes"]).sum() if "outcome_d1_d5_minus2_touch" in review_1y.columns else 0
            st.markdown(
                f'<div class="cb-mini-row">'
                f'<span class="cb-mini-cell"><span class="cb-mini-key">1년치 표본</span><b>{total_b:,}</b></span>'
                f'<span class="cb-mini-cell"><span class="cb-mini-key">+3% 도달률</span><span class="cb-result-good">{p3/total_b*100:.1f}%</span></span>'
                f'<span class="cb-mini-cell"><span class="cb-mini-key">-2% 터치율</span><span class="cb-result-bad">{m2/total_b*100:.1f}%</span></span>'
                f'<span class="cb-mini-cell"><span class="cb-mini-key">자세히</span>→ [통계] 탭</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # === 상태 + 데이터 파일 (expander로 접음) ===
    with st.expander("운영 상태 요약 / 데이터 파일", expanded=False):
        status = pd.DataFrame(
            [
                {"항목": "TEST 웹훅", "상태": sent["test_latest"], "메모": "기존 TEST는 401 Unauthorized 기록이 있어 교체 필요"},
                {"항목": "PROD 웹훅", "상태": sent["prod_latest"], "메모": f"오늘 PROD-TEST 성공 {sent['prod_sent_count_today']}회. 반복 발송 금지"},
                {"항목": "전송 기록", "상태": sent["latest_status"], "메모": sent["latest_created_at"]},
                {"항목": "비밀값 스캔", "상태": f"{scan.get('findings', scan.get('matches', 0))}건", "메모": "원문 URL/API key 미출력"},
            ]
        )
        st.dataframe(status, use_container_width=True, hide_index=True)
        files = [D0_POOL_PATH, ENRICHED_PATH, LIVE_SAFE_PATH, REVIEW_PATH, WATCHLIST_20D_PATH, WEBHOOK_PICKS_PATH, SCORE_PATH]
        file_rows = [{"파일": str(path), "상태": "있음" if path.exists() else "없음", "수정시각": latest_file_mtime(path)} for path in files]
        st.dataframe(pd.DataFrame(file_rows), use_container_width=True, hide_index=True)


def _format_billion(value: Any) -> str:
    """원 단위 거래대금 → '1,234억' 형식."""
    n = numeric(value)
    if n is None:
        return "—"
    eok = n / 1_0000_0000  # 1억 = 10^8
    return f"{eok:,.0f}억"


def _format_signed_pct(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:+.2f}%"


def _format_ratio(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:.2f}x"


def render_d0_pool(d0_pool: pd.DataFrame) -> None:
    st.subheader("D0 감시 종목 전체")
    st.markdown(
        '<div class="cb-note"><b>D0 감시 종목 전체</b>는 조건을 만족한 모든 종목입니다. '
        '웹훅 본문 후보(Top2)와는 다른 층입니다. 여기는 <b>관찰 풀</b>이고, 웹훅 후보는 점수 상위만.</div>',
        unsafe_allow_html=True,
    )
    if d0_pool.empty:
        st.warning("D0 pool 파일이 없습니다.")
        return
    df = d0_pool.copy()
    # 시각용 한글 컬럼 구성
    df["종목"] = df.apply(lambda r: f"{r.get('stock_name', '')} ({normalize_code(r.get('stock_code', ''))})", axis=1)
    df["기준일"] = df.get("signal_date", "")
    df["D0 사유"] = df.get("d0_reason", "").map(d0_reason_label)
    df["D0 거래대금"] = df.get("d0_trading_value", "").map(_format_billion)
    df["거래량 순위"] = df.get("d0_volume_rank", "")
    df["거래대금 순위"] = df.get("d0_trading_value_rank", "")
    df["등락률"] = df.get("pct_change", "").map(_format_signed_pct)
    df["D0 고가"] = df.get("d0_high", "")
    df["현재가"] = df.get("current_price", "")
    df["D0 고가 대비"] = df.get("distance_from_d0_high_pct", "").map(_format_signed_pct)
    df["D0 대비 거래량"] = df.get("volume_ratio_vs_d0", "").map(_format_ratio)
    df["감시 상태"] = df.get("watch_status", "").map(watch_status_label)
    df["오래됨"] = df.get("is_stale", "").map(lambda v: "오래됨" if str(v).strip().lower() in {"true", "1", "yes"} else "신선")
    visible = ["기준일", "종목", "D0 사유", "D0 거래대금", "거래량 순위", "거래대금 순위", "등락률", "D0 고가", "현재가", "D0 고가 대비", "D0 대비 거래량", "감시 상태", "오래됨"]
    out = df[visible].reset_index(drop=True)
    st.dataframe(
        out, use_container_width=True, hide_index=True, height=560,
        column_config={
            "기준일": st.column_config.TextColumn("기준일", width="small"),
            "종목": st.column_config.TextColumn("종목", width="small"),
            "D0 사유": st.column_config.TextColumn("D0 사유", width="large"),
            "D0 거래대금": st.column_config.TextColumn("D0 거래대금", width="small"),
            "거래량 순위": st.column_config.TextColumn("거래량 순위", width="small"),
            "거래대금 순위": st.column_config.TextColumn("거래대금 순위", width="small"),
            "등락률": st.column_config.TextColumn("등락률", width="small"),
            "D0 고가": st.column_config.TextColumn("D0 고가", width="small"),
            "현재가": st.column_config.TextColumn("현재가", width="small"),
            "D0 고가 대비": st.column_config.TextColumn("D0 고가 대비", width="small"),
            "D0 대비 거래량": st.column_config.TextColumn("D0 대비 거래량", width="small"),
            "감시 상태": st.column_config.TextColumn("감시 상태", width="small"),
            "오래됨": st.column_config.TextColumn("오래됨", width="small"),
        },
    )


def render_webhook_candidates(score: pd.DataFrame, picks: pd.DataFrame, enriched: pd.DataFrame) -> None:
    """오늘의 웹훅 후보 — 1년치 복기와 같은 차트 패널 디자인.
    슬롯 탭(Top1/Top2/Rank3) → 차트 → 4컬럼 정보 패널(종목/시간대가격/수급공시/글로벌)."""
    st.subheader("오늘의 웹훅 후보")
    if score.empty:
        st.warning("score_breakdown 파일이 없습니다.")
        return

    score = score.copy()
    score["rank_int"] = pd.to_numeric(score.get("rank", 0), errors="coerce").fillna(0).astype(int)
    main_df = score[score["rank_int"].between(1, 3)].copy()
    log_df = score[score["rank_int"].between(4, 5)].copy()
    signal_date = str(score["signal_date"].iloc[0]) if "signal_date" in score.columns and not score.empty else ""

    # === 헤더 ===
    header_cols = st.columns([2.0, 1, 1, 1, 1])
    with header_cols[0]:
        st.markdown("기준일")
        st.markdown(f'<div class="cb-period">{signal_date}</div>', unsafe_allow_html=True)
    header_cols[1].metric("본문 후보", int((main_df["role"] == "BODY_TOP2").sum()) if "role" in main_df else 0)
    header_cols[2].metric("참고 후보", int((main_df["role"] == "REFERENCE_RANK3").sum()) if "role" in main_df else 0)
    header_cols[3].metric("보조 후보", len(log_df))
    header_cols[4].metric("D+1~D+5 추적", len(picks))

    st.markdown(
        '<div class="cb-note"><span class="cb-badge cb-top2">🟢 본문 후보</span> 2개 + '
        '<span class="cb-badge cb-rank3">🟡 참고 후보</span> 1개가 이 화면의 핵심입니다. '
        '<span class="cb-badge cb-log">⚪ 보조 후보</span>는 아래 expander에 분리. 점수·후보는 이 화면에서 바꾸지 않습니다.</div>',
        unsafe_allow_html=True,
    )

    # === enriched 인덱스 (코드별) ===
    enriched_idx: dict[str, dict[str, Any]] = {}
    if not enriched.empty:
        for _, row in enriched.iterrows():
            enriched_idx[normalize_code(row.get("stock_code", ""))] = row.to_dict()

    # === 슬롯 lookup ===
    slot_lookup: dict[str, dict[str, Any]] = {}
    for _, row in main_df.iterrows():
        rank_int = int(row.get("rank_int", 0))
        role_text = str(row.get("role", "")).strip()
        for key, rank, role, _label, _cls in SLOT_DEFINITIONS:
            if rank_int == rank and role_text == role:
                live_d = row.to_dict()
                code_local = normalize_code(live_d.get("stock_code", ""))
                slot_lookup[key] = {"live": live_d, "enriched": enriched_idx.get(code_local), "code": code_local}
                break

    available = [k for k in SLOT_KEYS if k in slot_lookup]
    if not available:
        st.info("Top1/Top2/Rank3에 해당하는 후보가 없습니다.")
        # 보조 후보만이라도 표시
        if not log_df.empty:
            with st.expander(f"보조 후보 (Log4/Log5) {len(log_df)}건"):
                _show_log_candidates(log_df)
        return

    # === 슬롯 탭 ===
    def _slot_label_today(key: str) -> str:
        entry = slot_lookup.get(key)
        if not entry:
            return f"{key} —"
        live = entry["live"]
        return f"{key}  ({SLOT_BY_KEY[key][3]} · {live.get('score', '')}점)"

    slot_state = "today_v2_slot"
    if slot_state not in st.session_state or st.session_state[slot_state] not in available:
        st.session_state[slot_state] = available[0]
    selected_slot = st.radio(
        "종목 슬롯",
        available,
        format_func=_slot_label_today,
        horizontal=True,
        key=slot_state,
        label_visibility="collapsed",
    )

    entry = slot_lookup[selected_slot]
    live_dict = entry["live"]
    enriched_row = entry.get("enriched")
    code = entry["code"]
    # enriched와 score를 합쳐 left card에 사용 (live가 우선)
    merged = {**(enriched_row or {}), **live_dict}

    # === 차트 상단바: 종목명 + role + 점수 ===
    role_v = str(live_dict.get("role", ""))
    role_short = ROLE_LABELS.get(role_v, role_v)
    badge_cls = "cb-top2" if role_v == "BODY_TOP2" else ("cb-rank3" if role_v == "REFERENCE_RANK3" else "cb-log")
    st.markdown(
        f'<div style="font-size:1.2rem; font-weight:700; padding-top:6px;">'
        f'{live_dict.get("stock_name", "")} <span class="cb-key">{code}</span> '
        f'<span class="cb-badge {badge_cls}">{role_short}</span> '
        f'<span class="cb-badge cb-review">{live_dict.get("score", "")}점</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # === 차트 ===
    chart_info: dict[str, Any] = dict(merged)
    chart_info["signal_date"] = signal_date
    chart_info["stock_code"] = code
    plot_minute_chart(load_minute(code), chart_info, key_prefix=f"today_v2_{signal_date}_{selected_slot}_{code}")

    # === 5컬럼 정보 패널 ===
    info_cols = st.columns([1.2, 1.0, 1.1, 1.0, 1.0])
    with info_cols[0]:
        render_left_info_card(merged)
    with info_cols[1]:
        render_intraday_price_card(enriched_row)
    with info_cols[2]:
        render_supply_disclosure_card(enriched_row)
    with info_cols[3]:
        render_global_index_card(signal_date)
    with info_cols[4]:
        render_financials_card(code)

    # === 보조 후보 expander ===
    if not log_df.empty:
        with st.expander(f"보조 후보 (Log4/Log5) — 메시지 미발송 점검용 {len(log_df)}건"):
            _show_log_candidates(log_df)
    return


def _show_log_candidates(log_df: pd.DataFrame) -> None:
    """오늘의 웹훅 후보 화면 보조 후보 표 (Log4/Log5)."""
    log_table = pd.DataFrame()
    log_table["순위"] = log_df["rank"].astype(str)
    log_table["종목"] = log_df.apply(lambda r: f"{r.get('stock_name', '')} ({normalize_code(r.get('stock_code', ''))})", axis=1)
    log_table["점수"] = log_df.get("score", "")
    if "policy_decision" in log_df.columns:
        log_table["정책"] = log_df["policy_decision"].map(policy_label)
    if "warning_codes" in log_df.columns:
        log_table["경고"] = log_df["warning_codes"].map(warning_labels)
    st.dataframe(log_table.reset_index(drop=True), use_container_width=True, hide_index=True, height=140)


def _legacy_render_webhook_candidates_table(score: pd.DataFrame, picks: pd.DataFrame) -> None:
    """이전 표 기반 화면 — 호출 안 함, 참고용."""
    out = display_candidates(score, picks)
    if out.empty:
        return
    out["rank_int"] = pd.to_numeric(out.get("rank", 0), errors="coerce").fillna(0).astype(int)
    main_df = out[out["rank_int"].between(1, 3)].copy()
    log_df = out[out["rank_int"].between(4, 5)].copy()

    # 핵심 3개 — 친절한 한글 표 (구분에 색 이모지 prefix: 본문=🟢 / 참고=🟡 / 보조=⚪)
    def _role_with_dot(label_text: str) -> str:
        if "본문" in label_text:
            return f"🟢 {label_text}"
        if "참고" in label_text:
            return f"🟡 {label_text}"
        if "보조" in label_text:
            return f"⚪ {label_text}"
        return label_text

    main_table = pd.DataFrame()
    main_table["순위"] = main_df["rank"].astype(str)
    main_table["구분"] = main_df["role_label"].map(_role_with_dot)
    main_table["종목"] = main_df.apply(lambda r: f"{r.get('stock_name', '')} ({normalize_code(r.get('stock_code', ''))})", axis=1)
    main_table["기준일"] = main_df.get("signal_date", "")
    main_table["점수"] = main_df.get("score", "")
    main_table["정책 판단"] = main_df["policy_label"]
    if "data_confidence" in main_df.columns:
        main_table["데이터 확신도"] = main_df["data_confidence"].map(confidence_label)
    main_table["점수 근거"] = main_df["score_reason_label"]
    main_table["경고"] = main_df["warning_label"]
    if "d1_d5_tracking_saved" in main_df.columns:
        main_table["D+1~D+5 저장"] = main_df["d1_d5_tracking_saved"]
    st.dataframe(
        main_table.reset_index(drop=True), use_container_width=True, hide_index=True, height=260,
        column_config={
            "종목": st.column_config.TextColumn("종목", width="medium"),
            "정책 판단": st.column_config.TextColumn("정책 판단", width="medium"),
            "점수 근거": st.column_config.TextColumn("점수 근거", width="large"),
            "경고": st.column_config.TextColumn("경고", width="medium"),
        },
    )

    if not log_df.empty:
        with st.expander(f"보조 후보 (Log4/Log5) — 메시지에 안 올라가는 점검용 {len(log_df)}건", expanded=False):
            log_table = pd.DataFrame()
            log_table["순위"] = log_df["rank"].astype(str)
            log_table["종목"] = log_df.apply(lambda r: f"{r.get('stock_name', '')} ({normalize_code(r.get('stock_code', ''))})", axis=1)
            log_table["점수"] = log_df.get("score", "")
            log_table["정책"] = log_df["policy_label"]
            log_table["경고"] = log_df["warning_label"]
            st.dataframe(log_table.reset_index(drop=True), use_container_width=True, hide_index=True, height=120)


def _format_pct(value: Any, default: str = "—") -> str:
    n = numeric(value)
    if n is None:
        return default
    sign = "+" if n > 0 else ""
    return f"{sign}{n:.1f}%"


def _slot_mini_cell(slot_key: str, slot_label_short: str, entry: dict[str, Any] | None) -> str:
    """미니 성과 요약줄 한 셀."""
    if not entry:
        return f'<span class="cb-mini-cell"><span class="cb-mini-key">{slot_key}</span>—</span>'
    review = entry.get("review")
    emoji, _, css = slot_outcome_color(review)
    if review:
        max_pct = _format_pct(review.get("outcome_max_high_return"))
        # max return 값을 표시해서 한눈에 결과 비교
        return f'<span class="cb-mini-cell"><span class="cb-mini-key">{slot_key}</span>{emoji} <span class="{css}">{max_pct}</span></span>'
    return f'<span class="cb-mini-cell"><span class="cb-mini-key">{slot_key}</span>{emoji}</span>'


def render_mini_performance_row(slot_lookup: dict[str, dict[str, Any]]) -> None:
    """5종목 한 줄 요약: Top1 🟢+7.2% Top2 🟢+3.1% ..."""
    cells = [_slot_mini_cell(key, SLOT_BY_KEY[key][3], slot_lookup.get(key)) for key in SLOT_KEYS]
    st.markdown(f'<div class="cb-mini-row">{"".join(cells)}</div>', unsafe_allow_html=True)


def render_date_navigator_with_dots(
    dates: list[str],
    review_index: dict[str, dict[str, dict[str, Any]]],
    live: pd.DataFrame,
    key_prefix: str,
) -> str:
    """날짜 네비게이터 + 옆에 5종목 결과 점.
    review_index: signal_date → code → review row dict (build_review_index 결과)
    live: 전체 live_safe_candidates_1y (해당 날짜의 슬롯 매핑용)
    """
    if not dates:
        return ""
    asc = sorted(set(str(d) for d in dates if str(d)))
    current_key = f"{key_prefix}_date"
    select_key = f"{key_prefix}_select"
    if current_key not in st.session_state or st.session_state[current_key] not in asc:
        st.session_state[current_key] = asc[-1]
    if select_key not in st.session_state or st.session_state[select_key] not in asc:
        st.session_state[select_key] = st.session_state[current_key]
    idx = asc.index(st.session_state[current_key])
    nav_cols = st.columns([1.2, 1.2, 2.5, 3.5, 3.0])
    with nav_cols[0]:
        if st.button("◀ 이전 거래일", key=f"{key_prefix}_prev", disabled=idx == 0, use_container_width=True):
            st.session_state[current_key] = asc[max(0, idx - 1)]
            st.session_state[select_key] = st.session_state[current_key]
            idx = asc.index(st.session_state[current_key])
    with nav_cols[1]:
        if st.button("다음 거래일 ▶", key=f"{key_prefix}_next", disabled=idx == len(asc) - 1, use_container_width=True):
            st.session_state[current_key] = asc[min(len(asc) - 1, idx + 1)]
            st.session_state[select_key] = st.session_state[current_key]
            idx = asc.index(st.session_state[current_key])
    with nav_cols[2]:
        order = st.radio("정렬", ["최신순", "과거순"], horizontal=True, key=f"{key_prefix}_order", label_visibility="collapsed")
    ordered = list(reversed(asc)) if order == "최신순" else asc
    with nav_cols[3]:
        selected = st.selectbox("날짜", ordered, index=ordered.index(st.session_state[current_key]), key=select_key, label_visibility="collapsed")
    st.session_state[current_key] = selected
    # 컬러 힌트 점
    with nav_cols[4]:
        day_live = live[live["signal_date"] == selected]
        slot_lookup = _build_slot_lookup_from_review_index(day_live, review_index.get(selected, {}))
        dots_html = []
        for key in SLOT_KEYS:
            entry = slot_lookup.get(key)
            if not entry:
                dots_html.append("·")
                continue
            emoji, _, _ = slot_outcome_color(entry.get("review"))
            dots_html.append(emoji)
        st.markdown(f'<div style="padding-top:6px;"><span class="cb-date-dots">{" ".join(dots_html)}</span></div>', unsafe_allow_html=True)
    return selected


def _build_slot_lookup_from_review_index(
    day_live: pd.DataFrame,
    review_for_date: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """선택 날짜의 live + 미리 인덱싱한 review로 슬롯 lookup 구성."""
    lookup: dict[str, dict[str, Any]] = {}
    if day_live.empty:
        return lookup
    for _, row in day_live.iterrows():
        key = slot_key_for_row(row.get("rank"), row.get("role"))
        if not key:
            continue
        live_dict = row.to_dict()
        code = normalize_code(live_dict.get("stock_code", ""))
        review_dict = review_for_date.get(code)
        lookup[key] = {"live": live_dict, "review": review_dict}
    return lookup


def render_left_info_card(live_dict: dict[str, Any]) -> None:
    """왼쪽 컬럼: 종목 기본 정보 + 점수 근거 + 경고."""
    name = live_dict.get("stock_name", "")
    code = normalize_code(live_dict.get("stock_code", ""))
    role = str(live_dict.get("role", ""))
    role_short = ROLE_LABELS.get(role, role)
    badge_cls = "cb-top2" if role == "BODY_TOP2" else ("cb-rank3" if role == "REFERENCE_RANK3" else "cb-log")
    score = live_dict.get("score", "")
    policy = policy_label(live_dict.get("policy_decision", ""))
    d0_date = str(live_dict.get("d0_date", ""))[:10]
    days_after = live_dict.get("days_after_D0", "")
    distance = live_dict.get("distance_from_d0_high_pct", "")
    distance_n = numeric(distance)
    distance_cls = "cb-val-neg" if (distance_n is not None and distance_n < 0) else "cb-val-pos"
    distance_text = f"{distance_n:+.1f}%" if distance_n is not None else (str(distance) or "—")
    confidence = confidence_label(live_dict.get("data_confidence", ""))
    vol_ratio = live_dict.get("volume_ratio_vs_20d", "")
    vol_n = numeric(vol_ratio)
    vol_text = f"{vol_n:.2f}x" if vol_n is not None else (str(vol_ratio) or "—")

    reasons = [p.strip() for p in str(live_dict.get("score_reasons", "") or "").replace(";", "|").replace(",", "|").split("|") if p.strip()]
    warnings = [p.strip() for p in str(live_dict.get("warning_codes", "") or "").replace(";", "|").replace(",", "|").split("|") if p.strip()]

    parts = [
        '<div class="cb-info-card">',
        f'<h4>종목 정보 <span class="cb-badge {badge_cls}">{role_short}</span></h4>',
        f'<div style="font-size:1.05rem; font-weight:700; margin-bottom:8px;">{name} <span class="cb-key">({code})</span></div>',
        f'<div class="cb-row"><span class="cb-key">D0 날짜</span><span class="cb-val">{d0_date or "—"}</span></div>',
        f'<div class="cb-row"><span class="cb-key">D0 이후</span><span class="cb-val">{days_after}거래일</span></div>',
        f'<div class="cb-row"><span class="cb-key">정책 판단</span><span class="cb-val">{policy}</span></div>',
        f'<div class="cb-row"><span class="cb-key">D0 고가 대비</span><span class="cb-val {distance_cls}">{distance_text}</span></div>',
        f'<div class="cb-row"><span class="cb-key">20일 대비 거래량</span><span class="cb-val">{vol_text}</span></div>',
        f'<div class="cb-row"><span class="cb-key">데이터 확신도</span><span class="cb-val">{confidence or "—"}</span></div>',
        f'<div class="cb-row"><span class="cb-key">점수</span><span class="cb-val">{score}</span></div>',
    ]
    parts.append('<div class="cb-section-title">점수 근거</div><div>')
    if reasons:
        for r in reasons:
            label_text = SCORE_REASON_LABELS.get(r, r)
            parts.append(f'<span class="cb-tag">{label_text}</span>')
    else:
        parts.append('<span class="cb-key">— 점수 근거 없음 —</span>')
    parts.append('</div>')
    parts.append('<div class="cb-section-title">경고</div><div>')
    if warnings:
        for w in warnings:
            label_text = WARNING_LABELS.get(w, w)
            parts.append(f'<span class="cb-tag cb-tag-warn">🚨 {label_text}</span>')
    else:
        parts.append('<span class="cb-tag cb-tag-good">특이 경고 없음</span>')
    parts.append('</div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_center_review_card(review_dict: dict[str, Any] | None, *, show_outcome: bool) -> None:
    """가운데 컬럼: REVIEW 결과 카드. show_outcome=False면 가린 표시."""
    if not show_outcome:
        st.markdown(
            '<div class="cb-info-card">'
            '<h4>D+5 복기 결과</h4>'
            '<div class="cb-key" style="padding:30px 0; text-align:center; line-height:1.7;">'
            '🔒 결과 숨김 모드<br>'
            '<span style="font-size:0.82rem;">사전 느낌을 먼저 정리한 뒤<br>차트 상단 토글로 결과를 열어 보세요.</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return
    if not review_dict:
        st.markdown(
            '<div class="cb-info-card"><h4>D+5 복기 결과</h4>'
            '<div class="cb-key">이 종목의 REVIEW 결과 행이 없습니다. 미래 D+1~D+5 미도래 또는 추적 미생성일 수 있습니다.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    plus1 = is_truthy(review_dict.get("outcome_d1_d5_plus1_touch"))
    plus2 = is_truthy(review_dict.get("outcome_d1_d5_plus2_touch"))
    plus3 = is_truthy(review_dict.get("outcome_d1_d5_plus3_touch"))
    minus2 = is_truthy(review_dict.get("outcome_d1_d5_minus2_touch"))
    f1 = str(review_dict.get("first_plus1_day", "")).strip()
    f2 = str(review_dict.get("first_plus2_day", "")).strip()
    f3 = str(review_dict.get("first_plus3_day", "")).strip()
    fm = str(review_dict.get("first_minus2_day", "")).strip()
    order = str(review_dict.get("target3_vs_risk2_order", "")).strip()
    order_text = order_label(order)
    if order == "TARGET3_FIRST":
        order_cls = "cb-tag-good"
        order_emoji = "🟢"
    elif order == "RISK2_FIRST":
        order_cls = "cb-tag-warn"
        order_emoji = "🔴"
    elif order in {"SAME_DAY_ORDER_UNKNOWN", "TARGET3_ONLY", "RISK2_ONLY"}:
        order_cls = "cb-tag-info"
        order_emoji = "🟡"
    else:
        order_cls = "cb-tag"
        order_emoji = "⚪"

    max_h = numeric(review_dict.get("outcome_max_high_return"))
    min_l = numeric(review_dict.get("outcome_min_low_return"))

    def _row(label_text: str, hit: bool, day_text: str, hit_word: str = "도달", miss_word: str = "미도달") -> str:
        if hit:
            day_label = f"D+{day_text}" if day_text else hit_word
            return f'<div class="cb-row"><span class="cb-key">✓ {label_text}</span><span class="cb-val cb-val-pos">{day_label}</span></div>'
        return f'<div class="cb-row"><span class="cb-key">— {label_text}</span><span class="cb-val cb-key">{miss_word}</span></div>'

    def _row_minus(label_text: str, hit: bool, day_text: str) -> str:
        if hit:
            day_label = f"D+{day_text}" if day_text else "터치"
            return f'<div class="cb-row"><span class="cb-key">✗ {label_text}</span><span class="cb-val cb-val-neg">{day_label}</span></div>'
        return f'<div class="cb-row"><span class="cb-key">— {label_text}</span><span class="cb-val cb-key">미터치</span></div>'

    parts = ['<div class="cb-info-card">', '<h4>D+5 복기 결과</h4>']
    parts.append(_row("+1% 도달", plus1, f1))
    parts.append(_row("+2% 도달", plus2, f2))
    parts.append(_row("+3% 도달", plus3, f3))
    parts.append(_row_minus("-2% 터치", minus2, fm))
    parts.append(f'<div style="margin: 10px 0 6px;"><span class="cb-tag {order_cls}">{order_emoji} {order_text}</span></div>')

    # 최고/최저 progress bar
    parts.append('<div class="cb-section-title">최고 / 최저 수익률</div>')
    if max_h is not None:
        max_w = min(abs(max_h) / 10.0 * 100, 100)  # 10% 기준 풀바
        parts.append(f'<div class="cb-row"><span class="cb-key">최고</span><span class="cb-val cb-val-pos">{max_h:+.1f}%</span></div>')
        parts.append(f'<div class="cb-progress-wrap"><div class="cb-progress-bar cb-progress-pos" style="width:{max_w:.1f}%;"></div></div>')
    if min_l is not None:
        min_w = min(abs(min_l) / 10.0 * 100, 100)
        parts.append(f'<div class="cb-row"><span class="cb-key">최저</span><span class="cb-val cb-val-neg">{min_l:+.1f}%</span></div>')
        parts.append(f'<div class="cb-progress-wrap"><div class="cb-progress-bar cb-progress-neg" style="width:{min_w:.1f}%;"></div></div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_right_note_panel(
    notes_path: Path,
    selected_date: str,
    live_dict: dict[str, Any],
    notes_df: pd.DataFrame,
) -> None:
    """오른쪽 컬럼: 메모 입력/저장."""
    code = normalize_code(live_dict.get("stock_code", ""))
    name = str(live_dict.get("stock_name", ""))
    rank = str(live_dict.get("rank", ""))
    role = str(live_dict.get("role", ""))

    existing = pd.DataFrame()
    if not notes_df.empty and "signal_date" in notes_df.columns and "stock_code" in notes_df.columns:
        existing = notes_df[
            (notes_df["signal_date"].astype(str) == str(selected_date))
            & (notes_df["stock_code"].map(normalize_code) == code)
        ]
    has_note = not existing.empty
    existing_row = existing.iloc[0].to_dict() if has_note else {}
    confidence_existing = str(existing_row.get("confidence_by_user", ""))

    st.markdown('<div class="cb-info-card"><h4>메모</h4>', unsafe_allow_html=True)

    # 데이터 품질 경고가 있으면 메모 작성자에게 참고문구를 표시 (자동 작성은 하지 않음 — 판단은 사람이)
    _q_warn = quality_warning_text_for(code, selected_date)
    if _q_warn:
        st.markdown(
            '<div class="cb-key" style="font-size:0.78rem; background:rgba(246,173,85,0.10); '
            'border-left:3px solid #f6ad55; padding:4px 8px; margin:2px 0 8px; border-radius:4px; line-height:1.5;">'
            f'💡 참고: {_q_warn.replace(" / ", " · ")}<br>'
            '<span style="font-size:0.72rem;">→ 이 종목 메모에 「선후관계 판단 주의」를 적어 두면 나중에 통계 해석할 때 도움이 됩니다.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    key_base = f"one_year_v2_note_{selected_date}_{code}"
    field_values: dict[str, str] = {}
    for field, label_text, placeholder in NOTE_FIELDS:
        field_values[field] = st.text_area(
            label_text,
            value=str(existing_row.get(field, "") or ""),
            key=f"{key_base}_{field}",
            placeholder=placeholder,
            height=72,
        )
    confidence_options = ["", "낮음", "보통", "높음", "매우 높음"]
    conf_index = confidence_options.index(confidence_existing) if confidence_existing in confidence_options else 0
    confidence = st.selectbox(
        "확신도",
        confidence_options,
        index=conf_index,
        key=f"{key_base}_confidence",
        format_func=lambda v: v if v else "미입력",
    )

    btn_cols = st.columns([1.0, 1.0, 1.0])
    with btn_cols[0]:
        save_clicked = st.button("💾 저장", key=f"{key_base}_save", use_container_width=True, type="primary")
    with btn_cols[1]:
        delete_clicked = st.button("🗑 삭제", key=f"{key_base}_delete", use_container_width=True, disabled=not has_note)
    with btn_cols[2]:
        st.caption(f"수정: {existing_row.get('updated_at', '—')}" if has_note else "신규")

    if save_clicked:
        payload = {
            "review_date": datetime.now().date().isoformat(),
            "signal_date": selected_date,
            "stock_code": code,
            "stock_name": name,
            "rank": rank,
            "role": role,
            "confidence_by_user": confidence,
            **field_values,
        }
        try:
            upsert_user_note(notes_path, payload)
            st.success("메모를 저장했습니다.")
            st.rerun()
        except Exception as exc:
            st.error(f"저장 실패: {exc}")
    if delete_clicked and has_note:
        try:
            delete_user_note(notes_path, selected_date, code)
            st.success("메모를 삭제했습니다.")
            st.rerun()
        except Exception as exc:
            st.error(f"삭제 실패: {exc}")
    st.markdown('</div>', unsafe_allow_html=True)


def _format_money_short(value: Any, default: str = "—") -> str:
    """원 단위 금액 → '+1.2조', '+1,234억', '-567만' 형식."""
    n = numeric(value)
    if n is None:
        return default
    abs_n = abs(n)
    if abs_n >= 1_0000_0000_0000:
        return f"{n / 1_0000_0000_0000:+,.2f}조"
    if abs_n >= 1_0000_0000:
        return f"{n / 1_0000_0000:+,.1f}억"
    if abs_n >= 10000:
        return f"{n / 10000:+,.0f}만"
    return f"{n:+,.0f}"


def fmt_eok_to_human(value_in_eok: Any, default: str = "—") -> str:
    """억 단위 숫자 → '1조 4,710억' (1조 이상) 또는 '541억' (1조 미만).

    Used by 종목 상세 카드 B/C 거래대금 표시.
    """
    try:
        if value_in_eok is None or (isinstance(value_in_eok, float) and pd.isna(value_in_eok)):
            return default
        v = float(value_in_eok)
    except (TypeError, ValueError):
        return default
    if v <= 0:
        return f"{v:,.0f}억"
    if v >= 10000:  # 1조 = 10,000억
        jo = int(v // 10000)
        eok = int(round(v - jo * 10000))
        if eok == 0:
            return f"{jo}조"
        return f"{jo}조 {eok:,}억"
    if v >= 100:
        return f"{v:,.0f}억"
    return f"{v:,.1f}억"


def fmt_pct(value: Any, default: str = "—", sign: bool = True) -> str:
    """% 값 → 소수점 한 자리 통일. sign=True면 +/- 부호 표시."""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        v = float(value)
    except (TypeError, ValueError):
        return default
    return f"{v:+.1f}%" if sign else f"{v:.1f}%"


def render_intraday_price_card(enriched_row: dict[str, Any] | None) -> None:
    """오늘 14:15 → 14:30 → 14:55 → 15:00 가격 흐름 + VWAP."""
    parts = ['<div class="cb-info-card"><h4>14:15 → 15:00 흐름</h4>']
    if not enriched_row:
        parts.append('<div class="cb-key">enriched 데이터 없음</div></div>')
        st.markdown("".join(parts), unsafe_allow_html=True)
        return
    p1415 = numeric(enriched_row.get("preclose_price_1415"))
    p1430 = numeric(enriched_row.get("preclose_price_1430"))
    p1455 = numeric(enriched_row.get("snapshot_price_1455"))
    p1500 = numeric(enriched_row.get("signal_price_1500"))
    vwap = numeric(enriched_row.get("vwap_until_1500"))
    vol = numeric(enriched_row.get("minute_volume_1415_1500"))

    def _row(label_text: str, n: float | None, *, signal: bool = False) -> str:
        if n is None:
            return ""
        suffix = " (신호가)" if signal else ""
        return f'<div class="cb-row"><span class="cb-key">{label_text}{suffix}</span><span class="cb-val">{n:,.0f}</span></div>'

    parts.append(_row("14:15", p1415))
    parts.append(_row("14:30", p1430))
    parts.append(_row("14:55", p1455))
    parts.append(_row("15:00", p1500, signal=True))
    if p1415 and p1500:
        change = (p1500 - p1415) / p1415 * 100
        cls = "cb-val-pos" if change >= 0 else "cb-val-neg"
        parts.append(f'<div class="cb-row"><span class="cb-key">14:15 → 15:00 변동</span><span class="cb-val {cls}">{change:+.2f}%</span></div>')
    if vwap is not None:
        parts.append(f'<div class="cb-row"><span class="cb-key">VWAP (~15:00)</span><span class="cb-val">{vwap:,.0f}</span></div>')
    if vol is not None:
        parts.append(f'<div class="cb-row"><span class="cb-key">14:15~15:00 거래량</span><span class="cb-val">{int(vol):,}</span></div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_supply_disclosure_card(enriched_row: dict[str, Any] | None, code: str = "", signal_date: str = "") -> None:
    """수급(외인/기관/프로그램/공매도) + 최근 공시 카운트. code/signal_date 주면 0값/결측 audit 안내 추가."""
    parts = ['<div class="cb-info-card"><h4>수급 / 공시</h4>']
    if not enriched_row:
        parts.append('<div class="cb-key">enriched 데이터 없음</div></div>')
        st.markdown("".join(parts), unsafe_allow_html=True)
        return
    foreign = enriched_row.get("foreign_net_latest")
    inst = enriched_row.get("institution_net_latest")
    program = enriched_row.get("program_net_latest")
    short_ratio = numeric(enriched_row.get("short_sale_ratio_latest"))
    supply_status = _safe_text(enriched_row.get("supply_freshness_status"))
    program_status = _safe_text(enriched_row.get("program_status"))
    good = numeric(enriched_row.get("recent_good_disclosure_count")) or 0
    bad = numeric(enriched_row.get("recent_bad_disclosure_count")) or 0
    total = numeric(enriched_row.get("recent_disclosure_count")) or 0

    def _money_row(label_text: str, value: Any) -> str:
        text = str(value or "").strip()
        if not text or text.lower() == "nan":
            # 결측: 0처럼 보이지 않게 명시
            return f'<div class="cb-row"><span class="cb-key">{label_text}</span><span class="cb-val cb-key">데이터 없음</span></div>'
        n = numeric(value)
        if n is None:
            return f'<div class="cb-row"><span class="cb-key">{label_text}</span><span class="cb-val cb-key">데이터 없음</span></div>'
        if n == 0:
            return (f'<div class="cb-row"><span class="cb-key">{label_text}</span>'
                    f'<span class="cb-val">0 <span class="cb-key" style="font-size:0.76rem;">(실제 0)</span></span></div>')
        cls = "cb-val-pos" if n > 0 else "cb-val-neg"
        return f'<div class="cb-row"><span class="cb-key">{label_text}</span><span class="cb-val {cls}">{_format_money_short(n)}</span></div>'

    parts.append(_money_row("외인 순매수", foreign))
    parts.append(_money_row("기관 순매수", inst))
    parts.append(_money_row("프로그램 순매수", program))
    if short_ratio is not None:
        cls = "cb-val-warn" if short_ratio >= 5 else "cb-val"
        parts.append(f'<div class="cb-row"><span class="cb-key">공매도 비율</span><span class="cb-val {cls}">{short_ratio:.2f}%</span></div>')
    supply_label_map = {
        "fresh": "최신",
        "ok": "정상",
        "stale": "오래됨",
        "missing": "데이터 없음",
        "diagnostic_only": "진단용만",
        "diagnostic_only_or_missing": "진단용 또는 미보유",
    }
    if supply_status and supply_status != "—":
        supply_text = supply_label_map.get(supply_status.lower(), supply_status)
        parts.append(f'<div class="cb-row"><span class="cb-key">수급 신선도</span><span class="cb-val">{supply_text}</span></div>')
    # 프로그램 상태는 데이터 부족으로 표시 생략 (사용자 피드백 반영)

    parts.append('<div class="cb-section-title">최근 공시</div>')
    parts.append(f'<div class="cb-row"><span class="cb-key">전체</span><span class="cb-val">{int(total)}건</span></div>')
    if good > 0:
        parts.append(f'<div class="cb-row"><span class="cb-key">호재</span><span class="cb-val cb-val-pos">{int(good)}건</span></div>')
    if bad > 0:
        parts.append(f'<div class="cb-row"><span class="cb-key">악재</span><span class="cb-val cb-val-neg">{int(bad)}건</span></div>')
    if total == 0:
        parts.append('<div class="cb-key">최근 공시 없음</div>')

    # 수급 0값/결측 audit 안내 (Codex zero_value_root_cause_audit)
    if code and signal_date:
        supply_audit = [
            r for r in zero_value_rows_for(code, signal_date)
            if any(k in str(r.get("data_layer", "")).lower() for k in ("foreign", "institution", "supply", "program"))
        ]
        if supply_audit:
            zts = {str(r.get("zero_or_missing_type", "")) for r in supply_audit}
            if "REAL_ZERO_SOURCE_ROW_PRESENT" in zts:
                parts.append('<div class="cb-key" style="margin-top:6px; font-size:0.78rem;">💸 일부 수급 값이 <b>실제 0</b>입니다 (그날 순매수 없음). 결측이 아닙니다.</div>')
            if zts & {"MISSING_VALUE", "PARTIAL_VALUE", "MISSING_FILE", "MISSING_DATE"}:
                parts.append('<div class="cb-key" style="margin-top:4px; font-size:0.78rem;">💸 일부 수급 값이 <b>결측</b>입니다 (확인 중) — 점수 판단에 사용하지 않습니다. 0으로 채우지 않습니다.</div>')

    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_daily_chart_with_ma(code: str, signal_date: str) -> None:
    """일봉 + MA(5/8/20/33/60/120) + 거래량 — 종목 상세용 큰 그림."""
    df = load_daily(code)
    if df.empty:
        st.info("일봉 parquet이 없습니다.")
        return
    signal_dt = pd.to_datetime(signal_date) if signal_date else df["date"].max()
    # 최근 6개월 + signal_date 이후 한 달
    start = signal_dt - pd.Timedelta(days=180)
    end = signal_dt + pd.Timedelta(days=30)
    view = df[(df["date"] >= start) & (df["date"] <= end)].copy()
    if view.empty:
        st.info("일봉 데이터 범위 부족")
        return
    if not (go and make_subplots):
        st.line_chart(view.set_index("date")[["close"] + [f"ma{w}" for w in MA_WINDOWS]])
        return
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.74, 0.26], vertical_spacing=0.04)
    fig.add_trace(
        go.Candlestick(
            x=view["date"], open=view["open"], high=view["high"], low=view["low"], close=view["close"],
            name="OHLC", increasing_line_color="#7ee0a1", decreasing_line_color="#ff8a8a",
        ), row=1, col=1,
    )
    ma_colors = {5: "#fbb6ce", 8: "#9ecbff", 20: "#fbd38d", 33: "#b794f4", 60: "#68d391", 120: "#a0aec0"}
    for w in MA_WINDOWS:
        col = f"ma{w}"
        if col not in view.columns:
            continue
        fig.add_trace(go.Scatter(
            x=view["date"], y=view[col], mode="lines", name=f"MA{w}",
            line={"width": 1.2, "color": ma_colors.get(w, "#888")},
        ), row=1, col=1)
    fig.add_trace(go.Bar(x=view["date"], y=view["volume"], name="거래량", marker_color="#5a6068"), row=2, col=1)
    # signal_date 수직선
    fig.add_shape(
        type="line", x0=signal_dt, x1=signal_dt, y0=0, y1=1,
        xref="x", yref="paper", line={"color": "#ffd166", "width": 1.5, "dash": "dash"},
    )
    fig.add_annotation(
        x=signal_dt, y=1, xref="x", yref="paper", text="신호일", showarrow=False,
        yanchor="bottom", font={"size": 11, "color": "#ffd166"},
    )
    _apply_light_chart_layout(fig, height=480, legend_y=1.08, top_margin=60)
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], row=1, col=1, tickformat="%Y.%m.%d")
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], row=2, col=1, tickformat="%Y.%m.%d")
    # 가격축 auto-zoom
    try:
        prices = pd.concat([view["high"], view["low"], view["close"]]).dropna()
        prices = prices[prices > 0]
        if not prices.empty:
            y_lo = float(prices.min()) * 0.97
            y_hi = float(prices.max()) * 1.03
            if y_hi > y_lo:
                fig.update_yaxes(range=[y_lo, y_hi], row=1, col=1)
    except Exception:  # noqa: BLE001
        pass
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


def render_investor_flow_table(code: str, signal_date: str, lookback_days: int = 22) -> None:
    """일별 매매주체 표 (외국인/기관 순매수). 신호일 기준 최근 N거래일.

    프로그램 컬럼은 데이터 커버리지가 낮아 (Codex supply_dart audit 기준 80~169개/2800+ 종목)
    표시 가치가 작다고 판단해 제거 (사용자 2026-05-21 피드백).
    """
    inst = load_inst_trade(code)
    if inst.empty:
        st.warning(
            "외국인/기관 수급 데이터가 없습니다. "
            "원천 미제공이거나 종목별 수집 누락일 수 있습니다."
        )
        return

    signal_dt = pd.to_datetime(signal_date) if signal_date else None
    if signal_dt is not None:
        end = signal_dt + pd.Timedelta(days=10)
        start = signal_dt - pd.Timedelta(days=lookback_days * 2)
        inst = inst[(inst["date"] >= start) & (inst["date"] <= end)]

    if inst.empty:
        st.caption(
            f"신호일 {signal_date} 기준 ±{lookback_days}거래일 범위에 수급 데이터가 없습니다. "
            "외인/기관 데이터가 종목·기간별로 결손될 수 있습니다."
        )
        return

    merged = inst[["date", "for_daly_nettrde_qty", "orgn_daly_nettrde_qty", "trde_qty", "close_pric"]].copy()
    merged = merged.sort_values("date", ascending=False).head(lookback_days)
    out = pd.DataFrame()
    out["일자"] = merged["date"].dt.strftime("%Y-%m-%d")
    if "close_pric" in merged.columns:
        out["종가"] = merged["close_pric"].astype(str).str.replace(r"^\+", "", regex=True)
    out["외국인 순매수(주)"] = merged["for_daly_nettrde_qty"].apply(lambda v: f"{int(v):+,}" if pd.notna(v) else "—")
    out["기관 순매수(주)"] = merged["orgn_daly_nettrde_qty"].apply(lambda v: f"{int(v):+,}" if pd.notna(v) else "—")
    if "trde_qty" in merged.columns:
        out["거래량"] = merged["trde_qty"].apply(lambda v: f"{int(v):,}" if pd.notna(v) else "—")

    # 결손 일자 카운트
    missing_for = int(merged["for_daly_nettrde_qty"].isna().sum())
    missing_org = int(merged["orgn_daly_nettrde_qty"].isna().sum())
    total = len(merged)
    note_parts = ["표시 정책: **0** = 실제 0 / **—** = 원천 행 없음·미제공"]
    if missing_for or missing_org:
        note_parts.append(
            f"표시 {total}일 중 결손: 외인 {missing_for}일 / 기관 {missing_org}일"
        )
    st.caption(" · ".join(note_parts))
    st.dataframe(out.reset_index(drop=True), use_container_width=True, hide_index=True, height=420)


def render_investor_flow_chart(code: str, signal_date: str, lookback_days: int = 60) -> None:
    """매매주체 차트 — 외국인/기관 순매수 (프로그램 제거, 사용자 2026-05-21 피드백)."""
    inst = load_inst_trade(code)
    if inst.empty:
        return
    signal_dt = pd.to_datetime(signal_date) if signal_date else None
    if signal_dt is not None:
        end = signal_dt + pd.Timedelta(days=10)
        start = signal_dt - pd.Timedelta(days=lookback_days * 2)
        inst = inst[(inst["date"] >= start) & (inst["date"] <= end)]
    if inst.empty or not (go and make_subplots):
        return
    fig = go.Figure()
    fig.add_trace(go.Bar(x=inst["date"], y=inst["for_daly_nettrde_qty"], name="외국인", marker_color="#9ecbff"))
    fig.add_trace(go.Bar(x=inst["date"], y=inst["orgn_daly_nettrde_qty"], name="기관", marker_color="#7ee0a1"))
    if signal_dt is not None:
        fig.add_shape(type="line", x0=signal_dt, x1=signal_dt, y0=0, y1=1,
                      xref="x", yref="paper", line={"color": "#ffd166", "width": 1.2, "dash": "dash"})
        fig.add_annotation(
            x=signal_dt, y=1, xref="x", yref="paper",
            text="신호일", showarrow=False, yanchor="bottom",
            font={"size": 11, "color": "#d97706"},
        )
    _apply_light_chart_layout(fig, height=280, legend_y=1.14, top_margin=60)
    fig.update_layout(barmode="relative", yaxis={"title": "주식 수"})
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


WARN_KEYWORDS_FINANCIALS = (
    "유상증자", "전환사채", "감자", "거래정지", "관리종목",
    "상장폐지", "불성실공시", "소송", "횡령", "배임", "감사의견",
)


@st.cache_data(show_spinner=False)
def load_recent_disclosure_30d() -> pd.DataFrame:
    """dart/recent_30d.parquet 로드 (전체 종목 최근 30일 공시 인덱스)."""
    p = DART_DIR / "recent_30d.parquet"
    if not p.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(p)
        if "stock_code" in df.columns:
            df["stock_code"] = df["stock_code"].astype(str).str.zfill(6)
        return df
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


def render_financials_card(stock_code: str, name: str = "", market: str = "", signal_date: str = "") -> None:
    """기업 개요 + DART 재무 + 최근 공시 + 위험 키워드 매칭.

    Codex Claude handoff (2026-05-18) 권장:
    - 기업 개요(회사명/코드/시장)
    - 신호일 시점 이전 30일 DART 공시 5건 + 위험 키워드 배지
    - 신호일 시점 안내를 붙인 최신 수집 분기 매출/영업이익/당기순이익

    2026-05-21 사용자 피드백 반영:
    - 공시는 신호일 시점 이전 30일로 필터
    - 재무는 현재 finstate_ts의 최신 수집 분기를 표시하되, 신호일 이후 공시 가능성을 경고
    - PER/PBR/ROE/시가총액은 현재 수집 데이터에 없어 "미수집"으로 통일
    """
    code6 = normalize_code(stock_code)
    sig_dt = pd.to_datetime(signal_date).date() if signal_date else None

    # ── 1) 기업 개요 카드
    parts = ['<div class="cb-info-card"><h4>기업 개요</h4>']
    if name:
        parts.append(f'<div class="cb-row"><span class="cb-key">회사명</span><span class="cb-val">{name}</span></div>')
    parts.append(f'<div class="cb-row"><span class="cb-key">종목코드</span><span class="cb-val">{code6}</span></div>')
    if market:
        parts.append(f'<div class="cb-row"><span class="cb-key">시장</span><span class="cb-val">{market}</span></div>')
    parts.append(
        '<div class="cb-row" style="opacity:0.65;"><span class="cb-key">PER / PBR / ROE</span>'
        '<span class="cb-val cb-key">미수집 (추후 보강)</span></div>'
    )
    parts.append(
        '<div class="cb-row" style="opacity:0.65;"><span class="cb-key">시가총액 / 상장일</span>'
        '<span class="cb-val cb-key">미수집 (추후 보강)</span></div>'
    )
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

    # ── 2) DART 공시 — 신호일 시점 이전 30일 (사용자 피드백 2026-05-21)
    disc = load_recent_disclosure_30d()
    title_text = f"신호일 {signal_date} 이전 30일 DART 공시" if sig_dt else "최근 DART 공시 (30일)"
    parts = [f'<div class="cb-info-card"><h4>{title_text}</h4>']
    rows = pd.DataFrame()
    if not disc.empty and "stock_code" in disc.columns:
        sub = disc[disc["stock_code"] == code6].copy()
        if sig_dt is not None and not sub.empty:
            sub["_rcept_d"] = pd.to_datetime(sub["rcept_dt"], format="%Y%m%d", errors="coerce").dt.date
            start_dt = sig_dt - timedelta(days=30)
            sub = sub[(sub["_rcept_d"] <= sig_dt) & (sub["_rcept_d"] >= start_dt)]
        rows = sub.sort_values("rcept_dt", ascending=False).head(5)
    if rows.empty:
        if sig_dt is not None:
            parts.append(f'<div class="cb-key">신호일 {signal_date} 이전 30일간 공시 없음</div>')
        else:
            parts.append('<div class="cb-key">DART 공시 데이터 없음</div>')
    else:
        for _, dr in rows.iterrows():
            rcept = str(dr.get("rcept_dt", ""))
            rcept_fmt = f"{rcept[:4]}-{rcept[4:6]}-{rcept[6:8]}" if len(rcept) >= 8 else rcept
            title = str(dr.get("report_nm", "")).strip()
            warn_hits = [k for k in WARN_KEYWORDS_FINANCIALS if k in title]
            badge = (
                f' <span style="color:#dc2626; font-weight:600;">⚠️ {", ".join(warn_hits)}</span>'
                if warn_hits else ""
            )
            parts.append(
                f'<div class="cb-row"><span class="cb-key">{rcept_fmt}</span>'
                f'<span class="cb-val" style="font-size:0.9rem;">{title}{badge}</span></div>'
            )
        parts.append(
            f'<div class="cb-key" style="font-size:0.78rem; margin-top:6px;">'
            f'위험 키워드: {" / ".join(WARN_KEYWORDS_FINANCIALS)}'
            '</div>'
        )
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

    # ── 3) DART 재무 (기존 finstate_ts 기반)
    parts = ['<div class="cb-info-card"><h4>최근 재무 (DART)</h4>']
    corp = find_corp_code(stock_code)
    if not corp:
        parts.append('<div class="cb-key">DART corp_code 매핑 없음 (비상장·신규상장 가능)</div></div>')
        st.markdown("".join(parts), unsafe_allow_html=True)
        return
    fin = load_finstate(corp)
    if not fin or not any(k in fin for k in ("매출액", "영업이익", "당기순이익")):
        parts.append(f'<div class="cb-key">finstate_ts 데이터 없음 (corp_code: {corp})</div></div>')
        st.markdown("".join(parts), unsafe_allow_html=True)
        return
    year = fin.get("_year", "")
    fs_div_text = "연결" if fin.get("_fs_div") == "CFS" else ("별도" if fin.get("_fs_div") == "OFS" else fin.get("_fs_div", ""))
    parts.append(f'<div class="cb-key" style="margin-bottom:8px;">{year} ({fs_div_text}) · corp {corp}</div>')
    for label_text in ["매출액", "영업이익", "당기순이익", "기본 EPS", "희석 EPS"]:
        if label_text not in fin:
            parts.append(
                f'<div class="cb-row"><span class="cb-key">{label_text}</span>'
                f'<span class="cb-val cb-key">—</span></div>'
            )
            continue
        item = fin[label_text]
        this_n = numeric(item["this"])
        prev_n = numeric(item["prev"])
        # EPS는 원 단위 그대로 표시 (조/억 변환 부적절), 손익은 _format_money_short
        if label_text in ("기본 EPS", "희석 EPS"):
            text = f"{this_n:+,.0f}원" if this_n is not None else "—"
        else:
            text = _format_money_short(this_n) if this_n is not None else "—"
        cls_main = "cb-val-pos" if (this_n is not None and this_n > 0) else ("cb-val-neg" if this_n is not None and this_n < 0 else "cb-val")
        delta_text = ""
        if this_n is not None and prev_n is not None and prev_n != 0:
            delta = (this_n - prev_n) / abs(prev_n) * 100
            cls_delta = "cb-val-pos" if delta >= 0 else "cb-val-neg"
            delta_text = f' <span class="{cls_delta}">({delta:+.1f}%)</span>'
        parts.append(
            f'<div class="cb-row"><span class="cb-key">{label_text}</span>'
            f'<span class="cb-val {cls_main}">{text}{delta_text}</span></div>'
        )
    # 신호일 시점 안내 — finstate는 가장 최신 분기 기준이라 신호일 이후 발표일 수 있음
    if sig_dt is not None:
        parts.append(
            '<div class="cb-key" style="margin-top:8px; font-size:0.76rem; '
            'background:rgba(246,173,85,0.10); border-left:3px solid #f6ad55; '
            'padding:5px 8px; border-radius:4px;">'
            f'⚠ 표시된 재무는 가장 최신 분기 기준입니다. 신호일 {signal_date} 시점에서는 '
            '아직 공시되지 않은 분기일 수 있으니 해석 시 주의 (시점별 분기 정확 매핑은 추후 보강 예정). '
            '전년 대비 증감률 동시 표시.'
            '</div>'
        )
    else:
        parts.append('<div class="cb-key" style="margin-top:6px; font-size:0.78rem;">전년 대비 증감률 표시</div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_global_index_card(target_date: str) -> None:
    """signal_date 기준 글로벌 지수 한 줄."""
    g = global_row_for_date(target_date)
    if not g:
        st.markdown(
            '<div class="cb-info-card"><h4>글로벌 지수</h4>'
            '<div class="cb-key">global_merged.csv 데이터 없음</div></div>',
            unsafe_allow_html=True,
        )
        return
    items = [
        ("KOSPI", g.get("kospi_close"), g.get("kospi_change_pct")),
        ("KOSDAQ", g.get("kosdaq_close"), g.get("kosdaq_change_pct")),
        ("나스닥", g.get("nasdaq_close"), g.get("nasdaq_change_pct")),
        ("S&P 500", g.get("sp500_close"), g.get("sp500_change_pct")),
        ("USD/KRW", g.get("usdkrw_close"), g.get("usdkrw_change_pct")),
        ("VIX", g.get("vix_close"), g.get("vix_change_pct")),
    ]
    parts = [f'<div class="cb-info-card"><h4>글로벌 지수 <span class="cb-key">({g.get("date","")})</span></h4>']
    for label, close, chg in items:
        chg_n = numeric(chg)
        close_n = numeric(close)
        cls = "cb-val-pos" if (chg_n is not None and chg_n >= 0) else "cb-val-neg"
        chg_text = f"{chg_n:+.2f}%" if chg_n is not None else "—"
        if close_n is None:
            close_text = "—"
        elif close_n > 1000:
            close_text = f"{close_n:,.1f}"
        else:
            close_text = f"{close_n:,.2f}"
        parts.append(
            f'<div class="cb-row"><span class="cb-key">{label}</span>'
            f'<span class="cb-val">{close_text} <span class="{cls}">({chg_text})</span></span></div>'
        )
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_one_year_backdata(score: pd.DataFrame | None = None, enriched: pd.DataFrame | None = None) -> None:
    """1년치 backdata 복기 + 종목 상세 통합. 가장 최근 날짜는 오늘 운영 데이터.
    score/enriched는 오늘 데이터(외인/공시/글로벌/재무) 추가 패널 표시용 — 신호일과 매칭 시에만 표시."""
    st.subheader("1년치 복기 + 종목 상세")
    backtest_dir_text = latest_backtest_dir()
    if not backtest_dir_text:
        st.warning("1년치 backdata run_manifest가 아직 없습니다.")
        return
    backtest_dir = Path(backtest_dir_text)
    live = read_csv(str(backtest_dir / "live_safe_candidates_1y.csv"))
    review = read_csv(str(backtest_dir / "review_outcomes_1y.csv"))
    d0_pool = read_csv(str(backtest_dir / "d0_pool_1y.csv"))
    manifest = read_json(str(backtest_dir / "run_manifest.json"))
    notes = read_csv(str(USER_NOTES_PATH))
    review_index = build_review_index(str(backtest_dir / "review_outcomes_1y.csv"))

    # enriched 인덱스 (오늘 데이터일 때 패널 표시용)
    enriched_idx: dict[str, dict[str, Any]] = {}
    enriched_signal_date = ""
    if enriched is not None and not enriched.empty:
        for _, row in enriched.iterrows():
            enriched_idx[normalize_code(row.get("stock_code", ""))] = row.to_dict()
        if "signal_date" in enriched.columns:
            enriched_signal_date = str(enriched["signal_date"].iloc[0])

    # === 헤더 ===
    header_cols = st.columns([2.2, 1, 1, 1, 1])
    with header_cols[0]:
        st.markdown("기간")
        st.markdown(
            f'<div class="cb-period">{manifest.get("start_date", "")} ~ {manifest.get("end_date", "")}</div>',
            unsafe_allow_html=True,
        )
    header_cols[1].metric("거래일", manifest.get("trading_days", ""))
    header_cols[2].metric("D0 감시 전체", len(d0_pool))
    header_cols[3].metric("웹훅 후보", len(live))
    header_cols[4].metric("작성한 메모", len(notes))

    st.markdown(
        '<div class="cb-note">'
        '이 화면은 <b>비AI backdata</b>입니다. D0 조건은 임시 조건이며 운영 점수 변경이 아닙니다. '
        '<b>날짜 → 종목 탭 → 차트 → 정보 패널</b> 순서로 한 번에 복기합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    if live.empty:
        st.warning("live_safe_candidates_1y.csv가 비어 있습니다.")
        return

    # === 날짜 네비 + 컬러 힌트 ===
    dates = sorted(live["signal_date"].dropna().unique().tolist(), reverse=True)
    selected_date = render_date_navigator_with_dots(dates, review_index, live, "one_year_v2")

    day_live = live[live["signal_date"] == selected_date].copy()
    review_for_date = review_index.get(selected_date, {})
    slot_lookup = _build_slot_lookup_from_review_index(day_live, review_for_date)

    # === 5종목 미니 성과 요약줄 ===
    render_mini_performance_row(slot_lookup)

    # === 종목 슬롯 탭 (Top1|Top2|Rank3|Log4|Log5) ===
    available_keys = [key for key in SLOT_KEYS if key in slot_lookup]
    if not available_keys:
        st.info("선택 날짜의 후보 행이 없습니다.")
        return

    def _slot_label(key: str) -> str:
        _, _, _, label_short, _ = SLOT_BY_KEY[key]
        entry = slot_lookup.get(key)
        if not entry:
            return f"{key} —"
        live_dict = entry["live"]
        score_v = live_dict.get("score", "")
        return f"{key}  ({label_short} · {score_v}점)"

    slot_key_state = "one_year_v2_slot"
    if slot_key_state not in st.session_state or st.session_state[slot_key_state] not in available_keys:
        st.session_state[slot_key_state] = available_keys[0]
    selected_slot = st.radio(
        "종목 슬롯",
        available_keys,
        format_func=_slot_label,
        horizontal=True,
        key=slot_key_state,
        label_visibility="collapsed",
    )

    entry = slot_lookup[selected_slot]
    live_dict = entry["live"]
    review_dict = entry.get("review")
    code = normalize_code(live_dict.get("stock_code", ""))

    # === 차트 상단바: 종목명 + role + 점수 + 사전/사후 토글 ===
    head_cols = st.columns([5.5, 2.5])
    with head_cols[0]:
        role_v = str(live_dict.get("role", ""))
        role_short = ROLE_LABELS.get(role_v, role_v)
        badge_cls = "cb-top2" if role_v == "BODY_TOP2" else ("cb-rank3" if role_v == "REFERENCE_RANK3" else "cb-log")
        st.markdown(
            f'<div style="font-size:1.2rem; font-weight:700; padding-top:6px;">'
            f'{live_dict.get("stock_name", "")} <span class="cb-key">{code}</span> '
            f'<span class="cb-badge {badge_cls}">{role_short}</span> '
            f'<span class="cb-badge cb-review">{live_dict.get("score", "")}점</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with head_cols[1]:
        toggle_key = "one_year_v2_show_outcome"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False
        outcome_choice = st.radio(
            "결과 표시",
            ["🔒 결과 숨김", "👁 결과 표시"],
            horizontal=True,
            key=f"{toggle_key}_radio",
            index=1 if st.session_state[toggle_key] else 0,
            label_visibility="collapsed",
        )
        st.session_state[toggle_key] = outcome_choice.startswith("👁")
    show_outcome = st.session_state[toggle_key]

    # === 데이터 품질 배지 (Codex dashboard_data_quality_badges 우선, 없으면 audit heuristic) ===
    _future_dates_for_badge = [d.isoformat() for d in trading_days_after(code, str(selected_date), 5)]
    render_quality_badge_row(code, selected_date, extra_dates=_future_dates_for_badge)
    _audit_rows = zero_value_rows_for(code, selected_date)
    if _audit_rows:
        with st.expander(f"⚠️ 데이터 품질 상세 ({len(_audit_rows)}건) — 0값/결측 원인 분류 (Codex audit)"):
            _qdf = pd.DataFrame(_audit_rows)
            _qcols = [c for c in ["data_layer", "expected_date", "field_name", "observed_value", "zero_or_missing_type", "possible_reason", "halt_or_warning_status", "confidence", "recommended_treatment", "notes"] if c in _qdf.columns]
            st.dataframe(_qdf[_qcols], use_container_width=True, hide_index=True, height=min(320, 60 + len(_audit_rows) * 36))
            st.caption("0값 ≠ 무조건 오류. 실제 0 / 거래정지 / 결측 / 수집오류 구분. 이 데이터는 점수 판단에 사용하지 않습니다 (표시·안내만).")

    # === 차트 ===
    plot_one_year_minute_chart(
        load_minute(code),
        live_dict,
        review_dict,
        show_outcome=show_outcome,
        key_prefix=f"one_year_v2_{selected_date}_{selected_slot}_{code}",
    )

    # === 정보 3컬럼 ===
    info_cols = st.columns([1.2, 1.0, 1.3])
    with info_cols[0]:
        render_left_info_card(live_dict)
    with info_cols[1]:
        render_center_review_card(review_dict, show_outcome=show_outcome)
    with info_cols[2]:
        render_right_note_panel(USER_NOTES_PATH, selected_date, live_dict, notes)

    # === 종목 상세 — 오늘 데이터일 때만 외인/공시/글로벌/재무 4컬럼 ===
    is_today = bool(enriched_signal_date) and str(selected_date) == enriched_signal_date
    enriched_row = enriched_idx.get(code) if is_today else None
    if enriched_row:
        st.markdown('<div class="cb-section-title">📡 오늘 운영 데이터 (14:15→15:00 / 수급 / 글로벌 / 재무)</div>', unsafe_allow_html=True)
        today_cols = st.columns(4)
        with today_cols[0]:
            render_intraday_price_card(enriched_row)
        with today_cols[1]:
            render_supply_disclosure_card(enriched_row, code=code, signal_date=selected_date)
        with today_cols[2]:
            render_global_index_card(selected_date)
        with today_cols[3]:
            render_financials_card(code)
    else:
        # 오늘 enriched가 없는 과거 신호여도 글로벌·재무는 표시 가능
        st.markdown('<div class="cb-section-title">🌐 글로벌 지수 / 최근 재무</div>', unsafe_allow_html=True)
        gf_cols = st.columns(2)
        with gf_cols[0]:
            render_global_index_card(selected_date)
        with gf_cols[1]:
            render_financials_card(code)

    # === MTS 같은 종목 상세: 일봉(MA) + 매매주체 ===
    with st.expander("📊 일봉 차트 + 매매주체 흐름 (MTS 스타일)", expanded=True):
        st.markdown('<div class="cb-section-title">일봉 (MA 5/8/20/33/60/120) — 신호일 ±6개월</div>', unsafe_allow_html=True)
        render_daily_chart_with_ma(code, selected_date)
        flow_cols = st.columns([1.6, 1.0])
        with flow_cols[0]:
            st.markdown('<div class="cb-section-title">일별 매매주체 (외국인 / 기관 / 프로그램, 신호일 ±)</div>', unsafe_allow_html=True)
            render_investor_flow_chart(code, selected_date, lookback_days=60)
        with flow_cols[1]:
            st.markdown('<div class="cb-section-title">최근 표</div>', unsafe_allow_html=True)
            render_investor_flow_table(code, selected_date, lookback_days=22)

    # === 보조 후보 (Log4/Log5) expander ===
    log_rows = []
    for log_key, rank, role, label_short in LOG_SLOT_DEFINITIONS:
        sub = day_live[
            (day_live["rank"].astype(str) == str(rank)) & (day_live["role"] == role)
        ]
        if sub.empty:
            continue
        live_d = sub.iloc[0].to_dict()
        code_l = normalize_code(live_d.get("stock_code", ""))
        review_d = review_for_date.get(code_l)
        emoji, summary, _ = slot_outcome_color(review_d)
        max_pct = _format_pct(review_d.get("outcome_max_high_return")) if review_d else "—"
        min_pct = _format_pct(review_d.get("outcome_min_low_return")) if review_d else "—"
        log_rows.append({
            "슬롯": log_key,
            "구분": label_short,
            "종목": f"{live_d.get('stock_name', '')} ({code_l})",
            "점수": live_d.get("score", ""),
            "정책": policy_label(live_d.get("policy_decision", "")),
            "결과": f"{emoji} {summary}",
            "최고": max_pct,
            "최저": min_pct,
        })
    if log_rows:
        with st.expander(f"보조 후보 (Log4/Log5) — 핵심 분석 대상 아님, 점검용", expanded=False):
            st.caption("본문 후보(Top1/Top2)와 참고 후보(Rank3)만 깊이 분석합니다. 보조 후보는 점수 흐름과 결과만 가볍게 점검합니다.")
            st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)

    # === 하단 안내 ===
    ref_price, ref_label = reference_price(live_dict)
    ref_text = f"{ref_label}({ref_price:,.0f})" if ref_price else "기준가 미확인"
    with st.expander("이 화면에서 보는 것 / 데이터 위치"):
        st.markdown(
            f"""
- **차트**: 분봉(기본 30분, 5/15분 전환) + VWAP, {ref_text} 기준 +1/+2/+3% 목표선과 -2% 손절선
- **결과 점**: 🟢 +3% 먼저 / 🔴 -2% 먼저 / 🟡 +1·+2까지 또는 같은 날 / ⚪ 미도달
- **메모 CSV**: `{USER_NOTES_PATH}` (저장 시 `.bak` 백업 1개 유지)
- **백테스트 디렉토리**: `{backtest_dir}`
- **사전/사후 토글**은 이 1년치 탭에 자체 적용 — 다른 탭과 독립
"""
        )


def _safe_text(value: Any, default: str = "—") -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return default
    return text


def render_notes_browser() -> None:
    """메모 모아보기: 검색·필터·결과 색깔별 분류."""
    st.subheader("메모 모아보기")
    notes = read_csv(str(USER_NOTES_PATH))
    if notes.empty:
        st.info("아직 작성한 메모가 없습니다. **1년치 복기** 탭에서 종목 선택 후 메모 저장 → 여기서 모아 볼 수 있습니다.")
        return

    backtest_dir_text = latest_backtest_dir()
    review_index = build_review_index(str(Path(backtest_dir_text) / "review_outcomes_1y.csv")) if backtest_dir_text else {}

    # 메모에 결과 색 컬럼 추가
    enriched_notes = notes.copy()
    color_emojis: list[str] = []
    color_labels: list[str] = []
    max_pcts: list[str] = []
    for _, row in enriched_notes.iterrows():
        sd = str(row.get("signal_date", ""))
        code = normalize_code(row.get("stock_code", ""))
        review_d = review_index.get(sd, {}).get(code)
        emoji, summary, _ = slot_outcome_color(review_d)
        color_emojis.append(emoji)
        color_labels.append(summary)
        max_pcts.append(_format_pct(review_d.get("outcome_max_high_return")) if review_d else "—")
    enriched_notes["결과"] = [f"{e} {l}" for e, l in zip(color_emojis, color_labels)]
    enriched_notes["최고"] = max_pcts
    enriched_notes["color_only"] = color_emojis

    # === 필터 ===
    filter_cols = st.columns([1.5, 1.5, 1.0, 2.5])
    all_dates = sorted(enriched_notes["signal_date"].dropna().astype(str).unique())
    with filter_cols[0]:
        start_date = st.selectbox("시작일", ["전체"] + all_dates, key="notes_filter_start")
    with filter_cols[1]:
        end_date = st.selectbox("종료일", ["전체"] + all_dates, key="notes_filter_end")
    with filter_cols[2]:
        color_filter = st.multiselect("결과", ["🟢", "🔴", "🟡", "⚪"], default=[], key="notes_filter_color")
    with filter_cols[3]:
        keyword = st.text_input("메모 본문 키워드", key="notes_filter_keyword", placeholder="패턴/사후 생각 등에서 검색")

    filtered = enriched_notes.copy()
    if start_date != "전체":
        filtered = filtered[filtered["signal_date"].astype(str) >= start_date]
    if end_date != "전체":
        filtered = filtered[filtered["signal_date"].astype(str) <= end_date]
    if color_filter:
        filtered = filtered[filtered["color_only"].isin(color_filter)]
    if keyword:
        kw_lower = keyword.lower()
        text_cols = ["user_view_before_result", "user_view_after_result", "pattern_note", "mistake_note", "next_rule_idea"]
        mask = pd.Series(False, index=filtered.index)
        for col in text_cols:
            if col in filtered.columns:
                mask = mask | filtered[col].astype(str).str.lower().str.contains(kw_lower, na=False)
        filtered = filtered[mask]

    st.caption(f"전체 메모 {len(notes)}건 중 {len(filtered)}건 표시")

    if filtered.empty:
        st.info("필터 조건에 맞는 메모가 없습니다.")
        return

    # === 메모 카드 리스트 ===
    for _, row in filtered.iterrows():
        sd = str(row.get("signal_date", ""))
        code = normalize_code(row.get("stock_code", ""))
        name = str(row.get("stock_name", ""))
        rank = str(row.get("rank", ""))
        role_text = role_label(row.get("role", ""))
        result = str(row.get("결과", ""))
        max_pct = str(row.get("최고", ""))
        confidence = str(row.get("confidence_by_user", "") or "—")
        updated = str(row.get("updated_at", "") or "—")

        with st.container():
            head = (
                f'<div style="font-size:1.05rem; font-weight:700; padding-top:6px;">'
                f'{result} · {name} <span class="cb-key">({code})</span> '
                f'<span class="cb-badge cb-review">{role_text} · rank {rank}</span> '
                f'<span class="cb-key">{sd} · 최고 {max_pct} · 확신도 {confidence}</span>'
                f'</div>'
            )
            st.markdown(head, unsafe_allow_html=True)
            note_cols = st.columns(3)
            with note_cols[0]:
                v = str(row.get("user_view_before_result", "") or "").strip()
                if v:
                    st.markdown(f"**사전 느낌**\n\n{v}")
            with note_cols[1]:
                v = str(row.get("user_view_after_result", "") or "").strip()
                if v:
                    st.markdown(f"**사후 생각**\n\n{v}")
                v = str(row.get("pattern_note", "") or "").strip()
                if v:
                    st.markdown(f"**패턴 메모**\n\n{v}")
            with note_cols[2]:
                v = str(row.get("mistake_note", "") or "").strip()
                if v:
                    st.markdown(f"**놓친 점**\n\n{v}")
                v = str(row.get("next_rule_idea", "") or "").strip()
                if v:
                    st.markdown(f"**다음 점검 아이디어**\n\n{v}")
            st.caption(f"수정: {updated}")
            st.divider()


def render_stats() -> None:
    """1년치 backdata 기반 점수 분포 + 적중률 통계."""
    st.subheader("점수 분포 · 적중률 통계")
    backtest_dir_text = latest_backtest_dir()
    if not backtest_dir_text:
        st.warning("1년치 backdata가 없습니다.")
        return
    backtest_dir = Path(backtest_dir_text)
    live = read_csv(str(backtest_dir / "live_safe_candidates_1y.csv"))
    review = read_csv(str(backtest_dir / "review_outcomes_1y.csv"))
    if live.empty or review.empty:
        st.warning("backdata 파일이 비어 있습니다.")
        return

    st.markdown(
        '<div class="cb-note">1년치 backdata 기반. <b>점수 = 신호 당시 점수, 결과 = D+1~D+5 사후</b>. '
        '점수가 미래 예측력이 있는지(높은 점수일수록 +3% 도달률↑, -2% 터치율↓) 한눈에 확인.<br>'
        '<span class="cb-subtle">점수 구간 <code>~30</code>은 0~30점. 이 backdata에는 <b>0점 종목이 없습니다</b> (최저 약 30점, 모두 보조·참고 후보). '
        '0점은 일일 운영의 별개 점수 모델(score_candidate)에서만 나오며 — D0 이후 시간이 길거나, 데이터 확신도가 낮거나, 손절 위험이 큰 "감점 요인이 매우 많은 종목"을 뜻합니다.</span></div>',
        unsafe_allow_html=True,
    )

    # === merge: live + review (signal_date + stock_code) ===
    live = live.copy()
    review = review.copy()
    live["score_n"] = pd.to_numeric(live.get("score", 0), errors="coerce")
    live["rank_n"] = pd.to_numeric(live.get("rank", 0), errors="coerce")
    merged = live.merge(
        review,
        on=["signal_date", "stock_code", "rank", "role"],
        suffixes=("", "_r"),
        how="left",
    )
    if merged.empty:
        st.info("merge 결과가 비어 있습니다.")
        return

    for col in ["outcome_d1_d5_plus1_touch", "outcome_d1_d5_plus2_touch", "outcome_d1_d5_plus3_touch", "outcome_d1_d5_minus2_touch"]:
        merged[col + "_b"] = merged.get(col, "").astype(str).str.lower().isin(["true", "1", "yes"])
    merged["max_h"] = pd.to_numeric(merged.get("outcome_max_high_return", ""), errors="coerce")
    merged["min_l"] = pd.to_numeric(merged.get("outcome_min_low_return", ""), errors="coerce")

    # === 전체 요약 ===
    total = len(merged)
    p3_total = int(merged["outcome_d1_d5_plus3_touch_b"].sum())
    p2_total = int(merged["outcome_d1_d5_plus2_touch_b"].sum())
    m2_total = int(merged["outcome_d1_d5_minus2_touch_b"].sum())
    summary_cols = st.columns(5)
    summary_cols[0].metric("표본 수", total)
    summary_cols[1].metric("+3% 도달률", f"{p3_total/total*100:.1f}%" if total else "—", help=f"{p3_total} / {total}")
    summary_cols[2].metric("+2% 도달률", f"{p2_total/total*100:.1f}%" if total else "—")
    summary_cols[3].metric("-2% 터치율", f"{m2_total/total*100:.1f}%" if total else "—")
    summary_cols[4].metric("평균 최고/최저", f"{merged['max_h'].mean():+.1f}% / {merged['min_l'].mean():+.1f}%")

    # === 점수 구간별 적중률 ===
    st.markdown('<div class="cb-section-title">점수 구간별 적중률</div>', unsafe_allow_html=True)
    bins = [-1, 30, 50, 60, 70, 80, 100]
    labels = ["~30", "31~50", "51~60", "61~70", "71~80", "81+"]
    merged["score_bin"] = pd.cut(merged["score_n"], bins=bins, labels=labels, include_lowest=True)
    grp = merged.groupby("score_bin", observed=True).agg(
        표본=("score_n", "count"),
        plus3=("outcome_d1_d5_plus3_touch_b", "sum"),
        plus2=("outcome_d1_d5_plus2_touch_b", "sum"),
        minus2=("outcome_d1_d5_minus2_touch_b", "sum"),
        평균최고=("max_h", "mean"),
        평균최저=("min_l", "mean"),
    ).reset_index()
    grp["+3% 도달률"] = (grp["plus3"] / grp["표본"] * 100).round(1).astype(str) + "%"
    grp["+2% 도달률"] = (grp["plus2"] / grp["표본"] * 100).round(1).astype(str) + "%"
    grp["-2% 터치율"] = (grp["minus2"] / grp["표본"] * 100).round(1).astype(str) + "%"
    grp["평균 최고"] = grp["평균최고"].round(2).astype(str) + "%"
    grp["평균 최저"] = grp["평균최저"].round(2).astype(str) + "%"
    grp = grp.rename(columns={"score_bin": "점수 구간"})
    st.dataframe(
        grp[["점수 구간", "표본", "+3% 도달률", "+2% 도달률", "-2% 터치율", "평균 최고", "평균 최저"]],
        use_container_width=True, hide_index=True,
    )

    # === Role별 적중률 ===
    st.markdown('<div class="cb-section-title">역할별 적중률 (본문 / 참고 / 보조)</div>', unsafe_allow_html=True)
    role_grp = merged.groupby("role").agg(
        표본=("score_n", "count"),
        plus3=("outcome_d1_d5_plus3_touch_b", "sum"),
        plus2=("outcome_d1_d5_plus2_touch_b", "sum"),
        minus2=("outcome_d1_d5_minus2_touch_b", "sum"),
        평균최고=("max_h", "mean"),
    ).reset_index()
    role_grp["역할"] = role_grp["role"].map(role_label)
    role_grp["+3% 도달률"] = (role_grp["plus3"] / role_grp["표본"] * 100).round(1).astype(str) + "%"
    role_grp["+2% 도달률"] = (role_grp["plus2"] / role_grp["표본"] * 100).round(1).astype(str) + "%"
    role_grp["-2% 터치율"] = (role_grp["minus2"] / role_grp["표본"] * 100).round(1).astype(str) + "%"
    role_grp["평균 최고"] = role_grp["평균최고"].round(2).astype(str) + "%"
    st.dataframe(
        role_grp[["역할", "표본", "+3% 도달률", "+2% 도달률", "-2% 터치율", "평균 최고"]],
        use_container_width=True, hide_index=True,
    )

    # === 역설 경고 ===
    # 점수 낮은 구간이 +3% 도달률·+3 먼저 비율이 더 높으면 경고
    bin_plus3 = merged.groupby("score_bin", observed=True)["outcome_d1_d5_plus3_touch_b"].mean()
    if not bin_plus3.empty and "~30" in bin_plus3.index:
        low_rate = bin_plus3.get("~30", 0)
        mid_rate = bin_plus3.get("51~60", bin_plus3.median())
        if low_rate > mid_rate + 0.05:
            st.markdown(
                f'<div class="cb-note" style="border-left-color:#ffd166; background:rgba(214,158,46,0.10);">'
                f'⚠️ <b>점수 역설</b>: 점수가 낮은 구간(<code>~30</code>, {low_rate*100:.1f}%)이 중간 구간(<code>51~60</code>, {mid_rate*100:.1f}%)보다 +3% 도달률이 높습니다. '
                f'점수 모델의 rank 가중치가 실제 성과와 역상관일 수 있어 재검토가 필요합니다. '
                f'<span class="cb-subtle">단 표본 60 미만 구간은 노이즈 가능 — 참고만.</span></div>',
                unsafe_allow_html=True,
            )

    # === D+1~D+5 일자별 누적 (점수 구간 × D+N) ===
    st.markdown('<div class="cb-section-title">D+1~D+5 일자별 누적 (점수 구간 × D+N)</div>', unsafe_allow_html=True)
    days3 = pd.to_numeric(merged.get("first_plus3_day", ""), errors="coerce")
    days2 = pd.to_numeric(merged.get("first_plus2_day", ""), errors="coerce")
    days1 = pd.to_numeric(merged.get("first_plus1_day", ""), errors="coerce")
    daysM = pd.to_numeric(merged.get("first_minus2_day", ""), errors="coerce")
    merged["_d3"], merged["_d2"], merged["_d1"], merged["_dM"] = days3, days2, days1, daysM
    order_col = merged.get("target3_vs_risk2_order", "").astype(str)
    merged["_target_first"] = order_col.isin(["TARGET3_FIRST", "TARGET3_ONLY"])
    merged["_risk_first"] = order_col.isin(["RISK2_FIRST", "RISK2_ONLY"])

    metric_choice = st.radio(
        "지표",
        ["+3% 누적 도달률", "+2% 누적 도달률", "+1% 누적 도달률", "-2% 누적 터치율", "+3 먼저 vs -2 먼저 비율"],
        horizontal=True, key="stats_dn_metric", label_visibility="collapsed",
    )
    col_map = {"+3% 누적 도달률": "_d3", "+2% 누적 도달률": "_d2", "+1% 누적 도달률": "_d1", "-2% 누적 터치율": "_dM"}
    rows_dn = []
    for lbl in labels:
        g = merged[merged["score_bin"] == lbl]
        n = len(g)
        if n == 0:
            continue
        if metric_choice == "+3 먼저 vs -2 먼저 비율":
            tf = g["_target_first"].sum()
            rf = g["_risk_first"].sum()
            rows_dn.append({
                "점수 구간": lbl, "표본": n,
                "+3 먼저": f"{tf/n*100:.1f}%", "-2 먼저": f"{rf/n*100:.1f}%",
                "같은날/없음": f"{(n-tf-rf)/n*100:.1f}%",
            })
        else:
            col = col_map[metric_choice]
            row = {"점수 구간": lbl, "표본": n}
            for d in [1, 2, 3, 4, 5]:
                row[f"D+{d}"] = f"{(g[col] <= d).sum()/n*100:.1f}%"
            rows_dn.append(row)
    st.dataframe(pd.DataFrame(rows_dn), use_container_width=True, hide_index=True)
    st.caption("누적 = D+1~D+N 사이에 한 번이라도 해당 수준을 터치한 비율 (first_*_day 컬럼 기준). 같은 날 +3/-2 동시 터치는 순서 미확인.")

    # === 전체 D+1~D+5 일자별 누적 곡선 (점수 무관) ===
    if go is not None:
        st.markdown('<div class="cb-section-title">전체 D+1~D+5 누적 곡선 (점수 무관)</div>', unsafe_allow_html=True)
        n_all = len(merged)
        cum = {}
        for name, col, color in [("+1%", "_d1", "#9ae6b4"), ("+2%", "_d2", "#68d391"), ("+3%", "_d3", "#38a169"), ("-2%", "_dM", "#fc8181")]:
            cum[name] = [(merged[col] <= d).sum() / n_all * 100 for d in [1, 2, 3, 4, 5]]
        fig_c = go.Figure()
        for name, color in [("+1%", "#9ae6b4"), ("+2%", "#68d391"), ("+3%", "#38a169"), ("-2%", "#fc8181")]:
            fig_c.add_trace(go.Scatter(x=["D+1", "D+2", "D+3", "D+4", "D+5"], y=cum[name], mode="lines+markers", name=name, line={"color": color, "width": 2}))
        fig_c.update_layout(
            height=300, template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 14, "r": 14, "t": 24, "b": 12},
            yaxis_title="누적 터치율 (%)", xaxis_title="",
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        )
        st.plotly_chart(fig_c, use_container_width=True)
        d1_p3, d1_m2 = cum["+3%"][0], cum["-2%"][0]
        d5_p3, d5_m2 = cum["+3%"][4], cum["-2%"][4]
        st.caption(f"D+1엔 -2%({d1_m2:.1f}%)가 +3%({d1_p3:.1f}%)보다 먼저 많이 닿음 → 단기엔 하방이 먼저. D+5쯤엔 +3%({d5_p3:.1f}%)와 -2%({d5_m2:.1f}%)가 거의 동률.")

    # === 점수 히스토그램 (Plotly) ===
    if go is not None:
        st.markdown('<div class="cb-section-title">점수 분포 히스토그램</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=merged["score_n"].dropna(), nbinsx=30, marker_color="#9ecbff", name="전체"))
        fig.add_trace(go.Histogram(x=merged.loc[merged["outcome_d1_d5_plus3_touch_b"], "score_n"].dropna(),
                                    nbinsx=30, marker_color="#7ee0a1", name="+3% 도달", opacity=0.75))
        fig.update_layout(
            barmode="overlay", height=320,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 14, "r": 14, "t": 24, "b": 12},
            xaxis_title="점수", yaxis_title="건수",
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("해석 가이드 / 점수 역설 메모"):
        st.markdown(
            "**점수에 예측력이 있다면:**\n"
            "- 점수 구간이 올라갈수록 +3% 도달률이 단조 증가해야 함\n"
            "- -2% 터치율이 높은 점수 구간에서 낮아져야 함\n"
            "- 평균 최고가 평균 최저보다 절댓값이 큰 구간이 매매에 유리\n\n"
            "**현재 backdata에서 관찰되는 역설 (2026-05-11 분석):**\n"
            "- `~30` 구간(rank3·4·5 중 감점 많은 종목)이 +3% 도달 89.7%, +3 먼저 39.7%, -2 먼저 17.2% — 모든 지표에서 가장 우수\n"
            "- `51~60` 구간(본문 후보 BODY_TOP2 위주)이 +3% 도달 77.2% — 가장 부진\n"
            "- 점수가 거의 rank의 함수 (51~60 이상은 본문 후보만, ~30은 rank3-5만) → 점수 구간 비교 = 사실상 rank 비교\n"
            "- 가능한 해석: ① 천장 효과(본문 후보=거래대금 1·2위=이미 큰 폭 상승=추가 +3% 여력 적음) ② 표본 불균형·노이즈(~30 표본 58개) ③ rank 가중치 부호 문제\n"
            "- → 점수 모델 재검토는 Codex 영역. 상세: `docs/closingbell/reports_summary/stats_deep_analysis_and_uiux_20260511.md`\n\n"
            "**주의:** touch rate는 실제 매매 승률이 아님 (일봉 high/low 기반 터치율). 같은 날 +3/-2 동시 터치는 순서 미확인. 표본 < 60 구간은 통계적 유의성 약함, 참고만."
        )


# === V2 차트 검증 (Codex 산출, 2026-05-13) ===
V2_CHART_AUDIT_DIR = CLOSINGBELL / "research_index" / "v2_chart_audit_20260513"
V2_TOP3_CHART_REVIEW_DIR = CLOSINGBELL / "research_index" / "v2_top3_chart_review_20260513"

V2_AUDIT_COLUMN_LABELS = {
    "stock_name": "종목",
    "stock_code": "코드",
    "score_total_100": "점수",
    "entry_basis": "진입 기준",
    "entry_price": "진입가",
    "mfe_5d_pct": "5일 안 최고수익률(%)",
    "mae_5d_pct": "5일 안 최대하락률(%)",
    "success_label": "결과",
    "result_group": "결과 그룹",
    "pattern_label": "패턴",
    "selection_name": "선정 방식",
    "variant_id": "variant",
    "sample_n": "표본",
    "win_n": "승리",
    "loss_n": "패배",
    "unknown_n": "애매",
    "win_rate_pct": "승률(%)",
    "loss_rate_pct": "패배율(%)",
    "avg_score": "평균 점수",
    "median_score": "중앙 점수",
    "top_failure_reason": "주요 실패 사유",
    "top_success_pattern": "주요 성공 패턴",
}

V2_ENTRY_BASIS_LABELS = {
    "D0_CLOSE": "D0 종가 진입 (연구 기준)",
    "D1_OPEN": "D+1 시가 진입",
}

V2_PATTERN_LABELS = {
    "STRONG_CLOSE_CONTINUATION": "강세종가 추세 지속",
    "THEME_MOMENTUM": "테마 모멘텀",
    "SHALLOW_PULLBACK_DEFENSE": "얕은 눌림 방어",
    "LOW_UPPER_WICK_CONTINUATION": "짧은 윗꼬리 지속",
    "DEEP_PULLBACK": "깊은 눌림 (실패)",
    "LONG_UPPER_WICK": "긴 윗꼬리 (실패)",
    "GAP_OVERHEAT": "갭 과열 (실패)",
    "D0_CLOSE_WEAK": "D0 종가 약세 (실패)",
    "UNKNOWN": "패턴 미상",
}

V2_TOP3_CASE_LABELS = {
    "WIN_FAST": "빠른 성공",
    "WIN_LATE": "늦은 성공",
    "LOSS_FAST": "빠른 실패",
    "LOSS_LATE": "늦은 실패",
    "TIME_EXIT": "시간청산",
    "BOTH_TOUCH": "동시/순서불명",
    "DATA_MISSING": "데이터 부족",
    "LOW_SCORE_HOLD": "점수 미달 보류",
}


@st.cache_data(show_spinner=False)
def load_v2_top3_chart_cases() -> pd.DataFrame:
    p = V2_TOP3_CHART_REVIEW_DIR / "v2_top3_chart_cases_20260513.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


@st.cache_data(show_spinner=False)
def load_v2_top3_chart_manifest() -> dict[str, Any]:
    p = V2_TOP3_CHART_REVIEW_DIR / "v2_top3_chart_manifest_20260513.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _v2_pct_text(value: Any) -> str:
    num = numeric(value)
    if num is None:
        return "—"
    return f"{num:+.2f}%"


def _v2_case_label(value: Any, fallback: Any = "") -> str:
    text = str(value or "").strip()
    if text in V2_TOP3_CASE_LABELS:
        return V2_TOP3_CASE_LABELS[text]
    return str(fallback or text or "—")


def _v2_bool_label(value: Any) -> str:
    return "Y" if str(value).strip().lower() in {"true", "1", "yes", "y"} else "N"


def _v2_show_case_table(rows: pd.DataFrame) -> None:
    if rows.empty:
        st.info("표시할 케이스가 없습니다.")
        return
    show = rows.copy()
    cols = [
        "signal_date",
        "rank",
        "policy_label_ko",
        "stock_code",
        "stock_name",
        "score_total_100",
        "signal_price_1500",
        "case_label_ko",
        "nextday_close_result_ko",
        "nextday_close_return_pct",
        "d5_mfe_pct",
        "d5_mae_pct",
        "hold_reason",
    ]
    show = show[[col for col in cols if col in show.columns]].rename(columns={
        "signal_date": "신호일",
        "rank": "순위",
        "policy_label_ko": "정책",
        "stock_code": "코드",
        "stock_name": "종목",
        "score_total_100": "V2 점수",
        "signal_price_1500": "15시 기준가",
        "case_label_ko": "분류",
        "nextday_close_result_ko": "D+1 +2/-2",
        "nextday_close_return_pct": "다음날 결과(%)",
        "d5_mfe_pct": "D+5 최고(%)",
        "d5_mae_pct": "D+5 최저(%)",
        "hold_reason": "보류 사유",
    })
    st.dataframe(show, use_container_width=True, hide_index=True, height=240)


def render_v2_top3_chart_review_section(cases: pd.DataFrame, manifest: dict[str, Any]) -> None:
    st.markdown("### V2 Top3 D+1~D+5 추적")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#60a5fa; background:rgba(96,165,250,0.10);">'
        '기존 LIVE P0 파일은 그대로 두고, 별도 산출물의 V2 Top3 백데이터를 읽는 복기 화면입니다.<br>'
        '<b>현재 매수/매도 추천이 아니며, 현재일 후보에는 미래 봉을 표시하지 않습니다.</b>'
        '</div>',
        unsafe_allow_html=True,
    )

    if cases.empty:
        st.info(f"V2 Top3 차트 검증 산출물이 없습니다. 경로: `{V2_TOP3_CHART_REVIEW_DIR}`")
        return

    view = cases.copy()
    view["rank_n"] = pd.to_numeric(view.get("rank", ""), errors="coerce")
    view = view.sort_values(["signal_date", "policy_key", "rank_n"], ascending=[False, True, True])
    v2 = view[view["policy_key"] == "V2_TOP3"].copy()
    chart_count = int(v2.get("chart_path_d5", pd.Series(dtype=str)).astype(str).str.len().gt(0).sum()) if not v2.empty else 0
    data_missing = int((v2.get("case_label", pd.Series(dtype=str)) == "DATA_MISSING").sum()) if not v2.empty else 0
    low_score = int((v2.get("case_label", pd.Series(dtype=str)) == "LOW_SCORE_HOLD").sum()) if not v2.empty else 0

    metric_cols = st.columns(5)
    metric_cols[0].metric("기간", "최근 22거래일")
    metric_cols[1].metric("V2 Top3 행", len(v2))
    metric_cols[2].metric("PNG 차트", chart_count)
    metric_cols[3].metric("데이터 부족", data_missing)
    metric_cols[4].metric("점수 보류", low_score)
    if manifest:
        st.caption(f"산출 시각: {manifest.get('created_at', '')} · 원본 LIVE P0/웹훅 발송 로직 미수정")

    control_cols = st.columns([1.5, 1.7, 2.2, 2.6])
    with control_cols[0]:
        horizon = st.radio("표시 기간", ["D+3", "D+5"], horizontal=True, key="v2_top3_horizon")
    with control_cols[1]:
        mode = st.radio("보기", ["V2 Top3", "P0 비교"], horizontal=True, key="v2_top3_mode")
    date_options = sorted(view["signal_date"].dropna().unique().tolist(), reverse=True)
    with control_cols[2]:
        selected_date = st.selectbox("신호일", date_options, key="v2_top3_signal_date")
    label_options = ["전체"] + sorted(v2["case_label_ko"].dropna().unique().tolist())
    with control_cols[3]:
        selected_label = st.selectbox("분류", label_options, key="v2_top3_case_filter")

    day_count = 3 if horizon == "D+3" else 5
    chart_col = "chart_path_d3" if day_count == 3 else "chart_path_d5"
    filtered = view[view["signal_date"] == selected_date].copy()
    if selected_label != "전체":
        filtered = filtered[filtered["case_label_ko"] == selected_label]

    if mode == "P0 비교":
        left, right = st.columns(2)
        with left:
            st.markdown("#### 기존 거래대금 Top3")
            _v2_show_case_table(filtered[filtered["policy_key"] == "P0_VALUE_TOP3"])
        with right:
            st.markdown("#### V2 Top3")
            _v2_show_case_table(filtered[filtered["policy_key"] == "V2_TOP3"])
        st.caption("비교 표는 같은 신호일의 기존 P0 Top3와 V2 Top3를 나란히 보기 위한 복기용입니다.")
        return

    rows = filtered[filtered["policy_key"] == "V2_TOP3"].copy().sort_values("rank_n")
    if rows.empty:
        st.info("선택 조건에 맞는 V2 Top3 케이스가 없습니다.")
        return

    for _, row in rows.iterrows():
        rank = str(row.get("rank", ""))
        code = normalize_code(row.get("stock_code", ""))
        name = str(row.get("stock_name", ""))
        label = _v2_case_label(row.get("case_label"), row.get("case_label_ko"))
        st.markdown(f"#### {selected_date} · {rank}위 · {name} (`{code}`) · {label}")
        cols = st.columns(6)
        cols[0].metric("V2 점수", _safe_text(row.get("score_total_100", ""), default="—"))
        cols[1].metric("15시 기준가", _safe_text(row.get("signal_price_1500", ""), default="—"))
        cols[2].metric("D+1 결과", _safe_text(row.get("nextday_close_result_ko", ""), default="—"))
        cols[3].metric("D+5 최고", _v2_pct_text(row.get("d5_mfe_pct")))
        cols[4].metric("D+5 최저", _v2_pct_text(row.get("d5_mae_pct")))
        cols[5].metric("유효 후보", _v2_bool_label(row.get("is_valid_v2_candidate")))

        chart_path_text = str(row.get(chart_col, "")).strip()
        chart_path = Path(chart_path_text) if chart_path_text else None
        if chart_path and chart_path.is_file():
            st.image(str(chart_path), use_container_width=True)
        else:
            st.warning(f"{horizon} 차트 PNG가 없습니다. 분봉 부족 또는 15시 기준가 부족 가능성이 있습니다.")

        detail = pd.DataFrame([{
            "분류 사유": row.get("case_reason", ""),
            "보류 사유": row.get("hold_reason", ""),
            "D+1 종가": _v2_pct_text(row.get("dplus1_close_return_pct")),
            "D+2 종가": _v2_pct_text(row.get("dplus2_close_return_pct")),
            "D+3 종가": _v2_pct_text(row.get("dplus3_close_return_pct")),
            "D+4 종가": _v2_pct_text(row.get("dplus4_close_return_pct")),
            "D+5 종가": _v2_pct_text(row.get("dplus5_close_return_pct")),
            "+2 도달": _v2_bool_label(row.get("plus2_touch")),
            "+3 도달": _v2_bool_label(row.get("plus3_touch")),
            "-2 터치": _v2_bool_label(row.get("minus2_touch")),
        }])
        st.dataframe(detail, use_container_width=True, hide_index=True, height=84)
        st.divider()


@st.cache_data(show_spinner=False)
def load_v2_chart_audit_summary() -> pd.DataFrame:
    p = V2_CHART_AUDIT_DIR / "v2_chart_audit_summary_20260513.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


@st.cache_data(show_spinner=False)
def load_v2_chart_audit_samples() -> pd.DataFrame:
    p = V2_CHART_AUDIT_DIR / "v2_chart_audit_chart_samples_20260513.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


def _v2_audit_gallery(samples: pd.DataFrame, group: str, n_columns: int = 2) -> None:
    """승리/패배/애매 차트 갤러리. 종목당 [이미지 + 메타 + 한 줄 해석]."""
    if samples.empty:
        st.info("chart_samples CSV 없음")
        return
    rows = samples[samples["result_group"] == group].sort_values(
        ["selection_name", "entry_basis", "signal_date"]
    ).reset_index(drop=True)
    if rows.empty:
        st.info(f"{group} 케이스가 없습니다.")
        return
    st.caption(f"{group.upper()} 케이스 {len(rows)}개 — 각 차트에 한 줄 해석. "
               "백데이터 결과이며 운영 신호·매수 지시 아님.")
    for i in range(0, len(rows), n_columns):
        cols = st.columns(n_columns)
        for j, col in enumerate(cols):
            if i + j >= len(rows):
                break
            r = rows.iloc[i + j].to_dict()
            with col:
                path = str(r.get("chart_path", ""))
                if Path(path).exists():
                    st.image(path, use_container_width=True)
                else:
                    st.warning(f"이미지 없음: {path}")
                pattern_ko = V2_PATTERN_LABELS.get(str(r.get("pattern_label", "")), str(r.get("pattern_label", "")))
                entry_ko = V2_ENTRY_BASIS_LABELS.get(str(r.get("entry_basis", "")), str(r.get("entry_basis", "")))
                sel = str(r.get("selection_name", ""))
                score = str(r.get("score_total_100", ""))
                try:
                    mfe = float(r.get("mfe_5d_pct", "0") or 0)
                    mae = float(r.get("mae_5d_pct", "0") or 0)
                    mfe_text = f"{mfe:+.1f}%"
                    mae_text = f"{mae:+.1f}%"
                except Exception:
                    mfe_text = mae_text = "—"
                st.markdown(
                    f"**{r.get('stock_name', '')}** (`{r.get('stock_code', '')}`)  ·  "
                    f"점수 `{score}`  ·  {entry_ko}<br>"
                    f"선정 `{sel}`  ·  "
                    f"5일 최고 <span style='color:#7ee0a1'>{mfe_text}</span> · "
                    f"5일 최저 <span style='color:#ff8a8a'>{mae_text}</span>  ·  "
                    f"패턴: {pattern_ko}<br>"
                    f"<span class='cb-subtle'>💬 {r.get('notes', '')}</span>",
                    unsafe_allow_html=True,
                )
                st.divider()


def render_v2_chart_audit() -> None:
    """Codex V2 점수제 차트 검증 결과 — 5 sub-tabs (결과 요약 / 승리 / 패배 / 애매 / 공통점)."""
    st.subheader("🔬 V2 차트 검증")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#9f7aea; background:rgba(159,122,234,0.10);">'
        '이 화면은 V2 점수제가 뽑은 종목을 사람이 눈으로 검증하기 위한 연구 화면입니다.<br>'
        '<b>승리/패배는 백데이터 결과이며, 운영 신호나 매수 지시가 아닙니다.</b> '
        '"높은 도달률(touch rate)은 승률이 아니라 변동성 도달률" 이라는 점에 유의하세요.'
        '</div>',
        unsafe_allow_html=True,
    )

    summary = load_v2_chart_audit_summary()
    samples = load_v2_chart_audit_samples()
    top3_cases = load_v2_top3_chart_cases()
    top3_manifest = load_v2_top3_chart_manifest()
    if summary.empty and samples.empty and top3_cases.empty:
        st.warning(f"Codex V2 차트 검증 산출물이 아직 없습니다.\n경로: `{V2_CHART_AUDIT_DIR}`")
        return

    if not top3_cases.empty:
        render_v2_top3_chart_review_section(top3_cases, top3_manifest)

    sub_tabs = st.tabs(["결과 요약", "승리 차트 (20)", "패배 차트 (20)", "애매한 케이스 (10)", "공통점 메모"])

    # 1. 결과 요약
    with sub_tabs[0]:
        st.markdown("##### 12개 variant × 진입 기준 — Codex audit (2026-05-13)")
        if summary.empty:
            st.info("summary CSV 없음")
        else:
            df = summary.copy()
            for col in ("sample_n", "win_n", "loss_n", "unknown_n"):
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            for col in ("win_rate_pct", "loss_rate_pct"):
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            df = df.sort_values("win_rate_pct", ascending=False)
            display_cols = ["selection_name", "entry_basis", "sample_n", "win_n", "loss_n", "unknown_n",
                            "win_rate_pct", "loss_rate_pct", "median_score", "median_mfe_5d", "median_mae_5d",
                            "top_success_pattern", "top_failure_reason"]
            display = df[display_cols].rename(columns={
                **V2_AUDIT_COLUMN_LABELS,
                "median_mfe_5d": "중앙 MFE(%)",
                "median_mae_5d": "중앙 MAE(%)",
            })
            if "진입 기준" in display.columns:
                display["진입 기준"] = display["진입 기준"].map(lambda v: V2_ENTRY_BASIS_LABELS.get(str(v), str(v)))
            for col in ("주요 성공 패턴", "주요 실패 사유"):
                if col in display.columns:
                    display[col] = display[col].map(lambda v: V2_PATTERN_LABELS.get(str(v), str(v)))
            st.dataframe(display, use_container_width=True, hide_index=True, height=520)
            st.caption(
                "정렬: 승률 내림차순. 진입 기준 = D0 종가/D+1 시가 진입 가정. "
                "MFE = 5일 안 최고수익률, MAE = 5일 안 최대하락률. "
                "BEST_SCORE_TOP3_PROXY D0_CLOSE = 표본 755, 승률 59.87% (이번 audit 최상). "
                "P0 거래대금 Top3 D0_CLOSE = 승률 30.86% — V2 상위 variant 대비 -29%p."
            )

    # 2. 승리 / 3. 패배 / 4. 애매
    with sub_tabs[1]:
        _v2_audit_gallery(samples, "win", n_columns=2)
    with sub_tabs[2]:
        _v2_audit_gallery(samples, "loss", n_columns=2)
    with sub_tabs[3]:
        _v2_audit_gallery(samples, "unknown", n_columns=2)

    # 5. 공통점 메모
    with sub_tabs[4]:
        st.markdown("##### 이긴 차트의 공통점 (Codex 패턴 라벨링)")
        st.markdown("""
- **강세종가 추세 지속** (STRONG_CLOSE_CONTINUATION) — 종가가 일중 상단에 가깝게 마감, 윗꼬리 짧음, 추세 유지
- **테마 모멘텀** (THEME_MOMENTUM) — 같은 시점 유사 종목 동반 상승, 매수세 지속, 거래량 감소해도 가격 방어
- **얕은 눌림 방어** (SHALLOW_PULLBACK_DEFENSE) — D+1에 -2% 가까이 눌리지만 곧바로 회복, 매수세 지지선 형성
- **짧은 윗꼬리 지속** (LOW_UPPER_WICK_CONTINUATION) — D0 윗꼬리 짧고 종가 강함, 다음날 가격 흐름 안정
""")
        st.markdown("##### 진 차트의 공통점")
        st.markdown("""
- **깊은 눌림** (DEEP_PULLBACK) — D+1~D+3 중 -5% 이상 하락, 매수세 약화, MAE > 5%
- **긴 윗꼬리** (LONG_UPPER_WICK) — D0 윗꼬리 길어 매도세 강함, D+1 갭하락
- **갭 과열** (GAP_OVERHEAT) — D+1 시가가 D0 종가 대비 크게 갭상승 → 곧바로 매도세 → -2% 빠르게 터치
- **D0 종가 약세** (D0_CLOSE_WEAK) — 거래대금은 컸지만 종가가 일중 하단 마감 → 약한 매수세
""")
        st.markdown("##### 다음 점수제 보정 방향 (Codex 영역)")
        st.markdown("""
- 짧은 윗꼬리 + 강한 종가 = 가산점 ✓ (이미 일부 variant 반영)
- 깊은 눌림 / 긴 윗꼬리 / 갭 과열 = 감점
- pullback 깊이 정량화 (pullback_depth_pct) — 깊은 눌림 변환 임계 정의 필요
- D1_OPEN 진입 시 슬리피지 보정 추가 — D0_CLOSE 대비 D1_OPEN 승률이 평균 15~25%p 떨어짐
""")
        st.caption("출처: `docs/closingbell/reports_summary/V2_SCORE_CHART_AUDIT_REPORT_20260513.md` (Codex). "
                   "점수 산식 변경은 Codex 영역, 사용자 승인 후만 운영 적용.")


@st.cache_data(show_spinner=False)
def load_online_v2_csv(filename: str) -> pd.DataFrame:
    path = ONLINE_V2_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")


@st.cache_data(show_spinner=False)
def load_online_v2_manifest() -> dict[str, Any]:
    path = ONLINE_V2_DIR / "manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_online_v2_freshness() -> dict[str, Any]:
    path = ONLINE_V2_DIR / "supply_freshness.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _v2_score_grade_st(score: float) -> tuple[str, str, str]:
    """점수 → (등급 라벨, 이모지, 색상hex).

    2026-05-15 sweet spot 연구 반영:
        - 65~75 = 스위트 스팟 후보 (진입 구간)
        - 75~85 = 표준 강세 후보 (sweet spot)
        - 85+   = 고득점·과열 주의 후보
        점수대 라벨은 연구 가설이며 매수 신호가 아닙니다.
    """
    if score >= 85:
        return ("고득점·과열 주의 후보", "🔥", "#dc2626")
    if score >= 75:
        return ("표준 강세 후보 (sweet spot)", "✨", "#ea580c")
    if score >= 65:
        return ("스위트 스팟 후보 (진입 구간)", "✅", "#16a34a")
    if score >= 55:
        return ("운영 기준선 통과 (보통)", "✅", "#10b981")
    if score >= 45:
        return ("낮은 점수대 — 연구 필요", "⚠️", "#ca8a04")
    return ("매우 주의 — 백데이터 안정 구간 밖", "🚨", "#dc2626")


def _v2_fmt_price(value: Any) -> str:
    try:
        return f"{int(float(value)):,}원"
    except Exception:
        return "—"


def _v2_fmt_freshness(latest: str, target: str) -> tuple[str, str]:
    """(라벨, 색상) — 오늘=초록 / 어제=노랑 / 그 이전=빨강."""
    if not latest or not target:
        return ("—", "#9ca3af")
    try:
        from datetime import date
        ly = date.fromisoformat(str(latest)[:10])
        ty = date.fromisoformat(str(target)[:10])
        diff = (ty - ly).days
        if diff <= 0:
            return (f"{latest} (오늘) ✅", "#16a34a")
        if diff == 1:
            return (f"{latest} (어제) ⚠️", "#ca8a04")
        return (f"{latest} (D-{diff} 지연) 🚨", "#dc2626")
    except Exception:
        return (str(latest), "#9ca3af")


def _load_v2_d0_audit_csv() -> pd.DataFrame:
    """Codex audit CSV 로딩 — 있으면 D0 통과·금액제한·대형주 정보 반환, 없으면 빈 DF."""
    for candidate in [
        QUALITY / "v2_d0_universe_audit_20260514" / "v2_d0_audit_20260513.csv",
        QUALITY / "v2_d0_universe_audit_20260514" / f"v2_d0_audit_{datetime.now().strftime('%Y%m%d')}.csv",
    ]:
        if candidate.exists():
            try:
                return pd.read_csv(candidate, dtype=str, encoding="utf-8-sig").fillna("")
            except Exception:
                pass
    return pd.DataFrame()


def _load_recent_sent_status() -> dict[str, Any]:
    """sent_log 마지막 줄 + V2 result.json → 현재 발송 상태 한 줄 정리."""
    out: dict[str, Any] = {"p0_last": None, "v2_last": None}
    if SENT_LOG.exists():
        try:
            lines = [l for l in SENT_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
            for ln in reversed(lines):
                try:
                    rec = json.loads(ln)
                except Exception:
                    continue
                # V2 Top3 메시지는 본문에 "V2 Top3" 포함
                msg = rec.get("message", "")
                if "V2 Top3" in msg and out["v2_last"] is None:
                    out["v2_last"] = rec
                elif "V2 Top3" not in msg and out["p0_last"] is None:
                    out["p0_last"] = rec
                if out["v2_last"] and out["p0_last"]:
                    break
        except Exception:
            pass
    return out


def _audit_status_for_code(audit_df: pd.DataFrame, code: str) -> dict[str, str]:
    """Codex audit DF에서 종목 1개의 D0/금액제한/대형주 상태 추출."""
    if audit_df.empty:
        return {"d0_pass": "확인 중", "amount_limit": "확인 중", "large_cap": "확인 중",
                "status": "검증 필요", "reason": ""}
    row = audit_df[audit_df["code"].astype(str).str.zfill(6) == str(code).zfill(6)]
    if row.empty:
        return {"d0_pass": "audit 미포함", "amount_limit": "audit 미포함",
                "large_cap": "audit 미포함", "status": "검증 필요", "reason": ""}
    r = row.iloc[0]
    def _yn(value: str, yes: str = "통과", no: str = "미통과") -> str:
        v = str(value).strip().lower()
        if v in ("true", "1", "y", "yes", "pass"): return yes
        if v in ("false", "0", "n", "no", "fail"): return no
        return "확인 중"
    return {
        "d0_pass": _yn(r.get("legacy_d0_pass", "")),
        "amount_limit": _yn(r.get("amount_limit_pass", "")),
        "large_cap": "해당" if str(r.get("large_cap_flag", "")).strip().lower() in ("true", "1", "y", "yes") else
                     "해당 없음" if str(r.get("large_cap_flag", "")).strip().lower() in ("false", "0", "n", "no") else "확인 중",
        "status": r.get("final_audit_status", "확인 중") or "확인 중",
        "reason": r.get("legacy_exclusion_reason", "") or "",
    }


def render_online_v2_dashboard() -> None:
    """온라인 V2 Top3 — 친화 카드 + D0 재검증 안전 표시 + 진입·청산 가이드.

    2026-05-14 사용자 긴급 피드백 반영:
        - 상단 "D0 후보군 재검증 중" 배너
        - V2 카드에 D0/금액제한/대형주 필드 (Codex audit CSV 자동 인식)
        - LIVE P0 vs V2 SHADOW 실제 발송 상태 표시
        - 백데이터 수치 "재검증 전 임시값" 표기
        - "진입 가이드" → "Paper 기준선"
    """
    st.subheader("📈 V2 Top3 — Paper Watch (후보군 재검증 전 임시판)")

    # ── ⚠ D0 후보군 재검증 경고 배너 (최상단, 진한 노랑) ──────────────
    st.markdown(
        '<div style="background:#fef3c7; border:2px solid #d97706; border-radius:8px; '
        'padding:14px 18px; margin-bottom:14px; color:#78350f;">'
        '<div style="font-size:1.1em; font-weight:bold; margin-bottom:6px;">⚠ D0 후보군 / 금액제한 재검증 중</div>'
        '<div style="font-size:0.95em; line-height:1.6;">'
        '현재 V2 Top3 가 <b>기존 D0 금액제한 / 대형주 제외 조건</b> 과 완전히 일치하는지 확인 중입니다.<br>'
        '2026-05-13 결과에 <b>현대차 · SK하이닉스 · 현대글로비스</b> 같은 대형주가 포함되어, '
        '기존 ClosingBell 의도와 다른 후보군에서 산출됐을 가능성이 있습니다.<br>'
        '이 화면은 <b>연구용 Paper Watch</b> 이며 매수 추천이 아닙니다. '
        '<b>아래 백데이터 수치는 재검증 전 임시값</b> 입니다.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cb-note" style="border-left-color:#3b82f6; background:rgba(59,130,246,0.10);">'
        '📌 <b>연구·관찰용 신호</b>입니다. 실전 주문 아님 · 자동매매 아님 · 매수 추천 아님. '
        'V2 점수 상위 3개 종목을 <b>눈으로 보고 직접 판단</b>하기 위한 화면입니다.<br>'
        '<span style="font-size:0.85em; opacity:0.8;">GitHub/Streamlit Cloud 배포 시에도 같은 데이터를 본다 — 전체 parquet/DART 원본은 포함되지 않으며, '
        '1년치 결과는 미리 계산된 요약 CSV 만 사용.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    manifest = load_online_v2_manifest()
    top3 = load_online_v2_csv("v2_top3_latest.csv")
    overlay = load_online_v2_csv("v2_top3_overlay_latest.csv")
    daily = load_online_v2_csv("v2_backdata_1y_daily_summary.csv")
    backdata = load_online_v2_csv("v2_backdata_1y_detail.csv")
    excluded = load_online_v2_csv("v2_top3_excluded_latest.csv")
    freshness = load_online_v2_freshness()
    audit_df = _load_v2_d0_audit_csv()  # Codex audit CSV (있으면 자동 인식)
    sent_status = _load_recent_sent_status()  # LIVE P0 + V2 SHADOW 최근 발송

    if not manifest and top3.empty:
        st.warning(
            "⚠️ 온라인 V2 스냅샷이 없습니다.\n\n"
            f"경로: `{ONLINE_V2_DIR}`\n\n"
            "**해결 방법**: `bell-data` 프로젝트에서 다음 명령으로 스냅샷을 만드세요.\n"
            "```powershell\n"
            "$py = 'C:/Coding/projects/_venvs/closingbell-py312/Scripts/python.exe'\n"
            "& $py -m bell_data.cli export-online-v2-dashboard --date 2026-05-14\n"
            "```"
        )
        return

    # ── 헤더 메트릭 ──────────────────────────────────────────────
    target_date = manifest.get("target_date", "")
    try:
        from datetime import date as _date
        d = _date.fromisoformat(target_date[:10])
        wd = "월화수목금토일"[d.weekday()]
        date_kor = f"{d.month}월 {d.day}일 ({wd})"
    except Exception:
        date_kor = ""

    bd_manifest = manifest.get("backdata_1y", {}).get("manifest", {}) if manifest else {}
    quick = bd_manifest.get("quick_metrics", {}) if isinstance(bd_manifest, dict) else {}
    selected_cnt = int(manifest.get("v2_top3", {}).get("selected_count", len(top3))) if manifest else len(top3)
    stability_status = manifest.get("v2_top3", {}).get("stability_gate_status", manifest.get("stability_gate_status", "")) or ""

    head_cols = st.columns([1.2, 1, 1, 1, 1])
    head_cols[0].metric("기준일", f"{target_date}", help=date_kor)
    head_cols[1].metric("V2 Top3 선정", f"{selected_cnt} / 3")
    head_cols[2].metric("1년 후보 표본", f"{bd_manifest.get('selected_rows', len(backdata))}개")
    head_cols[3].metric("D+1 +2% 터치율", f"{quick.get('d1_ge_plus2_rate_pct', '—')}%")
    head_cols[4].metric("D+5 +3% 터치율", f"{quick.get('d5_ge_plus3_rate_pct', '—')}%")

    # 안정성 게이트 한 줄
    if stability_status:
        gate_emoji = "✅" if str(stability_status).upper() in ("PASSED", "READY", "READY_FOR_PHASE_2") else "⏳"
        st.caption(f"{gate_emoji} **안정성 게이트**: `{stability_status}` — 5영업일 연속 V2 유효 ≥ 3 여부 (Phase 전환 준비도)")
    st.caption(f"📅 생성 시각: {manifest.get('created_at', '')} · 📂 스냅샷 위치: `{ONLINE_V2_DIR}`")

    st.divider()

    # ── V2 Top3 카드 ────────────────────────────────────────────
    st.markdown("### 🎯 오늘 V2 Top3 후보 (점수 순)")
    if top3.empty:
        st.info("오늘 V2 Top3 파일이 비어 있습니다. 데이터 가드(점수·15:00 기준가·일봉/분봉)에서 모두 제외됐을 가능성.")
    else:
        # 점수 desc 정렬
        try:
            top3_sorted = top3.copy()
            top3_sorted["__score"] = pd.to_numeric(top3_sorted["score_total_100"], errors="coerce").fillna(0)
            top3_sorted = top3_sorted.sort_values("__score", ascending=False).reset_index(drop=True)
        except Exception:
            top3_sorted = top3

        rank_emoji = {0: "🥇", 1: "🥈", 2: "🥉"}
        cards = st.columns(min(len(top3_sorted), 3))
        for idx, (_, row) in enumerate(top3_sorted.iterrows()):
            if idx >= 3:
                break
            try:
                score = float(row.get("score_total_100", 0))
            except Exception:
                score = 0.0
            grade_label, grade_emoji, grade_color = _v2_score_grade_st(score)
            below_55 = score < 55

            with cards[idx]:
                code = row.get("stock_code", "")
                name = row.get("stock_name", "")
                price_str = _v2_fmt_price(row.get("entry_price_1500"))
                daily_fresh, daily_color = _v2_fmt_freshness(row.get("daily_latest_date", ""), target_date)
                minute_fresh, minute_color = _v2_fmt_freshness(row.get("minute_latest_date", ""), target_date)
                market = row.get("market", "")

                warn_bar = (
                    '<div style="background:#fef3c7; border-left:4px solid #ca8a04; padding:6px 10px; margin-top:8px; '
                    'border-radius:4px; font-size:0.85em; color:#78350f;">'
                    '⚠️ <b>점수 55 미만 — 주의</b><br>'
                    '<span style="font-size:0.9em;">백데이터 안정 구간 밖. 진입 시 시뮬 손실률 ↑ 가능.</span></div>'
                ) if below_55 else ""

                # D0 / 금액제한 / 대형주 audit 상태
                audit = _audit_status_for_code(audit_df, code)
                def _badge_color(v: str) -> str:
                    if v in ("통과", "해당 없음"): return "#16a34a"
                    if v in ("미통과", "해당"): return "#dc2626"
                    return "#9ca3af"  # 확인 중 / audit 미포함
                d0_color = _badge_color(audit["d0_pass"])
                amt_color = _badge_color(audit["amount_limit"])
                lc_color = _badge_color(audit["large_cap"])

                audit_box = (
                    f'<div style="background:#fef9c3; border:1px solid #ca8a04; border-radius:6px; '
                    f'padding:8px 10px; margin-top:10px; font-size:0.86em; color:#78350f;">'
                    f'<div style="font-weight:bold; margin-bottom:4px;">🔍 D0 후보군 재검증 상태</div>'
                    f'<div style="line-height:1.6;">'
                    f'• D0 후보군 통과: <span style="color:{d0_color}; font-weight:bold;">{audit["d0_pass"]}</span><br>'
                    f'• 금액제한 통과: <span style="color:{amt_color}; font-weight:bold;">{audit["amount_limit"]}</span><br>'
                    f'• 대형주 필터: <span style="color:{lc_color}; font-weight:bold;">{audit["large_cap"]}</span><br>'
                    f'• 후보 상태: <span style="font-weight:bold;">{audit["status"]}</span>'
                    f'</div></div>'
                )

                # 카드 HTML
                st.markdown(
                    f"""
<div style="border:1.5px solid {grade_color}; border-radius:10px; padding:14px; background:rgba(255,255,255,0.6);">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="font-size:1.4em; font-weight:bold;">{rank_emoji.get(idx, f'{idx+1}.')} {name}</div>
        <div style="font-size:0.85em; color:#6b7280;">{code} · {market}</div>
    </div>
    <div style="background:{grade_color}; color:white; padding:8px 12px; border-radius:6px; text-align:center; margin-bottom:10px;">
        <div style="font-size:1.6em; font-weight:bold;">{score:.1f} <span style="font-size:0.6em;">/ 100</span></div>
        <div style="font-size:0.82em; opacity:0.95;">{grade_emoji} {grade_label}</div>
    </div>
    <div style="font-size:0.92em; line-height:1.7;">
        <div>💰 <b>15:00 기준가</b>: <code>{price_str}</code></div>
        <div>🗂 <b>일봉</b>: <span style="color:{daily_color};">{daily_fresh}</span></div>
        <div>🗂 <b>분봉</b>: <span style="color:{minute_color};">{minute_fresh}</span></div>
        <div>🔭 <b>추적</b>: D+1 ~ D+{row.get('tracking_days', 5)}</div>
    </div>
    {audit_box}
    {warn_bar}
</div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── 발송 상태 (LIVE P0 vs V2 SHADOW) ───────────────────────
    with st.expander("📡 실제 발송 상태 (LIVE P0 / V2 SHADOW / dry-run)", expanded=False):
        st.markdown("**현재 운영 웹훅:** `LIVE P0` (V2 는 dry-run · 미발송)")
        col_p, col_v = st.columns(2)
        with col_p:
            st.markdown("**LIVE P0 (기존 거래대금 웹훅)**")
            if sent_status["p0_last"]:
                rec = sent_status["p0_last"]
                st.code(
                    f"created: {rec.get('created_at', '—')}\n"
                    f"status: {rec.get('status', '—')}\n"
                    f"mode: {rec.get('webhook_mode', '—')}\n"
                    f"sent: {rec.get('send_attempted', False)}",
                    language="text",
                )
            else:
                st.caption("최근 P0 발송 기록 없음")
        with col_v:
            st.markdown("**V2 SHADOW (dry-run)**")
            if sent_status["v2_last"]:
                rec = sent_status["v2_last"]
                st.code(
                    f"created: {rec.get('created_at', '—')}\n"
                    f"status: {rec.get('status', '—')}\n"
                    f"mode: {rec.get('webhook_mode', '—')}\n"
                    f"sent: {rec.get('send_attempted', False)}",
                    language="text",
                )
            else:
                st.caption("V2 발송 기록 없음 — dry-run 만 실행됨")
        st.caption(
            "🛑 V2 단독 PROD 발송은 D0 후보군 재검증 완료 + 사용자 명시 승인 후에만 가능합니다."
        )

    # ── Paper 기준선 (D+1 시가 시뮬 가정) ───────────────────────
    with st.expander("📖 Paper 기준선 — 복기·관찰용 시뮬 규칙 (운영 진입 가이드 아님)", expanded=False):
        st.markdown(
            """
🛑 **이 박스는 매수·진입 가이드가 아닙니다.** 백데이터를 어떤 규칙으로 계산했는지 보여주는 설명이며,
실거래는 별도 슬리피지·갭·호가공백 보정이 필요합니다.

**진입 가정 (복기 기준)**: D+1 시가. 백데이터는 D0 종가 기준 → 실제 D+1 시가는 평균 ~0.5~1.5% 이격.

**익절 기준선**: +2% 분봉 첫 터치 &nbsp;&nbsp;|&nbsp;&nbsp; **손절 기준선**: -2% 분봉 첫 터치

**시간 청산**: 다음날 11:30 까지 둘 다 안 닿으면 시뮬상 시장가 청산.

**슬리피지 보정**: 0.3~1.5% (호가창 ↑) — 실제 익절선 ≈ +2.5%, 손절 ≈ -2.5% 로 봐야 안전.

**도달률 ≠ 승률** — 같은 날 양쪽 (+2%, -2%) 다 닿는 변동성 케이스가 다수. 실제 손익은 슬리피지·갭·체결지연 보정 후 판단.
            """
        )

    # ── overlay (기업·수급·공매도) ────────────────────────────────
    st.markdown("### 🏢 후보별 기업·수급·공매도 정보")
    if overlay.empty:
        st.info("overlay 파일이 없습니다.")
    else:
        overlay_cols = [
            "v2_rank", "stock_code", "stock_name", "sector",
            "institution_net_qty", "foreign_net_qty", "inst_trade_latest_date",
            "short_sale_qty", "short_sale_trade_weight", "short_sale_latest_date",
            "program_feature_used",
        ]
        st.dataframe(
            overlay[[c for c in overlay_cols if c in overlay.columns]].rename(
                columns={
                    "v2_rank": "순위", "stock_code": "코드", "stock_name": "종목", "sector": "업종",
                    "institution_net_qty": "기관 순매수", "foreign_net_qty": "외인 순매수",
                    "inst_trade_latest_date": "수급 최신",
                    "short_sale_qty": "공매도 수량", "short_sale_trade_weight": "공매도 비중(%)",
                    "short_sale_latest_date": "공매도 최신",
                    "program_feature_used": "프로그램 점수사용",
                }
            ),
            use_container_width=True, hide_index=True, height=160,
        )
        st.caption("💡 프로그램 매수 데이터는 커버리지가 부족해 V2 점수 계산에 사용하지 않습니다 (상태 표시만).")

    # ── 1년치 백데이터 요약 ──────────────────────────────────────
    st.markdown("### 📊 1년치 V2 백데이터 요약 (재검증 전 임시값)")
    st.markdown(
        '<div style="background:#fef3c7; border-left:4px solid #d97706; padding:8px 12px; '
        'margin-bottom:10px; border-radius:4px; font-size:0.87em; color:#78350f;">'
        '⚠ 이 수치는 <b>현재 후보군 기준</b> 입니다. 기존 D0 금액제한 / 대형주 제외 조건을 '
        '재적용한 후 달라질 수 있습니다 (Codex audit 진행 중).'
        '</div>',
        unsafe_allow_html=True,
    )
    if daily.empty:
        st.info("일별 요약 파일이 없습니다.")
    else:
        ok_days = int((daily.get("status", pd.Series(dtype=str)) == "ok").sum()) if "status" in daily.columns else 0
        st.caption(f"📅 일별 요약 **{len(daily)}일** · Top3 모두 채워진 날 **{ok_days}일** ({ok_days/max(len(daily),1)*100:.1f}%)")

        # 핵심 누적 도달률
        if quick:
            m_cols = st.columns(4)
            m_cols[0].metric("D+1 +2% 터치", f"{quick.get('d1_ge_plus2_rate_pct', '—')}%",
                             help="다음날 분봉에서 +2% 익절선에 닿은 비율")
            m_cols[1].metric("D+1 -2% 터치", f"{quick.get('d1_le_minus2_rate_pct', '—')}%",
                             help="다음날 분봉에서 -2% 손절선에 닿은 비율 — 양쪽 다 닿은 변동성 케이스도 포함")
            m_cols[2].metric("D+5 +3% 터치", f"{quick.get('d5_ge_plus3_rate_pct', '—')}%",
                             help="5거래일 누적 +3% 도달 비율")
            m_cols[3].metric("D+5 -3% 터치", f"{quick.get('d5_le_minus3_rate_pct', '—')}%",
                             help="5거래일 누적 -3% 도달 비율")
            st.caption("⚠️ **도달률 ≠ 승률** — 변동성 도달이며 실제 매매 결과 아님.")

        with st.expander("🗓 최근 20일 일별 요약 표 보기"):
            st.dataframe(
                daily.tail(20).sort_values("signal_date", ascending=False),
                use_container_width=True, hide_index=True, height=280,
            )

    # ── 제외 후보 ────────────────────────────────────────────────
    if not excluded.empty:
        with st.expander(f"⏸ 제외/보류 후보 ({len(excluded)}건) — 점수·데이터 사유"):
            ex_cols = ["v2_rank", "stock_code", "stock_name", "score_total_100", "exclude_reason"]
            st.dataframe(
                excluded[[c for c in ex_cols if c in excluded.columns]].rename(
                    columns={"v2_rank": "순위", "stock_code": "코드", "stock_name": "종목",
                             "score_total_100": "점수", "exclude_reason": "제외 사유"}
                ),
                use_container_width=True, hide_index=True, height=200,
            )

    # ── 데이터 신선도 메타 ───────────────────────────────────────
    with st.expander("🔧 원천 데이터 최신성 메타 (참고)"):
        st.json(freshness)

    # ── 푸터 ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="background:#fee2e2; border-left:4px solid #dc2626; padding:10px 14px; border-radius:6px; '
        'font-size:0.9em; color:#7f1d1d;">'
        '🛡 <b>운영 경계선</b><br>'
        '• 이 화면은 <b>연구·관찰용</b>입니다. 매수·매도 지시가 아닙니다.<br>'
        '• 자동매매 / 주문 / 계좌 API 에 연결되어 있지 않습니다.<br>'
        '• 점수가 <b>55점 미만이면 ⚠️ 주의</b> — 백데이터 안정 구간 밖.<br>'
        '• IPO 후보는 V2 자동 표시에서 제외 (사용자 수동 영역).'
        '</div>',
        unsafe_allow_html=True,
    )


def render_detail(mode: str, universe: pd.DataFrame, enriched: pd.DataFrame, review: pd.DataFrame, picks: pd.DataFrame) -> None:
    st.subheader("종목 상세")
    st.markdown(
        '<div class="cb-note">이 화면은 <b>오늘의 D0 감시 / 웹훅 후보</b> 종목의 일봉·분봉·MA를 한 화면에서 깊이 보는 용도입니다. '
        '<b>1년치 backdata 종목은 「1년치 복기」 탭</b>에서 슬롯 단위로 보세요.<br>'
        'D0 감시만 종목(웹훅 후보 아님)은 점수·정책·역할이 비어 있습니다.</div>',
        unsafe_allow_html=True,
    )
    if universe.empty:
        st.warning("표시할 종목이 없습니다.")
        return
    labels = [f"{row.stock_name} ({normalize_code(row.stock_code)}) · {source_label(row.source)}" for row in universe.itertuples()]
    selected = st.selectbox("종목", labels)
    code = selected.split("(")[-1].split(")")[0]
    info_rows = enriched[enriched["stock_code"].map(normalize_code) == code] if not enriched.empty else pd.DataFrame()
    info = info_rows.iloc[0].to_dict() if not info_rows.empty else universe[universe["stock_code"].map(normalize_code) == code].iloc[0].to_dict()
    target_dates = target_dates_for_code(picks, code)

    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.markdown("종목")
        st.markdown(f'<div class="cb-period">{info.get("stock_name", "")} <span class="cb-subtle">({code})</span></div>', unsafe_allow_html=True)
    summary_cols[1].metric("선택 날짜", _safe_text(str(info.get("signal_date", ""))[:10]))
    summary_cols[2].metric("위치", role_label(info.get("role", "")))
    summary_cols[3].metric("일봉 최신", latest_date_from_daily(code) or "없음")
    detail_cols = st.columns(4)
    detail_cols[0].metric("점수", _safe_text(info.get("score", "")))
    detail_cols[1].metric("정책 판단", policy_label(info.get("policy_decision", info.get("candidate_policy", ""))))
    detail_cols[2].metric("D0 날짜", _safe_text(str(info.get("d0_date", ""))[:10]))
    detail_cols[3].metric("D0 이후", f"{_safe_text(info.get('days_after_D0', ''), default='0')}거래일")

    _detail_sd = str(info.get("signal_date", ""))[:10]
    _detail_future = [d.isoformat() for d in trading_days_after(code, _detail_sd, 5)] if _detail_sd else []
    render_quality_badge_row(code, _detail_sd or str(info.get("d0_date", ""))[:10], extra_dates=_detail_future)

    st.markdown("#### 일봉")
    plot_daily_chart(load_daily(code), info, target_dates)
    st.markdown("#### 분봉 복기")
    st.caption("기본은 30분봉입니다. 5분봉은 세부 체결 흐름, 15분봉은 중간 압축 확인에 사용합니다.")
    plot_minute_chart(load_minute(code), info, key_prefix=f"detail_{code}")

    if mode == "REVIEW":
        st.markdown("#### REVIEW 결과")
        if review.empty:
            st.info("REVIEW 결과 파일이 아직 없습니다. 먼저 장마감 이후 review_outcomes 생성이 필요합니다.")
        else:
            rows = review[review["stock_code"].map(normalize_code) == code]
            if rows.empty:
                st.info("선택 종목의 REVIEW 결과가 없습니다. 이 종목이 웹훅 추적 대상이 아니었거나, D+1~D+5 결과 생성 전일 수 있습니다.")
            else:
                first = rows.iloc[0].to_dict()
                cards = st.columns(5)
                cards[0].metric("+1%", bool_label(first.get("outcome_d1_plus1_touch"), "도달", "미도달"))
                cards[1].metric("+2%", bool_label(first.get("outcome_d1_plus2_touch"), "도달", "미도달"))
                cards[2].metric("+3%", bool_label(first.get("outcome_d1_plus3_touch"), "도달", "미도달"))
                cards[3].metric("-2%", bool_label(first.get("outcome_d1_minus2_touch"), "터치", "미터치"))
                cards[4].metric("최저/최고", f"{first.get('outcome_d1_low_return', '')} / {first.get('outcome_d1_high_return', '')}")
                visible = [
                    "signal_date",
                    "rank",
                    "role",
                    "outcome_result_label",
                    "outcome_d1_plus1_touch",
                    "outcome_d1_plus2_touch",
                    "outcome_d1_plus3_touch",
                    "outcome_d1_minus2_touch",
                    "outcome_d1_high_return",
                    "outcome_d1_low_return",
                ]
                show_table(rows, visible, height=260)
    else:
        st.info("당시 정보/메모 모드에서는 D+1~D+5 사후 결과를 숨깁니다. 사후 복기 모드에서만 결과를 확인합니다.")


# ─────────────────────────────────────────────────────────────────────
# 2026-05-15 신설 탭 3개 — Sweet Spot 연구 / 1년 차트 복기 / 눌림 후 회복
# CLAUDE_V2_1Y_VISUAL_DASHBOARD_WEBHOOK_ORDER_20260515.md §2 반영.
# 점수 산식·후보 선정·발송 로직 일절 변경 X — 표시 전용.
# ─────────────────────────────────────────────────────────────────────

def _load_sweetspot_csvs() -> dict[str, pd.DataFrame]:
    """Codex 2026-05-15 09:00 sweet spot 리서치 CSV 들을 로딩.

    위치: C:\\Users\\PYJ\\Downloads\\ (사용자 다운로드 폴더 기준)
    """
    out = {}
    base = Path(r"C:\Users\PYJ\Downloads")
    csvs = {
        "bucket":   base / "V2_SCORE_RANK_SWEETSPOT_SCORE_RANK_BUCKET_SUMMARY_20260515.csv",
        "rank":     base / "V2_SCORE_RANK_SWEETSPOT_RANK_ONLY_SUMMARY_20260515.csv",
        "sweet":    base / "V2_SCORE_RANK_SWEETSPOT_SWEETSPOT_CANDIDATE_SUMMARY_20260515.csv",
        "matrix":   base / "V2_SCORE_RANK_SWEETSPOT_SCORE_RANK_MATRIX_20260515.csv",
        "risky":    base / "V2_SCORE_RANK_SWEETSPOT_RISKY_ENTRY_EXIT_SUMMARY_20260515.csv",
    }
    for k, p in csvs.items():
        if p.exists():
            try:
                out[k] = pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")
            except Exception:
                out[k] = pd.DataFrame()
        else:
            out[k] = pd.DataFrame()
    return out


def render_v2_sweetspot_research() -> None:
    """V2 점수대·순위 sweet spot 연구 탭.

    표현은 조심스럽게 (지시서 §2.3): '~ 후보' / '연구 가치' / '운영 기준 아님'.
    """
    st.subheader("🎯 V2 점수대·순위 연구 (Sweet Spot)")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#7c3aed; background:rgba(124,58,237,0.08);">'
        '<b>이 탭은 연구용입니다.</b> Codex 2026-05-15 09:00 산출 1년치 sweet spot 리서치 결과를 표시합니다.<br>'
        '점수대 라벨은 <b>연구 가설</b>이며 매수 신호가 아닙니다. 운영 기준 (D0 strict 3일 + V2 Top3 전체) 은 그대로 유지됩니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    csvs = _load_sweetspot_csvs()
    if csvs["sweet"].empty and csvs["bucket"].empty:
        st.warning(
            "⚠️ sweet spot 리서치 CSV가 없습니다.\n\n"
            "Codex 가 다음 명령으로 생성:\n"
            "```\npython -m bell_data.research v2_score_rank_sweetspot --date 2026-05-15\n```"
        )
        return

    # ── 핵심 4 그룹 카드 (Codex 추천) ────────────────────────────
    st.markdown("### 📊 핵심 후보 그룹 비교 (Codex 추천 4개)")
    if not csvs["sweet"].empty:
        sweet = csvs["sweet"].copy()
        for col in ["sample_n", "fill_pass_rate_pct", "d1_plus_minus_2_pp", "d5_plus_minus_3_pp"]:
            if col in sweet.columns:
                sweet[col] = pd.to_numeric(sweet[col], errors="coerce")

        group_kor = {
            "Top3_all":                       "Top3 전체 (운영 기준)",
            "Rank1_only":                     "Rank1 only",
            "Rank2_only":                     "Rank2 only",
            "Rank3_only":                     "Rank3 only",
            "score_ge85_all":                 "점수 85+ 전체",
            "score_ge85_rank1":               "점수 85+ × Rank1 ★",
            "score_70_85_excluding_rank1":    "점수 70~85 (Rank1 제외) ★",
            "score_65_75_all":                "점수 65~75 전체 ★",
            "score_65_75_rank2":              "점수 65~75 × Rank2",
            "score_65_80_rank2":              "점수 65~80 × Rank2 (연구)",
            "score_lt65_all":                 "점수 65 미만 전체",
        }
        # Codex 추천 강조 그룹 (level==eligible_for_oos_check)
        recommended = ["score_70_85_excluding_rank1", "score_ge85_rank1", "score_65_75_all", "Top3_all"]
        show_groups = [g for g in recommended if g in sweet["group"].values]

        cols = st.columns(min(len(show_groups), 4))
        for i, g in enumerate(show_groups):
            row = sweet[sweet["group"] == g].iloc[0]
            n = int(row.get("sample_n", 0) or 0)
            d1 = float(row.get("d1_plus_minus_2_pp", 0) or 0)
            d5 = float(row.get("d5_plus_minus_3_pp", 0) or 0)
            fp = float(row.get("fill_pass_rate_pct", 0) or 0)
            level = str(row.get("level", "")).strip()
            level_label = {
                "eligible_for_oos_check":   "OOS 검증 가능",
                "research_only_N_lt_100":   "연구 후보 (N<100)",
                "do_not_interpret_N_lt_50": "해석 금지 (N<50)",
            }.get(level, level or "—")
            is_star = g in ("score_70_85_excluding_rank1", "score_ge85_rank1", "score_65_75_all")
            color = "#7c3aed" if is_star else "#3b82f6"
            cols[i].markdown(
                f"""
<div style="border:1.5px solid {color}; border-radius:10px; padding:12px; background:rgba(255,255,255,0.6);">
    <div style="font-size:0.95em; color:#6b7280;">{level_label}</div>
    <div style="font-size:1.05em; font-weight:bold; margin:6px 0; color:{color};">{group_kor.get(g, g)}</div>
    <div style="font-size:0.9em;">표본 <b>{n}</b>건 · fill 통과 {fp:.1f}%</div>
    <hr style="margin:8px 0; border-color:#e5e7eb;">
    <div style="font-size:0.92em; line-height:1.7;">
        <div>D+1 ±2 선터치 우위<br><b style="font-size:1.2em; color:#16a34a;">+{d1:.2f}%p</b></div>
        <div style="margin-top:8px;">D+5 ±3 선터치 우위<br><b style="font-size:1.2em; color:#16a34a;">+{d5:.2f}%p</b></div>
    </div>
</div>
                """,
                unsafe_allow_html=True,
            )

    # ── 점수대 × 순위 매트릭스 ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔬 점수대 × 순위 매트릭스 (D+1 종가 ±2% 선터치 우위 %p)")
    st.caption("색상: 초록=높음 / 빨강=낮음 · N<10인 칸은 해석 주의")
    if not csvs["matrix"].empty:
        matrix = csvs["matrix"].copy()
        for col in matrix.columns:
            if col not in ("group", "score_bucket", "rank_v2"):
                matrix[col] = pd.to_numeric(matrix[col], errors="coerce")
        # Build pivot
        try:
            buckets = ["<55", "55~60", "60~65", "65~70", "70~75", "75~80", "80~85", "85~90", "90+"]
            ranks = ["1", "2", "3"]
            cells = []
            for b in buckets:
                row_data = {"점수대": b}
                for r in ranks:
                    sub = matrix[(matrix["score_bucket"] == b) & (matrix["rank_v2"].astype(str) == r)]
                    if not sub.empty:
                        n = int(sub.iloc[0].get("sample_n", 0) or 0)
                        v = sub.iloc[0].get("d1_close_t2_profit_minus_loss_pp")
                        row_data[f"Rank {r}"] = f"{v:+.1f}pp (N={n})" if pd.notna(v) and n > 0 else "—"
                    else:
                        row_data[f"Rank {r}"] = "—"
                cells.append(row_data)
            mdf = pd.DataFrame(cells)
            st.dataframe(mdf, use_container_width=True, hide_index=True, height=380)
        except Exception as e:
            st.error(f"매트릭스 표시 실패: {e}")

    # ── 점수대 막대그래프 ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 점수대별 first-touch 우위 (%p)")
    if not csvs["bucket"].empty and go is not None:
        bucket = csvs["bucket"].copy()
        bucket["bucket"] = bucket["group"].str.replace("score_bucket=", "")
        for col in bucket.columns:
            if col not in ("group", "bucket"):
                bucket[col] = pd.to_numeric(bucket[col], errors="coerce")
        bucket = bucket[bucket["sample_n"] >= 30].copy()
        if not bucket.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=bucket["bucket"],
                y=bucket["d1_close_t2_profit_minus_loss_pp"],
                name="D+1 ±2% 우위",
                marker_color="#3b82f6",
                text=[f"+{v:.1f}" if v >= 0 else f"{v:.1f}" for v in bucket["d1_close_t2_profit_minus_loss_pp"]],
                textposition="outside",
            ))
            fig.add_trace(go.Bar(
                x=bucket["bucket"],
                y=bucket["d5_close_t3_profit_minus_loss_pp"],
                name="D+5 ±3% 우위",
                marker_color="#10b981",
                text=[f"+{v:.1f}" if v >= 0 else f"{v:.1f}" for v in bucket["d5_close_t3_profit_minus_loss_pp"]],
                textposition="outside",
            ))
            fig.update_layout(
                barmode="group",
                xaxis_title="점수대 (N≥30)",
                yaxis_title="선터치 우위 (%p)",
                height=380,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "**핵심 발견**: 75~80점 (N=183) 이 D+1 +17.5%p / D+5 +16.4%p 로 가장 robust. "
                "65~70 (N=37) 은 D+5에서 손실 우위 (-2.7%p), 80~90 (N=412) 은 과열로 edge 작음."
            )

    # ── 위험-기대값 진입/청산 ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚡ 위험하지만 기대값 높은 진입/청산 조합 (연구)")
    if not csvs["risky"].empty:
        risky = csvs["risky"].copy()
        for col in risky.columns:
            if col not in ("entry", "exit", "note"):
                risky[col] = pd.to_numeric(risky[col], errors="coerce")
        risky_sorted = risky.sort_values("profit_minus_loss_pp", ascending=False).head(8)
        entry_kor = {
            "ENTRY_1500":                         "15:00 즉시 진입",
            "ENTRY_DROP_MINUS3":                  "-3% 눌림 도달 후 진입",
            "ENTRY_DROP_MINUS4":                  "-4% 눌림 도달 후 진입",
            "ENTRY_DROP_MINUS5":                  "-5% 눌림 도달 후 진입",
            "ENTRY_DROP_MINUS3_THEN_VWAP_RECLAIM": "-3% 눌림 후 VWAP 회복 진입 ★",
        }
        show_rows = []
        for _, r in risky_sorted.iterrows():
            show_rows.append([
                entry_kor.get(r["entry"], r["entry"]),
                r["exit"],
                f"{r.get('entry_success_rate_pct', 0):.1f}%" if pd.notna(r.get("entry_success_rate_pct")) else "—",
                f"+{r['profit_minus_loss_pp']:.2f}%p",
                f"{r.get('net_mean_pct', 0):+.3f}%" if pd.notna(r.get("net_mean_pct")) else "—",
            ])
        st.dataframe(
            pd.DataFrame(show_rows, columns=["진입 조건", "청산 조건", "진입 성공률", "익절-손절 우위", "평균 순수익"]),
            use_container_width=True, hide_index=True, height=320,
        )
        st.caption(
            "⚠️ 위 결과는 minute_proxy_phase1 — VI / 단일가 / 거래정지 / 호가잔량 미반영. "
            "운영 기준이 아닌 연구 후보입니다. "
            "**-3% 눌림 후 VWAP 회복 진입** 이 가장 유망한 연구 후보."
        )

    # ── 푸터 ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="background:#ede9fe; border-left:4px solid #7c3aed; padding:10px 14px; '
        'border-radius:6px; font-size:0.9em; color:#5b21b6;">'
        '🛡 <b>이 탭의 한계</b><br>'
        '• 점수대 라벨은 1년 백데이터 기준 연구 가설. OOS 검증 전 운영 기준 변경 X.<br>'
        '• 단순 도달률이 아닌 first-touch (선터치) 기반 — 도달률 ≠ 승률.<br>'
        '• 65~80점 × Rank2 (N=98) 같이 N<100 그룹은 연구 후보로만 해석.<br>'
        '• 위험 진입 (예: -3% 눌림 후 VWAP 회복) 은 별도 탭 "눌림 후 회복" 으로 분리.'
        '</div>',
        unsafe_allow_html=True,
    )


def render_v2_1y_visual_review() -> None:
    """V2 1년 차트 복기 탭 — Codex 5/15 18:54 지시로 산출 예정.

    Codex 산출 대기 중 placeholder.
    산출 위치: data/closingbell/research_index/v2_visual_review_1y_20260515/
    """
    st.subheader("🖼 V2 1년 차트 복기")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#0891b2; background:rgba(8,145,178,0.08);">'
        '<b>이 탭은 V2 가 1년 동안 어떤 후보를 골랐는지 사람이 눈으로 복기</b> 하기 위한 화면입니다.<br>'
        '15:00 기준가 + ±2/±3 선 + first-touch 마커가 표시된 차트 753장 + 카테고리별 샘플팩.'
        '</div>',
        unsafe_allow_html=True,
    )

    cases_path = ONLINE_V2_DIR / "v2_visual_cases_latest.csv"
    daily_summary_path = ONLINE_V2_DIR / "v2_visual_daily_summary_latest.csv"

    if not cases_path.exists():
        st.info(
            "⏳ **Codex 산출 대기 중**\n\n"
            "이 탭에 표시할 차트 복기 데이터는 다음 명령으로 Codex 가 생성 예정 (2026-05-15 18:54 지시):\n\n"
            "```\n"
            "python -m bell_data.research v2_visual_review --date 2026-05-15\n"
            "```\n\n"
            "산출 파일 (생성되면 자동 표시):\n"
            f"- `{cases_path}`\n"
            f"- `{daily_summary_path}`\n"
            "- 차트 PNG: `data/closingbell/research_index/v2_visual_review_1y_20260515/charts/`\n\n"
            "**필터 예정**: 날짜 / 종목 / 순위 (1·2·3) / 점수대 (65~75 / 70~85 / 85+) / "
            "결과 (빠른 성공·늦은 성공·손실 먼저·애매) / Fill 상태 / 진입 조건 (15:00 · -3% 눌림 후 VWAP 회복)"
        )
        # 진행 상황 안내
        st.markdown("---")
        st.markdown("**오늘 (2026-05-15) V2 Top3 — 운영 결과** (placeholder)")
        top3 = load_online_v2_csv("v2_top3_latest.csv")
        if not top3.empty:
            st.dataframe(top3[["v2_rank", "stock_code", "stock_name", "score_total_100",
                                "entry_price_1500", "entry_status"]].rename(columns={
                "v2_rank": "순위", "stock_code": "코드", "stock_name": "종목",
                "score_total_100": "V2 점수", "entry_price_1500": "15:00 기준가",
                "entry_status": "진입 상태",
            }), use_container_width=True, hide_index=True, height=140)
        return

    # ── Codex 산출 후 표시 (placeholder — 향후 자동 활성화) ──
    try:
        cases = pd.read_csv(cases_path, dtype=str, encoding="utf-8-sig").fillna("")
        st.success(f"✅ Codex 차트 복기 데이터 로드 — {len(cases)} 건")

        # 필터 UI
        col1, col2, col3 = st.columns(3)
        with col1:
            score_band = st.selectbox("점수대",
                ["전체", "<55", "55~64", "65~74", "75~84", "85+"], key="visual_score")
        with col2:
            rank_sel = st.selectbox("순위",
                ["전체", "1등", "2등", "3등"], key="visual_rank")
        with col3:
            outcome_sel = st.selectbox("결과",
                ["전체", "빠른 성공 (FAST_WIN)", "늦은 성공 (SLOW_WIN)",
                 "손실 먼저 (LOSS_FIRST)", "애매 (AMBIGUOUS)"], key="visual_outcome")

        # 필터링 + 표시 (placeholder — 자동 활성화)
        st.dataframe(cases.head(50), use_container_width=True, hide_index=True, height=400)
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")


def render_v2_pullback_reclaim() -> None:
    """V2 눌림 후 회복 Top3 탭 — Codex 5/15 18:54 지시.

    별도 연구/감시 섹션. 운영 15:00 Paper Watch 와 분리.
    """
    st.subheader("🔁 V2 눌림 후 회복 감시")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#dc2626; background:rgba(220,38,38,0.06);">'
        '<b>-3% 하락 자체는 매수 신호가 아닙니다. 눌림 후 회복 확인이 핵심입니다.</b><br>'
        '15:00 기준가 대비 -3% 눌림 후 VWAP / ORB / 전일 고가 등을 회복한 종목을 감시합니다. '
        '연구용 / 운영 기준 아님.'
        '</div>',
        unsafe_allow_html=True,
    )

    pb_path = ONLINE_V2_DIR / "v2_pullback_reclaim_top3_latest.csv"

    if not pb_path.exists():
        st.info(
            "⏳ **Codex 산출 대기 중**\n\n"
            "이 탭은 별도 연구 산출물이 필요합니다 (2026-05-15 18:54 지시).\n\n"
            "**상태 정의** (Codex 산출 예정):\n"
            "- `WAIT_DROP` — 아직 -3% 눌림 없음\n"
            "- `DROP_HIT` — -3% 눌림은 왔지만 회복 미확인\n"
            "- `VWAP_RECLAIMED` — -3% 눌림 후 누적 VWAP 회복 ★\n"
            "- `ORB_RECLAIMED` — -3% 눌림 후 ORB 30/60 회복\n"
            "- `PREV_HIGH_RECLAIMED` — -3% 눌림 후 전일 고가 회복\n"
            "- `INVALID` — Fill reject / 거래정지 / 상하한 고착 / VI / 단일가\n\n"
            "**정렬**: 1차 상태 우선순위 (VWAP > ORB > PREV_HIGH > DROP_HIT > WAIT_DROP) / "
            "2차 V2 점수 내림차순.\n\n"
            "산출되면 이 탭에서 자동 표시됩니다."
        )
        # 백데이터 참고 (-3% 눌림 후 VWAP 회복 진입 결과)
        st.markdown("---")
        st.markdown("### 📊 백데이터 참고 — -3% 눌림 후 VWAP 회복 진입 (1년)")
        rows = [
            ["TP1/SL1 (+1/-1%)",  "75.30%",  "+24.04%p",  "-0.029",  "minute_proxy_phase1"],
            ["TP2/SL2 (+2/-2%)",  "75.30%",  "+18.33%p",  "+0.141",  "minute_proxy_phase1"],
            ["TP3/SL3 (+3/-3%)",  "75.30%",  "+14.48%p",  "+0.232",  "minute_proxy_phase1"],
        ]
        st.dataframe(
            pd.DataFrame(rows, columns=["청산 조합", "진입 성공률", "익절-손절 우위", "평균 순수익", "비고"]),
            use_container_width=True, hide_index=True,
        )
        st.caption(
            "⚠️ VI / 단일가 / 거래정지 / 호가잔량 미반영 — 운영 기준 아닌 연구 후보. "
            "OOS 검증 + 최종 Realistic Fill Filter 통과 후에만 운영 승격 가능."
        )
        return

    # Codex 산출 후 자동 활성화
    try:
        pb = pd.read_csv(pb_path, dtype=str, encoding="utf-8-sig").fillna("")
        st.success(f"✅ 눌림 후 회복 Top3 로드 — {len(pb)} 건")
        st.dataframe(pb, use_container_width=True, hide_index=True, height=400)
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")


# ─────────────────────────────────────────────────────────────────────
# 2026-05-15 신설 — 🟢 전일 종가 색깔 복기 탭
# CLOSINGBELL_PREV_CLOSE_COLOR_REVIEW_DASHBOARD_FEEDBACK_20260515.md §5 반영.
# 사후 복기용. 운영 V2 점수 산식 / D0 필터 / 웹훅 발송 일절 변경 X.
# ─────────────────────────────────────────────────────────────────────

# 색깔 시각 매핑
_COLOR_HEX = {
    "G": "#16a34a",  # 초록
    "Y": "#facc15",  # 노랑
    "O": "#f97316",  # 주황
    "R": "#dc2626",  # 빨강
    "X": "#9ca3af",  # 회색
}
_COLOR_KO = {
    "G": "완전 강세",
    "Y": "흔들렸지만 회복",
    "O": "위로 갔지만 실패",
    "R": "완전 약세",
    "X": "변동 거의 없음",
}
_POLICY_KO_FULL = {
    "V2_FINAL_TOP3":          "V2 점수제 Top3 (지금 운영 중)",
    "P0_TRADING_VALUE_TOP3":  "기존 거래대금 Top3",
    "P0_LEGACY_D0_RANK_TOP3": "기존 관심도 순위 Top3",
    "D0_POOL_ALL_RECENT_1M":  "전체 감시 종목 (D0 풀)",
}


def _load_prev_close_color_csvs() -> dict[str, pd.DataFrame]:
    """Codex 22:51 산출 전일 종가 색깔 CSV 들을 로딩.

    dashboard online_v2/latest 에 export 된 파일 우선, 없으면 Downloads 폴더 fallback.
    """
    out: dict[str, pd.DataFrame] = {}
    bundles = [
        ("cases", "prev_close_color_cases_recent_1m.csv",
                  "CHATGPT_WEB_PREV_CLOSE_COLOR_CASES_RECENT_1M_20260515.csv"),
        ("daily", "prev_close_color_daily_summary_recent_1m.csv",
                  "PREV_CLOSE_COLOR_DAILY_SUMMARY_RECENT_1M_20260515.csv"),
        ("pattern", "prev_close_color_pattern_summary_recent_1m.csv",
                    "PREV_CLOSE_COLOR_PATTERN_SUMMARY_RECENT_1M_20260515.csv"),
    ]
    download_root = Path(r"C:\Users\PYJ\Downloads")
    for key, online_name, downloads_name in bundles:
        online_path = ONLINE_V2_DIR / online_name
        downloads_path = download_root / downloads_name
        path = online_path if online_path.exists() else downloads_path
        if path.exists():
            try:
                out[key] = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            except Exception:
                out[key] = pd.DataFrame()
        else:
            out[key] = pd.DataFrame()
    return out


def _color_chip(code: str) -> str:
    """색깔 코드 → HTML 색 동그라미 + 한글 라벨."""
    hex_c = _COLOR_HEX.get(code, "#9ca3af")
    ko = _COLOR_KO.get(code, "?")
    return (
        f'<span style="display:inline-flex; align-items:center; gap:6px;">'
        f'<span style="display:inline-block; width:14px; height:14px; '
        f'border-radius:50%; background:{hex_c};"></span>'
        f'<span>{ko}</span></span>'
    )


def _path_to_html(path: str) -> str:
    """color_path (예: 'G-Y-O-Y-O') → 5개 색 동그라미 가로 배치."""
    parts = (path or "").split("-")
    dots = []
    for c in parts:
        hex_c = _COLOR_HEX.get(c, "#9ca3af")
        dots.append(
            f'<span title="{_COLOR_KO.get(c, c)}" '
            f'style="display:inline-block; width:18px; height:18px; '
            f'border-radius:50%; background:{hex_c}; margin-right:4px; '
            f'border:1px solid rgba(0,0,0,0.1);"></span>'
        )
    return '<div style="white-space:nowrap;">' + "".join(dots) + '</div>'


def render_prev_close_color_review() -> None:
    """전일 종가 기준 색깔 복기 - 한 달치 사후 복기.

    구조 (피드백 §5):
        1. 색깔 설명 카드 5개 (그림처럼)
        2. 정책별 요약 카드 4개
        3. 메인 케이스 테이블 + 필터 8개
        4. 패턴 요약 카드 5개 (가설별)
        5. 일자별 / 정책별 색깔 분포
    """
    st.subheader("🟢 전일 종가 색깔 복기 (한 달치)")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#16a34a; background:rgba(22,163,74,0.08);">'
        '<b>이 탭은 사후 복기용입니다.</b> Codex 2026-05-15 22:51 산출 — 최근 22 거래일 D0/V2/P0 후보의 '
        '<b>전일 종가 기준 색깔 흐름</b>을 표시합니다.<br>'
        '운영 V2 점수 산식 / D0 필터 / 웹훅 발송 일절 변경 없음. '
        '<b>매수 추천이 아니며 자동매매 연결도 없습니다.</b>'
        '</div>',
        unsafe_allow_html=True,
    )

    csvs = _load_prev_close_color_csvs()
    cases = csvs.get("cases", pd.DataFrame())
    daily = csvs.get("daily", pd.DataFrame())
    pattern = csvs.get("pattern", pd.DataFrame())

    if cases.empty:
        st.warning(
            "⚠️ 전일 종가 색깔 CSV가 없습니다.\n\n"
            "Codex 가 다음 명령으로 생성:\n"
            "```\npython -m bell_data.research prev_close_color_review --date 2026-05-15\n```\n\n"
            "위치 (자동 인식):\n"
            f"- 우선: `{ONLINE_V2_DIR}/prev_close_color_cases_recent_1m.csv`\n"
            f"- 보조: `C:\\Users\\PYJ\\Downloads\\CHATGPT_WEB_PREV_CLOSE_COLOR_CASES_RECENT_1M_*.csv`"
        )
        return

    # ── 1. 색깔 설명 카드 5개 ─────────────────────────────────────
    st.markdown("### 🎨 다섯 가지 색깔이 무슨 뜻인가요")
    info_cols = st.columns(5)
    color_info = [
        ("G", "완전 강세",     "어제 가격 위에서만 놀고\n더 높게 끝남",       "매수세 강함"),
        ("Y", "흔들렸지만 회복", "잠깐 떨어졌다가 위로 회복",                "종가 방어 성공"),
        ("O", "위로 갔지만 실패", "한 번 올라갔지만\n아래로 끝남",            "돌파 실패 / 윗꼬리"),
        ("R", "완전 약세",     "어제 가격 위로 한 번도 못 가고\n떨어진 채 끝남", "매수세 약함"),
        ("X", "변동 거의 없음", "어제와 거의 같거나\n데이터 부족",            "방향 없음"),
    ]
    for col, (code, name, action, meaning) in zip(info_cols, color_info):
        hex_c = _COLOR_HEX[code]
        col.markdown(
            f"""
<div style="border:1.5px solid {hex_c}; border-radius:10px; padding:10px; background:rgba(255,255,255,0.6);">
    <div style="text-align:center; margin-bottom:6px;">
        <span style="display:inline-block; width:36px; height:36px; border-radius:50%;
                     background:{hex_c};"></span>
    </div>
    <div style="text-align:center; font-size:1.05em; font-weight:bold; color:{hex_c}; margin-bottom:6px;">
        {name}
    </div>
    <div style="font-size:0.85em; color:#374151; text-align:center; line-height:1.5; min-height:50px;">
        {action.replace(chr(10), "<br>")}
    </div>
    <div style="font-size:0.82em; color:#6b7280; text-align:center; margin-top:6px;">
        ▸ {meaning}
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── 2. 정책별 요약 카드 4개 ──────────────────────────────────
    st.markdown("### 📊 각 방식별 22일 누적 요약")
    sum_cols = st.columns(4)
    pol_order = ["V2_FINAL_TOP3", "P0_TRADING_VALUE_TOP3", "P0_LEGACY_D0_RANK_TOP3", "D0_POOL_ALL_RECENT_1M"]
    pol_color = {
        "V2_FINAL_TOP3":          "#7c3aed",
        "P0_TRADING_VALUE_TOP3":  "#3b82f6",
        "P0_LEGACY_D0_RANK_TOP3": "#0891b2",
        "D0_POOL_ALL_RECENT_1M":  "#6b7280",
    }
    for col, pol in zip(sum_cols, pol_order):
        sub = cases[cases["policy_key"] == pol]
        n = len(sub)
        if n == 0:
            col.info(f"{_POLICY_KO_FULL[pol]}: 데이터 없음")
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        d1_dist = sub["dplus1_color"].value_counts()
        top_color = d1_dist.idxmax() if not d1_dist.empty else "X"
        top_color_pct = d1_dist.max() * 100 / max(n, 1) if not d1_dist.empty else 0
        c = pol_color[pol]
        col.markdown(
            f"""
<div style="border:1.5px solid {c}; border-radius:10px; padding:12px; background:rgba(255,255,255,0.6);">
    <div style="font-size:0.92em; font-weight:bold; color:{c}; margin-bottom:6px;">
        {_POLICY_KO_FULL[pol]}
    </div>
    <div style="font-size:0.88em; color:#6b7280;">고른 종목 수</div>
    <div style="font-size:1.4em; font-weight:bold; margin-bottom:8px;">{n} 건</div>
    <hr style="margin:6px 0; border-color:#e5e7eb;">
    <div style="font-size:0.85em; line-height:1.6;">
        <div>5일 안 익절 먼저: <b style="color:#16a34a;">{profit}/{n} ({profit*100/max(n,1):.0f}%)</b></div>
        <div>5일 안 손절 먼저: <b style="color:#dc2626;">{loss}/{n} ({loss*100/max(n,1):.0f}%)</b></div>
        <div style="margin-top:6px;">
            다음날 가장 많이 나온 색깔:<br>
            <span style="display:inline-block; width:14px; height:14px; border-radius:50%;
                         background:{_COLOR_HEX[top_color]}; vertical-align:middle;
                         margin-right:5px;"></span>
            <b>{_COLOR_KO[top_color]}</b> ({top_color_pct:.0f}%)
        </div>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ── 3. 메인 케이스 테이블 + 필터 ─────────────────────────────
    st.markdown("### 🔍 종목별 색깔 흐름 (필터 적용)")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        sel_pol = st.selectbox(
            "정책",
            ["V2 점수제 Top3", "기존 거래대금 Top3", "기존 관심도 Top3", "D0 전체 풀", "공통 (V2 ∩ P0)", "V2 만", "P0 만"],
            key="prev_color_pol",
        )
    with f_col2:
        sel_d1 = st.selectbox(
            "다음날 색깔",
            ["전체", "🟢 완전 강세", "🟡 흔들렸지만 회복", "🟠 위로 갔지만 실패", "🔴 완전 약세", "⚪ 변동 거의 없음"],
            key="prev_color_d1",
        )
    with f_col3:
        sel_outcome = st.selectbox(
            "5일 결과",
            ["전체", "익절 먼저 닿음", "손절 먼저 닿음"],
            key="prev_color_outcome",
        )
    with f_col4:
        sel_search = st.text_input("종목명 검색", key="prev_color_search")

    # 필터링
    filtered = cases.copy()
    pol_map = {
        "V2 점수제 Top3": "V2_FINAL_TOP3",
        "기존 거래대금 Top3": "P0_TRADING_VALUE_TOP3",
        "기존 관심도 Top3": "P0_LEGACY_D0_RANK_TOP3",
        "D0 전체 풀": "D0_POOL_ALL_RECENT_1M",
    }
    if sel_pol in pol_map:
        filtered = filtered[filtered["policy_key"] == pol_map[sel_pol]]
    elif sel_pol == "공통 (V2 ∩ P0)":
        filtered = filtered[filtered["relationship_group"] == "BOTH"]
    elif sel_pol == "V2 만":
        filtered = filtered[filtered["relationship_group"] == "V2_ONLY"]
    elif sel_pol == "P0 만":
        filtered = filtered[filtered["relationship_group"] == "P0_ONLY"]

    color_filter_map = {
        "🟢 완전 강세": "G", "🟡 흔들렸지만 회복": "Y",
        "🟠 위로 갔지만 실패": "O", "🔴 완전 약세": "R", "⚪ 변동 거의 없음": "X",
    }
    if sel_d1 in color_filter_map:
        filtered = filtered[filtered["dplus1_color"] == color_filter_map[sel_d1]]

    if sel_outcome == "익절 먼저 닿음":
        filtered = filtered[filtered["d5_first_touch_result"] == "profit_first"]
    elif sel_outcome == "손절 먼저 닿음":
        filtered = filtered[filtered["d5_first_touch_result"] == "loss_first"]

    if sel_search:
        filtered = filtered[filtered["stock_name"].str.contains(sel_search, na=False)]

    st.caption(f"필터 결과: **{len(filtered)} 건** / 전체 {len(cases)} 건")

    # 표시 컬럼 + 한글 + 색깔 칸 배경색 (HTML 직접 렌더링)
    if not filtered.empty:
        outcome_ko = {
            "FAST_WIN": "빠른 성공", "SLOW_WIN": "늦은 성공",
            "BOTH_PROFIT_FIRST": "양쪽 닿음 (이익 먼저)",
            "BOTH_LOSS_FIRST": "양쪽 닿음 (손실 먼저)",
            "LOSS_FIRST": "손실 먼저",
            "AMBIGUOUS": "애매", "NO_TOUCH": "닿지 않음", "": "—",
        }
        first_ko = {
            "profit_first": "이익 먼저", "loss_first": "손실 먼저",
            "no_touch": "닿지 않음", "ambiguous": "애매", "": "—",
        }
        ko_short = {"G": "강", "Y": "회", "O": "실", "R": "약", "X": "보"}
        # HTML 표 직접 생성 (배경색 칸)
        head_html = (
            "<thead style='background:#e0e7ff;'><tr style='font-weight:bold; color:#1e3a8a;'>"
            "<th style='padding:6px;'>신호일</th>"
            "<th style='padding:6px;'>종목</th>"
            "<th style='padding:6px;'>정책</th>"
            "<th style='padding:6px;'>순위</th>"
            "<th style='padding:6px;'>점수</th>"
            "<th style='padding:6px;'>다음날</th>"
            "<th style='padding:6px;'>2일째</th>"
            "<th style='padding:6px;'>3일째</th>"
            "<th style='padding:6px;'>4일째</th>"
            "<th style='padding:6px;'>5일째</th>"
            "<th style='padding:6px;'>결과</th>"
            "<th style='padding:6px;'>최고상승%</th>"
            "<th style='padding:6px;'>최저하락%</th>"
            "</tr></thead>"
        )
        body_html = "<tbody>"
        for i, (_, r) in enumerate(filtered.head(50).iterrows()):
            row_bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            d_colors = []
            for k in ["dplus1_color", "dplus2_color", "dplus3_color", "dplus4_color", "dplus5_color"]:
                c = str(r.get(k, ""))
                hex_c = _COLOR_HEX.get(c, "#f3f4f6")
                short = ko_short.get(c, "—")
                txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
                d_colors.append(
                    f"<td style='background:{hex_c}; color:{txt_color}; text-align:center; "
                    f"font-weight:bold; padding:6px; min-width:46px;'>{short}</td>"
                )
            score_val = r.get("score_v2", "")
            try:
                score_str = f"{float(score_val):.1f}"
            except Exception:
                score_str = "—"
            mfe = r.get("mfe_d5_pct", "")
            mae = r.get("mae_d5_pct", "")
            try:
                mfe_str = f"+{float(mfe):.1f}"
            except Exception:
                mfe_str = "—"
            try:
                mae_str = f"{float(mae):.1f}"
            except Exception:
                mae_str = "—"
            body_html += (
                f"<tr style='background:{row_bg};'>"
                f"<td style='padding:6px;'>{r.get('signal_date', '')}</td>"
                f"<td style='padding:6px;'><b>{r.get('stock_name', '')}</b><br>"
                f"<span style='font-size:0.85em; color:#6b7280;'>{r.get('stock_code', '')}</span></td>"
                f"<td style='padding:6px; font-size:0.85em;'>{r.get('policy_label_ko', '')}</td>"
                f"<td style='padding:6px; text-align:center;'>{r.get('rank', '')}</td>"
                f"<td style='padding:6px; text-align:center;'>{score_str}</td>"
                f"{''.join(d_colors)}"
                f"<td style='padding:6px; font-size:0.9em;'>{outcome_ko.get(str(r.get('outcome_label', '')), '')}</td>"
                f"<td style='padding:6px; text-align:right; color:#16a34a;'>{mfe_str}</td>"
                f"<td style='padding:6px; text-align:right; color:#dc2626;'>{mae_str}</td>"
                f"</tr>"
            )
        body_html += "</tbody>"
        full_html = (
            "<div style='max-height:480px; overflow-y:auto;'>"
            "<table style='width:100%; border-collapse:collapse; font-size:0.92em;'>"
            f"{head_html}{body_html}"
            "</table></div>"
        )
        st.markdown(full_html, unsafe_allow_html=True)

        # 색깔 범례
        st.caption(
            "각 칸 색깔 = 그 날 전일 종가 기준 결과 — "
            "🟢 강(완전 강세) · 🟡 회(흔들렸다 회복) · 🟠 실(위로 갔지만 실패) · "
            "🔴 약(완전 약세) · ⚪ 보(변동 거의 없음)"
        )
        if len(filtered) > 50:
            st.caption(f"… 외 {len(filtered) - 50} 건 더 있음. 필터를 좁히면 위 표에 더 표시됩니다.")
    else:
        st.info("필터에 해당하는 종목이 없습니다.")

    st.divider()

    # ── 4. 패턴 요약 카드 5개 ────────────────────────────────────
    st.markdown("### 🧭 가설별 색깔 흐름 패턴 검증")
    st.caption("Codex 가 만든 481 가지 색깔 흐름 패턴 중 사용자 가설 5개와 매칭 (V2 정책 기준)")

    v2_pat = pattern[pattern["policy_key"] == "V2_FINAL_TOP3"].copy() if not pattern.empty else pd.DataFrame()
    for col in ["sample_n", "plus2_first_rate_pct", "minus2_first_rate_pct",
                "plus3_first_rate_pct", "minus3_first_rate_pct",
                "profit_minus_loss_pp", "avg_mfe_d5_pct", "avg_mae_d5_pct"]:
        if col in v2_pat.columns:
            v2_pat[col] = pd.to_numeric(v2_pat[col], errors="coerce")

    hypotheses = [
        ("Y-G", "🟡 → 🟢", "흔들렸다 회복 → 강세 (가설 1)"),
        ("R-Y-G", "🔴 → 🟡 → 🟢", "약세 → 회복 → 강세 (가설 2)"),
        ("G-G-G", "🟢 → 🟢 → 🟢", "강세 3일 연속 (가설 3)"),
        ("O-R", "🟠 → 🔴", "실패 마감 → 약세 (가설 4)"),
        ("Y-O-R", "🟡 → 🟠 → 🔴", "회복 → 실패 → 약세 (가설 5)"),
    ]
    h_cols = st.columns(5)
    for col, (prefix, dots, desc) in zip(h_cols, hypotheses):
        matched = v2_pat[v2_pat["color_path"].str.startswith(prefix, na=False)] if not v2_pat.empty else pd.DataFrame()
        n_total = matched["sample_n"].sum() if not matched.empty else 0
        if n_total > 0:
            weighted_diff = (matched["profit_minus_loss_pp"] * matched["sample_n"]).sum() / max(n_total, 1)
            avg_mfe = (matched["avg_mfe_d5_pct"] * matched["sample_n"]).sum() / max(n_total, 1)
            avg_mae = (matched["avg_mae_d5_pct"] * matched["sample_n"]).sum() / max(n_total, 1)
        else:
            weighted_diff = avg_mfe = avg_mae = 0.0
        color = "#16a34a" if weighted_diff > 0 else "#dc2626" if weighted_diff < 0 else "#6b7280"
        col.markdown(
            f"""
<div style="border:1.5px solid {color}; border-radius:10px; padding:10px; background:rgba(255,255,255,0.6);">
    <div style="font-size:1.4em; text-align:center; margin-bottom:4px;">{dots}</div>
    <div style="font-size:0.82em; color:#6b7280; text-align:center; min-height:36px;">{desc}</div>
    <hr style="margin:6px 0; border-color:#e5e7eb;">
    <div style="font-size:0.85em; line-height:1.7;">
        <div>표본: <b>{int(n_total)} 건</b></div>
        <div>익절-손절 차: <b style="color:{color};">{weighted_diff:+.1f}%p</b></div>
        <div>최고 상승: <span style="color:#16a34a;">+{avg_mfe:.1f}%</span></div>
        <div>최저 하락: <span style="color:#dc2626;">{avg_mae:.1f}%</span></div>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )
    st.caption("⚠️ 표본 N<10인 패턴은 통계 유효성 약함 — 1년치 확장 후 재검증 필요.")

    st.divider()

    # ── 5. 일자별 정책별 색깔 분포 ──────────────────────────────
    st.markdown("### 📅 일자별 색깔 분포 (V2 점수제)")
    if not daily.empty:
        v2_daily = daily[daily["policy_key"] == "V2_FINAL_TOP3"].copy()
        if not v2_daily.empty:
            for col in v2_daily.columns:
                if col not in ("signal_date", "policy_key", "policy_label_ko"):
                    v2_daily[col] = pd.to_numeric(v2_daily[col], errors="coerce")
            show_daily = v2_daily[[
                "signal_date", "candidate_n",
                "dplus1_G_count", "dplus1_Y_count", "dplus1_O_count", "dplus1_R_count",
                "d5_profit_first_rate_pct", "d5_loss_first_rate_pct",
            ]].rename(columns={
                "signal_date": "신호일", "candidate_n": "종목수",
                "dplus1_G_count": "다음날 🟢",
                "dplus1_Y_count": "다음날 🟡",
                "dplus1_O_count": "다음날 🟠",
                "dplus1_R_count": "다음날 🔴",
                "d5_profit_first_rate_pct": "5일 익절먼저 %",
                "d5_loss_first_rate_pct": "5일 손절먼저 %",
            })
            st.dataframe(show_daily, use_container_width=True, hide_index=True, height=300)

    # ── 푸터 ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="background:#fef3c7; border-left:4px solid #d97706; padding:10px 14px; '
        'border-radius:6px; font-size:0.9em; color:#78350f;">'
        '🛡 <b>이 탭의 한계와 다음 단계</b><br>'
        '• 한 달(22일) 표본은 통계 유효성 약함 → Codex 가 1년치(252일)로 확장 예정.<br>'
        '• 색깔이 좋아도 ‘진짜 그 가격에 살 수 있었나(호가/거래량/잠김)’는 별도 검증 필요.<br>'
        '• 다음에 차트 연동(행 클릭 → 5일 가격 차트 + 색깔 배경) 추가 예정.<br>'
        '• 이 화면은 사후 복기용. 운영 V2 점수제와 15:00 웹훅은 그대로 유지됩니다.'
        '</div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_whole_market_pattern_summary(name: str) -> pd.DataFrame:
    path = WHOLE_MARKET_PATTERN_DIR / f"{name}_20260516.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


@st.cache_data(show_spinner=False)
def load_whole_market_pattern_color_counts() -> pd.DataFrame:
    if not WHOLE_MARKET_PATTERN_COLOR_COUNTS_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(WHOLE_MARKET_PATTERN_COLOR_COUNTS_PATH, encoding="utf-8-sig")
    if "rows" in df.columns:
        df["rows"] = pd.to_numeric(df["rows"], errors="coerce").fillna(0).astype(int)
    return df


@st.cache_data(show_spinner="전날 패턴 케이스 로딩…")
def load_whole_market_pattern_cases(use_full_positive: bool = False, target_mode: str = "close_up") -> pd.DataFrame:
    """전날 패턴 실험실 케이스.

    target_mode:
    - close_up: D+1 종가가 D0 종가보다 높은 모든 케이스
    - green: D+1 저가까지 D0 종가 이상을 지킨 종가 상승 케이스
    - yellow: D+1 장중 D0 종가 아래로 흔들렸지만 종가 상승 케이스
    - orange: D+1 장중 D0 종가 위로 갔지만 종가 실패 케이스
    - red: D+1 장중 D0 종가 위로 못 간 실패 케이스
    """
    target_files = {
        "close_up": (WHOLE_MARKET_PATTERN_CLOSE_UP_PATH, WHOLE_MARKET_PATTERN_CLOSE_UP_SAMPLE_PATH),
        "green": (WHOLE_MARKET_PATTERN_POSITIVE_PATH, WHOLE_MARKET_PATTERN_SAMPLE_PATH),
        "full_above": (WHOLE_MARKET_PATTERN_POSITIVE_PATH, WHOLE_MARKET_PATTERN_SAMPLE_PATH),
        "yellow": (WHOLE_MARKET_PATTERN_YELLOW_PATH, WHOLE_MARKET_PATTERN_YELLOW_SAMPLE_PATH),
        "orange": (WHOLE_MARKET_PATTERN_ORANGE_PATH, WHOLE_MARKET_PATTERN_ORANGE_SAMPLE_PATH),
        "red": (WHOLE_MARKET_PATTERN_RED_PATH, WHOLE_MARKET_PATTERN_RED_SAMPLE_PATH),
    }
    full_path, sample_path = target_files.get(target_mode, target_files["close_up"])

    if use_full_positive and full_path.exists():
        df = pd.read_parquet(full_path)
    elif sample_path.exists():
        df = pd.read_csv(sample_path, dtype={"code": str}, encoding="utf-8-sig")
    elif full_path.exists():
        df = pd.read_parquet(full_path)
    else:
        return pd.DataFrame()
    if df.empty:
        return df
    df = df.copy()
    df["code"] = df["code"].astype(str).str.zfill(6)
    for col in ["d0_date", "d1_date"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
    if "d1_rel_color" not in df.columns:
        df["d1_rel_color"] = {"green": "G", "yellow": "Y", "orange": "O", "red": "R"}.get(target_mode, "")
    numeric_cols = [
        "d0_close", "d1_open", "d1_low", "d1_high", "d1_close",
        "d0_ret_pct", "d0_gap_pct", "d0_intraday_ret_pct", "d0_upper_shadow_pct",
        "d0_lower_shadow_pct", "d0_range_pct", "d0_trading_value_eok",
        "d0_value_vs_20d", "d0_volume_vs_20d", "d0_close_vs_ma20_pct",
        "d0_60d_value_above_close_share", "d0_60d_turnover_eok",
        "d1_ret_vs_d0_close_pct", "d1_gap_vs_d0_close_pct",
        "d1_low_vs_d0_close_pct", "d1_high_vs_d0_close_pct",
        "kospi_change_pct_asof", "kosdaq_change_pct_asof", "nasdaq_change_pct_asof",
        "sp500_change_pct_asof", "usdkrw_change_pct_asof", "vix_change_pct_asof",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _pattern_lab_rate_text(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n * 100:.2f}%"


def _pattern_lab_num(value: Any, digits: int = 1, suffix: str = "") -> str:
    n = numeric(value)
    if n is None or pd.isna(n):
        return "-"
    return f"{n:,.{digits}f}{suffix}"


def _pattern_lab_color_label(value: Any) -> str:
    labels = {
        "G": "녹색",
        "Y": "노랑",
        "O": "주황",
        "R": "빨강",
    }
    return labels.get(str(value), "기타")


def _pattern_lab_summary_table(df: pd.DataFrame, group_col: str, label_map: dict[str, str] | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    label_map = label_map or {}
    rename = {
        group_col: label_map.get(group_col, group_col),
        "N": "표본",
        "d1_close_up_rate": "D+1 종가상승",
        "d1_gap_hold_rate": "D+1 갭유지",
        "d1_full_above_rate": "시고저종 전부 위",
        "median_d0_ret_pct": "D0 중앙등락",
        "median_d0_value_eok": "D0 중앙거래대금",
        "median_value_vs_20d": "20일대비 거래대금",
        "median_ma20_pct": "MA20 대비",
        "median_supply_overhang": "상단매물 근사",
    }
    for col in ["d1_close_up_rate", "d1_gap_hold_rate", "d1_full_above_rate"]:
        if col in out.columns:
            out[col] = out[col].map(_pattern_lab_rate_text)
    for col in ["median_d0_ret_pct", "median_ma20_pct"]:
        if col in out.columns:
            out[col] = out[col].map(lambda v: _format_pct(v))
    if "median_d0_value_eok" in out.columns:
        out["median_d0_value_eok"] = out["median_d0_value_eok"].map(lambda v: _pattern_lab_num(v, 1, "억"))
    for col in ["median_value_vs_20d", "median_supply_overhang"]:
        if col in out.columns:
            out[col] = out[col].map(lambda v: _pattern_lab_num(v, 3))
    return out.rename(columns=rename)


def _pattern_lab_notes_lookup() -> set[tuple[str, str]]:
    notes = read_csv(str(WHOLE_MARKET_PATTERN_NOTES_PATH))
    if notes.empty or "signal_date" not in notes.columns or "stock_code" not in notes.columns:
        return set()
    return {
        (str(r.get("signal_date", "")), normalize_code(r.get("stock_code", "")))
        for _, r in notes.iterrows()
    }


def plot_pattern_lab_daily_candle(row: pd.Series) -> None:
    code = normalize_code(row.get("code", ""))
    daily = load_daily(code)
    if daily.empty:
        st.warning("일봉 parquet 파일이 없습니다.")
        return
    d0 = pd.to_datetime(row.get("d0_date"))
    d1 = pd.to_datetime(row.get("d1_date"))
    start = d0 - pd.Timedelta(days=180)
    end = d1 + pd.Timedelta(days=35)
    view = daily[(daily["date"] >= start) & (daily["date"] <= end)].copy()
    if view.empty:
        st.warning("선택 기간의 일봉 데이터가 없습니다.")
        return

    d0_close = numeric(row.get("d0_close"))
    if go and make_subplots:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.04)
        fig.add_trace(
            go.Candlestick(
                x=view["date"],
                open=view["open"],
                high=view["high"],
                low=view["low"],
                close=view["close"],
                name="일봉",
            ),
            row=1,
            col=1,
        )
        for window, color in [(5, "#2563eb"), (20, "#16a34a"), (60, "#9333ea")]:
            col = f"ma{window}"
            if col in view.columns:
                fig.add_trace(
                    go.Scatter(x=view["date"], y=view[col], mode="lines", name=f"MA{window}", line={"width": 1, "color": color}),
                    row=1,
                    col=1,
                )
        fig.add_trace(go.Bar(x=view["date"], y=view["volume"], name="거래량", marker_color="#94a3b8"), row=2, col=1)
        if d0_close:
            for pct, label, color in [
                (0, "D0 종가", "#111827"),
                (0.01, "+1%", "#16a34a"),
                (0.03, "+3%", "#7c3aed"),
                (-0.02, "-2%", "#dc2626"),
            ]:
                fig.add_hline(y=d0_close * (1 + pct), line_dash="dot", line_color=color, annotation_text=label, row=1, col=1)
        add_vertical_marker(fig, str(d0.date()), "D0", "#f97316")
        add_vertical_marker(fig, str(d1.date()), "D+1", "#16a34a")
        fig.update_layout(
            height=520,
            xaxis_rangeslider_visible=False,
            margin={"l": 8, "r": 8, "t": 28, "b": 8},
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(view.set_index("date")[["close", "ma5", "ma20", "ma60"]])


def render_whole_market_pattern_lab() -> None:
    st.subheader("🧪 전날 패턴 실험실")
    st.markdown(
        '<div class="cb-note" style="border-left-color:#0f766e; background:rgba(15,118,110,0.08);">'
        '<b>보통주 전체 10년 일봉</b>에서 D+1 종가 상승 전체와 녹색/노랑/주황/빨강 비교군을 날짜별로 보는 화면입니다. '
        '녹색은 D+1 시가·고가·저가·종가가 D0 종가 이상이고 종가는 상승한 케이스입니다. '
        '운영 후보 선정, V2 산식, 웹훅, 주문/계좌 로직은 건드리지 않는 읽기 전용 복기 탭입니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    by_market = load_whole_market_pattern_summary("by_market")
    if by_market.empty:
        st.warning(
            "전날 패턴 실험실 데이터가 없습니다. 먼저 다음 산출을 실행해야 합니다.\n\n"
            "`python C:\\Coding\\projects\\bell-data\\scripts\\whole_market_next_green_daily_probe_20260516.py`"
        )
        return

    total_n = int(pd.to_numeric(by_market.get("N", pd.Series(dtype=float)), errors="coerce").sum())
    close_up_n = int((pd.to_numeric(by_market["N"], errors="coerce") * pd.to_numeric(by_market["d1_close_up_rate"], errors="coerce")).sum())
    positive_n = int((pd.to_numeric(by_market["N"], errors="coerce") * pd.to_numeric(by_market["d1_full_above_rate"], errors="coerce")).sum())
    color_counts = load_whole_market_pattern_color_counts()
    color_rows = {}
    if not color_counts.empty:
        color_rows = dict(zip(color_counts["d1_rel_color"].astype(str), color_counts["rows"].astype(int)))
    green_n = color_rows.get("G", positive_n)
    yellow_n = color_rows.get("Y", 0)
    orange_n = color_rows.get("O", 0)
    red_n = color_rows.get("R", 0)
    target_options = {
        "D+1 종가 상승 전체": "close_up",
        "녹색: 저가까지 D0 종가 이상": "green",
        "노랑: 흔들린 뒤 종가 상승": "yellow",
        "주황: 위로 갔다 종가 실패": "orange",
        "빨강: 위로 못 감": "red",
    }
    target_label = st.radio(
        "표시 대상",
        list(target_options.keys()),
        horizontal=True,
        key="pattern_lab_target_mode_v2",
    )
    target_mode = target_options[target_label]
    sample_default = load_whole_market_pattern_cases(use_full_positive=False, target_mode=target_mode)
    target_n = {
        "close_up": close_up_n,
        "green": green_n,
        "yellow": yellow_n,
        "orange": orange_n,
        "red": red_n,
    }.get(target_mode, close_up_n)

    metric_cols = st.columns(6)
    metric_cols[0].metric("10년 D0 라벨", f"{total_n:,}건")
    metric_cols[1].metric("D+1 종가 상승", f"{close_up_n:,}건")
    metric_cols[2].metric("녹색", f"{green_n:,}건")
    metric_cols[3].metric("노랑", f"{yellow_n:,}건")
    metric_cols[4].metric("주황", f"{orange_n:,}건")
    metric_cols[5].metric("현재 대상 비율", f"{target_n / max(total_n, 1) * 100:.2f}%")
    if not color_counts.empty:
        color_show = color_counts.copy()
        color_show["구분"] = color_show["d1_rel_color"].map(_pattern_lab_color_label)
        color_show["비율"] = color_show["rows"].map(lambda v: f"{v / max(total_n, 1) * 100:.2f}%")
        st.dataframe(
            color_show[["구분", "rows", "비율"]].rename(columns={"rows": "건수"}),
            use_container_width=True,
            hide_index=True,
            height=170,
        )

    st.markdown("### 기준별 양성률")
    s_tabs = st.tabs(["시장", "거래대금", "거래대금 증가", "MA20 위치", "매물대 근사", "업종"])
    summary_specs = [
        ("by_market", "market", "시장"),
        ("by_d0_value_bucket", "d0_value_bucket", "D0 거래대금 분위"),
        ("by_value_vs_20d_bucket", "d0_value_vs_20d_bucket", "20일대비 거래대금"),
        ("by_ma20_bucket", "d0_ma20_bucket", "MA20 위치"),
        ("by_supply_overhang_bucket", "d0_supply_overhang_bucket", "상단 매물 근사"),
        ("by_sector_top", "sector", "업종"),
    ]
    for tab, (file_key, group_col, label) in zip(s_tabs, summary_specs):
        with tab:
            table = load_whole_market_pattern_summary(file_key)
            show = _pattern_lab_summary_table(table, group_col, {group_col: "구분"})
            if not show.empty:
                group_label = f"{label} 구분" if label in show.columns else label
                show = show.rename(columns={"구분": group_label})
            st.dataframe(show.head(30), use_container_width=True, hide_index=True, height=260)

    st.markdown("### 양성 케이스 탐색")
    controls = st.columns([1.25, 1.0, 1.0, 1.0, 1.1, 1.35])
    with controls[0]:
        use_full = st.checkbox("전체 기간 사용", value=True, key="pattern_lab_use_full")
    cases = load_whole_market_pattern_cases(use_full_positive=use_full, target_mode=target_mode)
    if cases.empty:
        st.info("표시할 양성 케이스가 없습니다.")
        return

    with controls[1]:
        market_opts = sorted(cases["market"].dropna().astype(str).unique().tolist())
        selected_markets = st.multiselect("시장", market_opts, default=market_opts, key="pattern_lab_market")
    with controls[2]:
        value_opts = sorted(cases["d0_value_bucket"].dropna().astype(str).unique().tolist())
        selected_values = st.multiselect("거래대금", value_opts, default=value_opts, key="pattern_lab_value")
    with controls[3]:
        ma_opts = sorted(cases["d0_ma20_bucket"].dropna().astype(str).unique().tolist())
        selected_ma = st.multiselect("MA20", ma_opts, default=ma_opts, key="pattern_lab_ma")
    with controls[4]:
        period = st.selectbox("기간", ["전체", "최근 3년", "최근 1년", "최근 3개월"], key="pattern_lab_period")
    with controls[5]:
        keyword = st.text_input("검색", key="pattern_lab_search", placeholder="종목명/코드/업종")

    view = cases.copy()
    if selected_markets:
        view = view[view["market"].isin(selected_markets)]
    if selected_values:
        view = view[view["d0_value_bucket"].astype(str).isin(selected_values)]
    if selected_ma:
        view = view[view["d0_ma20_bucket"].astype(str).isin(selected_ma)]
    if period != "전체":
        max_date = pd.to_datetime(view["d0_date"]).max()
        days = {"최근 3개월": 100, "최근 1년": 370, "최근 3년": 1110}[period]
        min_date = max_date - pd.Timedelta(days=days)
        view = view[pd.to_datetime(view["d0_date"]) >= min_date]
    if keyword:
        q = keyword.strip().lower()
        hay = (
            view["name"].astype(str)
            + " "
            + view["code"].astype(str)
            + " "
            + view["sector"].astype(str)
            + " "
            + view["industry"].astype(str)
        ).str.lower()
        view = view[hay.str.contains(q, na=False)]

    view_mode = st.radio("보기 방식", ["날짜별 메모", "전체 표"], horizontal=True, key="pattern_lab_view_mode")
    sort_key = st.radio(
        "정렬",
        ["과거순", "최근순", "D+1 수익률", "20일대비 거래대금", "MA20 괴리"],
        horizontal=True,
        key="pattern_lab_sort",
    )
    if sort_key == "D+1 수익률":
        view = view.sort_values(["d1_ret_vs_d0_close_pct", "d0_trading_value_eok"], ascending=[False, False])
    elif sort_key == "20일대비 거래대금":
        view = view.sort_values(["d0_value_vs_20d", "d0_trading_value_eok"], ascending=[False, False])
    elif sort_key == "MA20 괴리":
        view = view.sort_values(["d0_close_vs_ma20_pct", "d0_trading_value_eok"], ascending=[False, False])
    elif sort_key == "최근순":
        view = view.sort_values(["d0_date", "d0_trading_value_eok"], ascending=[False, False])
    else:
        view = view.sort_values(["d0_date", "d0_trading_value_eok"], ascending=[True, False])

    st.caption(f"필터 결과: {len(view):,}건")
    notes_lookup = _pattern_lab_notes_lookup()
    if view.empty:
        return

    if view_mode == "날짜별 메모":
        dates = sorted(view["d0_date"].dropna().astype(str).unique().tolist())
        if not dates:
            st.info("필터 조건에 맞는 날짜가 없습니다.")
            return
        idx_key = "pattern_lab_date_idx"
        if idx_key not in st.session_state:
            st.session_state[idx_key] = 0
        st.session_state[idx_key] = max(0, min(int(st.session_state[idx_key]), len(dates) - 1))

        nav = st.columns([0.8, 0.8, 2.0, 1.2, 1.2, 1.8])
        with nav[0]:
            if st.button("이전 날짜", key="pattern_lab_prev_date", use_container_width=True, disabled=st.session_state[idx_key] <= 0):
                st.session_state[idx_key] -= 1
                st.rerun()
        with nav[1]:
            if st.button("다음 날짜", key="pattern_lab_next_date", use_container_width=True, disabled=st.session_state[idx_key] >= len(dates) - 1):
                st.session_state[idx_key] += 1
                st.rerun()
        with nav[2]:
            selected_date = st.selectbox("D0 날짜", dates, index=st.session_state[idx_key], key="pattern_lab_date_picker")
            st.session_state[idx_key] = dates.index(selected_date)
        day_view = view[view["d0_date"].astype(str).eq(selected_date)].copy()
        day_view = day_view.sort_values("d0_trading_value_eok", ascending=False)
        day_notes = sum((selected_date, normalize_code(code)) in notes_lookup for code in day_view["code"].astype(str))
        with nav[3]:
            st.metric("날짜 위치", f"{st.session_state[idx_key] + 1:,}/{len(dates):,}")
        with nav[4]:
            st.metric("해당일 종목", f"{len(day_view):,}개")
        with nav[5]:
            st.metric("메모", f"{day_notes:,}개")
        table_source = day_view
    else:
        table_source = view.head(300).copy()

    display = table_source.head(120).copy()
    display["메모"] = display.apply(lambda r: "Y" if (str(r.get("d0_date", "")), normalize_code(r.get("code", ""))) in notes_lookup else "", axis=1)
    display["종목"] = display.apply(lambda r: f"{r.get('name', '')} ({normalize_code(r.get('code', ''))})", axis=1)
    display["신호등"] = display["d1_rel_color"].map(_pattern_lab_color_label) if "d1_rel_color" in display.columns else ""
    display["D+1 수익률"] = display["d1_ret_vs_d0_close_pct"].map(_format_pct)
    display["D+1 저가"] = display["d1_low_vs_d0_close_pct"].map(_format_pct)
    display["D0 거래대금"] = display["d0_trading_value_eok"].map(lambda v: _pattern_lab_num(v, 1, "억"))
    display["20일대비"] = display["d0_value_vs_20d"].map(lambda v: _pattern_lab_num(v, 2))
    display["MA20"] = display["d0_close_vs_ma20_pct"].map(_format_pct)
    display["매물대"] = display["d0_60d_value_above_close_share"].map(lambda v: _pattern_lab_num(v, 2))
    display_cols = [
        "d0_date", "신호등", "종목", "market", "sector", "d0_value_bucket",
        "D0 거래대금", "20일대비", "MA20", "매물대", "D+1 수익률", "D+1 저가", "메모",
    ]
    st.dataframe(
        display[display_cols].rename(columns={
            "d0_date": "D0", "market": "시장", "sector": "업종", "d0_value_bucket": "거래대금 분위",
        }),
        use_container_width=True,
        hide_index=True,
        height=260 if view_mode == "날짜별 메모" else 360,
        column_config={
            "신호등": st.column_config.TextColumn("신호등", width="small"),
            "종목": st.column_config.TextColumn("종목", width="large"),
            "업종": st.column_config.TextColumn("업종", width="large"),
        },
    )
    if view_mode == "날짜별 메모":
        st.caption("날짜별 메모 모드에서는 과거 날짜부터 하루씩 넘기며, 해당 날짜 종목만 표와 선택 목록에 표시합니다.")
    elif len(view) > len(display):
        st.caption(f"전체 표 모드는 상위 {len(display)}건만 표시합니다. 날짜별 메모 모드를 쓰면 스크롤 없이 날짜 단위로 볼 수 있습니다.")

    label_rows = table_source.head(300).copy()
    label_rows["_select_label"] = label_rows.apply(
        lambda r: (
            f"{r.get('d0_date')} · {r.get('name')} ({normalize_code(r.get('code', ''))}) · "
            f"D+1 {_format_pct(r.get('d1_ret_vs_d0_close_pct'))} · "
            f"{_pattern_lab_num(r.get('d0_trading_value_eok'), 0, '억')}"
        ),
        axis=1,
    )
    selected_label = st.selectbox("상세로 볼 케이스", label_rows["_select_label"].tolist(), key="pattern_lab_selected_case")
    selected = label_rows[label_rows["_select_label"] == selected_label].iloc[0]

    left, right = st.columns([2.2, 1.0])
    with left:
        st.markdown(f"### {selected.get('name')} ({normalize_code(selected.get('code', ''))})")
        m = st.columns(5)
        m[0].metric("D+1 종가", _format_pct(selected.get("d1_ret_vs_d0_close_pct")))
        m[1].metric("D+1 저가", _format_pct(selected.get("d1_low_vs_d0_close_pct")))
        m[2].metric("D0 거래대금", _pattern_lab_num(selected.get("d0_trading_value_eok"), 1, "억"))
        m[3].metric("20일대비", _pattern_lab_num(selected.get("d0_value_vs_20d"), 2))
        m[4].metric("MA20 대비", _format_pct(selected.get("d0_close_vs_ma20_pct")))
        plot_pattern_lab_daily_candle(selected)
    with right:
        st.markdown("#### 전날 조건")
        info_df = pd.DataFrame([
            {"항목": "D0", "값": selected.get("d0_date", "")},
            {"항목": "D+1", "값": selected.get("d1_date", "")},
            {"항목": "시장/업종", "값": f"{selected.get('market', '')} · {selected.get('sector', '')}"},
            {"항목": "D0 등락", "값": _format_pct(selected.get("d0_ret_pct"))},
            {"항목": "D0 장중", "값": _format_pct(selected.get("d0_intraday_ret_pct"))},
            {"항목": "윗꼬리", "값": _format_pct(selected.get("d0_upper_shadow_pct"))},
            {"항목": "아랫꼬리", "값": _format_pct(selected.get("d0_lower_shadow_pct"))},
            {"항목": "60일 매물대 근사", "값": _pattern_lab_num(selected.get("d0_60d_value_above_close_share"), 3)},
            {"항목": "60일 누적거래대금", "값": _pattern_lab_num(selected.get("d0_60d_turnover_eok"), 1, "억")},
        ])
        st.dataframe(info_df, use_container_width=True, hide_index=True, height=340)
        st.markdown("#### 글로벌 as-of")
        global_df = pd.DataFrame([
            {"지표": "KOSPI", "변화": _format_pct(selected.get("kospi_change_pct_asof"))},
            {"지표": "KOSDAQ", "변화": _format_pct(selected.get("kosdaq_change_pct_asof"))},
            {"지표": "Nasdaq", "변화": _format_pct(selected.get("nasdaq_change_pct_asof"))},
            {"지표": "S&P500", "변화": _format_pct(selected.get("sp500_change_pct_asof"))},
            {"지표": "USD/KRW", "변화": _format_pct(selected.get("usdkrw_change_pct_asof"))},
            {"지표": "VIX", "변화": _format_pct(selected.get("vix_change_pct_asof"))},
        ])
        st.dataframe(global_df, use_container_width=True, hide_index=True, height=250)

    note_cols = st.columns([1.2, 1.0])
    with note_cols[0]:
        st.markdown(
            '<div class="cb-note" style="border-left-color:#64748b;">'
            '이 화면은 “다음날 완전 상승이 나온 D0”를 먼저 눈으로 보는 실험실입니다. '
            '나중에 메모가 쌓이면 사람이 좋다고 본 패턴과 실제 통계를 다시 교차검증할 수 있습니다.'
            '</div>',
            unsafe_allow_html=True,
        )
    with note_cols[1]:
        notes = read_csv(str(WHOLE_MARKET_PATTERN_NOTES_PATH))
        live_dict = {
            "stock_code": normalize_code(selected.get("code", "")),
            "stock_name": selected.get("name", ""),
            "rank": "",
            "role": "전날 패턴",
        }
        render_right_note_panel(WHOLE_MARKET_PATTERN_NOTES_PATH, str(selected.get("d0_date", "")), live_dict, notes)


# ============================================================
# 4탭 슬림 골격 (2026-05-16 reorg)
#   오늘 / 복기 / 연구실 / 메모
#
# 메인 표시: BellGuard 안정후보
# V2: 삭제하지 않고 기록/비교용으로 보존
# 현재일 후보에는 D+1~D+5 결과를 노출하지 않는다.
#
# 기존 12탭의 모든 render 함수는 그대로 재사용한다.
# 주문/계좌/yj_bot/실제 웹훅 발송 가드는 변경하지 않는다.
# ============================================================


def _resolve_hybrid_data_path(name: str) -> Path | None:
    """BellGuard / V2 record 데이터 위치 우선순위 검색.
    1) bell-dashboard repo data/online_v2/latest/
    2) C:/Users/PYJ/Downloads/  (Codex 직출 위치)
    """
    candidates = [
        ONLINE_V2_DIR / name,
        Path(r"C:\Users\PYJ\Downloads") / name,
    ]
    for p in candidates:
        try:
            if p.exists():
                return p
        except OSError:
            continue
    return None


def _resolve_main_dataset() -> tuple[Path, str, str]:
    """메인 1년치 복기 데이터셋 자동 선택.

    우선순위:
        1. eod_d0_active_watch_1y (EOD Active Watch + D1 15:00 +1.3 신호등)
        2. bellguard_d0_strict_1y (기록/비교용)
        3. bellguard_pricecap_1y (기록/비교용)
        4. bellguard_1y (legacy Mixed, COLOR_EDGE 섞임 - 수치 신뢰 X)

    Returns:
        (dataset_dir, file_prefix, display_label)
    """
    eod = EOD_ACTIVE_WATCH_1Y_DIR
    if eod.exists() and (eod / "eod_d0_active_watch_top3_latest.csv").exists():
        return eod, "eod_d0_active_watch", "Bell Watch EOD 1년치 (D1 15:00 +1.3%)"
    strict = ONLINE_V2_DIR / "bellguard_d0_strict_1y"
    if strict.exists() and (strict / "bellguard_d0_strict_top3_latest.csv").exists():
        return strict, "bellguard_d0_strict", "벨가드 안정후보 (D0 3일 풀 + 신호일 점수)"
    pc = ONLINE_V2_DIR / "bellguard_pricecap_1y"
    if pc.exists() and (pc / "bellguard_pricecap_top3_latest.csv").exists():
        return pc, "bellguard_pricecap", "벨가드 안정후보 (D0 Strict + 가격필터 100k)"
    bg = ONLINE_V2_DIR / "bellguard_1y"
    if bg.exists():
        return bg, "bellguard", "벨가드 안정후보 (legacy - 수치 검증 중)"
    return ONLINE_V2_DIR, "bellguard", "데이터 없음"


def _resolve_legacy_bellguard_dataset() -> tuple[Path, str, str]:
    """Bell Watch 이전 BellGuard 기록용 데이터셋 선택."""
    strict = ONLINE_V2_DIR / "bellguard_d0_strict_1y"
    if strict.exists() and (strict / "bellguard_d0_strict_top3_latest.csv").exists():
        return strict, "bellguard_d0_strict", "벨가드 안정후보 (D0 3일 풀 + 신호일 점수)"
    pc = ONLINE_V2_DIR / "bellguard_pricecap_1y"
    if pc.exists() and (pc / "bellguard_pricecap_top3_latest.csv").exists():
        return pc, "bellguard_pricecap", "벨가드 안정후보 (D0 Strict + 가격필터 100k)"
    bg = ONLINE_V2_DIR / "bellguard_1y"
    if bg.exists():
        return bg, "bellguard", "벨가드 안정후보 (legacy - 수치 검증 중)"
    return ONLINE_V2_DIR, "bellguard", "데이터 없음"


def _load_main_manifest_kpi() -> dict | None:
    """메인 데이터셋의 manifest.json + summary_1y.csv 에서 KPI 로드.

    새 manifest 구조(2026-05-18~)는 메타 정보(selection_policy, webhook_data_guard 등)만 담고
    summary_kpi/main_variant 키가 없다. KPI는 별도 `{prefix}_summary_1y.csv`(variant별 행)에 있다.
    manifest에 KPI가 없으면 그 CSV를 읽어 summary_kpi/main_variant를 채워 호환을 유지한다.
    """
    base, prefix, _ = _resolve_main_dataset()
    p = base / f"{prefix}_manifest.json"
    data: dict = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001
            data = {}
    if not data.get("summary_kpi"):
        summary_p = base / f"{prefix}_summary_1y.csv"
        if summary_p.exists():
            try:
                df = pd.read_csv(summary_p, encoding="utf-8-sig")
                if not df.empty:
                    if "variant" in df.columns:
                        data["summary_kpi"] = df.to_dict(orient="records")
                        variants = df["variant"].astype(str).tolist()
                        if not data.get("main_variant"):
                            data["main_variant"] = "100k" if "100k" in variants else variants[0]
                    else:
                        rec = df.iloc[0].to_dict()
                        rec["variant"] = "main"
                        data["summary_kpi"] = [rec]
                        data["main_variant"] = "main"
            except Exception:  # noqa: BLE001
                pass
    return data or None


_LIGHT_EMOJI = {"GREEN": "🟢", "YELLOW": "🟡", "ORANGE": "🟠", "RED": "🔴", "GRAY": "⚪"}
_LIGHT_ORDER = {"GREEN": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3, "GRAY": 4, "": 5}


def _format_signal_cell(light: str, raw_cell: str, name: str = "") -> str:
    """신호등 셀 표시: 🟢 종목명 형태로 통일."""
    if pd.isna(light) or not light:
        return raw_cell or "—"
    emoji = _LIGHT_EMOJI.get(str(light).upper(), "⚪")
    txt = name or raw_cell or ""
    if txt and "(" not in txt and "—" not in str(raw_cell):
        return f"{emoji} {txt}"
    if isinstance(raw_cell, str) and any(e in raw_cell for e in _LIGHT_EMOJI.values()):
        return raw_cell  # 이미 이모지 포함
    return f"{emoji} {raw_cell}" if raw_cell else emoji


def _extract_name_from_cell(cell: str) -> str:
    """'🟡 하나마이크론(067310)' → '하나마이크론(067310)'"""
    if pd.isna(cell) or not isinstance(cell, str):
        return ""
    for e in _LIGHT_EMOJI.values():
        cell = cell.replace(e, "").strip()
    return cell


def render_bellguard_signal_table() -> None:
    """벨가드 신호등표 — 날짜별 r1/r2/r3 + 정렬·필터 토글.

    데이터: bellguard_signal_by_date_1y.csv
    표시 컬럼: 날짜 / 1위 / 2위 / 3위 / 그날 판정
    """
    eod_p = EOD_ACTIVE_WATCH_PREVIEW_DIR / "webhook_top3_preview.csv"
    if eod_p.exists():
        try:
            eod = pd.read_csv(eod_p, encoding="utf-8-sig", dtype=str).fillna("")
            if not eod.empty:
                eod["rank_num"] = pd.to_numeric(
                    eod.get("webhook_rank", eod.get("rank_num", "")), errors="coerce"
                )
                eod = eod.sort_values(["signal_date", "rank_num", "stock_code"])
                latest_signal = str(eod["signal_date"].dropna().astype(str).max())
                latest = eod[eod["signal_date"].astype(str) == latest_signal].copy()

                def _fmt_price(v: Any) -> str:
                    try:
                        return f"{float(v):,.0f}원"
                    except (TypeError, ValueError):
                        return "—"

                def _fmt_pct(v: Any) -> str:
                    try:
                        return f"{float(v):+.1f}%"
                    except (TypeError, ValueError):
                        return "—"

                st.markdown("#### 🔔 Bell Watch — 최신 신호 (Top3)")
                st.caption(
                    "현재 운영 본진입니다. 장후 확정 D0 감시풀에서 오늘 15시 데이터만으로 고른 Top3입니다. "
                    "아래 기존 BellGuard 신호등표는 비교·기록용으로 접혀 있습니다."
                )
                eod_rows = []
                for _, row in latest.iterrows():
                    eod_rows.append({
                        "신호일": row.get("signal_date", "—"),
                        "순위": int(row.get("rank_num")) if pd.notna(row.get("rank_num")) else row.get("webhook_rank", "—"),
                        "종목": f"{row.get('stock_name', '')} ({row.get('stock_code', '')})",
                        "D0": row.get("d0_date", "—"),
                        "감시일차": f"D+{int(float(row.get('trading_day_age')))}" if str(row.get("trading_day_age", "")).strip() else "—",
                        "15시가": _fmt_price(row.get("entry_1500_price")),
                        "신호일 등락": _fmt_pct(row.get("signal_day_pct_change_1500")),
                        "D0종가대비": _fmt_pct(row.get("signal_vs_d0_close_pct")),
                        "D0고가대비": _fmt_pct(row.get("signal_vs_d0_high_pct")),
                        "RSI": f"{float(row.get('rsi14_signal_1500')):.0f}" if str(row.get("rsi14_signal_1500", "")).strip() else "—",
                        "상태": row.get("badge_text", "paper watch"),
                    })
                st.dataframe(pd.DataFrame(eod_rows), use_container_width=True, hide_index=True, height=150)

                # ───── Bell Watch 신호등표 (EOD +1.3 / D1 15:00) ─────
                st.markdown("##### 🚦 Bell Watch EOD 신호등표 — D1 15:00 +1.3%")
                eod_1y = load_eod_active_watch_1y_csv("eod_d0_active_watch_signal_by_date_1y.csv")
                eod_1y_manifest = load_eod_active_watch_1y_manifest()
                if not eod_1y.empty:
                    show_cols = [
                        c
                        for c in [
                            "signal_date",
                            "1위",
                            "2위",
                            "3위",
                            "plus_touch_count",
                            "profit_before_minus2_count",
                            "red_count",
                            "traffic_preference_bucket",
                        ]
                        if c in eod_1y.columns
                    ]
                    by_date = eod_1y[show_cols].copy().head(60)
                    latest_label_date = by_date["signal_date"].iloc[0] if not by_date.empty else "—"
                    st.caption(
                        "기준: EOD_D0_BASE_VALUE_TOP3 / watch_days=10 / D1 15:00까지 +1.3% 도달. "
                        "🟢 +1.3 도달·-2% 없음 · 🟡 +1.3 먼저 후 변동 · 🟠 -2% 먼저 후 회복 · "
                        "🔴 +1.3 기회 없음/빠른 실패 · ⚪ 평가 보류. "
                        f"확정 구간: {eod_1y_manifest.get('date_min', '—')}~{eod_1y_manifest.get('date_max', '—')} · "
                        f"마지막 라벨 신호일: **{latest_label_date}**"
                    )
                    st.dataframe(by_date, use_container_width=True, hide_index=True, height=360)
                else:
                    pw_log = load_eod_paper_watch_log()
                    if pw_log.empty:
                        st.info("EOD +1.3 신호등 데이터가 없습니다. export_eod_1p3_dashboard_backdata 스크립트 실행이 필요합니다.")
                    else:
                        df_p = pw_log.copy()
                        df_p["rank_n"] = pd.to_numeric(df_p["rank"], errors="coerce")
                        df_p = df_p.dropna(subset=["rank_n"])
                        df_p["rank_n"] = df_p["rank_n"].astype(int)
                        df_p["sd"] = df_p["signal_date"].astype(str).str[:10]
                        df_p["cell"] = df_p.apply(
                            lambda r: f"{_d1_label_to_light(r.get('d1_label', ''))} {r.get('stock_name', '')}({r.get('stock_code', '')})",
                            axis=1,
                        )
                        by_date = (
                            df_p.pivot_table(
                                index="sd",
                                columns="rank_n",
                                values="cell",
                                aggfunc="first",
                            )
                            .sort_index(ascending=False)
                            .head(60)
                        )
                        by_date.columns = [f"{int(c)}위" for c in by_date.columns]
                        by_date.index.name = "signal_date"
                        by_date = by_date.reset_index()
                        st.caption("임시 fallback: 기존 paper_watch_log 라벨입니다. +1.3 전용 EOD 신호등 산출물이 없을 때만 표시됩니다.")
                        st.dataframe(by_date, use_container_width=True, hide_index=True, height=360)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Bell Watch 최신 신호 로드 실패: {exc}")

    # ───── 기존 BellGuard 표는 expander로 접어둠 (비교·기록용) ─────
    with st.expander("📁 기존 BellGuard 기록 신호등 (비교·기록용 · 본진 아님)", expanded=False):
        st.caption("Bell Watch 본진 전환 이전 BellGuard 안정후보 신호등표입니다. 운영 후보 선정에는 반영되지 않습니다.")
        _render_legacy_bellguard_signal_table_body()


def _render_legacy_bellguard_signal_table_body() -> None:
    """기존 BellGuard 신호등표 본체 — expander 안에서 호출."""
    ds_dir, prefix, ds_label = _resolve_legacy_bellguard_dataset()
    base_p = ds_dir / f"{prefix}_signal_by_date_1y.csv"
    if not base_p.exists():
        base_p = _resolve_hybrid_data_path("bellguard_1y/bellguard_signal_by_date_1y.csv")
    if base_p is None or not base_p.exists():
        st.warning("BellGuard 신호등 데이터가 없습니다.")
        return
    st.caption(f"데이터셋: {ds_label}")
    try:
        df = pd.read_csv(base_p, encoding="utf-8-sig")
    except Exception as exc:  # noqa: BLE001
        st.error(f"신호등 데이터 로드 실패: {exc}")
        return

    # 컨트롤 행
    ctrl = st.columns([1.3, 1.3, 1.3, 2.0])
    with ctrl[0]:
        order = st.selectbox("정렬", ["최신순", "과거순"], index=0, key="sig_order")
    with ctrl[1]:
        rank_filter = st.selectbox("순위 필터", ["전체", "1위만", "2위만", "3위만"], index=0, key="sig_rank")
    with ctrl[2]:
        light_filter = st.selectbox(
            "신호등 필터", ["전체", "🟢 강세", "🟡 회복", "🟠 실패", "🔴 약세"],
            index=0, key="sig_light",
        )
    with ctrl[3]:
        search = st.text_input("종목 검색 (이름·코드)", "", key="sig_search").strip()

    # 정렬
    df["d0_date"] = df["d0_date"].astype(str)
    df = df.sort_values("d0_date", ascending=(order == "과거순"))

    # 신호등 필터 — 어느 슬롯이라도 매치되면 해당 행 보임
    if light_filter != "전체":
        target = {"🟢 강세": "GREEN", "🟡 회복": "YELLOW", "🟠 실패": "ORANGE", "🔴 약세": "RED"}[light_filter]
        light_cols = ["bellguard_r1_light", "bellguard_r2_light", "bellguard_r3_light"]
        mask = pd.Series(False, index=df.index)
        for c in light_cols:
            if c in df.columns:
                mask = mask | (df[c].astype(str).str.upper() == target)
        df = df[mask]

    # 검색 — 셀 텍스트에 포함
    if search:
        cell_cols = ["bellguard_r1_cell", "bellguard_r2_cell", "bellguard_r3_cell"]
        mask = pd.Series(False, index=df.index)
        for c in cell_cols:
            if c in df.columns:
                mask = mask | df[c].astype(str).str.contains(search, case=False, na=False)
        df = df[mask]

    st.caption(
        "각 셀의 색은 그 신호일의 **다음 거래일(D+1) 결과**로 사후 판단합니다 — "
        "🟢 강세 / 🟡 회복 / 🟠 실패 / 🔴 약세 / ⚪ 보합·결과 미발생."
    )
    # 표시용 — 컬럼 4개만
    show_rows = []
    for _, r in df.iterrows():
        row = {
            "날짜": r.get("d0_date", "—"),
            "1위": r.get("bellguard_r1_cell", "—"),
            "2위": r.get("bellguard_r2_cell", "—"),
            "3위": r.get("bellguard_r3_cell", "—"),
            "그날 판정": r.get("date_verdict", "—"),
        }
        # 순위 필터
        if rank_filter == "1위만":
            row.pop("2위"); row.pop("3위")
        elif rank_filter == "2위만":
            row.pop("1위"); row.pop("3위")
        elif rank_filter == "3위만":
            row.pop("1위"); row.pop("2위")
        show_rows.append(row)

    show_df = pd.DataFrame(show_rows)
    st.caption(f"표시 중 {len(show_df):,}일 · 정렬: {order} · 클릭은 다음 단계에서 종목상세 연결 예정")
    st.dataframe(show_df, use_container_width=True, hide_index=True, height=560)


# 종목상세 메모 영구 저장 위치
SECURITY_DETAIL_NOTES_PATH = CLOSINGBELL / "user_notes" / "security_detail_notes.csv"
PAPER_WATCH_NOTES_PATH = CLOSINGBELL / "user_notes" / "paper_watch_user_notes.csv"


def _save_security_detail_memo(code: str, date: str, key_base: str) -> None:
    """버튼 클릭 시 세션 메모 4종을 CSV로 영구 저장 (append, 동일 키 update)."""
    save_clicked = st.button("💾 메모 영구 저장", key=f"{key_base}_save_btn", use_container_width=False)
    if not save_clicked:
        return
    fields = {
        "pre": st.session_state.get(f"{key_base}_pre", ""),
        "pattern": st.session_state.get(f"{key_base}_pattern", ""),
        "post": st.session_state.get(f"{key_base}_post", ""),
        "miss": st.session_state.get(f"{key_base}_miss", ""),
        "rule": st.session_state.get(f"{key_base}_rule", ""),
        "interval": st.session_state.get(f"{key_base}_interval_30default", ""),
        "entry_guess": st.session_state.get(f"{key_base}_entry_guess", ""),
    }
    # 모두 비어있으면 skip
    if not any(str(v).strip() for v in fields.values()):
        st.warning("저장할 메모 내용이 없습니다.")
        return
    record = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "code": code,
        "d0_date": date,
        "pre_feeling": fields["pre"],
        "pattern_memo": fields["pattern"],
        "post_thought": fields["post"],
        "missed_or_next": fields["miss"],
        "observed_rule": fields["rule"],
        "observed_interval": fields["interval"],
        "entry_price_guess": fields["entry_guess"],
    }
    p = SECURITY_DETAIL_NOTES_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        if p.exists():
            existing = pd.read_csv(p, encoding="utf-8-sig", dtype=str).fillna("")
            # 같은 (code, d0_date) 행 있으면 update, 없으면 append
            mask = (existing["code"] == code) & (existing["d0_date"] == date)
            if mask.any():
                for k, v in record.items():
                    existing.loc[mask, k] = str(v)
                merged = existing
            else:
                merged = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
        else:
            merged = pd.DataFrame([record])
        merged.to_csv(p, index=False, encoding="utf-8-sig")
        st.success(f"메모 저장 완료: {p.name}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"메모 저장 실패: {exc}")


def _signed_qty(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        return f"{int(round(float(value))):+,}"
    except (TypeError, ValueError):
        return "—"


def _count_trailing_negative(values: list[float]) -> int:
    count = 0
    for value in reversed(values):
        if value < 0:
            count += 1
        else:
            break
    return count


def _security_detail_supply_line(code: str, signal_date: str) -> str:
    """종목상세 상단에 표시할 장후 수급 요약. 웹훅 점수에는 사용하지 않는다."""
    inst = load_inst_trade(code)
    if inst.empty or not signal_date:
        return ""
    sig = pd.to_datetime(signal_date, errors="coerce")
    if pd.isna(sig):
        return ""
    recent = inst[inst["date"].le(sig)].sort_values("date").tail(10).copy()
    if recent.empty:
        return ""
    foreign = pd.to_numeric(recent.get("for_daly_nettrde_qty"), errors="coerce").dropna()
    institution = pd.to_numeric(recent.get("orgn_daly_nettrde_qty"), errors="coerce").dropna()
    if foreign.empty and institution.empty:
        return ""
    parts = []
    if not foreign.empty:
        f_values = foreign.astype(float).tolist()
        parts.append(
            f"외인 10일 합계 {_signed_qty(sum(f_values))}주"
            f" · 매도일 {sum(1 for v in f_values if v < 0)}/{len(f_values)}"
            f" · 연속매도 {_count_trailing_negative(f_values)}일"
        )
    if not institution.empty:
        i_values = institution.astype(float).tolist()
        parts.append(
            f"기관 10일 합계 {_signed_qty(sum(i_values))}주"
            f" · 매도일 {sum(1 for v in i_values if v < 0)}/{len(i_values)}"
            f" · 연속매도 {_count_trailing_negative(i_values)}일"
        )
    latest = str(recent["date"].max().date())
    return " / ".join(parts) + f" · 최신 {latest} 장후 확정치(웹훅 점수 미사용)"


def render_security_detail() -> None:
    """종목 상세 — 차트 + 기업정보 + 메모 (1차 골격).

    심화 작업(이평선·분봉 5/15/30분·수급·DART)은 다음 세션에서 확장.
    """
    st.markdown(
        '<div class="cb-note" style="border-left-color:#0ea5e9;">'
        '<b>종목 상세 (1차 골격)</b> — 종목 선택 후 차트와 정보, 메모를 한 화면에서 봅니다. '
        '심화된 일봉/분봉 차트·수급·DART 정보는 다음 단계에서 확장합니다.'
        '</div>',
        unsafe_allow_html=True,
    )
    ds_dir, prefix, ds_label = _resolve_main_dataset()
    case_frames: list[pd.DataFrame] = []

    # 최신 운영 후보는 Bell Watch preview를 우선 병합한다.
    # paper/review 결과가 아직 없는 당일도 종목 상세에서 바로 차트 공부할 수 있어야 한다.
    eod_p = EOD_ACTIVE_WATCH_PREVIEW_DIR / "webhook_top3_preview.csv"
    if eod_p.exists():
        try:
            eod_cases = pd.read_csv(eod_p, encoding="utf-8-sig", dtype=str).fillna("")
            if not eod_cases.empty:
                eod_cases = eod_cases.copy()
                eod_cases["code"] = eod_cases.get("stock_code", "")
                eod_cases["name"] = eod_cases.get("stock_name", "")
                eod_cases["rank"] = eod_cases.get("webhook_rank", "")
                eod_cases["bellguard_score"] = eod_cases.get("daily3_active_score", "")
                eod_cases["source_score"] = eod_cases.get("daily3_active_score", "")
                eod_cases["entry_price_1500"] = eod_cases.get("entry_1500_price", "")
                eod_cases["entry_price_used"] = eod_cases.get("entry_1500_price", "")
                eod_cases["signal_rsi14_1500"] = eod_cases.get("rsi14_signal_1500", "")
                eod_cases["bellguard_reason_auto"] = eod_cases.get("badge_text", "")
                eod_cases["traffic_light"] = "GRAY"
                eod_cases["bellguard_live_light"] = "GRAY"
                if "signal_trading_value_to_1500_eok" not in eod_cases.columns:
                    price = pd.to_numeric(eod_cases.get("entry_1500_price", ""), errors="coerce")
                    volume = pd.to_numeric(eod_cases.get("signal_volume_to_1500", ""), errors="coerce")
                    eod_cases["signal_trading_value_to_1500_eok"] = ((price * volume) / 100_000_000).round(1)
                case_frames.append(eod_cases)
        except Exception as exc:  # noqa: BLE001
            st.caption(f"최신 Bell Watch 후보 병합 실패: {exc}")

    # 1년 복기용 기록 데이터는 보조로 병합한다.
    base_p = ds_dir / f"{prefix}_signal_rows_1y.csv"
    if not base_p.exists():
        base_p = ds_dir / f"{prefix}_chart_review_cases_1y.csv"
    if not base_p.exists():
        base_p = _resolve_hybrid_data_path("bellguard_1y/bellguard_chart_review_cases_1y.csv")
    if base_p is not None and base_p.exists():
        try:
            case_frames.append(pd.read_csv(base_p, encoding="utf-8-sig").fillna(""))
        except Exception as exc:  # noqa: BLE001
            st.error(f"케이스 로드 실패: {exc}")
            return

    if not case_frames:
        st.info("종목 상세 데이터가 없습니다.")
        return

    cases = pd.concat(case_frames, ignore_index=True, sort=False).fillna("")
    if {"signal_date", "code"}.issubset(cases.columns):
        cases["signal_date"] = cases["signal_date"].astype(str).str[:10]
        cases["code"] = cases["code"].map(normalize_code)
        cases = cases.drop_duplicates(subset=["signal_date", "code"], keep="first")
    st.caption(f"데이터셋: 최신 Bell Watch + {ds_label}")
    # 신호일 필터는 signal_date(웹훅 발송일) 기준. 3일 active pool이라
    # d0_date(실제 D0 등장일)와 signal_date가 다를 수 있어, 신호등표와
    # 일관되게 보이려면 signal_date를 써야 한다 (2026-05-18 버그 수정).
    filter_col = "signal_date" if "signal_date" in cases.columns else "d0_date"
    if filter_col in cases.columns:
        cases[filter_col] = cases[filter_col].astype(str).str[:10]
        cases = cases.sort_values(filter_col, ascending=False)

    # 선택 UI — 신호일 달력 위젯(거래일만 valid, 가장 가까운 거래일로 fallback)
    valid_dates = sorted(cases.get(filter_col, pd.Series(dtype=str)).unique().tolist())
    if not valid_dates:
        st.info("선택 가능한 신호일이 없습니다.")
        return
    valid_date_objs = sorted({pd.to_datetime(d).date() for d in valid_dates})
    min_d, max_d = valid_date_objs[0], valid_date_objs[-1]
    latest_seen_key = "sd_date_calendar_latest_seen"
    calendar_key = "sd_date_calendar"
    latest_iso = max_d.isoformat()
    if st.session_state.get(latest_seen_key) != latest_iso:
        st.session_state[calendar_key] = max_d
        st.session_state[latest_seen_key] = latest_iso
    sel_cols = st.columns([2, 2])
    with sel_cols[0]:
        # 달력 위젯 (Streamlit 한계: 거래일만 비활성화 못 함 → 가장 가까운 거래일로 snap)
        calendar_kwargs = {
            "label": "신호일 (달력)",
            "min_value": min_d,
            "max_value": max_d,
            "key": calendar_key,
            "help": "신호등표의 그 날(웹훅 발송일) 기준. D0 등장일은 종목별로 다를 수 있습니다 (3일 감시풀).",
        }
        if calendar_key not in st.session_state:
            calendar_kwargs["value"] = max_d
        picked = st.date_input(**calendar_kwargs)
        if picked not in set(valid_date_objs):
            picked = max((d for d in valid_date_objs if d <= picked), default=valid_date_objs[0])
            st.caption(f"⤷ 가장 가까운 거래일로 조정: **{picked}**")
        sel_date = picked.isoformat()
    with sel_cols[1]:
        day = cases[cases[filter_col] == sel_date]
        name_col = "name" if "name" in day.columns else (
            "stock_label" if "stock_label" in day.columns else None
        )
        if name_col:
            stock_opts = day[name_col].astype(str).unique().tolist()
            sel_stock = st.selectbox("종목", stock_opts, key="sd_stock") if stock_opts else None
        else:
            sel_stock = None
    # 결과 표시 — 체크박스 제거 후 상시 표시 (사용자 2026-05-18 피드백)
    show_result = True

    if not sel_stock:
        st.info("종목을 선택하면 상세가 표시됩니다.")
        return

    row = day[day[name_col].astype(str) == sel_stock]
    if row.empty:
        st.info("선택한 케이스를 찾을 수 없습니다.")
        return
    r = row.iloc[0]

    code = str(r.get("code", ""))
    # 차트·분봉·D0 마커·D+N·기준가·메모 모두 신호일(웹훅 발송일) 기준으로 통일
    # — 사용자 2026-05-18 피드백 ("d0 감시 기준이 아닌 웹훅 날짜 기준")
    # 실제 D0 등장일(d0_date)은 헤더 캡션에 별도 표기 (감시 D+N).
    date = str(r.get("signal_date", ""))[:10] or str(r.get("d0_date", ""))[:10]
    key_base = f"sd_memo_{code}_{date}"

    # 운영 모델 + 학습 영역 안내 (Codex 핸드오프 2026-05-21 §10 필수 문구)
    st.markdown(
        '<div style="background:#f8fafc; border-left:3px solid #475569; padding:7px 12px; '
        'border-radius:4px; margin:0 0 10px; font-size:0.84rem; color:#334155;">'
        '<b>운영 모델</b>: <code>EOD_D0_BASE_VALUE_TOP3 / watch_days=10</code> · '
        '아래 카드 중 Scorebook · Deep Pattern · Paper Watch · 학습 배지는 '
        '<b>학습 참고용</b>이며 운영 후보 선정에는 반영되지 않습니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    # 상단 카드: 기본 정보 — "D0" 라벨을 "신호일" 로 변경
    head = st.columns([2, 2, 2, 2])
    with head[0]:
        st.markdown(f"### 🛡 {r.get('name', '—')}")
        st.caption(f"{r.get('code', '—')} · {r.get('market', '—')}")
    with head[1]:
        result_light = str(r.get("traffic_light") or "").upper()
        live_light = str(r.get("bellguard_live_light") or "").upper()
        light = result_light or live_light
        emoji = _LIGHT_EMOJI.get(light, "⚪")
        if result_light and result_light != "GRAY":
            st.metric("결과 신호등", f"{emoji} {result_light}")
            if live_light and live_light != result_light:
                live_emoji = _LIGHT_EMOJI.get(live_light, "⚪")
                st.caption(f"선정 당시 상태: {live_emoji} {live_light}")
        elif light in ("", "GRAY"):
            st.metric("결과 신호등", f"{emoji} 결과 미발생")
            st.caption("D+1 결과가 나와야 색이 정해집니다.")
        else:
            st.metric("선정 상태", f"{emoji} {light}")
            st.caption("아직 결과 신호등이 확정되지 않은 현재/미래 케이스입니다.")
    with head[2]:
        score = r.get("bellguard_score") or r.get("source_score")
        try:
            sv = float(score)
            if 0 <= sv <= 1.0001:
                sv *= 100
            st.metric("BellGuard 점수", f"{sv:.1f}")
        except (TypeError, ValueError):
            st.metric("BellGuard 점수", "—")
    with head[3]:
        sig_d = str(r.get("signal_date", ""))[:10] or "—"
        d0_d = str(r.get("d0_date", ""))[:10] or "—"
        st.metric("신호일 (웹훅)", sig_d)
        if d0_d != "—" and d0_d != sig_d:
            try:
                age_days = (pd.to_datetime(sig_d).date() - pd.to_datetime(d0_d).date()).days
                st.caption(f"감시 등록일: {d0_d} (감시 D+{age_days})")
            except Exception:  # noqa: BLE001
                st.caption(f"감시 등록일: {d0_d}")
        elif d0_d != "—":
            st.caption(f"감시 등록일: {d0_d} (당일)")

    # ──────── 카드 A · 후보 기준 (Codex 핸드오프 2026-05-21 §5.A) ────────
    # 모델·감시 구조·날짜 분리 검증 한 줄. 미래시 의심 차단용.
    age_int = None
    try:
        age_int = int(r.get("trading_day_age")) if pd.notna(r.get("trading_day_age")) else None
    except (TypeError, ValueError):
        age_int = None
    model_id = str(r.get("selection_model") or r.get("model_id") or "EOD_D0_BASE_VALUE_TOP3")
    source_layer = str(r.get("source_layer") or "ACTIVE_WATCHLIST")
    watch_days_val = r.get("watch_days") or 10
    d0_lt_signal = "✅" if (d0_d != "—" and sig_d != "—" and d0_d < sig_d) else (
        "≡ 당일" if d0_d == sig_d else "⚠️"
    )
    st.markdown(
        '<div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; '
        'padding:8px 12px; margin:0 0 8px; font-size:0.84rem; color:#0c4a6e;">'
        '<b>후보 기준</b> · '
        f'모델 <code>{model_id}</code> · '
        f'source <code>{source_layer}</code> · watch_days {watch_days_val} · '
        '정렬 D0 거래대금 내림차순<br>'
        f'이 후보: <b>d0_date</b> {d0_d} → <b>signal_date</b> {sig_d} '
        f'(감시 D+{age_int if age_int is not None else "—"}) · '
        f'd0 &lt; signal {d0_lt_signal} · '
        '15시 feature는 상태/위험 확인용 (선정 점수 미포함)'
        '</div>',
        unsafe_allow_html=True,
    )

    # ──────── 신호일 15시 변수 + 위험 배지 일괄 계산 (카드 B/C, B2 띠에서 공용) ────────
    try:
        _ep_raw = r.get("entry_price_used") or r.get("entry_price_1500") or r.get("entry_price_hint") or r.get("d0_close")
        _ep_val = float(_ep_raw) if pd.notna(_ep_raw) else None
    except (TypeError, ValueError):
        _ep_val = None
    _sig_d = str(r.get("signal_date", ""))[:10]
    _sig_pct = r.get("signal_day_pct_change_1500")
    if pd.isna(_sig_pct) or str(_sig_pct).strip() == "":
        _sig_pct = compute_signal_day_pct_change(code, _sig_d, _ep_val) if _sig_d else None
    _signal_value_eok = r.get("signal_trading_value_to_1500_eok")
    _vs_d0_close = r.get("signal_vs_d0_close_pct")
    _vs_d0_high = r.get("signal_vs_d0_high_pct")
    _retention = r.get("signal_volume_retention_vs_d0")
    _rsi = r.get("signal_rsi14_1500")
    if pd.isna(_rsi) or str(_rsi).strip() == "":
        _rsi = compute_rsi14(code, _sig_d) if _sig_d else None
    # retention: dataset에 따라 0~1 또는 0~100 — 자동 감지
    _ret_pct: float | None = None
    try:
        if pd.notna(_retention) and str(_retention).strip() != "":
            _rv = float(_retention)
            _ret_pct = _rv * 100 if _rv <= 1.5 else _rv
    except (TypeError, ValueError):
        _ret_pct = None

    # 위험 배지 계산 (red = #fee2e2/#991b1b, orange = #ffedd5/#9a3412)
    risk_bits: list[tuple[str, str, str]] = []
    try:
        if pd.notna(_vs_d0_high) and float(_vs_d0_high) <= -20:
            risk_bits.append(("D0고가 -20%↓", "#fee2e2", "#991b1b"))
    except (TypeError, ValueError):
        pass
    try:
        if pd.notna(_vs_d0_close) and float(_vs_d0_close) <= -10:
            risk_bits.append(("D0종가 -10%↓", "#fee2e2", "#991b1b"))
    except (TypeError, ValueError):
        pass
    try:
        if pd.notna(_sig_pct) and float(_sig_pct) <= -7:
            risk_bits.append(("신호일 약세", "#fee2e2", "#991b1b"))
    except (TypeError, ValueError):
        pass
    if _ret_pct is not None and _ret_pct < 10:
        risk_bits.append(("거래량 약화", "#ffedd5", "#9a3412"))
    try:
        if pd.notna(_rsi):
            rsi_v = float(_rsi)
            if rsi_v >= 75:
                risk_bits.append(("RSI 과열", "#fee2e2", "#991b1b"))
            elif rsi_v >= 70:
                risk_bits.append(("RSI 과매수", "#ffedd5", "#9a3412"))
            elif rsi_v <= 30:
                risk_bits.append(("RSI 과매도", "#ffedd5", "#9a3412"))
    except (TypeError, ValueError):
        pass
    if age_int is not None and age_int >= 8:
        risk_bits.append(("오래된 D0", "#ffedd5", "#9a3412"))

    # ──────── B2: 최상단 위험 배지 띠 (한눈에 위험 프로파일) ────────
    has_red = any(bg == "#fee2e2" for _, bg, _ in risk_bits)
    if risk_bits:
        pills_top = "".join(
            f'<span style="background:{bg}; color:{fg}; padding:3px 10px; '
            f'border-radius:999px; font-size:0.80rem; font-weight:600; margin-right:6px;">{lbl}</span>'
            for lbl, bg, fg in risk_bits
        )
        prefix = "🚨 위험" if has_red else "⚠ 주의"
        st.markdown(
            f'<div style="margin:4px 0 10px; padding:6px 10px; background:#fafafa; '
            f'border-left:3px solid {"#dc2626" if has_red else "#f59e0b"}; '
            f'border-radius:4px; font-size:0.84rem;">'
            f'<b style="color:{"#991b1b" if has_red else "#9a3412"}; margin-right:8px;">{prefix}</b>'
            f'{pills_top}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="margin:4px 0 10px; padding:6px 10px; background:#f0fdf4; '
            'border-left:3px solid #16a34a; border-radius:4px; font-size:0.84rem;">'
            '<b style="color:#166534;">✅ 위험 배지 없음</b> '
            '<span style="color:#475569; margin-left:6px;">— D0 대비 큰 이탈 없음 · RSI 중립 구간</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ──────── 카드 B · D0 이벤트 (왜 감시풀에 들어왔는가) ────────
    st.markdown("##### 🔥 D0 이벤트 — 감시풀 등록 사유")
    d0_value_eok = r.get("d0_trading_value_proxy_eok") or r.get("d0_trading_value_eok")
    d0_pct = r.get("d0_pct_change") or r.get("d0_ret_pct")
    d0_vol_20d = r.get("d0_volume_vs_20d") or r.get("volume_ratio_vs_20d")
    d0_upper = r.get("d0_upper_shadow_ratio") or r.get("upper_shadow_ratio")
    d0_range = r.get("d0_range_pct")
    d0_value_rank = r.get("d0_value_rank")
    d0b = st.columns(3)
    d0b[0].metric("D0 거래대금", fmt_eok_to_human(d0_value_eok))
    try:
        d0b[1].metric("D0 등락률", f"{float(d0_pct):+.1f}%" if pd.notna(d0_pct) else "—")
    except (TypeError, ValueError):
        d0b[1].metric("D0 등락률", "—")
    try:
        d0b[2].metric("거래량 vs 20일", f"{float(d0_vol_20d):.1f}배" if pd.notna(d0_vol_20d) else "—")
    except (TypeError, ValueError):
        d0b[2].metric("거래량 vs 20일", "—")
    # 보조 정보 한 줄 — 윗꼬리/range/거래대금 순위
    sub_bits = []
    try:
        if pd.notna(d0_upper):
            sub_bits.append(f"윗꼬리 {float(d0_upper) * 100:.0f}%")
    except (TypeError, ValueError):
        pass
    try:
        if pd.notna(d0_range):
            sub_bits.append(f"range {float(d0_range):.1f}%")
    except (TypeError, ValueError):
        pass
    try:
        if pd.notna(d0_value_rank):
            sub_bits.append(f"거래대금 순위 {int(float(d0_value_rank))}위")
    except (TypeError, ValueError):
        pass

    # B1 적용: "근거/체크/장후수급" 평문 3줄 → 카드 B의 캡션으로 흡수
    reason = str(
        r.get("bellguard_reason_auto") or r.get("bellguard_reason")
        or r.get("traffic_reason") or ""
    ).strip()
    if not reason or reason.lower() == "nan":
        bits = []
        d0v = r.get("d0_pct_change") or r.get("d0_ret_pct")
        if pd.notna(d0v):
            try:
                bits.append(f"감시 등록일 {float(d0v):+.1f}%")
            except (TypeError, ValueError):
                pass
        vr = r.get("volume_ratio_vs_20d")
        if pd.notna(vr):
            try:
                bits.append(f"거래량 20일대비 {float(vr):.1f}배")
            except (TypeError, ValueError):
                pass
        reason = " / ".join(bits) if bits else ""
    reason_kr = (
        reason.replace("D0+", "감시 D+")
              .replace("D0 +", "감시 등록일 +")
              .replace("D0 -", "감시 등록일 -")
    )
    # 1줄째 캡션: 윗꼬리/range/순위 + 근거 텍스트
    cap_line1_bits = list(sub_bits)
    if reason_kr and reason_kr != "—":
        cap_line1_bits.append(f"근거 {reason_kr}")
    if cap_line1_bits:
        st.caption(" · ".join(cap_line1_bits))
    # 2줄째 캡션: 체크 포인트 + 장후 수급
    cap_line2 = "체크: 15시 가격 지지 · VWAP/전고점 반응 · 거래량 유지"
    supply_line = _security_detail_supply_line(code, date)
    if supply_line:
        cap_line2 += f"  │  장후 {supply_line}"
    st.caption(cap_line2)

    # ──────── 카드 C · 신호일 15시 상태 (Codex 핸드오프 2026-05-21 §5.C) ────────
    # 변수와 risk_bits는 카드 A 직후 블록에서 이미 계산됨 (B2 위험 배지 띠와 공용)
    st.markdown("##### 📍 신호일 15시 상태")

    # 컬럼 비율 조정 — RSI는 좁게, 거래대금은 넓게 (조 단위 표시 시 잘림 방지)
    sig_cols = st.columns([1.0, 1.0, 1.0, 1.0, 0.8, 1.3])
    sig_cols[0].metric("15시 등락률", fmt_pct(_sig_pct))
    sig_cols[1].metric("vs D0 종가", fmt_pct(_vs_d0_close))
    sig_cols[2].metric("vs D0 고가", fmt_pct(_vs_d0_high))
    sig_cols[3].metric("거래량 유지", f"{_ret_pct:.1f}%" if _ret_pct is not None else "—")
    try:
        sig_cols[4].metric("RSI", f"{float(_rsi):.1f}" if pd.notna(_rsi) else "—")
    except (TypeError, ValueError):
        sig_cols[4].metric("RSI", "—")
    sig_cols[5].metric("15시 거래대금", fmt_eok_to_human(_signal_value_eok))

    # 카드 C 안의 위험 배지 pill — 위에서 계산된 risk_bits 재사용 (상단 띠와 같은 정보, 자세히 보는 용도)
    if risk_bits:
        pills = "".join(
            f'<span style="background:{bg}; color:{fg}; padding:2px 9px; '
            f'border-radius:999px; font-size:0.78rem; font-weight:600; margin-right:5px;">{lbl}</span>'
            for lbl, bg, fg in risk_bits
        )
        st.markdown(f'<div style="margin:6px 0 0;">{pills}</div>', unsafe_allow_html=True)
    st.caption("배지는 학습용·주의용이며 운영 컷이 아닙니다.")

    # ──────── 카드 D · D+1 / D+5 결과 (paper_watch_log join) ────────
    st.markdown("##### 🏁 D+1 / H5 결과")
    try:
        pw_log = load_eod_paper_watch_log()
        if pw_log.empty or not _sig_d:
            pw_row = pd.DataFrame()
        else:
            pw_row = pw_log[
                (pw_log["signal_date"].astype(str).str[:10] == _sig_d)
                & (pw_log["stock_code"].astype(str).str.zfill(6) == str(code).zfill(6))
            ]
    except Exception:  # noqa: BLE001
        pw_row = pd.DataFrame()
    if pw_row.empty:
        st.info("Paper Watch 로그에 매칭되는 행 없음 (신호일 미수집 또는 후보 비대상).")
    else:
        pwr = pw_row.iloc[0].to_dict()
        pw_status = str(pwr.get("paper_watch_status", ""))
        is_pending = pw_status.startswith("pending")
        if is_pending:
            st.info("📅 D+1·H5 결과 미확정 — paper watch 대기 (신호일이 오늘이거나 D+1 영업일 미경과)")
        d_cols = st.columns([1.2, 1.2, 1.8])
        with d_cols[0]:
            st.caption("D+1 라벨")
            st.markdown(_paper_watch_label_pill(str(pwr.get("d1_label", "D1_PENDING"))), unsafe_allow_html=True)
            try:
                d1_ret = pwr.get("d1_close_return_pct")
                if pd.notna(d1_ret) and str(d1_ret).strip():
                    st.caption(f"D+1 종가 {float(d1_ret):+.2f}%")
            except (TypeError, ValueError):
                pass
        with d_cols[1]:
            st.caption("H5 라벨")
            st.markdown(_paper_watch_label_pill(str(pwr.get("h5_label", "H5_PENDING"))), unsafe_allow_html=True)
            try:
                h5_mfe = pwr.get("h5_mfe")
                h5_mae = pwr.get("h5_mae")
                parts_h5 = []
                if pd.notna(h5_mfe):
                    parts_h5.append(f"MFE {float(h5_mfe):+.1f}%")
                if pd.notna(h5_mae):
                    parts_h5.append(f"MAE {float(h5_mae):+.1f}%")
                if parts_h5:
                    st.caption(" / ".join(parts_h5))
            except (TypeError, ValueError):
                pass
        with d_cols[2]:
            st.caption("해석 태그 (retro_tags)")
            retro = str(pwr.get("retro_tags", "")).strip()
            if retro and retro.lower() != "nan":
                st.markdown(
                    f'<div style="font-size:0.82rem; color:#475569; line-height:1.5;">'
                    f'{retro.replace("|", " · ")}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("—")
        st.caption("D+1·H5 결과는 사후 평가·해석 메모용. 후보 선정 점수에 반영 금지 (미래시 방지).")

    # ──────── ① 차트·수급·재무 (위로 이동, 사용자 피드백 반영) ────────
    st.markdown("---")
    st.markdown("### 차트 · 수급 · 재무")
    if IS_ONLINE_MODE:
        st.info(
            "🌐 온라인 모드 — 로컬 raw 데이터(일봉·분봉·수급·DART parquet/json)에 의존하는 화면입니다. "
            "온라인 배포본은 경량 데이터셋만 포함되어 차트가 표시되지 않을 수 있습니다. "
            "정밀 복기는 로컬에서 띄워 주세요."
        )
    entry_price = None
    try:
        entry_price = float(r.get("entry_price_used") or r.get("entry_price_1500") or r.get("entry_price_hint") or r.get("d0_close"))
    except (TypeError, ValueError):
        entry_price = None
    info_dict = {
        "stock_code": code,
        "signal_date": date,
        "entry_price_1500": entry_price,
        "d0_close": r.get("d0_close"),
    }
    # 탭 클릭 없이 위에서부터 한눈에 — 일봉/분봉은 항상 펼침, 수급·재무는 expander로 접어둠 (선택적 펼침).
    # 일봉 (MA)
    st.markdown("##### 📈 일봉 (MA)")
    try:
        render_daily_chart_with_ma(code, date)
        st.caption(
            "MA(이동평균)는 전체 일봉 데이터로 미리 계산된 값을 현재 view 구간만 잘라서 표시합니다."
        )
    except Exception as exc:  # noqa: BLE001
        st.info(f"일봉 차트 표시 불가: {exc}")

    # 분봉
    st.markdown("##### ⏱ 분봉 (5/15/30분)")
    try:
        mdf = load_minute(code)
        if mdf.empty:
            st.info("로컬 분봉 parquet이 없습니다. (`data/market/minute_ohlcv/{code}.parquet`)")
        else:
            plot_one_year_minute_chart(
                mdf,
                info_dict,
                r.to_dict(),
                show_outcome=False,
                key_prefix=f"sd_{code}_{date}",
            )
            st.caption("분봉은 거래일만 압축 표시되며, 휴장일/주말 공백은 자동 제거됩니다. (기간 고정: 웹훅일+D+1~D+5 전체)")
    except Exception as exc:  # noqa: BLE001
        st.info(f"분봉 차트 표시 불가: {exc}")

    # 수급 (외인·기관) — 보조 정보, 접어둠 (프로그램은 데이터 커버리지 낮아 제거)
    with st.expander("💰 수급 (외인·기관)", expanded=False):
        try:
            render_investor_flow_chart(code, date, lookback_days=40)
            render_investor_flow_table(code, date, lookback_days=22)
        except Exception as exc:  # noqa: BLE001
            st.info(f"수급 데이터 표시 불가: {exc}")

    # 재무 (DART) — 보조 정보, 접어둠. 신호일 시점 기준으로 공시·재무 필터.
    with st.expander("🏢 재무 (DART) · 기업정보 · 공시", expanded=False):
        try:
            render_financials_card(
                code,
                name=str(r.get("name", "") or ""),
                market=str(r.get("market", "") or ""),
                signal_date=date,
            )
        except Exception as exc:  # noqa: BLE001
            st.info(f"DART 재무 표시 불가: {exc}")

    # ──────── ② 메모 + 결과 (결과를 메모 옆으로 가깝게 배치) ────────
    st.markdown("---")
    st.markdown("### 메모 · 결과")

    # 관찰 기준 — 차트에서 고른 자동감시 룰/분봉 단위 자동 표시 + 가정 진입가 입력
    obs_cols = st.columns([1, 1, 2])
    with obs_cols[0]:
        chart_rule = st.session_state.get(f"{key_base}_rule", "기본")
        st.caption("자동감시 룰 (차트에서 선택)")
        st.markdown(f"**{chart_rule}**")
    with obs_cols[1]:
        chart_interval = st.session_state.get(f"{key_base}_interval_30default", "30분")
        st.caption("본 분봉 단위 (차트에서 선택)")
        st.markdown(f"**{chart_interval}**")
    with obs_cols[2]:
        st.text_input(
            "가정 진입가 (원)",
            key=f"{key_base}_entry_guess",
            placeholder="예: 13380 · 메모와 함께 저장됩니다",
        )

    memo_cols = st.columns([3, 3, 2])
    with memo_cols[0]:
        st.markdown("#### 사전 느낌")
        st.caption("결과 보기 전, 첫 인상부터 적어두면 다음에 비교 가능")
        st.text_area("첫 인상 / 우려 / 기대", key=f"{key_base}_pre", height=140, label_visibility="collapsed")
        st.markdown("##### 패턴 메모")
        st.text_area("패턴 메모", key=f"{key_base}_pattern", height=100, label_visibility="collapsed")
    with memo_cols[1]:
        st.markdown("#### 사후 생각")
        st.caption("결과 확인 후 추가 (오른쪽 칼럼)")
        st.text_area("실제 결과와 비교한 생각", key=f"{key_base}_post", height=140, label_visibility="collapsed")
        st.markdown("##### 놓친 점 · 다음 룰")
        st.text_area("놓친 점 / 다음 룰 아이디어", key=f"{key_base}_miss", height=100, label_visibility="collapsed")
    with memo_cols[2]:
        st.markdown("#### D+1~D+5 결과")
        result_keys = [
            ("max_gain_d1d5", "최대 상승"),
            ("max_loss_d1d5", "최대 하락"),
            ("d1_close_return_pct", "D+1 종가"),
            ("plus3_first", "+3 먼저"),
            ("minus3_first", "-3 먼저"),
            ("d5_last_price_return_from_1500", "D+5 종가"),
        ]
        for k, lbl in result_keys:
            v = r.get(k)
            if pd.isna(v):
                st.metric(lbl, "—")
            else:
                try:
                    fv = float(v)
                    if k in ("plus3_first", "minus3_first"):
                        st.metric(lbl, "Y" if fv else "N")
                    else:
                        st.metric(lbl, f"{fv:+.2f}%")
                except (TypeError, ValueError):
                    st.metric(lbl, str(v))

    _save_security_detail_memo(code, date, key_base)
    # 결과는 위쪽 메모 옆 컬럼(memo_cols[2])에 통합. 별도 하단 블록 제거.


def render_v2_hybrid_signal_board() -> None:
    """벨가드 안정후보 신호등 복기 — V2는 기록/비교용으로만 보존."""
    st.markdown(
        '<div class="cb-note" style="border-left-color:#6366f1;">'
        '<b>벨가드 안정후보 복기</b> — 1년치 D0 후보를 신호등으로 되돌아보는 화면입니다. '
        '기존 V2는 삭제하지 않고 기록/비교용 데이터셋으로 보존합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    ds_dir, prefix, _ = _resolve_main_dataset()
    wide_p = ds_dir / f"{prefix}_signal_by_date_1y.csv"
    if not wide_p.exists():
        wide_p = _resolve_hybrid_data_path("bellguard_1y/bellguard_signal_by_date_1y.csv") or _resolve_hybrid_data_path("v2_hybrid_signal_wide_by_date_1y.csv")
    ver_p = ds_dir / f"{prefix}_version_summary_1y.csv"
    if not ver_p.exists():
        ver_p = _resolve_hybrid_data_path("bellguard_1y/bellguard_version_summary_1y.csv") or _resolve_hybrid_data_path("v2_hybrid_signal_version_summary_1y.csv")
    month_p = ds_dir / f"{prefix}_month_summary_1y.csv"
    if not month_p.exists():
        month_p = _resolve_hybrid_data_path("bellguard_1y/bellguard_month_summary_1y.csv") or _resolve_hybrid_data_path("v2_hybrid_signal_month_summary_1y.csv")

    if wide_p is None:
        st.warning(
            "BellGuard 복기 데이터가 아직 도착하지 않았습니다. Codex 산출 "
            "`bellguard_1y/bellguard_signal_by_date_1y.csv` 등을 "
            "`bell-dashboard/data/closingbell/online_v2/latest/`에 두면 자동으로 표시됩니다."
        )
        return

    # KPI 영역 — 매일 볼 화면이 아니라 expander로 접기 (PDF에서 정식 비교 제공)
    if ver_p is not None:
      with st.expander("1년 KPI 요약 (자세한 비교는 PDF 리포트 참고)", expanded=False):
        try:
            ver_df = pd.read_csv(ver_p)
            metric_cols = [c for c in ver_df.columns if c not in ("version", "compare_group")]
            label_col = "version" if "version" in ver_df.columns else (
                "compare_group" if "compare_group" in ver_df.columns else ver_df.columns[0]
            )
            cols = st.columns(min(len(ver_df), 4) or 1)
            for i, (_, row) in enumerate(ver_df.iterrows()):
                with cols[i % len(cols)]:
                    label = str(row.get(label_col, "-"))
                    # 표시명 정리 — 데이터 원본 ID → 사용자 친화 라벨
                    label = label.replace("CURRENT_WEBHOOK_V2_TOP3", "기존 V2 기록후보")
                    label = label.replace("NEW_D0_1500_HYBRID_TOP3", "벨가드 안정후보")
                    label = label.replace("HYBRID_D0_RISK_FILTER", "벨가드 안정후보")
                    label = label.replace("HYBRID", "벨가드")
                    st.markdown(f"**{label}**")
                    show_keys = [
                        ("green_rate", "GREEN", "{:.1%}"),
                        ("red_rate", "RED", "{:.1%}"),
                        ("plus3_first_rate", "+3 먼저", "{:.1%}"),
                        ("minus3_first_rate", "-3 먼저", "{:.1%}"),
                    ]
                    for key, lbl, fmt in show_keys:
                        if key in row.index and pd.notna(row[key]):
                            try:
                                st.caption(f"{lbl}: {fmt.format(float(row[key]))}")
                            except (TypeError, ValueError):
                                st.caption(f"{lbl}: {row[key]}")
        except Exception as exc:  # noqa: BLE001
            st.caption(f"version summary 로드 실패: {exc}")

    # (NEW 2026-05-18) 최신일 후보 풀 요약 — 사용자 의문 "Top3가 다 안 보임"에 즉시 답하는 카드
    candidates_all_p = ds_dir / f"{prefix}_latest_candidates_all.csv"
    if candidates_all_p.exists():
        try:
            cand_df = pd.read_csv(candidates_all_p, encoding="utf-8-sig")
            if not cand_df.empty:
                latest_sig = str(cand_df.get("signal_date", pd.Series(["—"])).iloc[0])[:10]
                total_n = len(cand_df)
                ready_n = int(
                    pd.to_numeric(cand_df.get("webhook_data_ready", 0), errors="coerce")
                    .fillna(0)
                    .astype(int)
                    .sum()
                )
                top3_n = int(
                    pd.to_numeric(cand_df.get("selected_top3", 0), errors="coerce")
                    .fillna(0)
                    .astype(int)
                    .sum()
                )
                outside_n = total_n - top3_n
                st.markdown(f"##### 최신일({latest_sig}) 후보 풀 요약")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("원천 후보", f"{total_n}개")
                c2.metric("data_ready", f"{ready_n}개")
                c3.metric("Top3 선정", f"{top3_n}개")
                c4.metric("Top3 밖", f"{outside_n}개")
                st.caption(
                    "Codex audit (2026-05-18) 기준 1년 255일 모두 Top3 3개 정상. "
                    "신호등표에서 빈칸으로 느껴지면 화면 필터/스크롤 영향이며 데이터 부족이 아닙니다."
                )
                with st.expander("후보 풀 전체 + Top3 선정 / 제외 사유 / 중복 종목 표시", expanded=False):
                    show_cand_cols = [
                        "code", "name", "d0_date", "trading_day_age", "bellguard_score",
                        "webhook_data_ready", "signal_minute_rows",
                        "duplicate_in_latest_pool", "duplicate_score_rank_for_code",
                        "selected_top3", "display_reason",
                    ]
                    label_map = {
                        "code": "코드", "name": "종목", "d0_date": "D0",
                        "trading_day_age": "감시일차", "bellguard_score": "BG점수",
                        "webhook_data_ready": "data_ready", "signal_minute_rows": "분봉행수",
                        "duplicate_in_latest_pool": "중복",
                        "duplicate_score_rank_for_code": "중복순위",
                        "selected_top3": "Top3", "display_reason": "사유",
                    }
                    disp = cand_df[[c for c in show_cand_cols if c in cand_df.columns]].rename(columns=label_map)
                    st.dataframe(
                        disp, use_container_width=True, hide_index=True,
                        height=min(520, 44 + 30 * len(disp)),
                    )
        except Exception as exc:  # noqa: BLE001
            st.caption(f"최신일 후보 풀 로드 실패: {exc}")

    # 메인 신호등 표
    st.subheader("벨가드 날짜별 신호등 (1년)")
    try:
        wide_df = pd.read_csv(wide_p)
        st.dataframe(wide_df, use_container_width=True, height=520, hide_index=True)
        st.caption(
            f"표시 중 {len(wide_df):,}행 · 출처 {wide_p} · "
            "상세 차트용 일봉/분봉 캔들은 bellguard_1y 패키지에 함께 보존되어 있습니다."
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"wide 표 로드 실패: {exc}")

    # 월별 안정성
    if month_p is not None:
        with st.expander("월별 안정성 비교", expanded=False):
            try:
                month_df = pd.read_csv(month_p)
                st.dataframe(month_df, use_container_width=True, hide_index=True)
            except Exception as exc:  # noqa: BLE001
                st.caption(f"month summary 로드 실패: {exc}")


def render_today_hybrid_shadow() -> None:
    """오늘 탭의 벨가드 안정후보 메인 영역. 현재일 미래 결과는 표시하지 않는다."""
    st.markdown(
        '<div class="cb-note" style="border-left-color:#10b981; background:rgba(16,185,129,0.08);">'
        '🛡️ <b>오늘의 메인 표시: 벨가드 안정후보</b><br>'
        '현재일 후보 파일은 D+1~D+5 결과를 포함하지 않습니다. 실제 발송은 preview/가드 확인 후 별도 단계에서만 진행합니다.'
        '</div>',
        unsafe_allow_html=True,
    )
    # (5/19 점수 모델 전환 안내는 Bell Watch 본진 전환 5/20 이후 outdated가 되어 제거됨)
    # 메인 데이터셋 자동 선택 (pricecap_1y > bellguard_1y)
    ds_dir, prefix, ds_label = _resolve_main_dataset()
    today_p = ds_dir / f"{prefix}_top3_latest.csv"
    if not today_p.exists():
        today_p = _resolve_hybrid_data_path("bellguard_1y/bellguard_top3_latest.csv") or _resolve_hybrid_data_path("hybrid_top3_latest.csv")
    st.caption(f"데이터셋: {ds_label}")
    if today_p is not None and today_p.exists():
        try:
            df = pd.read_csv(today_p, encoding="utf-8-sig")
            st.subheader("벨가드 안정후보 Top3")
            show_cols = [
                "pricecap_rank", "bellguard_rank", "name", "code", "market", "d0_date",
                "bellguard_score", "bellguard_live_light", "bellguard_reason",
                "d0_pct_change", "distance_from_d0_high_pct", "volume_ratio_vs_20d",
                "entry_price_used", "overheat_score", "health_score", "regime_score", "regime",
                "daily_latest", "minute_latest", "inst_trade_latest", "short_sale_latest",
            ]
            label_map = {
                "pricecap_rank": "순위",
                "bellguard_rank": "순위",
                "name": "종목",
                "code": "코드",
                "market": "시장",
                "d0_date": "D0",
                "bellguard_score": "BellGuard",
                "bellguard_live_light": "신호등",
                "bellguard_reason": "근거",
                "d0_pct_change": "D0 등락",
                "distance_from_d0_high_pct": "고가대비",
                "volume_ratio_vs_20d": "20일대비",
                "entry_price_used": "15시가",
                "overheat_score": "과열",
                "health_score": "건전성",
                "regime_score": "국면",
                "regime": "장세",
                "daily_latest": "일봉",
                "minute_latest": "분봉",
                "inst_trade_latest": "외인/기관",
                "short_sale_latest": "공매도",
            }
            show = df[[c for c in show_cols if c in df.columns]].rename(columns=label_map)
            st.dataframe(show, use_container_width=True, hide_index=True, height=min(240, 44 + 38 * len(show)))
            st.caption(f"출처: {today_p} · 현재일 후보에는 미래 성과 컬럼을 넣지 않음")
        except Exception as exc:  # noqa: BLE001
            st.caption(f"오늘자 벨가드 데이터 로드 실패: {exc}")
    else:
        st.info(
            "오늘자 벨가드 안정후보 Top3는 다음 산출 슬롯 대기 중입니다 "
            "(`bellguard_1y/bellguard_top3_latest.csv` 도착 시 자동 표시)."
        )


def render_today_v2_record() -> None:
    """기존 V2는 비교/기록용으로 접어서 표시한다."""
    v2_p = _resolve_hybrid_data_path("v2_record_1y/v2_record_top3_latest.csv") or _resolve_hybrid_data_path("v2_top3_latest.csv")
    if v2_p is None:
        st.caption("기존 V2 기록후보 파일이 없습니다.")
        return
    try:
        df = pd.read_csv(v2_p, encoding="utf-8-sig")
        show_cols = ["role", "name", "code", "market", "score_v2", "d0_date", "entry_price_1500", "daily_latest_date", "minute_latest_date"]
        label_map = {
            "role": "기록 슬롯",
            "name": "종목",
            "code": "코드",
            "market": "시장",
            "score_v2": "V2",
            "d0_date": "D0",
            "entry_price_1500": "15시가",
            "daily_latest_date": "일봉",
            "minute_latest_date": "분봉",
        }
        show = df[[c for c in show_cols if c in df.columns]].rename(columns=label_map)
        st.dataframe(show, use_container_width=True, hide_index=True, height=min(220, 44 + 38 * len(show)))
        st.caption(f"출처: {v2_p} · V2 산식은 보존, 메인 표시에서는 제외")
    except Exception as exc:  # noqa: BLE001
        st.caption(f"V2 기록후보 로드 실패: {exc}")


def render_bellguard_intro_cards() -> None:
    """벨가드 안정후보의 도달률·안정성·보는 법을 카드로 소개 (manifest 기반 동적)."""
    st.markdown("### 벨가드 안정후보란?")
    # 메인 variant 찾기
    manifest = _load_main_manifest_kpi()
    main_kpi: dict | None = None
    n_sample = "—"
    dataset_label = "데이터 미감지"
    if manifest:
        main_key = manifest.get("main_variant", "100k")
        for v in manifest.get("summary_kpi", []):
            if v.get("variant") == main_key:
                main_kpi = v
                break
        dataset_label = manifest.get("dataset_name", "—")
        if main_kpi:
            n_sample = f"{main_kpi.get('sample_n', '—')}건"
    st.markdown(
        f'<div class="cb-note" style="border-left-color:#16a34a;">'
        f'<b>더 크게 먹기 위한 후보가 아니라, 덜 깨지는 후보를 고르기 위한 안정 필터입니다.</b><br>'
        f'데이터셋: {dataset_label} · 표본 {n_sample} · D0 Strict (active_d0_3d_pool) 기반.'
        f'</div>',
        unsafe_allow_html=True,
    )


def load_daily3_pool_csv(filename: str) -> pd.DataFrame:
    path = DAILY3_POOL_PREVIEW_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    except Exception:
        return pd.DataFrame()


def load_daily3_pool_manifest() -> dict[str, Any]:
    path = DAILY3_POOL_PREVIEW_DIR / "daily3_pool_manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _daily3_money(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:,.0f}원"


def _daily3_pct(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:+.1f}%"


def _daily3_ratio(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:.0f}%"


def _daily3_bool(value: Any) -> str:
    return "예" if str(value).strip().lower() in {"true", "1", "yes", "y"} else "아니오"


def _daily3_result_text(row: dict[str, Any], latest_date: str) -> str:
    signal_date = str(row.get("signal_date", ""))[:10]
    if signal_date == latest_date and not str(row.get("ret_d1_close", "")).strip():
        return "paper watch 대기"
    return (
        f"D+1 +1 {_daily3_bool(row.get('d1_plus1_touch'))} / "
        f"-2 {_daily3_bool(row.get('d1_minus2_touch'))} · "
        f"D+5 +2 {_daily3_bool(row.get('h5_plus2_touch'))} / "
        f"-2 {_daily3_bool(row.get('h5_minus2_touch'))}"
    )


def load_eod_active_watch_csv(filename: str) -> pd.DataFrame:
    path = EOD_ACTIVE_WATCH_PREVIEW_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    except Exception:
        return pd.DataFrame()


def load_eod_active_watch_manifest() -> dict[str, Any]:
    path = EOD_ACTIVE_WATCH_PREVIEW_DIR / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def _load_eod_active_watch_1y_csv_cached(filename: str, mtime_ns: int) -> pd.DataFrame:
    path = EOD_ACTIVE_WATCH_1Y_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    except Exception:
        return pd.DataFrame()


def load_eod_active_watch_1y_csv(filename: str) -> pd.DataFrame:
    path = EOD_ACTIVE_WATCH_1Y_DIR / filename
    mtime_ns = path.stat().st_mtime_ns if path.exists() else 0
    return _load_eod_active_watch_1y_csv_cached(filename, mtime_ns)


def load_eod_active_watch_1y_manifest() -> dict[str, Any]:
    path = EOD_ACTIVE_WATCH_1Y_DIR / "eod_d0_active_watch_manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _eod_paper_watch_dir() -> Path | None:
    """Paper Watch 데이터 폴더 — online 사본 우선, 없으면 shared 원본."""
    for d in EOD_PAPER_WATCH_DIRS:
        if d.exists() and (d / "paper_watch_log.csv").exists():
            return d
    return None


@st.cache_data(show_spinner=False)
def load_eod_paper_watch_log() -> pd.DataFrame:
    """paper_watch_log.csv 로드 (Codex retro labeling 산출 825행)."""
    d = _eod_paper_watch_dir()
    if d is None:
        return pd.DataFrame()
    try:
        return pd.read_csv(d / "paper_watch_log.csv", encoding="utf-8-sig", dtype=str).fillna("")
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


def load_eod_paper_watch_manifest() -> dict[str, Any]:
    d = _eod_paper_watch_dir()
    if d is None:
        return {}
    p = d / "paper_watch_manifest.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return {}


# 사후 라벨 색상 매핑 (Codex retro labeling §5)
_PAPER_WATCH_LABEL_STYLE: dict[str, tuple[str, str]] = {
    # D+1 라벨
    "D1_PLUS1_PROTECT_SUCCESS": ("#dcfce7", "#166534"),
    "D1_VOLATILE_BOTH": ("#ffedd5", "#9a3412"),
    "D1_FAST_FAIL": ("#fee2e2", "#991b1b"),
    "D1_FLAT": ("#f1f5f9", "#475569"),
    "D1_PENDING": ("#f1f5f9", "#94a3b8"),
    # H5 라벨
    "H5_GOOD": ("#dcfce7", "#166534"),
    "H5_RISKY_WINNER": ("#ffedd5", "#9a3412"),
    "H5_FAIL": ("#fee2e2", "#991b1b"),
    "H5_DEAD": ("#f1f5f9", "#475569"),
    "H5_PENDING": ("#f1f5f9", "#94a3b8"),
}


# Bell Watch 신호등표용 — d1_label을 🟢🟡🟠🔴⚪로 매핑 (BellGuard 신호등표와 동일 색 체계)
def _traffic_label_to_light(label: str) -> str:
    lbl = (label or "").strip().upper()
    if lbl == "GREEN_DIRECT_PROFIT_CHANCE":
        return "🟢"
    if lbl == "YELLOW_PROFIT_CHANCE_VOLATILE":
        return "🟡"
    if lbl == "ORANGE_DIP_REBOUND_CHANCE":
        return "🟠"
    if lbl in ("RED_FAST_FAIL", "RED_NO_PROFIT_CHANCE"):
        return "🔴"
    return "⚪"


def _d1_label_to_light(label: str) -> str:
    """paper_watch_log d1_label → 신호등 이모지."""
    lbl = (label or "").strip().upper()
    if not lbl or lbl in ("D1_PENDING", "NAN"):
        return "⚪"
    if lbl in {
        "GREEN_DIRECT_PROFIT_CHANCE",
        "YELLOW_PROFIT_CHANCE_VOLATILE",
        "ORANGE_DIP_REBOUND_CHANCE",
        "RED_FAST_FAIL",
        "RED_NO_PROFIT_CHANCE",
        "GRAY_PENDING_OR_INSUFFICIENT",
    }:
        return _traffic_label_to_light(lbl)
    # 강세 — +1.3% 도달, -2% 없음 / 방어 성공
    if lbl in ("D1_DIRECT_RISE", "D1_PLUS1_PROTECT_SUCCESS", "D1_PRICE_DEFENSE"):
        return "🟢"
    # 회복 — +1.3% 먼저 도달 + -2%도 터치 / dip rebound
    if lbl in ("D1_VOLATILE_PLUS_FIRST", "D1_VOLATILE_BOTH", "D1_DIP_REBOUND"):
        return "🟡"
    # 실패 — -2% 먼저 후 +1.3% 도달
    if lbl in ("D1_VOLATILE_MINUS_FIRST",):
        return "🟠"
    # 약세 — +1.3% 기회 없이 -2% 발생
    if lbl in ("D1_FAST_FAIL",):
        return "🔴"
    # 보합 / 미발생
    return "⚪"


@st.cache_data(show_spinner=False)
def load_eod_chart_learning_replay() -> pd.DataFrame:
    """chart_learning_replay.csv 로드 (Codex retro labeling replay 825행)."""
    d = _eod_paper_watch_dir()
    if d is None:
        return pd.DataFrame()
    try:
        return pd.read_csv(d / "chart_learning_replay.csv", encoding="utf-8-sig", dtype=str).fillna("")
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


def load_eod_chart_learning_manifest() -> dict[str, Any]:
    d = _eod_paper_watch_dir()
    if d is None:
        return {}
    p = d / "chart_learning_replay_manifest.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return {}


# chart_status 색상 매핑
_CHART_STATUS_STYLE: dict[str, tuple[str, str, str]] = {
    "OK": ("#dcfce7", "#166534", "정상"),
    "PARTIAL_MINUTE": ("#ffedd5", "#9a3412", "분봉 부분 결손"),
    "ENTRY_OR_SIGNAL_MINUTE_INSUFFICIENT": ("#fee2e2", "#991b1b", "15시 분봉 부족"),
    "H5_PENDING": ("#f1f5f9", "#475569", "H5 대기"),
    "PENDING_LATEST": ("#f1f5f9", "#94a3b8", "오늘 대기"),
}


def _chart_status_pill(status: str) -> str:
    bg, fg, label = _CHART_STATUS_STYLE.get(
        str(status).strip(), ("#f1f5f9", "#475569", str(status) or "—")
    )
    return (
        f'<span style="background:{bg}; color:{fg}; padding:3px 10px; '
        f'border-radius:999px; font-size:0.82rem; font-weight:600;">{label}</span>'
    )


def _paper_watch_label_pill(label: str) -> str:
    if not label or str(label).strip() in ("", "nan"):
        return '<span style="color:#94a3b8;">—</span>'
    bg, fg = _PAPER_WATCH_LABEL_STYLE.get(str(label).strip(), ("#f1f5f9", "#475569"))
    return (
        f'<span style="background:{bg}; color:{fg}; padding:2px 8px; '
        f'border-radius:999px; font-size:0.78rem; font-weight:600;">{label}</span>'
    )


def _eod_money(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:,.0f}원"


def _eod_pct(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:+.1f}%"


def _eod_ratio(value: Any) -> str:
    n = numeric(value)
    if n is None:
        return "—"
    return f"{n:.0f}%"


def _eod_color_pct(value: Any) -> str:
    """등락률 색상 — 양수 녹색·음수 빨간색·0/None 무채색."""
    n = numeric(value)
    if n is None:
        return "#0f172a"
    if n > 0:
        return "#16a34a"
    if n < 0:
        return "#dc2626"
    return "#0f172a"


def _eod_color_rsi(value: Any) -> str:
    """RSI 색상 — 과매수(>=70) / 과매도(<=30) 시 빨간색, 중립은 무채색."""
    n = numeric(value)
    if n is None:
        return "#0f172a"
    if n >= 70 or n <= 30:
        return "#dc2626"
    return "#0f172a"


# 배지 분류 (Codex 2026-05-20 retro labeling badge_text 10종 매핑)
_EOD_BADGE_DANGER = (
    "D0고가 -20%↓", "D0종가 -10%↓", "깊은 눌림",
    "신호일 약세", "RSI 과열", "RSI 과매도",
)
_EOD_BADGE_CAUTION = ("거래량 약화",)
_EOD_BADGE_POSITIVE = ("Pool F refined", "15시 balanced")
_EOD_BADGE_NEUTRAL = ("RSI 중립",)


def _eod_badge_pills(badge_text: Any) -> str:
    """badge_text의 `·` 구분 토큰을 색상 분리된 pill HTML로 변환."""
    raw = str(badge_text or "").strip()
    if not raw or raw.lower() == "nan":
        return '<span style="color:#94a3b8;">—</span>'
    parts = [p.strip() for p in raw.replace("/", "·").split("·") if p.strip()]
    if not parts:
        return '<span style="color:#94a3b8;">—</span>'
    pills: list[str] = []
    for p in parts:
        if any(k in p for k in _EOD_BADGE_DANGER):
            bg, fg = "#fee2e2", "#991b1b"
        elif any(k in p for k in _EOD_BADGE_CAUTION):
            bg, fg = "#ffedd5", "#9a3412"
        elif any(k in p for k in _EOD_BADGE_POSITIVE):
            bg, fg = "#dcfce7", "#166534"
        elif any(k in p for k in _EOD_BADGE_NEUTRAL):
            bg, fg = "#f1f5f9", "#475569"
        else:
            bg, fg = "#f1f5f9", "#475569"
        pills.append(
            f'<span style="background:{bg}; color:{fg}; padding:2px 8px; '
            f'border-radius:999px; font-size:0.78rem; font-weight:600; '
            f'margin:0 4px 3px 0; display:inline-block;">{p}</span>'
        )
    return "".join(pills)


def render_eod_active_watch_preview() -> None:
    """Bell Watch main route. D0 storage, active watch, and webhook Top3 stay separated."""
    manifest = load_eod_active_watch_manifest()
    top3 = load_eod_active_watch_csv("webhook_top3_preview.csv")
    active = load_eod_active_watch_csv("active_watchlist.csv")
    d0_pool = load_eod_active_watch_csv("d0_storage_pool_latest.csv")
    legacy = load_eod_active_watch_csv("legacy_baseline_summary.csv")

    st.markdown("### Bell Watch · 운영 메인")
    st.caption("장후 확정 D0 저장풀을 다음 거래일부터 감시하고, 15시 이하 데이터만으로 15시 Top3를 뽑습니다. 자동매매·주문·계좌 API는 없습니다.")
    # 선정 기준 명시 — Codex retro labeling 핸드오프 권장 (사용자 메시지 일관성)
    st.markdown(
        '<div style="background:#f1f5f9; border-left:3px solid #475569; padding:7px 12px; '
        'border-radius:4px; margin:4px 0 10px; font-size:0.86rem; color:#334155;">'
        '<b>선정 기준</b> — D0 거래대금 우선 Top3 · 15시 지표(등락률·D0대비·거래량·RSI)는 '
        '<b>상태/위험 확인용</b>이며 선정 점수에는 들어가지 않습니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    if not manifest and top3.empty:
        st.info(f"Bell Watch preview 데이터가 없습니다. 경로: `{EOD_ACTIVE_WATCH_PREVIEW_DIR}`")
        return

    signal_date = str(manifest.get("signal_date") or (top3["signal_date"].iloc[0] if not top3.empty and "signal_date" in top3.columns else ""))[:10]
    guard_status = str(manifest.get("guard_status") or (manifest.get("guards") or {}).get("status") or "UNKNOWN")
    metric_cols = st.columns(5)
    metric_cols[0].metric("신호일", signal_date or "—")
    metric_cols[1].metric("D0 저장풀", manifest.get("d0_storage_count_latest", len(d0_pool)))
    metric_cols[2].metric("Active Watch", manifest.get("active_watch_count", len(active)))
    metric_cols[3].metric("Top3", manifest.get("selected_count", len(top3)))
    metric_cols[4].metric("Guard", guard_status)

    if guard_status != "PASS":
        st.warning("Guard가 PASS가 아닙니다. 오늘 데이터 대기/실패 상태일 수 있으며, 대시보드는 마지막 PASS 사본을 보존합니다.")

    if top3.empty:
        st.info("15시 Top3 preview 후보가 없습니다.")
        return

    top3 = top3.copy()
    top3["rank_num"] = pd.to_numeric(top3.get("webhook_rank", 0), errors="coerce").fillna(0).astype(int)
    top3 = top3.sort_values("rank_num").head(3)
    card_cols = st.columns(3)
    for i, (_, r) in enumerate(top3.iterrows()):
        row = r.to_dict()
        age = numeric(row.get("trading_day_age"))
        if age is not None and age <= 3:
            age_badge = "신선"
            age_color = "#059669"
        elif age is not None and age <= 7:
            age_badge = "관찰"
            age_color = "#2563eb"
        else:
            age_badge = "오래된 D0 주의"
            age_color = "#d97706"
        high_gap = numeric(row.get("signal_vs_d0_high_pct"))
        close_gap = row.get("signal_vs_d0_close_pct")
        signal_pct = row.get("signal_day_pct_change_1500")
        rsi_val = row.get("rsi14_signal_1500")
        # 카드 헤더 옆 경고 pill — D0 고가 대비 -20% 이하면 강조
        warn_pill = (
            '<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; '
            'border-radius:999px; font-size:0.78rem; font-weight:600; margin-left:6px;">'
            '⚠️ 고가 -20%↓</span>'
        ) if high_gap is not None and high_gap <= -20 else ""
        with card_cols[i % 3]:
            st.markdown(
                f"""
<div style="border:1px solid #d6dae3; border-radius:8px; padding:14px 14px 12px; min-height:270px;">
  <div style="display:flex; justify-content:space-between; gap:8px; align-items:center; flex-wrap:wrap;">
    <div><b>#{row.get('webhook_rank', '')} {row.get('stock_name', '')}</b>{warn_pill}</div>
    <span style="background:{age_color}; color:white; padding:2px 8px; border-radius:999px; font-size:0.82rem;">D+{row.get('trading_day_age', '')} · {age_badge}</span>
  </div>
  <div style="color:#64748b; font-size:0.86rem; margin:4px 0 10px;">{normalize_code(row.get('stock_code', ''))} · {row.get('market', '')}</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:7px; font-size:0.90rem;">
    <div><span style="color:#64748b;">15시가</span><br><b>{_eod_money(row.get('entry_1500_price'))}</b></div>
    <div><span style="color:#64748b;">10만원 1주</span><br><b>{_daily3_bool(row.get('current_seed_100k_buyable'))}</b></div>
    <div><span style="color:#64748b;">D0 등록일</span><br><b>{row.get('d0_date', '')}</b></div>
    <div><span style="color:#64748b;">감시 일차</span><br><b>D+{row.get('trading_day_age', '')}</b></div>
    <div><span style="color:#64748b;">신호일 등락</span><br><b style="color:{_eod_color_pct(signal_pct)};">{_eod_pct(signal_pct)}</b></div>
    <div><span style="color:#64748b;">D0 종가대비</span><br><b style="color:{_eod_color_pct(close_gap)};">{_eod_pct(close_gap)}</b></div>
    <div><span style="color:#64748b;">D0 고가대비</span><br><b style="color:{_eod_color_pct(high_gap)};">{_eod_pct(high_gap)}</b></div>
    <div><span style="color:#64748b;">거래량 유지</span><br><b>{_eod_ratio(row.get('signal_volume_retention_vs_d0'))}</b></div>
    <div><span style="color:#64748b;">RSI14</span><br><b style="color:{_eod_color_rsi(rsi_val)};">{_eod_ratio(rsi_val).replace('%', '')}</b></div>
  </div>
  <div style="margin-top:12px; font-size:0.85rem; color:#334155;">{_eod_badge_pills(row.get('badge_text', ''))}</div>
  <div style="margin-top:6px; font-size:0.86rem; color:#64748b;">D+ 결과는 paper watch 대기</div>
</div>
""",
                unsafe_allow_html=True,
            )

    with st.expander("D0 저장풀 / Active Watchlist / Guard 세부", expanded=False):
        st.markdown("#### Guard")
        guards = manifest.get("guards") or {}
        if guards:
            guard_rows = [{"항목": _safe_text(k), "값": _safe_text(v)} for k, v in guards.items()]
            guard_df = pd.DataFrame(guard_rows, columns=["항목", "값"]).astype(str)
            st.dataframe(guard_df, use_container_width=True, hide_index=True, height=260)
        st.markdown("#### Active Watchlist")
        active_cols = ["signal_date", "stock_code", "stock_name", "d0_date", "trading_day_age", "d0_pct_change", "d0_trading_value_proxy_eok", "d0_value_rank"]
        if active.empty:
            st.caption("Active watchlist 파일이 없습니다.")
        else:
            st.dataframe(active[[c for c in active_cols if c in active.columns]].head(200), use_container_width=True, hide_index=True, height=300)
        st.markdown("#### 최신 D0 저장풀")
        d0_cols = ["d0_date", "stock_code", "stock_name", "market", "d0_close", "d0_volume", "d0_pct_change", "d0_trading_value_proxy_eok", "d0_value_rank"]
        if d0_pool.empty:
            st.caption("D0 storage pool 파일이 없습니다.")
        else:
            st.dataframe(d0_pool[[c for c in d0_cols if c in d0_pool.columns]].head(200), use_container_width=True, hide_index=True, height=260)
    with st.expander("Bell Watch 본진 vs 기존 V2/BellGuard/P0 비교 기준선", expanded=False):
        if legacy.empty:
            st.caption("legacy_baseline_summary.csv 파일이 없습니다.")
        else:
            # EOD 현재 본진 row를 상단에 별도 카드로 강조 — 사용자가 한눈에 비교
            eod_row = legacy[legacy.get("comparison_group", "").astype(str) == "current_eod_active_watch"]
            if not eod_row.empty:
                er = eod_row.iloc[0]
                st.markdown(
                    '<div style="background:#ecfdf5; border:2px solid #059669; border-radius:8px; '
                    'padding:10px 14px; margin-bottom:10px;">'
                    '<div style="font-size:0.92rem; font-weight:700; color:#065f46;">🛡 현재 운영 본진</div>'
                    f'<div style="font-size:0.86rem; color:#047857; margin:2px 0 8px;">{er.get("model_id", "EOD_D0_BASE_VALUE_TOP3")} · watch_days={int(numeric(er.get("watch_days"), 10))}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                eod_metric_cols = st.columns(5)
                eod_metric_cols[0].metric("D+1 +1%", f"{numeric(er.get('d1_plus1_touch_rate'), 0):.2f}%")
                eod_metric_cols[1].metric("D+1 -2%", f"{numeric(er.get('d1_minus2_touch_rate'), 0):.2f}%")
                eod_metric_cols[2].metric("+1 먼저", f"{numeric(er.get('d1_plus1_before_minus2_rate'), 0):.2f}%")
                eod_metric_cols[3].metric("H5 +2%", f"{numeric(er.get('h5_plus2_touch_rate'), 0):.2f}%")
                eod_metric_cols[4].metric("위험보정", f"{numeric(er.get('risk_adjusted_score'), 0):.2f}")
                # P0 baseline 대비 risk_adj 차이 표시 (사용자가 우위 즉시 인지)
                p0_row = legacy[legacy.get("model_id", "").astype(str) == "P0_VALUE_20D_D0_FROZEN"]
                if not p0_row.empty:
                    p0_ra = numeric(p0_row.iloc[0].get("risk_adjusted_score"), 0)
                    eod_ra = numeric(er.get("risk_adjusted_score"), 0)
                    diff = eod_ra - p0_ra
                    diff_color = "#059669" if diff > 0 else ("#dc2626" if diff < 0 else "#475569")
                    diff_sign = "+" if diff >= 0 else ""
                    st.caption(
                        f"P0_VALUE_20D baseline 대비 위험보정 "
                        f"<b style='color:{diff_color}'>{diff_sign}{diff:.2f}pp</b> "
                        f"(Bell Watch {eod_ra:.2f} vs P0 {p0_ra:.2f})",
                        unsafe_allow_html=True,
                    )
                st.markdown("---")
            # 비교 표 전체 (legacy 모두 + EOD 현재 본진을 한 표에서 risk_adj 순)
            st.markdown("##### 전체 비교 표 (위험보정 점수 내림차순)")
            show_cols = [
                "model_id",
                "comparison_group",
                "watch_days",
                "sample_n",
                "full3_day_rate",
                "d1_plus1_touch_rate",
                "d1_minus2_touch_rate",
                "d1_plus1_before_minus2_rate",
                "h5_plus2_touch_rate",
                "h5_minus2_touch_rate",
                "risk_adjusted_score",
            ]
            labels = {
                "model_id": "기준선",
                "comparison_group": "구분",
                "watch_days": "감시일",
                "sample_n": "표본",
                "full3_day_rate": "일 3종목",
                "d1_plus1_touch_rate": "D+1 +1%",
                "d1_minus2_touch_rate": "D+1 -2%",
                "d1_plus1_before_minus2_rate": "+1 먼저",
                "h5_plus2_touch_rate": "H5 +2%",
                "h5_minus2_touch_rate": "H5 -2%",
                "risk_adjusted_score": "위험보정",
            }
            st.dataframe(legacy[[c for c in show_cols if c in legacy.columns]].rename(columns=labels), use_container_width=True, hide_index=True)
            st.caption("Bell Watch 본진과 기존 P0/V2/BellGuard는 내부 학습용 비교표입니다. 현재 메인 후보는 Bell Watch입니다.")
    st.caption(f"데이터: `{EOD_ACTIVE_WATCH_PREVIEW_DIR}` · D0 저장풀, Active Watchlist, 15시 Top3는 별도 파일로 분리됩니다.")


def render_eod_paper_watch_tab() -> None:
    """Paper Watch 사후 라벨링 — Codex retro labeling 산출(2026-05-20) 표시.

    실제 발송이 아니라 매 거래일 15시에 Bell Watch Top3로 뽑힌 후보를 누적 로그로 저장하고,
    D+1 / H5(5거래일 후) 결과 확정 시 사후 라벨과 해석 태그를 자동 갱신한다.

    절대 미래시 금지 (D+1/H5 결과는 표시·평가·학습 메모용이며 선정 점수에 들어가지 않음).
    """
    log = load_eod_paper_watch_log()
    manifest = load_eod_paper_watch_manifest()

    st.markdown("### Paper Watch · 사후 라벨링")
    st.caption(
        "매 거래일 15시 Bell Watch Top3 후보를 누적 저장하고 D+1·H5 결과 확정 시 "
        "사후 라벨/해석 태그를 자동 갱신합니다. 미래 결과는 후보 선정에 사용되지 않습니다."
    )

    if log.empty:
        st.info(
            "Paper Watch 로그가 아직 없습니다. Codex retro labeling 산출이 완료되면 자동 표시됩니다."
        )
        return

    # 숫자 컬럼 변환
    for c in ("rank", "trading_day_age", "d1_close_return_pct",
              "h5_close_return_pct", "h5_mfe", "h5_mae"):
        if c in log.columns:
            log[c] = pd.to_numeric(log[c], errors="coerce")

    # ── 상단 metric
    rows_total = manifest.get("rows_total", len(log))
    signal_days = manifest.get("signal_days", log["signal_date"].nunique())
    latest_signal_date = manifest.get("latest_signal_date") or log["signal_date"].max()
    d1_done = manifest.get("d1_done_rows", int((log.get("d1_status", "") == "DONE").sum()))
    h5_done = manifest.get("h5_done_rows", int((log.get("h5_status", "") == "DONE").sum()))
    pending = manifest.get("pending_rows", int(((log.get("d1_status", "") == "PENDING") |
                                                 (log.get("h5_status", "") == "PENDING")).sum()))
    g_status = manifest.get("guard_status", "—")

    mcols = st.columns(6)
    mcols[0].metric("총 로그", f"{rows_total}")
    mcols[1].metric("신호일 수", f"{signal_days}")
    mcols[2].metric("최신 신호일", latest_signal_date or "—")
    mcols[3].metric("D+1 확정", f"{d1_done}")
    mcols[4].metric("H5 확정", f"{h5_done}")
    mcols[5].metric("Guard", g_status)

    # ── 필터
    fcols = st.columns([1.5, 1.3, 1.3, 2])
    with fcols[0]:
        sort_order = st.radio("정렬", ["최신순", "과거순"], horizontal=True, key="pw_sort")
    with fcols[1]:
        d1_options = ["전체"] + sorted([x for x in log["d1_label"].dropna().unique() if x])
        d1_filter = st.selectbox("D+1 라벨", d1_options, key="pw_d1_filter")
    with fcols[2]:
        h5_options = ["전체"] + sorted([x for x in log["h5_label"].dropna().unique() if x])
        h5_filter = st.selectbox("H5 라벨", h5_options, key="pw_h5_filter")
    with fcols[3]:
        name_q = st.text_input("종목 검색 (이름/코드)", key="pw_name_search", placeholder="비워두면 전체")

    view = log.copy()
    if d1_filter != "전체":
        view = view[view["d1_label"] == d1_filter]
    if h5_filter != "전체":
        view = view[view["h5_label"] == h5_filter]
    if name_q:
        q = name_q.strip()
        view = view[
            view["stock_name"].astype(str).str.contains(q, case=False, na=False)
            | view["stock_code"].astype(str).str.contains(q, na=False)
        ]
    view = view.sort_values("signal_date", ascending=(sort_order == "과거순"))

    st.caption(f"표시 중 {len(view):,}행")

    # ── 라벨 분포 expander (사후 학습 요약)
    with st.expander("📊 사후 라벨 분포 (D+1 / H5)", expanded=False):
        dist_cols = st.columns(2)
        with dist_cols[0]:
            st.markdown("**D+1 라벨 분포**")
            d1_dist = log["d1_label"].value_counts().rename_axis("라벨").reset_index(name="N")
            st.dataframe(d1_dist, use_container_width=True, hide_index=True, height=240)
        with dist_cols[1]:
            st.markdown("**H5 라벨 분포**")
            h5_dist = log["h5_label"].value_counts().rename_axis("라벨").reset_index(name="N")
            st.dataframe(h5_dist, use_container_width=True, hide_index=True, height=240)
        st.caption(
            "PENDING은 D+1/H5 결과가 아직 확정되지 않은 후보 (오늘·최신 신호일 + 휴장일 영향)."
        )

    # ── retro_tags 빈도 시각화 (성공 vs 실패 후보 반복 태그)
    with st.expander("🏷 retro_tags 빈도 — 성공·실패 후보 반복 태그", expanded=False):
        success_mask = (
            log["h5_label"].isin(["H5_GOOD", "H5_RISKY_WINNER"])
            | (log["d1_label"] == "D1_PLUS1_PROTECT_SUCCESS")
        )
        fail_mask = (
            log["h5_label"].isin(["H5_FAIL", "H5_DEAD"])
            | (log["d1_label"] == "D1_FAST_FAIL")
        )

        def _retro_tag_freq(subset: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
            all_tags: list[str] = []
            for tags in subset.get("retro_tags", pd.Series(dtype=str)).dropna():
                all_tags.extend([t.strip() for t in str(tags).split("|") if t.strip()])
            if not all_tags:
                return pd.DataFrame(columns=["태그", "N", "비율(%)"])
            base_n = len(subset)
            counts = pd.Series(all_tags).value_counts().head(top_n)
            return pd.DataFrame({
                "태그": counts.index,
                "N": counts.values,
                "비율(%)": [f"{c / base_n * 100:.1f}" for c in counts.values],
            })

        s_df = _retro_tag_freq(log[success_mask])
        f_df = _retro_tag_freq(log[fail_mask])
        cols_tag = st.columns(2)
        with cols_tag[0]:
            st.markdown(f"**🟢 성공 후보 (N={int(success_mask.sum())}) 반복 태그**")
            if s_df.empty:
                st.caption("성공 후보가 없거나 retro_tags가 비어있습니다.")
            else:
                st.dataframe(s_df, hide_index=True, use_container_width=True, height=420)
        with cols_tag[1]:
            st.markdown(f"**🔴 실패 후보 (N={int(fail_mask.sum())}) 반복 태그**")
            if f_df.empty:
                st.caption("실패 후보가 없거나 retro_tags가 비어있습니다.")
            else:
                st.dataframe(f_df, hide_index=True, use_container_width=True, height=420)
        st.caption(
            "성공 = H5_GOOD/H5_RISKY_WINNER 또는 D1_PLUS1_PROTECT_SUCCESS · "
            "실패 = H5_FAIL/H5_DEAD 또는 D1_FAST_FAIL. 비율(%)은 해당 그룹 N 기준. "
            "단순 빈도이며 인과 관계가 아님 — 패턴 가설 출발점으로만 활용."
        )

    # ── 본문 표 (HTML 카드 형태로 핵심만)
    st.markdown("##### 후보 로그")
    if view.empty:
        st.info("필터에 맞는 후보가 없습니다.")
        return

    header_html = (
        '<div style="display:grid; grid-template-columns:1.0fr 0.5fr 1.5fr 0.9fr 0.7fr '
        '1.4fr 1.0fr 2.5fr; gap:8px; padding:6px 10px; font-size:0.82rem; font-weight:700; '
        'color:#475569; border-bottom:1px solid #cbd5e1; background:#f8fafc;">'
        '<div>신호일</div><div>순위</div><div>종목</div><div>D0 등록</div>'
        '<div>감시</div><div>D+1 라벨</div><div>H5 라벨</div><div>해석 태그</div>'
        '</div>'
    )
    rows_html = [header_html]
    # 최대 200행까지 (퍼포먼스 고려, 사용자가 필터로 좁힐 수 있게)
    for _, r in view.head(200).iterrows():
        retro = str(r.get("retro_tags", "")).replace("|", " · ") or "—"
        age = r.get("trading_day_age")
        try:
            age_int = int(float(age)) if pd.notna(age) and age != "" else "—"
            age_label = f"D+{age_int}"
        except (TypeError, ValueError):
            age_label = "—"
        d1_pill = _paper_watch_label_pill(str(r.get("d1_label", "")))
        h5_pill = _paper_watch_label_pill(str(r.get("h5_label", "")))
        # pending 행은 시각적으로 옅게
        is_pending = str(r.get("paper_watch_status", "")).startswith("pending")
        row_bg = "rgba(241,245,249,0.55)" if is_pending else "transparent"
        rows_html.append(
            f'<div style="display:grid; grid-template-columns:1.0fr 0.5fr 1.5fr 0.9fr 0.7fr '
            f'1.4fr 1.0fr 2.5fr; gap:8px; padding:6px 10px; font-size:0.86rem; '
            f'border-bottom:1px solid #f1f5f9; background:{row_bg}; align-items:center;">'
            f'<div>{r.get("signal_date", "")[:10]}</div>'
            f'<div>{r.get("rank", "")}</div>'
            f'<div><b>{r.get("stock_name", "")}</b> '
            f'<span style="color:#64748b; font-size:0.78rem;">{r.get("stock_code", "")}</span></div>'
            f'<div>{str(r.get("d0_date", ""))[:10]}</div>'
            f'<div>{age_label}</div>'
            f'<div>{d1_pill}</div>'
            f'<div>{h5_pill}</div>'
            f'<div style="color:#475569; font-size:0.78rem;">{retro}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="border:1px solid #e2e8f0; border-radius:6px; overflow:hidden;">{"".join(rows_html)}</div>',
        unsafe_allow_html=True,
    )

    if len(view) > 200:
        st.caption(f"표시 상한 200행 도달 — 전체 {len(view)}행 중 200행만 표시. 필터로 좁혀 보세요.")

    # ── 사용자 메모 입력 (Codex retro labeling 핸드오프 §7.2 "사람이 직접 남길 메모 칸")
    st.markdown("---")
    st.markdown("##### ✏ 후보 메모 — 사후 해석 기록")
    st.caption(
        "특정 (신호일, 종목) 조합에 사용자가 직접 남기는 사후 해석 메모. "
        "라벨/태그가 자동 분류해주는 것 외에 '왜 그랬는지' 가설·관찰을 자유 텍스트로 저장."
    )
    # 메모 대상 선택
    note_view = view if not view.empty else log
    options_df = note_view.head(200).copy()
    note_cols = st.columns([2, 2, 6, 1])
    with note_cols[0]:
        note_date_opts = sorted(options_df["signal_date"].dropna().astype(str).unique().tolist(), reverse=True)
        if not note_date_opts:
            st.caption("선택 가능한 신호일이 없습니다.")
            note_date = ""
        else:
            note_date = st.selectbox("신호일", note_date_opts, key="pw_note_date")
    with note_cols[1]:
        if note_date:
            same_day = options_df[options_df["signal_date"].astype(str) == note_date]
            stock_opts = [
                f"{r['stock_name']} ({r['stock_code']})"
                for _, r in same_day.iterrows()
            ]
            if not stock_opts:
                st.caption("종목 없음")
                note_stock_idx = None
            else:
                note_stock_idx = st.selectbox(
                    "종목", options=range(len(stock_opts)),
                    format_func=lambda i: stock_opts[i],
                    key="pw_note_stock",
                )
        else:
            note_stock_idx = None
    # 기존 메모 로드
    existing_note_text = ""
    existing_notes_df = pd.DataFrame()
    if PAPER_WATCH_NOTES_PATH.exists():
        try:
            existing_notes_df = pd.read_csv(PAPER_WATCH_NOTES_PATH, encoding="utf-8-sig", dtype=str).fillna("")
        except Exception:  # noqa: BLE001
            existing_notes_df = pd.DataFrame()
    sel_code = ""
    sel_name = ""
    if note_date and note_stock_idx is not None:
        same_day = options_df[options_df["signal_date"].astype(str) == note_date].reset_index(drop=True)
        sel_row = same_day.iloc[note_stock_idx]
        sel_code = str(sel_row["stock_code"])
        sel_name = str(sel_row["stock_name"])
        if not existing_notes_df.empty:
            mask = (
                (existing_notes_df["signal_date"] == note_date)
                & (existing_notes_df["stock_code"] == sel_code)
            )
            if mask.any():
                existing_note_text = str(existing_notes_df.loc[mask, "note"].iloc[-1])
    note_text = st.text_area(
        "메모",
        value=existing_note_text,
        key=f"pw_note_text_{note_date}_{sel_code}",
        height=120,
        placeholder="예) 15시에 거래량 유지율 13%로 낮았지만 D0 종가 부근 지지 시도, 그러나 16:00 분봉에서 추가 매도세 — 다음 비슷한 패턴 주의.",
        label_visibility="collapsed",
    )
    with note_cols[3]:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        save_clicked = st.button("💾 저장", key="pw_note_save", use_container_width=True)
    if save_clicked:
        if not note_date or not sel_code:
            st.warning("신호일·종목을 선택해주세요.")
        elif not note_text.strip():
            st.warning("메모 내용이 비어있습니다.")
        else:
            try:
                PAPER_WATCH_NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
                new_row = {
                    "saved_at": datetime.now().isoformat(timespec="seconds"),
                    "signal_date": note_date,
                    "stock_code": sel_code,
                    "stock_name": sel_name,
                    "note": note_text.strip(),
                }
                if existing_notes_df.empty:
                    merged = pd.DataFrame([new_row])
                else:
                    mask = (
                        (existing_notes_df["signal_date"] == note_date)
                        & (existing_notes_df["stock_code"] == sel_code)
                    )
                    if mask.any():
                        for k, v in new_row.items():
                            existing_notes_df.loc[mask, k] = v
                        merged = existing_notes_df
                    else:
                        merged = pd.concat([existing_notes_df, pd.DataFrame([new_row])], ignore_index=True)
                merged.to_csv(PAPER_WATCH_NOTES_PATH, index=False, encoding="utf-8-sig")
                st.success(f"메모 저장 완료: {PAPER_WATCH_NOTES_PATH.name} ({note_date} {sel_name})")
            except Exception as exc:  # noqa: BLE001
                st.error(f"메모 저장 실패: {exc}")

    # 저장된 메모 목록 expander
    if not existing_notes_df.empty:
        with st.expander(f"📓 저장된 메모 ({len(existing_notes_df)}건)", expanded=False):
            st.dataframe(
                existing_notes_df[["saved_at", "signal_date", "stock_name", "stock_code", "note"]],
                use_container_width=True, hide_index=True, height=260,
            )

    src_dir = _eod_paper_watch_dir()
    if src_dir is not None:
        st.caption(
            f"데이터: `{src_dir}` · paper_watch_log.csv / paper_watch_manifest.json · "
            f"사용자 메모: `{PAPER_WATCH_NOTES_PATH}`"
        )


def render_eod_chart_learning_tab() -> None:
    """과거순 차트 학습 Step Replay — Codex chart_learning_replay 산출 활용.

    핵심 원칙:
    - 기본 정렬 과거순 (replay_order asc)
    - hide_outcome_default=True인 행은 결과 자동 숨김 + Step Replay 버튼으로 순차 공개
    - PENDING_LATEST / PARTIAL_MINUTE / ENTRY_OR_SIGNAL_MINUTE_INSUFFICIENT 상태는 강조 표시
    - D0 / 신호일 / Entry / 결과 / 사후 라벨을 시각적으로 분리
    """
    df = load_eod_chart_learning_replay()
    manifest = load_eod_chart_learning_manifest()

    st.markdown("### Chart Learning · 과거순 Step Replay")
    st.caption(
        "1년치 Bell Watch 후보를 과거순으로 한 명씩 펼치며 학습. "
        "결과는 기본 숨김 — 사용자가 단계별로 공개해 \"15시 시점 데이터로 맞췄는지\" 자기 평가."
    )

    if df.empty:
        st.info("chart_learning_replay.csv 데이터가 없습니다. Codex 산출 대기 중.")
        return

    # 숫자 변환
    for c in ("replay_order", "rank", "trading_day_age", "entry_1500_price",
              "signal_day_pct_change_1500", "signal_vs_d0_close_pct",
              "signal_vs_d0_high_pct", "signal_volume_retention_vs_d0",
              "rsi14_signal_1500", "risk_count"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # ── 상단 metric
    mcols = st.columns(5)
    mcols[0].metric("총 후보", f"{manifest.get('replay_rows', len(df))}")
    mcols[1].metric("최신 신호일", manifest.get("latest_signal_date") or "—")
    mcols[2].metric("entry 가용", f"{numeric(manifest.get('entry_1500_available_rate'), 0):.1f}%")
    mcols[3].metric("D+1 가용", f"{numeric(manifest.get('d1_outcome_available_rate'), 0):.1f}%")
    mcols[4].metric("Status", manifest.get("overall_status") or "—")

    # ── 필터/정렬
    fcols = st.columns([1.3, 1.3, 1.3, 1.3, 1.8])
    with fcols[0]:
        order = st.radio("정렬", ["과거순", "최신순"], horizontal=True, key="cl_sort")
    with fcols[1]:
        d1_opts = ["전체"] + sorted([x for x in df["d1_label"].dropna().unique() if x])
        d1_filter = st.selectbox("D+1 라벨", d1_opts, key="cl_d1")
    with fcols[2]:
        h5_opts = ["전체"] + sorted([x for x in df["h5_label"].dropna().unique() if x])
        h5_filter = st.selectbox("H5 라벨", h5_opts, key="cl_h5")
    with fcols[3]:
        cs_opts = ["전체"] + sorted([x for x in df["chart_status"].dropna().unique() if x])
        cs_filter = st.selectbox("Chart Status", cs_opts, key="cl_cs")
    with fcols[4]:
        name_q = st.text_input("종목 검색", key="cl_name", placeholder="이름 또는 코드")

    view = df.copy()
    if d1_filter != "전체":
        view = view[view["d1_label"] == d1_filter]
    if h5_filter != "전체":
        view = view[view["h5_label"] == h5_filter]
    if cs_filter != "전체":
        view = view[view["chart_status"] == cs_filter]
    if name_q:
        q = name_q.strip()
        view = view[
            view["stock_name"].astype(str).str.contains(q, case=False, na=False)
            | view["stock_code"].astype(str).str.contains(q, na=False)
        ]
    view = view.sort_values("replay_order", ascending=(order == "과거순")).reset_index(drop=True)

    if view.empty:
        st.info("필터에 맞는 후보가 없습니다.")
        return

    # ── 현재 후보 인덱스 (session_state)
    idx_key = "cl_cur_idx"
    if idx_key not in st.session_state or st.session_state[idx_key] >= len(view):
        st.session_state[idx_key] = 0

    # ── 후보 nav
    nav_cols = st.columns([1, 4, 1])
    with nav_cols[0]:
        if st.button("◀ 이전", key="cl_prev", disabled=st.session_state[idx_key] == 0, use_container_width=True):
            st.session_state[idx_key] = max(0, st.session_state[idx_key] - 1)
    with nav_cols[2]:
        if st.button("다음 ▶", key="cl_next", disabled=st.session_state[idx_key] >= len(view) - 1, use_container_width=True):
            st.session_state[idx_key] = min(len(view) - 1, st.session_state[idx_key] + 1)
    with nav_cols[1]:
        # 후보 직접 선택 (replay_order + 종목명 + 신호일)
        opt_labels = [
            f"#{int(r['replay_order'])} · {r['signal_date'][:10]} · {r['stock_name']} ({r['stock_code']})"
            for _, r in view.iterrows()
        ]
        new_idx = st.selectbox(
            f"후보 ({st.session_state[idx_key] + 1} / {len(view)})",
            options=range(len(view)),
            format_func=lambda i: opt_labels[i],
            index=st.session_state[idx_key],
            key="cl_select",
            label_visibility="collapsed",
        )
        if new_idx != st.session_state[idx_key]:
            st.session_state[idx_key] = new_idx

    r = view.iloc[st.session_state[idx_key]]
    is_pending_latest = str(r.get("chart_status", "")) == "PENDING_LATEST"
    is_data_warning = str(r.get("chart_status", "")) in (
        "PARTIAL_MINUTE", "ENTRY_OR_SIGNAL_MINUTE_INSUFFICIENT"
    )

    # ── 헤더 영역 (분리 표시: 종목 · D0 · 신호일 · Entry)
    st.markdown("---")
    head_cols = st.columns([2, 2, 2, 2])
    with head_cols[0]:
        st.markdown(f"#### {r.get('stock_name', '')}")
        st.caption(f"{r.get('stock_code', '')} · 후보 #{int(r.get('replay_order', 0))}")
    with head_cols[1]:
        st.metric("D0 등록일", str(r.get("d0_date", ""))[:10] or "—")
        try:
            age_int = int(r.get("trading_day_age"))
            st.caption(f"감시 D+{age_int}")
        except (TypeError, ValueError):
            pass
    with head_cols[2]:
        st.metric("신호일", str(r.get("signal_date", ""))[:10] or "—")
        st.caption("Bell Watch 15시 신호 기준")
    with head_cols[3]:
        ep = r.get("entry_1500_price")
        try:
            st.metric("Entry (15시)", f"{float(ep):,.0f}원")
        except (TypeError, ValueError):
            st.metric("Entry (15시)", "—")
        st.markdown(_chart_status_pill(r.get("chart_status", "")), unsafe_allow_html=True)

    # 데이터 결손 경고
    if is_data_warning:
        miss_reason = str(r.get("minute_missing_reason", "")).strip()
        st.warning(
            f"⚠️ **데이터 결손 후보** — {r.get('chart_status', '')}: "
            f"{miss_reason or '분봉 또는 결과 데이터 일부 누락'}. "
            "이 후보의 라벨/태그는 부분 데이터 기반이므로 해석에 주의."
        )

    # ── 15시 시점 지표 (신호일 시점 데이터 — 결과 공개와 분리)
    st.markdown("##### 15시 시점 지표 (결과 보기 전 단서)")
    sig_cols = st.columns(6)
    sig_pct = r.get("signal_day_pct_change_1500")
    close_gap = r.get("signal_vs_d0_close_pct")
    high_gap = r.get("signal_vs_d0_high_pct")
    vol_ret = r.get("signal_volume_retention_vs_d0")
    rsi_val = r.get("rsi14_signal_1500")
    risk_n = r.get("risk_count")
    sig_cols[0].metric("신호일 등락",
                       f"{float(sig_pct):+.1f}%" if pd.notna(sig_pct) else "—")
    sig_cols[1].metric("D0 종가대비",
                       f"{float(close_gap):+.1f}%" if pd.notna(close_gap) else "—")
    sig_cols[2].metric("D0 고가대비",
                       f"{float(high_gap):+.1f}%" if pd.notna(high_gap) else "—")
    sig_cols[3].metric("거래량 유지",
                       f"{float(vol_ret):.0f}%" if pd.notna(vol_ret) else "—")
    sig_cols[4].metric("RSI(14)",
                       f"{float(rsi_val):.0f}" if pd.notna(rsi_val) else "—")
    sig_cols[5].metric("위험 카운트",
                       f"{int(risk_n)}" if pd.notna(risk_n) else "—")

    # 위험 배지
    badges_text = str(r.get("badges", "")).strip()
    if badges_text and badges_text.lower() != "nan":
        st.markdown(
            f'<div style="margin:4px 0 12px;">{_eod_badge_pills(badges_text)}</div>',
            unsafe_allow_html=True,
        )

    reason_text = str(r.get("selection_reason_text", "")).strip()
    if reason_text and reason_text.lower() != "nan":
        st.caption(f"💡 선정이유: {reason_text}")

    # ── 결과 영역 (Step Replay — 사용자가 직접 공개)
    st.markdown("---")
    st.markdown("##### 결과 · 사후 라벨 (Step Replay)")
    if is_pending_latest:
        st.info(
            "📅 **paper watch 대기** — 오늘 신호일 후보. D+1·H5 결과가 아직 확정되지 않았습니다. "
            "결과는 D+1 영업일이 끝난 후 자동 갱신됩니다."
        )
    else:
        d1_avail = str(r.get("d1_reveal_available", "True")).lower() not in ("false", "0", "no", "")
        h5_avail = str(r.get("h5_reveal_available", "True")).lower() not in ("false", "0", "no", "")
        reveal_key = f"cl_reveal_{int(r.get('replay_order', 0))}"
        if reveal_key not in st.session_state:
            st.session_state[reveal_key] = {"d1": False, "h5": False}

        step_cols = st.columns([1, 1, 2])
        with step_cols[0]:
            if st.button(
                "D+1 결과 공개", key=f"cl_reveal_d1_{int(r.get('replay_order', 0))}",
                disabled=not d1_avail or st.session_state[reveal_key]["d1"],
                use_container_width=True,
            ):
                st.session_state[reveal_key]["d1"] = True
        with step_cols[1]:
            if st.button(
                "H5 결과 공개", key=f"cl_reveal_h5_{int(r.get('replay_order', 0))}",
                disabled=not h5_avail or not st.session_state[reveal_key]["d1"]
                         or st.session_state[reveal_key]["h5"],
                use_container_width=True,
                help="D+1 결과를 먼저 공개해야 H5 공개 가능 (Step Replay).",
            ):
                st.session_state[reveal_key]["h5"] = True
        with step_cols[2]:
            if st.button(
                "↺ 다시 숨기기", key=f"cl_hide_{int(r.get('replay_order', 0))}",
                use_container_width=True,
            ):
                st.session_state[reveal_key] = {"d1": False, "h5": False}

        # D+1 공개
        if st.session_state[reveal_key]["d1"]:
            d1_label = str(r.get("d1_label", ""))
            st.markdown(
                f'**D+1 라벨**: {_paper_watch_label_pill(d1_label)}',
                unsafe_allow_html=True,
            )
        else:
            st.caption("⬛ D+1 결과 비공개")

        # H5 공개
        if st.session_state[reveal_key]["h5"]:
            h5_label = str(r.get("h5_label", ""))
            st.markdown(
                f'**H5 라벨**: {_paper_watch_label_pill(h5_label)}',
                unsafe_allow_html=True,
            )
            # 사후 해석 태그 (성공/실패)
            success_tags = str(r.get("retro_success_tags", "")).strip()
            fail_tags = str(r.get("retro_fail_tags", "")).strip()
            if success_tags and success_tags.lower() != "nan":
                st.markdown(
                    f'<div style="margin-top:8px; color:#166534;">✅ 성공 해석 태그: '
                    f'<b>{success_tags.replace("|", " · ")}</b></div>',
                    unsafe_allow_html=True,
                )
            if fail_tags and fail_tags.lower() != "nan":
                st.markdown(
                    f'<div style="margin-top:4px; color:#991b1b;">⚠ 실패/주의 해석 태그: '
                    f'<b>{fail_tags.replace("|", " · ")}</b></div>',
                    unsafe_allow_html=True,
                )
        elif st.session_state[reveal_key]["d1"]:
            st.caption("⬛ H5 결과 비공개 (D+1을 본 뒤 공개 가능)")

    src_dir = _eod_paper_watch_dir()
    if src_dir is not None:
        st.caption(f"데이터: `{src_dir}` · chart_learning_replay.csv")


def render_daily3_pool_preview() -> None:
    """Daily3 소액 pool preview. 운영 latest/webhook/scheduler는 교체하지 않는다."""
    manifest = load_daily3_pool_manifest()
    candidates = load_daily3_pool_csv("daily3_pool_candidates_1y.csv")
    summary = load_daily3_pool_csv("daily3_pool_summary.csv")
    tier = load_daily3_pool_csv("daily3_pool_tier_summary.csv")

    st.markdown("### 🧪 Daily3 소액 Pool Preview")
    st.caption("실제 발송 아님 · 운영 스케줄러 미교체 · 날짜별 3후보를 눈으로 확인하기 위한 preview입니다.")

    if candidates.empty:
        st.info(f"Daily3 preview 데이터가 없습니다. 경로: `{DAILY3_POOL_PREVIEW_DIR}`")
        return

    dates = sorted(candidates["signal_date"].astype(str).str[:10].dropna().unique().tolist())
    latest_date = str(manifest.get("latest_signal_date") or (dates[-1] if dates else ""))[:10]
    metric_cols = st.columns(5)
    metric_cols[0].metric("Preview 최신일", latest_date or "—")
    metric_cols[1].metric("1년 거래일", manifest.get("signal_days", len(dates)))
    metric_cols[2].metric("후보 수", manifest.get("candidate_rows", len(candidates)))
    if not summary.empty:
        s = summary.iloc[0].to_dict()
        metric_cols[3].metric("D+1 +1 touch", f"{numeric(s.get('d1_plus1_touch_rate'), 0):.1f}%")
        metric_cols[4].metric("D+1 -2 touch", f"{numeric(s.get('d1_minus2_touch_rate'), 0):.1f}%")
    else:
        metric_cols[3].metric("D+1 +1 touch", "—")
        metric_cols[4].metric("D+1 -2 touch", "—")
    watch_status = (manifest.get("validation") or {}).get("watch_period_status", "")
    if watch_status == "D0_ONLY":
        st.warning("현재 Daily3 preview는 모든 후보가 `trading_day_age=0`인 D0 당일형입니다. 기존 BellGuard식 3거래일 감시 대체는 아직 아닙니다.")

    selected_date = st.selectbox(
        "Preview 날짜",
        dates,
        index=(dates.index(latest_date) if latest_date in dates else max(len(dates) - 1, 0)),
        key="daily3_pool_preview_date",
    )
    rows = candidates[candidates["signal_date"].astype(str).str[:10] == selected_date].copy()
    rows["rank_num"] = pd.to_numeric(rows.get("rank_final", 0), errors="coerce").fillna(0).astype(int)
    rows = rows.sort_values("rank_num")

    card_cols = st.columns(3)
    tier_color = {"S": "#059669", "A": "#2563eb", "B": "#7c3aed", "C": "#d97706", "D": "#dc2626"}
    for i, (_, r) in enumerate(rows.iterrows()):
        row = r.to_dict()
        tier_label = str(row.get("source_tier", "")).strip() or "?"
        color = tier_color.get(tier_label, "#64748b")
        with card_cols[i % 3]:
            st.markdown(
                f"""
<div style="border:1px solid #d6dae3; border-radius:8px; padding:14px 14px 12px; min-height:245px;">
  <div style="display:flex; justify-content:space-between; gap:8px; align-items:center;">
    <b>#{row.get('rank_final', '')} {row.get('stock_name', '')}</b>
    <span style="background:{color}; color:white; padding:2px 8px; border-radius:999px; font-size:0.82rem;">Tier {tier_label}</span>
  </div>
  <div style="color:#64748b; font-size:0.86rem; margin:4px 0 10px;">{normalize_code(row.get('stock_code', ''))} · {row.get('badge_text', '')}</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:7px; font-size:0.90rem;">
    <div><span style="color:#64748b;">15시가</span><br><b>{_daily3_money(row.get('entry_price_1500'))}</b></div>
    <div><span style="color:#64748b;">10만원 1주</span><br><b>{_daily3_bool(row.get('current_seed_100k_buyable'))}</b></div>
    <div><span style="color:#64748b;">D0</span><br><b>{row.get('d0_date', '')} / +{row.get('trading_day_age', '')}</b></div>
    <div><span style="color:#64748b;">신호일 등락</span><br><b>{_daily3_pct(row.get('signal_day_pct_change_1500'))}</b></div>
    <div><span style="color:#64748b;">D0 고가대비</span><br><b>{_daily3_pct(row.get('signal_vs_d0_high_pct'))}</b></div>
    <div><span style="color:#64748b;">거래량 유지</span><br><b>{_daily3_ratio(row.get('signal_volume_retention_vs_d0'))}</b></div>
    <div><span style="color:#64748b;">RSI14</span><br><b>{_daily3_pct(row.get('rsi14_signal_1500')).replace('%', '')}</b></div>
    <div><span style="color:#64748b;">모델</span><br><b>{row.get('source_model', '')}</b></div>
  </div>
  <div style="margin-top:12px; font-size:0.88rem; color:#334155;"><b>결과</b> · {_daily3_result_text(row, latest_date)}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    with st.expander("Daily3 tier 성과 요약", expanded=False):
        if tier.empty:
            st.info("tier summary 파일이 없습니다.")
        else:
            display_cols = [
                "source_tier",
                "source_model",
                "sample_n",
                "buyable_100k_rate",
                "d1_plus1_touch_rate",
                "d1_plus1_profit_protect_rate",
                "d1_minus2_touch_rate",
                "h5_plus2_touch_rate",
                "h5_minus2_touch_rate",
            ]
            st.dataframe(tier[[c for c in display_cols if c in tier.columns]], use_container_width=True, hide_index=True)
    st.caption(f"데이터: `{DAILY3_POOL_PREVIEW_DIR}` · 최신 후보의 D+ 결과는 확정 전에는 대기로 표시합니다.")
    # 1년 도달률 카드 4개 — manifest 우선, 없으면 placeholder
    def _kpi(key, fallback="—"):
        if main_kpi and key in main_kpi and main_kpi[key] is not None:
            return f"{float(main_kpi[key]):.1f}%"
        return fallback
    cols = st.columns(4)
    cards = [
        ("🟢 강세 (GREEN)", _kpi("green_rate"), "D+1 저가·종가 모두 진입 위", "#16a34a"),
        ("🔴 약세 (RED)",  _kpi("red_rate"),   "D+1 진입 위로 한 번도 못 감", "#dc2626"),
        ("+3% 먼저 도달", _kpi("plus3_first_rate"), "5일 안에 +3을 -3보다 먼저", "#16a34a"),
        ("-3% 먼저 도달", _kpi("minus3_first_rate"), "5일 안에 -3을 +3보다 먼저", "#f97316"),
    ]
    for col, (h, val, sub, c) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="cb-info-card">'
                f'<div class="cb-key" style="margin-bottom:6px;">{h}</div>'
                f'<div style="font-size:2rem; font-weight:800; color:{c}; line-height:1.1;">{val}</div>'
                f'<div class="cb-key" style="margin-top:6px; font-size:0.82rem;">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    # 하락 도달률 (안정성) — manifest 우선
    st.markdown("#### 큰 손실은 얼마나 자주 오는가 (낮을수록 좋음)")
    cols2 = st.columns(3)
    downs = [
        ("-3% 도달", _kpi("minus3_touch_rate"), "5일 안 한 번이라도 -3% 아래", "#f97316"),
        ("-5% 도달", _kpi("minus5_touch_rate"), "5일 안 한 번이라도 -5% 아래", "#f97316"),
        ("-10% 도달", _kpi("minus10_touch_rate", _kpi("minus5_touch_rate")), "5일 안 한 번이라도 -10% 아래", "#16a34a"),
    ]
    for col, (h, val, sub, c) in zip(cols2, downs):
        with col:
            st.markdown(
                f'<div class="cb-info-card">'
                f'<div class="cb-key" style="margin-bottom:6px;">{h}</div>'
                f'<div style="font-size:1.6rem; font-weight:700; color:{c}; line-height:1.1;">{val}</div>'
                f'<div class="cb-key" style="margin-top:6px; font-size:0.82rem;">{sub}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    # 보는 법
    with st.expander("📖 처음 보시는 분 — 신호등과 보는 법", expanded=False):
        st.markdown(
            """
<div style="font-size:1.05rem; line-height:1.75; color:#0f172a;">
  <div style="font-size:1.15rem; font-weight:700; margin:4px 0 10px;">신호등 5색 의미</div>
  <table style="font-size:1.05rem; line-height:1.7; border-collapse:collapse; margin-bottom:14px;">
    <thead>
      <tr style="background:#f8fafc;">
        <th style="text-align:left; padding:6px 14px; border-bottom:1px solid #e5e7eb;">색</th>
        <th style="text-align:left; padding:6px 14px; border-bottom:1px solid #e5e7eb;">이름</th>
        <th style="text-align:left; padding:6px 14px; border-bottom:1px solid #e5e7eb;">설명</th>
      </tr>
    </thead>
    <tbody>
      <tr><td style="padding:5px 14px; font-size:1.2rem;">🟢</td><td style="padding:5px 14px; font-weight:600;">강세</td><td style="padding:5px 14px;">위로 먼저 가고 잘 버팀</td></tr>
      <tr><td style="padding:5px 14px; font-size:1.2rem;">🟡</td><td style="padding:5px 14px; font-weight:600;">회복</td><td style="padding:5px 14px;">아래로 흔들렸다 다시 위로 회복</td></tr>
      <tr><td style="padding:5px 14px; font-size:1.2rem;">🟠</td><td style="padding:5px 14px; font-weight:600;">실패</td><td style="padding:5px 14px;">위로 시도했지만 종가 약함</td></tr>
      <tr><td style="padding:5px 14px; font-size:1.2rem;">🔴</td><td style="padding:5px 14px; font-weight:600;">약세</td><td style="padding:5px 14px;">아래로 먼저 깨지는 형</td></tr>
      <tr><td style="padding:5px 14px; font-size:1.2rem;">⚪</td><td style="padding:5px 14px; font-weight:600;">보류</td><td style="padding:5px 14px;">변동 거의 없음 / 데이터 부족</td></tr>
    </tbody>
  </table>
  <div style="font-size:1.15rem; font-weight:700; margin:14px 0 8px;">15시 판단 5단계</div>
  <ol style="font-size:1.05rem; line-height:1.75; padding-left:22px; margin:0 0 12px;">
    <li>오늘의 벨가드 Top3와 신호등을 본다.</li>
    <li>🟢🟡 비중과 🔴 경고를 확인한다.</li>
    <li>차트(일봉·분봉·이평선)를 직접 본다.</li>
    <li>급하게 전부 사지 않고 손절 위치부터 정한다.</li>
    <li>사전 느낌을 메모하고 다음날 사후 비교한다.</li>
  </ol>
  <blockquote style="font-size:1.0rem; color:#475569; border-left:3px solid #94a3b8; padding:6px 12px; margin:10px 0 0; background:#f8fafc;">
    <b>도달률은 "이렇게 갈 확률"이지 "이렇게 간다"가 아닙니다. 매번 차트 직접 확인이 필요합니다.</b>
  </blockquote>
</div>
""",
            unsafe_allow_html=True,
        )


def render_today_tab(
    *,
    online: bool,
    d0_pool: pd.DataFrame | None = None,
    score: pd.DataFrame | None = None,
    picks: pd.DataFrame | None = None,
    scan: dict[str, Any] | None = None,
) -> None:
    """오늘 탭 — Bell Watch main route + legacy records."""
    st.markdown(
        '<div class="cb-note" style="border-left-color:#10b981; background:rgba(16,185,129,0.08);">'
        '<b>투자 권유가 아닙니다.</b> Paper Watch / 수동 복기 화면입니다. '
        '메인 표시는 Bell Watch이며 기존 BellGuard/V2/Daily3는 비교·기록용으로 보존합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    # 1) Bell Watch main route
    render_eod_active_watch_preview()

    st.markdown("---")
    render_bell_v3_consensus_research()

    st.markdown("---")
    with st.expander("기존 BellGuard 기록 후보", expanded=False):
        render_today_hybrid_shadow()
    st.caption("Daily3 D0_ONLY와 V2 기록 화면은 연구/복기 탭에 보존되어 있으며, 오늘 메인 후보에는 사용하지 않습니다.")
    # V2 기록후보 표시는 제거. 데이터는 v2_record_1y/ 폴더에 그대로 보존.


def render_replay_tab(
    *,
    online: bool,
    score: pd.DataFrame | None = None,
    enriched: pd.DataFrame | None = None,
) -> None:
    """복기 탭 — 신호등표 + 종목 상세 중심.

    매일 보는 화면은 날짜별 신호등표와 종목 상세만 1차 탭에 노출한다.
    사후 라벨과 Chart Learning은 내부 기록 함수/데이터로만 보존하고 화면에서는 호출하지 않는다.
    기존 render_prev_close_color_review (1개월·V2 혼합)는 호출에서 제외, 함수는 보존.
    """
    _ = (online, score, enriched)
    sub_tabs = st.tabs(["날짜별 신호등표", "종목 상세"])
    with sub_tabs[0]:
        render_bellguard_signal_table()
    with sub_tabs[1]:
        render_security_detail()
    # render_prev_close_color_review / render_one_year_backdata / render_v2_hybrid_signal_board 는
    # render_eod_paper_watch_tab / render_eod_chart_learning_tab 과 함께 함수 정의는 보존,
    # 호출에서만 제외.


def render_lab_tab(*, online: bool) -> None:
    """연구실 탭 — Sweet Spot, 눌림, 패턴실험실, 차트검증, 통계."""
    st.markdown(
        '<div class="cb-note" style="border-left-color:#94a3b8;">'
        '연구·실험 화면. 일반 사용에는 필요 없고, 패턴 탐색이나 통계 검증이 필요할 때만 열어 보세요.'
        '</div>',
        unsafe_allow_html=True,
    )
    if online:
        sub_tabs = st.tabs(["🎯 Sweet Spot", "🔁 눌림 회복"])
        with sub_tabs[0]:
            render_v2_sweetspot_research()
        with sub_tabs[1]:
            render_v2_pullback_reclaim()
        return

    sub_tabs = st.tabs([
        "🎯 Sweet Spot",
        "🧪 전날 패턴 실험실",
        "🔁 눌림 회복",
        "🔬 V2 차트 검증",
        "📊 통계",
    ])
    with sub_tabs[0]:
        render_v2_sweetspot_research()
    with sub_tabs[1]:
        render_whole_market_pattern_lab()
    with sub_tabs[2]:
        render_v2_pullback_reclaim()
    with sub_tabs[3]:
        render_v2_chart_audit()
    with sub_tabs[4]:
        render_stats()


# ─────────────────────────────────────────────────────────────────────────────
# Bell Watch 수동검증 (read-only, Codex 2026-05-26 핸드오프 §1~§6)
# 자동매매/투자권유 아님. 운영 산식·웹훅·스케줄러 미접촉.
# ─────────────────────────────────────────────────────────────────────────────

def _bell_watch_mtime_ns(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return 0


@st.cache_data(show_spinner=False)
def _load_bell_watch_csv_cached(
    path_text: str,
    mtime_ns: int,
    parse_signal_date: bool = False,
) -> pd.DataFrame:
    path = Path(path_text)
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        if parse_signal_date and "signal_date" in df.columns:
            df["signal_date"] = pd.to_datetime(df["signal_date"], errors="coerce")
        return df
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def _load_bell_watch_json_cached(path_text: str, mtime_ns: int) -> dict[str, Any]:
    path = Path(path_text)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return {}


def load_bell_v3_consensus_csv(filename: str) -> pd.DataFrame:
    p = BELL_V3_CONSENSUS_DIR / filename
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_bell_v3_consensus_manifest() -> dict[str, Any]:
    p = BELL_V3_CONSENSUS_DIR / "manifest.json"
    return _load_bell_watch_json_cached(str(p), _bell_watch_mtime_ns(p))


def load_bell_v3_promotion_csv(filename: str) -> pd.DataFrame:
    p = BELL_V3_PROMOTION_DIR / filename
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_bell_v3_operational_csv(filename: str) -> pd.DataFrame:
    p = BELL_V3_OPERATIONAL_DIR / filename
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_bell_v3_operational_manifest() -> dict[str, Any]:
    p = BELL_V3_OPERATIONAL_DIR / "bell_v3_dashboard_bundle_manifest.json"
    return _load_bell_watch_json_cached(str(p), _bell_watch_mtime_ns(p))


def _v3_num(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or pd.isna(value):
            return default
        val = float(value)
        if pd.isna(val):
            return default
        return val
    except Exception:
        return default


def _v3_pct(value: Any) -> str:
    val = _v3_num(value)
    if val is None:
        return "-"
    return f"{val:.2f}%"


def _v3_score(value: Any) -> str:
    val = _v3_num(value)
    if val is None:
        return "-"
    return f"{val:.2f}"


def _v3_bool(value: Any) -> bool:
    text = str(value).strip().lower()
    return text in {"true", "1", "1.0", "y", "yes"}


def _v3_code(value: Any) -> str:
    text = str(value or "").strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(6) if text else ""


def _v3_sources(row: pd.Series) -> str:
    mapping = [
        ("in_eod_active_top3", "EOD"),
        ("in_v2_hybrid_top3", "V2"),
        ("in_eod_human_proxy_a", "Human"),
        ("in_eod_mechanical_top1", "EOD Top1"),
        ("in_daily3_pool_top3", "Daily3"),
        ("in_p0_trading_value_top3", "P0"),
        ("in_legacy_classic_webhook_top3", "Legacy"),
        ("in_v2_record_top3", "V2 record"),
        ("in_bellguard_pricecap_top3", "Pricecap"),
        ("in_bellguard_d0_strict_top3", "D0 strict"),
    ]
    labels = [label for col, label in mapping if col in row.index and _v3_bool(row[col])]
    return ", ".join(labels) if labels else "-"


def render_bell_v3_operational_switch_panel() -> None:
    manifest = load_bell_v3_operational_manifest()
    latest = load_bell_v3_operational_csv("bell_v3_operational_latest_top3.csv")
    freshness = load_bell_v3_operational_csv("bell_v3_source_freshness.csv")
    fallback = load_bell_v3_operational_csv("bell_v3_fallback_audit.csv")

    if not manifest and latest.empty and freshness.empty:
        return

    source_status = str(manifest.get("source_freshness", "UNKNOWN")).upper() if isinstance(manifest, dict) else "UNKNOWN"
    active_variant = str(manifest.get("active_variant", "-")) if isinstance(manifest, dict) else "-"
    fallback_route = str(manifest.get("fallback_route", "-")) if isinstance(manifest, dict) else "-"
    raw_allowed = manifest.get("operational_switch_allowed_now", False) if isinstance(manifest, dict) else False
    switch_allowed = raw_allowed if isinstance(raw_allowed, bool) else _v3_bool(raw_allowed)
    latest20_eod_only = "-"
    if not fallback.empty and "latest20_all_eod_only_day_rate_pct" in fallback.columns:
        value = pd.to_numeric(fallback["latest20_all_eod_only_day_rate_pct"], errors="coerce").dropna()
        if not value.empty:
            latest20_eod_only = f"{value.iloc[-1]:.2f}%"

    with st.expander("V3 Operational Switch QA", expanded=True):
        if switch_allowed:
            st.success("V3 operational switch is allowed by the current QA bundle.")
        elif source_status == "FAIL":
            st.error("V3 operational route switch is blocked: source freshness failed. Dashboard and webhook should stay on the fallback route.")
        else:
            st.warning("V3 operational route switch is not allowed yet. Keep this bundle in shadow/read-only mode.")

        cols = st.columns(4)
        cols[0].metric("Source freshness", source_status)
        cols[1].metric("Active variant", active_variant)
        cols[2].metric("Latest20 EOD-only", latest20_eod_only)
        cols[3].metric("Switch allowed", "YES" if switch_allowed else "NO")
        st.caption(f"Fallback route: `{fallback_route}`")

        if not latest.empty:
            show_cols = [
                "signal_date",
                "rank",
                "stock_code",
                "stock_name",
                "v3_total_score",
                "v3_grade",
                "consensus_sources",
                "fallback_used",
                "fallback_reason",
                "data_quality_flag",
            ]
            st.dataframe(latest[[c for c in show_cols if c in latest.columns]], use_container_width=True, hide_index=True)

        if not freshness.empty and "status" in freshness.columns:
            stale = freshness[freshness["status"].astype(str).str.upper().ne("OK")]
            if not stale.empty:
                stale_cols = ["source_name", "date_max", "latest_date_rows", "status", "note"]
                st.markdown("#### Blocked sources")
                st.dataframe(stale[[c for c in stale_cols if c in stale.columns]], use_container_width=True, hide_index=True)


def render_bell_v3_consensus_research() -> None:
    manifest = load_bell_v3_consensus_manifest()
    selected = load_bell_v3_consensus_csv("bell_v3_consensus_selected_top3.csv")
    overall = load_bell_v3_consensus_csv("bell_v3_consensus_summary_overall.csv")
    rolling = load_bell_v3_consensus_csv("bell_v3_consensus_summary_rolling.csv")
    score_detail = load_bell_v3_consensus_csv("bell_v3_consensus_score_detail.csv")
    outlier = load_bell_v3_consensus_csv("bell_v3_consensus_outlier_audit.csv")
    gates = load_bell_v3_promotion_csv("bell_v3_promotion_readiness_gates.csv")
    freshness = load_bell_v3_promotion_csv("bell_v3_source_freshness.csv")
    latest20 = load_bell_v3_promotion_csv("bell_v3_latest20_source_composition.csv")
    threshold_matrix = load_bell_v3_promotion_csv("bell_v3_promotion_d1_d5_threshold_matrix.csv")
    overlap_metrics = load_bell_v3_promotion_csv("bell_v3_eod_overlap_strategy_metrics.csv")

    st.markdown("### V3 Hybrid Consensus 연구")
    st.caption("V3 Consensus는 연구용 종합 후보입니다. 현재 운영 웹훅 선정식에는 아직 반영되지 않았습니다.")
    render_bell_v3_operational_switch_panel()

    if selected.empty or overall.empty:
        st.info(f"V3 consensus 데이터가 없습니다. 경로: `{BELL_V3_CONSENSUS_DIR}`")
        return

    validation = manifest.get("validation", {}) if isinstance(manifest, dict) else {}
    if not gates.empty:
        fail_rows = gates[gates["status"].astype(str).str.upper().eq("FAIL")]
        if fail_rows.empty:
            st.success("V3 승격 게이트: FAIL 없음. 그래도 운영 전환 전에는 병렬 검증을 유지합니다.")
        else:
            fail_text = " / ".join(fail_rows["gate"].astype(str).tolist())
            st.warning(f"V3 승격 게이트 FAIL: {fail_text}. 현재는 연구/병렬 표시 단계입니다.")
        with st.expander("승격 게이트 상세", expanded=False):
            st.dataframe(gates, use_container_width=True, hide_index=True)

    if not freshness.empty or not latest20.empty:
        warn_cols = st.columns(2)
        with warn_cols[0]:
            st.markdown("#### Source freshness")
            if freshness.empty:
                st.caption("source freshness 파일이 없습니다.")
            else:
                core = freshness[freshness["source"].astype(str).isin(["EOD Active", "V2 Hybrid", "Human Proxy", "Daily3", "P0"])]
                st.dataframe(
                    core[["source", "date_max", "latest_date_rows", "freshness_status", "stale_calendar_days_vs_eod_latest"]],
                    use_container_width=True,
                    hide_index=True,
                    height=210,
                )
        with warn_cols[1]:
            st.markdown("#### Latest 20 composition")
            if latest20.empty:
                st.caption("latest20 composition 파일이 없습니다.")
            else:
                focus_latest = latest20[latest20["v3_variant"].astype(str).isin(["V3_D_V2_CONFIRM", "V3_C_RISK_CONTROL"])]
                st.dataframe(
                    focus_latest[
                        [
                            "v3_variant",
                            "all_eod_only_day_rate_pct",
                            "days_with_any_v2_rate_pct",
                            "days_with_any_human_rate_pct",
                            "avg_eod_count",
                            "avg_v2_count",
                            "avg_human_count",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                    height=210,
                )

    variants = sorted([str(v) for v in selected["v3_variant"].dropna().unique()])
    default_variant = "V3_D_V2_CONFIRM" if "V3_D_V2_CONFIRM" in variants else variants[0]
    dates = sorted([str(d)[:10] for d in selected["signal_date"].dropna().unique()], reverse=True)

    control_cols = st.columns([1.6, 1.1, 1.1, 1.2])
    with control_cols[0]:
        variant = st.selectbox("Variant", variants, index=variants.index(default_variant), key="v3_consensus_variant")
    with control_cols[1]:
        signal_date = st.selectbox("Signal date", dates, index=0, key="v3_consensus_signal_date")

    overall_variant = overall[overall["v3_variant"].astype(str).eq(variant)]
    best = overall.sort_values("plus13_before_minus2_d5_rate_pct", ascending=False, na_position="last").head(1)
    with control_cols[2]:
        st.metric("Top3 guard", str(validation.get("top3_bad_group_count", 0)))
    with control_cols[3]:
        best_label = best["v3_variant"].iloc[0] if not best.empty else "-"
        st.metric("Best first-touch", best_label)

    if not overall_variant.empty:
        ov = overall_variant.iloc[0]
        metric_cols = st.columns(5)
        metric_cols[0].metric("D5 rows", f"{int(_v3_num(ov.get('complete_d5_rows'), 0) or 0):,}")
        metric_cols[1].metric("D5 win", _v3_pct(ov.get("d5_close_win_rate_pct")))
        metric_cols[2].metric("+1.3 first", _v3_pct(ov.get("plus13_before_minus2_d5_rate_pct")))
        metric_cols[3].metric("D5 close avg", _v3_pct(ov.get("avg_d5_close_return_pct")))
        metric_cols[4].metric("D5 median", _v3_pct(ov.get("median_d5_close_return_pct")))

    day = selected[
        selected["v3_variant"].astype(str).eq(variant)
        & selected["signal_date"].astype(str).str[:10].eq(signal_date)
    ].copy()
    if not day.empty:
        day["_rank"] = pd.to_numeric(day["v3_rank"], errors="coerce")
        day = day.sort_values("_rank")
        table = pd.DataFrame(
            {
                "Rank": day["v3_rank"].map(lambda x: int(_v3_num(x, 0) or 0)),
                "Code": day["stock_code"].map(_v3_code),
                "Name": day["stock_name"].astype(str),
                "Score": day["total_score"].map(_v3_score),
                "Sources": day.apply(_v3_sources, axis=1),
                "Eval source": day["evaluation_source_model_key"].astype(str),
                "Data": day["data_quality_flag"].astype(str),
            }
        )
        st.dataframe(table, use_container_width=True, hide_index=True)

    with st.expander("점수 breakdown", expanded=False):
        if score_detail.empty:
            st.caption("score detail 파일이 없습니다.")
        else:
            sd = score_detail[
                score_detail["v3_variant"].astype(str).eq(variant)
                & score_detail["signal_date"].astype(str).str[:10].eq(signal_date)
            ].copy()
            if sd.empty:
                st.caption("선택 날짜의 score detail이 없습니다.")
            else:
                sd["_rank"] = pd.to_numeric(sd["v3_rank"], errors="coerce")
                sd = sd.sort_values(["selected_top3", "_rank", "total_score"], ascending=[False, True, False])
                cols = [
                    "v3_rank",
                    "stock_code",
                    "stock_name",
                    "selected_top3",
                    "total_score",
                    "consensus_score",
                    "rank_score",
                    "path_score",
                    "risk_control_score",
                    "market_condition_score",
                    "liquidity_score",
                    "manual_proxy_score",
                    "evaluation_source_model_key",
                    "data_quality_flag",
                ]
                view = sd[[c for c in cols if c in sd.columns]].head(40).copy()
                if "stock_code" in view.columns:
                    view["stock_code"] = view["stock_code"].map(_v3_code)
                st.dataframe(view, use_container_width=True, hide_index=True, height=420)

    tabs = st.tabs(["기간 성과", "최근 rolling", "승격 비교", "EOD 겹침", "outlier"])
    with tabs[0]:
        show_cols = [
            "v3_variant",
            "rows",
            "complete_d5_rows",
            "signal_days",
            "avg_d5_close_return_pct",
            "median_d5_close_return_pct",
            "d5_close_win_rate_pct",
            "plus13_touch_d1_rate_pct",
            "plus13_touch_d2_rate_pct",
            "plus13_touch_d3_rate_pct",
            "plus13_touch_d4_rate_pct",
            "plus13_touch_d5_rate_pct",
            "cumulative_plus13_touch_d5_rate_pct",
            "plus13_before_minus2_d5_rate_pct",
            "minus2_before_plus13_d5_rate_pct",
            "same_day_ambiguous_d5_rate_pct",
            "sample_status",
        ]
        st.dataframe(overall[[c for c in show_cols if c in overall.columns]], use_container_width=True, hide_index=True)
    with tabs[1]:
        if rolling.empty:
            st.caption("rolling summary 파일이 없습니다.")
        else:
            latest_asof = str(rolling["as_of_date"].max())[:10]
            roll = rolling[
                rolling["as_of_date"].astype(str).str[:10].eq(latest_asof)
                & rolling["period_key"].astype(str).isin(["ROLLING_20TD", "ROLLING_60TD", "ROLLING_120TD"])
            ]
            cols = [
                "v3_variant",
                "period_key",
                "as_of_date",
                "complete_d5_rows",
                "d5_close_win_rate_pct",
                "plus13_before_minus2_d5_rate_pct",
                "avg_d5_close_return_pct",
                "sample_status",
                "partial_window",
            ]
            st.dataframe(roll[[c for c in cols if c in roll.columns]], use_container_width=True, hide_index=True)
    with tabs[2]:
        if threshold_matrix.empty:
            st.caption("promotion threshold matrix 파일이 없습니다.")
        else:
            focus_labels = ["V3-D V2 확인", "V3-C 리스크", "현재 EOD웹훅 Top3", "EOD Top1", "EOD Top3", "V2 하이브리드"]
            tm = threshold_matrix[threshold_matrix["strategy_label"].astype(str).isin(focus_labels)]
            st.dataframe(tm, use_container_width=True, hide_index=True)
    with tabs[3]:
        if overlap_metrics.empty:
            st.caption("EOD overlap metrics 파일이 없습니다.")
        else:
            st.dataframe(overlap_metrics, use_container_width=True, hide_index=True)
    with tabs[4]:
        if outlier.empty:
            st.caption("outlier audit 파일이 없습니다.")
        else:
            st.dataframe(outlier, use_container_width=True, hide_index=True)

    st.caption(f"데이터: `{BELL_V3_CONSENSUS_DIR}`")


def load_bell_watch_asof_cards() -> pd.DataFrame:
    p = BELL_WATCH_ASOF_DIR / "bell_watch_asof_latest_cards.csv"
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_bell_watch_asof_manifest() -> dict[str, Any]:
    p = BELL_WATCH_ASOF_DIR / "manifest.json"
    return _load_bell_watch_json_cached(str(p), _bell_watch_mtime_ns(p))


def load_mvm_summary() -> pd.DataFrame:
    p = BELL_WATCH_MANUAL_VS_MECH_DIR / "bell_watch_manual_vs_mechanical_summary.csv"
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_mvm_by_recent_window() -> pd.DataFrame:
    p = BELL_WATCH_MANUAL_VS_MECH_DIR / "bell_watch_manual_vs_mechanical_by_recent_window.csv"
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_mvm_equity_curve() -> pd.DataFrame:
    p = BELL_WATCH_MANUAL_VS_MECH_DIR / "bell_watch_manual_vs_mechanical_equity_curve.csv"
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p), parse_signal_date=True)


def load_mvm_break_even() -> pd.DataFrame:
    p = BELL_WATCH_MANUAL_VS_MECH_DIR / "bell_watch_manual_pick_break_even.csv"
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


def load_mvm_manual_proxy_scores() -> pd.DataFrame:
    p = BELL_WATCH_MANUAL_VS_MECH_DIR / "bell_watch_manual_proxy_scores.csv"
    return _load_bell_watch_csv_cached(str(p), _bell_watch_mtime_ns(p))


# 전략 표시명/분류 라벨 (Codex 핸드오프 §4)
_MVM_STRATEGY_META: dict[str, dict[str, str]] = {
    "MECHANICAL_TOP1": {"label": "기계 Top1", "role": "비교 기준", "icon": "🤖"},
    "MECHANICAL_TOP2": {"label": "기계 Top2", "role": "분산 기준선", "icon": "🤖"},
    "MECHANICAL_TOP3": {"label": "기계 Top3", "role": "분산 기준선", "icon": "🤖"},
    "HUMAN_PROXY_A": {"label": "수동 Proxy A", "role": "수동 체크리스트 보조", "icon": "🧠"},
    "HUMAN_PROXY_RISK_OFF": {"label": "수동 Risk-Off", "role": "방어형 위험 경고 배지 후보", "icon": "🛡"},
    "NO_TRADE_BAD_DAY_FILTER": {"label": "안 사는 날 필터", "role": "방어형 안 사는 날 보조", "icon": "🚫"},
    "BEST_OF_TOP3_ORACLE": {"label": "Best Oracle", "role": "참고 상한 (운영 불가)", "icon": "✨"},
    "WORST_OF_TOP3_ORACLE": {"label": "Worst Oracle", "role": "참고 하한 (운영 불가)", "icon": "💀"},
}

_MVM_PRIMARY_ORDER = [
    "MECHANICAL_TOP1",
    "MECHANICAL_TOP2",
    "MECHANICAL_TOP3",
    "HUMAN_PROXY_A",
    "HUMAN_PROXY_RISK_OFF",
    "NO_TRADE_BAD_DAY_FILTER",
]


def _asof_risk_badges(row: dict[str, Any]) -> list[tuple[str, str, str]]:
    """as-of 카드 → 위험 배지 (red/orange/gray)."""
    bits: list[tuple[str, str, str]] = []
    status = str(row.get("sample_status", "")).upper()
    if status in ("NO_LABELS", "LOW_SAMPLE"):
        bits.append(("표본 부족", "#f1f5f9", "#475569"))
    minus2_touch = numeric(row.get("cum_d5_minus2_touch_rate"))
    minus2_first = numeric(row.get("cum_d5_minus2_before_plus13_rate"))
    plus13_first = numeric(row.get("cum_d5_plus13_before_minus2_rate"))
    window_id = str(row.get("window_id", ""))
    # 최근 20거래일 -2 touch >= 80
    if window_id == "ROLLING_20TD" and minus2_touch is not None and minus2_touch >= 80:
        bits.append(("최근 난이도 높음", "#ffedd5", "#9a3412"))
    # 최근 20거래일 -2 우선이 +1.3 우선보다 큼
    if (
        window_id == "ROLLING_20TD"
        and minus2_first is not None
        and plus13_first is not None
        and minus2_first >= plus13_first
    ):
        bits.append(("-2 우선 주의 · 매수 축소 검토", "#fee2e2", "#991b1b"))
    return bits


def _render_asof_card(row: dict[str, Any]) -> None:
    """as-of 한 윈도우 카드."""
    label = row.get("window_label", row.get("window_id", "—"))
    n = numeric(row.get("n_d5_eligible_rows"))
    plus13_first = numeric(row.get("cum_d5_plus13_before_minus2_rate"))
    minus2_first = numeric(row.get("cum_d5_minus2_before_plus13_rate"))
    minus2_touch = numeric(row.get("cum_d5_minus2_touch_rate"))
    median_ret = numeric(row.get("median_ret_d5_close"))
    avg_mfe = numeric(row.get("cum_d5_avg_mfe_pct"))
    avg_mae = numeric(row.get("cum_d5_avg_mae_pct"))

    bits_html = ""
    badges = _asof_risk_badges(row)
    if badges:
        bits_html = "".join(
            f'<span style="background:{bg}; color:{fg}; padding:2px 8px; '
            f'border-radius:999px; font-size:0.74rem; font-weight:600; margin-right:4px;">{lbl}</span>'
            for lbl, bg, fg in badges
        )

    def _pct(v: float | None) -> str:
        return f"{v:.1f}%" if v is not None else "—"

    def _signed_pct(v: float | None) -> str:
        return f"{v:+.1f}%" if v is not None else "—"

    st.markdown(
        f"""
<div style="border:1px solid #e2e8f0; border-radius:8px; padding:10px 12px; background:#ffffff;">
  <div style="font-size:0.78rem; color:#64748b; margin-bottom:4px;">{label} (n={int(n) if n is not None else '—'})</div>
  <div style="display:flex; gap:14px; flex-wrap:wrap; align-items:baseline;">
    <div><span style="color:#475569; font-size:0.74rem;">+1.3 먼저</span> <b style="color:#15803d;">{_pct(plus13_first)}</b></div>
    <div><span style="color:#475569; font-size:0.74rem;">-2 먼저</span> <b style="color:#b91c1c;">{_pct(minus2_first)}</b></div>
    <div><span style="color:#475569; font-size:0.74rem;">-2 touch</span> <b>{_pct(minus2_touch)}</b></div>
    <div><span style="color:#475569; font-size:0.74rem;">D+5 종가 중앙값</span> <b>{_signed_pct(median_ret)}</b></div>
    <div><span style="color:#475569; font-size:0.74rem;">평균 MFE/MAE</span> <b>{_signed_pct(avg_mfe)} / {_signed_pct(avg_mae)}</b></div>
  </div>
  <div style="margin-top:6px;">{bits_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_mvm_strategy_card(row: dict[str, Any]) -> None:
    """기계 vs 수동 비교 한 전략 카드."""
    strat = str(row.get("strategy", ""))
    meta = _MVM_STRATEGY_META.get(strat, {"label": strat, "role": "—", "icon": "•"})
    buy_days = int(numeric(row.get("buy_days"), 0))
    no_trade = int(numeric(row.get("no_trade_days"), 0))
    avg_h5 = numeric(row.get("avg_ret_h5_close"))
    med_h5 = numeric(row.get("median_ret_h5_close"))
    win = numeric(row.get("h5_close_win_rate"))
    mdd = numeric(row.get("h5_close_mdd_pct"))
    plus13_first = numeric(row.get("d1_plus13_before_minus2_rate"))
    minus2_first = numeric(row.get("d1_minus2_before_plus13_rate"))
    best_hit = numeric(row.get("hit_best_of_top3_rate"))
    worst_hit = numeric(row.get("hit_worst_of_top3_rate"))

    avg_color = "#15803d" if (avg_h5 or 0) > 0 else "#b91c1c"

    def _pct(v: float | None) -> str:
        return f"{v:.1f}%" if v is not None else "—"

    def _signed_pct(v: float | None) -> str:
        return f"{v:+.2f}%" if v is not None else "—"

    st.markdown(
        f"""
<div style="border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; background:#ffffff; height:100%;">
  <div style="font-size:0.86rem; font-weight:600;">{meta['icon']} {meta['label']}</div>
  <div style="font-size:0.72rem; color:#64748b; margin-bottom:8px;">{meta['role']}</div>
  <div style="font-size:1.45rem; font-weight:700; color:{avg_color};">{_signed_pct(avg_h5)}</div>
  <div style="font-size:0.72rem; color:#475569; margin-bottom:8px;">평균 H5 종가 수익률 (중앙값 {_signed_pct(med_h5)})</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px 12px; font-size:0.78rem;">
    <div><span style="color:#64748b;">승률</span> <b>{_pct(win)}</b></div>
    <div><span style="color:#64748b;">MDD</span> <b style="color:#b91c1c;">{_signed_pct(mdd)}</b></div>
    <div><span style="color:#64748b;">+1.3 먼저</span> <b style="color:#15803d;">{_pct(plus13_first)}</b></div>
    <div><span style="color:#64748b;">-2 먼저</span> <b style="color:#b91c1c;">{_pct(minus2_first)}</b></div>
    <div><span style="color:#64748b;">매수일</span> <b>{buy_days}</b></div>
    <div><span style="color:#64748b;">노트레이드</span> <b>{no_trade}</b></div>
    <div><span style="color:#64748b;">best hit</span> <b>{_pct(best_hit)}</b></div>
    <div><span style="color:#64748b;">worst hit</span> <b>{_pct(worst_hit)}</b></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_bell_watch_manual_review_tab() -> None:
    """Bell Watch 수동검증 — read-only 연구/복기 화면.

    핸드오프 (2026-05-26) §1~§6 구현:
    §1 새 탭 안내 박스
    §2 장세 체력 카드 (asof_latest_cards)
    §3 오늘 Top3 수동 체크리스트 (webhook_top3_preview, session_state 메모)
    §4 기계 vs 수동 비교 카드 (manual_vs_mechanical_summary)
    §5 그래프 (equity_curve, by_recent_window)
    §6 CSV expander
    """
    # ── §1 안내 박스 ──
    st.markdown(
        '<div style="background:#fef3c7; border-left:4px solid #d97706; padding:10px 14px; '
        'border-radius:6px; margin:8px 0 14px; font-size:0.86rem; color:#78350f;">'
        '⚠️ <b>이 화면은 자동매매/투자권유가 아닙니다.</b> Bell Watch가 뽑은 Top3를 사람이 '
        '복기/연구할 때 참고하는 read-only 연구 화면입니다. 사후 결과 라벨은 오늘 카드와 분리됩니다. '
        '운영 산식·웹훅·스케줄러·주문/계좌 API는 일절 변경되지 않습니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ──────── §2 장세 체력 카드 ────────
    st.markdown("### 🩺 오늘 장세 체력 (as-of)")
    asof = load_bell_watch_asof_cards()
    asof_manifest = load_bell_watch_asof_manifest()
    if asof.empty:
        st.info(f"as-of 데이터 없음. 경로: `{BELL_WATCH_ASOF_DIR}`")
    else:
        latest_date = asof_manifest.get("effective_as_of_date") or asof["effective_as_of_date"].astype(str).max()
        st.caption(
            f"as-of 기준일: **{latest_date}** · 모델: BASELINE_EOD_VALUE_TOP3 · "
            "최근 구간 난이도가 높으면 매수 축소를 검토하는 보조 카드입니다."
        )
        window_order = ["EXPANDING", "ROLLING_120TD", "ROLLING_60TD", "ROLLING_20TD"]
        asof_sorted = asof.copy()
        asof_sorted["__o"] = asof_sorted["window_id"].map({w: i for i, w in enumerate(window_order)}).fillna(99)
        asof_sorted = asof_sorted.sort_values("__o")
        cols = st.columns(min(len(asof_sorted), 4))
        for i, (_, row) in enumerate(asof_sorted.iterrows()):
            with cols[i % len(cols)]:
                _render_asof_card(row.to_dict())

    st.markdown("---")

    # ──────── §3 오늘 Top3 수동 체크리스트 ────────
    st.markdown("### ✏️ 오늘 Top3 수동 체크리스트")
    st.caption(
        "오늘 Top3를 한눈에 보고 종목별 메모와 1순위/제외를 기록합니다. "
        "기록은 세션 메모리에만 저장되며 운영 산식/선정 순위에 반영되지 않습니다."
    )
    top3_df = load_eod_active_watch_csv("webhook_top3_preview.csv")
    if top3_df.empty:
        st.info("오늘 Top3 데이터 없음.")
    else:
        # 최신 신호일만 (signal_date가 가장 큰 값)
        top3_df["__sd"] = top3_df["signal_date"].astype(str).str[:10]
        latest_sd = top3_df["__sd"].max()
        latest_top3 = top3_df[top3_df["__sd"] == latest_sd].copy()
        latest_top3["__rank"] = pd.to_numeric(latest_top3.get("webhook_rank", latest_top3.get("rank_num", "")), errors="coerce")
        latest_top3 = latest_top3.sort_values("__rank")
        st.caption(f"신호일: **{latest_sd}** · {len(latest_top3)}건")

        check_cols = st.columns(min(len(latest_top3), 3) or 1)
        memo_records: list[dict[str, str]] = []
        for i, (_, row) in enumerate(latest_top3.iterrows()):
            code = str(row.get("stock_code", "—"))
            name = str(row.get("stock_name", "—"))
            rank_v = row.get("__rank", "—")
            try:
                rank_int = int(rank_v) if pd.notna(rank_v) else "—"
            except (TypeError, ValueError):
                rank_int = "—"
            key_base = f"bw_mr_{latest_sd}_{code}"
            with check_cols[i % len(check_cols)]:
                price = row.get("entry_1500_price", "—")
                try:
                    price_str = f"{float(price):,.0f}원"
                except (TypeError, ValueError):
                    price_str = "—"
                age = row.get("trading_day_age", "—")

                def _safe_pct(v: Any) -> str:
                    try:
                        return f"{float(v):+.1f}%" if pd.notna(v) and str(v).strip() else "—"
                    except (TypeError, ValueError):
                        return "—"

                def _safe_num_disp(v: Any, fmt: str = "{:.1f}") -> str:
                    try:
                        if pd.notna(v) and str(v).strip():
                            return fmt.format(float(v))
                    except (TypeError, ValueError):
                        pass
                    return "—"

                badge_txt = str(row.get("badge_text", "")).strip()
                st.markdown(
                    f"""
<div style="border:1px solid #cbd5e1; border-radius:8px; padding:10px 12px; background:#f8fafc;">
  <div style="font-size:0.94rem; font-weight:600;">{rank_int}. {name} ({code})</div>
  <div style="font-size:0.78rem; color:#475569; margin-bottom:6px;">{price_str} · 감시 D+{age}</div>
  <div style="font-size:0.78rem; line-height:1.6;">
    <span style="color:#64748b;">15시 등락</span> {_safe_pct(row.get('signal_day_pct_change_1500'))}<br>
    <span style="color:#64748b;">vs D0 종가</span> {_safe_pct(row.get('signal_vs_d0_close_pct'))} ·
    <span style="color:#64748b;">vs D0 고가</span> {_safe_pct(row.get('signal_vs_d0_high_pct'))}<br>
    <span style="color:#64748b;">거래량 유지</span> {_safe_num_disp(row.get('signal_volume_retention_vs_d0'))}% ·
    <span style="color:#64748b;">RSI</span> {_safe_num_disp(row.get('rsi14_signal_1500'))}<br>
    <span style="color:#64748b;">10만원 1주</span> {('Y' if str(row.get('current_seed_100k_buyable','')).lower() in ('true','1','yes','y') else 'N')}
  </div>
  <div style="font-size:0.72rem; color:#9a3412; margin-top:6px;">{badge_txt}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
                grade = st.selectbox(
                    "등급",
                    ["—", "A (강하게 검토)", "B (보통)", "C (약함)", "D (제외 검토)"],
                    key=f"{key_base}_grade",
                )
                pick = st.radio(
                    "오늘 선택",
                    ["—", "1순위", "2순위", "제외"],
                    horizontal=True,
                    key=f"{key_base}_pick",
                )
                reason = st.text_area(
                    "메모 (선택/제외 이유)",
                    height=80,
                    key=f"{key_base}_reason",
                )
                memo_records.append({
                    "signal_date": latest_sd,
                    "rank": str(rank_int),
                    "code": code,
                    "name": name,
                    "grade": str(grade),
                    "pick": str(pick),
                    "reason": str(reason).strip(),
                })

        # 다운로드 가능 CSV
        if memo_records:
            memo_df = pd.DataFrame(memo_records)
            csv_bytes = memo_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "💾 오늘 메모 CSV 다운로드 (세션 기록)",
                data=csv_bytes,
                file_name=f"bell_watch_manual_review_{latest_sd}.csv",
                mime="text/csv",
            )

    st.markdown("---")

    # ──────── §4 기계 vs 수동 비교 카드 ────────
    st.markdown("### ⚖️ 기계 vs 수동 비교 (누적)")
    mvm = load_mvm_summary()
    if mvm.empty:
        st.info(f"manual_vs_mechanical 데이터 없음. 경로: `{BELL_WATCH_MANUAL_VS_MECH_DIR}`")
    else:
        all_window = mvm[mvm["window_id"].astype(str) == "ALL"].copy()
        if all_window.empty:
            all_window = mvm.copy()
        # 주요 6개 전략을 카드로 (Oracle은 expander)
        primary_rows = []
        for strat in _MVM_PRIMARY_ORDER:
            sub = all_window[all_window["strategy"].astype(str) == strat]
            if not sub.empty:
                primary_rows.append(sub.iloc[0].to_dict())
        if primary_rows:
            be_df = load_mvm_break_even()
            be_map = {}
            if not be_df.empty:
                for _, br in be_df.iterrows():
                    be_map[str(br.get("metric", ""))] = numeric(br.get("value"))
            st.caption(
                f"비교 기간: 2025-04-02 ~ 2026-05-18 · 274 신호일 · "
                f"사람이 Top3 중 best를 골라야 하는 비율 · Top3 동일비중 대비 "
                f"**{be_map.get('best_pick_rate_needed_to_match_top3', 0):.1f}%** / "
                f"Top1 대비 **{be_map.get('best_pick_rate_needed_to_match_top1', 0):.1f}%**"
            )
            for chunk_start in range(0, len(primary_rows), 3):
                chunk = primary_rows[chunk_start:chunk_start + 3]
                ccols = st.columns(len(chunk))
                for i, row in enumerate(chunk):
                    with ccols[i]:
                        _render_mvm_strategy_card(row)

        with st.expander("✨💀 Oracle 참고 상한/하한 (운영 불가 · 사후 정답 기준)", expanded=False):
            oracle_rows = []
            for strat in ("BEST_OF_TOP3_ORACLE", "WORST_OF_TOP3_ORACLE"):
                sub = all_window[all_window["strategy"].astype(str) == strat]
                if not sub.empty:
                    oracle_rows.append(sub.iloc[0].to_dict())
            if oracle_rows:
                ocols = st.columns(len(oracle_rows))
                for i, row in enumerate(oracle_rows):
                    with ocols[i]:
                        _render_mvm_strategy_card(row)
            st.caption(
                "Oracle은 사후적으로 Top3 중 가장 좋은/나쁜 종목을 알았다고 가정한 결과로, "
                "사람이 얼마나 맞혀야 하는지의 참고 상한과 하한입니다. 실전 사용 불가."
            )

    st.markdown("---")

    # ──────── §5 그래프 ────────
    st.markdown("### 📈 자본곡선 · 최근 구간 비교")
    eq_df = load_mvm_equity_curve()
    if eq_df.empty:
        st.info("equity_curve 데이터 없음.")
    else:
        st.caption(
            "각 신호일 basket을 같은 paper unit으로 복리 비교한 연구용 자본곡선입니다. "
            "실제 5일 보유 겹침/현금제약 포트폴리오가 아닙니다. Oracle은 기본 제외."
        )
        # 주요 전략만 표시 (Oracle 제외)
        eq_primary = eq_df[eq_df["strategy"].astype(str).isin(_MVM_PRIMARY_ORDER)].copy()
        if not eq_primary.empty:
            pivot = eq_primary.pivot_table(
                index="signal_date",
                columns="strategy",
                values="equity_h5_close",
                aggfunc="last",
            ).sort_index()
            # strategy 라벨 친근하게
            pivot.columns = [_MVM_STRATEGY_META.get(c, {}).get("label", c) for c in pivot.columns]
            st.line_chart(pivot, height=320)

    by_win = load_mvm_by_recent_window()
    if not by_win.empty:
        st.markdown("##### 최근 윈도우별 평균 H5 종가 수익률")
        recent = by_win[by_win["window_id"].astype(str).isin(["RECENT_20_SIGNAL_DAYS", "RECENT_60_SIGNAL_DAYS", "RECENT_120_SIGNAL_DAYS"])].copy()
        recent = recent[recent["strategy"].astype(str).isin(_MVM_PRIMARY_ORDER)]
        if not recent.empty:
            recent["전략"] = recent["strategy"].map(lambda s: _MVM_STRATEGY_META.get(s, {}).get("label", s))
            recent["윈도우"] = recent["window_id"].map({
                "RECENT_20_SIGNAL_DAYS": "최근 20거래일",
                "RECENT_60_SIGNAL_DAYS": "최근 60거래일",
                "RECENT_120_SIGNAL_DAYS": "최근 120거래일",
            })
            pivot_recent = recent.pivot_table(
                index="윈도우",
                columns="전략",
                values="avg_ret_h5_close",
                aggfunc="first",
            ).reindex(["최근 20거래일", "최근 60거래일", "최근 120거래일"])
            st.bar_chart(pivot_recent, height=300)
        st.caption("최근 20거래일은 표본이 작으므로 운영 교체보다 경고 배지/수동 복기 보조로 해석합니다.")

    st.markdown("---")

    # ──────── §6 CSV expander ────────
    st.markdown("### 📁 상세 자료 (접힘)")

    with st.expander("상세: 전체 비교 요약 (manual_vs_mechanical_summary)", expanded=False):
        if not mvm.empty:
            st.dataframe(mvm, use_container_width=True, hide_index=True, height=300)

    with st.expander("상세: 최근 윈도우별 비교 (by_recent_window)", expanded=False):
        if not by_win.empty:
            st.dataframe(by_win, use_container_width=True, hide_index=True, height=300)

    with st.expander("상세: 수동 proxy 점수 (manual_proxy_scores)", expanded=False):
        ps = load_mvm_manual_proxy_scores()
        if not ps.empty:
            st.dataframe(ps.head(500), use_container_width=True, hide_index=True, height=300)
            st.caption(f"전체 {len(ps):,}건 중 상위 500건 표시.")
        else:
            st.info("manual_proxy_scores 데이터 없음.")

    with st.expander("상세: as-of 윈도우 audit", expanded=False):
        audit_p = BELL_WATCH_ASOF_DIR / "bell_watch_asof_window_audit.csv"
        if audit_p.exists():
            try:
                audit = pd.read_csv(audit_p, encoding="utf-8-sig")
                st.dataframe(audit.head(500), use_container_width=True, hide_index=True, height=300)
            except Exception as exc:  # noqa: BLE001
                st.info(f"window audit 로드 실패: {exc}")

    # 결론 박스
    st.markdown(
        '<div style="background:#f1f5f9; border-left:4px solid #475569; padding:10px 14px; '
        'border-radius:6px; margin-top:10px; font-size:0.84rem; color:#1e293b;">'
        '<b>실전 반영 분류</b>: 기계 Top1=비교 기준 · 기계 Top3=분산 기준선 · '
        '수동 Proxy A=수동 체크리스트 보조 · Risk-Off=방어형 위험 배지 후보 · '
        '안 사는 날 필터=방어형 보조 · Oracle=참고 상한/하한(운영 불가). '
        '운영 모델 교체 없음.'
        '</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    st.title("ClosingBell 수동 복기 대시보드")
    st.caption("읽기 전용 · 실전 주문 아님 · 자동매매 아님 · 수동 검토용")
    st.caption(
        "메인 표시: Bell Watch  ·  기존 BellGuard/V2/Daily3는 기록/비교용 보존  ·  현재일 후보에는 미래 결과 미노출"
    )

    # ── 온라인 (GitHub/Streamlit Cloud) 모드 ──
    if IS_ONLINE_MODE:
        st.markdown(
            '<div class="cb-note" style="border-left-color:#3b82f6; background:rgba(59,130,246,0.10);">'
            '🌐 <b>온라인 모드</b> — 큰 원본 데이터(일봉/분봉 parquet, DART) 미감지. '
            '경량 데이터 기반 4탭 화면을 표시합니다.'
            '</div>',
            unsafe_allow_html=True,
        )
        tabs = st.tabs(["오늘", "복기", "수동검증", "메모"])
        with tabs[0]:
            render_today_tab(online=True)
        with tabs[1]:
            render_replay_tab(online=True)
        with tabs[2]:
            render_bell_watch_manual_review_tab()
        with tabs[3]:
            render_notes_browser()
        return

    # ── 로컬 (풀 데이터) 모드 ──
    d0_pool = read_csv(str(D0_POOL_PATH))
    enriched = read_csv(str(ENRICHED_PATH))
    picks = read_csv(str(WEBHOOK_PICKS_PATH))
    score = read_csv(str(SCORE_PATH))
    scan = read_json(str(SECRET_SCAN_SUMMARY))

    tabs = st.tabs(["오늘", "복기", "수동검증", "메모"])
    with tabs[0]:
        render_today_tab(online=False, d0_pool=d0_pool, score=score, picks=picks, scan=scan)
    with tabs[1]:
        render_replay_tab(online=False, score=score, enriched=enriched)
    with tabs[2]:
        render_bell_watch_manual_review_tab()
    with tabs[3]:
        render_notes_browser()


if __name__ == "__main__":
    main()
