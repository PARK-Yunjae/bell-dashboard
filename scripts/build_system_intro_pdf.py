"""ClosingBell 시스템 소개 PDF — PPT 슬라이드 풍.

개요 → D0 → 기존 거래대금(P0) → V2 → 벨가드 안정후보(HYBRID) 까지
시스템의 흐름을 한 페이지 한 메시지로 정리한다.

운영 코드는 변경하지 않으며, 본 PDF는 연구/소개 자료다.
매수 추천이나 자동매매 시사 문구는 들어가지 않는다.

usage:
    & C:\\Coding\\projects\\_venvs\\closingbell-py312\\Scripts\\python.exe \\
      C:\\Coding\\projects\\bell-dashboard\\scripts\\build_system_intro_pdf.py
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LATEST = REPO / "data" / "closingbell" / "online_v2" / "latest"
OUT_DIR = REPO / "data" / "closingbell" / "online_v2" / "latest"
OUT_PATH = OUT_DIR / f"CLOSINGBELL_SYSTEM_INTRO_{datetime.now():%Y%m%d}.pdf"

# Korean font setup
plt.rcParams["font.family"] = ["Malgun Gothic", "Apple SD Gothic Neo", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42  # TrueType embed

# Slide palette (light theme, modern flat)
BG = "#ffffff"
INK = "#0f172a"          # primary text
MUTED = "#64748b"        # secondary text
ACCENT = "#2563eb"       # blue (V2)
GREEN = "#16a34a"        # 벨가드 안정후보
GRAY = "#94a3b8"         # P0 거래대금
WARN = "#f97316"         # caution
LINE = "#e5e7eb"

PAGE_W, PAGE_H = 13.33, 7.5  # 16:9 슬라이드 (인치)


def _new_slide():
    fig = plt.figure(figsize=(PAGE_W, PAGE_H), dpi=200)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(BG)
    ax.set_axis_off()
    return fig, ax


def _footer(ax, slide_no: int, total: int, title: str):
    # bottom line
    ax.add_line(plt.Line2D([0.04, 0.96], [0.06, 0.06], color=LINE, lw=0.8))
    ax.text(0.04, 0.035, "ClosingBell · 연구/복기 자료 · 매수 추천 아님 · 자동매매 아님",
            color=MUTED, fontsize=8, ha="left", va="center")
    ax.text(0.96, 0.035, f"{slide_no} / {total}    {title}",
            color=MUTED, fontsize=8, ha="right", va="center")


def _title_top(ax, kicker: str, title: str, kicker_color: str = ACCENT):
    ax.text(0.05, 0.91, kicker, color=kicker_color, fontsize=14,
            fontweight="bold", ha="left", va="center")
    ax.text(0.05, 0.83, title, color=INK, fontsize=34, fontweight="bold",
            ha="left", va="center", linespacing=1.15)
    # title underline accent
    ax.add_patch(Rectangle((0.05, 0.78), 0.08, 0.006, facecolor=kicker_color, edgecolor="none"))


def _card(ax, x, y, w, h, *, color="#ffffff", edge=LINE, radius=0.018):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.002,rounding_size={radius}",
        facecolor=color, edgecolor=edge, linewidth=1.2
    ))


# ─────────────────────────── 슬라이드 정의 ────────────────────────────


def slide_cover(slide_no, total):
    fig, ax = _new_slide()
    # 좌상단 작은 라벨
    ax.text(0.05, 0.86, "CLOSINGBELL", color=ACCENT, fontsize=14,
            fontweight="bold", ha="left")
    # 큰 타이틀
    ax.text(0.05, 0.62, "한국 주식 D0 신호\n복기 시스템", color=INK, fontsize=58,
            fontweight="bold", ha="left", va="center", linespacing=1.05)
    # 부제
    ax.text(0.05, 0.36, "기존 거래대금 → V2 점수제 → 벨가드 안정후보\n세 갈래를 한 화면에서 비교하고 메모합니다.",
            color=MUTED, fontsize=18, ha="left", va="top", linespacing=1.5)
    # 좌하단 안내 카드
    _card(ax, 0.05, 0.10, 0.55, 0.09, color="#f8fafc")
    ax.text(0.07, 0.145, "Paper Watch · 매수 추천 아님 · 자동매매 아님",
            color=INK, fontsize=12, fontweight="bold", ha="left", va="center")
    # 우측 액센트 바
    ax.add_patch(Rectangle((0.83, 0.10), 0.005, 0.78, facecolor=ACCENT, edgecolor="none"))
    ax.text(0.86, 0.49, f"{datetime.now():%Y-%m-%d}", color=MUTED, fontsize=14,
            ha="left", va="center", rotation=0)
    _footer(ax, slide_no, total, "표지")
    return fig


def slide_overview(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "OVERVIEW", "한 줄로 요약하면")
    ax.text(0.05, 0.66,
            "매일 14:15 한국 시장에서 '강하게 움직이는 종목'을 골라",
            color=INK, fontsize=22, ha="left", va="center")
    ax.text(0.05, 0.58,
            "D+1~D+5 사이 +3% 먼저 / -3% 먼저 결과를 복기하는 시스템.",
            color=INK, fontsize=22, ha="left", va="center")
    # 3 카드: 핵심 원칙
    cards = [
        ("매일 14:15", "D0 신호 발생", "거래량·등락률로 후보 선별", ACCENT),
        ("매일 15:00", "Paper Watch 발송", "Discord 알림 — 매수 추천 아님", GREEN),
        ("매일 17:05", "데이터 갱신", "D+1~D+5 결과 사후 복기", GRAY),
    ]
    for i, (h, t, sub, c) in enumerate(cards):
        x = 0.05 + i * 0.31
        _card(ax, x, 0.20, 0.28, 0.26)
        ax.text(x + 0.02, 0.41, h, color=c, fontsize=12, fontweight="bold")
        ax.text(x + 0.02, 0.34, t, color=INK, fontsize=18, fontweight="bold", va="top")
        ax.text(x + 0.02, 0.25, sub, color=MUTED, fontsize=12, va="top",
                wrap=True)
    _footer(ax, slide_no, total, "개요")
    return fig


def slide_d0(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "STEP 1 · D0", "D0 — 신호가 발생하는 날")
    ax.text(0.05, 0.68,
            "그날 시장에서 '평소보다 크게 움직인 종목'을 D0 후보로 잡습니다.",
            color=INK, fontsize=18, ha="left")
    # D0 필터 카드
    _card(ax, 0.05, 0.18, 0.40, 0.46)
    ax.text(0.07, 0.58, "D0 필터", color=ACCENT, fontsize=13, fontweight="bold")
    rules = [
        "✓ KOSPI / KOSDAQ 보통주",
        "✗ ETF · ETN · SPAC · REIT · 우선주 제외",
        "✓ 거래량 10,000,000주 이상",
        "✓ 종가 2,000원 ~ 100,000원",
        "✓ 등락률 0% 초과",
        "✓ 최근 3거래일 active pool 유지",
    ]
    for i, r in enumerate(rules):
        ax.text(0.07, 0.52 - i * 0.055, r, color=INK, fontsize=14, va="top")
    # 우측: D0 의미
    _card(ax, 0.50, 0.18, 0.45, 0.46, color="#f8fafc")
    ax.text(0.52, 0.58, "D0 의 의미", color=GREEN, fontsize=13, fontweight="bold")
    ax.text(0.52, 0.51, "D0 = 감시 시작 신호",
            color=INK, fontsize=20, fontweight="bold", va="top")
    ax.text(0.52, 0.42,
            "D0는 매수 시점이 아닙니다.\n‘이 종목을 다음 5거래일 동안\n관찰해보자’ 는 표시입니다.",
            color=MUTED, fontsize=14, va="top", linespacing=1.55)
    _footer(ax, slide_no, total, "STEP 1 · D0")
    return fig


def slide_p0(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "STEP 2 · P0", "기존 방식 — 거래대금 Top3", kicker_color=GRAY)
    ax.text(0.05, 0.69,
            "D0 후보 중에서 그날 '돈이 가장 많이 몰린' 상위 3종목을 알림합니다.",
            color=INK, fontsize=18, ha="left")
    # 좌: 장점 / 우: 한계
    _card(ax, 0.05, 0.18, 0.42, 0.48)
    ax.text(0.07, 0.61, "장점", color=GREEN, fontsize=13, fontweight="bold")
    pros = [
        "단순하고 직관적",
        "유동성이 충분 → 실제 진입·청산 쉬움",
        "재료가 있는 종목이 자주 등장",
    ]
    for i, p in enumerate(pros):
        ax.text(0.07, 0.54 - i * 0.07, f"• {p}", color=INK, fontsize=14, va="top")
    _card(ax, 0.52, 0.18, 0.43, 0.48, color="#fff7ed", edge="#fed7aa")
    ax.text(0.54, 0.61, "한계", color=WARN, fontsize=13, fontweight="bold")
    cons = [
        "대형주·하이닉스 같은 거래대금 거인이",
        "  매번 1위라 후보가 거의 고정됨",
        "변동성·수익률 모두 평균 회귀",
        "1년 +3 먼저 약 55% — 동전 던지기 근처",
    ]
    for i, c in enumerate(cons):
        ax.text(0.54, 0.54 - i * 0.07, f"• {c}", color=INK, fontsize=14, va="top")
    _footer(ax, slide_no, total, "STEP 2 · 기존 거래대금")
    return fig


def slide_v2(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "STEP 3 · V2", "V2 — 점수제 도입", kicker_color=ACCENT)
    ax.text(0.05, 0.69,
            "거래대금만 보지 말고 수급·등락률·강도를 합성한 점수로 다시 정렬.",
            color=INK, fontsize=18, ha="left")
    # 본문: V2 산식의 의도
    _card(ax, 0.05, 0.18, 0.42, 0.48)
    ax.text(0.07, 0.61, "V2 점수의 의도", color=ACCENT, fontsize=13, fontweight="bold")
    intents = [
        "단순 거래대금에 가려진 후보 발굴",
        "수급 흐름 (외인·기관) 반영",
        "장 강도 / 상대 강도 가중치",
        "최근 3거래일 active pool 안에서 재정렬",
    ]
    for i, t in enumerate(intents):
        ax.text(0.07, 0.54 - i * 0.07, f"• {t}", color=INK, fontsize=14, va="top")
    # 우: 1년 결과 (의외)
    _card(ax, 0.52, 0.18, 0.43, 0.48, color="#f8fafc")
    ax.text(0.54, 0.61, "1년 결과 (의외)", color=INK, fontsize=13, fontweight="bold")
    ax.text(0.54, 0.53, "+3 먼저  54.4%", color=INK, fontsize=22, fontweight="bold", va="top")
    ax.text(0.54, 0.43, "-3 먼저  45.6%", color=WARN, fontsize=22, fontweight="bold", va="top")
    ax.text(0.54, 0.34,
            "P0 거래대금 Top3 (55.2%) 와 거의 동률.\n점수제는 분류는 더 좋지만\n변동성 자체를 줄이지는 못함.",
            color=MUTED, fontsize=12, va="top", linespacing=1.6)
    _footer(ax, slide_no, total, "STEP 3 · V2 점수제")
    return fig


def slide_belguard(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "STEP 4 · 새 자리", "벨가드 안정후보", kicker_color=GREEN)
    ax.text(0.05, 0.69,
            "V2 후보 중에서 '하방 위험이 큰 종목을 미리 걸러낸' 필터링 버전.",
            color=INK, fontsize=18, ha="left")
    # 좌: 무엇이 다른가
    _card(ax, 0.05, 0.18, 0.42, 0.48, color="#ecfdf5", edge="#bbf7d0")
    ax.text(0.07, 0.61, "무엇이 다른가", color=GREEN, fontsize=13, fontweight="bold")
    diffs = [
        "D0 15시 가격·수급·내림세 필터",
        "초변동성 후보 제외",
        "GREEN 비율이 평균적으로 더 높음",
        "동일 D0 풀 안에서 다시 고른 것",
    ]
    for i, d in enumerate(diffs):
        ax.text(0.07, 0.54 - i * 0.07, f"• {d}", color=INK, fontsize=14, va="top")
    # 우: 1년 결과 (안정성)
    _card(ax, 0.52, 0.18, 0.43, 0.48)
    ax.text(0.54, 0.61, "1년 결과 (안정성)", color=GREEN, fontsize=13, fontweight="bold")
    ax.text(0.54, 0.53, "-3 먼저  39.8%", color=GREEN, fontsize=22, fontweight="bold", va="top")
    ax.text(0.54, 0.43, "GREEN 48.9%", color=GREEN, fontsize=22, fontweight="bold", va="top")
    ax.text(0.54, 0.34,
            "V2 (-3 먼저 45.6%) 대비 -5.8pp 개선.\n최악 10건 하락폭도 D1 종가 기준\n-17.8% → -13.4% 로 +4.4pp.",
            color=MUTED, fontsize=12, va="top", linespacing=1.6)
    _footer(ax, slide_no, total, "STEP 4 · 벨가드 안정후보")
    return fig


def slide_compare(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "1년 비교", "세 갈래 한눈에", kicker_color=INK)
    # 비교 표
    headers = ["지표", "기존 V2", "기존 거래대금 P0", "벨가드 안정후보"]
    rows = [
        ["GREEN 비율",  "32.1%",  "—",      "48.9%"],
        ["RED 비율",   "67.9%",  "—",      "48.4%"],
        ["+3 먼저",     "54.4%",  "55.2%",  "55.6%"],
        ["-3 먼저",     "45.6%",  "41.8%",  "39.8%"],
        ["-3 도달률",   "75.3%",  "—",      "53.4%"],
        ["최악 10 D1", "-17.8%", "—",      "-13.4%"],
    ]
    # 표 위치/크기
    tx, ty, tw, th = 0.06, 0.16, 0.88, 0.52
    col_x = [tx + 0.00 * tw, tx + 0.30 * tw, tx + 0.50 * tw, tx + 0.72 * tw]
    row_y0 = ty + th - 0.05
    row_dy = (th - 0.08) / (len(rows) + 1)
    # 헤더
    _card(ax, tx, ty, tw, th, color="#ffffff", edge=LINE)
    for cx, htext in zip(col_x, headers):
        color = INK if "벨가드" not in htext else GREEN
        weight = "bold"
        ax.text(cx + 0.02, row_y0, htext, color=color, fontsize=13, fontweight=weight, va="center")
    # 헤더 underline
    ax.add_line(plt.Line2D([tx + 0.01, tx + tw - 0.01],
                           [row_y0 - row_dy * 0.4, row_y0 - row_dy * 0.4], color=LINE, lw=1.0))
    # 데이터 행
    for i, row in enumerate(rows):
        y = row_y0 - (i + 1) * row_dy
        is_belguard_better = False
        # 강조 셀: 벨가드가 더 좋은 행
        if row[0] in ("-3 먼저", "-3 도달률", "최악 10 D1", "GREEN 비율"):
            is_belguard_better = True
        for j, val in enumerate(row):
            cx = col_x[j]
            color = INK
            weight = "normal"
            fontsize = 13
            if j == 0:
                color = MUTED
                weight = "bold"
            elif j == 3 and is_belguard_better:
                color = GREEN
                weight = "bold"
                fontsize = 14
            ax.text(cx + 0.02, y, val, color=color, fontsize=fontsize,
                    fontweight=weight, va="center")
    # 캡션
    ax.text(0.06, 0.10,
            "초록 글씨 = 벨가드가 V2 보다 우수한 지표.  "
            "+3 먼저는 셋 다 비슷하나, 하방 위험은 벨가드가 가장 작음.",
            color=MUTED, fontsize=11, va="center")
    _footer(ax, slide_no, total, "1년 비교")
    return fig


def slide_today_policy(slide_no, total):
    fig, ax = _new_slide()
    _title_top(ax, "운영 정책", "지금 어떻게 사용하나", kicker_color=INK)
    ax.text(0.05, 0.69,
            "벨가드 결과가 더 좋아 보여도 운영을 바로 바꾸지 않습니다.",
            color=INK, fontsize=18, ha="left")
    # 좌: 현재
    _card(ax, 0.05, 0.20, 0.42, 0.45, color="#f0f9ff", edge="#bae6fd")
    ax.text(0.07, 0.59, "운영 본진", color=ACCENT, fontsize=13, fontweight="bold")
    ax.text(0.07, 0.51, "기존 V2", color=INK, fontsize=26, fontweight="bold", va="top")
    ax.text(0.07, 0.41,
            "Discord 웹훅은 V2 Top3로 계속 발송.\nbell-webhook 코드 변경 없음.",
            color=MUTED, fontsize=14, va="top", linespacing=1.55)
    # 우: shadow
    _card(ax, 0.52, 0.20, 0.43, 0.45, color="#ecfdf5", edge="#bbf7d0")
    ax.text(0.54, 0.59, "Shadow 후보", color=GREEN, fontsize=13, fontweight="bold")
    ax.text(0.54, 0.51, "벨가드 안정후보", color=INK, fontsize=26, fontweight="bold", va="top")
    ax.text(0.54, 0.41,
            "최소 2~4주 shadow 검증.\n매일 결과를 비교해서 안정성을\n눈으로 확인한 뒤 운영 전환 검토.",
            color=MUTED, fontsize=14, va="top", linespacing=1.55)
    _footer(ax, slide_no, total, "운영 정책")
    return fig


def slide_closing(slide_no, total):
    fig, ax = _new_slide()
    # 큰 한 줄
    ax.text(0.05, 0.68, "결론", color=ACCENT, fontsize=14, fontweight="bold")
    ax.text(0.05, 0.56,
            "변동성을 조금 덜고\n안정적으로 꾸준히 보는 쪽이 좋다.",
            color=INK, fontsize=44, fontweight="bold", va="center", linespacing=1.18)
    # 하단 메시지 카드
    _card(ax, 0.05, 0.15, 0.90, 0.20, color="#f8fafc")
    ax.text(0.07, 0.27, "다음 단계", color=INK, fontsize=14, fontweight="bold", va="center")
    ax.text(0.07, 0.21,
            "• 매일 색깔 흐름과 일자별 상세를 보면서 메모를 남긴다\n"
            "• 2~4주 후 벨가드 안정후보의 실전 안정성을 재검증한다",
            color=MUTED, fontsize=13, va="center", linespacing=1.7)
    _footer(ax, slide_no, total, "결론")
    return fig


# ─────────────────────────── 빌드 ────────────────────────────


def build_pdf(out_path: Path = OUT_PATH) -> Path:
    builders = [
        slide_cover,
        slide_overview,
        slide_d0,
        slide_p0,
        slide_v2,
        slide_belguard,
        slide_compare,
        slide_today_policy,
        slide_closing,
    ]
    total = len(builders)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        for i, builder in enumerate(builders, start=1):
            fig = builder(i, total)
            pdf.savefig(fig, facecolor=BG, bbox_inches="tight", pad_inches=0.0)
            plt.close(fig)
        info = pdf.infodict()
        info["Title"] = "ClosingBell 시스템 소개"
        info["Subject"] = "D0 → P0 → V2 → 벨가드 안정후보"
        info["Keywords"] = "ClosingBell, V2, HYBRID, BellGuard, paper watch"
        info["CreationDate"] = datetime.now()
    return out_path


if __name__ == "__main__":
    out = build_pdf()
    print(f"PDF saved: {out}")
    print(f"size: {out.stat().st_size / 1024:.0f} KB")
