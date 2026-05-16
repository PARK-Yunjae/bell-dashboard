"""
V2 점수 sweet spot + 데이터 진단 + 스케줄러 체크 종합 PDF.

사용자 질문 3가지에 답:
    1. 백테스트 1년치 데이터 있는지 + C:\\Coding\\data 폴더 구조
    2. 55~70점 사이가 왜 승률이 좋을지 (실제로는 70~80점이 sweet spot)
    3. 14:15 / 15:00 / 17:05 슬롯 체크 방법

입력:
    Codex 2026-05-15 09:00 산출 sweet spot CSV 3개:
    - V2_SCORE_RANK_SWEETSPOT_SCORE_RANK_BUCKET_SUMMARY_20260515.csv
    - V2_SCORE_RANK_SWEETSPOT_RANK_ONLY_SUMMARY_20260515.csv
    - V2_SCORE_RANK_SWEETSPOT_SWEETSPOT_CANDIDATE_SUMMARY_20260515.csv

페이지 (~12 페이지):
    1. 표지 + 결론 한 페이지
    2. 데이터 폴더 / 백테스트 현황
    3. 점수대별 first-touch 막대 (D+1 ±2 / D+5 ±3)
    4. 점수대별 표 (전체)
    5. 순위별 first-touch (rank1/rank2/rank3)
    6. 점수×순위 매트릭스 heatmap
    7. Sweet spot 후보 그룹 비교
    8. 70~80점이 왜 sweet spot 인가 - 해석
    9. 14:15 / 15:00 / 17:05 슬롯 체크 가이드
   10. 결론 + 다음 단계
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

BUCKET_CSV = Path(r"C:\Users\PYJ\Downloads\V2_SCORE_RANK_SWEETSPOT_SCORE_RANK_BUCKET_SUMMARY_20260515.csv")
RANK_CSV = Path(r"C:\Users\PYJ\Downloads\V2_SCORE_RANK_SWEETSPOT_RANK_ONLY_SUMMARY_20260515.csv")
SWEET_CSV = Path(r"C:\Users\PYJ\Downloads\V2_SCORE_RANK_SWEETSPOT_SWEETSPOT_CANDIDATE_SUMMARY_20260515.csv")
MATRIX_CSV = Path(r"C:\Users\PYJ\Downloads\V2_SCORE_RANK_SWEETSPOT_SCORE_RANK_MATRIX_20260515.csv")


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
            "V2 점수 sweet spot + 데이터 진단  ·  연구·관찰용  ·  자동매매 아님",
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


# ===== 데이터 로드 =====
def load_data():
    df = pd.read_csv(BUCKET_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    # bucket 라벨 정리
    df["bucket"] = df["group"].str.replace("score_bucket=", "")
    for col in df.columns:
        if col not in ("group", "bucket"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    rank_df = pd.read_csv(RANK_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    for col in rank_df.columns:
        if col != "group":
            rank_df[col] = pd.to_numeric(rank_df[col], errors="coerce")

    sweet_df = pd.read_csv(SWEET_CSV, dtype=str, encoding="utf-8-sig").fillna("")

    matrix_df = pd.read_csv(MATRIX_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    for col in matrix_df.columns:
        if col not in ("group", "score_bucket", "rank_v2"):
            matrix_df[col] = pd.to_numeric(matrix_df[col], errors="coerce")
    return df, rank_df, sweet_df, matrix_df


# ===== 페이지 1 — 표지 + 결론 =====
def page_1_cover(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    ax = fig.add_axes([0.0, 0.78, 1.0, 0.22]); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                           facecolor="#1e3a8a", edgecolor="none"))
    ax.text(0.05, 0.66, "V2 점수 sweet spot + 데이터 진단",
            fontsize=22, fontweight="bold", color="white", va="center")
    ax.text(0.05, 0.36, "사용자 질문 3가지 답 - 백테스트 데이터 / 55-70점 분석 / 슬롯 체크",
            fontsize=12, color="#dbeafe", va="center")
    ax.text(0.05, 0.10, f"작성 {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  Claude Code  ·  Codex 09:00 sweet spot 리서치 인용",
            fontsize=10, color="#cbd5e0", va="center")

    _band(fig, 0.69, 0, "결론 한 페이지 - 사용자 3가지 질문에 답",
          color="#fef3c7", text_color="#78350f")

    # 3 카드
    answers = [
        ("Q1. 백테스트 1년 데이터 + C:\\Coding\\data 폴더",
         "★ 모두 정상.\n"
         "  - daily parquet 2,883개 (target_rate 99.3%) - 2026-05-15 06:57 갱신\n"
         "  - minute parquet 2,688개 (target_rate 93.9%) - 2026-05-15 07:25 갱신\n"
         "  - data/ 하위: closingbell(13) / dart(8) / market(10) / workspace_audit / _backups\n"
         "  - V2 1년 백데이터 753 행 (D+5 완성 738) 2026-05-15 08:28 재생성",
         "#16a34a"),
        ("Q2. 55-70점이 왜 좋은가? (사용자 가설 검증)",
         "★ 부분 수정. 실제로는 70-80점이 sweet spot.\n"
         "  - 65-70점 (N=37): D+1 +-2 first-touch +8.1pp, D+5 +-3 -2.7pp  → 약함\n"
         "  - 70-75점 (N=90): D+1 +12.2pp, D+5 +7.8pp  → 본격 강세\n"
         "  - 75-80점 (N=183): D+1 +17.5pp, D+5 +16.4pp  → ★ 최고 robust\n"
         "  - 80-90점 (N=412): D+1 +3.5~3.8pp  → 과열 (사용자 직감 일치)",
         "#3b82f6"),
        ("Q3. 14:15 / 15:00 / 17:05 슬롯 체크?",
         "★ 가능. 모니터링 스크립트 신설 (check_today_slots.ps1).\n"
         "  - 12:17 현재 baseline: 스케줄러 3개 Ready / 5/14 정상 실행\n"
         "  - 사용자가 15:01 / 17:06 이후 .\\check_today_slots.ps1 한 번 실행하면 OK\n"
         "  - 자동 점검: 산출물 존재 / manifest 가드 / HTTP 200/204 / 메시지 < 1800자\n"
         "  - 빨강/초록 색상 표시로 사용자 즉시 판정 가능",
         "#dc2626"),
    ]
    y = 0.49
    for title, body, color in answers:
        ax = fig.add_axes([0.05, y, 0.90, 0.18]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                     transform=ax.transAxes,
                                     facecolor="white", edgecolor=color, linewidth=1.5))
        ax.text(0.02, 0.78, title, fontsize=12, fontweight="bold",
                color=color, va="center")
        ax.text(0.02, 0.30, body, fontsize=9.8, color="#374151",
                va="center", linespacing=1.6)
        y -= 0.22

    _footer(fig, 1, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 2 — 데이터 폴더 / 백테스트 현황 =====
def page_2_data_status(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "2. 데이터 폴더 + 백테스트 1년치 현황",
            "C:\\Coding\\data 구조 + 갱신 상태")

    _band(fig, 0.83, 1, "C:\\Coding\\data 폴더 구조")
    ax = fig.add_axes([0.04, 0.62, 0.92, 0.20]); ax.axis("off")
    rows = [
        ["closingbell",      "13",  "운영 산출물 (V2 후보 / paper_watch / shared / scheduled / research_index / quality)"],
        ["dart",             "8",   "DART 공시 (company / finstate_ts / disclosures 등)"],
        ["market",           "10",  "시장 원천 (daily_ohlcv / minute_ohlcv / supply / global / events / universe ...)"],
        ["workspace_audit",  "1",   "워크스페이스 감사 결과 (보조)"],
        ["_backups",         "1",   "백업 (운영 미사용)"],
    ]
    _table(ax, ["폴더", "하위 디렉토리", "내용"],
           rows, [0.18, 0.12, 0.70],
           header_color="#bfdbfe", scale=1.85, cell_align="left")

    _band(fig, 0.55, 2, "2026-05-15 백테스트 1년치 데이터 갱신 상태", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.25, 0.92, 0.30]); ax.axis("off")
    rows = [
        ["daily_ohlcv",       "2,883",  "2,864",  "99.34%",  "2026-05-15 06:57", "OK"],
        ["minute_ohlcv",      "2,688",  "2,526",  "93.97%",  "2026-05-15 07:25", "PASS_WITH_GUARD"],
        ["inst_trade",        "2,810",  "2,805",  "99.82%",  "2026-05-15",       "OK"],
        ["short_sale",        "2,645",  "2,265",  "85.63%",  "2026-05-15",       "WARN"],
        ["program_per_code",  "243",    "74",     "30.45%",  "2026-04-27",       "COVERAGE_LOW (점수 미사용)"],
        ["global",            "3",      "2",      "66.67%",  "2026-05-11",       "STALE (regime stratifier 보조)"],
        ["dart",              "121",    "0",      "0.00%",   "2026-05-11",       "STALE (known_at 기준만)"],
    ]
    _table(ax,
           ["레이어", "파일 수", "target 도달", "도달률", "최신일", "판정"],
           rows, [0.20, 0.10, 0.12, 0.10, 0.20, 0.28],
           header_color="#dcfce7", scale=1.8, font_size=10)

    _warn_box(fig, 0.05, 0.18,
              "백테스트 1년치 데이터 = 충분히 사용 가능",
              "  V2 백데이터 1년: 753 행 (D+5 완성 738, 2026-05-15 08:28 갱신)\n"
              "  - 일봉/분봉 갱신 모두 오늘 새벽 완료\n"
              "  - 운영 V2 후보 (~50개) 의 분봉/15:00 기준가는 100% 갱신\n"
              "  - 단, 전체 universe 분봉은 162개 stale (대부분 daily 거래량 0인 종목)\n"
              "  - 시뮬용으로 충분, 단 전체 시장 sweep 이면 추가 갱신 필요",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    _footer(fig, 2, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 3 — 점수대별 first-touch 막대 =====
def page_3_score_bars(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "3. 점수대별 first-touch 차이 (%p)",
            "사용자 핵심 질문: 어느 점수대가 가장 좋나")

    _band(fig, 0.83, 1, "D+1 종가 +-2% / D+5 종가 +-3% (익절 - 손절 first-touch %p)")

    # 표본 N >= 30 인 bucket만 표시
    df_sig = df[df["sample_n"] >= 30].copy()
    df_sig = df_sig.sort_values("bucket")

    ax = fig.add_axes([0.08, 0.30, 0.86, 0.52])
    x = np.arange(len(df_sig))
    w = 0.36
    d1_pp = df_sig["d1_close_t2_profit_minus_loss_pp"].values
    d5_pp = df_sig["d5_close_t3_profit_minus_loss_pp"].values

    bars1 = ax.bar(x - w / 2, d1_pp, w, label="D+1 종가 +-2% (익절 - 손절)",
                   color="#3b82f6", alpha=0.85)
    bars2 = ax.bar(x + w / 2, d5_pp, w, label="D+5 종가 +-3% (익절 - 손절)",
                   color="#10b981", alpha=0.85)
    ax.axhline(0, color="#1f2937", linewidth=1)
    ax.set_xticks(x); ax.set_xticklabels(df_sig["bucket"], fontsize=11)
    ax.set_ylabel("first-touch 차이 (%p)", fontsize=11)
    ax.set_ylim(-5, 25)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("점수대별 first-touch edge (N >= 30 인 bucket 만)",
                 fontsize=12, color="#1e3a8a", pad=10)
    # 막대 위에 값 + 표본수
    for i, (b1, b2, n) in enumerate(zip(bars1, bars2, df_sig["sample_n"].values)):
        ax.text(b1.get_x() + b1.get_width() / 2,
                b1.get_height() + (0.5 if b1.get_height() >= 0 else -1.5),
                f"+{b1.get_height():.1f}" if b1.get_height() >= 0 else f"{b1.get_height():.1f}",
                ha="center", fontsize=9, color="#1e3a8a")
        ax.text(b2.get_x() + b2.get_width() / 2,
                b2.get_height() + (0.5 if b2.get_height() >= 0 else -1.5),
                f"+{b2.get_height():.1f}" if b2.get_height() >= 0 else f"{b2.get_height():.1f}",
                ha="center", fontsize=9, color="#14532d")
        ax.text(i, -3.5, f"n={int(n)}", ha="center", fontsize=8.5, color="#6b7280")

    _warn_box(fig, 0.05, 0.18,
              "★ 핵심 발견 - 75-80점이 진짜 sweet spot",
              "  - 75-80점 (N=183): D+1 +17.5pp / D+5 +16.4pp  ← 표본 많고 edge 가장 큼\n"
              "  - 70-75점 (N=90):  D+1 +12.2pp / D+5 +7.8pp   ← 시작 구간 (sweet spot 진입)\n"
              "  - 65-70점 (N=37):  D+1 +8.1pp  / D+5 -2.7pp   ← edge 약함 (sweet spot 미달)\n"
              "  - 80-85점 (N=239): D+1 +3.8pp  / D+5 +5.0pp   ← 표본 많지만 과열 (edge 감소)\n"
              "  - 85-90점 (N=173): D+1 +3.5pp  / D+5 +4.0pp   ← 과열 지속",
              bg="#fef3c7", border="#d97706", text="#78350f")

    _footer(fig, 3, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 4 — 점수대별 표 (전체) =====
def page_4_score_table(pdf, total, df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "4. 점수대별 상세 수치표 - 753 행 전체",
            "표본 / 통과율 / first-touch / MFE / MAE")

    _band(fig, 0.83, 1, "score_bucket 표 (오름차순)")
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.72]); ax.axis("off")

    df_s = df.sort_values("bucket")
    rows = []
    for _, r in df_s.iterrows():
        rows.append([
            r["bucket"],
            f"{int(r['sample_n']) if pd.notna(r['sample_n']) else 0}",
            f"{r['fill_pass_rate_pct']:.1f}%" if pd.notna(r['fill_pass_rate_pct']) else "—",
            f"{r['median_mfe_pct']:+.1f}%" if pd.notna(r['median_mfe_pct']) else "—",
            f"{r['median_mae_pct']:+.1f}%" if pd.notna(r['median_mae_pct']) else "—",
            f"{r['d1_close_t2_profit_first_rate_pct']:.1f}%" if pd.notna(r['d1_close_t2_profit_first_rate_pct']) else "—",
            f"{r['d1_close_t2_loss_first_rate_pct']:.1f}%" if pd.notna(r['d1_close_t2_loss_first_rate_pct']) else "—",
            f"{r['d1_close_t2_profit_minus_loss_pp']:+.1f}" if pd.notna(r['d1_close_t2_profit_minus_loss_pp']) else "—",
            f"{r['d5_close_t3_profit_first_rate_pct']:.1f}%" if pd.notna(r['d5_close_t3_profit_first_rate_pct']) else "—",
            f"{r['d5_close_t3_loss_first_rate_pct']:.1f}%" if pd.notna(r['d5_close_t3_loss_first_rate_pct']) else "—",
            f"{r['d5_close_t3_profit_minus_loss_pp']:+.1f}" if pd.notna(r['d5_close_t3_profit_minus_loss_pp']) else "—",
        ])

    _table(ax,
           ["점수대", "표본", "fill 통과", "MFE 중앙", "MAE 중앙",
            "D+1+2 익절", "D+1-2 손절", "D+1 Δ",
            "D+5+3 익절", "D+5-3 손절", "D+5 Δ"],
           rows,
           [0.09, 0.05, 0.08, 0.08, 0.08, 0.10, 0.10, 0.08, 0.10, 0.10, 0.08],
           header_color="#e0e7ff", scale=1.7, font_size=9)

    _footer(fig, 4, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 5 — 순위별 first-touch =====
def page_5_rank(pdf, total, rank_df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "5. V2 순위별 first-touch (rank1 / rank2 / rank3)",
            "어느 순위가 더 robust 한가")

    _band(fig, 0.83, 1, "순위별 D+1 +-2% 와 D+5 +-3% 차이 (%p)")
    rank_df_s = rank_df[rank_df["group"].isin(["rank1", "rank2", "rank3", "Top3_all"])].copy()

    ax = fig.add_axes([0.12, 0.42, 0.78, 0.40])
    x = np.arange(len(rank_df_s))
    w = 0.36
    d1 = rank_df_s["d1_close_t2_profit_minus_loss_pp"].values
    d5 = rank_df_s["d5_close_t3_profit_minus_loss_pp"].values
    bars1 = ax.bar(x - w / 2, d1, w, label="D+1 +-2% Δ", color="#3b82f6", alpha=0.85)
    bars2 = ax.bar(x + w / 2, d5, w, label="D+5 +-3% Δ", color="#10b981", alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(rank_df_s["group"], fontsize=11)
    ax.set_ylabel("first-touch 차이 (%p)", fontsize=10)
    ax.set_ylim(0, 13)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    for b in bars1:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15,
                f"+{b.get_height():.1f}", ha="center", fontsize=10, color="#1e3a8a")
    for b in bars2:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15,
                f"+{b.get_height():.1f}", ha="center", fontsize=10, color="#14532d")
    for i, n in enumerate(rank_df_s["sample_n"].values):
        ax.text(i, -1.0, f"n={int(n)}", ha="center", fontsize=9, color="#6b7280")

    _warn_box(fig, 0.05, 0.36,
              "순위별 해석",
              "  - rank1 (N=227): D+1 +10.1pp / D+5 +8.4pp - 가장 균형 잡힘 (점수 최고)\n"
              "  - rank2 (N=229): D+1 +3.9pp  / D+5 +6.6pp - rank3 보다 약함! 의외\n"
              "  - rank3 (N=238): D+1 +6.7pp  / D+5 +5.5pp - rank2 보다 D+1 우위\n"
              "  - Top3 전체 (N=753): D+1 +8.8pp / D+5 +8.1pp\n"
              "\n"
              "▶ 의외의 발견: rank2 가 rank3 보다 약한 구간 있음 - sweet spot 후보 그룹에서 더 깊이 봄.\n"
              "▶ 표본 200 이상으로 모두 N>=100 통계 유효성 통과.",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, 5, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 6 — 점수×순위 매트릭스 heatmap =====
def page_6_matrix(pdf, total, matrix_df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "6. 점수대 × 순위 매트릭스 - heatmap",
            "어느 칸이 진짜 가장 좋은가")

    # Build 9x3 grid
    buckets = ["<55", "55~60", "60~65", "65~70", "70~75",
               "75~80", "80~85", "85~90", "90+"]
    ranks = ["1", "2", "3"]
    mat = np.full((len(buckets), len(ranks)), np.nan)
    n_mat = np.full((len(buckets), len(ranks)), 0, dtype=int)
    for _, r in matrix_df.iterrows():
        b = r.get("score_bucket")
        rk = str(r.get("rank_v2"))
        if b in buckets and rk in ranks:
            v = r.get("d1_close_t2_profit_minus_loss_pp")
            n = r.get("sample_n", 0)
            mat[buckets.index(b), ranks.index(rk)] = v if pd.notna(v) else np.nan
            n_mat[buckets.index(b), ranks.index(rk)] = int(n) if pd.notna(n) else 0

    _band(fig, 0.83, 1, "D+1 종가 +-2% first-touch 차이 (%p) - 점수대 × rank")
    ax = fig.add_axes([0.15, 0.20, 0.65, 0.62])
    im = ax.imshow(mat, aspect="auto", cmap="RdYlGn", vmin=-15, vmax=25)
    ax.set_xticks(range(3)); ax.set_xticklabels([f"Rank {r}" for r in ranks], fontsize=11)
    ax.set_yticks(range(len(buckets))); ax.set_yticklabels(buckets, fontsize=10)
    # 값 + 표본수 표시
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]; n = n_mat[i, j]
            if n == 0:
                txt = "—"
            elif n < 10:
                txt = f"{v:+.0f}\nn={n}"
            else:
                txt = f"{v:+.1f}\nn={n}"
            col = "white" if abs(v if pd.notna(v) else 0) > 10 else "#1f2937"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=8.5, color=col, fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("D+1 +-2% Δ (%p)", fontsize=10)
    ax.set_title("점수 × 순위 매트릭스 (값: %p / N: 표본수)",
                 fontsize=12, color="#1e3a8a", pad=10)

    _warn_box(fig, 0.05, 0.13,
              "최강 칸들 (N >= 50)",
              "  - 75~80 × rank3 (N=74):  +18.9pp - 가장 큰 edge\n"
              "  - 75~80 × rank2 (N=68):  +10.3pp\n"
              "  - 75~80 × rank1 (N=23):  +30.4pp - 작은 표본 (warning)\n"
              "  - 70~75 × rank3 (N=45):  D+1 +0.0pp - 약함 (왜? - rank3 안에서도 점수가 낮으면 약함)\n"
              "  - 85~90 × rank1 (N=101): +8.9pp - 과열이지만 rank1 만 적당히 살아남음",
              bg="#fef3c7", border="#d97706", text="#78350f")

    _footer(fig, 6, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 7 — Sweet spot 후보 그룹 비교 =====
def page_7_sweetspot_groups(pdf, total, sweet_df):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "7. Sweet spot 후보 그룹 비교 - Codex 추천",
            "어떤 묶음이 OOS 검증 후보가 될까")

    _band(fig, 0.83, 1, "Codex sweet spot candidate 그룹 (raw)")
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.62]); ax.axis("off")
    rows = [
        ["Top3 전체",                         "753",  "98.8%",  "+8.76",  "+8.10",  "OOS 검증 가능"],
        ["Rank1 only",                       "227",  "100.0%", "+10.13", "+8.37",  "OOS 검증 가능"],
        ["Rank2 only",                       "229",  "99.1%",  "+3.93",  "+6.55",  "OOS 검증 가능 (약함)"],
        ["Rank3 only",                       "238",  "98.3%",  "+6.72",  "+5.46",  "OOS 검증 가능"],
        ["점수 85+ 전체",                     "202",  "100.0%", "+5.45",  "+6.44",  "OOS 검증 가능"],
        ["★ 점수 85+ × rank1 (high)",         "130",  "100.0%", "+10.77", "+10.77", "★★ OOS 가능 (high score 신뢰)"],
        ["★ 점수 70~85 (rank1 제외)",         "415",  "98.6%",  "+10.36", "+10.60", "★★ OOS 가능 (sweet spot 본체)"],
        ["★ 점수 65~75 전체",                 "127",  "92.9%",  "+11.02", "+4.72",  "★ OOS 가능 (sweet spot 진입)"],
        ["점수 65~80 × rank2 (research)",     "98",   "98.0%",  "+9.18",  "+8.16",  "research_only_N_lt_100"],
        ["점수 65~75 × rank2 (small)",        "30",   "93.3%",  "+6.67",  "+13.3",  "N<50 해석 X"],
        ["점수 <65 전체 (small)",             "2",    "100.0%", "0.0",    "0.0",    "N<50 해석 X"],
    ]
    _table(ax,
           ["그룹", "표본", "fill 통과", "D+1+-2 Δ", "D+5+-3 Δ", "OOS 단계"],
           rows, [0.34, 0.07, 0.10, 0.10, 0.10, 0.29],
           header_color="#dcfce7", scale=1.65, font_size=9.5, cell_align="left")

    _warn_box(fig, 0.04, 0.13,
              "Codex 추천 핵심 3개 그룹",
              "  1. 점수 70~85 (rank1 제외) - N=415 - D+1 +10.4pp / D+5 +10.6pp - sweet spot 본체\n"
              "  2. 점수 85+ × rank1       - N=130 - D+1 +10.8pp / D+5 +10.8pp - 고득점 신뢰\n"
              "  3. 점수 65~75 전체         - N=127 - D+1 +11.0pp / D+5 +4.7pp - sweet spot 진입 구간\n"
              "\n"
              "▶ 이 셋 모두 OOS (2026-02-01 이후) 1회 검증 후보로 잠금 가능.",
              bg="#dcfce7", border="#16a34a", text="#14532d")

    _footer(fig, 7, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 8 — 왜 70~80점이 sweet spot 인가 해석 =====
def page_8_why_70_80(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "8. 왜 70-80점이 진짜 sweet spot 인가",
            "사용자 가설 부분 수정 + 해석")

    _band(fig, 0.83, 1, "점수대별 행태 해석 (가설 수준)")
    ax = fig.add_axes([0.04, 0.30, 0.92, 0.52]); ax.axis("off")
    paragraphs = [
        "[ 65~70점 (N=37, D+1 +8.1pp / D+5 -2.7pp) - 약함 ]",
        "    - 강세 신호 임계점 막 통과 단계, 패턴 완성도 낮음",
        "    - D+5 까지 가면 오히려 손절 우위 (-2.7pp) - 단기 추세 짧음",
        "    - 표본 37로 통계 유효성 경계 (N>=30 권장)",
        "",
        "[ 70~80점 (N=273, D+1 +12~17pp / D+5 +8~16pp) - sweet spot ★ ]",
        "    - D0 강세종가 + 얕은 눌림 + 적정 거래대금 모두 충족",
        "    - 점수가 충분히 높아 패턴 완성도 OK, 단 아직 과열 진입 X",
        "    - 다음날 추가 상승 여력 충분 - D+1 ~ D+5 누적 edge 모두 양수",
        "    - 표본 273 (75~80 만 183) - 통계 robust",
        "",
        "[ 80~90점 (N=412, D+1 +3.5~3.8pp / D+5 +4~5pp) - 과열 ]",
        "    - 점수가 매우 높으면 패턴이 이미 완성된 상태 - 차익실현 매물 ↑",
        "    - 다음날 평균적으로 정체 또는 양쪽 비슷 - first-touch 차이 작음",
        "    - 사용자 직감 (\"85+ 점은 과열\") 데이터로 확인됨",
        "",
        "[ 90+ (N=29, D+1 +17.2pp / D+5 +20.7pp) - 작은 표본 다시 강 ]",
        "    - N=29 로 통계 약함 (해석 주의)",
        "    - 극단 점수 = 매우 강세 (도지 / 시초가 갭상승) 일 가능성 - 추가 분석 필요",
    ]
    ax.text(0.0, 0.97, "\n".join(paragraphs), fontsize=10, color="#374151",
            va="top", linespacing=1.6, family="Malgun Gothic")

    _warn_box(fig, 0.06, 0.20,
              "한 줄 결론 + 운영 영향",
              "  '점수가 높을수록 좋다' 가 아님. 70~80점 구간이 '진입 직전 강세' 로 가장 robust.\n"
              "  현재 V2 운영 정책은 'Top3 무조건' 이라 80~90점 과열 종목도 포함됨 - 정상.\n"
              "  사용자 의사결정: 카드의 점수만 보지 말고 '점수대 라벨' (75~85 표준 강세 / 85+ 과열 주의) 같이 보기.",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, 8, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 9 — 14:15 / 15:00 / 17:05 체크 가이드 =====
def page_9_slot_guide(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "9. 14:15 / 15:00 / 17:05 슬롯 체크 가이드",
            "사용자가 사후 확인할 방법")

    _band(fig, 0.83, 1, "오늘 (2026-05-15) 스케줄러 상태 baseline")
    ax = fig.add_axes([0.04, 0.62, 0.92, 0.20]); ax.axis("off")
    rows = [
        ["ClosingBell_Data_Preclose_1415",    "14:15",  "Ready",     "2026-05-14 14:15",  "2026-05-15 14:15"],
        ["ClosingBell_Data_V2Minute_1502",    "15:02",  "Disabled",  "(의도된 비활성)",     "—"],
        ["ClosingBell_Webhook_Preclose_1415", "15:00",  "Ready",     "2026-05-14 15:00",  "2026-05-15 15:00"],
        ["ClosingBell_Data_PostClose_1705",   "17:05",  "Ready",     "2026-05-14 17:05",  "2026-05-15 17:05"],
    ]
    _table(ax,
           ["스케줄러", "시간", "상태", "마지막 실행", "다음 실행"],
           rows, [0.30, 0.10, 0.12, 0.24, 0.24],
           header_color="#bfdbfe", scale=1.85, font_size=10)

    _band(fig, 0.54, 2, "사후 확인 명령 (15:01 / 17:06 이후)")
    ax = fig.add_axes([0.04, 0.34, 0.92, 0.19]); ax.axis("off")
    ax.text(0.0, 0.97,
            "  PowerShell 한 줄로 모든 슬롯 결과 자동 점검:\n"
            "\n"
            "    powershell -ExecutionPolicy Bypass -File `\n"
            "        C:\\Coding\\projects\\bell-dashboard\\scripts\\check_today_slots.ps1\n"
            "\n"
            "  다른 날짜: -Date 2026-05-15 옵션 추가\n"
            "\n"
            "  자동 점검 항목 (색상 표시):\n"
            "    [OK] 빨강 / 초록 - 스케줄러 상태, 산출 파일 존재, manifest 가드, HTTP 200/204",
            fontsize=10, color="#374151", va="top", linespacing=1.7, family="Malgun Gothic")

    _band(fig, 0.27, 3, "각 슬롯 검증 게이트", color="#fef3c7", text_color="#78350f")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.20]); ax.axis("off")
    items = [
        "  14:15 preclose:  V2 Top3 3개 / 중복 X / source_mode=operational / fallback_used=false",
        "  15:00 webhook:   Discord HTTP 200 or 204 / message_length < 1800 / status=sent",
        "  17:05 postclose: 1년 백데이터 갱신 / Phase 0 갱신 / online_v2 target_date=오늘 갱신",
        "",
        "  실패 케이스 처리:",
        "    - HTTP 400 재발 시 (어제 5/14): 즉시 메시지 길이 확인, 늦은 재전송 금지",
        "    - selected_count < 3 시: 강제 채우기 금지, 0~2개로 표시",
        "    - fallback_used=true 시: D0 pool 자체 문제 - 데이터 게이트 재실행",
    ]
    ax.text(0.0, 0.97, "\n".join(items), fontsize=10, color="#78350f",
            va="top", linespacing=1.7, family="Malgun Gothic")

    _footer(fig, 9, total); pdf.savefig(fig); plt.close(fig)


# ===== 페이지 10 — 결론 + 다음 단계 =====
def page_10_conclusion(pdf, total):
    fig = plt.figure(figsize=A4_LANDSCAPE)
    _header(fig, "10. 종합 결론 + 다음 단계",
            "오늘 사용자가 해야 할 일 순서")

    _band(fig, 0.83, 1, "오늘 즉시 가능 (1)")
    ax = fig.add_axes([0.04, 0.55, 0.92, 0.27]); ax.axis("off")
    items = [
        "  ★ 백테스트 1년 데이터 OK / 폴더 구조 OK - 시뮬·연구 진행 가능",
        "  ★ V2 sweet spot 분석 완료 - 70~80점이 진짜 sweet spot (사용자 65~70 가설 부분 수정)",
        "  ★ 슬롯 모니터링 스크립트 완성 - check_today_slots.ps1 한 줄로 사후 자동 점검",
        "  ★ 어제 (5/14) 두 버그 수정 완료 - 메시지 길이 (800자), LG디스플레이 중복",
        "  ★ 오늘 14:15 / 15:00 / 17:05 슬롯 모두 Ready 상태 (Disabled = V2Minute_1502 의도된 OFF)",
    ]
    ax.text(0.0, 0.97, "\n".join(items), fontsize=10.5, color="#14532d",
            va="top", linespacing=1.85, family="Malgun Gothic")

    _band(fig, 0.46, 2, "오늘 14:15 이후 사용자 행동", color="#dcfce7", text_color="#14532d")
    ax = fig.add_axes([0.04, 0.16, 0.92, 0.30]); ax.axis("off")
    actions = [
        "  [ 14:16 ]  스케줄러 자동 실행 - 사용자 행동 없음 (확인만)",
        "",
        "  [ 15:01 ]  PowerShell 열고 한 줄 실행:",
        "             powershell -File C:\\Coding\\projects\\bell-dashboard\\scripts\\check_today_slots.ps1",
        "             - 화면에 초록 [OK] 표시 확인",
        "             - 빨강 [FAIL] 나오면 어떤 게이트인지 확인",
        "",
        "  [ 15:01 ]  Discord 채널 확인 - V2 Top3 Paper Watch 메시지 도착했는지",
        "",
        "  [ 17:10 ]  PowerShell 다시 실행 - 17:05 postclose 결과 확인",
        "             - online_v2 target_date 가 '2026-05-15' 로 갱신됐는지",
        "             - 1년 백데이터 detail 새 mtime 인지",
        "",
        "  [ 다음 ]   대시보드 UI/UX 작업 + 웹훅 추가 정리 진행 가능",
        "             (모든 슬롯 OK 확인 후)",
    ]
    ax.text(0.0, 0.97, "\n".join(actions), fontsize=10.5, color="#14532d",
            va="top", linespacing=1.6, family="Malgun Gothic")

    _warn_box(fig, 0.05, 0.10,
              "한 줄 결론",
              "백테스트 데이터·시뮬·sweet spot 분석·스케줄러·발송 가드 모두 OK. 70-80점 sweet spot 데이터로 확인됨.\n"
              "오늘 15:00 발송 성공만 확인되면 Paper Watch 운영 전환 첫 검증 완료 - 대시보드 UI/UX + 웹훅 polish 진행 가능.",
              bg="#dbeafe", border="#1e3a8a", text="#1e3a8a")

    _footer(fig, total, total); pdf.savefig(fig); plt.close(fig)


# ===== Main =====
def build(out_path: Path):
    df, rank_df, sweet_df, matrix_df = load_data()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 10
    with PdfPages(out_path) as pdf:
        page_1_cover(pdf, total, df)
        page_2_data_status(pdf, total)
        page_3_score_bars(pdf, total, df)
        page_4_score_table(pdf, total, df)
        page_5_rank(pdf, total, rank_df)
        page_6_matrix(pdf, total, matrix_df)
        page_7_sweetspot_groups(pdf, total, sweet_df)
        page_8_why_70_80(pdf, total)
        page_9_slot_guide(pdf, total)
        page_10_conclusion(pdf, total)
    size_kb = out_path.stat().st_size / 1024
    print(f"[ok] {out_path}  ({size_kb:.1f} KB, {total} pages)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path(r"C:\Users\PYJ\Downloads\V2_SWEETSPOT_DATA_AUDIT_SLOT_CHECK_KR_20260515.pdf"))
    args = ap.parse_args()
    build(args.out)
