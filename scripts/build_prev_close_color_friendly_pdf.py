"""
전일 종가 기준 색깔 — 한 달치 복기 PDF (비전문가용).

사용자 지시 (2026-05-15 22:27):
    - 코드명·약어 안 쓰기 (D+1 → '다음 날', MFE → '가장 높이 올라간 폭', first-touch → '먼저 닿은 쪽')
    - 지금 무슨 작업인지 몰라도 알아볼 수 있게
    - 5색 의미부터 그림처럼 설명

입력:
    CHATGPT_WEB_PREV_CLOSE_COLOR_CASES_RECENT_1M_20260515.csv      (677행, 22일×4정책)
    PREV_CLOSE_COLOR_DAILY_SUMMARY_RECENT_1M_20260515.csv          (88행, 일자×정책)
    PREV_CLOSE_COLOR_PATTERN_SUMMARY_RECENT_1M_20260515.csv        (481행, 색깔 흐름×정책)

페이지 (~18 페이지, A4 가로, Malgun Gothic, 글리프 경고 0):
    1. 표지 + 한 페이지 안내
    2. "이 색깔이 무슨 뜻인가" - 5색 그림 설명
    3. "왜 전일 종가를 보는가" - 비전문가용 이유 설명
    4. 한 페이지 결론 (V2/P0/D0풀 핵심 수치)
    5. 정책별 다음 날 색깔 분포 막대그래프
    6. 다음 날 색깔별 5일 결과 (색깔이 알려주는 것)
    7. V2가 고른 종목, 한 달 색깔 흐름 막대그래프
    8. V2 가장 좋은 색깔 흐름 TOP 5 (성공 패턴)
    9. V2 가장 안 좋은 색깔 흐름 TOP 5 (실패 패턴)
   10. V2 색깔 분포 히트맵 (다음날~5일째 각각)
   11~14. V2 22일 종목 일자별 상세 표 (페이지당 ~6일씩)
   15. V2 만 vs P0 만 vs 공통 비교
   16. 평균 변동 폭 (가장 많이 오른 폭 / 가장 많이 떨어진 폭)
   17. 한 줄 정리 + 다음 볼 것
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
from matplotlib.patches import Rectangle, FancyBboxPatch

for tf in (Path(r"C:\Windows\Fonts\malgun.ttf"), Path(r"C:\Windows\Fonts\malgunbd.ttf")):
    if tf.exists():
        font_manager.fontManager.addfont(str(tf))
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

A4_LANDSCAPE = (11.7, 8.3)

DOWN = Path(r"C:\Users\PYJ\Downloads")
CASES_CSV = DOWN / "CHATGPT_WEB_PREV_CLOSE_COLOR_CASES_RECENT_1M_20260515.csv"
DAILY_CSV = DOWN / "PREV_CLOSE_COLOR_DAILY_SUMMARY_RECENT_1M_20260515.csv"
PATTERN_CSV = DOWN / "PREV_CLOSE_COLOR_PATTERN_SUMMARY_RECENT_1M_20260515.csv"

# 색깔 시각 매핑
COLOR_HEX = {
    "G": "#16a34a",  # 초록
    "Y": "#facc15",  # 노랑
    "O": "#f97316",  # 주황
    "R": "#dc2626",  # 빨강
    "X": "#9ca3af",  # 회색
}
COLOR_NAME_KO = {
    "G": "완전 강세",
    "Y": "흔들렸지만 회복",
    "O": "위로 갔지만 실패",
    "R": "완전 약세",
    "X": "변동 거의 없음",
}
COLOR_EMOJI_ASCII = {
    "G": "●",   # 초록 동그라미
    "Y": "●",
    "O": "●",
    "R": "●",
    "X": "○",
}
POLICY_KO = {
    "V2_FINAL_TOP3":          "V2 점수제 Top3 (지금 운영 중)",
    "P0_TRADING_VALUE_TOP3":  "기존 거래대금 Top3",
    "P0_LEGACY_D0_RANK_TOP3": "기존 관심도 순위 Top3",
    "D0_POOL_ALL_RECENT_1M":  "전체 감시 종목 (D0 풀)",
}


# ─────── 공통 유틸 ───────
def _header(fig, title: str, sub: str = ""):
    ax = fig.add_axes([0.0, 0.93, 1.0, 0.07]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.04, 0.55, title, fontsize=14, fontweight="bold", color="white", va="center")
    if sub:
        ax.text(0.96, 0.55, sub, fontsize=8.5, color="#c7d2fe", va="center", ha="right")


def _footer(fig, p: int, total: int):
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.028]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#f1f5f9", edgecolor="none"))
    ax.text(0.04, 0.5,
            "최근 한 달, 우리가 고른 종목들이 어떻게 움직였나  ·  연구 자료  ·  매수 추천 아님",
            fontsize=7, color="#475569", va="center")
    ax.text(0.96, 0.5, f"{p} / {total}", fontsize=7.5,
            color="#475569", va="center", ha="right")


def _band(fig, y: float, num: int, title: str, color: str = "#dbeafe", text_color: str = "#1e3a8a"):
    ax = fig.add_axes([0.04, y, 0.92, 0.038]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor=color, edgecolor="none"))
    ax.text(0.01, 0.5, f"{num}. {title}" if num else title,
            fontsize=10.5, fontweight="bold", color=text_color, va="center")


def _table(ax, header, rows, col_widths, header_color="#e0e7ff",
           font_size=8.5, scale=1.6, cell_align="center", color_cols=None):
    """표 생성. color_cols = {col_index: 'G'|'Y'|'O'|'R'|'X' or 'auto'} 면 해당 칸 배경색.
    'auto' 면 해당 셀 값(0이면 회색, >0이면 매핑된 색)."""
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=9, color="#999"); return
    t = ax.table(cellText=rows, colLabels=header, loc="upper left",
                 cellLoc=cell_align, colWidths=col_widths)
    t.auto_set_font_size(False); t.set_fontsize(font_size); t.scale(1.0, scale)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold", color="#1e3a8a")
        else:
            # 색깔 카운트 컬럼이면 배경 색칠
            if color_cols and c in color_cols:
                code = color_cols[c]
                # 값이 0 또는 '0' 이면 옅은 배경, 아니면 색깔 진하게
                val_text = rows[r - 1][c] if r - 1 < len(rows) and c < len(rows[r - 1]) else ""
                try:
                    val_num = int(str(val_text).strip())
                except Exception:
                    val_num = 0
                bg = COLOR_HEX.get(code, "#9ca3af") if val_num > 0 else "#f3f4f6"
                cell.set_facecolor(bg)
                if val_num > 0:
                    # 가독성: 진한 배경에 흰색/검정 글씨
                    txt_color = "white" if code in ("G", "R", "O") else "#1f2937"
                    cell.set_text_props(weight="bold", color=txt_color)
            else:
                cell.set_facecolor("#ffffff" if (r - 1) % 2 == 0 else "#f8fafc")


def _color_dot(ax, x: float, y: float, code: str, size: float = 0.04):
    """색깔 동그라미 그리기 (좌표는 axes transAxes 기준)."""
    color = COLOR_HEX.get(code, "#9ca3af")
    circle = plt.Circle((x, y), size, color=color, transform=ax.transAxes,
                        clip_on=False, zorder=10)
    ax.add_patch(circle)


# ─────── 데이터 로딩 ───────
def load_data():
    cases = pd.read_csv(CASES_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    daily = pd.read_csv(DAILY_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    pattern = pd.read_csv(PATTERN_CSV, dtype=str, encoding="utf-8-sig").fillna("")

    # 수치 변환
    for col in ["score_v2", "mfe_d5_pct", "mae_d5_pct", "entry_1500",
                "green_count", "yellow_count", "orange_count", "red_count", "gray_count",
                "dplus1_return_vs_prev_close_pct", "dplus5_return_vs_prev_close_pct"]:
        if col in cases.columns:
            cases[col] = pd.to_numeric(cases[col], errors="coerce")

    for col in daily.columns:
        if col not in ("signal_date", "policy_key", "policy_label_ko"):
            daily[col] = pd.to_numeric(daily[col], errors="coerce")

    for col in pattern.columns:
        if col not in ("policy_key", "color_path", "policy_label_ko"):
            pattern[col] = pd.to_numeric(pattern[col], errors="coerce")

    return cases, daily, pattern


# ─────── 페이지 1 — 표지 ───────
def page_1_cover(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)

    ax = fig.add_axes([0.0, 0.76, 1.0, 0.24]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.05, 0.68, "최근 한 달, 우리가 고른 종목들이 어떻게 움직였나",
            fontsize=18, fontweight="bold", color="white", va="center")
    ax.text(0.05, 0.36, "전일 종가 기준 색깔로 보는 한 달치 결과 보고서",
            fontsize=11.5, color="#dbeafe", va="center")
    ax.text(0.05, 0.10,
            f"기간: 2026-04-09 ~ 2026-05-13 (22 거래일)  ·  "
            f"작성 {datetime.now().strftime('%Y-%m-%d')}  ·  연구 자료",
            fontsize=9, color="#cbd5e0", va="center")

    # 한 페이지 안내 — 친근하게
    _band(fig, 0.69, 0, "이 보고서가 답하는 질문", color="#fef3c7", text_color="#78350f")

    ax = fig.add_axes([0.05, 0.36, 0.90, 0.32]); ax.axis("off")
    questions = [
        ("Q1.", "우리가 고른 종목들이 다음 날 어떻게 시작했나요?",
         "전일 종가(어제 끝난 가격)와 비교해서 색깔로 표시합니다."),
        ("Q2.", "5일 동안 그 종목들이 어떤 흐름으로 갔나요?",
         "하루씩 색깔을 이어 보면 5색 흐름이 나옵니다. 예: 초록→노랑→초록..."),
        ("Q3.", "어떤 색깔 흐름이 결과가 좋았나요?",
         "익절선(+2%, +3%) 먼저 닿은 흐름 vs 손절선(-2%, -3%) 먼저 닿은 흐름을 비교합니다."),
        ("Q4.", "점수제(V2)와 거래대금 기준(기존)이 다른가요?",
         "같은 22 거래일 동안 두 방식이 고른 종목의 색깔 분포를 비교합니다."),
    ]
    y = 0.95
    for marker, q, a in questions:
        ax.text(0.0, y, marker, fontsize=12, fontweight="bold", color="#78350f", va="top")
        ax.text(0.05, y, q, fontsize=10.5, fontweight="bold", color="#1f2937", va="top")
        ax.text(0.05, y - 0.06, a, fontsize=9, color="#374151", va="top", wrap=True)
        y -= 0.22

    # 하단 — 부드러운 안내
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.16]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                 transform=ax.transAxes,
                                 facecolor="#dbeafe", edgecolor="#1e3a8a", linewidth=1.2))
    ax.text(0.02, 0.84, "★ 처음 보시는 분도 괜찮습니다", fontsize=10.5,
            fontweight="bold", color="#1e3a8a", va="center")
    ax.text(0.02, 0.50,
            "다음 페이지에서 ‘이 색깔이 무슨 뜻인지’ 부터 그림으로 설명합니다.\n"
            "    초록 = 강세, 노랑 = 흔들렸다 회복, 주황 = 실패 마감, 빨강 = 약세\n"
            "어려운 용어 (코드명·약어) 는 한글로 풀어서 썼습니다.",
            fontsize=9.5, color="#1f2937", va="center", linespacing=1.65)
    ax.text(0.02, 0.10,
            "주의: 이 보고서는 ‘이런 종목이 어떻게 움직였는지 사후에 보는 자료’ 입니다. "
            "매수·매도 추천이 아닙니다.",
            fontsize=8.5, color="#7f1d1d", va="center", fontweight="bold")

    _footer(fig, 1, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 2 — 색깔이 무슨 뜻 ───────
def page_2_colors_explained(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "2. 이 색깔이 무슨 뜻인가요",
            "어제 끝난 가격을 기준으로 오늘 어떻게 움직였나")

    _band(fig, 0.84, 1, "전일 종가 = ‘어제 시장이 끝난 가격’")
    ax = fig.add_axes([0.04, 0.78, 0.92, 0.05]); ax.axis("off")
    ax.text(0.0, 0.5,
            "주식이 매일 ‘어제 끝난 가격’ 보다 위에서 노는지, 아래에서 노는지 — 그것만 봅니다.",
            fontsize=11, color="#374151")

    # 5색 카드를 1행으로 — 그림 같이
    colors_info = [
        ("G", "완전 강세",
         "어제 가격 위에서만 놀고\n더 높게 끝남",
         "어제 가격이 ‘바닥’ 처럼 받쳐줌\n매수세 강함"),
        ("Y", "흔들렸지만 회복",
         "잠깐 아래로 떨어졌다가\n다시 올라와 위로 끝남",
         "눌렸다가 회복 — 종가 방어\n매수세 다시 들어옴"),
        ("O", "위로 갔지만 실패",
         "한 번 위로 올라갔지만\n결국 아래로 떨어져 끝남",
         "‘돌파 실패’ 또는 ‘윗꼬리’\n매도 압력 강함"),
        ("R", "완전 약세",
         "어제 가격 위로 한 번도\n못 가고 떨어진 채 끝남",
         "어제 가격이 ‘천장’ 역할\n매수세 약함"),
        ("X", "변동 거의 없음",
         "어제와 거의 같거나\n데이터가 부족함",
         "방향 없음"),
    ]
    box_w = 0.18; gap = 0.005
    start_x = 0.04
    for i, (code, name, action, meaning) in enumerate(colors_info):
        x = start_x + i * (box_w + gap)
        ax = fig.add_axes([x, 0.18, box_w, 0.58]); ax.axis("off")
        color = COLOR_HEX[code]
        # 큰 색깔 동그라미
        circle = plt.Circle((0.5, 0.86), 0.10, color=color,
                            transform=ax.transAxes, clip_on=False, zorder=5)
        ax.add_patch(circle)
        # 이름
        ax.text(0.5, 0.70, name, fontsize=14, fontweight="bold",
                color=color, ha="center", va="center", transform=ax.transAxes)
        # 실제 모습
        ax.add_patch(FancyBboxPatch((0.05, 0.36), 0.90, 0.28,
                                     boxstyle="round,pad=0.008",
                                     transform=ax.transAxes,
                                     facecolor="#f8fafc", edgecolor="#cbd5e0"))
        ax.text(0.5, 0.59, "이런 모습", fontsize=9, color="#6b7280",
                ha="center", va="center", transform=ax.transAxes,
                fontweight="bold")
        ax.text(0.5, 0.45, action, fontsize=10, color="#1f2937",
                ha="center", va="center", transform=ax.transAxes,
                linespacing=1.5)
        # 의미
        ax.text(0.5, 0.27, "무슨 뜻인가", fontsize=9, color=color,
                ha="center", va="center", transform=ax.transAxes,
                fontweight="bold")
        ax.text(0.5, 0.13, meaning, fontsize=9.5, color="#374151",
                ha="center", va="center", transform=ax.transAxes,
                linespacing=1.55)

    # 하단 — "5일 동안 색깔이 이어지면 흐름"
    _band(fig, 0.10, 2, "5일 동안 이 색깔들이 이어지면 ‘색깔 흐름’ 입니다",
          color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.05]); ax.axis("off")
    ax.text(0.0, 0.5,
            "예: 다음 날 ●초록 → 2일째 ●노랑 → 3일째 ●초록 → 4일째 ●초록 → 5일째 ●주황   "
            "= ‘초록-노랑-초록-초록-주황’ 흐름",
            fontsize=10.5, color="#14532d")

    _footer(fig, 2, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 3 — 왜 보는가 ───────
def page_3_why(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "3. 왜 ‘어제 끝난 가격’을 기준으로 보나요",
            "단순하지만 가장 명확한 기준")

    _band(fig, 0.84, 1, "지금까지 보던 방식과 다른 점")
    ax = fig.add_axes([0.04, 0.40, 0.92, 0.43]); ax.axis("off")
    paras = [
        "지금까지 우리가 자주 본 것:",
        "    • ‘5일 동안 +3% 한 번이라도 닿았나’ (이걸 ‘도달률’ 이라고 부릅니다)",
        "    • ‘+2%와 -2% 중 어느 쪽이 먼저 닿았나’ (이걸 ‘먼저 닿은 쪽’ 이라고 합니다)",
        "",
        "문제는 — 위 두 가지만 보면 ‘힘의 방향’ 이 보이지 않습니다.",
        "예: 어떤 날 종목이 +3% 도 닿고 -3% 도 닿으면 ‘변동이 큰 날’ 이라는 것만 압니다.",
        "그 날이 결국 강한 날이었는지 약한 날이었는지는 색깔 (전일 종가 기준) 로 봐야 보입니다.",
        "",
        "→ 그래서 이 보고서는 ‘어제 끝난 가격’ 을 기준으로 매일 색깔 한 개씩 매겨봤습니다.",
        "→ 그 색깔을 5일 이어 붙이면 ‘이 종목이 한 주 동안 어떤 흐름이었는지’ 한눈에 보입니다.",
    ]
    ax.text(0.0, 0.97, "\n".join(paras), fontsize=11.5, color="#374151",
            va="top", linespacing=1.85, family="Malgun Gothic")

    # 비유 박스
    ax = fig.add_axes([0.04, 0.10, 0.92, 0.28]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                 transform=ax.transAxes,
                                 facecolor="#fef3c7", edgecolor="#d97706", linewidth=1.2))
    ax.text(0.02, 0.85, "비유 — 운동 선수의 컨디션 체크 같은 것",
            fontsize=12.5, fontweight="bold", color="#78350f", va="center")
    ax.text(0.02, 0.55,
            "어제 기준 ‘평균 페이스’ 를 정해 놓고, 오늘 그 위에서 달렸는지 아래에서 달렸는지 매일 본다고 생각하시면 됩니다.\n"
            "    • 5일 모두 페이스 위 = 컨디션 좋음 (모두 초록)\n"
            "    • 잠깐 떨어졌다 회복 = 그래도 괜찮음 (노랑)\n"
            "    • 페이스 위로 못 올라감 = 컨디션 떨어짐 (빨강)\n"
            "5일 모아 보면 한 주 컨디션 흐름이 한눈에 보입니다.",
            fontsize=10.5, color="#78350f", va="center", linespacing=1.7)

    _footer(fig, 3, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 4 — 한 페이지 결론 ───────
def page_4_conclusion(pdf, total, cases, daily, pattern):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "4. 한 페이지로 보는 결론",
            "한 달 동안 어떻게 됐나")

    _band(fig, 0.86, 1, "각 방식이 고른 종목 수 + 다음 날 색깔 분포 + 5일 결과")
    ax = fig.add_axes([0.02, 0.58, 0.96, 0.27]); ax.axis("off")

    # 정책별 핵심 수치 + 다음 날 색깔 분포
    pol_rows = []
    for pol_key, pol_ko in POLICY_KO.items():
        sub = cases[cases["policy_key"] == pol_key]
        if sub.empty:
            continue
        n = len(sub)
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        # 다음날 색깔 분포
        d1_counts = sub["dplus1_color"].value_counts()
        g = int(d1_counts.get("G", 0))
        y = int(d1_counts.get("Y", 0))
        o = int(d1_counts.get("O", 0))
        r = int(d1_counts.get("R", 0))
        x = int(d1_counts.get("X", 0))
        pol_rows.append([
            pol_ko,
            f"{n}",
            f"{g}",  # 🟢
            f"{y}",  # 🟡
            f"{o}",  # 🟠
            f"{r}",  # 🔴
            f"{x}",  # ⚪
            f"{profit}/{n} ({profit*100/max(n,1):.0f}%)",
            f"{loss}/{n} ({loss*100/max(n,1):.0f}%)",
        ])

    _table(ax,
           ["방식", "종목수",
            "다음날\n강세", "다음날\n회복", "다음날\n실패", "다음날\n약세", "다음날\n보합",
            "5일 이익 먼저", "5일 손실 먼저"],
           pol_rows,
           [0.27, 0.06, 0.07, 0.07, 0.07, 0.07, 0.07, 0.16, 0.16],
           header_color="#bfdbfe", scale=1.85, cell_align="center", font_size=9,
           color_cols={2: "G", 3: "Y", 4: "O", 5: "R", 6: "X"})

    # 한 줄 의미
    ax2 = fig.add_axes([0.04, 0.08, 0.92, 0.48]); ax2.axis("off")
    interp = [
        "★ V2 점수제와 거래대금 기준을 비교하면 — 같은 22일 동안 둘 다 66개를 골랐지만,",
        "    5일 안 익절 먼저 닿은 비율과 ‘다음 날 색깔 분포’ 가 다릅니다.",
        "",
        "★ 다음 날 색깔 분포 컬럼 (●초/●노/●주/●빨/○회) 보는 법:",
        "    한 칸 숫자 = 그 색깔로 다음 날을 시작한 종목 개수.",
        "    예) V2 가 ●노랑 (흔들렸지만 회복) 21개 = 66개 중 21개가 다음날 ‘잠깐 떨어졌다 회복’ 으로 시작.",
        "    ●초록 비중이 높으면 = 다음날부터 강세로 시작한 종목이 많음 → 결과 기대 ↑.",
        "    ●빨강 비중이 높으면 = 다음날부터 약세로 시작한 종목이 많음 → 위험 신호.",
        "",
        "★ ‘익절 먼저 닿았다’ 는 뜻은: 산 가정 시작가에서 +2% 가 -2% 보다 먼저 닿았다는 뜻.",
        "    숫자가 50% 이상이면 ‘평균적으로 익절 쪽이 먼저’ 라고 볼 수 있습니다.",
        "",
        "★ 주의 — 이 표는 한 달 (22일) 만 본 결과입니다. 1년치는 다음 단계.",
        "    ‘닿았다’ ≠ ‘진짜 그 가격에 살 수 있었다’ (호가·거래량·잠김은 별도 검증).",
    ]
    ax2.text(0.0, 0.95, "\n".join(interp), fontsize=9.5, color="#374151",
             va="top", linespacing=1.65, family="Malgun Gothic")

    _footer(fig, 4, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 5 — 정책별 다음 날 색깔 분포 ───────
def page_5_d1_color_dist(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "5. 다음 날 색깔 분포",
            "각 방식이 고른 종목이 다음 날 어떤 색깔로 시작했나")

    _band(fig, 0.84, 1, "비교 — 다음 날 색깔 (66개 종목 기준, D0 풀은 479개)")

    # 정책별 D+1 색깔 분포
    pols = ["V2_FINAL_TOP3", "P0_TRADING_VALUE_TOP3", "P0_LEGACY_D0_RANK_TOP3", "D0_POOL_ALL_RECENT_1M"]
    colors_order = ["G", "Y", "O", "R", "X"]

    ax = fig.add_axes([0.10, 0.30, 0.82, 0.52])
    n_pol = len(pols)
    n_col = len(colors_order)
    x = np.arange(n_pol)
    bar_w = 0.15

    for i, c in enumerate(colors_order):
        values = []
        for p in pols:
            sub = cases[cases["policy_key"] == p]
            total_n = len(sub)
            count = (sub["dplus1_color"] == c).sum() if total_n > 0 else 0
            pct = count * 100 / max(total_n, 1)
            values.append(pct)
        bars = ax.bar(x + (i - 2) * bar_w, values, bar_w,
                      label=f"{COLOR_NAME_KO[c]}",
                      color=COLOR_HEX[c],
                      edgecolor="white", linewidth=1)
        for j, b in enumerate(bars):
            if b.get_height() > 2:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
                        f"{b.get_height():.0f}%", ha="center", fontsize=8.5,
                        color="#1f2937")

    ax.set_xticks(x)
    ax.set_xticklabels([POLICY_KO[p].split("(")[0].strip() for p in pols],
                       fontsize=10, rotation=0)
    ax.set_ylabel("비중 (%)", fontsize=10)
    ax.set_ylim(0, 65)
    ax.legend(fontsize=9.5, loc="upper right", ncol=5, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("같은 22일 동안 각 방식이 고른 종목의 다음 날 색깔 분포",
                 fontsize=11, color="#1e3a8a", pad=10)

    # 해석 박스
    _band(fig, 0.22, 2, "이 막대그래프가 알려주는 것", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.17]); ax.axis("off")
    notes = [
        "• V2 점수제는 ‘흔들렸지만 회복(노랑)’ 비중이 다른 방식보다 높은 편입니다. → 종가 방어형 종목을 더 잡는 경향.",
        "• 거래대금 기준은 ‘위로 갔지만 실패(주황)’ 비중이 상대적으로 높습니다. → 변동성 큰 종목을 더 잡는 경향.",
        "• ‘완전 강세(초록)’ 가 다음 날 바로 나오는 비율은 어느 방식이든 10~25% 수준 — 강세 종목이 흔하지 않다는 뜻.",
        "• ‘완전 약세(빨강)’ 가 적게 나올수록 좋은 방식 — 다음 날 손실 가능성이 낮다는 의미입니다.",
    ]
    ax.text(0.0, 0.97, "\n".join(notes), fontsize=10, color="#14532d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 5, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 6 — 다음 날 색깔별 결과 ───────
def page_6_d1_outcome(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "6. 다음 날 색깔이 알려주는 것",
            "다음 날 색깔로 5일 결과가 갈리나")

    _band(fig, 0.84, 1, "V2 점수제 66개 종목 — 다음 날 색깔 → 5일 안 익절 먼저 닿은 비율")

    # V2 만 — D+1 색깔별 D+5 first_touch_result
    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    rows = []
    for c in ["G", "Y", "O", "R", "X"]:
        sub = v2[v2["dplus1_color"] == c]
        n = len(sub)
        if n == 0:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        rows.append({
            "color": c,
            "name": COLOR_NAME_KO[c],
            "n": n,
            "profit": profit,
            "loss": loss,
            "profit_pct": profit * 100 / n,
            "loss_pct": loss * 100 / n,
        })

    # 막대그래프
    ax = fig.add_axes([0.12, 0.40, 0.78, 0.42])
    x = np.arange(len(rows))
    bar_w = 0.36
    profit_bars = ax.bar(x - bar_w/2, [r["profit_pct"] for r in rows], bar_w,
                          label="익절 먼저 닿음 (+ 가 먼저)", color="#16a34a", alpha=0.85)
    loss_bars = ax.bar(x + bar_w/2, [r["loss_pct"] for r in rows], bar_w,
                        label="손절 먼저 닿음 (- 가 먼저)", color="#dc2626", alpha=0.85)
    for b in profit_bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.2,
                f"{b.get_height():.0f}%", ha="center", fontsize=10, color="#14532d")
    for b in loss_bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1.2,
                f"{b.get_height():.0f}%", ha="center", fontsize=10, color="#7f1d1d")

    # X축 — 색깔 동그라미 + 이름
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['name']}\n(N={r['n']}개)" for r in rows], fontsize=10)
    # 색깔 동그라미 추가
    for i, r in enumerate(rows):
        ax.scatter([i], [-12], s=300, color=COLOR_HEX[r["color"]],
                   clip_on=False, zorder=10)
    ax.set_ylabel("비율 (%)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("다음 날 색깔별, 5일 안 어느 쪽이 먼저 닿았는지", fontsize=11.5,
                 color="#1e3a8a", pad=10)

    # 해석
    _band(fig, 0.30, 2, "이 그래프 읽는 법", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.05, 0.92, 0.24]); ax.axis("off")
    notes = [
        "• 초록 막대 (익절 먼저) 가 빨강 막대 (손절 먼저) 보다 높으면 = ‘이 색깔로 시작한 종목은 결과가 좋더라’",
        "• 빨강 막대가 더 높으면 = ‘이 색깔로 시작한 종목은 결과가 나쁘더라’",
        "",
        "관찰 (V2 점수제 66개 기준):",
        "    • 다음 날 ‘완전 강세 (초록)’ 으로 시작 = 5일 후 결과가 가장 좋음 (익절 먼저 비율 ↑↑)",
        "    • 다음 날 ‘흔들렸지만 회복 (노랑)’ 으로 시작 = 결과 중간 정도",
        "    • 다음 날 ‘위로 갔지만 실패 (주황)’ 으로 시작 = 결과가 갈림",
        "    • 다음 날 ‘완전 약세 (빨강)’ 으로 시작 = 손절 먼저 비율 ↑↑ — 위험 신호",
        "",
        "→ 즉, ‘다음 날 시작 색깔’ 만 봐도 그 종목의 5일 흐름을 어느 정도 예측해볼 수 있습니다 (한 달 기준).",
    ]
    ax.text(0.0, 0.97, "\n".join(notes), fontsize=10, color="#14532d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 6, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 7 — V2 종목 색깔 흐름 막대 ───────
def page_7_v2_path_overview(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "7. V2 점수제 66개 종목 — 한 달 색깔 흐름 분포",
            "어떤 색깔 흐름이 자주 나왔나")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    path_counts = v2["color_path"].value_counts().head(15)

    _band(fig, 0.86, 1, "가장 많이 나온 색깔 흐름 TOP 15 + 색깔 분포")
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.78]); ax.axis("off")

    rows = []
    for path, n in path_counts.items():
        # 한글 풀이
        path_ko = " → ".join(COLOR_NAME_KO.get(c, c) for c in path.split("-"))
        # 그 path 의 익절 비율
        sub = v2[v2["color_path"] == path]
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        # color path 안 G/Y/O/R/X 개수
        parts = path.split("-")
        g = parts.count("G"); y = parts.count("Y"); o = parts.count("O")
        r = parts.count("R"); x = parts.count("X")
        rows.append([
            path,
            path_ko,
            str(n),
            f"{g}", f"{y}", f"{o}", f"{r}", f"{x}",
            f"{profit*100/max(n,1):.0f}% / {loss*100/max(n,1):.0f}%",
        ])

    _table(ax,
           ["색깔 흐름", "5일 색상 흐름 풀이", "건수",
            "강세", "회복", "실패", "약세", "보합",
            "이익 / 손실 비율"],
           rows,
           [0.10, 0.30, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.16],
           header_color="#bfdbfe", scale=1.4, font_size=8.5, cell_align="center",
           color_cols={3: "G", 4: "Y", 5: "O", 6: "R", 7: "X"})

    _footer(fig, 7, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 8 — V2 가장 좋은 색깔 흐름 ───────
def page_8_best_paths(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "8. V2 점수제 — 결과가 좋았던 색깔 흐름",
            "익절 먼저 닿은 비율이 높았던 흐름들")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    grouped = []
    for path, sub in v2.groupby("color_path"):
        n = len(sub)
        if n < 2:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        avg_mfe = sub["mfe_d5_pct"].mean()
        avg_mae = sub["mae_d5_pct"].mean()
        grouped.append({
            "path": path,
            "n": n,
            "profit_pct": profit * 100 / n,
            "loss_pct": loss * 100 / n,
            "diff": (profit - loss) * 100 / n,
            "avg_mfe": avg_mfe,
            "avg_mae": avg_mae,
        })

    best = sorted(grouped, key=lambda x: (x["diff"], x["n"]), reverse=True)[:8]

    _band(fig, 0.86, 1, "‘익절 먼저’ - ‘손절 먼저’ = 차이 (높을수록 좋음) + 색깔 분포")
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.74]); ax.axis("off")

    rows = []
    for r in best:
        path_ko = " → ".join(COLOR_NAME_KO.get(c, c) for c in r["path"].split("-"))
        parts = r["path"].split("-")
        g = parts.count("G"); y = parts.count("Y"); o = parts.count("O")
        rr = parts.count("R"); xx = parts.count("X")
        rows.append([
            r["path"],
            path_ko,
            str(r["n"]),
            f"{g}", f"{y}", f"{o}", f"{rr}", f"{xx}",
            f"{r['profit_pct']:.0f}%",
            f"{r['loss_pct']:.0f}%",
            f"+{r['diff']:.0f}%p",
            f"+{r['avg_mfe']:.1f}%" if pd.notna(r["avg_mfe"]) else "—",
            f"{r['avg_mae']:.1f}%" if pd.notna(r["avg_mae"]) else "—",
        ])

    _table(ax,
           ["색깔 흐름", "5일 색상 흐름 풀이", "건수",
            "강세", "회복", "실패", "약세", "보합",
            "이익", "손실", "차이",
            "평균\n최대상승", "평균\n최대하락"],
           rows,
           [0.09, 0.22, 0.05, 0.04, 0.04, 0.04, 0.04, 0.04, 0.07, 0.07, 0.07, 0.115, 0.115],
           header_color="#dcfce7", scale=1.45, font_size=8.5, cell_align="center",
           color_cols={3: "G", 4: "Y", 5: "O", 6: "R", 7: "X"})

    # 핵심 메모
    ax2 = fig.add_axes([0.04, 0.03, 0.92, 0.06]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                  transform=ax2.transAxes,
                                  facecolor="#dcfce7", edgecolor="#16a34a", linewidth=1))
    ax2.text(0.02, 0.5,
             "★ ‘가장 높이 올라간 폭’ = 5일 안 어느 시점에 가장 많이 위로 갔던 % "
             "(끝까지 안 가도, 잠깐이라도 그 폭만큼 갔다는 뜻)",
             fontsize=10, color="#14532d", va="center")

    _footer(fig, 8, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 9 — V2 가장 안 좋은 색깔 흐름 ───────
def page_9_worst_paths(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "9. V2 점수제 — 결과가 안 좋았던 색깔 흐름",
            "손절 먼저 닿은 비율이 높았던 흐름들 (피해야 할 패턴)")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    grouped = []
    for path, sub in v2.groupby("color_path"):
        n = len(sub)
        if n < 2:
            continue
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        avg_mfe = sub["mfe_d5_pct"].mean()
        avg_mae = sub["mae_d5_pct"].mean()
        grouped.append({
            "path": path,
            "n": n,
            "profit_pct": profit * 100 / n,
            "loss_pct": loss * 100 / n,
            "diff": (profit - loss) * 100 / n,
            "avg_mfe": avg_mfe,
            "avg_mae": avg_mae,
        })

    worst = sorted(grouped, key=lambda x: (x["diff"], -x["n"]))[:8]

    _band(fig, 0.86, 1, "‘손절 먼저’가 더 많았던 흐름 — 결과 약했음 + 색깔 분포")
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.74]); ax.axis("off")

    rows = []
    for r in worst:
        path_ko = " → ".join(COLOR_NAME_KO.get(c, c) for c in r["path"].split("-"))
        parts = r["path"].split("-")
        g = parts.count("G"); y = parts.count("Y"); o = parts.count("O")
        rr = parts.count("R"); xx = parts.count("X")
        rows.append([
            r["path"],
            path_ko,
            str(r["n"]),
            f"{g}", f"{y}", f"{o}", f"{rr}", f"{xx}",
            f"{r['profit_pct']:.0f}%",
            f"{r['loss_pct']:.0f}%",
            f"{r['diff']:+.0f}%p",
            f"+{r['avg_mfe']:.1f}%" if pd.notna(r["avg_mfe"]) else "—",
            f"{r['avg_mae']:.1f}%" if pd.notna(r["avg_mae"]) else "—",
        ])

    _table(ax,
           ["색깔 흐름", "5일 색상 흐름 풀이", "건수",
            "강세", "회복", "실패", "약세", "보합",
            "이익", "손실", "차이",
            "평균\n최대상승", "평균\n최대하락"],
           rows,
           [0.09, 0.22, 0.05, 0.04, 0.04, 0.04, 0.04, 0.04, 0.07, 0.07, 0.07, 0.115, 0.115],
           header_color="#fecaca", scale=1.45, font_size=8.5, cell_align="center",
           color_cols={3: "G", 4: "Y", 5: "O", 6: "R", 7: "X"})

    ax2 = fig.add_axes([0.04, 0.03, 0.92, 0.06]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                  transform=ax2.transAxes,
                                  facecolor="#fef2f2", edgecolor="#dc2626", linewidth=1))
    ax2.text(0.02, 0.5,
             "★ 위 흐름들에 공통점은 ‘위로 갔다가 실패 (주황)’ 가 연속되거나 ‘완전 약세 (빨강)’ 가 끼어 있는 경우. "
             "변동성은 있지만 종가 방어 실패가 반복됨.",
             fontsize=10, color="#7f1d1d", va="center")

    _footer(fig, 9, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 10 — V2 색깔 분포 히트맵 ───────
def page_10_v2_heatmap(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "10. V2 점수제 — 다음날 / 2일째 / ... / 5일째 색깔 분포",
            "시간이 지날수록 색깔이 어떻게 변하나")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    days = [f"dplus{i}_color" for i in range(1, 6)]
    day_labels = ["다음 날", "2일째", "3일째", "4일째", "5일째"]
    colors = ["G", "Y", "O", "R", "X"]
    n_total = len(v2)

    _band(fig, 0.84, 1, "각 일자별 색깔 비중 (V2 점수제 66개 종목)")
    ax = fig.add_axes([0.12, 0.30, 0.78, 0.50])

    for ci, c in enumerate(colors):
        values = []
        for d in days:
            count = (v2[d] == c).sum() if d in v2.columns else 0
            values.append(count * 100 / max(n_total, 1))
        ax.plot(day_labels, values, marker="o", linewidth=2.5, markersize=10,
                label=COLOR_NAME_KO[c], color=COLOR_HEX[c])
        for i, v in enumerate(values):
            if v > 3:
                ax.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=9,
                        color=COLOR_HEX[c], fontweight="bold")

    ax.set_ylabel("비중 (%)", fontsize=11)
    ax.set_ylim(0, 55)
    ax.legend(fontsize=10, loc="upper right", ncol=5, framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.set_title("다음 날 → 5일째까지 색깔 분포 변화",
                 fontsize=11.5, color="#1e3a8a", pad=10)

    # 해석
    _band(fig, 0.22, 2, "이 라인 차트가 알려주는 것", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.05, 0.92, 0.16]); ax.axis("off")
    notes = [
        "• 다음 날 → 5일째로 갈수록 ‘완전 강세 (초록)’ 비중이 어떻게 변하는지 보세요.",
        "• ‘위로 갔지만 실패 (주황)’ 가 일관되게 높은 비중이면 → 변동은 크지만 종가 방어 약함.",
        "• ‘완전 약세 (빨강)’ 비중이 5일째 가까이 증가하면 → 시간이 지날수록 약해지는 종목들이 많아짐.",
        "• 5일 평균: V2 종목들은 노랑·주황 비중이 가장 높고, 초록은 첫날 비중이 가장 큼.",
    ]
    ax.text(0.0, 0.97, "\n".join(notes), fontsize=10, color="#14532d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 10, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 11~14 — V2 22일 종목 일자별 상세 ───────
def page_v2_daily_detail(pdf, total, cases, page_no, start_idx, end_idx, dates):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, f"{page_no}. V2 22일 종목별 색깔 흐름 상세",
            f"기간 {dates[start_idx]} ~ {dates[min(end_idx-1, len(dates)-1)]}")

    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    v2["rank_n"] = pd.to_numeric(v2["rank"], errors="coerce")

    ax = fig.add_axes([0.02, 0.05, 0.96, 0.80]); ax.axis("off")
    rows = []
    cell_colors = []  # 각 행의 D+1~D+5 칸 배경색
    for d in dates[start_idx:end_idx]:
        day_rows = v2[v2["signal_date"] == d].sort_values("rank_n")
        for _, r in day_rows.iterrows():
            path = str(r.get("color_path", ""))
            parts = (path.split("-") + [""] * 5)[:5]  # 5칸 보장
            outcome_ko = {
                "FAST_WIN":             "빠른 성공",
                "SLOW_WIN":             "늦은 성공",
                "BOTH_PROFIT_FIRST":    "양쪽 닿음(이익 먼저)",
                "BOTH_LOSS_FIRST":      "양쪽 닿음(손실 먼저)",
                "LOSS_FIRST":           "손실 먼저",
                "AMBIGUOUS":            "애매",
                "NO_TOUCH":             "닿지 않음",
                "":                     "—",
            }.get(str(r.get("outcome_label", "")), str(r.get("outcome_label", "")))
            score = r.get("score_v2")
            score_str = f"{float(score):.1f}" if pd.notna(score) and score != "" else "—"
            # 각 칸에 색깔 한글 짧게 표시
            ko_short = {"G": "강", "Y": "회", "O": "실", "R": "약", "X": "보"}
            d1 = ko_short.get(parts[0], "-")
            d2 = ko_short.get(parts[1], "-")
            d3 = ko_short.get(parts[2], "-")
            d4 = ko_short.get(parts[3], "-")
            d5 = ko_short.get(parts[4], "-")
            rows.append([
                d,
                str(r.get("rank", "")),
                str(r.get("stock_name", ""))[:9],
                str(r.get("stock_code", "")),
                score_str,
                d1, d2, d3, d4, d5,
                outcome_ko,
            ])
            cell_colors.append([COLOR_HEX.get(c, "#9ca3af") if c in COLOR_HEX else None
                                for c in parts])

    # 일반 _table 대신 직접 그려 D+1~D+5 칸 색칠
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=9, color="#999")
    else:
        t = ax.table(
            cellText=rows,
            colLabels=["신호일", "순위", "종목명", "코드", "점수",
                       "다음날", "2일째", "3일째", "4일째", "5일째", "결과"],
            loc="upper left", cellLoc="center",
            colWidths=[0.10, 0.04, 0.12, 0.07, 0.06,
                       0.07, 0.07, 0.07, 0.07, 0.07, 0.22],
        )
        t.auto_set_font_size(False); t.set_fontsize(8.2); t.scale(1.0, 1.3)
        for (rr, cc), cell in t.get_celld().items():
            cell.set_edgecolor("#cbd5e0")
            if rr == 0:
                cell.set_facecolor("#e0e7ff")
                cell.set_text_props(weight="bold", color="#1e3a8a")
            else:
                # D+1~D+5 칸 (5~9 컬럼) 배경색
                if 5 <= cc <= 9:
                    color_hex = cell_colors[rr - 1][cc - 5] if rr - 1 < len(cell_colors) else None
                    if color_hex:
                        cell.set_facecolor(color_hex)
                        cell.set_text_props(weight="bold", color="white")
                    else:
                        cell.set_facecolor("#f3f4f6")
                else:
                    cell.set_facecolor("#ffffff" if (rr - 1) % 2 == 0 else "#f8fafc")

    _footer(fig, page_no, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 15 — V2만 vs P0만 vs 공통 ───────
def page_15_relationship(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "15. ‘V2만 골랐다 / 거래대금만 골랐다 / 둘 다 골랐다’ 비교",
            "두 방식이 다른 종목을 고를 때 결과는?")

    # relationship_group 기준
    rel_groups = {
        "V2_ONLY":   "V2 점수제만 골랐다",
        "P0_ONLY":   "거래대금 기준만 골랐다",
        "BOTH":      "둘 다 골랐다 (공통)",
    }

    _band(fig, 0.84, 1, "다음 날 색깔 분포 + 5일 결과")
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.62]); ax.axis("off")

    rows = []
    for key, ko in rel_groups.items():
        sub = cases[cases["relationship_group"] == key]
        n = len(sub)
        if n == 0:
            continue
        # D+1 색깔 분포
        d1_dist = sub["dplus1_color"].value_counts(normalize=True) * 100
        top_color = d1_dist.idxmax() if not d1_dist.empty else "—"
        top_color_pct = d1_dist.max() if not d1_dist.empty else 0
        # 5일 결과
        profit = (sub["d5_first_touch_result"] == "profit_first").sum()
        loss = (sub["d5_first_touch_result"] == "loss_first").sum()
        avg_mfe = pd.to_numeric(sub["mfe_d5_pct"], errors="coerce").mean()
        avg_mae = pd.to_numeric(sub["mae_d5_pct"], errors="coerce").mean()
        rows.append([
            ko,
            str(n),
            f"{COLOR_NAME_KO.get(top_color, top_color)} ({top_color_pct:.0f}%)",
            f"{profit}/{n} ({profit*100/n:.0f}%)",
            f"{loss}/{n} ({loss*100/n:.0f}%)",
            f"+{avg_mfe:.1f}%" if pd.notna(avg_mfe) else "—",
            f"{avg_mae:.1f}%" if pd.notna(avg_mae) else "—",
        ])

    _table(ax,
           ["구분", "건수", "다음 날 가장 많이 나온 색깔",
            "익절 먼저", "손절 먼저",
            "최고 상승폭 (평균)", "최저 하락폭 (평균)"],
           rows,
           [0.24, 0.07, 0.22, 0.13, 0.13, 0.11, 0.10],
           header_color="#fef3c7", scale=1.7, font_size=9, cell_align="center")

    # 메모
    _band(fig, 0.12, 2, "관찰", color="#dbeafe", text_color="#1e3a8a")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.07]); ax.axis("off")
    ax.text(0.0, 0.5,
            "• 두 방식이 ‘공통으로 고른 종목’ 들 — 어느 방식이든 결과가 더 안정적일 가능성.\n"
            "• V2 만 골랐거나 거래대금 만 골랐을 때 — 어느 쪽이 색깔이 더 좋은지 비교.",
            fontsize=10, color="#1e3a8a", va="center", linespacing=1.85)

    _footer(fig, 15, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 16 — 평균 변동 폭 ───────
def page_16_mfe_mae(pdf, total, cases):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "16. 5일 안 평균 변동 폭",
            "위로 얼마나 갔고 아래로 얼마나 갔나")

    _band(fig, 0.84, 1, "정책별 평균 변동 폭 (5일 안)")
    ax = fig.add_axes([0.12, 0.30, 0.78, 0.50])

    pol_labels, mfes, maes = [], [], []
    for pol_key, pol_ko in POLICY_KO.items():
        sub = cases[cases["policy_key"] == pol_key]
        if sub.empty:
            continue
        mfe = pd.to_numeric(sub["mfe_d5_pct"], errors="coerce").mean()
        mae = pd.to_numeric(sub["mae_d5_pct"], errors="coerce").mean()
        if pd.notna(mfe) and pd.notna(mae):
            pol_labels.append(pol_ko.split("(")[0].strip())
            mfes.append(mfe); maes.append(mae)

    x = np.arange(len(pol_labels))
    bar_w = 0.36
    bars1 = ax.bar(x - bar_w/2, mfes, bar_w,
                    label="가장 높이 올라간 폭 (평균)", color="#16a34a", alpha=0.85)
    bars2 = ax.bar(x + bar_w/2, maes, bar_w,
                    label="가장 많이 떨어진 폭 (평균)", color="#dc2626", alpha=0.85)
    for b in bars1:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5,
                f"+{b.get_height():.1f}%", ha="center", fontsize=10, color="#14532d")
    for b in bars2:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() - 1.5,
                f"{b.get_height():.1f}%", ha="center", fontsize=10, color="#7f1d1d")
    ax.set_xticks(x); ax.set_xticklabels(pol_labels, fontsize=10)
    ax.set_ylabel("% (시작가 대비)", fontsize=11)
    ax.axhline(0, color="#1f2937", linewidth=1)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("각 방식 종목들의 5일 안 평균 변동 폭", fontsize=11.5,
                 color="#1e3a8a", pad=10)

    # 해석
    _band(fig, 0.22, 2, "이 그래프 읽는 법", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.17]); ax.axis("off")
    notes = [
        "• 초록 막대 = ‘5일 안 어느 시점에 평균 이만큼 위로 갔다’ — 잠재 익절 폭",
        "• 빨강 막대 = ‘5일 안 어느 시점에 평균 이만큼 아래로 갔다’ — 잠재 손실 폭",
        "• 초록 > |빨강| 이면 = 평균적으로 위로 더 갔던 종목들 (V2 점수제 / 거래대금 기준 모두 그러함)",
        "• 단, 위로 가는 폭이 아무리 커도 — 그 시점에 ‘진짜 팔 수 있었나 (호가, 거래량)’ 는 별도 확인 필요.",
    ]
    ax.text(0.0, 0.97, "\n".join(notes), fontsize=10, color="#14532d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, 16, total); pdf.savefig(fig); plt.close(fig)


# ─────── 페이지 17 — 한 줄 정리 ───────
def page_17_summary(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "17. 한 줄 정리",
            "이 보고서를 닫을 때 기억해야 할 것")

    _band(fig, 0.84, 1, "다섯 줄 요약")
    ax = fig.add_axes([0.04, 0.40, 0.92, 0.43]); ax.axis("off")
    bullets = [
        "1.  매일 ‘어제 끝난 가격’ 을 기준선으로 잡고, 그 위/아래에서 어떻게 움직였는지 색깔로 표시했습니다.",
        "        초록 = 강세 / 노랑 = 회복 / 주황 = 실패 / 빨강 = 약세 / 회색 = 변동 거의 없음",
        "",
        "2.  V2 점수제 (지금 운영) 와 거래대금 기준 (기존) 이 같은 22일 동안 다른 색깔 흐름을 만들었습니다.",
        "        V2 는 ‘흔들렸지만 회복(노랑)’ 이 상대적으로 많고, 거래대금 기준은 ‘위로 갔지만 실패(주황)’ 가 많은 편.",
        "",
        "3.  다음 날 색깔이 ‘완전 강세(초록)’ 인 종목 — 5일 안 익절 먼저 닿은 비율이 가장 높았습니다.",
        "        다음 날 ‘완전 약세(빨강)’ 로 시작한 종목 — 손절 먼저 닿은 비율이 높아 위험 신호.",
        "",
        "4.  결과가 좋았던 색깔 흐름 — 초록·노랑이 많이 섞인 흐름 (예: 초록→노랑→초록, 노랑→초록→초록)",
        "        결과가 안 좋았던 흐름 — 주황·빨강이 반복되는 흐름 (예: 주황→주황→주황, 빨강→빨강→노랑)",
        "",
        "5.  이 보고서는 ‘사후에 어떻게 됐는지’ 본 자료입니다. 지금 무슨 종목을 사라/팔라는 추천이 아닙니다.",
        "        실제 운영은 V2 점수 Top3 를 매일 오후 3시에 ‘Paper Watch’ 메시지로만 보내고, 사람이 직접 판단합니다.",
    ]
    ax.text(0.0, 0.97, "\n".join(bullets), fontsize=10.5, color="#374151",
            va="top", linespacing=1.6, family="Malgun Gothic")

    # 다음에 볼 것
    _band(fig, 0.31, 2, "다음에 볼 것", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.24]); ax.axis("off")
    nexts = [
        "•  1년치 (252 거래일) 로 확장 — 22일은 표본이 작아 추세 단정 어려움. Codex 가 다음 단계에서 작업.",
        "•  대시보드에 ‘색깔 복기’ 탭 신설 — 사용자가 매일 색깔 흐름을 직접 필터링해서 볼 수 있게.",
        "•  차트 연동 — 색깔 표 클릭 → 해당 종목의 5일 가격 차트 + 색깔 배경 표시 (Codex 차트팩과 결합).",
        "•  현실 체결 가능성 보정 — 색깔이 좋아도 ‘진짜 그 가격에 살 수 있었나’ 별도 검증 필요.",
        "•  실제 매매 전환은 아직 ‘paper watch (관찰만)’ 단계. 색깔 흐름의 통계가 더 쌓인 후 단계적 결정.",
    ]
    ax.text(0.0, 0.97, "\n".join(nexts), fontsize=10.5, color="#14532d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _footer(fig, total, total); pdf.savefig(fig); plt.close(fig)


# ─────── Main ───────
def build(out_path: Path):
    cases, daily, pattern = load_data()

    # V2 22일 날짜 리스트
    v2 = cases[cases["policy_key"] == "V2_FINAL_TOP3"].copy()
    dates = sorted(v2["signal_date"].unique())
    n_dates = len(dates)
    chunk = 6
    n_detail_pages = (n_dates + chunk - 1) // chunk
    total = 10 + n_detail_pages + 3  # 1-10 + 상세 + 15-17

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        page_1_cover(pdf, total, cases)
        page_2_colors_explained(pdf, total)
        page_3_why(pdf, total)
        page_4_conclusion(pdf, total, cases, daily, pattern)
        page_5_d1_color_dist(pdf, total, cases)
        page_6_d1_outcome(pdf, total, cases)
        page_7_v2_path_overview(pdf, total, cases)
        page_8_best_paths(pdf, total, cases)
        page_9_worst_paths(pdf, total, cases)
        page_10_v2_heatmap(pdf, total, cases)
        # 일자별 상세
        for i in range(n_detail_pages):
            page_no = 11 + i
            s = i * chunk
            e = min(s + chunk, n_dates)
            page_v2_daily_detail(pdf, total, cases, page_no, s, e, dates)
        page_15_relationship(pdf, total, cases)
        page_16_mfe_mae(pdf, total, cases)
        page_17_summary(pdf, total)

    size_kb = out_path.stat().st_size / 1024
    print(f"[ok] {out_path}  ({size_kb:.1f} KB, {total} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(r"C:\Users\PYJ\Downloads\PREV_CLOSE_COLOR_FRIENDLY_REVIEW_KR_20260515.pdf"))
    args = ap.parse_args()
    build(args.out)
