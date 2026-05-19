"""BellGuard 안정후보 설명 PDF — 외부 공유용, 벨가드 단독 어필 (11 슬라이드).

작성: 2026-05-17
변경 사유:
    초판은 기존 V2와 비교하는 형태였으나, 외부 공유용은 사용자만 알고 있는
    내부 모델(V2)을 노출하지 않는 것이 안전. 벨가드 단독으로 도달률·신호등·
    안정성을 어필하는 톤으로 재작성.

목적:
    - 웹훅 메시지를 같이 보는 분도 한 번에 이해
    - D0가 무엇 / 벨가드란 / 신호등 5색 / 도달률 / 15시 판단
    - 매수 추천 / 자동매매 문구 절대 금지

usage:
    & C:\\Coding\\projects\\_venvs\\closingbell-py312\\Scripts\\python.exe \\
      C:\\Coding\\projects\\bell-dashboard\\scripts\\build_bellguard_explainer_pdf.py
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "data" / "closingbell" / "online_v2" / "latest"
OUT_PATH = OUT_DIR / f"CLOSINGBELL_BELLGUARD_EXPLAINER_{datetime.now():%Y%m%d}.pdf"

plt.rcParams["font.family"] = ["Malgun Gothic", "Apple SD Gothic Neo", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42

# Palette — 벨가드 단독 톤: 초록 메인 / 강조는 INK
BG = "#ffffff"
INK = "#0f172a"
MUTED = "#64748b"
SUB = "#94a3b8"
BRAND = "#16a34a"          # 벨가드 메인 컬러
BRAND_DARK = "#15803d"
BRAND_BG = "#ecfdf5"
BRAND_EDGE = "#bbf7d0"
ACCENT = "#2563eb"         # 보조 강조 (D0 단계 등)
YELLOW = "#eab308"
ORANGE = "#f97316"
RED = "#dc2626"
GRAY = "#94a3b8"
LINE = "#e5e7eb"
SOFT_BG = "#f8fafc"
SOFT_AMBER_BG = "#fff7ed"
SOFT_AMBER_EDGE = "#fed7aa"
SOFT_BLUE_BG = "#f0f9ff"
SOFT_BLUE_EDGE = "#bae6fd"

PAGE_W, PAGE_H = 13.33, 7.5  # 16:9


def _new_slide():
    fig = plt.figure(figsize=(PAGE_W, PAGE_H), dpi=200)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_facecolor(BG); ax.set_axis_off()
    return fig, ax


def _footer(ax, slide_no, total, title):
    ax.add_line(plt.Line2D([0.04, 0.96], [0.06, 0.06], color=LINE, lw=0.8))
    ax.text(0.04, 0.035,
            "ClosingBell · 벨가드 안정후보 · 매수 추천 아님 · 자동매매 아님",
            color=MUTED, fontsize=8.5, ha="left", va="center")
    ax.text(0.96, 0.035, f"{slide_no} / {total}    {title}",
            color=MUTED, fontsize=8.5, ha="right", va="center")


def _title_top(ax, kicker, title, kicker_color=BRAND):
    ax.text(0.05, 0.91, kicker, color=kicker_color, fontsize=13, fontweight="bold", ha="left", va="center")
    ax.text(0.05, 0.83, title, color=INK, fontsize=34, fontweight="bold",
            ha="left", va="center", linespacing=1.15)
    ax.add_patch(Rectangle((0.05, 0.78), 0.08, 0.006, facecolor=kicker_color, edgecolor="none"))


def _card(ax, x, y, w, h, *, color="#ffffff", edge=LINE, radius=0.018):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.002,rounding_size={radius}",
        facecolor=color, edgecolor=edge, linewidth=1.2,
    ))


def _bar(ax, x, y, w, value_pct, max_pct, *, color, label_left, label_right, height=0.022, track="#f1f5f9"):
    full = w
    fill = full * (value_pct / max_pct)
    ax.add_patch(Rectangle((x, y), full, height, facecolor=track, edgecolor="none"))
    ax.add_patch(Rectangle((x, y), fill, height, facecolor=color, edgecolor="none"))
    if label_left:
        ax.text(x - 0.005, y + height / 2, label_left, color=INK, fontsize=12,
                ha="right", va="center", fontweight="bold")
    if label_right:
        ax.text(x + full + 0.005, y + height / 2, label_right, color=color, fontsize=12,
                ha="left", va="center", fontweight="bold")


# ──────────────────────────── 슬라이드 ────────────────────────────


def slide_01_cover(no, total):
    fig, ax = _new_slide()
    ax.text(0.05, 0.86, "CLOSINGBELL · BELLGUARD", color=BRAND, fontsize=14, fontweight="bold")
    ax.text(0.05, 0.60, "벨가드 안정후보\n무엇이 다른가",
            color=INK, fontsize=56, fontweight="bold", va="center", linespacing=1.10)
    ax.text(0.05, 0.34,
            "15시 빠른 판단을 돕는 복기형 신호등 시스템.\n비전문가도 한 번에 이해할 수 있게 정리한 안내서입니다.",
            color=MUTED, fontsize=17, va="top", linespacing=1.55)
    _card(ax, 0.05, 0.10, 0.62, 0.09, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.145, "Paper Watch · 매수 추천 아님 · 자동매매 도구 아님",
            color=BRAND_DARK, fontsize=12, fontweight="bold", va="center")
    ax.add_patch(Rectangle((0.83, 0.10), 0.005, 0.78, facecolor=BRAND, edgecolor="none"))
    ax.text(0.86, 0.49, f"{datetime.now():%Y-%m-%d}", color=MUTED, fontsize=14, va="center")
    _footer(ax, no, total, "표지")
    return fig


def slide_02_what_is_this(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "이 시스템은 무엇인가", "오늘 강했던 종목을\n다음 5일간 복기합니다.")
    flow = [
        ("D0", "큰 거래가 들어온 날", ACCENT),
        ("15:00", "벨가드 후보 정리", BRAND),
        ("D+1~D+5", "실제 결과 추적", ORANGE),
        ("복기·메모", "다음 판단 개선", MUTED),
    ]
    n = len(flow)
    x_start = 0.06; gap = 0.015
    w = (0.88 - gap * (n - 1)) / n
    for i, (h, t, c) in enumerate(flow):
        x = x_start + i * (w + gap)
        _card(ax, x, 0.34, w, 0.30)
        ax.text(x + w / 2, 0.585, h, color=c, fontsize=20, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, 0.49, t, color=INK, fontsize=14, ha="center", va="center", linespacing=1.5)
        if i < n - 1:
            ax.text(x + w + gap / 2, 0.49, "▶", color=GRAY, fontsize=14, ha="center", va="center")
    _card(ax, 0.06, 0.16, 0.88, 0.13, color=SOFT_BLUE_BG, edge=SOFT_BLUE_EDGE)
    ax.text(0.08, 0.255, "핵심", color=ACCENT, fontsize=11, fontweight="bold")
    ax.text(0.08, 0.21,
            "“좋은 종목을 찍어주는 도구”가 아니라\n“어제 강했던 종목이 오늘 어떻게 갔는지 매일 확인하는 복기 도구”입니다.",
            color=INK, fontsize=14, va="top", linespacing=1.55)
    _footer(ax, no, total, "1 · 시스템 안내")
    return fig


def slide_03_d0(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "D-제로 (D0)", "오늘 시장이 갑자기 주목한 종목", kicker_color=ACCENT)
    ax.text(0.05, 0.67,
            "D0는 거래량과 거래대금이 평소보다 크게 들어온 날입니다.\n특별한 점수가 아니라 “감시 시작점”입니다.",
            color=INK, fontsize=17, va="top", linespacing=1.6)
    _card(ax, 0.05, 0.15, 0.42, 0.40)
    ax.text(0.07, 0.49, "D0 조건", color=ACCENT, fontsize=12, fontweight="bold")
    conds = [
        ("거래량", "1,000만 주 이상"),
        ("종가 범위", "2,000원 ~ 100,000원"),
        ("등락률", "0% 초과"),
        ("시장", "KOSPI · KOSDAQ 보통주"),
        ("제외", "ETF · ETN · 우선주 · SPAC · REIT"),
    ]
    for i, (k, v) in enumerate(conds):
        y = 0.43 - i * 0.062
        ax.text(0.07, y, k, color=MUTED, fontsize=12.5, va="center")
        ax.text(0.20, y, v, color=INK, fontsize=13.5, fontweight="bold", va="center")
    _card(ax, 0.52, 0.15, 0.43, 0.40, color=SOFT_AMBER_BG, edge=SOFT_AMBER_EDGE)
    ax.text(0.54, 0.49, "주의", color=ORANGE, fontsize=12, fontweight="bold")
    ax.text(0.54, 0.42,
            "D0 = 좋은 종목이라는 뜻이 아닙니다.",
            color=INK, fontsize=18, fontweight="bold", va="top")
    ax.text(0.54, 0.32,
            "그날 시장이 관심을 보냈다는 신호일 뿐입니다.\n그 다음 5거래일 동안 어떻게 가는지\n“관찰”하는 시작점입니다.",
            color=MUTED, fontsize=13.5, va="top", linespacing=1.6)
    _footer(ax, no, total, "2 · D0")
    return fig


def slide_04_bellguard(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "벨가드 안정후보란?", "D0 후보 중 위험을 미리 걸러낸\n안정 우선 후보군입니다.")
    # 큰 메시지 카드
    _card(ax, 0.05, 0.50, 0.90, 0.20, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.65, "핵심 한 줄", color=BRAND_DARK, fontsize=12, fontweight="bold")
    ax.text(0.07, 0.55,
            "“더 크게 먹기 위한 후보가 아니라,\n덜 깨지는 후보를 고르기 위한 안정 필터입니다.”",
            color=INK, fontsize=20, fontweight="bold", va="center", linespacing=1.45)
    # 좌: 어떻게 걸러내나
    _card(ax, 0.05, 0.13, 0.42, 0.31)
    ax.text(0.07, 0.40, "필터 기준", color=BRAND, fontsize=12, fontweight="bold")
    items = [
        "D0 15시 가격·국면",
        "과열 / 급등 직후 위험",
        "이벤트성 변동 (장중 뉴스, 단발 급등)",
        "내림세 시그널",
    ]
    for i, t in enumerate(items):
        ax.text(0.07, 0.34 - i * 0.052, f"• {t}", color=INK, fontsize=13.5, va="top")
    # 우: 위치
    _card(ax, 0.52, 0.13, 0.43, 0.31, color=SOFT_AMBER_BG, edge=SOFT_AMBER_EDGE)
    ax.text(0.54, 0.40, "주의", color=ORANGE, fontsize=12, fontweight="bold")
    ax.text(0.54, 0.34, "재무 건강도(DART)는 아직 결합 X",
            color=INK, fontsize=14.5, fontweight="bold", va="top")
    ax.text(0.54, 0.27,
            "현재는 D0 가격 · 국면 · 과열 · 이벤트 위험\n기반의 “위험필터형” 후보군입니다.\n신호일 뿐 매수 신호가 아닙니다.",
            color=MUTED, fontsize=12.5, va="top", linespacing=1.6)
    _footer(ax, no, total, "3 · 벨가드 안정후보")
    return fig


def slide_05_signals(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "신호등 5색", "다음날 가격이 어떻게 갔는지\n5색 한 글자로 요약합니다.", kicker_color=INK)
    items = [
        ("🟢", "강세", BRAND, "위로 먼저 가고\n잘 버팀",     BRAND_BG, BRAND_EDGE),
        ("🟡", "회복", YELLOW, "잠시 아래로 갔다\n다시 위로 회복", "#fef9c3", "#fde68a"),
        ("🟠", "실패", ORANGE, "위로 시도했지만\n종가가 약함", SOFT_AMBER_BG, SOFT_AMBER_EDGE),
        ("🔴", "약세", RED, "아래로 먼저 깨짐\n손실 위험 큼", "#fef2f2", "#fecaca"),
        ("⚪", "보류", GRAY, "거의 안 움직임\n또는 데이터 부족", "#f1f5f9", "#cbd5e1"),
    ]
    n = len(items)
    x0 = 0.05; gap = 0.014
    w = (0.90 - gap * (n - 1)) / n
    for i, (emoji, label, color, desc, bg, edge) in enumerate(items):
        x = x0 + i * (w + gap)
        _card(ax, x, 0.20, w, 0.50, color=bg, edge=edge)
        ax.add_patch(Circle((x + w / 2, 0.59), 0.04, facecolor=color, edgecolor="white", linewidth=2))
        ax.text(x + w / 2, 0.495, label, color=INK, fontsize=22, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, 0.36, desc, color=INK, fontsize=12.5, ha="center", va="center", linespacing=1.55)
    ax.text(0.05, 0.12,
            "벨가드는 🟢·🟡 비중을 키우고 🔴 비중을 줄이는 것을 목표로 합니다.",
            color=MUTED, fontsize=13, va="center")
    _footer(ax, no, total, "4 · 신호등 5색")
    return fig


def slide_06_year_summary(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "벨가드 1년 신호등", "초록과 빨강이\n거의 같습니다.")
    ax.text(0.05, 0.66,
            "최근 1년 약 760건의 후보를 추적한 결과 — 빨강 비중이 절반 아래로 내려옵니다.",
            color=INK, fontsize=15.5, va="top", linespacing=1.55)
    # 큰 카드 4개
    items = [
        ("🟢", "강세", "48.9%", BRAND, "5일 안에 잘 버틴 비중"),
        ("🟡", "회복", " 1.2%", YELLOW, "흔들리고 회복한 비중"),
        ("🟠", "실패", " 1.6%", ORANGE, "위로 갔다 무너진 비중"),
        ("🔴", "약세", "48.4%", RED, "5일 안에 약했던 비중"),
    ]
    n = len(items)
    x0 = 0.05; gap = 0.016
    w = (0.90 - gap * (n - 1)) / n
    for i, (emoji, label, val, color, desc) in enumerate(items):
        x = x0 + i * (w + gap)
        _card(ax, x, 0.18, w, 0.44)
        ax.add_patch(Circle((x + w / 2, 0.55), 0.035, facecolor=color, edgecolor="white", linewidth=2))
        ax.text(x + w / 2, 0.47, label, color=INK, fontsize=14, fontweight="bold", ha="center")
        ax.text(x + w / 2, 0.36, val, color=color, fontsize=30, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, 0.25, desc, color=MUTED, fontsize=11.5, ha="center", va="center", linespacing=1.5)
    ax.text(0.05, 0.12,
            "빨강 비중이 절반 아래라는 점이 핵심입니다.\n5일 안에 큰 손실 구간으로 가는 경우가 절반보다 적습니다.",
            color=MUTED, fontsize=12.5, linespacing=1.6)
    _footer(ax, no, total, "5 · 1년 신호등")
    return fig


def slide_07_pm3_first(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "+3 / -3 먼저 도달", "5일 안에 +3%와 -3% 중\n어느 쪽이 먼저 오느냐", kicker_color=INK)
    ax.text(0.05, 0.69,
            "위와 아래 중 어느 쪽이 먼저 닿는지가 실제 손익 체감의 핵심입니다.",
            color=INK, fontsize=15.5, va="top", linespacing=1.55)
    # 두 큰 카드: +3 먼저 / -3 먼저
    # +3
    _card(ax, 0.05, 0.18, 0.43, 0.46, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.585, "+3% 먼저 도달", color=BRAND_DARK, fontsize=14, fontweight="bold")
    ax.text(0.07, 0.50, "55.7%", color=BRAND, fontsize=58, fontweight="bold", va="center")
    _bar(ax, 0.07, 0.34, 0.39, 55.7, 100, color=BRAND, label_left="", label_right="", height=0.018, track="#dcfce7")
    ax.text(0.07, 0.27,
            "다섯 종목 중 약 세 종목은\n5일 안에 한 번이라도 +3% 위로 갔습니다.",
            color=INK, fontsize=13.5, va="top", linespacing=1.55)
    # -3
    _card(ax, 0.52, 0.18, 0.43, 0.46)
    ax.text(0.54, 0.585, "-3% 먼저 도달", color=MUTED, fontsize=14, fontweight="bold")
    ax.text(0.54, 0.50, "39.8%", color=ORANGE, fontsize=58, fontweight="bold", va="center")
    _bar(ax, 0.54, 0.34, 0.39, 39.8, 100, color=ORANGE, label_left="", label_right="", height=0.018)
    ax.text(0.54, 0.27,
            "다섯 종목 중 약 두 종목만\n5일 안에 -3% 아래로 먼저 갔습니다.",
            color=INK, fontsize=13.5, va="top", linespacing=1.55)
    # 한 줄 결론
    _card(ax, 0.05, 0.10, 0.90, 0.05, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.5, 0.125,
            "위로 먼저 갈 비율 (55.7%) 이 아래로 먼저 갈 비율 (39.8%) 보다 큽니다.",
            color=INK, fontsize=13, fontweight="bold", ha="center", va="center")
    _footer(ax, no, total, "6 · +3/-3 먼저")
    return fig


def slide_08_downside(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "큰 손실은 얼마나 자주 오는가", "“얼마나 자주 하락 구간에 닿는지”\n— 낮을수록 좋습니다.", kicker_color=RED)
    # 3개 카드: -3 / -5 / -10 도달 (절대 수치만)
    items = [
        ("-3% 도달", 53.4, "5일 안에 한 번이라도\n-3% 아래로 간 비율"),
        ("-5% 도달", 36.4, "5일 안에 한 번이라도\n-5% 아래로 간 비율"),
        ("-10% 도달", 13.1, "5일 안에 한 번이라도\n-10% 아래로 간 비율"),
    ]
    n = len(items)
    x0 = 0.05; gap = 0.02
    w = (0.90 - gap * (n - 1)) / n
    for i, (label, value, desc) in enumerate(items):
        x = x0 + i * (w + gap)
        _card(ax, x, 0.16, w, 0.50)
        ax.text(x + w / 2, 0.60, label, color=INK, fontsize=18, fontweight="bold", ha="center")
        ax.text(x + w / 2, 0.48, f"{value:.1f}%", color=ORANGE if value > 30 else BRAND,
                fontsize=46, fontweight="bold", ha="center", va="center")
        _bar(ax, x + 0.025, 0.34, w - 0.05, value, 100, color=ORANGE if value > 30 else BRAND,
             label_left="", label_right="", height=0.016, track="#f1f5f9")
        ax.text(x + w / 2, 0.235, desc, color=MUTED, fontsize=11.5, ha="center", va="center", linespacing=1.55)
    # 메시지
    _card(ax, 0.05, 0.10, 0.90, 0.05, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.5, 0.125,
            "특히 -10% 같은 큰 손실 구간에 닿는 경우는 100건 중 13건 정도로 적습니다.",
            color=INK, fontsize=13, fontweight="bold", ha="center", va="center")
    _footer(ax, no, total, "7 · 하락 도달률")
    return fig


def slide_09_15h_decision(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "15시에 어떻게 볼 것인가", "“좋은 종목 찾기”보다\n“나쁜 후보 피하기”가 먼저입니다.", kicker_color=INK)
    items = [
        ("1", "웹훅 메시지를 먼저 본다.", "오늘의 벨가드 후보와 신호등 색깔"),
        ("2", "신호등과 위험 라벨을 확인한다.", "🟢🟡 비중이 큰가, 🔴 경고가 있는가"),
        ("3", "차트를 직접 본다.", "VWAP 위인지 · 거래량 유지 여부"),
        ("4", "급하게 전부 매수하지 않는다.", "한 번에 분할 / 손절 위치 먼저"),
        ("5", "메모를 남긴다.", "사전 느낌 → 다음날 사후 비교"),
    ]
    y0 = 0.62
    dy = 0.085
    for i, (num, title, desc) in enumerate(items):
        y = y0 - i * dy
        ax.add_patch(Circle((0.07, y + 0.022), 0.022, facecolor=BRAND, edgecolor="none"))
        ax.text(0.07, y + 0.022, num, color="white", fontsize=14, fontweight="bold",
                ha="center", va="center")
        ax.text(0.115, y + 0.035, title, color=INK, fontsize=15, fontweight="bold", va="center")
        ax.text(0.115, y + 0.010, desc, color=MUTED, fontsize=12.5, va="center")
    _card(ax, 0.05, 0.10, 0.90, 0.08, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.14,
            "15시에는 “좋아 보이는 종목”보다 “지금 들어가면 깨질 만한 후보”를 먼저 거르세요.",
            color=INK, fontsize=14, fontweight="bold", va="center")
    _footer(ax, no, total, "8 · 15시 체크리스트")
    return fig


def slide_10_for_companions(no, total):
    fig, ax = _new_slide()
    _title_top(ax, "같이 보는 분께 — 안내", "이 메시지는 매수 추천이 아닙니다.", kicker_color=ORANGE)
    _card(ax, 0.05, 0.30, 0.90, 0.40, color=SOFT_AMBER_BG, edge=SOFT_AMBER_EDGE)
    ax.text(0.07, 0.65, "꼭 알아두실 점", color=ORANGE, fontsize=13, fontweight="bold")
    notes = [
        "• 이 메시지는 “오늘 15시 기준으로 강한 거래가 들어온 종목”의 정리표입니다.",
        "• “지금 사세요”라는 추천이 아니라, “복기/관찰 후보”입니다.",
        "• 최종 매수·매도 판단은 차트·호가·뉴스·시장 상황을 직접 확인한 뒤 본인 책임으로 하세요.",
        "• 같은 종목이 매일 반복해서 나올 수 있습니다 (D0가 3거래일 유지되기 때문).",
        "• 자동매매·실주문 기능은 들어 있지 않습니다.",
    ]
    for i, n_ in enumerate(notes):
        ax.text(0.07, 0.57 - i * 0.055, n_, color=INK, fontsize=14, va="top")
    _card(ax, 0.05, 0.12, 0.43, 0.13)
    ax.text(0.07, 0.215, "데이터 출처", color=MUTED, fontsize=11, fontweight="bold")
    ax.text(0.07, 0.165, "KOSPI · KOSDAQ 공시 OHLCV (D+1 익영업일까지 확정)",
            color=INK, fontsize=12.5, va="center")
    _card(ax, 0.52, 0.12, 0.43, 0.13)
    ax.text(0.54, 0.215, "검증 기간", color=MUTED, fontsize=11, fontweight="bold")
    ax.text(0.54, 0.165, "최근 1년 · 신호 약 760건 추적 결과",
            color=INK, fontsize=12.5, va="center")
    _footer(ax, no, total, "9 · 같이 보는 사람용")
    return fig


def slide_11_closing(no, total):
    fig, ax = _new_slide()
    ax.text(0.05, 0.86, "한 줄 결론", color=BRAND, fontsize=14, fontweight="bold")
    ax.text(0.05, 0.62,
            "조금 덜 먹어도 좋으니,\n큰 손실을 피하고 꾸준히 가자.",
            color=INK, fontsize=44, fontweight="bold", va="center", linespacing=1.18)
    ax.text(0.05, 0.34,
            "벨가드는 “더 크게 먹기”가 아닌 “덜 깨지기”에 초점을 둔 안정 후보군입니다.\n매일 15시 신호등과 차트를 함께 보면서, 복기와 메모로 판단을 다듬어 갑니다.",
            color=MUTED, fontsize=16, va="top", linespacing=1.6)
    _card(ax, 0.05, 0.10, 0.90, 0.14, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.20, "기억할 한 가지", color=BRAND_DARK, fontsize=11, fontweight="bold")
    ax.text(0.07, 0.14,
            "도달률은 “이렇게 갈 확률”이지 “이렇게 간다”가 아닙니다. 매번 차트를 직접 확인하세요.",
            color=INK, fontsize=14, fontweight="bold", va="center")
    _footer(ax, no, total, "10 · 결론")
    return fig


# ──────────────────────────── 빌드 ────────────────────────────


def build_pdf(out_path: Path = OUT_PATH) -> Path:
    builders = [
        slide_01_cover,
        slide_02_what_is_this,
        slide_03_d0,
        slide_04_bellguard,
        slide_05_signals,
        slide_06_year_summary,
        slide_07_pm3_first,
        slide_08_downside,
        slide_09_15h_decision,
        slide_10_for_companions,
        slide_11_closing,
    ]
    total = len(builders)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        for i, builder in enumerate(builders, start=1):
            fig = builder(i, total)
            pdf.savefig(fig, facecolor=BG, bbox_inches="tight", pad_inches=0.0)
            plt.close(fig)
        info = pdf.infodict()
        info["Title"] = "ClosingBell · 벨가드 안정후보 안내서"
        info["Subject"] = "D0 / 벨가드 안정후보 / 신호등 / 도달률 / 15시 판단"
        info["Keywords"] = "ClosingBell, BellGuard, paper watch, 도달률, 신호등"
        info["CreationDate"] = datetime.now()
    return out_path


if __name__ == "__main__":
    out = build_pdf()
    print(f"PDF saved: {out}")
    print(f"size: {out.stat().st_size / 1024:.0f} KB")
