"""
V2 단계 전환 로드맵 — 한글 상세 PDF 생성기.

목적: 사용자가 묻는 세 가지에 한 PDF 로 답한다.
    1. 대시보드 V2 완전 전환이 가능한가?
    2. 온라인화 (외부 접속·매일 자동) 가능한가?
    3. 웹훅 메시지 V2 전환 가능한가?  (최종 = V2 Top3 방향)

페이지 구성 (16~18 pages, A4 가로, Malgun Gothic):
    1. 표지 + 한 페이지 결론 (세 질문 × 한 줄 답)
    2. V2 vs P0 핵심 증거 (한 달 / 1 년 / 분봉)
    3. 분봉 D+1~D+5 누적 도달표 (gain/loss 6 기준)
    4. 왜 백데이터 ≠ 운영 (슬리피지·호가공백·체결지연·미래누수)
    5. 데이터 누락 36% — excluded 사유 분포
    6. 정책 변형 비교 (Top3 / Top2 / 55점↑ × D0종가 / D+1시가)
    7. 권장 정책 — BEST_SCORE_TOP3_PROXY × D0_CLOSE
    8. 대시보드 변경안 — 메인 카드 V2화 + 비교 fallback
    9. 온라인화 옵션 비교 (Cloudflare Tunnel / Streamlit Cloud / VM)
   10. 온라인화 5분 절차 (Cloudflare Tunnel)
   11. 웹훅 단계 전환 — Phase 0~4
   12. 웹훅 SHADOW 메시지 mockup (Discord)
   13. 일일 운영 체크리스트 (preclose / postclose)
   14. 절대 건드리지 말 것 — 운영 경계선
   15. 다음 결정 사항 — Codex / Claude / 사용자 분담
   16. 부록 — 핵심 수치 한 표
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch

# Korean font
for tf in (Path(r"C:\Windows\Fonts\malgun.ttf"), Path(r"C:\Windows\Fonts\malgunbd.ttf")):
    if tf.exists():
        font_manager.fontManager.addfont(str(tf))
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"C:\Coding")
SUMMARY_MINUTE = ROOT / "data" / "closingbell" / "research_index" / \
    "minute_threshold_p0_vs_v2_top3_20260513" / "minute_threshold_p0_vs_v2_summary_20260513.csv"
SUMMARY_DPLUS = ROOT / "data" / "closingbell" / "research_index" / \
    "v2_top3_dplus_return_table_20260513" / "v2_vs_p0_top3_dplus_summary_20260513.csv"
SUMMARY_CHART_AUDIT = ROOT / "data" / "closingbell" / "research_index" / \
    "v2_chart_audit_20260513" / "v2_chart_audit_summary_20260513.csv"
EXCLUDED_MINUTE = ROOT / "data" / "closingbell" / "research_index" / \
    "minute_threshold_p0_vs_v2_top3_20260513" / "minute_threshold_p0_vs_v2_excluded_20260513.csv"

A4_LANDSCAPE = (11.7, 8.3)

# ===== 공통 유틸 =====
def _read(p: Path) -> pd.DataFrame:
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


def _page_header(fig, title: str, sub: str | None = None) -> None:
    """페이지 상단 큰 제목 + 색 띠."""
    ax = fig.add_axes([0.0, 0.92, 1.0, 0.08]); ax.axis("off")
    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.04, 0.55, title, fontsize=17, fontweight="bold", color="white", va="center")
    if sub:
        ax.text(0.96, 0.55, sub, fontsize=10, color="#cbd5e0", va="center", ha="right")


def _footer(fig, page_no: int, total: int) -> None:
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.035]); ax.axis("off")
    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, transform=ax.transAxes,
                           facecolor="#f1f5f9", edgecolor="none"))
    ax.text(0.04, 0.5,
            f"ClosingBell V2 단계 전환 로드맵  ·  생성 {datetime.now().strftime('%Y-%m-%d %H:%M')}  "
            "·  연구·검토용 — 매수 추천 아님 · 자동매매 연결 아님",
            fontsize=8, color="#475569", va="center")
    ax.text(0.96, 0.5, f"{page_no} / {total}", fontsize=8, color="#475569", va="center", ha="right")


def _section_band(fig, y: float, num: int, title: str, color: str = "#dbeafe") -> None:
    ax = fig.add_axes([0.04, y, 0.92, 0.045]); ax.axis("off")
    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, transform=ax.transAxes,
                           facecolor=color, edgecolor="none"))
    ax.text(0.01, 0.5, f"{num}. {title}", fontsize=12, fontweight="bold",
            color="#1e3a8a", va="center")


def _table(ax, header: list[str], rows: list[list[str]], col_widths: list[float],
           header_color: str = "#e0e7ff", font_size: int = 9, scale: float = 1.7,
           cell_align: str = "left") -> None:
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=10, color="#999"); return
    t = ax.table(cellText=rows, colLabels=header, loc="upper left",
                 cellLoc=cell_align, colWidths=col_widths)
    t.auto_set_font_size(False); t.set_fontsize(font_size); t.scale(1.0, scale)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor(header_color); cell.set_text_props(weight="bold", color="#1e3a8a")
        else:
            cell.set_facecolor("#ffffff" if (r - 1) % 2 == 0 else "#f8fafc")


def _verdict_pill(ax, x: float, y: float, label: str, color: str, text_color: str = "white") -> None:
    ax.add_patch(FancyBboxPatch((x, y), 0.13, 0.05, boxstyle="round,pad=0.005",
                                 transform=ax.transAxes, facecolor=color, edgecolor="none"))
    ax.text(x + 0.065, y + 0.025, label, fontsize=10, fontweight="bold",
            color=text_color, ha="center", va="center", transform=ax.transAxes)


# ===== 페이지 1 — 표지 + 한 페이지 결론 =====
def page_1_cover(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)

    # 표지 상단
    ax = fig.add_axes([0.0, 0.78, 1.0, 0.22]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.04, 0.72, "ClosingBell — V2 단계 전환 로드맵",
            fontsize=22, fontweight="bold", color="white", va="center")
    ax.text(0.04, 0.40,
            "대시보드 V2 완전 전환 · 외부 온라인화 · 웹훅 V2 메시지 — 가능 여부와 단계 평가",
            fontsize=12, color="#dbeafe", va="center")
    ax.text(0.04, 0.18,
            f"작성: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  Claude Code  ·  연구·검토용 PDF",
            fontsize=10, color="#cbd5e0", va="center")

    # 세 질문 × 한 줄 답
    _section_band(fig, 0.69, 0, "한 페이지 결론 — 세 질문 × 한 줄 답", color="#fef3c7")

    ax = fig.add_axes([0.04, 0.40, 0.92, 0.28]); ax.axis("off")

    qa = [
        ("Q1.", "대시보드를 V2 로 완전 전환 (P0 삭제) 가능한가?",
         "기술적으로 가능하지만 권장하지 않습니다. V2 산출물의 데이터 누락률이 36% (22/66) 라 P0 fallback 없이 운영하면 빈 화면이 자주 발생합니다. "
         "지금은 '메인 카드 V2 우선 + P0 비교 fallback' 이 가장 안전합니다.",
         "조건부 가능", "#f59e0b"),
        ("Q2.", "대시보드 외부 온라인화 (휴대폰·외부 PC 접속) 가능한가?",
         "지금 즉시 가능합니다. Cloudflare Tunnel 로 5분 안에 임시 URL 발급 (PC 켜진 동안). 24/7 필요하면 옵션 B(클라우드 스토리지) "
         "또는 옵션 C(VM) 로 단계 확장. 분봉 차트만 빠진 경량 Streamlit Cloud 도 가능.",
         "지금 가능", "#10b981"),
        ("Q3.", "웹훅 메시지 V2 전환 가능한가? (최종 = V2 Top3 방향)",
         "SHADOW (연구용) 발송은 지금 가능합니다. 코드에 shadow_mode 플래그와 [SHADOW] 헤더는 이미 있습니다. "
         "다만 PROD 본문 단독 사용은 최소 2주~1개월 paper watch + 사용자 명시 승인 이후로 미뤄야 합니다.",
         "SHADOW만 가능", "#3b82f6"),
    ]
    y = 0.95
    for marker, q, a, pill, pill_color in qa:
        ax.text(0.0, y, marker, fontsize=13, fontweight="bold", color="#1e3a8a", va="top")
        ax.text(0.045, y, q, fontsize=11.5, fontweight="bold", color="#111827", va="top", wrap=True)
        _verdict_pill(ax, 0.85, y - 0.045, pill, pill_color)
        ax.text(0.045, y - 0.08, a, fontsize=10, color="#374151", va="top", wrap=True)
        y -= 0.32

    # 핵심 증거 4줄
    _section_band(fig, 0.10, 0, "핵심 백데이터 증거 (요약)", color="#dcfce7")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.05]); ax.axis("off")
    bullets = [
        "•  한 달 (22 거래일) D0 종가 진입 — V2 승률 72.7% vs P0 30.3% (Δ +42.4%p), 중앙 MAE V2 -1.8% vs P0 -6.5%.",
        "•  1년 (252 거래일) D+1 시가 진입 — V2 승률 37.0% vs P0 22.9% (Δ +14.1%p), 슬리피지·호가공백 미반영.",
        "•  분봉 D+5 누적 +3% 도달 — V2 100% vs P0 85.7%, 단 -3% 도달도 V2 40.5% (변동성 큼).",
        "•  데이터 누락률 V2 36% vs P0 26% — 매일 V2 후보가 0~3개로 들쭉날쭉. 운영 전환 전 데이터 안정화 필수.",
    ]
    ax.text(0.0, 1.0, "\n".join(bullets), fontsize=9.5, color="#374151",
            va="top", linespacing=1.7)

    _footer(fig, 1, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 2 — V2 vs P0 핵심 증거표 =====
def page_2_evidence(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "2. V2 vs P0 핵심 증거 — 한눈에", "한 달 · 1 년 · 분봉 D+5")

    # 일봉 한 달 / 1 년 — D+1~D+5 종가 기준
    _section_band(fig, 0.83, 1, "일봉 D+1~D+5 종가 기준 (한 달 + 1 년)")
    ax = fig.add_axes([0.04, 0.59, 0.92, 0.24]); ax.axis("off")
    rows = [
        ["한 달 (22일)", "기존 거래대금 Top3 (P0)", "66",  "84.85%", "83.33%", "78.79%", "17.00%", "-6.67%"],
        ["한 달 (22일)", "V2 점수제 Top3",           "66",  "90.91%", "90.91%", "40.91%", "26.45%", "-1.83%"],
        ["1 년 (252일)", "기존 거래대금 Top3 (P0)",  "755", "84.77%", "80.13%", "79.34%", "9.92%",  "-6.75%"],
        ["1 년 (252일)", "V2 점수제 Top3",           "755", "94.44%", "92.58%", "57.48%", "18.42%", "-2.59%"],
    ]
    _table(ax, ["기간", "정책", "표본", "+2 도달", "+3 도달", "-2 터치", "D+5 최고중앙", "D+5 최저중앙"],
           rows, [0.11, 0.27, 0.07, 0.11, 0.11, 0.11, 0.11, 0.11],
           header_color="#bfdbfe", scale=1.9, cell_align="center")

    # 15시 진입 + 다음날 ±2 시뮬
    _section_band(fig, 0.53, 2, "15시 진입 → 다음날 ±2 % 선터치 시뮬 (분봉)")
    ax = fig.add_axes([0.04, 0.30, 0.92, 0.22]); ax.axis("off")
    rows = [
        ["한 달", "기존 거래대금 Top3", "다음날 11:30",  "63",  "42.86%", "57.14%", "0.0%",  "-0.29%"],
        ["한 달", "V2 점수제 Top3",     "다음날 11:30",  "59",  "69.49%", "23.73%", "5.08%", "0.79%"],
        ["1 년",  "기존 거래대금 Top3", "다음날 11:30",  "702", "45.73%", "46.30%", "7.26%", "-0.02%"],
        ["1 년",  "V2 점수제 Top3",     "다음날 11:30",  "699", "63.66%", "29.33%", "6.15%", "0.68%"],
        ["1 년",  "V2 점수제 Top3",     "다음날 종가까지", "699", "64.23%", "29.76%", "5.15%", "0.69%"],
    ]
    _table(ax, ["기간", "정책", "청산규칙", "표본", "목표먼저", "손실먼저", "시간청산", "평균수익률"],
           rows, [0.07, 0.22, 0.16, 0.07, 0.13, 0.13, 0.11, 0.11],
           header_color="#bfdbfe", scale=1.9, cell_align="center")

    # 챠트 audit 결과
    _section_band(fig, 0.24, 3, "Codex 차트 검증 (V2 12,986 case audit) — 최고 variant 3 개")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.20]); ax.axis("off")
    rows = [
        ["BEST_SCORE_TOP3_PROXY", "D0 종가 진입",  "755", "59.87%", "12.86%", "+47.01%p"],
        ["V2_TOP3",               "D0 종가 진입",  "691", "55.43%", "16.93%", "+24.57%p"],
        ["P0_VALUE_TOP3",         "D0 종가 진입",  "696", "30.86%", "39.66%", "—"],
    ]
    _table(ax, ["선정 방식", "진입 기준", "표본", "승률", "패배율", "P0 대비 Δ승률"],
           rows, [0.30, 0.20, 0.10, 0.13, 0.13, 0.14],
           header_color="#dcfce7", scale=2.0, cell_align="center")

    _footer(fig, 2, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 3 — 분봉 D+5 누적 도달표 =====
def page_3_minute(pdf: PdfPages, total: int) -> None:
    df = _read(SUMMARY_MINUTE)
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "3. 분봉 D+1~D+5 누적 도달표", "6 가지 기준선 × 두 정책")

    ax = fig.add_axes([0.04, 0.05, 0.92, 0.86]); ax.axis("off")
    ax.text(0.0, 0.99,
            "분봉 기준 — 신호일 15:00~15:05 첫 종가 대비, 각 D+N 까지 누적 분봉 고가/저가가 ±1/±2/±3 % 선을 닿았는지.\n"
            "데이터가 없는 후보는 제외(분모 차감). 같은 신호일에 ±3 양쪽이 다 닿으면 ‘변동성 큼’ 으로 해석.",
            fontsize=10, color="#475569", va="top", linespacing=1.5, wrap=True)

    if not df.empty:
        df["horizon_day"] = pd.to_numeric(df["horizon_day"], errors="coerce")
        rows_22, rows_252 = [], []
        for _, r in df.iterrows():
            row = [
                str(r["policy_label_ko"]), f"D+{int(r['horizon_day'])}",
                f"{r['included_candidate_n']}/{r['raw_candidate_n']}",
                f"{r['ge_plus1_rate_pct']}%", f"{r['ge_plus2_rate_pct']}%", f"{r['ge_plus3_rate_pct']}%",
                f"{r['le_minus1_rate_pct']}%", f"{r['le_minus2_rate_pct']}%", f"{r['le_minus3_rate_pct']}%",
                f"{r['cum_mfe_median_pct']}%", f"{r['cum_mae_median_pct']}%",
            ]
            if r["scope"] == "RECENT_22_TRADING_DAYS":
                rows_22.append(row)
            else:
                rows_252.append(row)

        ax_a = fig.add_axes([0.04, 0.54, 0.92, 0.34]); ax_a.axis("off")
        ax_a.set_title("최근 22 거래일 (한 달)", fontsize=11, fontweight="bold",
                       loc="left", pad=4, color="#1e3a8a")
        _table(ax_a, ["정책", "구간", "포함/원본", "+1↑", "+2↑", "+3↑", "-1↓", "-2↓", "-3↓", "MFE중앙", "MAE중앙"],
               rows_22,
               [0.18, 0.06, 0.10, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.09, 0.09],
               header_color="#bfdbfe", font_size=8.5, scale=1.5, cell_align="center")

        ax_b = fig.add_axes([0.04, 0.07, 0.92, 0.46]); ax_b.axis("off")
        ax_b.set_title("최근 252 거래일 (1 년)", fontsize=11, fontweight="bold",
                       loc="left", pad=4, color="#1e3a8a")
        _table(ax_b, ["정책", "구간", "포함/원본", "+1↑", "+2↑", "+3↑", "-1↓", "-2↓", "-3↓", "MFE중앙", "MAE중앙"],
               rows_252,
               [0.18, 0.06, 0.10, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.09, 0.09],
               header_color="#e0e7ff", font_size=8.5, scale=1.5, cell_align="center")

    _footer(fig, 3, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 4 — 백데이터 ≠ 운영 =====
def page_4_backdata_caveat(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "4. 왜 백데이터 ≠ 운영", "전환 전에 반드시 분리해야 할 4 가지 미반영 요소")

    ax = fig.add_axes([0.04, 0.05, 0.92, 0.85]); ax.axis("off")
    ax.text(0.0, 0.99,
            "위 페이지의 V2 승률·도달률은 모두 ‘과거에 어떻게 됐었을까’ 결과입니다.\n"
            "다음 네 가지는 백데이터에서 이미 제거되어 있고, 운영 단계에서 별도 보정이 필요합니다.",
            fontsize=11, color="#374151", va="top", linespacing=1.55)

    items = [
        ("①", "체결가 슬리피지 (slippage)",
         "분봉 종가는 ‘마지막 체결가’ 입니다. 실제 시장가 매수는 호가창의 매도 1~3 호가를 잡아먹으며 평균 0.3~1.5% 위에서 체결됩니다. "
         "V2 의 +2% 목표가도, 0.5% 슬리피지가 들어가면 실제 익절선은 +2.5%↑ 이 되어야 같은 성공률을 냅니다."),
        ("②", "호가 공백 (price gap / liquidity hole)",
         "거래량이 적은 종목, 또는 15:00 종가 직후 호가창이 얇은 종목은 -2% 손절선보다 훨씬 아래에서 체결됩니다. "
         "특히 다음날 시가 갭다운은 손절선을 건너뛰고 -5~-10% 에서 잡힙니다. 백데이터의 ‘-2% 손실먼저’ 비율은 실제로는 더 큰 손실을 의미합니다."),
        ("③", "체결 지연 (latency / queue position)",
         "분봉의 ‘±2% 선 터치’ 는 1초 단위 가격으로 판정합니다. 실거래에서는 주문 송신 → 거래소 처리 → 호가창 도착 까지 수백 ms~수 초 지연이 있고, "
         "그 사이 가격이 빠르게 움직이면 의도한 가격으로 잡지 못합니다."),
        ("④", "미래 누수 (look-ahead leakage) 잔존 위험",
         "V2 점수가 ‘D0 종가 직후 산출 가능한 정보’ 만 쓰는지, 아니면 D+1 일부 정보가 섞였는지 — 점수 산식의 운영 분리가 끝나야 안전합니다. "
         "현재 점수 산식은 연구 스크립트(d0_webhook_v2_score_experiment_20260513.py) 형태로만 존재하며, bell-data 의 매일 자동 산출 경로에 정식 편입 안 됨."),
    ]
    y = 0.86
    for marker, title, body in items:
        ax.text(0.0, y, marker, fontsize=18, fontweight="bold", color="#1e3a8a", va="top")
        ax.text(0.035, y - 0.005, title, fontsize=12, fontweight="bold", color="#111827", va="top")
        ax.text(0.035, y - 0.045, body, fontsize=10, color="#374151", va="top", wrap=True, linespacing=1.5)
        y -= 0.21

    # 마지막 박스 — 의미
    ax_box = fig.add_axes([0.04, 0.04, 0.92, 0.06]); ax_box.axis("off")
    ax_box.add_patch(FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.01",
                                     transform=ax_box.transAxes,
                                     facecolor="#fee2e2", edgecolor="#dc2626", linewidth=1.0))
    ax_box.text(0.02, 0.5,
                "▶ 보정 미반영분 = 백데이터 승률에서 실제 5~15%p 정도 깎아서 해석해야 합니다. "
                "V2 한 달 72.7% 도 실제로는 55~65% 영역으로 보는 것이 안전합니다.",
                fontsize=10.5, color="#7f1d1d", fontweight="bold", va="center")

    _footer(fig, 4, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 5 — 데이터 누락 36% =====
def page_5_missing_data(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "5. 데이터 누락 36% — 매일 V2 가 0~3 개로 들쭉날쭉", "운영 전환 직전 최대 장애물")

    _section_band(fig, 0.83, 1, "최근 22 거래일 V2 포함 / 제외 현황")
    ax = fig.add_axes([0.04, 0.62, 0.92, 0.20]); ax.axis("off")
    rows = [
        ["D+1", "66", "56", "10", "15.2%"],
        ["D+2", "66", "52", "14", "21.2%"],
        ["D+3", "66", "48", "18", "27.3%"],
        ["D+4", "66", "45", "21", "31.8%"],
        ["D+5", "66", "42", "24", "36.4%"],
    ]
    _table(ax, ["구간", "원본 후보 수", "포함", "제외", "제외율"],
           rows, [0.15, 0.20, 0.20, 0.20, 0.20],
           header_color="#fde68a", scale=1.9, cell_align="center")

    _section_band(fig, 0.53, 2, "주요 제외 사유 (excluded CSV 178 행)")
    ax2 = fig.add_axes([0.04, 0.30, 0.92, 0.22]); ax2.axis("off")
    rows = [
        ["entry_1500_missing",            "15:00~15:05 첫 분봉 종가가 없는 후보 (저유동·정지)",            "약 50%"],
        ["dplus1_minute_or_future_missing","D+1 ~ D+5 분봉이 일부/전부 누락",                                   "약 40%"],
        ["future_daily_days_less_than_5", "신호일 이후 5 거래일치 일봉이 아직 안 쌓임 (최근 신호 한정)",       "약 8%"],
        ["data_freshness_stale",          "daily/minute 최신 갱신일이 운영일 기준 미달",                       "약 2%"],
    ]
    _table(ax2, ["excluded_reason", "의미", "전체 중 비중"],
           rows, [0.30, 0.50, 0.20],
           header_color="#fde68a", scale=2.0)

    # 의미 + 결론
    _section_band(fig, 0.22, 3, "운영적 의미와 처리 방향", color="#fef3c7")
    ax3 = fig.add_axes([0.04, 0.04, 0.92, 0.18]); ax3.axis("off")
    items = [
        "▶ V2 후보 3 개 중 평균 0.6~1.1 개가 매일 ‘데이터 없음’ 으로 빠집니다 → 강제로 3 개를 채우면 백데이터 통계가 무너집니다.",
        "▶ ‘유효 V2 후보 최대 3 개’ 정책 — 부족하면 0 개·1 개·2 개로 표시. 강제 3 개 채우기 금지.",
        "▶ excluded 후보는 별도 ‘보류 목록 (Hold)’ 으로 명시 — 사용자가 사유를 보고 직접 판단 가능.",
        "▶ 운영 전환 전제 조건: 최근 5 거래일 연속 V2 유효 후보 ≥ 2 개가 안정적으로 채워질 것 (데이터 안정성 게이트).",
    ]
    ax3.text(0.0, 0.99, "\n".join(items), fontsize=10.5, color="#92400e",
             va="top", linespacing=1.7, fontweight="bold")

    _footer(fig, 5, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 6 — 정책 변형 비교 =====
def page_6_policy_variants(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "6. 정책 변형 비교 — 최종 V2 어떤 모양?", "Top3 무조건 / Top2 / 55점↑ 최대 3개")

    _section_band(fig, 0.84, 1, "최근 한 달, D0 종가 진입 기준")
    ax = fig.add_axes([0.04, 0.62, 0.92, 0.21]); ax.axis("off")
    rows = [
        ["기존 거래대금 3개",      "당일 종가 기준", "66", "3.0",  "30.30%", "37.88%", "31.82%", "17.00",  "-6.49"],
        ["V2 상위 3개",            "당일 종가 기준", "66", "3.0",  "72.73%", "7.58%",  "19.70%", "26.45",  "-1.82"],
        ["V2 상위 2개",            "당일 종가 기준", "44", "2.0",  "77.27%", "4.55%",  "18.18%", "27.10",  "-1.24"],
        ["V2 55점 이상 최대 3개",  "당일 종가 기준", "47", "2.24", "78.72%", "2.13%",  "19.15%", "31.08",  "-0.90"],
    ]
    _table(ax, ["정책", "진입", "표본", "하루평균", "성공률", "실패률", "애매", "최고중앙(MFE)", "최저중앙(MAE)"],
           rows, [0.20, 0.13, 0.07, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
           header_color="#bfdbfe", scale=2.0, cell_align="center")

    _section_band(fig, 0.55, 2, "최근 일 년, 다음날 시가 진입 기준 (실전성)")
    ax2 = fig.add_axes([0.04, 0.33, 0.92, 0.21]); ax2.axis("off")
    rows = [
        ["기존 거래대금 3개",      "다음날 시가",   "752", "3.0",  "22.87%", "44.81%", "32.31%", "9.01",  "-6.92"],
        ["V2 상위 3개",            "다음날 시가",   "752", "3.0",  "36.97%", "21.94%", "41.09%", "15.86", "-4.10"],
        ["V2 상위 2개",            "다음날 시가",   "502", "2.0",  "39.84%", "18.53%", "41.63%", "17.22", "-3.62"],
        ["V2 55점 이상 최대 3개",  "다음날 시가",   "430", "2.04", "43.49%", "16.28%", "40.23%", "19.07", "-3.05"],
    ]
    _table(ax2, ["정책", "진입", "표본", "하루평균", "성공률", "실패률", "애매", "최고중앙(MFE)", "최저중앙(MAE)"],
           rows, [0.20, 0.13, 0.07, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
           header_color="#e0e7ff", scale=2.0, cell_align="center")

    # 트레이드오프 해설
    _section_band(fig, 0.25, 3, "세 가지 변형의 트레이드오프")
    ax3 = fig.add_axes([0.04, 0.04, 0.92, 0.20]); ax3.axis("off")
    items = [
        "•  V2 상위 3개: 매일 후보가 안정적으로 3 개. 표본 많음. 단 점수 30~40 점대 약한 종목도 잡히면 실패률 올라감.",
        "•  V2 상위 2개: 더 보수적. 한 달 성공률 +4.5%p, 실패률 -3%p. 단 하루 후보 평균 2 개 → 변동 적은 날 발송 빈도 ↓.",
        "•  V2 55점 이상 최대 3개: 가장 보수적·가장 안정적 — 한 달 성공률 78.7%, 실패률 2.1%. 단 점수 미달 날은 후보 0 개도 발생 (~5% of days).",
        "•  실전성(D+1 시가) 으로 가면 세 변형 모두 약해지며 차이는 5~7%p 로 좁혀짐 → 슬리피지 + 갭다운 영향.",
    ]
    ax3.text(0.0, 0.95, "\n".join(items), fontsize=10.5, color="#374151",
             va="top", linespacing=1.7)

    _footer(fig, 6, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 7 — 권장 정책 =====
def page_7_recommendation(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "7. 권장 정책 — 최종 V2 의 모양", "표시·발송 분리 + 보수적 변형")

    # 추천 박스
    ax_box = fig.add_axes([0.04, 0.74, 0.92, 0.16]); ax_box.axis("off")
    ax_box.add_patch(FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.01",
                                     transform=ax_box.transAxes,
                                     facecolor="#dcfce7", edgecolor="#16a34a", linewidth=1.5))
    ax_box.text(0.02, 0.83, "▶ 권장 — 운영 V2 정책",
                fontsize=14, fontweight="bold", color="#14532d", va="center")
    ax_box.text(0.02, 0.50,
                "•  선정: V2 점수 55 점 이상 (혹은 상위 분위수 기준), 최대 3 개. 부족하면 강제로 채우지 않음 (0~3 개 변동).\n"
                "•  진입: 표시는 ‘D0 종가 기준 / D+1 시가 기준’ 둘 다, 운영 가정은 ‘D+1 시가 + 슬리피지 0.5% 보정’.\n"
                "•  청산: 다음날 +2% / -2% 선 터치 우선 + 11:30 시간청산 (백데이터 목표먼저 69.5%).\n"
                "•  IPO 후보 자동 V2 에서 제외 (사용자 수동 영역). Risk Alert 는 후보 아닌 경고 섹션.",
                fontsize=10.5, color="#1f2937", va="center", linespacing=1.6)

    # 왜 이 변형인가
    _section_band(fig, 0.66, 1, "왜 ‘55 점 이상, 최대 3 개’ 변형인가")
    ax = fig.add_axes([0.04, 0.40, 0.92, 0.25]); ax.axis("off")
    rows = [
        ["성공률 (한 달, D0 종가)",   "78.7%",  "= 최고 — Top3 무조건(72.7%) 대비 +6%p"],
        ["실패률 (한 달, D0 종가)",   "2.1%",   "= 최저 — Top3(7.6%) 대비 -5.5%p"],
        ["최대 하락 중앙 (MAE)",       "-0.9%",  "= 가장 얕음 — 슬리피지 보정해도 -2~-3% 안에서 끝"],
        ["1 년 D+1 시가 성공률",      "43.5%",  "= 1 년 기준 최고 — 실전성 가정에서도 우위 유지"],
        ["하루 평균 후보 수",          "2.24개", "≥ 1 개 이상 채워지는 날 = 95%"],
    ]
    _table(ax, ["지표", "값", "근거 / 의미"], rows, [0.30, 0.18, 0.52],
           header_color="#dcfce7", scale=1.85)

    # 표시 정책
    _section_band(fig, 0.32, 2, "표시 규칙 — 사용자에게 보이는 모양", color="#fef3c7")
    ax2 = fig.add_axes([0.04, 0.04, 0.92, 0.27]); ax2.axis("off")
    items = [
        "1.  메인 카드 (대시보드 홈): V2 유효 후보 1~3 개. 점수 / D0 등락률 / 데이터 최신성 뱃지 표시.",
        "2.  보류 목록 (Hold): 점수 미달 또는 데이터 누락으로 빠진 V2 원본 후보 + 사유.",
        "3.  비교 fallback (P0): 기존 거래대금 Top3 를 별도 카드로 유지 — 디버그·검증·하위호환.",
        "4.  D+1 결과 카드: 운영일 다음날 17:05 postclose 이후 채워짐. 현재일 후보에는 미래 결과 절대 노출 금지.",
        "5.  문구: ‘연구/감시용·매수 추천 아님·자동매매 연결 아님’ 매 화면 푸터에 박제.",
        "6.  도달률 ≠ 승률 표시 — 어디든 도달률 숫자 옆에 ‘변동성 도달이며 승률 아님’ 캡션.",
    ]
    ax2.text(0.0, 0.97, "\n".join(items), fontsize=10.5, color="#92400e",
             va="top", linespacing=1.7, fontweight="bold")

    _footer(fig, 7, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 8 — 대시보드 변경안 =====
def page_8_dashboard_plan(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "8. 대시보드 변경안 — 메인 카드 V2 화", "현재 6 탭 구조 유지 + 홈 카드 교체")

    # 현재 vs 권장
    _section_band(fig, 0.85, 1, "현재 vs 권장 구조")
    ax = fig.add_axes([0.04, 0.55, 0.45, 0.30]); ax.axis("off")
    ax.set_title("현재 (V2 는 5번째 탭에만)", fontsize=11, fontweight="bold",
                 color="#1e3a8a", loc="left", pad=4)
    rows = [
        ["1. 홈",                   "LIVE P0 후보 카드 (V20 정책)"],
        ["2. D0 감시 종목 전체",    "P0 점수 풀 표"],
        ["3. 1 년치 복기",          "P0 슬롯 단위 종목 상세"],
        ["4. 통계",                 "P0 성과 통계"],
        ["5. V2 차트 검증",         "Codex audit 50 PNG 갤러리 (완료)"],
        ["6. 메모",                 "수동 메모"],
    ]
    _table(ax, ["탭", "내용"], rows, [0.45, 0.55],
           header_color="#e0e7ff", scale=1.7)

    ax2 = fig.add_axes([0.51, 0.55, 0.45, 0.30]); ax2.axis("off")
    ax2.set_title("권장 (홈 카드 V2 우선)", fontsize=11, fontweight="bold",
                  color="#1e3a8a", loc="left", pad=4)
    rows = [
        ["1. 홈",                   "V2 유효 후보 (1~3) + 보류 + P0 비교"],
        ["2. D0 감시 종목 전체",    "P0 + V2 점수 동시 표"],
        ["3. 1 년치 복기",          "유지 (P0 슬롯 + V2 슬롯 토글)"],
        ["4. 통계",                 "P0 + V2 두 축 통계"],
        ["5. V2 차트 검증",         "유지"],
        ["6. 메모",                 "유지"],
    ]
    _table(ax2, ["탭", "내용"], rows, [0.45, 0.55],
           header_color="#dcfce7", scale=1.7)

    # 홈 화면 mock
    _section_band(fig, 0.48, 2, "홈 화면 mock — V2 우선 + P0 비교 fallback")
    ax3 = fig.add_axes([0.04, 0.07, 0.92, 0.40]); ax3.axis("off")
    mock = [
        "+-------------------------------------------------------------------------------------------------+",
        "|  [TOP]  V2 유효 후보 (오늘)  —  연구/감시용 · 매수 추천 아님         [데이터 갱신 OK]            |",
        "|  +-------------------------+-------------------------+-------------------------+               |",
        "|  |  1위  점수 67.5          |  2위  점수 61.2          |  3위  점수 58.4          |               |",
        "|  |  종목  대한광통신 010170  |  종목  한온시스템 018880  |  종목  아주IB투자 027360  |               |",
        "|  |  D0  +12.8% · 강세종가    |  D0  +8.3% · 얕은 눌림    |  D0  +5.7% · 테마 모멘텀  |               |",
        "|  |  D+1 시가 진입 가정 표시  |  D+1 시가 진입 가정 표시  |  D+1 시가 진입 가정 표시  |               |",
        "|  +-------------------------+-------------------------+-------------------------+               |",
        "|                                                                                                 |",
        "|  [보류]  V2 보류 (2 개) — 점수 / 데이터 사유 표시. 강제 채우기 없음.                              |",
        "|     - 선도전기 007610 (점수 38.2, 데이터 최신성 미달)                                            |",
        "|     - 민테크   452200 (점수 27.0, 점수 기준 55 점 미달)                                          |",
        "|                                                                                                 |",
        "|  [참고]  P0 거래대금 Top3 (비교 fallback)  —  과거 정책 유지 · 검증용                            |",
        "|     1) 종목A  2) 종목B  3) 종목C   같은 줄에 점수·등락·D+1 결과 (있을 때만)                      |",
        "|                                                                                                 |",
        "|  [주의]  도달률 != 승률  ·  백데이터 결과 · 자동매매 연결 아님 · IPO 는 수동 영역                 |",
        "+-------------------------------------------------------------------------------------------------+",
    ]
    ax3.text(0.0, 0.97, "\n".join(mock), fontsize=8.5, color="#1f2937",
             va="top", family="Malgun Gothic")

    _footer(fig, 8, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 9 — 온라인화 옵션 비교 =====
def page_9_online_options(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "9. 온라인화 옵션 비교", "Cloudflare Tunnel · Streamlit Cloud · VM")

    _section_band(fig, 0.84, 1, "세 가지 경로")
    ax = fig.add_axes([0.04, 0.30, 0.92, 0.54]); ax.axis("off")
    rows = [
        ["A. Cloudflare Tunnel\n(임시·즉시)",
         "본인 PC 켠 동안",
         "5 분",
         "0 원",
         "분봉·일봉 모두 동작",
         "본인 PC 가 켜져 있어야. 외출·취침 시 차단.",
         "**즉시 시작 권장**"],
        ["B. Streamlit Community Cloud\n(경량·24/7)",
         "GitHub 무료",
         "30 분",
         "0 원",
         "통계·V2 표·메모 동작. 분봉·일봉 차트 X (parquet 못 올림).",
         "데이터 ~10 MB 만. 분봉 차트 비활성. V2 표·도달률은 정상.",
         "장기 무료 대안"],
        ["C. 클라우드 VM (AWS / GCP / Oracle Cloud)\n(풀 기능·24/7)",
         "Linux VM",
         "1~3 시간",
         "월 $5~15",
         "분봉·일봉·차트 모두 동작. 매일 자동 데이터 sync 가능.",
         "Oracle Cloud Free Tier (Always Free) 로 비용 0 원 가능 (수동 세팅).",
         "운영 전환 후 권장"],
    ]
    _table(ax, ["옵션", "필요 환경", "세팅 시간", "비용", "데이터 / 기능", "제약 / 비고", "권장 시점"],
           rows, [0.18, 0.10, 0.08, 0.08, 0.22, 0.20, 0.14],
           header_color="#bfdbfe", scale=2.2, font_size=9)

    _section_band(fig, 0.22, 2, "권장 단계 — A → C", color="#dcfce7")
    ax2 = fig.add_axes([0.04, 0.04, 0.92, 0.18]); ax2.axis("off")
    items = [
        "1.  Phase 1 (지금): Cloudflare Tunnel 로 본인 PC 의 streamlit 을 외부 URL 로 노출. 휴대폰·외부 PC 에서 접속 확인.",
        "2.  Phase 2 (2주 후): bell-data 에 매일 자동 V2 산출 추가 + sync 스크립트 작성. 데이터 안정성 게이트 통과 시점.",
        "3.  Phase 3 (1개월 후): Oracle Cloud Free Tier VM 으로 이전, GitHub Actions 또는 cron 으로 매일 데이터 sync. PC 의존 제거.",
        "4.  Streamlit Cloud (B) 는 ‘분봉 없는 경량판’ 으로 별도 — 외부 공유·시연용 정도. 메인 대시보드는 A 또는 C.",
    ]
    ax2.text(0.0, 0.97, "\n".join(items), fontsize=10.5, color="#14532d",
             va="top", linespacing=1.7, fontweight="bold")

    _footer(fig, 9, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 10 — Cloudflare Tunnel 5분 절차 =====
def page_10_cloudflare(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "10. Cloudflare Tunnel 5 분 절차", "지금 즉시 외부 접속 만들기")

    ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")
    blocks = [
        ("Step 1.  cloudflared 설치 (Windows PowerShell, 1 회만)",
         "winget install --id Cloudflare.cloudflared\n"
         "cloudflared --version    # 버전 확인 (예: 2024.x.x)"),
        ("Step 2.  Streamlit 실행 (별도 PowerShell 창)",
         "cd C:\\Coding\\projects\\bell-dashboard\n"
         ".\\scripts\\run_dashboard.ps1\n"
         "    --server.address 127.0.0.1 --server.port 8501\n"
         "# 로컬 확인: http://127.0.0.1:8501"),
        ("Step 3.  Tunnel 띄우기 (또 다른 PowerShell 창, 임시 URL)",
         "cloudflared tunnel --url http://127.0.0.1:8501\n"
         "# 콘솔 출력 예:\n"
         "# Your quick Tunnel has been created! Visit it at:\n"
         "# https://random-words-1234.trycloudflare.com"),
        ("Step 4.  휴대폰·외부 PC 에서 URL 접속 — 끝.",
         "휴대폰 브라우저 → 위 URL 입력 → 본인 대시보드 그대로 보임.\n"
         "HTTPS 자동 / DDoS 보호 자동 / 포트 포워딩 불필요.\n"
         "PC 끄거나 cloudflared 종료하면 자동으로 외부 접속 차단."),
        ("Step 5. (선택) 영구 URL — 도메인 있을 때",
         "cloudflared tunnel login          # 브라우저 로그인\n"
         "cloudflared tunnel create bell    # 터널 생성\n"
         "cloudflared tunnel route dns bell bell.mydomain.com\n"
         "cloudflared tunnel run bell\n"
         "# 이후 https://bell.mydomain.com 으로 영구 접속"),
    ]
    y = 0.97
    for h, code in blocks:
        ax.text(0.0, y, h, fontsize=12, fontweight="bold", color="#1e3a8a", va="top")
        ax.text(0.02, y - 0.04, code, fontsize=10, color="#111827",
                va="top", family="Malgun Gothic", linespacing=1.5)
        y -= 0.18

    # 주의
    ax_box = fig.add_axes([0.04, 0.03, 0.92, 0.06]); ax_box.axis("off")
    ax_box.add_patch(FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.01",
                                     transform=ax_box.transAxes,
                                     facecolor="#fef3c7", edgecolor="#d97706", linewidth=1.0))
    ax_box.text(0.02, 0.5,
                "[주의] 임시 URL 은 cloudflared 재시작마다 바뀝니다. 매일 같은 주소가 필요하면 Step 5 의 영구 URL 또는 옵션 C(VM) 로.",
                fontsize=10, color="#78350f", fontweight="bold", va="center")

    _footer(fig, 10, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 11 — 웹훅 단계 전환 =====
def page_11_webhook_phases(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "11. 웹훅 V2 단계 전환 — Phase 0 ~ 4", "PROD 단독 = 마지막 단계")

    ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")

    phases = [
        ("Phase 0",  "현재 (지금)",
         "LIVE P0 발송. shadow_mode 플래그·[SHADOW] 헤더 코드는 있으나 V2 본문 섹션 미구현.",
         "#94a3b8"),
        ("Phase 1",  "V2 SHADOW 섹션 추가 + SHADOW URL 만 발송",
         "Discord SHADOW 채널 별도 생성 → bell-webhook 에 render_v2_shadow_block() 추가 → "
         "webhook_shadow_sections_*.csv 를 매일 읽어 V2 Top3 + 보류 + Data Guard 섹션 발송. "
         "PROD 채널은 P0 그대로. 절대 매수 신호처럼 보이지 않게 ‘연구용·paper watch’ 문구 강조.",
         "#3b82f6"),
        ("Phase 2",  "PROD 본문에 V2 SHADOW 섹션 병기 (2~4 주 paper watch 후)",
         "PROD 채널의 P0 메시지 뒤에 V2 SHADOW 섹션을 ‘참고 정보’ 로 추가. 발송 주체·발송 URL 은 변경 없음. "
         "사용자가 매일 같은 화면에서 P0 와 V2 를 동시에 비교 가능. SHADOW 마크는 유지.",
         "#10b981"),
        ("Phase 3",  "V2 PROD 본문 단독 + P0 fallback 카드 (1~2 개월 paper watch 후)",
         "메인 후보 표시를 V2 로 교체. P0 는 ‘비교 참고’ 작은 박스로 축소. 발송 빈도·URL 동일. "
         "사용자가 명시적 승인 한 시점에만 진행. SHADOW 헤더 제거 — 단 매수 신호는 여전히 아님.",
         "#f59e0b"),
        ("Phase 4",  "P0 완전 제거 (3 개월 이상 안정 운영 후, 선택사항)",
         "P0 산출·표시·발송 코드 전부 제거. 데이터 디렉토리는 아카이브로 이동. "
         "이 단계는 영구 결정이라 백테스트 비교축이 사라짐. 가급적 Phase 3 에서 멈추는 것 권장.",
         "#ef4444"),
    ]
    y = 0.96
    for tag, title, body, color in phases:
        # 단계 박스
        ax.add_patch(FancyBboxPatch((0.0, y - 0.16), 0.08, 0.14, boxstyle="round,pad=0.005",
                                     transform=ax.transAxes, facecolor=color, edgecolor="none"))
        ax.text(0.04, y - 0.09, tag, fontsize=12, fontweight="bold",
                color="white", ha="center", va="center", transform=ax.transAxes)
        # 본문
        ax.text(0.10, y - 0.02, title, fontsize=11.5, fontweight="bold",
                color="#111827", va="top")
        ax.text(0.10, y - 0.06, body, fontsize=10, color="#374151",
                va="top", wrap=True, linespacing=1.5)
        y -= 0.18

    _footer(fig, 11, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 12 — 웹훅 SHADOW 메시지 mockup =====
def page_12_webhook_mock(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "12. 웹훅 V2 SHADOW 메시지 mockup", "Phase 1 — SHADOW 채널 발송 예시")

    ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")
    msg = [
        "===============================================================================",
        "  [SHADOW] ClosingBell V2 SHADOW (연구용)  ·  운영 미반영 · 매수 추천 아님       ",
        "===============================================================================",
        "  신호일: 2026-05-14 (수)   |   slot: postclose 17:05                          ",
        "  데이터 최신성: daily 2026-05-14 OK / minute 2026-05-14 OK / 15:00 기준가 OK   ",
        "",
        "[ V2 유효 후보 ]  (오늘 2 / 최대 3)  —  점수 55점 이상 · D0 종가 진입 가정       ",
        "                                                                                ",
        "  1)  대한광통신  010170   점수 67.5  ·  D0 +12.8 %                              ",
        "        패턴: 강세종가 추세 지속                                                 ",
        "        해석: D+1 시가 진입 가정 / 슬리피지 0.5% 보정 시 +1.5% 안전권             ",
        "                                                                                ",
        "  2)  한온시스템  018880   점수 61.2  ·  D0 +8.3 %                               ",
        "        패턴: 얕은 눌림 방어                                                     ",
        "        해석: 거래대금 견조, MAE 중앙 -1.3% -> -2% 손절선 적합                    ",
        "                                                                                ",
        "[ V2 보류 ]  (3)  —  점수·데이터 사유 표시 · 강제 채우기 없음                     ",
        "  -  선도전기  007610  점수 38.2  (점수 미달 + 데이터 최신성 미달)                ",
        "  -  민테크    452200  점수 27.0  (점수 미달)                                     ",
        "  -  센서뷰    321370  점수  -    (entry_1500_missing  ·  15:00 기준가 없음)      ",
        "                                                                                ",
        "[ Data Guard ]                                                                  ",
        "    daily latest = minute latest = 2026-05-14  ·  miss rate 최근 5일 평균 18%    ",
        "    안정성 게이트: 5일 연속 V2 유효 >= 2  (현재 4/5)                              ",
        "                                                                                ",
        "[ P0 비교 (참고) ]                                                              ",
        "    P0 거래대금 Top3 = 종목A · 종목B · 종목C  ·  P0 한 달 승률 30.3 %             ",
        "                                                                                ",
        "-------------------------------------------------------------------------------",
        "  도달률 != 승률  ·  백데이터 결과 · 슬리피지·갭 미반영 · 매수 지시 아님          ",
        "  점수 산식 V2 (코드 v2_score_experiment_20260513) · IPO 자동 제외                ",
        "===============================================================================",
    ]
    ax.text(0.0, 0.99, "\n".join(msg), fontsize=8.7, color="#1f2937",
            va="top", family="Malgun Gothic", linespacing=1.45)

    _footer(fig, 12, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 13 — 일일 운영 체크리스트 =====
def page_13_daily_checklist(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "13. 일일 운영 체크리스트", "preclose 14:55 / postclose 17:05 / 익일 09:30")

    ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")

    sections = [
        ("[시간 14:55]  Preclose — 장 마감 5 분 전", "#1e3a8a", [
            "[ ]  bell-data run_preclose_candidates → 오늘 V2 점수 산출 정상 완료",
            "[ ]  V2 유효 후보 수 >= 1 (안 그러면 SHADOW 발송 보류)",
            "[ ]  데이터 최신성 daily latest = 오늘, minute latest = 오늘 14:00 이후",
            "[ ]  IPO 후보·Risk Alert 자동 제외 확인",
            "[ ]  Discord SHADOW 채널 발송 (Phase 1+): V2 Top3 + 보류 + Data Guard",
        ]),
        ("[시간 17:05]  Postclose — 당일 정리", "#10b981", [
            "[ ]  bell-data run_postclose_refresh → 오늘 15:00~15:30 분봉 보강",
            "[ ]  15:00 기준가 (entry_1500) 가 모든 V2 후보에 채워졌는지",
            "[ ]  어제 V2 후보의 D+1 결과 카드 갱신 — 매수 / 매도 시뮬 등락률",
            "[ ]  excluded 사유 분포 — 새 사유 코드 없는지 (예측 못 한 결측)",
            "[ ]  대시보드 -> 홈 -> V2 카드 정상 표시 (휴대폰 Cloudflare Tunnel 로 확인 가능)",
        ]),
        ("[시간 익일 09:30]  장 시작 후 30 분", "#f59e0b", [
            "[ ]  어제 V2 후보 D+1 시가 진입가 (호가창 갭다운 여부 메모)",
            "[ ]  -2% 손절선 / +2% 익절선 분봉 터치 시간 기록 (paper watch 메모만)",
            "[ ]  주문/계좌 연결 절대 금지 (PROD 매매 코드 없음 확인)",
        ]),
        ("[주간 금요일 17:30]  주간 리뷰", "#7c3aed", [
            "[ ]  이번주 V2 후보 매일 유효 개수 (안정성 게이트)",
            "[ ]  슬리피지 가정 후 실제 승률 = 백데이터 - 5~10%p 와 일치하는지",
            "[ ]  excluded 후보 사유 변화 추세",
            "[ ]  Phase 2 / 3 진입 결정 — 안정성 + 누적 표본 + 사용자 판단",
        ]),
    ]
    y = 0.96
    for title, color, items in sections:
        ax.text(0.0, y, title, fontsize=12.5, fontweight="bold", color=color, va="top")
        body = "\n".join(items)
        ax.text(0.02, y - 0.05, body, fontsize=10, color="#374151",
                va="top", linespacing=1.7, family="Malgun Gothic")
        y -= 0.23

    _footer(fig, 13, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 14 — 절대 건드리지 말 것 =====
def page_14_dont_touch(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "14. 절대 건드리지 말 것 — 운영 경계선", "전 단계 공통 가드")

    ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")

    dont = [
        ("[ X ]  주문 / 계좌 / 자동매매 연결",
         "어떤 단계에서도 한국투자증권·키움·yj_bot 등 실거래 API 호출 추가 금지. "
         "V2 발송은 '디스코드 메시지 한 줄' 까지만."),
        ("[ X ]  현재일 후보에 D+1~D+5 결과 노출",
         "오늘 발송한 후보 옆에 미래 결과 (예: 내일 등락률) 가 보이면 look-ahead 누수. "
         "복기 화면(1년치 탭) 에만 표시. 메인 카드는 '아직 결과 없음' 으로 둠."),
        ("[ X ]  데이터 없음을 채우기",
         "entry_1500_missing 인 후보를 D0 종가로 fallback 채우기 금지. "
         "'15:00 기준가 없음' 으로 표시하고 보류 분류. 분봉 누락도 마찬가지."),
        ("[ X ]  점수 산식 운영 분기 변경",
         "현재 V2 점수 산식은 연구 스크립트 (d0_webhook_v2_score_experiment_20260513.py) 형태. "
         "운영 매일 산출로 정식 편입 전, 점수 weight 변경·feature 추가 금지. 변경하려면 같은 audit (12,986 case) 재실행 후 비교."),
        ("[ X ]  V2 PROD 본문 단독 전환을 자동 트리거로",
         "Phase 3 진입은 사용자 명시 승인 → 한 줄 메시지 (예: 'V2 PROD 단독 전환 OK') 가 있는 시점에만. "
         "스케줄러·CI 자동 전환 절대 금지."),
        ("[ X ]  IPO 후보 자동 V2 편입",
         "IPO 는 사용자 수동 영역. V2 자동 산출 단계에서 IPO 코드는 필터로 빼고, 'IPO 감시' 별도 섹션만 유지."),
    ]
    y = 0.97
    for h, body in dont:
        ax.text(0.0, y, h, fontsize=12.5, fontweight="bold", color="#7f1d1d", va="top")
        ax.text(0.025, y - 0.05, body, fontsize=10.5, color="#374151",
                va="top", linespacing=1.6, wrap=True)
        y -= 0.155

    _footer(fig, 14, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 15 — 다음 결정 사항 =====
def page_15_next_decisions(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "15. 다음 결정 사항 — 책임 분담", "사용자 · Claude · Codex")

    ax = fig.add_axes([0.04, 0.07, 0.92, 0.83]); ax.axis("off")

    actors = [
        ("[ 사용자 ]", "#1e3a8a", [
            "1.  세 가지 정책 변형 중 어떤 걸로 갈지 결정 — (1) V2 Top3 무조건  (2) V2 Top2  (3) V2 55점↑ 최대 3개 (권장).",
            "2.  Cloudflare Tunnel 으로 Phase 1 온라인화 즉시 진행할지 (PC 가 자주 켜져 있는지 / 24/7 필요한지).",
            "3.  Discord SHADOW 채널 별도 개설 — V2 SHADOW 메시지 발송 시작 시점 (Phase 1).",
            "4.  Phase 2 (PROD 본문 병기) 진입 기준 — paper watch 며칠? 권장 14~28 일.",
            "5.  IPO 자동 제외 OK 한지 (현재 수동 영역 가정).",
        ]),
        ("[ Claude ] (이 세션 이후)", "#10b981", [
            "1.  bell-dashboard 홈 카드를 V2 우선 + P0 fallback 으로 교체 (코드 변경 ~150 줄 예상).",
            "2.  bell-webhook 에 render_v2_shadow_block() 추가 — webhook_shadow_sections_*.csv 를 매일 읽고 SHADOW 본문 생성.",
            "3.  대시보드 보류·excluded 카드 추가 (3~4 줄 표).",
            "4.  Cloudflare Tunnel 설치 안내 + Streamlit Cloud 옵션 A 분기점 README 보강.",
            "5.  주간 리뷰 자동 PDF (이 PDF 의 '오늘만 V2' 버전) — Phase 2 진입 후.",
        ]),
        ("[ Codex ]", "#f59e0b", [
            "1.  bell-data 에 produce_v2_top3_daily() 정식 함수 — preclose 14:55 / postclose 17:05 슬롯 자동 산출.",
            "2.  점수 산식 robust variant 검증 — BEST_SCORE_TOP3_PROXY 채택 전 다른 weight 조합 비교.",
            "3.  D+1 시가 슬리피지·호가 공백 보정 모델 — 백데이터 승률에 -5~-10%p 자동 차감 표시.",
            "4.  Pullback Reclaim 트리거형과 V2 결합 가능성 audit.",
            "5.  데이터 최신성 게이트 함수화 — '5일 연속 V2 유효 >= 2' 자동 판정.",
        ]),
    ]
    y = 0.96
    for title, color, items in actors:
        ax.text(0.0, y, title, fontsize=13, fontweight="bold", color=color, va="top")
        body = "\n".join(items)
        ax.text(0.025, y - 0.05, body, fontsize=10, color="#374151",
                va="top", linespacing=1.7, wrap=True)
        y -= 0.31

    _footer(fig, 15, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 16 — 부록: 핵심 수치 한 표 =====
def page_16_appendix(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _page_header(fig, "16. 부록 — 핵심 수치 한 표", "본 문서 전체 근거")

    _section_band(fig, 0.86, 1, "한 줄 비교 (한 달 D0 종가)")
    ax = fig.add_axes([0.04, 0.68, 0.92, 0.18]); ax.axis("off")
    rows = [
        ["기존 거래대금 Top3 (P0)", "66",  "30.30%", "37.88%", "17.00%", "-6.49%", "—"],
        ["V2 Top3",                  "66",  "72.73%", "7.58%",  "26.45%", "-1.82%", "+42.43%p"],
        ["V2 Top2",                  "44",  "77.27%", "4.55%",  "27.10%", "-1.24%", "+46.97%p"],
        ["V2 55점↑ 최대 3개 (권장)", "47",  "78.72%", "2.13%",  "31.08%", "-0.90%", "+48.42%p"],
        ["BEST_SCORE_TOP3_PROXY (audit, 1년)", "755", "59.87%", "12.86%", "—", "—", "+29.01%p (vs P0 1년)"],
    ]
    _table(ax, ["정책", "표본", "성공률", "실패률", "MFE중앙", "MAE중앙", "P0 대비 Δ승률"],
           rows, [0.32, 0.07, 0.12, 0.12, 0.12, 0.12, 0.13],
           header_color="#dcfce7", scale=1.9, cell_align="center")

    _section_band(fig, 0.60, 2, "분봉 D+5 누적 도달 (한 달)")
    ax2 = fig.add_axes([0.04, 0.42, 0.92, 0.17]); ax2.axis("off")
    rows = [
        ["P0 거래대금 Top3", "49 / 66 (26% 제외)", "89.80%", "89.80%", "85.71%", "91.84%", "87.76%", "83.67%"],
        ["V2 Top3",          "42 / 66 (36% 제외)", "100.00%","100.00%","100.00%","69.05%", "57.14%", "40.48%"],
    ]
    _table(ax2, ["정책", "포함/원본", "+1%↑", "+2%↑", "+3%↑", "-1%↓", "-2%↓", "-3%↓"],
           rows, [0.20, 0.18, 0.10, 0.10, 0.10, 0.10, 0.10, 0.12],
           header_color="#bfdbfe", scale=1.9, cell_align="center")

    _section_band(fig, 0.34, 3, "15시 진입 → 다음날 ±2 시뮬")
    ax3 = fig.add_axes([0.04, 0.16, 0.92, 0.17]); ax3.axis("off")
    rows = [
        ["P0", "한 달", "다음날 11:30",     "63",  "42.86%", "57.14%", "0.00%", "-0.29%"],
        ["V2", "한 달", "다음날 11:30",     "59",  "69.49%", "23.73%", "5.08%", "+0.79%"],
        ["P0", "1 년", "다음날 종가까지",   "702", "46.01%", "47.15%", "6.13%", "-0.02%"],
        ["V2", "1 년", "다음날 종가까지",   "699", "64.23%", "29.76%", "5.15%", "+0.69%"],
    ]
    _table(ax3, ["정책", "기간", "청산", "표본", "목표먼저", "손실먼저", "시간청산", "평균수익률"],
           rows, [0.08, 0.10, 0.18, 0.08, 0.14, 0.14, 0.13, 0.15],
           header_color="#fde68a", scale=1.9, cell_align="center")

    # 출처
    ax_src = fig.add_axes([0.04, 0.05, 0.92, 0.09]); ax_src.axis("off")
    src = [
        "출처 CSV:",
        "  · minute_threshold_p0_vs_v2_top3_20260513/minute_threshold_p0_vs_v2_summary_20260513.csv",
        "  · v2_top3_dplus_return_table_20260513/v2_vs_p0_top3_dplus_summary_20260513.csv",
        "  · v2_1500_nextday_exit_sim_20260513/*.csv",
        "  · v2_chart_audit_20260513/v2_chart_audit_summary_20260513.csv (Codex audit)",
        "  · v2_shadow_top3_policy_20260513/*.csv",
    ]
    ax_src.text(0.0, 1.0, "\n".join(src), fontsize=8.5, color="#475569",
                va="top", family="Malgun Gothic", linespacing=1.5)

    _footer(fig, 16, total); pdf.savefig(fig); plt.close(fig)


# ===== Main =====
def build(out_path: Path) -> None:
    summary_minute = _read(SUMMARY_MINUTE)
    if summary_minute.empty:
        print(f"[warn] {SUMMARY_MINUTE} not found — page 3 will be empty.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 16
    with PdfPages(out_path) as pdf:
        page_1_cover(pdf, total)
        page_2_evidence(pdf, total)
        page_3_minute(pdf, total)
        page_4_backdata_caveat(pdf, total)
        page_5_missing_data(pdf, total)
        page_6_policy_variants(pdf, total)
        page_7_recommendation(pdf, total)
        page_8_dashboard_plan(pdf, total)
        page_9_online_options(pdf, total)
        page_10_cloudflare(pdf, total)
        page_11_webhook_phases(pdf, total)
        page_12_webhook_mock(pdf, total)
        page_13_daily_checklist(pdf, total)
        page_14_dont_touch(pdf, total)
        page_15_next_decisions(pdf, total)
        page_16_appendix(pdf, total)

    size_kb = out_path.stat().st_size / 1024
    print(f"[ok] {out_path}  ({size_kb:.1f} KB, {total} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(r"C:\Users\PYJ\Downloads\V2_MIGRATION_ROADMAP_KR_20260514.pdf"))
    args = ap.parse_args()
    build(args.out)
