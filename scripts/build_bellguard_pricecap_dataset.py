"""BellGuard 가격필터 variant 1년 백데이터 생성기.

ChatGPT의 BELLGUARD_PRICECAP_REWORK_HANDOFF_20260517.md 지시 반영:
    - D0 후보군에 가격필터를 먼저 적용한 뒤 BellGuard 점수로 Top3
    - 4종 variant: 제한없음 / 100k / 50k / 30k
    - 일봉 raw에서 D+1~D+5 결과 직접 계산 (Mixed 케이스 재사용 불가)
    - 운영 산식·필터 변경 없음, 데이터 신규 생성만

입력:
    C:\\Coding\\data\\closingbell\\research_index\\bellguard_d0_source_audit_20260517\\
        d0_strict_bellguard_source_pool_scored_20260517.csv
    C:\\Coding\\data\\market\\daily_ohlcv\\{code}.parquet

출력:
    C:\\Coding\\projects\\bell-dashboard\\data\\closingbell\\online_v2\\latest\\bellguard_ui_review_1y\\
        bellguard_ui_review_signal_rows_1y.parquet
        bellguard_ui_review_signal_rows_1y.csv
        bellguard_ui_review_signal_by_date_1y.csv
        bellguard_ui_review_signal_day_summary_1y.csv
        bellguard_ui_review_signal_month_summary_1y.csv
        bellguard_ui_review_top3_latest.csv  (최신일 100k variant)
        bellguard_ui_review_latest_candidates_all.csv
        bellguard_ui_review_summary_1y.csv  (variant 비교 KPI)
        bellguard_ui_review_manifest.json

usage:
    & C:\\Coding\\projects\\_venvs\\closingbell-py312\\Scripts\\python.exe \\
      C:\\Coding\\projects\\bell-dashboard\\scripts\\build_bellguard_ui_review_dataset.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

# ─────────────────────────── 경로 / 상수 ───────────────────────────

REPO = Path(__file__).resolve().parents[1]
SRC_POOL_CSV = (
    Path(r"C:\Coding\data\closingbell\research_index")
    / "bellguard_d0_source_audit_20260517"
    / "d0_strict_bellguard_source_pool_scored_20260517.csv"
)
DAILY_DIR = Path(r"C:\Coding\data\market\daily_ohlcv")
STOCK_MAPPING = Path(r"C:\Coding\data\market\universe\stock_mapping.csv")

# ⚠️ 이 스크립트는 UI 검토용 보조 데이터셋 빌더입니다.
# 운영 active 데이터셋(bellguard_ui_review_1y)은 Codex 의
# C:\Coding\projects\bell-data\scripts\build_bellguard_ui_review_dashboard_20260517.py
# 만 갱신합니다. 이 스크립트는 그 결과를 **덮어쓰지 않습니다**.
OUT_DIR = REPO / "data" / "closingbell" / "online_v2" / "latest" / "bellguard_ui_review_1y"
OUT_PREFIX = "bellguard_ui_review"

# variant 정의
PRICECAP_VARIANTS = [
    ("none",  None,   "가격 제한 없음"),
    ("100k", 100_000, "100,000원 이하"),
    ("50k",   50_000, "50,000원 이하"),
    ("30k",   30_000, "30,000원 이하"),
]
MAIN_VARIANT_KEY = "100k"  # 사용자 선호: 10만원 이하 메인

# 신호등 (D+1 기준 단순)
def classify_light(d1_high_pct: float, d1_close_pct: float, d1_low_pct: float) -> str:
    """5색 신호등 — D+1 가격 흐름 기반.
    - GREEN: 저가가 D0 종가 위 + 종가가 D0 종가 위
    - YELLOW: 장중 D0 종가 깼지만 종가 D0 종가 위
    - ORANGE: 장중 D0 종가 위 갔지만 종가 D0 종가 아래
    - RED:   고가가 D0 종가 이하 + 종가 D0 종가 아래
    - GRAY:  데이터 없음
    """
    if any(pd.isna(x) for x in [d1_high_pct, d1_close_pct, d1_low_pct]):
        return "GRAY"
    if d1_low_pct >= 0 and d1_close_pct >= 0:
        return "GREEN"
    if d1_close_pct >= 0:
        return "YELLOW"
    if d1_high_pct >= 0:
        return "ORANGE"
    return "RED"


# ─────────────────────────── 데이터 로딩 ───────────────────────────

def load_source_pool() -> pd.DataFrame:
    if not SRC_POOL_CSV.exists():
        raise FileNotFoundError(f"Source pool not found: {SRC_POOL_CSV}")
    df = pd.read_csv(SRC_POOL_CSV, encoding="utf-8-sig")
    df["d0_date"] = df["d0_date"].astype(str)
    df["code"] = df["code"].astype(str).str.zfill(6)
    df["entry_price_hint"] = pd.to_numeric(df["entry_price_hint"], errors="coerce")
    df["bellguard_score"] = pd.to_numeric(df["bellguard_score"], errors="coerce")
    return df


def load_daily(code: str) -> pd.DataFrame:
    p = DAILY_DIR / f"{code}.parquet"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["date"] = df["date"].astype(str)
    return df


# 캐시 (반복 read 방지)
_DAILY_CACHE: dict[str, pd.DataFrame] = {}


def daily_cached(code: str) -> pd.DataFrame:
    if code not in _DAILY_CACHE:
        _DAILY_CACHE[code] = load_daily(code)
    return _DAILY_CACHE[code]


# ─────────────────────────── 결과 계산 ───────────────────────────

def compute_d1d5_outcomes(code: str, d0_date: str, entry_price: float) -> dict:
    """D+1~D+5 일봉으로 +1/+2/+3/+5/-1/-2/-3/-5 도달 및 first, max_gain/loss, d5_close 계산."""
    daily = daily_cached(code)
    if daily.empty or pd.isna(entry_price) or entry_price <= 0:
        return {}
    fut = daily[daily["date"] > d0_date].head(5).reset_index(drop=True)
    if fut.empty:
        return {"complete_d5": False, "future_days": 0}
    out: dict = {"complete_d5": len(fut) >= 5, "future_days": len(fut)}
    plus_thresholds = [1, 2, 3, 5, 10]
    minus_thresholds = [1, 2, 3, 5, 10]
    plus_first: dict[int, int | None] = {p: None for p in plus_thresholds}
    minus_first: dict[int, int | None] = {p: None for p in minus_thresholds}
    plus_touch: dict[int, bool] = {p: False for p in plus_thresholds}
    minus_touch: dict[int, bool] = {p: False for p in minus_thresholds}
    max_gain = -999.0
    max_loss = 999.0
    for i, row in fut.iterrows():
        day_idx = i + 1
        high_pct = (row["high"] / entry_price - 1.0) * 100
        low_pct = (row["low"] / entry_price - 1.0) * 100
        max_gain = max(max_gain, high_pct)
        max_loss = min(max_loss, low_pct)
        for p in plus_thresholds:
            if not plus_touch[p] and high_pct >= p:
                plus_touch[p] = True
                if plus_first[p] is None:
                    plus_first[p] = day_idx
        for p in minus_thresholds:
            if not minus_touch[p] and low_pct <= -p:
                minus_touch[p] = True
                if minus_first[p] is None:
                    minus_first[p] = day_idx
    # 결과 정리
    for p in plus_thresholds:
        out[f"plus{p}_touch"] = "Y" if plus_touch[p] else "N"
        out[f"plus{p}_first_day"] = plus_first[p]
    for p in minus_thresholds:
        out[f"minus{p}_touch"] = "Y" if minus_touch[p] else "N"
        out[f"minus{p}_first_day"] = minus_first[p]
    # +3 먼저 / -3 먼저
    p3 = plus_first[3]; m3 = minus_first[3]
    if p3 is not None and m3 is not None:
        out["plus3_first"] = "Y" if p3 < m3 else "N"
        out["minus3_first"] = "Y" if m3 < p3 else "N"
        out["pm3_same_day"] = "Y" if p3 == m3 else "N"
    elif p3 is not None:
        out["plus3_first"] = "Y"; out["minus3_first"] = "N"; out["pm3_same_day"] = "N"
    elif m3 is not None:
        out["plus3_first"] = "N"; out["minus3_first"] = "Y"; out["pm3_same_day"] = "N"
    else:
        out["plus3_first"] = "N"; out["minus3_first"] = "N"; out["pm3_same_day"] = "N"
    out["max_gain_d1d5"] = round(max_gain, 4)
    out["max_loss_d1d5"] = round(max_loss, 4)
    # D+1 / D+5 종가 수익률
    if len(fut) >= 1:
        out["d1_close_return_pct"] = round((fut.iloc[0]["close"] / entry_price - 1.0) * 100, 4)
        out["d1_high_vs_entry_pct"] = round((fut.iloc[0]["high"] / entry_price - 1.0) * 100, 4)
        out["d1_low_vs_entry_pct"] = round((fut.iloc[0]["low"] / entry_price - 1.0) * 100, 4)
        out["d1_color"] = classify_light(
            out["d1_high_vs_entry_pct"], out["d1_close_return_pct"], out["d1_low_vs_entry_pct"]
        )
    if len(fut) >= 5:
        out["d5_close_return_pct"] = round((fut.iloc[4]["close"] / entry_price - 1.0) * 100, 4)
    return out


# ─────────────────────────── variant 적용 ───────────────────────────

def apply_variant_top3(pool: pd.DataFrame, variant_key: str, max_price: int | None) -> pd.DataFrame:
    """가격필터 + BellGuard 점수 기준 일자별 Top3 추출."""
    df = pool.copy()
    if max_price is not None:
        df = df[df["entry_price_hint"].fillna(0) <= max_price]
    # 점수 정렬 후 일자별 상위 3
    df = df.sort_values(["d0_date", "bellguard_score"], ascending=[True, False])
    top3 = df.groupby("d0_date", group_keys=False).head(3).copy()
    top3 = top3.reset_index(drop=True)
    # rank 재계산
    top3["pricecap_rank"] = top3.groupby("d0_date").cumcount() + 1
    top3["pricecap_variant"] = variant_key
    return top3


def build_rows_with_outcomes(top3: pd.DataFrame) -> pd.DataFrame:
    """Top3 후보별 D+1~D+5 결과 계산."""
    print(f"  computing outcomes for {len(top3)} candidates...")
    out_rows: list[dict] = []
    for i, r in top3.iterrows():
        code = r["code"]
        d0 = r["d0_date"]
        entry = r["entry_price_hint"] if pd.notna(r["entry_price_hint"]) else r.get("d0_close")
        try:
            entry = float(entry)
        except (TypeError, ValueError):
            entry = float("nan")
        outcome = compute_d1d5_outcomes(code, d0, entry)
        row = r.to_dict()
        row.update(outcome)
        row["entry_price_used"] = entry
        out_rows.append(row)
        if (i + 1) % 200 == 0:
            print(f"    {i+1}/{len(top3)}")
    return pd.DataFrame(out_rows)


# ─────────────────────────── 집계 ───────────────────────────

def variant_summary(rows: pd.DataFrame, variant_key: str, variant_label: str) -> dict:
    """variant 1년 KPI 요약."""
    complete = rows[rows["complete_d5"] == True]  # noqa: E712
    n = len(complete) or 1
    light_counts = rows.get("d1_color", pd.Series(dtype=str)).value_counts().to_dict()
    days_with_pick = rows["d0_date"].nunique()
    pick_days = rows.groupby("d0_date").size()
    # Top3를 못 채운 날짜
    missing_3 = (pick_days < 3).sum()
    missing_2 = (pick_days == 1).sum()
    only_1 = (pick_days == 1).sum()
    only_2 = (pick_days == 2).sum()
    full_3 = (pick_days == 3).sum()
    def rate(col: str, target: str = "Y") -> float:
        if col not in complete.columns:
            return 0.0
        return (complete[col].astype(str) == target).mean() * 100
    summary = {
        "variant": variant_key,
        "label": variant_label,
        "sample_n": len(rows),
        "complete_d5_n": len(complete),
        "days_with_pick": days_with_pick,
        "picks_per_day_avg": round(len(rows) / max(days_with_pick, 1), 3),
        "days_full_top3": int(full_3),
        "days_only_2": int(only_2),
        "days_only_1": int(only_1),
        "days_missing_top3": int(missing_3),
        "green_rate": round(light_counts.get("GREEN", 0) / max(len(rows), 1) * 100, 2),
        "yellow_rate": round(light_counts.get("YELLOW", 0) / max(len(rows), 1) * 100, 2),
        "orange_rate": round(light_counts.get("ORANGE", 0) / max(len(rows), 1) * 100, 2),
        "red_rate": round(light_counts.get("RED", 0) / max(len(rows), 1) * 100, 2),
        "gray_rate": round(light_counts.get("GRAY", 0) / max(len(rows), 1) * 100, 2),
        "plus1_touch_rate": round(rate("plus1_touch"), 2),
        "plus2_touch_rate": round(rate("plus2_touch"), 2),
        "plus3_touch_rate": round(rate("plus3_touch"), 2),
        "plus5_touch_rate": round(rate("plus5_touch"), 2),
        "minus1_touch_rate": round(rate("minus1_touch"), 2),
        "minus2_touch_rate": round(rate("minus2_touch"), 2),
        "minus3_touch_rate": round(rate("minus3_touch"), 2),
        "minus5_touch_rate": round(rate("minus5_touch"), 2),
        "plus3_first_rate": round(rate("plus3_first"), 2),
        "minus3_first_rate": round(rate("minus3_first"), 2),
        "avg_max_gain": round(complete["max_gain_d1d5"].mean() if "max_gain_d1d5" in complete else 0, 3),
        "avg_max_loss": round(complete["max_loss_d1d5"].mean() if "max_loss_d1d5" in complete else 0, 3),
        "avg_d1_close_return": round(complete["d1_close_return_pct"].mean() if "d1_close_return_pct" in complete else 0, 3),
        "avg_d5_close_return": round(complete["d5_close_return_pct"].mean() if "d5_close_return_pct" in complete else 0, 3),
    }
    # Worst10 D5 (D5 종가 수익률 하위 10 평균)
    if "d5_close_return_pct" in complete.columns and len(complete) >= 10:
        worst10 = complete["d5_close_return_pct"].nsmallest(10).mean()
        summary["worst10_d5_return"] = round(worst10, 3)
    return summary


def build_signal_by_date(rows: pd.DataFrame) -> pd.DataFrame:
    """날짜별 r1/r2/r3 셀 (대시보드 신호등표용)."""
    rows = rows.copy().sort_values(["d0_date", "pricecap_rank"])
    out: list[dict] = []
    for d0, day in rows.groupby("d0_date"):
        row = {"d0_date": d0}
        for rank in (1, 2, 3):
            r = day[day["pricecap_rank"] == rank]
            if r.empty:
                row[f"bellguard_r{rank}_cell"] = ""
                row[f"bellguard_r{rank}_light"] = ""
                row[f"bellguard_r{rank}_score"] = None
                row[f"bellguard_r{rank}_code"] = ""
                row[f"bellguard_r{rank}_name"] = ""
                row[f"bellguard_r{rank}_reason"] = ""
            else:
                rr = r.iloc[0]
                light = rr.get("d1_color", "GRAY")
                emoji = {"GREEN": "🟢", "YELLOW": "🟡", "ORANGE": "🟠", "RED": "🔴", "GRAY": "⚪"}.get(light, "⚪")
                name = rr.get("name", "")
                code = rr.get("code", "")
                row[f"bellguard_r{rank}_cell"] = f"{emoji} {name}({code})"
                row[f"bellguard_r{rank}_light"] = light
                row[f"bellguard_r{rank}_score"] = round(float(rr.get("bellguard_score", 0)), 2)
                row[f"bellguard_r{rank}_code"] = code
                row[f"bellguard_r{rank}_name"] = name
                row[f"bellguard_r{rank}_reason"] = ""  # 추후 reason 추가
        # day verdict
        lights = [row[f"bellguard_r{i}_light"] for i in (1, 2, 3) if row[f"bellguard_r{i}_light"]]
        g = lights.count("GREEN") + lights.count("YELLOW")
        r_ = lights.count("RED") + lights.count("ORANGE")
        if g > r_:
            row["date_verdict"] = "안정 우세"
        elif r_ > g:
            row["date_verdict"] = "위험 우세"
        else:
            row["date_verdict"] = "혼조"
        out.append(row)
    return pd.DataFrame(out)


def build_day_summary(rows: pd.DataFrame) -> pd.DataFrame:
    """일별 통계 (대시보드 일별 요약용)."""
    g = rows.groupby("d0_date").agg(
        candidate_count=("code", "count"),
        green_count=("d1_color", lambda s: (s == "GREEN").sum()),
        yellow_count=("d1_color", lambda s: (s == "YELLOW").sum()),
        orange_count=("d1_color", lambda s: (s == "ORANGE").sum()),
        red_count=("d1_color", lambda s: (s == "RED").sum()),
        avg_bellguard_score=("bellguard_score", "mean"),
        avg_max_gain=("max_gain_d1d5", "mean"),
        avg_max_loss=("max_loss_d1d5", "mean"),
    ).reset_index()
    g["green_rate"] = (g["green_count"] / g["candidate_count"] * 100).round(2)
    g["red_rate"] = (g["red_count"] / g["candidate_count"] * 100).round(2)
    return g


def build_month_summary(rows: pd.DataFrame) -> pd.DataFrame:
    rows = rows.copy()
    rows["month"] = rows["d0_date"].str.slice(0, 7)
    g = rows.groupby("month").agg(
        candidate_count=("code", "count"),
        green_count=("d1_color", lambda s: (s == "GREEN").sum()),
        red_count=("d1_color", lambda s: (s == "RED").sum()),
        avg_max_gain=("max_gain_d1d5", "mean"),
        avg_max_loss=("max_loss_d1d5", "mean"),
        avg_d1_close=("d1_close_return_pct", "mean"),
    ).reset_index()
    g["green_rate"] = (g["green_count"] / g["candidate_count"] * 100).round(2)
    g["red_rate"] = (g["red_count"] / g["candidate_count"] * 100).round(2)
    return g


# ─────────────────────────── 메인 ───────────────────────────


def main():
    print("=" * 60)
    print("BellGuard 가격필터 1년 백데이터 생성")
    print("=" * 60)
    print(f"source: {SRC_POOL_CSV}")
    pool = load_source_pool()
    print(f"source pool: {len(pool):,} rows, {pool['d0_date'].nunique()} days")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summaries: list[dict] = []
    all_rows_by_variant: dict[str, pd.DataFrame] = {}

    for variant_key, max_price, label in PRICECAP_VARIANTS:
        print(f"\n--- variant: {variant_key} ({label}) ---")
        top3 = apply_variant_top3(pool, variant_key, max_price)
        print(f"  Top3 candidates: {len(top3)} ({top3['d0_date'].nunique()} days)")
        rows = build_rows_with_outcomes(top3)
        all_rows_by_variant[variant_key] = rows
        summary = variant_summary(rows, variant_key, label)
        summaries.append(summary)
        print(f"  GREEN {summary['green_rate']}% / RED {summary['red_rate']}% / "
              f"+3 first {summary['plus3_first_rate']}% / -3 first {summary['minus3_first_rate']}%")

    # 메인 variant 데이터 저장
    main_rows = all_rows_by_variant[MAIN_VARIANT_KEY]
    print(f"\n[main variant = {MAIN_VARIANT_KEY}] saving full dataset")
    main_rows.to_parquet(OUT_DIR / "bellguard_ui_review_signal_rows_1y.parquet", index=False)
    main_rows.to_csv(OUT_DIR / "bellguard_ui_review_signal_rows_1y.csv", index=False, encoding="utf-8-sig")
    build_signal_by_date(main_rows).to_csv(OUT_DIR / "bellguard_ui_review_signal_by_date_1y.csv", index=False, encoding="utf-8-sig")
    build_day_summary(main_rows).to_csv(OUT_DIR / "bellguard_ui_review_signal_day_summary_1y.csv", index=False, encoding="utf-8-sig")
    build_month_summary(main_rows).to_csv(OUT_DIR / "bellguard_ui_review_signal_month_summary_1y.csv", index=False, encoding="utf-8-sig")

    # 최신일 Top3 (현재일 — 미래 결과 컬럼 제거, 웹훅 메시지에 쓸 거래대금/근거 포함)
    latest_date = main_rows["d0_date"].max()
    latest_top3 = main_rows[main_rows["d0_date"] == latest_date].copy()
    # bellguard_reason 자동 생성 (source pool에 reason 컬럼 없어서 핵심 지표 조합)
    def _make_reason(row: pd.Series) -> str:
        bits = []
        d0 = row.get("d0_pct_change") or row.get("d0_ret_pct")
        if pd.notna(d0):
            try:
                bits.append(f"D0 {float(d0):+.1f}%")
            except (TypeError, ValueError):
                pass
        vr = row.get("volume_ratio_vs_20d")
        if pd.notna(vr):
            try:
                bits.append(f"거래량 20일대비 {float(vr):.1f}배")
            except (TypeError, ValueError):
                pass
        oh = row.get("overheat_score")
        if pd.notna(oh):
            try:
                ohf = float(oh)
                if ohf >= 0.7:
                    bits.append("과열↑")
                elif ohf <= 0.3:
                    bits.append("과열 낮음")
            except (TypeError, ValueError):
                pass
        ev = str(row.get("event_risk_note") or "").strip()
        if ev and ev.lower() != "nan":
            bits.append(ev)
        return " / ".join(bits) if bits else "—"

    latest_top3["bellguard_reason_auto"] = latest_top3.apply(_make_reason, axis=1)
    keep_cols_today = [
        "d0_date", "code", "name", "market", "sector", "industry",
        "pricecap_rank", "bellguard_score", "entry_price_used",
        "d0_pct_change", "distance_from_d0_high_pct", "volume_ratio_vs_20d",
        "d0_trading_value", "d0_trading_value_eok",
        "overheat_score", "health_score", "regime_score", "regime",
        "bellguard_reason_auto",
    ]
    latest_top3_clean = latest_top3[[c for c in keep_cols_today if c in latest_top3.columns]]
    latest_top3_clean.to_csv(OUT_DIR / "bellguard_ui_review_top3_latest.csv", index=False, encoding="utf-8-sig")

    # 전체 후보 (latest 일자만, 미래 결과 제거)
    latest_all = pool.copy()
    latest_all = latest_all[latest_all["d0_date"] == latest_date]
    if MAIN_VARIANT_KEY != "none":
        max_p = dict([(k, v) for k, v, _ in PRICECAP_VARIANTS])[MAIN_VARIANT_KEY]
        if max_p is not None:
            latest_all = latest_all[latest_all["entry_price_hint"].fillna(0) <= max_p]
    latest_all.to_csv(OUT_DIR / "bellguard_ui_review_latest_candidates_all.csv", index=False, encoding="utf-8-sig")

    # 4 variant 비교 요약
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(OUT_DIR / "bellguard_ui_review_summary_1y.csv", index=False, encoding="utf-8-sig")

    # manifest — publish.ps1 가드 필드 포함
    latest_signal_date = main_rows["d0_date"].max()
    latest_top3_count = int((main_rows["d0_date"] == latest_signal_date).sum())
    # webhook_ready: Top3 3개 + 신선도 충족(2 거래일 이내) 시 true
    from datetime import date as _date, timedelta as _td
    try:
        latest_dt = pd.to_datetime(latest_signal_date).date()
        webhook_ready = (latest_top3_count == 3) and ((_date.today() - latest_dt).days <= 3)
    except Exception:  # noqa: BLE001
        webhook_ready = False
    manifest = {
        "dataset_name": "bellguard_ui_review_1y",
        "latest_signal_date": str(latest_signal_date),
        "latest_top3_rows": latest_top3_count,
        "webhook_ready": bool(webhook_ready),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generator": "Claude Code: build_bellguard_ui_review_dataset.py",
        "source_pool": str(SRC_POOL_CSV),
        "source_pool_rows": len(pool),
        "source_pool_days": int(pool["d0_date"].nunique()),
        "main_variant": MAIN_VARIANT_KEY,
        "variants": [
            {"key": k, "max_price": p, "label": l}
            for k, p, l in PRICECAP_VARIANTS
        ],
        "selection_order": [
            "D0 strict 3D pool (active_d0_3d_pool, classic D0 base filter, 가격 2000~100k)",
            "가격필터 (variant별 entry_price_hint <= cap)",
            "BellGuard 점수 정렬",
            "일자별 Top3",
        ],
        "outcome_calculation": "D+1~D+5 일봉 high/low 기반, entry=entry_price_hint",
        "lookahead_safe_in_today_files": True,
        "operational_unchanged": True,
        "files": {
            "signal_rows_parquet": "bellguard_ui_review_signal_rows_1y.parquet",
            "signal_rows_csv": "bellguard_ui_review_signal_rows_1y.csv",
            "signal_by_date": "bellguard_ui_review_signal_by_date_1y.csv",
            "day_summary": "bellguard_ui_review_signal_day_summary_1y.csv",
            "month_summary": "bellguard_ui_review_signal_month_summary_1y.csv",
            "top3_latest": "bellguard_ui_review_top3_latest.csv",
            "latest_candidates_all": "bellguard_ui_review_latest_candidates_all.csv",
            "variant_summary": "bellguard_ui_review_summary_1y.csv",
        },
        "summary_kpi": summaries,
    }
    (OUT_DIR / "bellguard_ui_review_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 콘솔 요약
    print("\n" + "=" * 60)
    print("variant 비교 (1년)")
    print("=" * 60)
    print(summary_df[[
        "variant", "label", "sample_n", "days_full_top3", "days_missing_top3",
        "green_rate", "red_rate", "plus3_first_rate", "minus3_first_rate",
        "plus3_touch_rate", "minus3_touch_rate", "avg_max_gain", "avg_max_loss",
    ]].to_string(index=False))
    print(f"\n[OK] output: {OUT_DIR}")


if __name__ == "__main__":
    main()
