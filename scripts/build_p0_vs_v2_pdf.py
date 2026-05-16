"""
Build a one-shot PDF comparing LIVE webhook (P0 거래대금 기준) vs v2 (점수제) for ClosingBell.

- 운영 cli·후보 선정·점수 산식·웹훅 발송과 무관한 표시용 산출물.
- 산출 위치: 인자 --out 또는 기본 C:\\Users\\PYJ\\Downloads\\CLOSINGBELL_P0_VS_V2_REPORT_<YYYYMMDD>.pdf
- 데이터 소스:
    score_breakdown_{date}.csv              (LIVE Top5 with score)
    webhook_picks_5d_{date}.csv             (LIVE with d0_price/d0_trading_value)
    pullback_reclaim_watch_{date}.csv       (D0 pool with score_total_100 + watch_type)
    Codex audit/score_vs_value_top3_comparison_*.csv (1년치 성과 비교)
    Codex audit/baseline_value_top3_top5_touch_*.csv  (Top3/Top5 baseline)
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

# ----- Korean font -----
KOREAN_TTF = Path(r"C:\Windows\Fonts\malgun.ttf")
if KOREAN_TTF.exists():
    font_manager.fontManager.addfont(str(KOREAN_TTF))
    plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"C:\Coding")
WATCHLISTS = ROOT / "data" / "closingbell" / "shared" / "watchlists"
PULLBACK_DIR = ROOT / "data" / "closingbell" / "paper_watch" / "pullback_reclaim"
AUDIT_ZIP_DIR = Path(r"C:\Users\PYJ\AppData\Local\Temp\d0_score_audit_20260513\D0_SCORE_TOP3_TOUCH_AUDIT_20260513")


def _read(p: Path) -> pd.DataFrame:
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


def _fmt_value(value: Any) -> str:
    """원 단위 거래대금 → '2,360억' 형식."""
    try:
        n = float(str(value).replace(",", ""))
    except Exception:
        return "—"
    return f"{n / 1_0000_0000:,.0f}억"


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(float(str(value).replace(',', ''))):,}"
    except Exception:
        return "—"


def _fmt_pct(value: Any) -> str:
    try:
        return f"{float(value):+.2f}%"
    except Exception:
        return "—"


def page_today_comparison(pdf: PdfPages, target_date: str) -> None:
    """Page 1: 오늘 LIVE(P0 거래대금) vs v2(점수 desc) 사이드 바이 사이드."""
    score = _read(WATCHLISTS / f"score_breakdown_{target_date.replace('-','')}.csv")
    picks = _read(WATCHLISTS / f"webhook_picks_5d_{target_date.replace('-','')}.csv")
    if score.empty:
        print(f"[skip page1] score_breakdown_{target_date} not found")
        return
    # P0 ordering: rank as-is
    score["_rank_n"] = pd.to_numeric(score["rank"], errors="coerce").fillna(99).astype(int)
    p0 = score.sort_values("_rank_n").reset_index(drop=True)
    # v2 ordering: score desc
    score["_score_n"] = pd.to_numeric(score["score"], errors="coerce").fillna(0).astype(int)
    v2 = score.sort_values("_score_n", ascending=False).reset_index(drop=True)

    # join picks for d0_date, d0_price, d0_trading_value
    if not picks.empty:
        picks_idx = picks.set_index("stock_code").to_dict(orient="index")
    else:
        picks_idx = {}

    def _table_for(df: pd.DataFrame, rank_col_label: str) -> tuple[list[str], list[list[str]]]:
        header = ["순위", "구분", "종목", "점수", "거래대금", "D0 종가", "D0 원천일"]
        body: list[list[str]] = []
        for i, (_, r) in enumerate(df.iterrows(), start=1):
            code = str(r.get("stock_code", "")).zfill(6)
            pinfo = picks_idx.get(code, {})
            role = str(r.get("role", ""))
            role_label = {"BODY_TOP2": "본문", "REFERENCE_RANK3": "참고", "LOG_ONLY": "보조"}.get(role, role)
            body.append([
                str(i),
                role_label,
                f"{r.get('stock_name','')} ({code})",
                str(r.get("score", "")),
                _fmt_value(pinfo.get("d0_trading_value", "")),
                _fmt_int(pinfo.get("d0_price", "")),
                str(pinfo.get("d0_date", ""))[:10] or "—",
            ])
        return header, body

    fig = plt.figure(figsize=(11.7, 8.3))  # A4 landscape
    fig.suptitle(f"ClosingBell — LIVE(P0 거래대금) vs v2(점수제) 후보 비교  ·  {target_date}",
                 fontsize=15, fontweight="bold", y=0.97)

    # 헤더 주의 박스
    note_ax = fig.add_axes([0.04, 0.86, 0.92, 0.07])
    note_ax.axis("off")
    note_text = (
        "추천 종목 아님 · 자동매매 아님 · 수동 확인용  ·  "
        "동일한 5개 D0 후보를 두 가지 기준(거래대금 / 점수)으로 재정렬한 비교입니다.\n"
        "v2(점수제)는 연구용이며 운영 웹훅에는 반영되지 않습니다."
    )
    note_ax.text(0.0, 0.5, note_text, fontsize=10, color="#444", va="center",
                 bbox=dict(facecolor="#fff8e0", edgecolor="#f6ad55", boxstyle="round,pad=0.6"))

    # LIVE 표
    left_ax = fig.add_axes([0.04, 0.08, 0.46, 0.74])
    left_ax.axis("off")
    left_ax.set_title("[LIVE]  기존 거래대금 기준 (P0)", fontsize=12, fontweight="bold",
                      loc="left", pad=12, color="#1a7f37")
    h, b = _table_for(p0, "거래대금 순")
    t1 = left_ax.table(cellText=b, colLabels=h, loc="upper left", cellLoc="left",
                       colWidths=[0.07, 0.13, 0.28, 0.10, 0.16, 0.13, 0.13])
    t1.auto_set_font_size(False); t1.set_fontsize(9); t1.scale(1.0, 1.5)
    for (r, c), cell in t1.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor("#e8f5e9"); cell.set_text_props(weight="bold")

    # v2 표
    right_ax = fig.add_axes([0.52, 0.08, 0.46, 0.74])
    right_ax.axis("off")
    right_ax.set_title("[v2]  점수제 순(연구용 · 운영 미반영)", fontsize=12, fontweight="bold",
                       loc="left", pad=12, color="#7e22ce")
    h2, b2 = _table_for(v2, "점수 desc")
    t2 = right_ax.table(cellText=b2, colLabels=h2, loc="upper left", cellLoc="left",
                        colWidths=[0.07, 0.13, 0.28, 0.10, 0.16, 0.13, 0.13])
    t2.auto_set_font_size(False); t2.set_fontsize(9); t2.scale(1.0, 1.5)
    for (r, c), cell in t2.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor("#f3e8ff"); cell.set_text_props(weight="bold")

    # 하단 풋노트
    foot_ax = fig.add_axes([0.04, 0.02, 0.92, 0.06])
    foot_ax.axis("off")
    foot_ax.text(0.0, 0.5,
                 f"데이터: score_breakdown_{target_date}.csv · webhook_picks_5d_{target_date}.csv  ·  "
                 f"생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  "
                 "운영 cli·점수 산식 변경 없음",
                 fontsize=8, color="#666", va="center")
    pdf.savefig(fig); plt.close(fig)


def page_one_year_comparison(pdf: PdfPages) -> None:
    """Page 2: Codex 1년치 audit — 거래대금 baseline vs 점수제 SCORE_TOP5."""
    src = _read(AUDIT_ZIP_DIR / "score_vs_value_top3_comparison_20260513.csv")
    base = _read(AUDIT_ZIP_DIR / "baseline_value_top3_top5_touch_20260513.csv")
    if src.empty and base.empty:
        print("[skip page2] audit csv not found")
        return

    fig = plt.figure(figsize=(11.7, 8.3))
    fig.suptitle("1년치 성과 — 거래대금 기준(P0) vs 점수제(v2)", fontsize=15, fontweight="bold", y=0.97)

    # 핵심 4행 추출
    key_rows: list[list[str]] = []
    if not src.empty:
        keep = [
            ("D0 거래대금 순위 Top3", "거래대금 Top3 (P0)"),
            ("D0 거래대금 순위 Top5", "거래대금 Top5 (P0)"),
            ("점수제 SCORE_TOP5 median", "점수제 SCORE_TOP5 (v2, median)"),
            ("강세종가 Policy A", "강세종가 Policy A (참고)"),
        ]
        for src_label, display in keep:
            r = src[src["group"] == src_label]
            if r.empty: continue
            r = r.iloc[0]
            scope = str(r.get("rank_scope", ""))
            key_rows.append([
                display,
                scope.replace("D0_VALUE_", "").replace("WEBHOOK_", "WEBHOOK ").replace("TOP3_WITHIN_SELECTED", "Top3"),
                _fmt_int(r.get("eligible_n", "")),
                f"{float(r.get('up2_touch_d5_pct','0')):.1f}%",
                f"{float(r.get('up3_touch_d5_pct','0')):.1f}%",
                f"{float(r.get('down2_touch_d5_pct','0')):.1f}%",
                f"{float(r.get('down3_touch_d5_pct','0')):.1f}%",
                f"{float(r.get('target2_before_risk2_d5_pct','0')):.1f}%",
                f"{float(r.get('target3_before_risk2_d5_pct','0')):.1f}%",
            ])

    note_ax = fig.add_axes([0.04, 0.86, 0.92, 0.07])
    note_ax.axis("off")
    note_ax.text(0.0, 0.5,
                 "터치율(touch)은 '5일 안에 가격이 닿은 적이 있나'이지 '승률'이 아닙니다.\n"
                 "+2/+3은 목표, -2/-3은 손절 영역. target_before_risk = +N%가 -2%보다 먼저 닿은 비율 (= 선후관계 승률).",
                 fontsize=10, color="#444", va="center",
                 bbox=dict(facecolor="#fff8e0", edgecolor="#f6ad55", boxstyle="round,pad=0.6"))

    ax = fig.add_axes([0.04, 0.12, 0.92, 0.70])
    ax.axis("off")
    ax.set_title("그룹별 5일 안 도달/터치 비율 (Codex audit 2026-05-13)", fontsize=12, fontweight="bold",
                 loc="left", pad=12)
    header = ["그룹", "범위", "표본", "+2% 도달", "+3% 도달", "-2% 터치", "-3% 터치", "+2 먼저", "+3 먼저"]
    if key_rows:
        t = ax.table(cellText=key_rows, colLabels=header, loc="upper left", cellLoc="left",
                     colWidths=[0.24, 0.10, 0.08, 0.10, 0.10, 0.10, 0.10, 0.09, 0.09])
        t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.0, 1.7)
        for (r, c), cell in t.get_celld().items():
            cell.set_edgecolor("#cbd5e0")
            if r == 0:
                cell.set_facecolor("#e8eef7"); cell.set_text_props(weight="bold")
            elif r in (1, 2):
                cell.set_facecolor("#f0fdf4" if r == 1 else "#f0fdf4")
            elif r == 3:
                cell.set_facecolor("#f3e8ff")
            elif r == 4:
                cell.set_facecolor("#fef3c7")

    foot_ax = fig.add_axes([0.04, 0.04, 0.92, 0.06])
    foot_ax.axis("off")
    foot_ax.text(0.0, 0.5,
                 "데이터: score_vs_value_top3_comparison_20260513.csv (Codex)  ·  "
                 "점수제 SCORE_TOP5 median = 4,566개 가중치 variant 중앙값  ·  "
                 "1년치 = 247 거래일",
                 fontsize=8, color="#666", va="center")
    pdf.savefig(fig); plt.close(fig)


def page_interpretation(pdf: PdfPages, target_date: str) -> None:
    """Page 3: 차이 해석 + 운영 경계선 + 다음 단계."""
    fig = plt.figure(figsize=(11.7, 8.3))
    fig.suptitle("해석 · 운영 경계선 · 다음 단계", fontsize=15, fontweight="bold", y=0.97)

    sections = [
        ("이 보고서를 보는 법", [
            "이 PDF는 같은 D0 후보 풀을 두 가지 기준(거래대금 P0 / 점수제 v2)으로 재정렬한 비교입니다.",
            "오늘 5/13 LIVE 웹훅은 P0(거래대금 정렬)로 발송되었습니다. v2(점수제) 는 운영에 들어가 있지 않습니다.",
            "1년치 통계는 Codex audit 결과입니다 — 표본·기간·조건은 표 옆 주석을 보세요.",
        ]),
        ("핵심 차이 (1년치)", [
            "+3% 도달률 — 거래대금 Top3 80.5% vs 점수제 SCORE_TOP5 median 88.5%. +8%p.",
            "-2% 터치율 — 거래대금 Top3 79.9% vs 점수제 SCORE_TOP5 median 68.4%. -11%p (낮을수록 좋음).",
            "+3 먼저 비율 — 거래대금 Top3 30.8% vs 점수제 SCORE_TOP5 median 46.0%. +15%p.",
            "선후관계 승률 차이가 의미 있게 보이지만 — 점수제는 4,566개 가중치 variant 중앙값이며,",
            "단일 variant 채택은 과최적화 위험이 있으므로 운영 전 robust 검증이 필요합니다.",
        ]),
        ("주의", [
            "터치율은 '5일 안에 한 번이라도 닿았나' 비율입니다. 자동매매 승률이 아닙니다.",
            "+3과 -2가 같은 날 함께 발생했을 때 '무엇이 먼저 닿았나'는 분봉이 있어야 확정됩니다.",
            "Pullback Reclaim 같은 트리거형 전략은 별도이며, 이 비교는 'D0 후 D+1~D+5 단순 추적'입니다.",
            "강세종가 Policy A 는 표본 472건 기준이며 D+5 +3% 88.98% — 참고용 보조 지표.",
        ]),
        ("운영 경계선", [
            "후보 선정 로직 · 점수 산식 · D0 조건 · 웹훅 발송 — 이 보고서로 변경 안 함.",
            "v2 채택 결정은 Codex 의 robust variant 분석 + 사용자 승인 후에만.",
            "이 PDF 는 표시·복기 용도이며 자동매매·실거래·계좌 API 와 무관.",
        ]),
        ("다음에 볼 것", [
            "오늘 LIVE 후보(대한광통신·한온시스템·아주IB투자) D+1 결과 — 5/14 장마감·17:05 PostClose 후.",
            "Codex 의 'pullback 단독' / 'paper watch' robust 변형들의 분산 (variant 간 안정성).",
            "Pullback Reclaim 트리거가 실제 D+1~D+3에 발생하는 종목 비율.",
        ]),
    ]

    y = 0.86
    for title, bullets in sections:
        ax_t = fig.add_axes([0.04, y - 0.04, 0.92, 0.04]); ax_t.axis("off")
        ax_t.text(0.0, 0.5, title, fontsize=12, fontweight="bold", color="#1f2937", va="center")
        height = 0.04 + 0.038 * len(bullets)
        ax_b = fig.add_axes([0.04, y - 0.04 - height, 0.92, height]); ax_b.axis("off")
        text = "\n".join(f"  •  {line}" for line in bullets)
        ax_b.text(0.0, 1.0, text, fontsize=10.5, color="#374151", va="top", wrap=True)
        y -= (0.04 + height + 0.012)

    foot_ax = fig.add_axes([0.04, 0.02, 0.92, 0.04]); foot_ax.axis("off")
    foot_ax.text(0.0, 0.5,
                 f"생성: {datetime.now().strftime('%Y-%m-%d %H:%M')} · ClosingBell 수동 복기 — 추천 종목 아님",
                 fontsize=8, color="#666", va="center")
    pdf.savefig(fig); plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().date().isoformat())
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    target_date = args.date[:10]
    out_path = Path(args.out) if args.out else Path(
        rf"C:\Users\PYJ\Downloads\CLOSINGBELL_P0_VS_V2_REPORT_{target_date.replace('-', '')}.pdf"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        page_today_comparison(pdf, target_date)
        page_one_year_comparison(pdf)
        page_interpretation(pdf, target_date)
    print(f"PDF saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
