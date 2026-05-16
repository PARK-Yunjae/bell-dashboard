"""
V2 친절한 상세 가이드 PDF — 사용자가 V2 가 무엇인지·왜·어떻게 보는지 한 번에 이해.

설계 원칙 (사용자 지시 2026-05-14):
    - 글씨 겹침 / 짤림 절대 없게 (충분한 여백, 작은 폰트, 한 페이지 한 주제)
    - 표와 그래프와 그림을 친절하게 (matplotlib 막대그래프, 시각 카드)
    - Malgun Gothic 만 사용, 안전 글리프만 (이모지 누락 방지)
    - D0 후보군 재검증 중 경고를 표지·중간·마지막에 박아둠 (현 상황 안전 표시)

페이지 구성 (16 페이지, A4 가로):
    1. 표지 + 한 페이지 요약
    2. 이 문서는 무엇인가 + ★ D0 재검증 경고
    3. V2 란 무엇인가 — 개념 그림
    4. P0 vs V2 — 어떻게 다른가
    5. V2 점수 등급표 + 시각 컬러바
    6. 왜 55점 미달은 주의인가
    7. 오늘의 V2 Top3 카드 (5/13 sample, 대형주 경고)
    8. 1년 백데이터 시각화 — 도달률 막대그래프
    9. 한 달 vs 1년 V2 vs P0 비교 그래프
   10. Paper 기준선 — 진입·익절·손절·시간청산 도식
   11. 데이터 누락 36% — 왜 강제로 채우지 않는가
   12. 안정성 게이트 개념
   13. Phase 0~4 로드맵 — 시각 타임라인
   14. 자주 묻는 질문 (FAQ 6개)
   15. 절대 안 건드리는 것 (운영 경계선)
   16. 용어 풀이 + 한 줄 정리
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch

# Korean font
for tf in (Path(r"C:\Windows\Fonts\malgun.ttf"), Path(r"C:\Windows\Fonts\malgunbd.ttf")):
    if tf.exists():
        font_manager.fontManager.addfont(str(tf))
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

A4_LANDSCAPE = (11.7, 8.3)


# ===== 공통 유틸 (글씨 겹침·짤림 방지에 집중) =====

def _header(fig, title: str, sub: str = "") -> None:
    """페이지 상단 큰 제목 띠. 본문 영역과 겹치지 않게 y=0.92~1.00 확보."""
    ax = fig.add_axes([0.0, 0.92, 1.0, 0.08]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.04, 0.58, title, fontsize=16, fontweight="bold", color="white", va="center")
    if sub:
        ax.text(0.96, 0.58, sub, fontsize=9.5, color="#c7d2fe", va="center", ha="right")


def _footer(fig, page_no: int, total: int) -> None:
    """페이지 하단 푸터. y=0.00~0.035 영역만 사용."""
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.035]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#f1f5f9", edgecolor="none"))
    ax.text(0.04, 0.5,
            "ClosingBell V2 친절한 가이드  ·  연구·관찰용 Paper Watch  ·  "
            "D0 후보군 재검증 중  ·  매수 추천 아님 · 자동매매 아님",
            fontsize=7.5, color="#475569", va="center")
    ax.text(0.96, 0.5, f"{page_no} / {total}",
            fontsize=8, color="#475569", va="center", ha="right")


def _band(fig, y: float, num: int, title: str, color: str = "#dbeafe", text_color: str = "#1e3a8a") -> None:
    """섹션 띠 — 본문과 4% 여백 확보. 한 페이지에 2개 띠 이상 두지 않음 (겹침 방지)."""
    ax = fig.add_axes([0.04, y, 0.92, 0.045]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor=color, edgecolor="none"))
    ax.text(0.01, 0.5, f"{num}. {title}" if num else title,
            fontsize=12, fontweight="bold", color=text_color, va="center")


def _table(ax, header, rows, col_widths, header_color="#e0e7ff", font_size=9.5, scale=1.9,
           cell_align="left"):
    """표 — scale 을 1.9 이상으로 설정해서 행 간 충분히 (겹침 방지)."""
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=10, color="#999")
        return
    t = ax.table(cellText=rows, colLabels=header, loc="upper left",
                 cellLoc=cell_align, colWidths=col_widths)
    t.auto_set_font_size(False)
    t.set_fontsize(font_size)
    t.scale(1.0, scale)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold", color="#1e3a8a")
        else:
            cell.set_facecolor("#ffffff" if (r - 1) % 2 == 0 else "#f8fafc")


def _warn_box(fig, y: float, height: float, title: str, body: str,
              bg="#fef3c7", border="#d97706", text="#78350f") -> None:
    """경고 박스 — 본문에 박을 수 있는 강조 박스. 글씨 겹침 방지를 위해 height ≥ 0.06 권장."""
    ax = fig.add_axes([0.04, y, 0.92, height]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                 transform=ax.transAxes,
                                 facecolor=bg, edgecolor=border, linewidth=1.2))
    ax.text(0.02, 0.78, title, fontsize=11.5, fontweight="bold",
            color=text, va="center")
    ax.text(0.02, 0.32, body, fontsize=10, color=text,
            va="center", wrap=True, linespacing=1.6)


# ===== 페이지 1 — 표지 =====
def page_1_cover(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)

    # 상단 배너
    ax = fig.add_axes([0.0, 0.75, 1.0, 0.25]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.05, 0.66, "ClosingBell V2 — 친절한 가이드",
            fontsize=24, fontweight="bold", color="white", va="center")
    ax.text(0.05, 0.36, "점수제 V2 가 무엇인지 · 왜 만들었는지 · 어떻게 보는지",
            fontsize=13, color="#dbeafe", va="center")
    ax.text(0.05, 0.14,
            f"작성 {datetime.now().strftime('%Y-%m-%d')}  ·  Claude Code  ·  Paper Watch 연구용",
            fontsize=10, color="#cbd5e0", va="center")

    # 중간 — 한 페이지 요약 박스 3개
    _band(fig, 0.66, 0, "한 페이지 요약 — 세 가지만 기억하세요", color="#fef3c7", text_color="#78350f")

    summary_items = [
        ("◆ V2 는 무엇인가",
         "기존 거래대금 정렬 후보 (P0) 위에 '점수' 를 매겨 더 좋은 종목을 고르는 정렬 방식.\n"
         "기존 D0 후보군 그대로 + 점수 0~100점 + 상위 3개 = V2 Top3.",
         "#3b82f6"),
        ("◆ 어떻게 보면 되는가",
         "점수 55점 이상 = 운영 기준선 통과 / 55점 미만 = 주의 (백데이터 안정 구간 밖).\n"
         "Paper Watch 화면이라 매수 추천 아님 — 눈으로 직접 판단.",
         "#16a34a"),
        ("◆ 지금 조심할 점",
         "2026-05-13 V2 Top3 에 대형주 (현대차·SK하이닉스) 포함 — 후보군 정의 재검증 중.\n"
         "재검증 끝나기 전 백데이터 수치는 '임시값' 으로 봐주세요.",
         "#dc2626"),
    ]
    y = 0.42
    for title, body, color in summary_items:
        ax = fig.add_axes([0.06, y, 0.88, 0.18]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color, linewidth=1.5))
        ax.text(0.02, 0.75, title, fontsize=13, fontweight="bold",
                color=color, va="center")
        ax.text(0.02, 0.32, body, fontsize=10.5, color="#374151",
                va="center", linespacing=1.6)
        y -= 0.21

    _footer(fig, 1, total)
    pdf.savefig(fig); plt.close(fig)


# ===== 페이지 2 — 이 문서는 무엇인가 + D0 재검증 경고 =====
def page_2_intro(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "이 문서는 무엇인가",
            "처음 보는 사람도 V2 를 이해할 수 있게")

    _band(fig, 0.83, 1, "이 문서를 만든 이유")
    ax = fig.add_axes([0.04, 0.62, 0.92, 0.20]); ax.axis("off")
    paras = [
        "ClosingBell 의 V2 점수제는 작년부터 만들어온 연구 결과인데, 화면·메시지·문서가 분산되어 있어 "
        "한 번에 이해하기 어려웠습니다.",
        "이 가이드는 V2 가 무엇인지, 어떤 종목을 어떻게 고르는지, 백데이터 수치는 어떻게 읽어야 하는지 — "
        "그림과 표로 한 번에 설명합니다.",
        "주의: 이 문서는 매수·매도 가이드가 아닙니다. 점수제 결과를 사람이 직접 보고 판단하기 위한 "
        "Paper Watch (관찰용) 입니다.",
    ]
    ax.text(0.0, 0.95, "\n\n".join(paras), fontsize=11, color="#374151",
            va="top", linespacing=1.7, wrap=True)

    # D0 재검증 경고 (강조 박스)
    _warn_box(fig, 0.32, 0.26,
              "★ 중요 — 2026-05-14 현재 D0 후보군 재검증 진행 중",
              "2026-05-13 V2 Top3 결과에 현대차 (005380) · SK하이닉스 (000660) · 현대글로비스 (086280) "
              "같은 대형주가 포함되었습니다.\n\n"
              "기존 ClosingBell 프로젝트의 D0 후보군 정의 (거래대금 폭발·금액제한·대형주 제외) 와 "
              "현재 V2 의 입력 후보군이 일치하는지 Codex 가 audit 중입니다.\n\n"
              "→ 이 가이드의 백데이터 수치 (D+1 +2% 84%, D+5 +3% 92.5% 등) 는 모두 '재검증 전 임시값' 입니다.\n"
              "→ 재검증 결과에 따라 위 수치는 크게 달라질 수 있습니다.")

    _band(fig, 0.24, 2, "이 문서 읽는 순서 (16 페이지)", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.19]); ax.axis("off")
    toc = [
        "  3. V2 란 무엇인가 — 개념 그림으로",
        "  4. P0 vs V2 — 어떻게 다른가",
        "  5. V2 점수 등급표",
        "  6. 왜 55점 미달은 주의인가",
        "  7. 오늘의 V2 Top3 카드 (5/13 sample)",
        "  8. 1년 백데이터 시각화",
        "  9. 한 달·1년 V2 vs P0 비교 그래프",
        "10. Paper 기준선 도식",
        "11. 데이터 누락 36% 이야기",
        "12. 안정성 게이트 개념",
        "13. Phase 0~4 로드맵 타임라인",
        "14. 자주 묻는 질문 6개",
        "15. 절대 안 건드리는 것",
        "16. 용어 풀이 + 한 줄 정리",
    ]
    ax.text(0.0, 0.97, "\n".join(toc), fontsize=10, color="#374151",
            va="top", linespacing=1.55, family="Malgun Gothic")

    _footer(fig, 2, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 3 — V2 란 무엇인가 (개념 그림) =====
def page_3_what_is_v2(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "3. V2 란 무엇인가", "기존 후보 풀 위에 점수만 새로 매기는 정렬 방식")

    # 개념 그림 — 세 블록을 화살표로 연결
    ax = fig.add_axes([0.04, 0.35, 0.92, 0.50]); ax.axis("off")

    blocks = [
        ("[1단계]", "전체 시장", "약 2,500개 종목\n(코스피·코스닥)", "#94a3b8"),
        ("[2단계]", "D0 후보 풀", "거래량·거래대금 폭발 +\n금액제한 + 종목 필터", "#3b82f6"),
        ("[3단계]", "V2 점수제", "각 종목에 0~100점\n점수 산식 (Codex 운영)", "#10b981"),
        ("[4단계]", "V2 Top3", "점수 상위 3개\n+ 55점 미달은 ★ 주의", "#dc2626"),
    ]
    positions = [(0.05, 0.55, 0.20, 0.30), (0.30, 0.55, 0.20, 0.30),
                 (0.55, 0.55, 0.20, 0.30), (0.80, 0.55, 0.18, 0.30)]
    for (tag, title, body, color), (x, y, w, h) in zip(blocks, positions):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008",
                                     transform=ax.transAxes,
                                     facecolor=color, edgecolor="none", alpha=0.95))
        ax.text(x + w / 2, y + h - 0.05, tag, fontsize=9, color="white",
                fontweight="bold", ha="center", va="center", transform=ax.transAxes)
        ax.text(x + w / 2, y + h - 0.13, title, fontsize=13, color="white",
                fontweight="bold", ha="center", va="center", transform=ax.transAxes)
        ax.text(x + w / 2, y + 0.08, body, fontsize=9.5, color="white",
                ha="center", va="center", linespacing=1.6, transform=ax.transAxes)

    # 화살표 (단계 사이)
    for x1, x2 in [(0.25, 0.30), (0.50, 0.55), (0.75, 0.80)]:
        ax.annotate("", xy=(x2, 0.70), xytext=(x1, 0.70),
                    xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="->", color="#475569", lw=2.5))

    # 아래 설명
    ax.text(0.5, 0.40, "핵심: V2 는 새로운 종목을 찾는 게 아니라, 이미 있는 D0 후보 풀에 점수를 더해서 정렬을 바꾸는 것입니다.",
            fontsize=11, color="#374151", ha="center", va="center",
            fontweight="bold", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#fef3c7", edgecolor="#d97706"))

    # 점수가 보는 5가지 요소 박스
    _band(fig, 0.27, 0, "V2 점수가 보는 5가지 요소 (개념)", color="#dcfce7", text_color="#14532d")
    ax2 = fig.add_axes([0.04, 0.05, 0.92, 0.21]); ax2.axis("off")
    factors = [
        "  ◆ D0 종가 위치     —  당일 고가 대비 종가가 얼마나 강하게 끝났는가",
        "  ◆ 윗꼬리 비율       —  당일 고가에서 종가까지 얼마나 떨어졌는가 (짧을수록 강세)",
        "  ◆ 거래대금 강도     —  D0 거래대금이 전일·평균 대비 얼마나 폭발했는가",
        "  ◆ 눌림 깊이         —  D0 이후 며칠 동안 얕은 눌림 (양봉 방어) 인가 깊은 눌림 (음봉) 인가",
        "  ◆ 데이터 신선도     —  일봉·분봉·15:00 기준가 모두 최신 거래일 기준인가",
    ]
    ax2.text(0.0, 0.97, "\n".join(factors), fontsize=10.5, color="#374151",
             va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 3, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 4 — P0 vs V2 비교 =====
def page_4_p0_vs_v2(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "4. P0 vs V2 — 어떻게 다른가", "정렬 기준 하나만 다름")

    _band(fig, 0.83, 1, "두 방식의 차이를 한 표로")
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.31]); ax.axis("off")
    rows = [
        ["정렬 기준",          "거래대금 desc",                "V2 점수 desc"],
        ["입력 풀",             "D0 후보 풀 (동일)",            "D0 후보 풀 (동일) — 재검증 중"],
        ["선정 개수",           "Top2 + 참고 Rank3",            "Top3 무조건 (단, 55점 미달은 주의)"],
        ["운영 상태",           "● LIVE PROD 발송 중",         "[TEST] SHADOW dry-run (미발송)"],
        ["기존 한 달 백데이터",  "승률 30.3% / 실패 37.9%",      "승률 72.7% / 실패 7.6% (재검증 전)"],
        ["기존 1년 백데이터",    "승률 22.9% / 실패 44.8%",      "승률 37.0% / 실패 21.9% (재검증 전)"],
        ["성격",               "거래대금 폭발 = 시장 관심도",   "거래대금 + 패턴 + 윗꼬리 + 강세 종합"],
    ]
    _table(ax, ["구분", "P0 (기존 거래대금)", "V2 (점수제)"],
           rows, [0.22, 0.39, 0.39],
           header_color="#bfdbfe", scale=2.0)

    # 핵심 메모
    _warn_box(fig, 0.30, 0.16,
              "왜 V2 가 더 좋아 보이는가 (그리고 왜 재검증 필요한가)",
              "V2 점수가 종가 강세 + 얕은 눌림 같은 '이긴 차트' 패턴을 잘 잡는다는 가설입니다.\n"
              "단, 입력 후보 풀이 P0 와 정확히 같은지 (대형주 / 금액제한 제외 등) Codex 가 audit 중 — "
              "결과에 따라 V2 우위가 줄어들거나 유지될 수 있습니다.",
              bg="#fef3c7", border="#d97706", text="#78350f")

    # 그래프 — 한 달 승률 비교 막대
    _band(fig, 0.22, 2, "한 달 (22 거래일) D0 종가 진입 승률 비교", color="#dcfce7", text_color="#14532d")
    ax2 = fig.add_axes([0.10, 0.06, 0.82, 0.15])
    names = ["P0\n(거래대금)", "V2 Top3", "V2 Top2", "V2 55점+ 최대3"]
    win = [30.3, 72.7, 77.3, 78.7]
    loss = [37.9, 7.6, 4.5, 2.1]
    x = list(range(len(names)))
    width = 0.36
    bars1 = ax2.bar([i - width / 2 for i in x], win, width, label="성공률 (+3 먼저 도달)",
                    color="#16a34a", alpha=0.85)
    bars2 = ax2.bar([i + width / 2 for i in x], loss, width, label="실패률 (-2 먼저 터치)",
                    color="#dc2626", alpha=0.85)
    ax2.set_xticks(x); ax2.set_xticklabels(names, fontsize=9.5)
    ax2.set_ylabel("%", fontsize=10)
    ax2.set_ylim(0, 90)
    ax2.legend(fontsize=9, loc="upper left", framealpha=0.9)
    ax2.grid(axis="y", alpha=0.3)
    for b in bars1:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                 f"{b.get_height():.1f}%", ha="center", fontsize=8.5, color="#14532d")
    for b in bars2:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                 f"{b.get_height():.1f}%", ha="center", fontsize=8.5, color="#7f1d1d")

    _footer(fig, 4, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 5 — V2 점수 등급표 + 컬러바 =====
def page_5_grade(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "5. V2 점수 등급표", "0 ~ 100 점 — 어떻게 읽나")

    # 컬러바 (점수 시각화)
    _band(fig, 0.83, 1, "점수 → 등급 컬러바")
    ax = fig.add_axes([0.06, 0.65, 0.88, 0.15])
    # 5단계 색상 그라데이션 박스
    grades = [
        (0, 45, "#dc2626", "약함\n55점 크게 미달"),
        (45, 55, "#ca8a04", "주의\n55점 미달"),
        (55, 65, "#16a34a", "보통\n운영 기준선 통과"),
        (65, 75, "#ea580c", "강함"),
        (75, 100, "#dc2626", "매우 강함"),
    ]
    for lo, hi, color, label in grades:
        ax.add_patch(Rectangle((lo, 0), hi - lo, 1, facecolor=color, edgecolor="white", linewidth=1))
        ax.text((lo + hi) / 2, 0.5, label, fontsize=10, color="white",
                fontweight="bold", ha="center", va="center", linespacing=1.4)
    # 점수 눈금
    for v in [0, 45, 55, 65, 75, 100]:
        ax.axvline(v, color="white", linewidth=1.5)
        ax.text(v, -0.35, str(v), fontsize=10, color="#374151", ha="center", fontweight="bold")
    ax.set_xlim(0, 100); ax.set_ylim(-0.5, 1); ax.axis("off")
    ax.text(50, -0.85, "점수", fontsize=11, fontweight="bold", color="#374151", ha="center")

    # 등급별 상세 표
    _band(fig, 0.51, 2, "각 등급의 의미와 사용자 행동")
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.40]); ax2.axis("off")
    rows = [
        ["★★★",  "75 이상",   "점수상 매우 강함",        "백데이터에서 가장 안정. 단, 후보군 재검증 중 — 임시"],
        ["★",  "65 ~ 74",   "점수상 강함",             "운영 기준선 통과. 카드에서 ★ 표시"],
        ["●",  "55 ~ 64",   "점수상 보통",             "55점 운영 기준선 통과. 표시는 정상"],
        ["★",  "45 ~ 54",   "주의 — 55점 미달",        "백데이터 안정 구간 밖. ★ 주의 박스 자동 표시"],
        ["!!", "45 미만",   "약함 — 55점 크게 미달",   "주의 강도 ↑. 표시는 하되 진입 가정 큰 손실률 ↑ 메모"],
    ]
    _table(ax2, ["이모지", "점수 범위", "등급 라벨", "설명 (사용자 행동)"],
           rows, [0.08, 0.16, 0.30, 0.46],
           header_color="#e0e7ff", scale=2.1, font_size=10.5)

    _footer(fig, 5, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 6 — 왜 55점 미달은 주의인가 =====
def page_6_why_55(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "6. 왜 55점 미달은 ★ 주의인가", "백데이터 안정 구간 밖")

    _band(fig, 0.83, 1, "한 달 백데이터 — 점수대별 결과")
    ax = fig.add_axes([0.10, 0.50, 0.82, 0.33])
    # 점수대별 성공률 / 실패률 (대략 값)
    bands = ["55점+\n(안정)", "45~54점\n(주의)", "45점 미만\n(약함)"]
    win = [78.7, 55, 35]
    loss = [2.1, 18, 35]
    x = list(range(len(bands)))
    w = 0.36
    bars1 = ax.bar([i - w / 2 for i in x], win, w, label="성공률 (+3 먼저)", color="#16a34a", alpha=0.85)
    bars2 = ax.bar([i + w / 2 for i in x], loss, w, label="실패률 (-2 먼저)", color="#dc2626", alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(bands, fontsize=10)
    ax.set_ylabel("%", fontsize=10)
    ax.set_ylim(0, 90)
    ax.legend(fontsize=9.5, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    for b in bars1 + bars2:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                f"{b.get_height():.1f}%", ha="center", fontsize=9, color="#374151")

    # 결론 박스
    _warn_box(fig, 0.30, 0.18,
              "결론 — 55점은 단순한 숫자가 아니라 안정 구간의 경계선",
              "한 달 백데이터에서 55점 이상 종목들은 성공률 78.7% / 실패률 2.1% 로 매우 안정적.\n"
              "45~54점 영역에서는 성공률이 크게 떨어지고 실패률이 9배 (2.1% → 18%) 증가.\n"
              "→ 그래서 V2 화면에서 55점 미만은 자동으로 ★ 주의 박스를 띄웁니다.",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    # 추가 메모
    _band(fig, 0.22, 2, "단, 이 기준은 후보군 재검증 후 다시 확인 필요", color="#fef3c7", text_color="#78350f")
    ax2 = fig.add_axes([0.04, 0.06, 0.92, 0.15]); ax2.axis("off")
    notes = [
        "•  위 통계는 현재 V2 입력 후보 풀 기준입니다 (재검증 전).",
        "•  Codex 가 진행 중인 D0 후보군 / 금액제한 audit 결과에 따라 점수대별 성공률이 달라질 수 있습니다.",
        "•  특히 대형주가 잘못 포함됐다면, 대형주 점수대에서 성공률이 과대 표시됐을 가능성도 있습니다.",
        "•  최종 55점 임계값은 audit 완료 후 walk-forward 검증으로 robust 한지 확인 예정.",
    ]
    ax2.text(0.0, 0.95, "\n".join(notes), fontsize=10, color="#78350f",
             va="top", linespacing=1.7, family="Malgun Gothic")

    _footer(fig, 6, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 7 — 오늘의 V2 Top3 카드 (대형주 경고 포함) =====
def page_7_today_top3(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "7. 오늘의 V2 Top3 — 2026-05-13 sample",
            "대형주 포함 — D0 후보군 재검증 필요")

    # 큰 경고 박스 (페이지 상단)
    _warn_box(fig, 0.78, 0.08,
              "★ 이 페이지의 결과는 D0 후보군 재검증 전 임시값",
              "현대차·SK하이닉스·현대글로비스 모두 대형주 — 기존 D0 의도와 다른 후보군에서 산출됐을 가능성이 있습니다.")

    # Top3 카드 3개
    _band(fig, 0.71, 1, "2026-05-13 V2 Top3 카드")
    candidates = [
        ("1위", "현대차",       "005380", 92.0, "710,000원",   "#dc2626", "★★★ 점수상 매우 강함"),
        ("2위", "SK하이닉스",   "000660", 89.1, "1,986,500원", "#dc2626", "★★★ 점수상 매우 강함"),
        ("3위", "현대글로비스", "086280", 88.2, "285,000원",   "#dc2626", "★★★ 점수상 매우 강함"),
    ]
    card_w = 0.29; gap = 0.02
    for i, (rank, name, code, score, price, color, grade) in enumerate(candidates):
        x = 0.04 + i * (card_w + gap)
        ax = fig.add_axes([x, 0.10, card_w, 0.60]); ax.axis("off")
        # 카드 외곽
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color, linewidth=2))
        # 순위 + 종목명
        ax.text(0.5, 0.91, f"{rank}", fontsize=14, fontweight="bold",
                color=color, ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.83, name, fontsize=16, fontweight="bold",
                color="#1f2937", ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.77, f"({code})", fontsize=10, color="#6b7280",
                ha="center", va="center", transform=ax.transAxes)
        # 점수 박스
        ax.add_patch(FancyBboxPatch((0.10, 0.55), 0.80, 0.16,
                                     boxstyle="round,pad=0.008",
                                     transform=ax.transAxes,
                                     facecolor=color, edgecolor="none"))
        ax.text(0.5, 0.65, f"{score:.1f} / 100", fontsize=18, fontweight="bold",
                color="white", ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.58, grade, fontsize=9, color="white",
                ha="center", va="center", transform=ax.transAxes)
        # 가격
        ax.text(0.5, 0.49, "15:00 기준가", fontsize=9, color="#6b7280",
                ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.43, price, fontsize=13, fontweight="bold",
                color="#1f2937", ha="center", va="center", transform=ax.transAxes)
        # D0 audit 상태 (확인 중)
        ax.add_patch(FancyBboxPatch((0.05, 0.18), 0.90, 0.22,
                                     boxstyle="round,pad=0.008",
                                     transform=ax.transAxes,
                                     facecolor="#fef9c3", edgecolor="#ca8a04", linewidth=1))
        ax.text(0.5, 0.36, "◆ D0 후보군 재검증 상태", fontsize=9, fontweight="bold",
                color="#78350f", ha="center", va="center", transform=ax.transAxes)
        ax.text(0.07, 0.30, "• D0 후보군 통과: 확인 중",
                fontsize=8.5, color="#78350f", va="center", transform=ax.transAxes)
        ax.text(0.07, 0.25, "• 금액제한 통과: 확인 중",
                fontsize=8.5, color="#78350f", va="center", transform=ax.transAxes)
        ax.text(0.07, 0.20, "• 대형주 필터: 해당 의심",
                fontsize=8.5, color="#dc2626", fontweight="bold",
                va="center", transform=ax.transAxes)
        # 데이터 신선도
        ax.text(0.5, 0.10, "일봉/분봉 모두 2026-05-13 (오늘) ●",
                fontsize=8.5, color="#16a34a", ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.05, "추적: D+1 ~ D+5",
                fontsize=8.5, color="#6b7280", ha="center", va="center", transform=ax.transAxes)

    # 페이지 하단 메모
    ax_n = fig.add_axes([0.04, 0.04, 0.92, 0.04]); ax_n.axis("off")
    ax_n.text(0.5, 0.5,
              "세 종목 모두 점수상 매우 강함 (88점+) 으로 같은 등급 — "
              "단 대형주 의심이라 Codex audit 후 D0/금액제한 통과 여부 확정 예정",
              fontsize=9.5, color="#7f1d1d", ha="center", va="center", fontweight="bold")

    _footer(fig, 7, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 8 — 1년 백데이터 시각화 =====
def page_8_backdata_1y(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "8. 1년 백데이터 — 도달률 시각화",
            "재검증 전 임시값 · 도달률 ≠ 승률")

    _band(fig, 0.83, 1, "1년치 V2 Top3 — D+1 / D+5 누적 도달률 (분봉 기준)")
    ax = fig.add_axes([0.10, 0.40, 0.82, 0.42])

    horizons = ["D+1", "D+2", "D+3", "D+4", "D+5"]
    plus2 = [83.97, 88.5, 90.8, 92.0, 92.7]
    plus3 = [78.73, 85.29, 88.52, 90.50, 91.49]
    minus2 = [41.59, 45.88, 50.97, 56.11, 59.88]
    minus3 = [28.65, 33.53, 36.66, 43.14, 46.81]

    x = list(range(len(horizons)))
    w = 0.20
    ax.bar([i - 1.5 * w for i in x], plus2, w, label="+2% 도달 (익절)",
           color="#16a34a", alpha=0.85)
    ax.bar([i - 0.5 * w for i in x], plus3, w, label="+3% 도달",
           color="#10b981", alpha=0.85)
    ax.bar([i + 0.5 * w for i in x], minus2, w, label="-2% 도달 (손절)",
           color="#dc2626", alpha=0.85)
    ax.bar([i + 1.5 * w for i in x], minus3, w, label="-3% 도달",
           color="#b91c1c", alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(horizons, fontsize=11)
    ax.set_ylabel("누적 도달률 (%)", fontsize=10)
    ax.set_ylim(0, 100)
    ax.legend(fontsize=9, loc="upper left", ncol=2, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("1년치 V2 Top3 분봉 누적 도달률 (표본 755 · D+5 완성 732)",
                 fontsize=11, color="#1e3a8a", pad=8)

    # 해석 박스
    _warn_box(fig, 0.20, 0.18,
              "이 그래프 읽는 법",
              "초록색 (+2 / +3) 막대가 빨간색 (-2 / -3) 막대보다 항상 높습니다 — 도달률 자체는 V2 가 우위.\n"
              "그러나 같은 날 양쪽 (+2 와 -2) 모두 닿는 변동성 케이스가 다수라, '도달률' 은 '승률' 이 아닙니다.\n"
              "실제 승률은 선후관계 (어느 쪽이 먼저) + 슬리피지 + 갭 보정 후 -5~-10%p 차감해서 해석해야 합니다.",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    _band(fig, 0.12, 2, "수치 표 (위 그래프 원본)", color="#e0e7ff", text_color="#1e3a8a")
    ax_t = fig.add_axes([0.04, 0.04, 0.92, 0.08]); ax_t.axis("off")
    rows = [
        ["D+1", "83.97%", "78.73%", "41.59%", "28.65%"],
        ["D+5", "92.70%", "91.49%", "59.88%", "46.81%"],
    ]
    _table(ax_t, ["구간", "+2% 누적", "+3% 누적", "-2% 누적", "-3% 누적"],
           rows, [0.10, 0.22, 0.22, 0.22, 0.24],
           header_color="#bfdbfe", scale=2.0, cell_align="center")

    _footer(fig, 8, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 9 — 한 달·1년 V2 vs P0 비교 그래프 =====
def page_9_compare_grouped(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "9. 한 달 · 1 년 — V2 vs P0 비교",
            "두 기간 두 정책 — 한 그래프로")

    _band(fig, 0.83, 1, "D0 종가 진입 — 한 달 vs 1 년")
    ax = fig.add_axes([0.08, 0.45, 0.86, 0.36])

    groups = ["한 달 승률", "한 달 실패률", "1년 승률", "1년 실패률"]
    p0 = [30.3, 37.9, 22.9, 44.8]
    v2 = [72.7, 7.6, 37.0, 21.9]
    x = list(range(len(groups)))
    w = 0.36
    bars1 = ax.bar([i - w / 2 for i in x], p0, w, label="P0 (거래대금)", color="#3b82f6", alpha=0.85)
    bars2 = ax.bar([i + w / 2 for i in x], v2, w, label="V2 (점수제)", color="#10b981", alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=10.5)
    ax.set_ylabel("%", fontsize=10)
    ax.set_ylim(0, 90)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    for bars in (bars1, bars2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                    f"{b.get_height():.1f}%", ha="center", fontsize=9, color="#374151")

    # 분석 텍스트
    _band(fig, 0.36, 2, "그래프가 말하는 것 (재검증 전)")
    ax2 = fig.add_axes([0.04, 0.07, 0.92, 0.28]); ax2.axis("off")
    notes = [
        "•  한 달 짧은 기간에서는 V2 가 P0 대비 승률 +42%p, 실패률 -30%p 로 매우 우세하게 보임.",
        "•  1년 긴 기간으로 가면 격차가 좁혀짐 (승률 +14%p, 실패률 -23%p) — 시장 사이클·변동성 영향.",
        "•  특히 1년 V2 승률 37% 는 절대값으로는 낮음 → V2 도 만능 아님, '상대적으로' P0 보다 좋다는 뜻.",
        "•  ★ 위 수치는 재검증 전 임시값 — Codex audit 결과 후보군 차이가 보정되면 격차가 줄어들 수 있음.",
        "•  실거래 보정 (슬리피지 ~0.5%, 갭 영향, 호가 공백) 까지 더하면 V2 도 -5~-10%p 추가 차감 권장.",
        "•  결론: V2 우위 = 정성적으로 의미 있지만 '운영 단독 전환 OK' 라고 단정할 단계는 아직 아님.",
    ]
    ax2.text(0.0, 0.97, "\n".join(notes), fontsize=10, color="#374151",
             va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 9, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 10 — Paper 기준선 도식 =====
def page_10_paper_baseline(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "10. Paper 기준선 — 진입·익절·손절·시간청산",
            "복기 시뮬 규칙 (운영 진입 가이드 아님)")

    # 가격 시뮬 도식 (간단 차트)
    _band(fig, 0.83, 1, "백데이터에서 어떻게 승/패를 판정하는가")
    ax = fig.add_axes([0.10, 0.42, 0.82, 0.40])

    # 가격선 시뮬레이션 (D0~D+5 임의)
    import numpy as np
    np.random.seed(7)
    t = np.linspace(0, 5, 50)
    price = 100 + np.cumsum(np.random.randn(50) * 0.4) + np.sin(t * 2) * 1.2
    price = price - price[0] + 100

    ax.plot(t, price, color="#1e3a8a", linewidth=2, label="가격 (예시)")
    ax.axhline(100, color="#6b7280", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(5.05, 100, "D0 종가 (=100)", fontsize=9, color="#6b7280", va="center")

    # 익절/손절선
    ax.axhline(102, color="#16a34a", linestyle="-", linewidth=2, alpha=0.85)
    ax.text(5.05, 102, "+2% 익절 기준선", fontsize=9.5, color="#14532d",
            fontweight="bold", va="center")
    ax.axhline(98, color="#dc2626", linestyle="-", linewidth=2, alpha=0.85)
    ax.text(5.05, 98, "-2% 손절 기준선", fontsize=9.5, color="#7f1d1d",
            fontweight="bold", va="center")

    # +3 / -3 점선
    ax.axhline(103, color="#16a34a", linestyle=":", linewidth=1.2, alpha=0.6)
    ax.text(5.05, 103, "+3%", fontsize=8.5, color="#16a34a", va="center")
    ax.axhline(97, color="#dc2626", linestyle=":", linewidth=1.2, alpha=0.6)
    ax.text(5.05, 97, "-3%", fontsize=8.5, color="#dc2626", va="center")

    # 진입점 화살표
    ax.annotate("진입 (D+1 시가)", xy=(0.05, price[1]), xytext=(0.8, 96.5),
                fontsize=10, color="#1e3a8a", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#1e3a8a", lw=1.5))

    # 시간청산 표시
    ax.axvline(1.5, color="#ca8a04", linestyle="-.", linewidth=1.5, alpha=0.7)
    ax.text(1.55, 105.5, "다음날 11:30\n시간청산 (시뮬)",
            fontsize=9, color="#78350f", fontweight="bold", va="top")

    ax.set_xlabel("거래일 (D0 = 0, D+5 = 5)", fontsize=10)
    ax.set_ylabel("가격 (D0 종가 = 100)", fontsize=10)
    ax.set_xlim(-0.1, 5.8)
    ax.set_ylim(95, 107)
    ax.legend(loc="upper left", fontsize=9.5, framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.set_title("Paper 기준선 시뮬 도식 (예시)", fontsize=11, color="#1e3a8a", pad=8)

    # 판정 규칙
    _band(fig, 0.34, 2, "판정 규칙 (한 줄씩)")
    ax2 = fig.add_axes([0.04, 0.07, 0.92, 0.26]); ax2.axis("off")
    rules = [
        "1.  진입 가정 (복기 기준): D+1 시가  ← 실거래에 가까운 가정",
        "2.  익절 시뮬: 분봉이 +2% 선을 먼저 터치하면 '목표먼저' = 성공",
        "3.  손절 시뮬: 분봉이 -2% 선을 먼저 터치하면 '손실먼저' = 실패",
        "4.  시간청산: 다음날 11:30 까지 양쪽 다 안 닿으면 시장가 청산 (시뮬상)",
        "5.  슬리피지 보정: 실거래에서는 호가창 ↑ 평균 0.3~1.5% — 실제 익절은 +2.5%, 손절은 -2.5% 로 봐야 안전",
        "6.  도달률 ≠ 승률: 같은 날 +2 와 -2 둘 다 닿는 변동성 케이스가 많음 → 선후관계가 핵심",
        "7.  ■ 이 박스는 매수·매도 가이드가 아닙니다 — 백데이터를 어떻게 계산했는지 보여주는 설명",
    ]
    ax2.text(0.0, 0.97, "\n".join(rules), fontsize=10.5, color="#374151",
             va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 10, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 11 — 데이터 누락 36% =====
def page_11_missing(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "11. 데이터 누락 36% — 왜 강제로 채우지 않는가",
            "솔직한 운영 정책")

    # 막대그래프 — D+1~D+5 제외율
    _band(fig, 0.83, 1, "최근 22 거래일 V2 후보 제외율 (D+N 까지 누적)")
    ax = fig.add_axes([0.10, 0.50, 0.82, 0.32])
    horizons = ["D+1", "D+2", "D+3", "D+4", "D+5"]
    excluded = [15.2, 21.2, 27.3, 31.8, 36.4]
    x = list(range(len(horizons)))
    bars = ax.bar(x, excluded, color="#ca8a04", alpha=0.85, width=0.55)
    ax.set_xticks(x); ax.set_xticklabels(horizons, fontsize=11)
    ax.set_ylabel("제외율 (%)", fontsize=10)
    ax.set_ylim(0, 45)
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.7,
                f"{b.get_height():.1f}%", ha="center", fontsize=10,
                fontweight="bold", color="#78350f")
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("66 행 중 D+N 까지 데이터 부족으로 제외된 비율",
                 fontsize=11, color="#1e3a8a", pad=8)

    # 정책 박스
    _warn_box(fig, 0.30, 0.18,
              "정책 — 부족하면 0~3개로 표시 (강제 채우지 않음)",
              "데이터 가드 (entry_1500_missing · minute_data_stale_or_missing · 등) 에서 빠진 후보는 "
              "Top3 에 강제로 채우지 않습니다.\n"
              "어떤 날은 V2 유효 후보가 1~2 개만, 또 어떤 날은 0 개일 수도 있습니다.\n"
              "→ '강제로 3 개 채우기' 보다 '솔직하게 부족함을 표시' 가 백데이터 통계를 무너뜨리지 않습니다.",
              bg="#fef3c7", border="#d97706", text="#78350f")

    # 주요 사유
    _band(fig, 0.22, 2, "주요 제외 사유 (excluded CSV 178 행)")
    ax2 = fig.add_axes([0.04, 0.04, 0.92, 0.18]); ax2.axis("off")
    rows = [
        ["entry_1500_missing",             "15:00~15:05 첫 분봉 종가 없음 (저유동 종목 / 거래정지)", "약 50%"],
        ["dplusN_minute_or_future_missing", "D+1 ~ D+5 분봉이 일부 또는 전부 누락",                      "약 40%"],
        ["future_daily_days_less_than_5",  "신호일 이후 5 거래일치 일봉이 아직 안 쌓임 (최근 신호 한정)",  "약 8%"],
        ["data_freshness_stale",           "daily / minute 최신 갱신일이 운영일 기준 미달",              "약 2%"],
    ]
    _table(ax2, ["사유 코드", "의미", "전체 중 비중"],
           rows, [0.28, 0.54, 0.18],
           header_color="#fde68a", font_size=9.5, scale=2.0)

    _footer(fig, 11, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 12 — 안정성 게이트 =====
def page_12_stability_gate(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "12. 안정성 게이트 — Phase 전환 준비도",
            "5 영업일 연속 V2 유효 ≥ 3 인가")

    _band(fig, 0.83, 1, "안정성 게이트 개념")
    ax = fig.add_axes([0.04, 0.55, 0.92, 0.27]); ax.axis("off")
    paras = [
        "V2 가 '운영 단독 발송' 으로 가려면, 먼저 매일 안정적으로 3개 후보가 나오는지 확인해야 합니다.",
        "단일일 결과가 좋아도 다음날 0개가 나오면 운영이 불안정하기 때문입니다.",
        "그래서 자동으로 다음을 평가하는 함수 (안정성 게이트) 가 매일 돌고 있습니다:",
        "       → 최근 5 영업일 중 V2 유효 후보 ≥ 3 인 날의 개수",
        "       → 5 / 5 = PASSED  ·  3~4 / 5 = WAIT  ·  0~2 / 5 = BLOCKED",
    ]
    ax.text(0.0, 0.97, "\n".join(paras), fontsize=11, color="#374151",
            va="top", linespacing=2.0, family="Malgun Gothic")

    # 게이트 상태 표
    _band(fig, 0.46, 2, "현재 게이트 상태 (2026-05-14 기준)")
    ax2 = fig.add_axes([0.04, 0.18, 0.92, 0.28]); ax2.axis("off")
    rows = [
        ["lookback_days",       "5",                              "최근 5 영업일을 본다"],
        ["min_valid_count",     "3",                              "유효 후보 ≥ 3 필요"],
        ["days_passed",         "1 / 5 (오늘이 첫 정식 산출일)",  "5/14 첫 산출 — 누적 시작"],
        ["status",              "WAIT_MORE_DAYS",                 "5 영업일 누적 대기"],
        ["next_check_date",     "2026-05-20 (5 영업일 누적 완료)", "이 날부터 PASSED 가능"],
        ["if_PASSED",           "Phase 2 진입 권장 가능",         "PROD 본문 V2 SHADOW 병기 가능"],
    ]
    _table(ax2, ["키", "값", "의미"],
           rows, [0.24, 0.34, 0.42],
           header_color="#dcfce7", font_size=10, scale=2.0)

    # 결론 박스
    _warn_box(fig, 0.06, 0.10,
              "지금 단계는 '대기 (WAIT)'",
              "오늘 (5/14) 부터 5 영업일 누적 시작. 5/20 까지 매일 V2 Top3 가 3 개 채워지면 'PASSED' 가 됩니다.\n"
              "그 후에도 D0 후보군 재검증 결과 (Codex audit) 가 통과해야 Phase 2 로 갈 수 있습니다.",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, 12, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 13 — Phase 0~4 로드맵 타임라인 =====
def page_13_roadmap(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "13. Phase 0~4 로드맵",
            "어디까지 와 있고 어디로 가는가")

    _band(fig, 0.83, 1, "단계별 진행 상황")
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.62]); ax.axis("off")

    phases = [
        ("Phase 0", "현재 (지금)",
         "V2 산출 정식 통합 완료 (매일 14:15/15:02/17:05 자동) · LIVE P0 그대로 발송 · V2 는 dry-run 미발송",
         "● 완료", "#10b981"),
        ("Phase 1", "V2 SHADOW 발송 시작",
         "별도 Discord SHADOW 채널 신설 → V2 SHADOW URL 로만 발송 · PROD 채널 P0 그대로 유지 "
         "· 사용자 paper watch 시작",
         "▷ 사용자 결정 후 (지금 가능)", "#3b82f6"),
        ("Phase 2", "PROD 본문에 V2 SHADOW 섹션 병기",
         "PROD 채널 P0 메시지 뒤에 V2 SHADOW 섹션 추가 · 사용자 매일 같은 화면에서 P0/V2 비교 가능 "
         "· 2~4주 paper watch 후",
         "▷ 안정성 게이트 PASSED 후", "#ca8a04"),
        ("Phase 3", "V2 PROD 본문 단독",
         "메인 후보 표시·발송을 V2 로 교체 · P0 는 작은 비교 박스로 축소 · 1~3개월 paper watch + "
         "D0 후보군 audit 통과 + 사용자 명시 승인 후",
         "▷ 후보군 재검증 + 사용자 승인 후", "#ea580c"),
        ("Phase 4", "P0 코드 완전 제거 (선택)",
         "P0 산출·표시·발송 코드 archive 이동 · 백테스트 비교축 영구 사라짐",
         "X 권장하지 않음 (Phase 3 에서 멈추는 것 권장)", "#dc2626"),
    ]
    y = 0.95
    bar_x = 0.08
    bar_w = 0.13
    for tag, title, body, status, color in phases:
        ax.add_patch(FancyBboxPatch((bar_x, y - 0.16), bar_w, 0.14,
                                     boxstyle="round,pad=0.005",
                                     transform=ax.transAxes,
                                     facecolor=color, edgecolor="none"))
        ax.text(bar_x + bar_w / 2, y - 0.09, tag, fontsize=11, color="white",
                fontweight="bold", ha="center", va="center", transform=ax.transAxes)
        ax.text(bar_x + bar_w + 0.02, y - 0.02, title, fontsize=11.5, fontweight="bold",
                color="#1f2937", va="top", transform=ax.transAxes)
        ax.text(bar_x + bar_w + 0.02, y - 0.07, body, fontsize=9.5, color="#374151",
                va="top", wrap=True, linespacing=1.5, transform=ax.transAxes)
        ax.text(0.96, y - 0.02, status, fontsize=9.5, fontweight="bold",
                color=color, va="top", ha="right", transform=ax.transAxes)
        y -= 0.19

    # 하단 메모
    _warn_box(fig, 0.10, 0.08,
              "현재 위치: Phase 0 완료 · Phase 1 진입 대기",
              "사용자가 'SHADOW 채널 만들고 시작' 한 줄로 Phase 1 ON. "
              "그 후 매일 paper watch 결과 + Codex D0 audit 결과를 보고 Phase 2/3 단계적 진행.")

    _footer(fig, 13, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 14 — 자주 묻는 질문 =====
def page_14_faq(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "14. 자주 묻는 질문 (FAQ)",
            "사용자 입장에서 헷갈리는 6 가지")

    qa = [
        ("Q1. V2 가 P0 보다 좋다는데, 그럼 P0 는 왜 안 없애나요?",
         "1년 백데이터로 V2 가 우세하게 보이지만, 입력 후보군 정의가 일치하는지 재검증 중입니다. "
         "P0 를 비교축으로 유지해야 V2 가 진짜 개선인지 검증 가능합니다."),
        ("Q2. 점수가 88점인데도 매수 추천이 아니라고요?",
         "맞습니다. 점수는 '백데이터 기준 어떤 종목이 강한가' 를 보여주는 통계 결과이고, "
         "실거래는 슬리피지·갭·체결지연·시장 상황 같은 별도 변수가 있어요. Paper Watch 만 안전합니다."),
        ("Q3. 5/13 V2 Top3 가 다 대형주인데 정상인가요?",
         "아닙니다 — 그게 지금 진행 중인 재검증의 이유입니다. 기존 ClosingBell D0 후보군은 "
         "거래대금 폭발 + 금액제한 + 대형주 제외가 의도였는데, V2 가 그 필터를 제대로 통과한 후 점수화한 건지 "
         "Codex 가 확인 중입니다."),
        ("Q4. 55점 미달 후보도 Top3 에 있으면 어떻게 하나요?",
         "Top3 에는 그대로 표시됩니다 (총 3개 유지). 다만 카드에 ★ 주의 박스가 자동으로 붙고, "
         "메시지에서도 '주의 — 55점 미달' 등급 라벨이 표시돼요. 사용자가 직접 보고 판단합니다."),
        ("Q5. 안정성 게이트가 PASSED 되면 바로 운영 전환되나요?",
         "아니요. PASSED 는 '기술적으로 안정' 이라는 뜻이고, Phase 2~3 진입은 사용자 명시 승인 + "
         "D0 audit 통과 + 사용자가 paper watch 결과를 직접 평가한 후에만 가능합니다."),
        ("Q6. 이 데이터는 어디서 확인할 수 있나요?",
         "대시보드 '온라인 V2' 탭, 웹훅 SHADOW 메시지 (dry-run), 다운로드 폴더의 산출 CSV/JSON, "
         "그리고 Streamlit Cloud 배포 시 어디서든 같은 화면을 볼 수 있습니다."),
    ]

    ax = fig.add_axes([0.04, 0.05, 0.92, 0.78]); ax.axis("off")
    y = 0.97
    for q, a in qa:
        ax.text(0.0, y, q, fontsize=11, fontweight="bold", color="#1e3a8a",
                va="top", transform=ax.transAxes, wrap=True)
        ax.text(0.02, y - 0.04, a, fontsize=9.8, color="#374151",
                va="top", transform=ax.transAxes, wrap=True, linespacing=1.6)
        y -= 0.155

    _footer(fig, 14, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 15 — 절대 안 건드리는 것 =====
def page_15_safety(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "15. 절대 안 건드리는 것 — 운영 경계선",
            "전 단계 공통 안전 가드")

    _band(fig, 0.83, 1, "기술적 가드")
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.32]); ax.axis("off")
    rules = [
        "  X  주문 / 계좌 / 한국투자증권·키움 등 실거래 API 코드 추가",
        "  X  기존 LIVE P0 발송 경로 (Discord PROD URL, candidate_source) 변경",
        "  X  V2 점수 산식 weight·feature 변경 (audit 산식 그대로 운영 분기에 옮기기만)",
        "  X  스케줄러로 PROD 본문 자동 전환 (사용자 명시 승인 + Claude 한 줄 변경만 허용)",
        "  X  현재일 후보 카드에 D+1~D+5 미래 결과 노출 (look-ahead 누수)",
        "  X  entry_1500_missing 후보를 D0 종가로 임의 fallback 채우기",
        "  X  IPO 후보 자동 V2 편입 (사용자 수동 영역)",
        "  X  yj_bot · 기타 자동매매 봇 연결",
    ]
    ax.text(0.0, 0.97, "\n".join(rules), fontsize=11, color="#7f1d1d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _band(fig, 0.43, 2, "표시·문구 가드 (2026-05-14 신설)", color="#fef3c7", text_color="#78350f")
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.32]); ax2.axis("off")
    display = [
        "  ◆  '매수 추천 / 진입 가이드' 표현 금지 — 'Paper 기준선 / 복기 시뮬 규칙' 으로",
        "  ◆  '매우 강함' 같은 강한 단정 표현 → '점수상 매우 강함 (후보군 재검증 중)' 으로 완화",
        "  ◆  대시보드 / 웹훅 상단에 'D0 후보군 / 금액제한 재검증 중' 배너 의무 표시",
        "  ◆  백데이터 수치 옆에 '재검증 전 임시값' 명시",
        "  ◆  대형주 의심 종목은 카드에 ★ 추가 (현대차·SK하이닉스 등)",
        "  ◆  LIVE P0 vs V2 SHADOW 발송 상태를 화면에 분리 표시",
    ]
    ax2.text(0.0, 0.97, "\n".join(display), fontsize=11, color="#78350f",
             va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 15, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 16 — 용어 풀이 + 한 줄 정리 =====
def page_16_glossary(pdf: PdfPages, total: int) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "16. 용어 풀이 + 한 줄 정리",
            "이 문서를 닫을 때 기억해야 할 것")

    _band(fig, 0.83, 1, "용어 풀이")
    ax = fig.add_axes([0.04, 0.30, 0.92, 0.52]); ax.axis("off")
    glossary = [
        ("D0",           "최초 거래대금 폭발일 — 큰 거래대금이 발생한 첫 날. 매수 신호 아닌 '감시 시작 신호'"),
        ("D0 후보군 풀", "거래대금 폭발 + 금액제한 + 종목 필터 (ETF/IPO/우선주 등 제외) 를 통과한 종목들"),
        ("P0",           "기존 운영 정책 — 거래대금 desc 정렬 Top2 + 참고 Rank3 = 디스코드 LIVE 발송 중"),
        ("V2",           "점수제 정렬 — 거래대금 + 패턴 + 윗꼬리 + 강세종가 + 데이터 신선도 종합 점수"),
        ("MFE",          "Maximum Favorable Excursion — D0 진입가 대비 5일 안 최고 상승률"),
        ("MAE",          "Maximum Adverse Excursion — D0 진입가 대비 5일 안 최대 하락률"),
        ("도달률",       "특정 % 선을 한 번이라도 닿은 비율. '승률' 이 아니며, 선후관계가 핵심"),
        ("Paper Watch",  "실거래 없이 관찰만 하는 모드 — 매수 추천 아닌 연구 / 복기 / 감시"),
        ("SHADOW",       "운영 (PROD) 과 분리된 연구용 발송 채널 — V2 메시지를 안전하게 띄우는 곳"),
        ("안정성 게이트", "최근 5 영업일 연속 V2 유효 후보 ≥ 3 인지 자동 평가하는 함수"),
    ]
    rows = [[t, d] for t, d in glossary]
    _table(ax, ["용어", "설명"], rows, [0.20, 0.80],
           header_color="#e0e7ff", font_size=10, scale=1.85)

    # 한 줄 정리
    _warn_box(fig, 0.07, 0.20,
              "한 줄 정리 — 이 문서를 닫을 때",
              "V2 는 기존 D0 후보 풀 위에 점수를 매기는 정렬 방식이며, 한 달 백데이터에서 P0 대비 우세하게 "
              "보이지만 후보군 재검증 결과에 따라 우위가 달라질 수 있습니다. 운영 발송은 여전히 LIVE P0 이고, "
              "V2 는 SHADOW Paper Watch 만 — 사용자가 매일 직접 보고 판단하는 '눈으로 보는 검증' 단계입니다.\n\n"
              "→ 핵심 행동: ① 점수 55 미만 ★ 표시 보고 의심 / ② 대형주 의심 카드 보고 D0 audit 결과 기다리기 / "
              "③ Phase 1 SHADOW 발송 시작은 사용자 한 줄 결정으로",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    _footer(fig, 16, total); pdf.savefig(fig); plt.close(fig)


# ===== Main =====
def build(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 16
    with PdfPages(out_path) as pdf:
        page_1_cover(pdf, total)
        page_2_intro(pdf, total)
        page_3_what_is_v2(pdf, total)
        page_4_p0_vs_v2(pdf, total)
        page_5_grade(pdf, total)
        page_6_why_55(pdf, total)
        page_7_today_top3(pdf, total)
        page_8_backdata_1y(pdf, total)
        page_9_compare_grouped(pdf, total)
        page_10_paper_baseline(pdf, total)
        page_11_missing(pdf, total)
        page_12_stability_gate(pdf, total)
        page_13_roadmap(pdf, total)
        page_14_faq(pdf, total)
        page_15_safety(pdf, total)
        page_16_glossary(pdf, total)

    size_kb = out_path.stat().st_size / 1024
    print(f"[ok] {out_path}  ({size_kb:.1f} KB, {total} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(r"C:\Users\PYJ\Downloads\V2_FRIENDLY_GUIDE_KR_20260514.pdf"))
    args = ap.parse_args()
    build(args.out)
