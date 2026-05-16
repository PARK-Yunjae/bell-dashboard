"""
전일 종가 색깔 복기 - 슬라이드 스타일 PDF (V2_FRIENDLY_GUIDE 풍).

사용자 요청 (2026-05-16 09:50):
    "이전에 아무것도 모르는 사람을 위한 17페이지정도의 pdf식으로 ppt느낌도 나고
     눈에 확 들어오던데 그런식으로 개요부터 해서 만들어줄수 있는지"

기준:
    - 큰 글씨 (제목 22~26pt, 본문 12~14pt)
    - 한 페이지 한 메시지
    - 색깔 카드 / 큰 동그라미 / 도식 위주
    - 텍스트 최소
    - PPT 슬라이드 느낌

17 페이지 구성:
    1.  표지 + 5색 동그라미
    2.  이 보고서는 무엇인가 (3 카드)
    3.  이 색깔이 무슨 뜻인가 (5색 카드 그림)
    4.  왜 색깔로 보나 (비유 + 도식)
    5.  한 페이지 결론 (4 큰 카드)
    6.  색깔 흐름이란 (5칸 시각화)
    7.  V2 점수제 결과 — 다음날 색깔 분포 큰 막대
    8.  V2 vs 거래대금 vs D0 풀 (3 컬럼)
    9.  결과가 좋았던 흐름 TOP 5 (큰 색 동그라미)
   10.  결과가 안 좋았던 흐름 TOP 5
   11.  다음날 색깔 → 5일 결과 (큰 막대)
   12.  V2 22일 색깔 매트릭스 (행 = 신호일, 열 = D+1~D+5)
   13.  V2 + 거래대금 공통 후보 (안정성)
   14.  위험한 흐름 주의 카드
   15.  이건 무엇이 아닌가 (매수 추천 X 강조)
   16.  다음 단계 (3 카드)
   17.  한 줄 요약 (큰 글씨)
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

for tf in (Path(r"C:\Windows\Fonts\malgun.ttf"), Path(r"C:\Windows\Fonts\malgunbd.ttf")):
    if tf.exists():
        font_manager.fontManager.addfont(str(tf))
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# A4 가로 — PPT 16:9 느낌
SLIDE = (13.3, 7.5)

DOWN = Path(r"C:\Users\PYJ\Downloads")
# 우선순위: Codex 5/16 enriched → dashboard_cases_latest → 5/15 ChatGPT 버전
_CASES_CANDIDATES = [
    DOWN / "prev_close_color_cases_recent_1m_enriched_20260516.csv",
    DOWN / "prev_close_color_dashboard_cases_latest_20260516.csv",
    DOWN / "CHATGPT_WEB_PREV_CLOSE_COLOR_CASES_RECENT_1M_20260515.csv",
]
CASES_CSV = next((p for p in _CASES_CANDIDATES if p.exists()), _CASES_CANDIDATES[0])

COLOR_HEX = {
    "G": "#16a34a",
    "Y": "#facc15",
    "O": "#f97316",
    "R": "#dc2626",
    "X": "#9ca3af",
}
COLOR_KO = {
    "G": "완전 강세", "Y": "흔들렸지만 회복",
    "O": "위로 갔지만 실패", "R": "완전 약세", "X": "변동 거의 없음",
}
COLOR_SHORT = {"G": "강", "Y": "회", "O": "실", "R": "약", "X": "보"}


# ───────── 공통 유틸 (큰 글씨 / 슬라이드 풍) ─────────

def _slide_bg(fig, top_color="#1e3a8a"):
    """슬라이드 배경 (상단 컬러 띠)."""
    ax = fig.add_axes([0, 0.93, 1, 0.07]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor=top_color, edgecolor="none"))


def _title(fig, text, sub="", color="#1e3a8a", x=0.05, y=0.83):
    """페이지 큰 제목."""
    fig.text(x, y, text, fontsize=24, fontweight="bold", color=color,
             ha="left", va="center")
    if sub:
        fig.text(x, y - 0.06, sub, fontsize=12, color="#6b7280",
                 ha="left", va="center")


def _slide_footer(fig, p, total, txt="전일 종가 색깔 복기 - 한 달치 보고서"):
    ax = fig.add_axes([0, 0, 1, 0.03]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#f8fafc", edgecolor="none"))
    ax.text(0.05, 0.5, txt + "  ·  연구용 - 매수 추천 아님",
            fontsize=8, color="#6b7280", va="center")
    ax.text(0.95, 0.5, f"{p} / {total}", fontsize=8.5,
            color="#6b7280", va="center", ha="right")


def _big_circle(ax, x, y, radius, color, text="", text_color="white", text_size=18):
    """큰 색깔 동그라미 + 안에 한 글자."""
    ax.add_patch(Circle((x, y), radius, color=color, zorder=5,
                        transform=ax.transAxes, clip_on=False))
    if text:
        ax.text(x, y, text, fontsize=text_size, fontweight="bold",
                color=text_color, ha="center", va="center",
                transform=ax.transAxes, zorder=6)


def _card(fig, x, y, w, h, title, body, color="#3b82f6",
          title_size=14, body_size=11, title_color=None):
    """둥근 카드."""
    ax = fig.add_axes([x, y, w, h]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                 transform=ax.transAxes,
                                 facecolor="white", edgecolor=color,
                                 linewidth=2))
    ax.text(0.5, 0.82, title, fontsize=title_size, fontweight="bold",
            color=title_color or color, ha="center", va="center",
            transform=ax.transAxes)
    ax.text(0.5, 0.42, body, fontsize=body_size, color="#1f2937",
            ha="center", va="center", transform=ax.transAxes,
            linespacing=1.5, wrap=True)


def _color_pill(ax, x, y, code, w=0.08, h=0.06, with_label=True):
    """가로 색깔 알약 (작은 칸 표시용)."""
    color = COLOR_HEX.get(code, "#9ca3af")
    ax.add_patch(Rectangle((x, y), w, h, transform=ax.transAxes,
                           facecolor=color, edgecolor="white", linewidth=2,
                           clip_on=False, zorder=5))
    if with_label:
        short = COLOR_SHORT.get(code, "-")
        txt_color = "white" if code in ("G", "R", "O") else "#1f2937"
        ax.text(x + w/2, y + h/2, short, fontsize=12,
                fontweight="bold", color=txt_color,
                ha="center", va="center",
                transform=ax.transAxes, zorder=6)


def load_cases():
    df = pd.read_csv(CASES_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    for col in ["score_v2", "mfe_d5_pct", "mae_d5_pct"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ───────── 페이지 1 - 표지 ─────────
def slide_1_cover(pdf, total):
    fig = plt.figure(figsize=SLIDE)

    # 큰 그라데이션 느낌 박스
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 0.55, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))

    # 제목
    fig.text(0.08, 0.82, "전일 종가 색깔로 본",
             fontsize=22, color="white", ha="left", va="center")
    fig.text(0.08, 0.72, "한 달치 결과 보고서",
             fontsize=34, fontweight="bold", color="white",
             ha="left", va="center")
    fig.text(0.08, 0.62, "2026-04-09 ~ 2026-05-13  (22 거래일)",
             fontsize=13, color="#c7d2fe", ha="left", va="center")

    # 5색 동그라미 가로 배치 (제목 아래)
    radius = 0.045
    y_pos = 0.40
    colors = [("G", "강"), ("Y", "회"), ("O", "실"), ("R", "약"), ("X", "보")]
    start_x = 0.12
    gap = 0.16
    for i, (code, short) in enumerate(colors):
        x_pos = start_x + i * gap
        circle = Circle((x_pos, y_pos), radius, color=COLOR_HEX[code],
                        transform=fig.transFigure, zorder=5)
        fig.patches.append(circle)
        txt_color = "white" if code in ("G", "R", "O") else "#1f2937"
        fig.text(x_pos, y_pos, short, fontsize=20, fontweight="bold",
                 color=txt_color, ha="center", va="center", zorder=6)
        fig.text(x_pos, y_pos - 0.08, COLOR_KO[code], fontsize=11,
                 color="#1f2937", ha="center", va="center", fontweight="bold")

    # 하단 부드러운 안내
    ax2 = fig.add_axes([0.08, 0.08, 0.84, 0.13]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                  transform=ax2.transAxes,
                                  facecolor="#dbeafe", edgecolor="#1e3a8a",
                                  linewidth=1.5))
    ax2.text(0.03, 0.75, "처음 보시는 분도 괜찮습니다",
             fontsize=15, fontweight="bold", color="#1e3a8a", va="center")
    ax2.text(0.03, 0.30,
             "다음 페이지부터 그림으로 천천히 설명합니다. 어려운 용어 없이, 색깔만 봐도 결과가 보이도록.",
             fontsize=11.5, color="#1f2937", va="center")

    _slide_footer(fig, 1, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 2 - 이 보고서는? ─────────
def slide_2_what(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "이 보고서는 무엇인가요?",
           "한 페이지로 답합니다")

    cards = [
        ("우리가 산다고 가정한 종목들",
         "최근 한 달 동안\n점수제(V2)와 거래대금 기준이\n각각 고른 종목 = 약 200개",
         "#3b82f6"),
        ("그 종목들이 5일 동안\n어떻게 움직였나",
         "매일 색깔 하나씩 매겨서\n5색 흐름으로 정리\n(초록·노랑·주황·빨강·회색)",
         "#16a34a"),
        ("색깔 흐름 = 결과 예측?",
         "어떤 색깔 흐름이\n결과가 좋았는지\n표/그림으로 비교",
         "#7c3aed"),
    ]
    card_w = 0.27
    gap = 0.025
    start_x = (1 - 3 * card_w - 2 * gap) / 2
    for i, (title, body, color) in enumerate(cards):
        x = start_x + i * (card_w + gap)
        _card(fig, x, 0.20, card_w, 0.55, title, body, color=color,
              title_size=14, body_size=12)

    _slide_footer(fig, 2, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 3 - 5색 정의 ─────────
def slide_3_colors(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "다섯 가지 색깔이 무슨 뜻인가요",
           "어제 끝난 가격을 기준으로 - 오늘 어떻게 움직였는지")

    # 5색 카드 (가로 1줄)
    colors_data = [
        ("G", "완전 강세",
         "어제 가격 위에서만 놀고\n더 높게 끝남",
         "★ 매수세 강함"),
        ("Y", "흔들렸지만 회복",
         "잠깐 떨어졌다\n다시 위로 회복",
         "종가 방어 성공"),
        ("O", "위로 갔지만 실패",
         "한 번 위로 갔지만\n결국 아래로 끝남",
         "돌파 실패 / 윗꼬리"),
        ("R", "완전 약세",
         "어제 가격 위로\n한 번도 못 가고 떨어짐",
         "매수세 약함"),
        ("X", "변동 거의 없음",
         "어제와 비슷하거나\n데이터 부족",
         "방향 없음"),
    ]
    card_w = 0.175
    gap = 0.012
    start_x = (1 - 5 * card_w - 4 * gap) / 2
    for i, (code, name, action, meaning) in enumerate(colors_data):
        x = start_x + i * (card_w + gap)
        hex_c = COLOR_HEX[code]

        ax = fig.add_axes([x, 0.16, card_w, 0.62]); ax.axis("off")
        # 외곽 카드
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=hex_c,
                                     linewidth=2.5))
        # 큰 동그라미 + 한 글자
        ax.add_patch(Circle((0.5, 0.82), 0.13, color=hex_c,
                            transform=ax.transAxes, zorder=5))
        txt_color = "white" if code in ("G", "R", "O") else "#1f2937"
        ax.text(0.5, 0.82, COLOR_SHORT[code], fontsize=22,
                fontweight="bold", color=txt_color,
                ha="center", va="center", transform=ax.transAxes, zorder=6)
        # 이름
        ax.text(0.5, 0.61, name, fontsize=12.5, fontweight="bold",
                color=hex_c, ha="center", va="center",
                transform=ax.transAxes)
        # 행동
        ax.text(0.5, 0.38, action, fontsize=10, color="#1f2937",
                ha="center", va="center", transform=ax.transAxes,
                linespacing=1.55)
        # 의미
        ax.text(0.5, 0.13, meaning, fontsize=10, color="#6b7280",
                ha="center", va="center", transform=ax.transAxes,
                fontweight="bold", linespacing=1.4)

    _slide_footer(fig, 3, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 4 - 왜 색깔로? ─────────
def slide_4_why(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "왜 어제 끝난 가격을 기준으로 보나요",
           "운동 선수 컨디션 체크 같은 것")

    # 왼쪽 - 비유 박스
    ax = fig.add_axes([0.08, 0.18, 0.40, 0.62]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                 transform=ax.transAxes,
                                 facecolor="#fef3c7", edgecolor="#d97706",
                                 linewidth=2))
    ax.text(0.05, 0.88, "비유", fontsize=14, fontweight="bold",
            color="#78350f", va="top", transform=ax.transAxes)
    ax.text(0.05, 0.75,
            "어제 평균 페이스를 정해 놓고\n오늘 그 위/아래에서 달렸는지 매일 본다",
            fontsize=12.5, color="#78350f", va="top",
            transform=ax.transAxes, linespacing=1.7)
    ax.text(0.05, 0.45,
            "• 5일 모두 페이스 위 = 컨디션 좋음 (초록)\n"
            "• 잠깐 떨어졌다 회복 = 그래도 괜찮음 (노랑)\n"
            "• 페이스 위로 못 올라감 = 떨어짐 (빨강)",
            fontsize=11.5, color="#1f2937", va="top",
            transform=ax.transAxes, linespacing=2.0)
    ax.text(0.05, 0.10,
            "5일 모아 보면 한 주 흐름이 한눈에",
            fontsize=12, fontweight="bold", color="#78350f", va="top",
            transform=ax.transAxes)

    # 오른쪽 - 도식
    ax2 = fig.add_axes([0.55, 0.18, 0.40, 0.62]); ax2.axis("off")
    ax2.text(0.5, 0.92, "예시 - 한 종목의 5일 흐름",
             fontsize=13, fontweight="bold", color="#1e3a8a",
             ha="center", va="center", transform=ax2.transAxes)
    # 5색 알약 가로
    sample = ["G", "Y", "G", "O", "R"]
    labels = ["다음날", "2일째", "3일째", "4일째", "5일째"]
    pill_w = 0.16; gap = 0.015
    start_x = (1 - 5 * pill_w - 4 * gap) / 2
    for i, c in enumerate(sample):
        x = start_x + i * (pill_w + gap)
        hex_c = COLOR_HEX[c]
        ax2.add_patch(Rectangle((x, 0.50), pill_w, 0.18,
                                  transform=ax2.transAxes,
                                  facecolor=hex_c, edgecolor="white",
                                  linewidth=2))
        txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
        ax2.text(x + pill_w/2, 0.59, COLOR_SHORT[c],
                  fontsize=16, fontweight="bold", color=txt_color,
                  ha="center", va="center", transform=ax2.transAxes)
        ax2.text(x + pill_w/2, 0.42, labels[i], fontsize=9.5,
                  color="#6b7280", ha="center", va="center",
                  transform=ax2.transAxes)
    # 화살표 (왼→오)
    ax2.annotate("", xy=(0.95, 0.59), xytext=(0.02, 0.59),
                 xycoords=ax2.transAxes,
                 arrowprops=dict(arrowstyle="->", color="#1e3a8a", lw=2))
    ax2.text(0.5, 0.28, "강세→회복→강세→실패→약세",
              fontsize=12, color="#1f2937", ha="center", va="center",
              transform=ax2.transAxes, fontweight="bold")
    ax2.text(0.5, 0.15,
              "처음엔 좋았지만 점점 약해진 종목",
              fontsize=11, color="#6b7280", ha="center", va="center",
              transform=ax2.transAxes)

    _slide_footer(fig, 4, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 5 - 한 페이지 결론 ─────────
def slide_5_conclusion(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "한 페이지 결론",
           "각 방식이 고른 종목, 5일 후 어떻게 됐나")

    pols = [
        ("V2_FINAL_TOP3", "V2 점수제", "#7c3aed"),
        ("P0_TRADING_VALUE_TOP3", "거래대금 Top3", "#3b82f6"),
        ("P0_LEGACY_D0_RANK_TOP3", "관심도 Top3", "#0891b2"),
        ("D0_POOL_ALL_RECENT_1M", "전체 D0 풀", "#6b7280"),
    ]
    card_w = 0.21
    gap = 0.018
    start_x = (1 - 4 * card_w - 3 * gap) / 2

    for i, (key, name, color) in enumerate(pols):
        sub = cases[cases["policy_key"] == key]
        n = len(sub)
        if n == 0:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        profit_pct = profit * 100 / max(n, 1)
        loss_pct = loss * 100 / max(n, 1)

        x = start_x + i * (card_w + gap)
        ax = fig.add_axes([x, 0.18, card_w, 0.62]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color,
                                     linewidth=2.5))
        # 정책 이름
        ax.text(0.5, 0.91, name, fontsize=14, fontweight="bold",
                color=color, ha="center", va="center",
                transform=ax.transAxes)
        # 종목 수 (큰 숫자)
        ax.text(0.5, 0.75, f"{n}", fontsize=36, fontweight="bold",
                color="#1f2937", ha="center", va="center",
                transform=ax.transAxes)
        ax.text(0.5, 0.60, "건", fontsize=11, color="#6b7280",
                ha="center", va="center", transform=ax.transAxes)
        # 이익 vs 손실 비교 막대
        bar_y = 0.40
        bar_h = 0.05
        # 이익 (초록)
        ax.add_patch(Rectangle((0.10, bar_y), 0.80 * (profit_pct / 100), bar_h,
                                transform=ax.transAxes,
                                facecolor="#16a34a", edgecolor="none"))
        # 손실 (빨강) — 같은 줄 옆에
        ax.text(0.5, bar_y - 0.06, f"이익 먼저  {profit_pct:.0f}%",
                fontsize=11, color="#16a34a", fontweight="bold",
                ha="center", va="center", transform=ax.transAxes)

        bar_y2 = 0.22
        ax.add_patch(Rectangle((0.10, bar_y2), 0.80 * (loss_pct / 100), bar_h,
                                transform=ax.transAxes,
                                facecolor="#dc2626", edgecolor="none"))
        ax.text(0.5, bar_y2 - 0.06, f"손실 먼저  {loss_pct:.0f}%",
                fontsize=11, color="#dc2626", fontweight="bold",
                ha="center", va="center", transform=ax.transAxes)

    # 하단 한 줄 결론
    fig.text(0.5, 0.08,
             "★ 가장 안정적: 거래대금 Top3 / 점수제 V2 도 비슷. 전체 D0 풀은 약함",
             fontsize=12.5, fontweight="bold", color="#1e3a8a",
             ha="center", va="center")

    _slide_footer(fig, 5, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 6 - 색깔 흐름 시각화 ─────────
def slide_6_flow(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "색깔 흐름이란?",
           "매일 색깔 1개씩, 5일 이어 붙이면 흐름")

    # 3가지 예시 행
    examples = [
        ("좋은 흐름",   ["G", "G", "Y", "G", "G"], "#16a34a", "강세 + 잠깐 회복 + 강세 지속"),
        ("중간 흐름",  ["Y", "O", "Y", "O", "O"], "#f97316", "회복했다 실패 반복 - 변동성"),
        ("나쁜 흐름",  ["O", "R", "R", "O", "R"], "#dc2626", "실패 + 약세 반복 - 위험"),
    ]

    pill_w = 0.10
    gap = 0.012
    flow_start_x = 0.30

    for i, (label, path, color, desc) in enumerate(examples):
        y = 0.65 - i * 0.20
        # 왼쪽 라벨
        fig.text(0.08, y + 0.05, label, fontsize=14, fontweight="bold",
                 color=color, va="center")
        # 5색 알약
        for j, c in enumerate(path):
            x = flow_start_x + j * (pill_w + gap)
            hex_c = COLOR_HEX[c]
            ax = fig.add_axes([x, y, pill_w, 0.10]); ax.axis("off")
            ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=hex_c, edgecolor="white",
                                    linewidth=2))
            txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
            ax.text(0.5, 0.5, COLOR_SHORT[c], fontsize=18,
                    fontweight="bold", color=txt_color,
                    ha="center", va="center", transform=ax.transAxes)
        # 오른쪽 설명
        fig.text(0.84, y + 0.05, desc, fontsize=11, color="#1f2937",
                 va="center", style="italic")

    # 라벨 (다음날 ~ 5일째)
    labels = ["다음날", "2일째", "3일째", "4일째", "5일째"]
    for j, lab in enumerate(labels):
        x = flow_start_x + j * (pill_w + gap)
        fig.text(x + pill_w/2, 0.85, lab, fontsize=10,
                 color="#6b7280", ha="center", va="center")

    # 하단 메모
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.08]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                 transform=ax.transAxes,
                                 facecolor="#dbeafe", edgecolor="#1e3a8a"))
    ax.text(0.5, 0.5,
            "이렇게 5칸을 색만 봐도 그 종목의 한 주 흐름을 한눈에 볼 수 있습니다",
            fontsize=12, color="#1e3a8a", fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)

    _slide_footer(fig, 6, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 7 - V2 다음날 색깔 분포 ─────────
def slide_7_v2_d1_dist(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "V2 점수제 - 다음날 색깔 분포",
           "66개 종목이 다음 날 어떤 색깔로 시작했나")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"]
    n_total = len(v2)
    counts = v2["dplus1_color"].value_counts()

    # 막대그래프 (좌측)
    ax = fig.add_axes([0.08, 0.18, 0.50, 0.62])
    colors_order = ["G", "Y", "O", "R", "X"]
    values = [int(counts.get(c, 0)) for c in colors_order]
    pcts = [v * 100 / max(n_total, 1) for v in values]
    bars = ax.bar(range(5),
                  values,
                  color=[COLOR_HEX[c] for c in colors_order],
                  edgecolor="white", linewidth=2)
    for i, (b, n, p) in enumerate(zip(bars, values, pcts)):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5,
                f"{n}건\n({p:.0f}%)", ha="center", va="bottom",
                fontsize=13, fontweight="bold", color="#1f2937")
    ax.set_xticks(range(5))
    ax.set_xticklabels([COLOR_KO[c] for c in colors_order],
                       fontsize=12)
    ax.set_ylabel("종목 수", fontsize=12)
    ax.set_ylim(0, max(values) * 1.4 if values else 10)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 우측 해석 카드
    ax_card = fig.add_axes([0.62, 0.20, 0.32, 0.55]); ax_card.axis("off")
    ax_card.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                       transform=ax_card.transAxes,
                                       facecolor="#dbeafe",
                                       edgecolor="#1e3a8a", linewidth=2))
    # 가장 많은 색
    top_c = max(zip(colors_order, values), key=lambda x: x[1])
    ax_card.text(0.06, 0.85, "가장 많이 나온 색",
                 fontsize=12, color="#6b7280", va="center",
                 transform=ax_card.transAxes)
    # 큰 동그라미
    ax_card.add_patch(Circle((0.20, 0.65), 0.10,
                              color=COLOR_HEX[top_c[0]],
                              transform=ax_card.transAxes, zorder=5))
    ax_card.text(0.20, 0.65, COLOR_SHORT[top_c[0]], fontsize=22,
                 fontweight="bold",
                 color="white" if top_c[0] in ("G", "R", "O") else "#1f2937",
                 ha="center", va="center",
                 transform=ax_card.transAxes, zorder=6)
    ax_card.text(0.40, 0.70, COLOR_KO[top_c[0]],
                 fontsize=14, fontweight="bold", color="#1e3a8a",
                 va="center", transform=ax_card.transAxes)
    ax_card.text(0.40, 0.60, f"{top_c[1]}건 ({top_c[1]*100/max(n_total,1):.0f}%)",
                 fontsize=12, color="#1f2937",
                 va="center", transform=ax_card.transAxes)

    ax_card.text(0.06, 0.35,
                 "V2가 고른 종목은\n다음날 노랑·주황 비중이\n가장 높음",
                 fontsize=11.5, color="#1f2937",
                 va="center", transform=ax_card.transAxes,
                 linespacing=1.7)
    ax_card.text(0.06, 0.10,
                 "= 회복형 또는 변동성 큰 종목",
                 fontsize=11, color="#6b7280", fontweight="bold",
                 va="center", transform=ax_card.transAxes)

    _slide_footer(fig, 7, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 8 - V2 vs 거래대금 vs D0 풀 ─────────
def slide_8_compare(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "V2 점수제 vs 거래대금 vs 전체 D0",
           "같은 22일 동안, 다음날 색깔 분포가 다르다")

    pols = [
        ("V2_FINAL_TOP3", "V2 점수제", "#7c3aed"),
        ("P0_TRADING_VALUE_TOP3", "거래대금", "#3b82f6"),
        ("D0_POOL_ALL_RECENT_1M", "전체 D0", "#6b7280"),
    ]
    colors_order = ["G", "Y", "O", "R", "X"]
    card_w = 0.28
    gap = 0.025
    start_x = (1 - 3 * card_w - 2 * gap) / 2

    for i, (key, name, color) in enumerate(pols):
        sub = cases[cases["policy_key"] == key]
        n = len(sub)
        counts = sub["dplus1_color"].value_counts()
        x = start_x + i * (card_w + gap)

        ax = fig.add_axes([x, 0.18, card_w, 0.60]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color,
                                     linewidth=2.5))
        # 헤더
        ax.text(0.5, 0.92, name, fontsize=14, fontweight="bold",
                color=color, ha="center", va="center",
                transform=ax.transAxes)
        ax.text(0.5, 0.83, f"종목 {n}건", fontsize=10.5,
                color="#6b7280", ha="center", va="center",
                transform=ax.transAxes)

        # 5색 막대 (가로)
        for j, c in enumerate(colors_order):
            cnt = int(counts.get(c, 0))
            pct = cnt * 100 / max(n, 1)
            bar_y = 0.70 - j * 0.13
            # 라벨 + 카운트
            ax.add_patch(Circle((0.10, bar_y + 0.04), 0.035,
                                 color=COLOR_HEX[c],
                                 transform=ax.transAxes, zorder=5))
            txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
            ax.text(0.10, bar_y + 0.04, COLOR_SHORT[c],
                    fontsize=12, fontweight="bold", color=txt_color,
                    ha="center", va="center", transform=ax.transAxes, zorder=6)
            # 막대 - 비율
            ax.add_patch(Rectangle((0.20, bar_y + 0.015), 0.55 * (pct / 100), 0.06,
                                    transform=ax.transAxes,
                                    facecolor=COLOR_HEX[c], edgecolor="none"))
            ax.text(0.78, bar_y + 0.04, f"{cnt}건 ({pct:.0f}%)",
                    fontsize=10.5, color="#1f2937",
                    va="center", transform=ax.transAxes)

    _slide_footer(fig, 8, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 9 - 결과 좋은 흐름 ─────────
def slide_9_best_paths(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "결과가 좋았던 색깔 흐름 TOP 5",
           "V2 점수제 - 이익 먼저 닿은 비율 높은 흐름")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    grouped = []
    for path, sub in v2.groupby("color_path"):
        n = len(sub)
        if n < 2:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        grouped.append({
            "path": path, "n": n,
            "profit_pct": profit * 100 / n,
            "loss_pct": loss * 100 / n,
            "diff": (profit - loss) * 100 / n,
        })
    best = sorted(grouped, key=lambda x: (x["diff"], x["n"]), reverse=True)[:5]

    pill_w = 0.07
    gap = 0.008
    flow_start_x = 0.30
    for i, r in enumerate(best):
        y = 0.70 - i * 0.13
        # 순위
        fig.text(0.06, y + 0.04, f"#{i+1}", fontsize=18, fontweight="bold",
                 color="#16a34a", va="center")
        # 5색 알약
        parts = r["path"].split("-")
        for j, c in enumerate(parts[:5]):
            x = flow_start_x + j * (pill_w + gap)
            hex_c = COLOR_HEX.get(c, "#9ca3af")
            ax = fig.add_axes([x, y, pill_w, 0.08]); ax.axis("off")
            ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=hex_c, edgecolor="white",
                                    linewidth=2))
            txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
            ax.text(0.5, 0.5, COLOR_SHORT.get(c, "-"),
                    fontsize=14, fontweight="bold", color=txt_color,
                    ha="center", va="center", transform=ax.transAxes)
        # 결과
        fig.text(0.78, y + 0.05,
                 f"표본 {r['n']}건  ·  이익 {r['profit_pct']:.0f}%  ·  손실 {r['loss_pct']:.0f}%",
                 fontsize=11, color="#1f2937", va="center")
        fig.text(0.78, y + 0.02,
                 f"차이 +{r['diff']:.0f}%p",
                 fontsize=11.5, fontweight="bold", color="#16a34a",
                 va="center")

    # 헤더
    labels = ["다음날", "2일째", "3일째", "4일째", "5일째"]
    for j, lab in enumerate(labels):
        x = flow_start_x + j * (pill_w + gap)
        fig.text(x + pill_w/2, 0.82, lab, fontsize=9,
                 color="#6b7280", ha="center", va="center")

    _slide_footer(fig, 9, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 10 - 결과 나쁜 흐름 ─────────
def slide_10_worst_paths(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "결과가 안 좋았던 색깔 흐름 TOP 5",
           "V2 점수제 - 손실 먼저 닿은 비율 높은 흐름 (주의)")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    grouped = []
    for path, sub in v2.groupby("color_path"):
        n = len(sub)
        if n < 2:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        grouped.append({
            "path": path, "n": n,
            "profit_pct": profit * 100 / n,
            "loss_pct": loss * 100 / n,
            "diff": (profit - loss) * 100 / n,
        })
    worst = sorted(grouped, key=lambda x: (x["diff"], -x["n"]))[:5]

    pill_w = 0.07
    gap = 0.008
    flow_start_x = 0.30
    for i, r in enumerate(worst):
        y = 0.70 - i * 0.13
        fig.text(0.06, y + 0.04, f"#{i+1}", fontsize=18, fontweight="bold",
                 color="#dc2626", va="center")
        parts = r["path"].split("-")
        for j, c in enumerate(parts[:5]):
            x = flow_start_x + j * (pill_w + gap)
            hex_c = COLOR_HEX.get(c, "#9ca3af")
            ax = fig.add_axes([x, y, pill_w, 0.08]); ax.axis("off")
            ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=hex_c, edgecolor="white",
                                    linewidth=2))
            txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
            ax.text(0.5, 0.5, COLOR_SHORT.get(c, "-"),
                    fontsize=14, fontweight="bold", color=txt_color,
                    ha="center", va="center", transform=ax.transAxes)
        fig.text(0.78, y + 0.05,
                 f"표본 {r['n']}건  ·  이익 {r['profit_pct']:.0f}%  ·  손실 {r['loss_pct']:.0f}%",
                 fontsize=11, color="#1f2937", va="center")
        fig.text(0.78, y + 0.02,
                 f"차이 {r['diff']:+.0f}%p",
                 fontsize=11.5, fontweight="bold", color="#dc2626",
                 va="center")

    labels = ["다음날", "2일째", "3일째", "4일째", "5일째"]
    for j, lab in enumerate(labels):
        x = flow_start_x + j * (pill_w + gap)
        fig.text(x + pill_w/2, 0.82, lab, fontsize=9,
                 color="#6b7280", ha="center", va="center")

    _slide_footer(fig, 10, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 11 - 다음날 색깔별 5일 결과 ─────────
def slide_11_d1_outcome(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "다음날 색깔이 알려주는 것",
           "다음날 어떤 색깔이면 5일 결과가 좋더라")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"]
    rows = []
    for c in ["G", "Y", "O", "R"]:
        sub = v2[v2["dplus1_color"] == c]
        n = len(sub)
        if n == 0:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        rows.append({
            "code": c, "n": n,
            "profit_pct": profit * 100 / n,
            "loss_pct": loss * 100 / n,
        })

    # 막대 (세로 그룹)
    ax = fig.add_axes([0.12, 0.18, 0.76, 0.62])
    x = np.arange(len(rows))
    bar_w = 0.35
    bars1 = ax.bar(x - bar_w/2, [r["profit_pct"] for r in rows], bar_w,
                    label="이익 먼저", color="#16a34a", alpha=0.9)
    bars2 = ax.bar(x + bar_w/2, [r["loss_pct"] for r in rows], bar_w,
                    label="손실 먼저", color="#dc2626", alpha=0.9)
    for b in bars1:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5,
                f"{b.get_height():.0f}%", ha="center", va="bottom",
                fontsize=13, fontweight="bold", color="#14532d")
    for b in bars2:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5,
                f"{b.get_height():.0f}%", ha="center", va="bottom",
                fontsize=13, fontweight="bold", color="#7f1d1d")
    # X축 — 큰 색깔 동그라미 (대신 텍스트 + 색)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{COLOR_KO[r['code']]}\n({r['n']}건)" for r in rows],
                        fontsize=11.5)
    # 색깔 점 추가 - X축 라벨 위에
    for i, r in enumerate(rows):
        ax.scatter([i], [-13], s=500, color=COLOR_HEX[r["code"]],
                    clip_on=False, zorder=10, edgecolor="white", linewidth=2)
    ax.set_ylabel("비율 (%)", fontsize=12)
    ax.set_ylim(0, 100)
    ax.legend(fontsize=12, loc="upper right", framealpha=0.95)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("다음날 색깔 → 5일 안 어느 쪽이 먼저 닿았나",
                 fontsize=12.5, color="#1e3a8a", pad=15)

    _slide_footer(fig, 11, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 12 - V2 22일 색깔 매트릭스 ─────────
def slide_12_matrix(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "V2 22일 색깔 매트릭스",
           "신호일별 V2 1위 종목의 5일 색깔 흐름 - 색만 봐도 한눈에")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    v2["rank_n"] = pd.to_numeric(v2["rank"], errors="coerce")
    v2_top1 = v2[v2["rank_n"] == 1].sort_values("signal_date")

    days = ["dplus1_color", "dplus2_color", "dplus3_color", "dplus4_color", "dplus5_color"]
    day_labels = ["다음날", "2일째", "3일째", "4일째", "5일째"]

    n_rows = len(v2_top1)
    cell_w = 0.07
    cell_h = (0.62) / max(n_rows, 1)
    start_x = 0.22
    start_y_top = 0.78

    # 헤더 (D+1~D+5)
    for j, lab in enumerate(day_labels):
        x = start_x + j * cell_w
        fig.text(x + cell_w/2, start_y_top + 0.01, lab, fontsize=10,
                 color="#1e3a8a", fontweight="bold",
                 ha="center", va="bottom")

    # 매트릭스
    for i, (_, r) in enumerate(v2_top1.iterrows()):
        y = start_y_top - (i + 1) * cell_h
        # 왼쪽 - 날짜
        fig.text(start_x - 0.01, y + cell_h/2,
                 r["signal_date"], fontsize=8.5, color="#6b7280",
                 ha="right", va="center")
        # 오른쪽 - 종목명
        fig.text(start_x + 5 * cell_w + 0.01, y + cell_h/2,
                 str(r.get("stock_name", ""))[:8], fontsize=8.5,
                 color="#1f2937", ha="left", va="center")
        # 5칸 색
        for j, key in enumerate(days):
            c = str(r.get(key, ""))
            x = start_x + j * cell_w
            hex_c = COLOR_HEX.get(c, "#f3f4f6")
            ax = fig.add_axes([x, y, cell_w - 0.005, cell_h - 0.003])
            ax.axis("off")
            ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=hex_c, edgecolor="white",
                                    linewidth=1))
            short = COLOR_SHORT.get(c, "-")
            txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
            ax.text(0.5, 0.5, short, fontsize=10,
                    fontweight="bold", color=txt_color,
                    ha="center", va="center", transform=ax.transAxes)

    # 하단 범례
    fig.text(0.5, 0.07,
             "강(완전 강세)  ·  회(흔들렸지만 회복)  ·  실(위로 갔지만 실패)  ·  약(완전 약세)  ·  보(변동 거의 없음)",
             fontsize=10, color="#6b7280", ha="center", va="center")

    _slide_footer(fig, 12, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 13 - 공통 후보 ─────────
def slide_13_intersection(pdf, total, cases):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "V2 와 거래대금 둘 다 고른 종목은?",
           "공통 후보 vs V2 만 vs 거래대금 만")

    rel_groups = [
        ("BOTH",     "둘 다 골랐다",       "#16a34a"),
        ("V2_ONLY",  "V2 점수제만",       "#7c3aed"),
        ("P0_ONLY",  "거래대금만",         "#3b82f6"),
    ]
    card_w = 0.28
    gap = 0.025
    start_x = (1 - 3 * card_w - 2 * gap) / 2

    for i, (key, name, color) in enumerate(rel_groups):
        sub = cases[cases["relationship_group"] == key]
        n = len(sub)
        if n == 0:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        profit_pct = profit * 100 / max(n, 1)
        loss_pct = loss * 100 / max(n, 1)

        x = start_x + i * (card_w + gap)
        ax = fig.add_axes([x, 0.20, card_w, 0.58]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color,
                                     linewidth=2.5))
        ax.text(0.5, 0.90, name, fontsize=14, fontweight="bold",
                color=color, ha="center", va="center",
                transform=ax.transAxes)
        ax.text(0.5, 0.74, f"{n}건", fontsize=32, fontweight="bold",
                color="#1f2937", ha="center", va="center",
                transform=ax.transAxes)

        # 이익 vs 손실
        ax.text(0.5, 0.50, f"이익 먼저 {profit_pct:.0f}%",
                fontsize=14, fontweight="bold", color="#16a34a",
                ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.38, f"손실 먼저 {loss_pct:.0f}%",
                fontsize=14, fontweight="bold", color="#dc2626",
                ha="center", va="center", transform=ax.transAxes)

        # 차이
        diff = profit_pct - loss_pct
        diff_color = "#16a34a" if diff > 0 else "#dc2626"
        ax.text(0.5, 0.18, f"차이 {diff:+.0f}%p",
                fontsize=15, fontweight="bold", color=diff_color,
                ha="center", va="center", transform=ax.transAxes)

    fig.text(0.5, 0.10,
             "★ 둘 다 고른 종목이 가장 안정적인 신호일 수 있다 (관찰 가설)",
             fontsize=12, fontweight="bold", color="#1e3a8a",
             ha="center", va="center")

    _slide_footer(fig, 13, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 14 - 주의 패턴 ─────────
def slide_14_warning(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "위험한 색깔 흐름 - 주의",
           "이런 패턴이 보이면 무리하지 말 것", color="#dc2626")

    warnings = [
        ("실패 마감 → 약세",
         ["O", "R"],
         "한 번 위로 갔다가 실패하고\n다음 날 약세로 이어지는 패턴",
         "장기 추세 약화 신호"),
        ("회복 실패 → 약세",
         ["Y", "O", "R"],
         "잠깐 회복했다가\n다시 실패하고 약세로 끝남",
         "매수세 약함"),
        ("강세 없이 약세 연속",
         ["O", "O", "R", "R", "O"],
         "초록(완전 강세)이 한 번도 안 나오고\n실패/약세만 반복",
         "이미 손실 구간"),
    ]
    pill_w = 0.07
    gap = 0.008

    for i, (title, path, body, note) in enumerate(warnings):
        y = 0.62 - i * 0.18
        # 좌측 제목
        fig.text(0.08, y + 0.06, title, fontsize=14, fontweight="bold",
                 color="#dc2626", va="center")
        # 5색 알약 (최대 5칸)
        n_pills = min(len(path), 5)
        flow_x = 0.32
        for j in range(n_pills):
            c = path[j]
            x = flow_x + j * (pill_w + gap)
            hex_c = COLOR_HEX.get(c, "#9ca3af")
            ax = fig.add_axes([x, y, pill_w, 0.075]); ax.axis("off")
            ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=hex_c, edgecolor="white",
                                    linewidth=2))
            txt_color = "white" if c in ("G", "R", "O") else "#1f2937"
            ax.text(0.5, 0.5, COLOR_SHORT.get(c, "-"),
                    fontsize=14, fontweight="bold", color=txt_color,
                    ha="center", va="center", transform=ax.transAxes)
        # 우측 설명
        fig.text(0.74, y + 0.06, body, fontsize=10.5, color="#1f2937",
                 va="center", linespacing=1.4)
        fig.text(0.74, y - 0.005, note, fontsize=10, color="#dc2626",
                 va="center", fontweight="bold")

    _slide_footer(fig, 14, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 15 - 이건 무엇이 아닌가 ─────────
def slide_15_not_what(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig)
    _title(fig, "이건 무엇이 아닌가요",
           "꼭 알아두세요")

    items = [
        ("매수 추천이 아닙니다",
         "지금 어떤 종목을 사라/팔라는\n조언이 아닙니다",
         "#dc2626"),
        ("미래 예측이 아닙니다",
         "한 달 동안 어떻게 됐는지\n사후에 본 자료입니다",
         "#ea580c"),
        ("자동매매 연결 없습니다",
         "주문, 계좌, API 어디에도\n연결되어 있지 않습니다",
         "#ca8a04"),
        ("표본이 충분하지 않습니다",
         "22일치만 본 결과입니다.\n1년치는 다음 단계.",
         "#0891b2"),
    ]
    card_w = 0.22
    gap = 0.02
    start_x = (1 - 4 * card_w - 3 * gap) / 2

    for i, (title, body, color) in enumerate(items):
        x = start_x + i * (card_w + gap)
        ax = fig.add_axes([x, 0.22, card_w, 0.54]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color,
                                     linewidth=2.5))
        # X 표시 (큰)
        ax.text(0.5, 0.78, "X", fontsize=46, fontweight="bold",
                color=color, ha="center", va="center",
                transform=ax.transAxes)
        # 제목
        ax.text(0.5, 0.45, title, fontsize=13, fontweight="bold",
                color="#1f2937", ha="center", va="center",
                transform=ax.transAxes)
        # 본문
        ax.text(0.5, 0.20, body, fontsize=10.5, color="#374151",
                ha="center", va="center", transform=ax.transAxes,
                linespacing=1.55)

    fig.text(0.5, 0.10,
             "이 보고서는 V2 점수제가 어떤 종목을 골랐는지 사후에 색깔로 본 자료입니다",
             fontsize=12, fontweight="bold", color="#7f1d1d",
             ha="center", va="center")

    _slide_footer(fig, 15, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 16 - 다음 단계 ─────────
def slide_16_next(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    _slide_bg(fig, top_color="#16a34a")
    _title(fig, "다음 단계",
           "지금 한 달 → 앞으로 어디까지?", color="#14532d")

    steps = [
        ("1단계", "1년치 확장",
         "22일 → 252일\n표본 늘려 안정성 검증",
         "#16a34a"),
        ("2단계", "차트 연동",
         "표 행 클릭하면\n5일 차트 + 색깔 배경 표시",
         "#0891b2"),
        ("3단계", "현실 체결 보정",
         "색깔이 좋아도\n진짜 그 가격에 살 수 있었나\n별도 검증",
         "#7c3aed"),
        ("4단계", "단계적 운영 검토",
         "통계 충분히 쌓이면\nPaper Watch → 본격 운영\n사용자 명시 승인 후",
         "#dc2626"),
    ]
    card_w = 0.22
    gap = 0.02
    start_x = (1 - 4 * card_w - 3 * gap) / 2

    for i, (step, title, body, color) in enumerate(steps):
        x = start_x + i * (card_w + gap)
        ax = fig.add_axes([x, 0.20, card_w, 0.58]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color,
                                     linewidth=2.5))
        # Step 라벨
        ax.add_patch(FancyBboxPatch((0.1, 0.82), 0.8, 0.12,
                                     boxstyle="round,pad=0.008",
                                     transform=ax.transAxes,
                                     facecolor=color, edgecolor="none"))
        ax.text(0.5, 0.88, step, fontsize=12, fontweight="bold",
                color="white", ha="center", va="center",
                transform=ax.transAxes)
        # 제목
        ax.text(0.5, 0.65, title, fontsize=14, fontweight="bold",
                color=color, ha="center", va="center",
                transform=ax.transAxes)
        # 본문
        ax.text(0.5, 0.30, body, fontsize=10.5, color="#1f2937",
                ha="center", va="center", transform=ax.transAxes,
                linespacing=1.65)

    _slide_footer(fig, 16, total); pdf.savefig(fig); plt.close(fig)


# ───────── 페이지 17 - 한 줄 요약 ─────────
def slide_17_summary(pdf, total):
    fig = plt.figure(figsize=SLIDE)
    # 큰 배경
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))

    # 5색 가로 띠 (장식)
    for i, c in enumerate(["G", "Y", "O", "R", "X"]):
        ax.add_patch(Rectangle((0.1 + i * 0.16, 0.80), 0.15, 0.06,
                                transform=ax.transAxes,
                                facecolor=COLOR_HEX[c], edgecolor="white",
                                linewidth=2))

    # 큰 제목
    fig.text(0.5, 0.66, "한 줄 요약",
             fontsize=32, fontweight="bold", color="white",
             ha="center", va="center")

    # 핵심 메시지 박스
    ax_msg = fig.add_axes([0.10, 0.32, 0.80, 0.28]); ax_msg.axis("off")
    ax_msg.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                      transform=ax_msg.transAxes,
                                      facecolor="white",
                                      edgecolor="#facc15", linewidth=3))
    ax_msg.text(0.5, 0.72,
                "어제 끝난 가격을 기준으로",
                fontsize=20, color="#1e3a8a",
                ha="center", va="center",
                transform=ax_msg.transAxes)
    ax_msg.text(0.5, 0.45,
                "오늘 그 위에서 놀았는지 아래에서 놀았는지",
                fontsize=20, color="#1e3a8a",
                ha="center", va="center",
                transform=ax_msg.transAxes)
    ax_msg.text(0.5, 0.18,
                "색깔만 봐도 한 주 흐름이 보입니다",
                fontsize=22, fontweight="bold", color="#dc2626",
                ha="center", va="center",
                transform=ax_msg.transAxes)

    # 하단
    fig.text(0.5, 0.20,
             "단, 색깔이 좋아도 실제 매매와는 별개입니다.",
             fontsize=14, color="#cbd5e0", ha="center", va="center")
    fig.text(0.5, 0.13,
             "이 보고서는 사후 복기용이며, 매수 추천이 아닙니다.",
             fontsize=14, color="#cbd5e0", ha="center", va="center")

    fig.text(0.5, 0.05,
             f"작성 {datetime.now().strftime('%Y-%m-%d')}  ·  ClosingBell 연구 자료",
             fontsize=10, color="#9ca3af", ha="center", va="center")

    _slide_footer(fig, total, total); pdf.savefig(fig); plt.close(fig)


# ───────── Main ─────────
def build(out_path: Path):
    cases = load_cases()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 17
    with PdfPages(out_path) as pdf:
        slide_1_cover(pdf, total)
        slide_2_what(pdf, total)
        slide_3_colors(pdf, total)
        slide_4_why(pdf, total)
        slide_5_conclusion(pdf, total, cases)
        slide_6_flow(pdf, total)
        slide_7_v2_d1_dist(pdf, total, cases)
        slide_8_compare(pdf, total, cases)
        slide_9_best_paths(pdf, total, cases)
        slide_10_worst_paths(pdf, total, cases)
        slide_11_d1_outcome(pdf, total, cases)
        slide_12_matrix(pdf, total, cases)
        slide_13_intersection(pdf, total, cases)
        slide_14_warning(pdf, total)
        slide_15_not_what(pdf, total)
        slide_16_next(pdf, total)
        slide_17_summary(pdf, total)

    size_kb = out_path.stat().st_size / 1024
    print(f"[ok] {out_path}  ({size_kb:.1f} KB, {total} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(r"C:\Users\PYJ\Downloads\PREV_CLOSE_COLOR_SLIDES_KR_20260516.pdf"))
    args = ap.parse_args()
    build(args.out)
