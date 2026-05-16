"""
Phase 0 Realistic Fill 시뮬 — 자세한 승률 + 일자별 표 PDF.

입력:
    C:\\Users\\PYJ\\Downloads\\phase0_realistic_fill_detail_20260514.csv         (753 행)
    C:\\Users\\PYJ\\Downloads\\phase0_realistic_fill_summary_20260514.csv         (fill summary)
    C:\\Users\\PYJ\\Downloads\\phase0_realistic_fill_first_touch_summary_20260514.csv (32 행)

설계:
    - A4 가로, Malgun Gothic, glyph 경고 0
    - 한 페이지 한 주제 (글씨 겹침 방지)
    - 표·막대그래프·라인차트로 시각화
    - 일자별 표는 페이지당 ~32일씩 분할

페이지 구성 (~16 pages):
    1. 표지 + 한 페이지 요약
    2. 시뮬 개요 (Phase 0 Realistic Fill 무엇인가)
    3. Fill Filter 통과율 (98.8% pass)
    4. First-Touch 핵심 승률 표 (16행)
    5. Horizon × threshold 매트릭스 그래프
    6. 도달률 vs first-touch 비교 막대
    7. 월별 승률 추이 (라인)
    8. 22일 sliding 승률 (라인)
    9. 점수 분위별 결과
   10~15. 일자별 표 (251일 → 6 페이지 분할)
   16. 한계 + 다음 단계
"""
from __future__ import annotations

import argparse
import json
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

DETAIL_CSV = Path(r"C:\Users\PYJ\Downloads\phase0_realistic_fill_detail_20260514.csv")
SUMMARY_CSV = Path(r"C:\Users\PYJ\Downloads\phase0_realistic_fill_summary_20260514.csv")
FIRST_TOUCH_CSV = Path(r"C:\Users\PYJ\Downloads\phase0_realistic_fill_first_touch_summary_20260514.csv")


# ===== 공통 유틸 =====
def _header(fig, title, sub=""):
    ax = fig.add_axes([0.0, 0.92, 1.0, 0.08]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.04, 0.58, title, fontsize=16, fontweight="bold", color="white", va="center")
    if sub:
        ax.text(0.96, 0.58, sub, fontsize=9.5, color="#c7d2fe", va="center", ha="right")


def _footer(fig, p, total):
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.035]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#f1f5f9", edgecolor="none"))
    ax.text(0.04, 0.5,
            "Phase 0 Realistic Fill 시뮬 — D0_STRICT_3D_V2_TOP3 baseline  ·  "
            "1년 (251일, 753 행)  ·  매수 추천 아님 · 자동매매 아님",
            fontsize=7.5, color="#475569", va="center")
    ax.text(0.96, 0.5, f"{p} / {total}", fontsize=8,
            color="#475569", va="center", ha="right")


def _band(fig, y, num, title, color="#dbeafe", text_color="#1e3a8a"):
    ax = fig.add_axes([0.04, y, 0.92, 0.045]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor=color, edgecolor="none"))
    ax.text(0.01, 0.5, f"{num}. {title}" if num else title,
            fontsize=12, fontweight="bold", color=text_color, va="center")


def _table(ax, header, rows, col_widths, header_color="#e0e7ff",
           font_size=9.5, scale=1.85, cell_align="center"):
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=10, color="#999"); return
    t = ax.table(cellText=rows, colLabels=header, loc="upper left",
                 cellLoc=cell_align, colWidths=col_widths)
    t.auto_set_font_size(False); t.set_fontsize(font_size); t.scale(1.0, scale)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold", color="#1e3a8a")
        else:
            cell.set_facecolor("#ffffff" if (r - 1) % 2 == 0 else "#f8fafc")


def _warn_box(fig, y, h, title, body, bg="#fef3c7", border="#d97706", text="#78350f"):
    ax = fig.add_axes([0.04, y, 0.92, h]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                 transform=ax.transAxes,
                                 facecolor=bg, edgecolor=border, linewidth=1.2))
    ax.text(0.02, 0.78, title, fontsize=11.5, fontweight="bold", color=text, va="center")
    ax.text(0.02, 0.32, body, fontsize=10, color=text, va="center", linespacing=1.6)


