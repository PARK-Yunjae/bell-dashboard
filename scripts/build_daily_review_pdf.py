"""
ClosingBell 일일 한글 친화 복기 PDF 생성기.

지시서 (2026-05-13 FACEVALUE/DASHBOARD 핸드오프 §6) 8섹션 구조:
    1. 오늘의 결론
    2. 지금 후보는 어떤 기준으로 나왔나
    3. 기존 거래대금 기준과 점수제의 차이
    4. 5일 안에 +3% 도달률과 실제 승률의 차이
    5. 눌림목과 회복 확인이 왜 중요한가
    6. 오늘 데이터 최신성
    7. LIVE 후보와 연구용 후보 비교
    8. 다음에 확인할 것

원칙: 한글 제목 / 큰 표 분리 / 열 ≤ 7개 / 숫자마다 해석 / 50대 초보도 이해 가능.
운영 cli·점수 산식·후보 선정·웹훅 발송 — 모두 무관 (표시·해석 전용).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager

# ---- Korean font ----
KOREAN_TTF = Path(r"C:\Windows\Fonts\malgun.ttf")
KOREAN_TTF_BD = Path(r"C:\Windows\Fonts\malgunbd.ttf")
for tf in (KOREAN_TTF, KOREAN_TTF_BD):
    if tf.exists():
        font_manager.fontManager.addfont(str(tf))
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"C:\Coding")
DATA = ROOT / "data"
WATCHLISTS = DATA / "closingbell" / "shared" / "watchlists"
PULLBACK_DIR = DATA / "closingbell" / "paper_watch" / "pullback_reclaim"
DAILY_DIR = DATA / "market" / "daily_ohlcv"
MINUTE_DIR = DATA / "market" / "minute_ohlcv"
HOLIDAY_FILE = DATA / "market" / "calendar" / "krx_holidays_manual.csv"
AUDIT_DIR = Path(r"C:\Users\PYJ\AppData\Local\Temp\d0_score_audit_20260513\D0_SCORE_TOP3_TOUCH_AUDIT_20260513")

A4_LANDSCAPE = (11.7, 8.3)


# ===== helpers =====
def _read(p: Path) -> pd.DataFrame:
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


def _zfill(code: Any) -> str:
    s = str(code or "").strip()
    return s.zfill(6) if s else ""


def _to_float(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except Exception:
        return None


def _fmt_eok(value: Any) -> str:
    n = _to_float(value)
    if n is None:
        return "—"
    return f"{n / 1_0000_0000:,.0f}억"


def _fmt_int(value: Any) -> str:
    n = _to_float(value)
    return f"{int(n):,}" if n is not None else "—"


def _fmt_pct(value: Any, signed: bool = False) -> str:
    n = _to_float(value)
    if n is None:
        return "—"
    return f"{n:+.2f}%" if signed else f"{n:.1f}%"


def _load_holidays() -> set[str]:
    if not HOLIDAY_FILE.exists():
        return set()
    try:
        df = pd.read_csv(HOLIDAY_FILE, dtype=str, encoding="utf-8-sig").fillna("")
    except Exception:
        return set()
    return {str(row.get("date", ""))[:10] for _, row in df.iterrows() if str(row.get("date", "")).strip()}


def _busday_count(start: pd.Timestamp | None, end: pd.Timestamp, holidays: set[str]) -> int:
    if start is None or start >= end:
        return 0 if start is not None else 9_999
    days = pd.bdate_range(start + pd.Timedelta(days=1), end, freq="B")
    return sum(1 for d in days if d.strftime("%Y-%m-%d") not in holidays)


def _latest_daily_for(code: str) -> pd.Timestamp | None:
    p = DAILY_DIR / f"{_zfill(code)}.parquet"
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
    except Exception:
        return None
    if df.empty or "date" not in df.columns:
        return None
    return pd.Timestamp(pd.to_datetime(df["date"]).max()).normalize()


def _latest_minute_for(code: str) -> pd.Timestamp | None:
    p = MINUTE_DIR / f"{_zfill(code)}.parquet"
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
    except Exception:
        return None
    if df.empty or "dt" not in df.columns:
        return None
    return pd.Timestamp(pd.to_datetime(df["dt"]).max()).normalize()


def _add_table(ax, header: list[str], rows: list[list[str]], col_widths: list[float],
               header_color: str = "#e8eef7", zebra: tuple[str, str] = ("#ffffff", "#f8fafc"),
               font_size: int = 9, scale: float = 1.6) -> Any:
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=10, color="#999")
        return None
    t = ax.table(cellText=rows, colLabels=header, loc="upper left", cellLoc="left", colWidths=col_widths)
    t.auto_set_font_size(False)
    t.set_fontsize(font_size)
    t.scale(1.0, scale)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor(zebra[(r - 1) % 2])
    return t


def _section_header(fig, y: float, num: int, title: str) -> None:
    ax = fig.add_axes([0.04, y, 0.92, 0.05]); ax.axis("off")
    ax.text(0.0, 0.5, f"{num}. {title}", fontsize=14, fontweight="bold", color="#1f2937", va="center")
    ax.add_patch(plt.Rectangle((0.0, 0.0), 1.0, 0.06, transform=ax.transAxes,
                               facecolor="#dbeafe", edgecolor="none"))


def _footer(fig, target_date: str) -> None:
    ax = fig.add_axes([0.04, 0.015, 0.92, 0.025]); ax.axis("off")
    ax.text(0.0, 0.5,
            f"ClosingBell 일일 복기  ·  {target_date}  ·  생성 {datetime.now().strftime('%Y-%m-%d %H:%M')}  "
            "·  추천 종목 아님 · 자동매매 아님 · 수동 확인용",
            fontsize=7.5, color="#888", va="center")


def _data_ctx(target_date: str) -> dict[str, Any]:
    """모든 페이지가 공유하는 데이터 컨텍스트."""
    yyyymmdd = target_date.replace("-", "")
    score = _read(WATCHLISTS / f"score_breakdown_{yyyymmdd}.csv")
    picks = _read(WATCHLISTS / f"webhook_picks_5d_{yyyymmdd}.csv")
    d0_pool = _read(WATCHLISTS / f"d0_pool_dryrun_{yyyymmdd}.csv")
    pr_watch = _read(PULLBACK_DIR / f"pullback_reclaim_watch_{yyyymmdd}.csv")
    pr_result = _read(PULLBACK_DIR / f"pullback_reclaim_result_{yyyymmdd}.csv")
    audit_cmp = _read(AUDIT_DIR / "score_vs_value_top3_comparison_20260513.csv")
    audit_base = _read(AUDIT_DIR / "baseline_value_top3_top5_touch_20260513.csv")
    holidays = _load_holidays()

    # body+ref candidates
    if not score.empty:
        score["_rank_n"] = pd.to_numeric(score["rank"], errors="coerce").fillna(99).astype(int)
        body_ref = score[score["_rank_n"].between(1, 3)].sort_values("_rank_n")
    else:
        body_ref = pd.DataFrame()

    # latest daily/minute for body+ref
    today = pd.Timestamp.today().normalize()
    latest_dailies: list[pd.Timestamp] = []
    latest_minutes: list[pd.Timestamp] = []
    for _, r in body_ref.iterrows():
        c = _zfill(r.get("stock_code", ""))
        ld = _latest_daily_for(c); lm = _latest_minute_for(c)
        if ld is not None: latest_dailies.append(ld)
        if lm is not None: latest_minutes.append(lm)
    latest_daily = max(latest_dailies) if latest_dailies else None
    latest_minute = max(latest_minutes) if latest_minutes else None
    daily_lag = _busday_count(latest_daily, today, holidays)
    if daily_lag <= 1:
        status = ("[정상] 최신", "#dcfce7", "#166534")
    elif daily_lag == 2:
        status = ("[주의] 후보 가격 데이터가 최신이 아닐 수 있음", "#fef9c3", "#854d0e")
    else:
        status = ("[위험] 후보 가격 데이터가 2거래일 이상 지연", "#fee2e2", "#991b1b")

    return dict(
        target_date=target_date,
        score=score, picks=picks, d0_pool=d0_pool,
        body_ref=body_ref,
        pr_watch=pr_watch, pr_result=pr_result,
        audit_cmp=audit_cmp, audit_base=audit_base,
        latest_daily=latest_daily, latest_minute=latest_minute,
        daily_lag=daily_lag, status=status,
    )


# ===== Pages =====
def page_1_conclusion_and_basis(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """1. 오늘의 결론 + 2. 지금 후보는 어떤 기준으로 나왔나"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle(f"ClosingBell 일일 복기  ·  {ctx['target_date']}",
                 fontsize=16, fontweight="bold", y=0.965)

    # Section 1: 오늘의 결론
    _section_header(fig, 0.86, 1, "오늘의 결론")
    body_ref = ctx["body_ref"]
    picks = ctx["picks"]
    picks_idx = picks.set_index("stock_code").to_dict(orient="index") if not picks.empty else {}
    n_live = len(body_ref)
    n_pool = len(ctx["d0_pool"])
    n_shadow_live = 0
    n_shadow_pool = 0
    if not ctx["pr_watch"].empty:
        wt = ctx["pr_watch"]["watch_type"]
        n_shadow_live = int(wt.isin(["D0_STRONG_CLOSE_LIVE_TOP2", "D0_STRONG_CLOSE_LIVE_RANK3"]).sum())
        n_shadow_pool = int((wt == "D0_STRONG_CLOSE_POOL_ONLY").sum())
    bullet_lines = [
        f"• 오늘 실제 웹훅(LIVE) 후보는 본문 2 + 참고 1, 총 {n_live}건입니다. 모두 ‘기존 거래대금 기준(P0)’으로 뽑혔습니다.",
        f"• 최초 거래대금 폭발일(D0) 후보 풀 전체는 {n_pool}건이고, 그중 강세종가 Shadow 감시는 {n_shadow_live + n_shadow_pool}건입니다.",
        f"• 데이터 최신성: {ctx['status'][0]} (가격 데이터 최신일 = {ctx['latest_daily'].strftime('%Y-%m-%d') if ctx['latest_daily'] else '—'}).",
        "• 이 리포트는 매수 추천이 아니라 ‘오늘 어떤 종목을 어떤 기준으로 감시하기 시작했는가’의 기록입니다.",
    ]
    ax = fig.add_axes([0.04, 0.66, 0.92, 0.18]); ax.axis("off")
    ax.text(0.0, 1.0, "\n".join(bullet_lines), fontsize=11, color="#374151", va="top",
            linespacing=1.7, wrap=True)

    # Section 2: 지금 후보는 어떤 기준으로 나왔나
    _section_header(fig, 0.59, 2, "지금 후보는 어떤 기준으로 나왔나")
    explain = [
        "기준: 종가 2,000~100,000원 + 거래량 1,000만주 이상 + 전일 대비 등락률 양수 인 보통주 중 거래대금 상위 5종목을 본문/참고/보조로 분리.",
        "역할: 1·2위는 본문 후보(Top2), 3위는 참고 후보(Rank3), 4·5위는 보조 후보(LOG_ONLY, 기록 전용).",
        "오늘 본문 + 참고 후보 표:",
    ]
    ax2 = fig.add_axes([0.04, 0.49, 0.92, 0.09]); ax2.axis("off")
    ax2.text(0.0, 1.0, "\n".join(f"• {line}" for line in explain), fontsize=10.5, color="#374151",
             va="top", linespacing=1.65)

    # body+ref table
    rows = []
    for _, r in body_ref.iterrows():
        code = _zfill(r.get("stock_code", ""))
        pinfo = picks_idx.get(code, {})
        role = str(r.get("role", ""))
        role_label = {"BODY_TOP2": "본문", "REFERENCE_RANK3": "참고", "LOG_ONLY": "보조"}.get(role, role)
        rows.append([
            str(r.get("rank", "")),
            role_label,
            f"{r.get('stock_name','')} ({code})",
            f"{r.get('score','')}점",
            _fmt_eok(pinfo.get("d0_trading_value", "")),
            _fmt_int(pinfo.get("d0_price", "")),
            str(pinfo.get("d0_date", ""))[:10] or "—",
        ])
    ax3 = fig.add_axes([0.04, 0.08, 0.92, 0.38]); ax3.axis("off")
    _add_table(ax3,
               ["순위", "구분", "종목", "점수", "거래대금", "D0 종가", "최초 거래대금 폭발일(D0)"],
               rows,
               [0.06, 0.08, 0.28, 0.08, 0.16, 0.13, 0.21],
               header_color="#dcfce7")
    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def page_2_value_vs_score(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """3. 기존 거래대금 기준과 점수제의 차이"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("기존 거래대금 기준(P0)과 점수제(v2)의 차이",
                 fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 3, "기존 거래대금 기준과 점수제의 차이")

    score = ctx["score"].copy()
    if score.empty:
        ax = fig.add_axes([0.04, 0.5, 0.92, 0.3]); ax.axis("off")
        ax.text(0.0, 0.5, "score_breakdown 파일이 없습니다.", fontsize=11, color="#999")
        _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)
        return

    score["_rank_n"] = pd.to_numeric(score["rank"], errors="coerce").fillna(99).astype(int)
    score["_score_n"] = pd.to_numeric(score["score"], errors="coerce").fillna(0).astype(int)
    p0 = score.sort_values("_rank_n")
    v2 = score.sort_values("_score_n", ascending=False)

    def _mkrows(df: pd.DataFrame) -> list[list[str]]:
        out: list[list[str]] = []
        for i, (_, r) in enumerate(df.iterrows(), start=1):
            code = _zfill(r.get("stock_code", ""))
            role = str(r.get("role", ""))
            role_label = {"BODY_TOP2": "본문", "REFERENCE_RANK3": "참고", "LOG_ONLY": "보조"}.get(role, role)
            out.append([str(i), role_label, f"{r.get('stock_name','')} ({code})", f"{r.get('score','')}점"])
        return out

    header = ["순위", "구분", "종목", "점수"]
    widths = [0.10, 0.16, 0.50, 0.20]

    ax_left = fig.add_axes([0.04, 0.46, 0.44, 0.38]); ax_left.axis("off")
    ax_left.set_title("[LIVE] 기존 거래대금 기준 (P0)", fontsize=12, fontweight="bold",
                      loc="left", pad=12, color="#166534")
    _add_table(ax_left, header, _mkrows(p0), widths, header_color="#dcfce7")

    ax_right = fig.add_axes([0.52, 0.46, 0.44, 0.38]); ax_right.axis("off")
    ax_right.set_title("[v2] 점수제 순 (연구용 · 운영 미반영)", fontsize=12, fontweight="bold",
                       loc="left", pad=12, color="#7e22ce")
    _add_table(ax_right, header, _mkrows(v2), widths, header_color="#f3e8ff")

    note = [
        "• 두 표는 같은 5종목을 다른 순서로 정렬한 것입니다. 종목 자체는 같습니다.",
        "• LIVE 는 거래대금 큰 종목을 1위로 둡니다. 시장 관심을 기준선으로 삼는다는 뜻입니다.",
        "• v2 는 점수가 높은 종목을 1위로 둡니다. 점수는 4,566개 가중치 조합의 후보이며 운영에 반영되어 있지 않습니다.",
        "• 두 정렬의 차이가 의미 있는지는 1년치 통계로 다음 페이지에서 확인합니다.",
    ]
    ax_note = fig.add_axes([0.04, 0.10, 0.92, 0.34]); ax_note.axis("off")
    ax_note.text(0.0, 1.0, "\n".join(note), fontsize=10.5, color="#374151", va="top",
                 linespacing=1.7, wrap=True)
    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def page_3_touch_vs_winrate(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """4. 5일 안에 +3% 도달률과 실제 승률의 차이"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("5일 안에 +3% 도달률 vs 실제 승률의 차이",
                 fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 4, "5일 안에 +3% 도달률과 실제 승률의 차이")

    src = ctx["audit_cmp"]
    rows = []
    if not src.empty:
        keep = [
            ("D0 거래대금 순위 Top3", "거래대금 Top3 (P0)"),
            ("D0 거래대금 순위 Top5", "거래대금 Top5 (P0)"),
            ("점수제 SCORE_TOP5 median", "점수제 Top5 (v2 median)"),
        ]
        for src_label, display in keep:
            r = src[src["group"] == src_label]
            if r.empty: continue
            r = r.iloc[0]
            up3 = float(r.get("up3_touch_d5_pct", "0"))
            dn2 = float(r.get("down2_touch_d5_pct", "0"))
            t3b = float(r.get("target3_before_risk2_d5_pct", "0"))
            # 해석
            if "점수제" in display:
                interp = "기존 대비 +3 도달 ↑ · -2 터치 ↓ · 선후관계 ↑"
            elif "Top3" in display:
                interp = "많이 오르지만 많이 흔들림 (선후관계 약함)"
            else:
                interp = "Top3와 비슷 · 표본만 늘어남"
            rows.append([display, f"{up3:.1f}%", f"{dn2:.1f}%", f"{t3b:.1f}%", interp])

    ax = fig.add_axes([0.04, 0.50, 0.92, 0.34]); ax.axis("off")
    _add_table(ax,
               ["기준", "+3% 도달", "-2% 하락 터치", "+3 먼저 (선후관계)", "쉬운 해석"],
               rows,
               [0.22, 0.13, 0.14, 0.16, 0.35],
               header_color="#fef3c7", scale=1.9)

    explain = [
        "• ‘+3% 도달’ 은 5일 안에 한 번이라도 +3% 위로 닿았는지 비율입니다. 승률이 아닙니다.",
        "• ‘-2% 하락 터치’ 는 같은 기간 -2% 아래로 닿았는지 비율입니다. 낮을수록 좋습니다.",
        "• ‘+3 먼저’ 는 +3%가 -2%보다 먼저 닿은 비율입니다. 이것이 사실상 ‘선후관계 승률’ 에 가깝습니다.",
        "• 거래대금 Top3 는 +3 도달은 높지만 -2 도 같이 높습니다. ‘많이 오르고 많이 흔들리는’ 상태입니다.",
        "• 점수제 Top5 (4,566개 variant 중앙값) 는 +3 도달은 약간 더 높고, -2 터치는 의미 있게 낮으며,",
        "  +3 먼저 닿는 비율은 30.8% → 46.0% 로 가장 크게 개선됩니다.",
        "• 단, 점수제는 아직 단일 variant 채택 전입니다. 과최적화 위험이 있어 robust 검증 후 운영 전환합니다.",
    ]
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.36]); ax2.axis("off")
    ax2.text(0.0, 1.0, "\n".join(explain), fontsize=10.5, color="#374151", va="top",
             linespacing=1.65, wrap=True)
    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def page_4_pullback_reclaim(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """5. 눌림목과 회복 확인이 왜 중요한가"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("눌림목(pullback)과 회복 확인(reclaim)이 왜 중요한가",
                 fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 5, "눌림목과 회복 확인이 왜 중요한가")

    narrative = [
        "• 거래대금 D0 = ‘시장의 관심 입장권’. 다음날 추격 매수는 위험. 눌림 후 회복 확인이 더 안전한 진입 후보로 검토되어 왔습니다.",
        "• 눌림목: D0 이후 가격이 조정 받는 구간. 너무 깊이 떨어지면 보통 회복이 힘듭니다. ‘얕은 눌림’ 이 핵심 관찰 대상입니다.",
        "• 회복 확인: 눌림 후 거래량 가중 평균가(VWAP) 회복 / 전일 눌림 고가 회복 / 장초반 고점 돌파(ORB) 같은 트리거가 발생하는지 확인합니다.",
        "• Pullback Reclaim 은 매수 추천이 아니라 ‘D+1~D+3 안에 회복 트리거가 실제로 일어나는지 사후에 체크’ 하는 감시 후보입니다.",
    ]
    ax_n = fig.add_axes([0.04, 0.66, 0.92, 0.18]); ax_n.axis("off")
    ax_n.text(0.0, 1.0, "\n".join(narrative), fontsize=10.5, color="#374151", va="top",
              linespacing=1.7, wrap=True)

    # Pullback Reclaim 통계 from audit
    src = ctx["audit_base"]
    stat_rows = []
    if not src.empty:
        for policy_id in ("POLICY_A_STRONG_CLOSE", "POLICY_B_SHALLOW_PULLBACK"):
            r = src[src["policy_id"] == policy_id]
            if r.empty: continue
            r = r.iloc[0]
            stat_rows.append([
                "강세종가 (D0 종가 위치/방어 양호)" if policy_id == "POLICY_A_STRONG_CLOSE" else "얕은 눌림 (표본 적음, 참고용)",
                _fmt_int(r.get("eligible_n", "")),
                f"{float(r.get('up3_touch_d5_pct','0')):.1f}%",
                f"{float(r.get('down2_touch_d5_pct','0')):.1f}%",
                f"{float(r.get('target3_before_risk2_d5_pct','0')):.1f}%",
            ])
    ax_t = fig.add_axes([0.04, 0.42, 0.92, 0.22]); ax_t.axis("off")
    ax_t.set_title("강세종가 / 얕은 눌림 정책 — 1년치 참고 통계", fontsize=11, fontweight="bold",
                   loc="left", pad=8, color="#1f2937")
    _add_table(ax_t,
               ["정책", "표본", "+3% 도달", "-2% 터치", "+3 먼저"],
               stat_rows,
               [0.40, 0.10, 0.16, 0.16, 0.18],
               header_color="#fef3c7", scale=1.8)

    # 오늘 Pullback Reclaim watch
    pw = ctx["pr_watch"]
    today_rows = []
    if not pw.empty:
        live = pw[pw["watch_type"].isin(["D0_STRONG_CLOSE_LIVE_TOP2", "D0_STRONG_CLOSE_LIVE_RANK3"])]
        for _, r in live.iterrows():
            wt = str(r.get("watch_type", ""))
            label = {"D0_STRONG_CLOSE_LIVE_TOP2": "D0 강세종가 · 본문 LIVE",
                     "D0_STRONG_CLOSE_LIVE_RANK3": "D0 강세종가 · 참고 LIVE"}.get(wt, wt)
            today_rows.append([
                f"{r.get('stock_name','')} ({_zfill(r.get('stock_code',''))})",
                label,
                str(r.get("score_total_100", "")),
                str(r.get("d0_date", ""))[:10],
                "D+1 일봉·분봉 데이터 대기",
            ])
    ax_today = fig.add_axes([0.04, 0.10, 0.92, 0.28]); ax_today.axis("off")
    ax_today.set_title("오늘의 Pullback Reclaim 감시 (LIVE 매칭)", fontsize=11, fontweight="bold",
                       loc="left", pad=8, color="#1f2937")
    _add_table(ax_today,
               ["종목", "감시 유형", "점수", "최초 거래대금 폭발일(D0)", "현재 트리거 상태"],
               today_rows,
               [0.26, 0.24, 0.08, 0.18, 0.24],
               header_color="#f3e8ff", scale=1.8)
    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def page_5_freshness(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """6. 오늘 데이터 최신성"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("오늘 데이터 최신성", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 6, "오늘 데이터 최신성")

    sd = ctx["score"]["signal_date"].max() if not ctx["score"].empty else ctx["target_date"]
    d0 = ""
    if not ctx["picks"].empty and "d0_date" in ctx["picks"].columns:
        d0s = [str(x)[:10] for x in ctx["picks"]["d0_date"].tolist() if str(x).strip()]
        d0 = max(d0s) if d0s else ""
    daily = ctx["latest_daily"].strftime("%Y-%m-%d") if ctx["latest_daily"] else "—"
    minute = ctx["latest_minute"].strftime("%Y-%m-%d") if ctx["latest_minute"] else "—"
    status_text, status_bg, status_fg = ctx["status"]

    rows = [
        ["웹훅 기준일", sd, "오늘 15:00 Discord 메시지가 가리키는 날짜"],
        ["최초 거래대금 폭발일(D0)", d0 or "—", "후보를 만든 원천 거래일"],
        ["가격(일봉) 데이터 최신일", daily, "각 후보 일봉 parquet의 가장 최근 거래일"],
        ["분봉 데이터 최신일", minute, "분봉 parquet의 가장 최근 거래일"],
        ["상태", status_text, "정상/주의/위험 — 영업일(주말+휴장일 제외) 기준 일봉 지연"],
    ]
    ax = fig.add_axes([0.04, 0.52, 0.92, 0.32]); ax.axis("off")
    _add_table(ax, ["항목", "값", "쉬운 설명"], rows, [0.30, 0.28, 0.42],
               header_color=status_bg, scale=1.9)

    explain = [
        "• 일봉 지연이 0~1거래일이면 정상입니다 — 오늘 15:00 운영 시점에는 어제 종가가 들어와 있어야 합니다.",
        "• 2거래일 지연이면 주의 — D0 종가가 아닌 더 이전 데이터로 후보를 만들었을 가능성이 있습니다.",
        "• 3거래일 이상이면 위험 — 운영 cli 의 자동 갱신(키움 일봉 refresh)이 누락되었을 수 있습니다.",
        "• 분봉은 보조 데이터입니다. 분봉이 없으면 같은 날 ‘+3% 가 먼저인지 -2% 가 먼저인지’ 의 선후관계를 확정할 수 없습니다.",
        "• 매일 17:05 PostClose 가 정상 동작하면 그날의 일봉이 자동으로 최신화됩니다.",
    ]
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.40]); ax2.axis("off")
    ax2.text(0.0, 1.0, "\n".join(explain), fontsize=10.5, color="#374151", va="top",
             linespacing=1.7, wrap=True)
    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def page_6_live_vs_shadow(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """7. LIVE 후보와 연구용 후보 비교"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("LIVE 후보 vs 연구용 Shadow 후보", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 7, "LIVE 후보와 연구용 후보 비교")

    body_ref = ctx["body_ref"]
    pw = ctx["pr_watch"]
    pr_idx = pw.set_index("stock_code").to_dict(orient="index") if not pw.empty else {}
    rows = []
    for _, r in body_ref.iterrows():
        code = _zfill(r.get("stock_code", ""))
        role = str(r.get("role", ""))
        role_label = {"BODY_TOP2": "본문(LIVE)", "REFERENCE_RANK3": "참고(LIVE)", "LOG_ONLY": "보조(LIVE)"}.get(role, role)
        pri = pr_idx.get(code, {})
        shadow_label = {
            "D0_STRONG_CLOSE_LIVE_TOP2": "D0 강세종가 · 본문 Shadow",
            "D0_STRONG_CLOSE_LIVE_RANK3": "D0 강세종가 · 참고 Shadow",
            "D0_STRONG_CLOSE_POOL_ONLY": "D0 강세종가 · 풀 Shadow",
        }.get(str(pri.get("watch_type", "")), "—")
        rows.append([
            f"{r.get('stock_name','')} ({code})",
            role_label,
            shadow_label,
            f"{r.get('score','')}점",
            str(pri.get("trigger_status", "—")) and "D+1~D+3 회복 트리거 대기",
            "연구용 · 매수 추천 아님" if shadow_label != "—" else "—",
        ])
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.34]); ax.axis("off")
    _add_table(ax,
               ["종목", "LIVE 분류", "Shadow 분류", "점수", "Shadow 상태", "주의"],
               rows,
               [0.24, 0.14, 0.20, 0.08, 0.20, 0.14],
               header_color="#dbeafe", scale=1.9)

    explain = [
        "• LIVE = 오늘 15:00 실제 Discord 웹훅에 들어간 후보. 기준은 ‘기존 거래대금 기준(P0)’.",
        "• Shadow = Codex 의 연구용 감시. 같은 종목이라도 ‘D0 강세종가 + 눌림 회복 트리거 대기’ 라벨이 추가로 붙어 있을 수 있습니다.",
        "• 같은 종목이 두 분류에 같이 잡혔다고 ‘승률이 높다’ 는 뜻은 아닙니다. ‘두 시각 모두에서 보이는 후보’ 정도의 의미입니다.",
        "• Shadow 후보는 매수 추천이 아닙니다. D+1~D+3 안에 회복 트리거가 실제로 일어나는지 사후 검증하기 위한 기록입니다.",
        "• 운영(LIVE) 으로 전환하려면 Codex 가 robust shadow source 파일을 정식화하고 사용자가 승인해야 합니다.",
    ]
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.36]); ax2.axis("off")
    ax2.text(0.0, 1.0, "\n".join(explain), fontsize=10.5, color="#374151", va="top",
             linespacing=1.7, wrap=True)
    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def page_7_next(pdf: PdfPages, ctx: dict[str, Any]) -> None:
    """8. 다음에 확인할 것"""
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("다음에 확인할 것", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 8, "다음에 확인할 것")

    sections = [
        ("내일 (장마감 + 17:05 PostClose 후)", [
            "오늘 LIVE 후보의 D+1 결과 — 일봉 고가/저가로 +1/+2/+3% 도달과 -2% 터치 확인.",
            "분봉이 있는 종목은 +3 와 -2 중 어느 게 먼저인지 (선후관계) 까지 확인.",
            "Pullback Reclaim 감시 종목에 실제 회복 트리거가 발생했는지 확인.",
        ]),
        ("이번 주 안에", [
            "오늘 후보의 D+1~D+5 누적 결과 — 어디까지 가고 어디서 흔들렸는지.",
            "데이터 최신성이 매일 [정상] 인지 — [주의]/[위험] 이 자주 보이면 17:05 PostClose 점검.",
            "Pullback Reclaim 누적 — 트리거 발생 비율과 발생 시 결과.",
        ]),
        ("연구 (Codex 영역)", [
            "v2 점수제 — robust variant 찾기 (단일 variant 채택 전 과최적화 위험 점검).",
            "액면가/유통주식수/가격대 feature 가능성 — D0 후보 성과와의 상관 확인.",
            "Shadow 카테고리 확장 — VWAP 회복 / 전일 눌림 고가 회복 / IPO 별도.",
        ]),
        ("운영 경계선 (변경 금지 항목)", [
            "후보 선정 로직 · 점수 산식 · D0 조건 · 웹훅 발송 로직.",
            "주문 / 계좌 API / 자동매매 / 실거래 자동주문 — 일절 사용하지 않음.",
            "webhook URL / API key 출력 금지.",
        ]),
    ]
    y = 0.79
    for title, bullets in sections:
        ax_t = fig.add_axes([0.04, y - 0.035, 0.92, 0.035]); ax_t.axis("off")
        ax_t.text(0.0, 0.5, title, fontsize=12, fontweight="bold", color="#1f2937", va="center")
        height = 0.020 + 0.040 * len(bullets)
        ax_b = fig.add_axes([0.04, y - 0.035 - height, 0.92, height]); ax_b.axis("off")
        text = "\n".join(f"  •  {line}" for line in bullets)
        ax_b.text(0.0, 1.0, text, fontsize=10.5, color="#374151", va="top", linespacing=1.7, wrap=True)
        y -= (0.035 + height + 0.012)

    _footer(fig, ctx["target_date"]); pdf.savefig(fig); plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().date().isoformat())
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    target_date = args.date[:10]
    out_path = Path(args.out) if args.out else Path(
        rf"C:\Users\PYJ\Downloads\CLOSINGBELL_DAILY_REVIEW_{target_date.replace('-', '')}.pdf"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ctx = _data_ctx(target_date)
    with PdfPages(out_path) as pdf:
        page_1_conclusion_and_basis(pdf, ctx)
        page_2_value_vs_score(pdf, ctx)
        page_3_touch_vs_winrate(pdf, ctx)
        page_4_pullback_reclaim(pdf, ctx)
        page_5_freshness(pdf, ctx)
        page_6_live_vs_shadow(pdf, ctx)
        page_7_next(pdf, ctx)
    print(f"PDF saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