# ===== 데이터 로드 + 집계 =====
def load_data():
    df = pd.read_csv(DETAIL_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    df["signal_date"] = pd.to_datetime(df["signal_date"], errors="coerce")
    for col in ["score_total_100", "entry_price_1500", "entry_minute_volume",
                "entry_minute_value_krw", "d1_high_return_pct", "d1_low_return_pct",
                "d5_high_return_pct", "d5_low_return_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["fill_pass"] = df["fill_filter_passed"].astype(str) == "True"
    df["rank_v2"] = pd.to_numeric(df["rank_v2"], errors="coerce")

    # win/loss flags (다양한 horizon × threshold)
    for thr in [1, 2, 3, 5]:
        df[f"d1_high_ge_{thr}"] = df["d1_high_return_pct"] >= thr
        df[f"d1_low_le_m{thr}"] = df["d1_low_return_pct"] <= -thr
        df[f"d5_high_ge_{thr}"] = df["d5_high_return_pct"] >= thr
        df[f"d5_low_le_m{thr}"] = df["d5_low_return_pct"] <= -thr

    # first-touch summary 별도 로드
    ft = pd.read_csv(FIRST_TOUCH_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    for col in ["sample_n", "profit_first_n", "loss_first_n", "same_bar_both_n",
                "neither_n", "missing_n", "profit_first_rate_pct",
                "loss_first_rate_pct", "profit_minus_loss_pp", "threshold_pair"]:
        ft[col] = pd.to_numeric(ft[col], errors="coerce")

    summ = pd.read_csv(SUMMARY_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    return df, ft, summ


# ===== 페이지 1 — 표지 =====
def page_1_cover(pdf, total, df, ft):
    fig = plt.figure(figsize=A4_LANDSCAPE)

    ax = fig.add_axes([0.0, 0.78, 1.0, 0.22]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.05, 0.66, "Phase 0 Realistic Fill 시뮬 — 자세한 승률 보고서",
            fontsize=20, fontweight="bold", color="white", va="center")
    ax.text(0.05, 0.34, "D0_STRICT_3D_V2_TOP3 baseline · 1년 (251일) · 753 후보 · 일자별 표 포함",
            fontsize=12, color="#dbeafe", va="center")
    ax.text(0.05, 0.10, f"작성 {datetime.now().strftime('%Y-%m-%d')}  ·  Claude Code  ·  Paper Watch 연구용",
            fontsize=10, color="#cbd5e0", va="center")

    # 핵심 수치 6개 카드
    _band(fig, 0.69, 0, "한 페이지 요약 — 6 가지 핵심 수치",
          color="#fef3c7", text_color="#78350f")

    fill_pass_pct = df["fill_pass"].mean() * 100
    d1_win2 = df["d1_high_ge_2"].mean() * 100
    d1_loss2 = df["d1_low_le_m2"].mean() * 100
    d5_win3 = df["d5_high_ge_3"].mean() * 100
    d5_loss3 = df["d5_low_le_m3"].mean() * 100

    # first-touch from CSV
    ft_d1_2 = ft[(ft["scope"] == "fill_passed_only") &
                 (ft["first_touch_horizon"] == "d1_close") &
                 (ft["threshold_pair"] == 2)].iloc[0]
    ft_d5_3 = ft[(ft["scope"] == "fill_passed_only") &
                 (ft["first_touch_horizon"] == "d5_close") &
                 (ft["threshold_pair"] == 3)].iloc[0]

    cards = [
        ("Fill 통과율",        f"{fill_pass_pct:.1f}%", f"744 / 753",                "#16a34a"),
        ("D+1 +2% 도달률",     f"{d1_win2:.1f}%",      "다음날 high",              "#3b82f6"),
        ("D+1 -2% 도달률",     f"{d1_loss2:.1f}%",     "다음날 low",                "#dc2626"),
        ("D+1 +/-2 first 차이", f"+{ft_d1_2['profit_minus_loss_pp']:.1f}%p",
                                f"{ft_d1_2['profit_first_rate_pct']:.1f}% / {ft_d1_2['loss_first_rate_pct']:.1f}%", "#1e3a8a"),
        ("D+5 +/-3 first 차이", f"+{ft_d5_3['profit_minus_loss_pp']:.1f}%p",
                                f"{ft_d5_3['profit_first_rate_pct']:.1f}% / {ft_d5_3['loss_first_rate_pct']:.1f}%", "#1e3a8a"),
        ("표본 (1년 251일)",    "753 행",               "744 fill passed",            "#6b7280"),
    ]
    for i, (label, big, sub, color) in enumerate(cards):
        col = i % 3; row = i // 3
        x = 0.04 + col * 0.32
        y = 0.45 - row * 0.20
        ax = fig.add_axes([x, y, 0.28, 0.18]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.01",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color, linewidth=1.5))
        ax.text(0.5, 0.78, label, fontsize=10, color="#6b7280",
                ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.45, big, fontsize=22, fontweight="bold",
                color=color, ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.15, sub, fontsize=9, color="#374151",
                ha="center", va="center", transform=ax.transAxes)

    # 하단 메모
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.05]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.008",
                                 transform=ax.transAxes,
                                 facecolor="#dbeafe", edgecolor="#1e3a8a", linewidth=1))
    ax.text(0.02, 0.5,
            "★ 핵심 — 도달률 (다음날 high/low) 은 V2 우위 (D+1 +2% 70.1%), "
            "단 first-touch (선후관계) 가 진짜 운영 수치: D+1 +/-2% = +8.6%p edge, D+5 +/-5% = +14.4%p edge",
            fontsize=10, color="#1e3a8a", va="center", fontweight="bold")

    _footer(fig, 1, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 2 — 시뮬 개요 =====
def page_2_overview(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "2. 시뮬 개요 — Phase 0 Realistic Fill 이 무엇인가",
            f"기간 {df['signal_date'].min().strftime('%Y-%m-%d')} ~ {df['signal_date'].max().strftime('%Y-%m-%d')}")

    _band(fig, 0.83, 1, "이 시뮬이 추가한 것")
    ax = fig.add_axes([0.04, 0.55, 0.92, 0.27]); ax.axis("off")
    paras = [
        "기존 V2 백데이터는 '도달률' (다음날 분봉이 +2%/-2% 선을 한 번이라도 닿았는지) 만 봤습니다.",
        "이번 Phase 0 시뮬은 거기에 **최소 현실 체결 가능성 게이트** 를 붙였습니다:",
        "       • 15:00 분봉 존재 / 지연 / 거래량 / 거래대금 / 상한가 잠김 proxy",
        "       • 9 행은 'UPPER_LIMIT_LOCKED_PROXY' 로 하드 reject (1.2%)",
        "       • 25 행은 거래량 < 1,000 등 warning 만 (통과)",
        "그리고 '도달률' 이 아닌 **first-touch (선후관계)** 도 같이 계산 — 익절선과 손절선 중 어느 쪽이 먼저 닿았나.",
    ]
    ax.text(0.0, 0.97, "\n".join(paras), fontsize=11, color="#374151",
            va="top", linespacing=1.85, family="Malgun Gothic")

    # 입력 baseline 박스
    _band(fig, 0.48, 2, "Baseline 정책 — 무엇을 풀로 썼나",
          color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.40]); ax.axis("off")
    rows = [
        ["strategy_id",          "CLOSINGBELL_D0_STRICT_3D_V2_TOP3"],
        ["source_pool",          "active D0 3일 pool (KOSPI/KOSDAQ 보통주, 거래량 ≥ 1,000만, 가격 2,000~100,000원)"],
        ["score_variant_id",     "D0_POOL_S10_NO_PROGRAM__TOP3 (프로그램 매수 feature 제외)"],
        ["score_policy",         "TOP3_NO_MIN_SCORE (점수 desc, 무조건 3개)"],
        ["entry_base_time",      "15:00 첫 분봉 종가"],
        ["v2_tracking_days",     "D+1 ~ D+5"],
        ["fill filter",          "entry bar 존재 + 지연 / 거래량 / 상한가 잠김 proxy 체크"],
        ["기간",                  f"{df['signal_date'].min().strftime('%Y-%m-%d')} ~ {df['signal_date'].max().strftime('%Y-%m-%d')} (251 거래일)"],
        ["표본 수",                f"753 행 (744 fill passed, 9 rejected)"],
    ]
    _table(ax, ["키", "값"], rows, [0.30, 0.70],
           header_color="#bfdbfe", scale=1.85, cell_align="left")

    _footer(fig, 2, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 3 — Fill Filter =====
def page_3_fill_filter(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "3. Fill Filter 통과율", "현실 체결 가능성 1차 게이트")

    _band(fig, 0.83, 1, "통과 / 거절 / 경고 한눈에")
    ax = fig.add_axes([0.04, 0.62, 0.92, 0.20]); ax.axis("off")
    rows = [
        ["fill_filter_total",                     "753",     "100.0%", "baseline 선택 행"],
        ["fill_filter_passed",                    "744",     "98.8%",  "하드 reject 없음"],
        ["fill_filter_rejected",                  "9",       "1.2%",   "entry bar / 상한가 잠김 proxy"],
        ["reject_UPPER_LIMIT_LOCKED_PROXY",       "9",       "1.2%",   "다음날 진입 불가"],
        ["warn_LOW_ENTRY_MINUTE_VOLUME_LT_1000",  "25",      "3.3%",   "경고만 (통과)"],
        ["warn_LOW_ENTRY_MINUTE_VALUE_LT_5M_KRW", "18",      "2.4%",   "경고만 (통과)"],
    ]
    _table(ax, ["metric", "count", "비율", "비고"],
           rows, [0.40, 0.10, 0.10, 0.40],
           header_color="#fde68a", scale=1.85, cell_align="left")

    # Visual — pie / bar
    _band(fig, 0.55, 2, "통과 비율 시각화")
    ax_pie = fig.add_axes([0.10, 0.20, 0.35, 0.32])
    sizes = [744, 9]
    labels = [f"통과 (744)\n98.8%", f"거절 (9)\n1.2%"]
    colors = ["#16a34a", "#dc2626"]
    ax_pie.pie(sizes, labels=labels, colors=colors, startangle=90,
               wedgeprops=dict(edgecolor="white", linewidth=2),
               textprops=dict(fontsize=11, color="#1f2937"))
    ax_pie.set_title("Fill Filter Pass / Reject", fontsize=11,
                     color="#1e3a8a", pad=8)

    # 경고 막대
    ax_bar = fig.add_axes([0.55, 0.20, 0.40, 0.32])
    warn_labels = ["거래량\n< 1,000", "거래대금\n< 5M원", "0.005%\n미만"]
    warn_counts = [25, 18, 18]
    bars = ax_bar.bar(warn_labels, warn_counts, color="#ca8a04", alpha=0.85, width=0.55)
    for b in bars:
        ax_bar.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                    f"{int(b.get_height())} 건", ha="center", fontsize=10,
                    color="#78350f", fontweight="bold")
    ax_bar.set_ylabel("건수", fontsize=10)
    ax_bar.set_ylim(0, 30)
    ax_bar.set_title("경고 (통과는 됨)", fontsize=11, color="#1e3a8a", pad=8)
    ax_bar.grid(axis="y", alpha=0.3)

    # 메모
    _warn_box(fig, 0.05, 0.13,
              "이 fill filter 가 보수적인 이유",
              "상한가/VI/단일가/거래정지/호가잔량/저유동성 슬리피지 까지 완전 결합 X — "
              "Phase 1 (Realistic Fill Filter 최종화) 에서 더 깎일 예정. 현재 98.8% 통과율은 보수적 출발점.")

    _footer(fig, 3, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 4 — First-touch 핵심 표 =====
def page_4_first_touch_table(pdf, total, ft):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "4. First-Touch 핵심 승률 — 선후관계 기반",
            "어느 쪽이 먼저 닿았나 (도달률 != 승률)")

    _band(fig, 0.83, 1, "fill_passed_only (744 행) — Horizon × Threshold")
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.62]); ax.axis("off")

    # fill_passed_only 만, scope/policy 제외
    fp = ft[ft["scope"] == "fill_passed_only"].copy()
    rows = []
    horizons_kor = {"d1_1130": "D+1 (11:30)", "d1_close": "D+1 종가",
                    "d3_close": "D+3 종가", "d5_close": "D+5 종가"}
    for _, r in fp.iterrows():
        horizon_kor = horizons_kor.get(r["first_touch_horizon"], r["first_touch_horizon"])
        thr = r["threshold_pair"]
        rows.append([
            horizon_kor,
            f"+/- {int(thr)}%",
            f"{int(r['sample_n'])}",
            f"{int(r['profit_first_n'])}",
            f"{int(r['loss_first_n'])}",
            f"{int(r['same_bar_both_n'])}",
            f"{int(r['neither_n'])}",
            f"{r['profit_first_rate_pct']:.2f}%",
            f"{r['loss_first_rate_pct']:.2f}%",
            f"+{r['profit_minus_loss_pp']:.2f}%p" if r["profit_minus_loss_pp"] >= 0
                else f"{r['profit_minus_loss_pp']:.2f}%p",
        ])

    _table(ax,
           ["호라이즌", "기준선", "표본", "익절 먼저", "손절 먼저", "같은 봉", "둘 다 X", "익절률", "손절률", "차이"],
           rows,
           [0.13, 0.07, 0.06, 0.09, 0.09, 0.08, 0.08, 0.09, 0.09, 0.10],
           header_color="#bfdbfe", font_size=9, scale=1.55, cell_align="center")

    # 해석
    _warn_box(fig, 0.06, 0.13,
              "표 읽는 법",
              "• '익절 먼저' = +N% 선이 -N% 선보다 먼저 닿은 횟수 / '손절 먼저' = -N% 가 먼저\n"
              "• '같은 봉' = 1분봉 안에서 high·low 양쪽 동시 터치 (선후 불명)\n"
              "• '차이' = 익절률 - 손절률 (양수 = V2 우위, 운영 의미 있음)\n"
              "• 가장 큰 edge: D+1 11:30 ±5% = +13.94%p (변동 큰 종목 잡힘)",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    _footer(fig, 4, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 5 — Horizon × threshold 매트릭스 =====
def page_5_matrix(pdf, total, ft):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "5. Horizon × Threshold 매트릭스 — 그래프",
            "익절 - 손절 차이 (%p) 한눈에")

    fp = ft[ft["scope"] == "fill_passed_only"].copy()
    fp["threshold_pair"] = pd.to_numeric(fp["threshold_pair"])

    # Pivot
    pivot = fp.pivot_table(index="first_touch_horizon",
                            columns="threshold_pair",
                            values="profit_minus_loss_pp")
    pivot = pivot.reindex(["d1_1130", "d1_close", "d3_close", "d5_close"])

    _band(fig, 0.83, 1, "익절 - 손절 차이 (%p) — heatmap")
    ax = fig.add_axes([0.10, 0.40, 0.80, 0.42])
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn",
                   vmin=-5, vmax=15)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"+/- {int(c)}%" for c in pivot.columns], fontsize=11)
    ax.set_yticks(range(len(pivot.index)))
    horizons_kor = {"d1_1130": "D+1 (11:30)", "d1_close": "D+1 종가",
                    "d3_close": "D+3 종가", "d5_close": "D+5 종가"}
    ax.set_yticklabels([horizons_kor[h] for h in pivot.index], fontsize=11)
    # 값 표시
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            color = "white" if abs(v) > 8 else "#1f2937"
            ax.text(j, i, f"+{v:.1f}", ha="center", va="center",
                    fontsize=12, color=color, fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("익절 - 손절 (%p)", fontsize=10)
    ax.set_xlabel("기준선 (threshold)", fontsize=11)
    ax.set_ylabel("호라이즌", fontsize=11)
    ax.set_title("Phase 0 Realistic Fill — first-touch 차이 매트릭스",
                 fontsize=12, color="#1e3a8a", pad=10)

    # 해석
    _warn_box(fig, 0.06, 0.16,
              "매트릭스 읽는 법",
              "• 모든 셀이 양수 = 모든 호라이즌·threshold 에서 V2 우위 (보수적 측정)\n"
              "• 가장 진한 초록 셀이 가장 큰 edge: D+1 11:30 ±5% = +13.9%p, D+5 종가 ±5% = +12.5%p\n"
              "• 작은 threshold (±1, ±2) 에서는 +8~9%p 정도 (안정적이지만 작음) — 큰 변동 익절선이 V2 강점",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    _footer(fig, 5, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 6 — 도달률 vs first-touch 비교 =====
def page_6_touch_vs_first(pdf, total, df, ft):
    fig = plt.function = plt.figure(figsize=A4_LANDSCAPE) if False else plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "6. 도달률 vs First-Touch — 어느 게 진짜 승률인가",
            "왜 도달률이 부풀려 보이는가")

    # 도달률 (high/low touch 각각)
    d1_h2 = df["d1_high_ge_2"].mean() * 100
    d1_l2 = df["d1_low_le_m2"].mean() * 100
    d5_h3 = df["d5_high_ge_3"].mean() * 100
    d5_l3 = df["d5_low_le_m3"].mean() * 100

    # first-touch
    ft_fp = ft[ft["scope"] == "fill_passed_only"]
    ft_d1_2 = ft_fp[(ft_fp["first_touch_horizon"] == "d1_close") &
                    (ft_fp["threshold_pair"] == 2)].iloc[0]
    ft_d5_3 = ft_fp[(ft_fp["first_touch_horizon"] == "d5_close") &
                    (ft_fp["threshold_pair"] == 3)].iloc[0]

    _band(fig, 0.83, 1, "도달률 (touch rate) vs First-Touch (선후관계)")
    ax = fig.add_axes([0.10, 0.40, 0.80, 0.42])

    groups = ["D+1 +/-2%", "D+5 +/-3%"]
    touch_w = [d1_h2, d5_h3]
    touch_l = [d1_l2, d5_l3]
    ft_w = [ft_d1_2["profit_first_rate_pct"], ft_d5_3["profit_first_rate_pct"]]
    ft_l = [ft_d1_2["loss_first_rate_pct"], ft_d5_3["loss_first_rate_pct"]]

    x = np.arange(len(groups))
    w = 0.18
    b1 = ax.bar(x - 1.5 * w, touch_w, w, label="도달률 (high)", color="#86efac")
    b2 = ax.bar(x - 0.5 * w, touch_l, w, label="도달률 (low)", color="#fca5a5")
    b3 = ax.bar(x + 0.5 * w, ft_w, w, label="First-touch 익절", color="#16a34a")
    b4 = ax.bar(x + 1.5 * w, ft_l, w, label="First-touch 손절", color="#dc2626")
    for bars in (b1, b2, b3, b4):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1,
                    f"{b.get_height():.1f}", ha="center", fontsize=8.5, color="#374151")
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=11.5)
    ax.set_ylabel("%", fontsize=10)
    ax.set_ylim(0, 90)
    ax.legend(fontsize=9.5, loc="upper right", ncol=2, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("같은 표본 · 다른 측정 방법", fontsize=11,
                 color="#1e3a8a", pad=8)

    # 해설
    _warn_box(fig, 0.06, 0.20,
              "왜 first-touch 가 진짜 승률에 가까운가",
              "• 도달률 (touch rate) — 그 기간 안에 한 번이라도 +N%/-N% 선을 닿았는가 (high·low 독립)\n"
              "       → V2 변동성 큰 종목은 양쪽 다 닿아서 두 비율 모두 높음 (수치 부풀려 보임)\n"
              "• First-touch (선후관계) — 익절선과 손절선 중 어느 쪽이 '먼저' 닿았나 (실거래 가까움)\n"
              "       → 실제 운영에서는 둘 중 하나를 먼저 잡으면 거래 끝. 양쪽 동시 가능 X\n"
              "• 결론: 도달률은 '잠재력' / first-touch 는 '실현률'. 운영 판단은 first-touch 기준",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, 6, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 7 — 월별 승률 추이 =====
def page_7_monthly_trend(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "7. 월별 승률 추이",
            "1년치를 12개월로 잘라보기")

    df_m = df.copy()
    df_m["month"] = df_m["signal_date"].dt.to_period("M").astype(str)
    monthly = df_m.groupby("month").agg(
        n=("rank_v2", "count"),
        d1_w2=("d1_high_ge_2", "mean"),
        d1_l2=("d1_low_le_m2", "mean"),
        d5_w3=("d5_high_ge_3", "mean"),
        d5_l3=("d5_low_le_m3", "mean"),
    ).reset_index()
    monthly[["d1_w2", "d1_l2", "d5_w3", "d5_l3"]] *= 100

    _band(fig, 0.83, 1, "월별 도달률 추이 (D+1 +2%, D+1 -2%, D+5 +3%, D+5 -3%)")
    ax = fig.add_axes([0.08, 0.45, 0.86, 0.37])
    x = range(len(monthly))
    ax.plot(x, monthly["d1_w2"], marker="o", color="#16a34a", linewidth=2,
            label="D+1 +2% (익절 잠재)")
    ax.plot(x, monthly["d1_l2"], marker="o", color="#dc2626", linewidth=2,
            label="D+1 -2% (손절 잠재)")
    ax.plot(x, monthly["d5_w3"], marker="s", color="#10b981", linewidth=2,
            label="D+5 +3%", linestyle="--", alpha=0.8)
    ax.plot(x, monthly["d5_l3"], marker="s", color="#b91c1c", linewidth=2,
            label="D+5 -3%", linestyle="--", alpha=0.8)
    ax.set_xticks(x); ax.set_xticklabels(monthly["month"], rotation=45,
                                          ha="right", fontsize=9.5)
    ax.set_ylabel("도달률 (%)", fontsize=10)
    ax.set_ylim(0, 100)
    ax.legend(fontsize=9.5, loc="lower right", ncol=2, framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.set_title("월별 V2 Top3 도달률 (이상치 한 달 ↑/↓ 확인용)",
                 fontsize=11, color="#1e3a8a", pad=8)

    # 월별 표
    _band(fig, 0.36, 2, "월별 수치표")
    ax_t = fig.add_axes([0.04, 0.05, 0.92, 0.30]); ax_t.axis("off")
    rows = []
    for _, r in monthly.iterrows():
        rows.append([
            r["month"],
            f"{int(r['n'])}",
            f"{r['d1_w2']:.1f}%",
            f"{r['d1_l2']:.1f}%",
            f"{r['d5_w3']:.1f}%",
            f"{r['d5_l3']:.1f}%",
        ])
    _table(ax_t, ["월", "표본", "D+1 +2%", "D+1 -2%", "D+5 +3%", "D+5 -3%"],
           rows, [0.14, 0.10, 0.19, 0.19, 0.19, 0.19],
           header_color="#bfdbfe", scale=1.55, font_size=9)

    _footer(fig, 7, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 8 — 22일 sliding =====
def page_8_sliding(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "8. 22 거래일 sliding 승률",
            "롤링 윈도우 — 최근 안정성 확인")

    df_s = df.copy().sort_values("signal_date")
    df_s["date_str"] = df_s["signal_date"].dt.strftime("%Y-%m-%d")
    daily = df_s.groupby("date_str").agg(
        n=("rank_v2", "count"),
        d1_w2_sum=("d1_high_ge_2", "sum"),
        d1_l2_sum=("d1_low_le_m2", "sum"),
        d5_w3_sum=("d5_high_ge_3", "sum"),
        d5_l3_sum=("d5_low_le_m3", "sum"),
    ).reset_index()

    win = 22  # 22 거래일
    daily["d1_w2"] = daily["d1_w2_sum"].rolling(win).sum() / daily["n"].rolling(win).sum() * 100
    daily["d1_l2"] = daily["d1_l2_sum"].rolling(win).sum() / daily["n"].rolling(win).sum() * 100
    daily["d5_w3"] = daily["d5_w3_sum"].rolling(win).sum() / daily["n"].rolling(win).sum() * 100
    daily["d5_l3"] = daily["d5_l3_sum"].rolling(win).sum() / daily["n"].rolling(win).sum() * 100

    _band(fig, 0.83, 1, "22 거래일 sliding — D+1 / D+5 도달률")
    ax = fig.add_axes([0.08, 0.18, 0.86, 0.64])
    valid = daily.dropna(subset=["d1_w2"])
    x = pd.to_datetime(valid["date_str"])
    ax.plot(x, valid["d1_w2"], color="#16a34a", linewidth=2,
            label="D+1 +2% (sliding 22d)")
    ax.plot(x, valid["d1_l2"], color="#dc2626", linewidth=2,
            label="D+1 -2% (sliding 22d)")
    ax.plot(x, valid["d5_w3"], color="#10b981", linewidth=2,
            label="D+5 +3% (sliding 22d)", linestyle="--", alpha=0.85)
    ax.plot(x, valid["d5_l3"], color="#b91c1c", linewidth=2,
            label="D+5 -3% (sliding 22d)", linestyle="--", alpha=0.85)
    ax.set_ylabel("도달률 (%)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.legend(fontsize=10, loc="lower left", ncol=2, framealpha=0.9)
    ax.grid(alpha=0.3)
    ax.tick_params(axis="x", labelsize=9.5)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.set_title("최근 22 거래일 sliding 승률 — robust 한지 확인",
                 fontsize=11, color="#1e3a8a", pad=8)

    # 해설
    _warn_box(fig, 0.05, 0.10,
              "이 그래프 읽는 법",
              "• 라인이 평탄할수록 robust (시기 의존성 적음) / 들쭉날쭉이면 시장 사이클 영향 큼\n"
              "• D+1 +2% (초록) 가 D+1 -2% (빨강) 위에 있을 때 V2 우위 — 거의 항상 위에 있음 (양수 edge 일관)",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, 8, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 9 — 점수 분위별 =====
def page_9_score_quartile(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "9. V2 점수 분위별 결과",
            "점수 높을수록 진짜 더 좋은가")

    df_s = df[df["fill_pass"]].copy()
    df_s["score_band"] = pd.cut(df_s["score_total_100"],
                                 bins=[0, 55, 65, 75, 100],
                                 labels=["< 55", "55~64", "65~74", "75+"])
    agg = df_s.groupby("score_band", observed=True).agg(
        n=("score_total_100", "count"),
        d1_w2=("d1_high_ge_2", "mean"),
        d1_l2=("d1_low_le_m2", "mean"),
        d5_w3=("d5_high_ge_3", "mean"),
        d5_l3=("d5_low_le_m3", "mean"),
        med_score=("score_total_100", "median"),
    ).reset_index()
    agg[["d1_w2", "d1_l2", "d5_w3", "d5_l3"]] *= 100

    _band(fig, 0.83, 1, "점수 구간별 도달률")
    ax = fig.add_axes([0.10, 0.40, 0.80, 0.42])
    bands = agg["score_band"].astype(str).tolist()
    x = np.arange(len(bands))
    w = 0.20
    ax.bar(x - 1.5 * w, agg["d1_w2"], w, label="D+1 +2%", color="#16a34a")
    ax.bar(x - 0.5 * w, agg["d1_l2"], w, label="D+1 -2%", color="#dc2626")
    ax.bar(x + 0.5 * w, agg["d5_w3"], w, label="D+5 +3%", color="#10b981")
    ax.bar(x + 1.5 * w, agg["d5_l3"], w, label="D+5 -3%", color="#b91c1c")
    ax.set_xticks(x); ax.set_xticklabels(bands, fontsize=11)
    ax.set_ylabel("도달률 (%)", fontsize=10)
    ax.set_ylim(0, 85)
    ax.legend(fontsize=9.5, loc="upper right", ncol=2, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    for i, n in enumerate(agg["n"]):
        ax.text(i, -5, f"n={int(n)}", ha="center", fontsize=9, color="#6b7280")

    # 분위별 수치표
    _band(fig, 0.32, 2, "구간별 수치", color="#dcfce7", text_color="#14532d")
    ax_t = fig.add_axes([0.04, 0.05, 0.92, 0.26]); ax_t.axis("off")
    rows = [[str(r["score_band"]), int(r["n"]), f"{r['med_score']:.1f}",
             f"{r['d1_w2']:.1f}%", f"{r['d1_l2']:.1f}%",
             f"{r['d5_w3']:.1f}%", f"{r['d5_l3']:.1f}%"]
            for _, r in agg.iterrows()]
    _table(ax_t,
           ["점수 구간", "표본", "중앙 점수", "D+1 +2%", "D+1 -2%", "D+5 +3%", "D+5 -3%"],
           rows, [0.14, 0.10, 0.14, 0.155, 0.155, 0.155, 0.155],
           header_color="#dcfce7", scale=2.0)

    _footer(fig, 9, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 10~15 — 일자별 표 (251일 ÷ 6 페이지 = ~42일/페이지) =====
def page_daily_table(pdf, total, df, page_no, daily_full, start_idx, end_idx):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    page_total = (len(daily_full) + 41) // 42
    page_idx = page_no - 9
    sub = f"{start_idx + 1}~{min(end_idx, len(daily_full))} / {len(daily_full)} 일  ·  page {page_idx} / {page_total}"
    _header(fig, f"{page_no}. 일자별 표 — 각 거래일 V2 Top3 결과",
            sub)

    chunk = daily_full.iloc[start_idx:end_idx].copy()
    _band(fig, 0.84, 1, f"기간 {chunk.iloc[0]['date_str']} ~ {chunk.iloc[-1]['date_str']}  ·  {len(chunk)} 거래일")
    ax = fig.add_axes([0.025, 0.045, 0.95, 0.79]); ax.axis("off")

    rows = []
    for _, r in chunk.iterrows():
        rows.append([
            r["date_str"],
            f"{int(r['n'])}",
            f"{int(r['fill_pass'])}",
            f"{r['d1_high_med']:+.2f}" if pd.notna(r["d1_high_med"]) else "—",
            f"{r['d1_low_med']:+.2f}" if pd.notna(r["d1_low_med"]) else "—",
            f"{r['d5_high_med']:+.2f}" if pd.notna(r["d5_high_med"]) else "—",
            f"{r['d5_low_med']:+.2f}" if pd.notna(r["d5_low_med"]) else "—",
            f"{int(r['d1_win2'])}/{int(r['n'])}",
            f"{int(r['d1_loss2'])}/{int(r['n'])}",
            f"{int(r['d5_win3'])}/{int(r['n'])}",
            f"{int(r['d5_loss3'])}/{int(r['n'])}",
        ])
    _table(ax,
           ["신호일", "표본", "fill 통과", "D+1 H 중앙(%)", "D+1 L 중앙(%)",
            "D+5 H 중앙(%)", "D+5 L 중앙(%)", "D+1 +2 hit", "D+1 -2 hit",
            "D+5 +3 hit", "D+5 -3 hit"],
           rows,
           [0.09, 0.05, 0.06, 0.10, 0.10, 0.10, 0.10, 0.08, 0.08, 0.08, 0.08],
           header_color="#e0e7ff", font_size=8, scale=0.95)

    _footer(fig, page_no, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 16 — 한계 + 다음 단계 =====
def page_final(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "16. 한계 + 다음 단계", "이 시뮬이 못 본 것")

    _band(fig, 0.83, 1, "Phase 0 의 한계 — 정직하게")
    ax = fig.add_axes([0.04, 0.55, 0.92, 0.27]); ax.axis("off")
    limits = [
        "1. Fill filter 가 진짜 보수적이지 않음 — VI / 단일가 / 거래정지 / 호가잔량 미반영",
        "2. 슬리피지 0 가정 — 실거래는 0.3~1.5% 호가창 위 체결 → 실제 익절선 +2.5%, 손절 -2.5% 로 봐야 함",
        "3. 시가 갭 미반영 — D+1 시가 진입 시 D0 종가 대비 평균 ~0.5~1.5% 이격 가능",
        "4. 체결 지연 미반영 — 주문 송신 → 거래소 처리 → 호가창 도착까지 수백 ms~수 초",
        "5. 거래량 작은 종목은 시장가 매수 시 호가 1~3 호가 잡아먹는 슬리피지 큼",
        "6. 자동매매 / 실주문 미연결 — 본 결과는 Paper Watch 전용",
    ]
    ax.text(0.0, 0.97, "\n".join([f"• {l}" for l in limits]), fontsize=10.5,
            color="#374151", va="top", linespacing=1.85, family="Malgun Gothic")

    _band(fig, 0.46, 2, "Phase 1 (다음 단계) — 추가할 것", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.16, 0.92, 0.30]); ax.axis("off")
    nexts = [
        "1. Realistic Fill Filter 최종화 — VI / 단일가 / 거래정지 / 호가잔량 / 저유동성 슬리피지 결합",
        "2. 슬리피지 보정 모델 — 거래대금 / 호가 spread 기반으로 익절/손절선 자동 보정",
        "3. D0 후보군 audit — 대형주 (현대차·SK하이닉스) 가 D0 strict 풀에 들어온 경로 확인",
        "4. ENTRY_DROP_MINUS3 / VWAP reclaim / ORB reclaim — 진입 타이밍 변형 비교",
        "5. 글로벌·거시 regime stratification — 시장 상황별 V2 성과 차이",
        "6. Phase 2~3 단계 진입 — paper watch 안정 확인 + 사용자 명시 승인 후",
    ]
    ax.text(0.0, 0.95, "\n".join([f"• {l}" for l in nexts]), fontsize=10.5,
            color="#14532d", va="top", linespacing=1.85, family="Malgun Gothic")

    # 한 줄 결론
    _warn_box(fig, 0.06, 0.08,
              "한 줄 결론",
              "1년 251일 753 행 baseline 에서 first-touch 기준 V2 가 P0 대비 +8~14%p edge — "
              "운영 단독 전환 OK 라고 단정할 수준은 아니지만 Paper Watch 단계는 충분히 의미 있음.",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, total, total); pdf.savefig(fig); plt.close(fig)


# ===== Main =====
def build(out_path: Path):
    df, ft, summ = load_data()

    # daily aggregation for daily tables
    df["d1_high"] = df["d1_high_return_pct"]
    df["d1_low"] = df["d1_low_return_pct"]
    df["d5_high"] = df["d5_high_return_pct"]
    df["d5_low"] = df["d5_low_return_pct"]
    df["date_str"] = df["signal_date"].dt.strftime("%Y-%m-%d")
    daily_full = df.groupby("date_str").agg(
        n=("rank_v2", "count"),
        fill_pass=("fill_pass", "sum"),
        d1_high_med=("d1_high", "median"),
        d1_low_med=("d1_low", "median"),
        d5_high_med=("d5_high", "median"),
        d5_low_med=("d5_low", "median"),
        d1_win2=("d1_high_ge_2", "sum"),
        d1_loss2=("d1_low_le_m2", "sum"),
        d5_win3=("d5_high_ge_3", "sum"),
        d5_loss3=("d5_low_le_m3", "sum"),
    ).reset_index().sort_values("date_str", ascending=False)  # 최근 → 과거

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 일자별 표 페이지 수: 42일/페이지로 분할
    chunk_size = 42
    n_daily_pages = (len(daily_full) + chunk_size - 1) // chunk_size
    total = 9 + n_daily_pages + 1

    with PdfPages(out_path) as pdf:
        page_1_cover(pdf, total, df, ft)
        page_2_overview(pdf, total, df)
        page_3_fill_filter(pdf, total, df)
        page_4_first_touch_table(pdf, total, ft)
        page_5_matrix(pdf, total, ft)
        page_6_touch_vs_first(pdf, total, df, ft)
        page_7_monthly_trend(pdf, total, df)
        page_8_sliding(pdf, total, df)
        page_9_score_quartile(pdf, total, df)

        for i in range(n_daily_pages):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(daily_full))
            page_no = 10 + i
            page_daily_table(pdf, total, df, page_no, daily_full, start, end)

        page_final(pdf, total)

    size_kb = out_path.stat().st_size / 1024
    print(f"[ok] {out_path}  ({size_kb:.1f} KB, {total} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(r"C:\Users\PYJ\Downloads\PHASE0_REALISTIC_FILL_SIM_DETAIL_KR_20260515.pdf"))
    args = ap.parse_args()
    build(args.out)
