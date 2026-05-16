"""
V2 Score 차트 검증 결과 PDF 생성기.

지시서 (CLAUDE_CODE_20260513_V2_CHART_REVIEW_UI_PDF_HANDOFF.md §6) 9섹션 구조:
    1. 오늘의 결론
    2. 왜 차트 검증이 필요한가
    3. 승리와 패배를 어떻게 나눴나
    4. 결과 요약표
    5. 승리 차트 대표 (~20)
    6. 패배 차트 대표 (~20)
    7. 이긴 차트의 공통점
    8. 진 차트의 공통점
    9. 다음 점수제 보정 방향

원칙 (§7): 한글 제목 / 큰 글씨 / 표 ≤ 7컬럼 / 차트 한 페이지 2~4개 / 각 차트 한 줄 해석 / 영문 코드는 괄호.
운영 webhook·후보 선정·점수 산식 변경 없음 (표시·해석 전용).
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
from matplotlib import image as mpimg

# Korean font
for tf in (Path(r"C:\Windows\Fonts\malgun.ttf"), Path(r"C:\Windows\Fonts\malgunbd.ttf")):
    if tf.exists():
        font_manager.fontManager.addfont(str(tf))
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(r"C:\Coding")
AUDIT_DIR = ROOT / "data" / "closingbell" / "research_index" / "v2_chart_audit_20260513"
SUMMARY_CSV = AUDIT_DIR / "v2_chart_audit_summary_20260513.csv"
SAMPLES_CSV = AUDIT_DIR / "v2_chart_audit_chart_samples_20260513.csv"

A4_LANDSCAPE = (11.7, 8.3)

ENTRY_BASIS_LABEL = {
    "D0_CLOSE": "D0 종가 진입 (연구 기준)",
    "D1_OPEN": "D+1 시가 진입",
}
PATTERN_LABEL = {
    "STRONG_CLOSE_CONTINUATION": "강세종가 추세 지속",
    "THEME_MOMENTUM": "테마 모멘텀",
    "SHALLOW_PULLBACK_DEFENSE": "얕은 눌림 방어",
    "LOW_UPPER_WICK_CONTINUATION": "짧은 윗꼬리 지속",
    "DEEP_PULLBACK": "깊은 눌림 (실패)",
    "LONG_UPPER_WICK": "긴 윗꼬리 (실패)",
    "GAP_OVERHEAT": "갭 과열 (실패)",
    "D0_CLOSE_WEAK": "D0 종가 약세 (실패)",
    "UNKNOWN": "패턴 미상",
}


def _read(p: Path) -> pd.DataFrame:
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")


def _fmt_pct(value: Any, signed: bool = True) -> str:
    try:
        n = float(value)
    except Exception:
        return "—"
    return f"{n:+.1f}%" if signed else f"{n:.1f}%"


def _section_header(fig, y: float, num: int, title: str) -> None:
    ax = fig.add_axes([0.04, y, 0.92, 0.05]); ax.axis("off")
    ax.text(0.0, 0.5, f"{num}. {title}", fontsize=14, fontweight="bold", color="#1f2937", va="center")
    ax.add_patch(plt.Rectangle((0.0, 0.0), 1.0, 0.06, transform=ax.transAxes,
                               facecolor="#dbeafe", edgecolor="none"))


def _footer(fig) -> None:
    ax = fig.add_axes([0.04, 0.015, 0.92, 0.025]); ax.axis("off")
    ax.text(0.0, 0.5,
            f"V2 차트 검증  ·  Codex audit 2026-05-13  ·  생성 {datetime.now().strftime('%Y-%m-%d %H:%M')}  "
            "·  매수 추천 아님 · 자동매매 아님 · 연구용",
            fontsize=7.5, color="#888", va="center")


def _add_table(ax, header: list[str], rows: list[list[str]], col_widths: list[float],
               header_color: str = "#e8eef7", font_size: int = 9, scale: float = 1.6) -> None:
    if not rows:
        ax.text(0.0, 0.5, "(데이터 없음)", fontsize=10, color="#999"); return
    t = ax.table(cellText=rows, colLabels=header, loc="upper left", cellLoc="left", colWidths=col_widths)
    t.auto_set_font_size(False); t.set_fontsize(font_size); t.scale(1.0, scale)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#cbd5e0")
        if r == 0:
            cell.set_facecolor(header_color); cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#ffffff" if (r - 1) % 2 == 0 else "#f8fafc")


# ===== Pages =====
def page_1_conclusion(pdf: PdfPages, summary: pd.DataFrame) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("V2 점수제 차트 검증 — 결과 보고서", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 1, "오늘의 결론")

    bullets = [
        "이번 V2 점수제 차트 검증은 점수가 뽑은 종목을 ‘사람이 눈으로 본 결과’ 까지 확인한 첫 시도입니다.",
        "최고 승률은 BEST_SCORE_TOP3_PROXY × D0 종가 진입 = 표본 755 / 승률 59.87%. P0 거래대금 Top3 (승률 30.86%) 대비 +29%p.",
        "D1 시가 진입은 모든 variant 에서 D0 종가 진입보다 승률이 평균 15~25%p 낮습니다 — 슬리피지·갭 영향이 큽니다.",
        "win 케이스 공통점: 강세종가 추세 지속 / 테마 모멘텀 / 얕은 눌림 방어. loss 공통점: 깊은 눌림 / 긴 윗꼬리 / 갭 과열.",
        "주의: ‘승률’ 도 백데이터 결과이지 운영 매매 결과가 아닙니다. 슬리피지·호가 공백·체결 불확실성은 별도 보정 필요.",
    ]
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.34]); ax.axis("off")
    ax.text(0.0, 1.0, "\n".join(f"• {line}" for line in bullets),
            fontsize=11, color="#374151", va="top", linespacing=1.85, wrap=True)

    # 핵심 표 — top 3 variants
    if not summary.empty:
        df = summary.copy()
        df["sample_n"] = pd.to_numeric(df["sample_n"], errors="coerce").fillna(0).astype(int)
        df["win_rate_pct"] = pd.to_numeric(df["win_rate_pct"], errors="coerce").fillna(0)
        df["loss_rate_pct"] = pd.to_numeric(df["loss_rate_pct"], errors="coerce").fillna(0)
        df = df.sort_values("win_rate_pct", ascending=False).head(3)
        top_rows = []
        for _, r in df.iterrows():
            top_rows.append([
                str(r.get("selection_name", "")),
                ENTRY_BASIS_LABEL.get(str(r.get("entry_basis", "")), str(r.get("entry_basis", ""))),
                str(r.get("sample_n", "")),
                f"{r['win_rate_pct']:.1f}%",
                f"{r['loss_rate_pct']:.1f}%",
            ])
        ax_t = fig.add_axes([0.04, 0.10, 0.92, 0.32]); ax_t.axis("off")
        ax_t.set_title("최상위 3개 variant", fontsize=11, fontweight="bold", loc="left", pad=8)
        _add_table(ax_t,
                   ["선정 방식", "진입 기준", "표본", "승률", "패배율"],
                   top_rows,
                   [0.30, 0.30, 0.12, 0.14, 0.14],
                   header_color="#dcfce7", scale=1.9)
    _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_2_why(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("왜 차트 검증이 필요한가", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 2, "왜 차트 검증이 필요한가")
    paras = [
        "지금까지의 분석은 ‘5일 안에 +3% 한 번이라도 닿았나(도달률)’ 같은 숫자 위주였습니다.",
        "하지만 도달률(touch rate)은 ‘승률’이 아닙니다. 변동성이 큰 종목은 한 번씩 위아래로 다 닿고 결국 손실로 끝날 수 있습니다.",
        "따라서 점수가 높은 종목이 실제로 ‘이긴 차트 모양’인지 ‘진 차트 모양’인지 사람이 눈으로 확인할 필요가 있었습니다.",
        "이번 검증은 점수 기반 후보 (V2) 와 기존 거래대금 기반 후보 (P0) 의 win/loss 차트 패턴을 비교한 첫 단계입니다.",
        "결과는 모두 백데이터 기준이며, 운영 신호나 매수 지시가 아닙니다.",
    ]
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.64]); ax.axis("off")
    ax.text(0.0, 1.0, "\n\n".join(paras), fontsize=11.5, color="#374151", va="top", linespacing=1.7, wrap=True)
    _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_3_definition(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("승리와 패배를 어떻게 나눴나", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 3, "승리와 패배를 어떻게 나눴나")

    rows = [
        ["승리 (win)", "5일 안에 +3% 목표가가 -2% 손절선보다 먼저 도달", "선후관계 ‘목표 우선’ — 백데이터 기준"],
        ["패배 (loss)", "5일 안에 -2% 손절선이 +3% 목표가보다 먼저 도달", "선후관계 ‘손절 우선’"],
        ["애매 (unknown)", "같은 날에 +3 과 -2 가 같이 발생 또는 둘 다 도달 안 함", "일봉만으로 선후관계 확정 불가"],
    ]
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.34]); ax.axis("off")
    _add_table(ax, ["분류", "정의", "주의"], rows, [0.18, 0.45, 0.37],
               header_color="#fef3c7", scale=2.0)

    paras = [
        "용어 풀이:",
        "  • 최초 거래대금 폭발일(D0) — 큰 거래대금이 발생한 첫 날. 매수 신호 아니라 ‘감시 시작 신호’.",
        "  • 5일 안 최고수익률(MFE, Maximum Favorable Excursion) — D0 또는 D+1 진입가 대비 5일 안에 도달한 최대 상승률.",
        "  • 5일 안 최대하락률(MAE, Maximum Adverse Excursion) — 같은 기간 최대 하락률.",
        "  • 목표가가 손절보다 먼저 발생 (target-before-risk) — +3% 가 -2% 보다 먼저 닿은 경우.",
        "진입 기준 두 가지:",
        "  • D0 종가 진입 — 연구용 기준 (장 끝에 진입했다고 가정).",
        "  • D+1 시가 진입 — 실거래에 가까운 가정. 단, 슬리피지와 호가 공백은 아직 별도 보정 미반영.",
    ]
    ax2 = fig.add_axes([0.04, 0.10, 0.92, 0.36]); ax2.axis("off")
    ax2.text(0.0, 1.0, "\n".join(paras), fontsize=10.5, color="#374151", va="top", linespacing=1.65)
    _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_4_summary(pdf: PdfPages, summary: pd.DataFrame) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("결과 요약표 — 12개 variant × 진입 기준", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 4, "결과 요약표")

    if summary.empty:
        ax = fig.add_axes([0.04, 0.4, 0.92, 0.4]); ax.axis("off")
        ax.text(0.0, 0.5, "summary CSV 없음", fontsize=11, color="#999")
        _footer(fig); pdf.savefig(fig); plt.close(fig); return

    df = summary.copy()
    for col in ("sample_n", "win_n", "loss_n", "unknown_n"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in ("win_rate_pct", "loss_rate_pct"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df = df.sort_values("win_rate_pct", ascending=False)

    rows = []
    for _, r in df.iterrows():
        rows.append([
            str(r.get("selection_name", "")),
            ENTRY_BASIS_LABEL.get(str(r.get("entry_basis", "")), str(r.get("entry_basis", ""))),
            str(r["sample_n"]),
            f"{r['win_rate_pct']:.1f}%",
            f"{r['loss_rate_pct']:.1f}%",
            str(r.get("median_score", "")),
            PATTERN_LABEL.get(str(r.get("top_success_pattern", "")), str(r.get("top_success_pattern", "")))[:20],
        ])
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.72]); ax.axis("off")
    _add_table(ax,
               ["선정 방식", "진입 기준", "표본", "승률", "패배율", "중앙 점수", "주요 성공 패턴"],
               rows,
               [0.22, 0.22, 0.08, 0.10, 0.10, 0.10, 0.18],
               header_color="#dcfce7", scale=1.6, font_size=8.5)
    _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_charts(pdf: PdfPages, samples: pd.DataFrame, group: str, section_num: int, title: str,
                header_color: str = "#dcfce7", charts_per_page: int = 4) -> None:
    """승리/패배 차트 페이지 — 한 페이지에 charts_per_page 개 (2x2 grid).
    이미지 + 메타 1줄 + 한 줄 해석."""
    rows = samples[samples["result_group"] == group].sort_values(
        ["selection_name", "entry_basis", "signal_date"]
    ).reset_index(drop=True)
    if rows.empty:
        return

    n_pages = (len(rows) + charts_per_page - 1) // charts_per_page
    for page_idx in range(n_pages):
        fig = plt.figure(figsize=A4_LANDSCAPE)
        fig.suptitle(f"{title} ({page_idx + 1}/{n_pages})", fontsize=14, fontweight="bold", y=0.97)
        _section_header(fig, 0.89, section_num, title)

        chunk = rows.iloc[page_idx * charts_per_page:(page_idx + 1) * charts_per_page]
        # 2x2 grid
        positions = [
            (0.04, 0.46, 0.46, 0.40),
            (0.52, 0.46, 0.46, 0.40),
            (0.04, 0.06, 0.46, 0.40),
            (0.52, 0.06, 0.46, 0.40),
        ]
        for i, (_, r) in enumerate(chunk.iterrows()):
            if i >= len(positions): break
            x, y, w, h = positions[i]
            # image area
            ax_img = fig.add_axes([x, y + 0.10, w, h - 0.13])
            ax_img.axis("off")
            path = str(r.get("chart_path", ""))
            if Path(path).exists():
                try:
                    img = mpimg.imread(path)
                    ax_img.imshow(img)
                except Exception:
                    ax_img.text(0.5, 0.5, "이미지 로드 실패", ha="center", va="center", fontsize=9, color="#999")
            else:
                ax_img.text(0.5, 0.5, "이미지 없음", ha="center", va="center", fontsize=9, color="#999")

            # meta + note
            ax_meta = fig.add_axes([x, y, w, 0.10])
            ax_meta.axis("off")
            try:
                mfe = float(r.get("mfe_5d_pct", "0") or 0)
                mae = float(r.get("mae_5d_pct", "0") or 0)
                metric_text = f"5일 최고 {mfe:+.1f}% / 최저 {mae:+.1f}%"
            except Exception:
                metric_text = "MFE/MAE —"
            pattern_ko = PATTERN_LABEL.get(str(r.get("pattern_label", "")), str(r.get("pattern_label", "")))
            entry_ko = ENTRY_BASIS_LABEL.get(str(r.get("entry_basis", "")), str(r.get("entry_basis", "")))
            sel = str(r.get("selection_name", ""))
            head = f"{r.get('stock_name', '')} ({r.get('stock_code', '')})  ·  점수 {r.get('score_total_100', '')}  ·  {entry_ko}"
            sub = f"선정 {sel}  ·  {metric_text}  ·  패턴: {pattern_ko}"
            note = str(r.get("notes", ""))
            ax_meta.text(0.0, 0.95, head, fontsize=9, fontweight="bold", color="#1f2937", va="top")
            ax_meta.text(0.0, 0.55, sub, fontsize=8, color="#374151", va="top")
            ax_meta.text(0.0, 0.18, f"해석: {note}", fontsize=8, color="#6b7280", va="top", style="italic")

        _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_8_win_patterns(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("이긴 차트의 공통점", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 7, "이긴 차트의 공통점")

    rows = [
        ["강세종가 추세 지속", "STRONG_CLOSE_CONTINUATION",
         "종가가 일중 상단에 가깝게 마감 · 윗꼬리 짧음 · 다음날 갭상승 후 추세 유지"],
        ["테마 모멘텀", "THEME_MOMENTUM",
         "같은 시점에 유사 종목 동반 상승 · 매수세 지속 · 거래량 감소해도 가격 방어"],
        ["얕은 눌림 방어", "SHALLOW_PULLBACK_DEFENSE",
         "D+1에 -2% 가까이 눌리지만 곧바로 회복 · 매수세 지지선 형성"],
        ["짧은 윗꼬리 지속", "LOW_UPPER_WICK_CONTINUATION",
         "D0 윗꼬리 짧고 종가 강함 · 다음날 가격 흐름 안정"],
    ]
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.64]); ax.axis("off")
    _add_table(ax, ["한글 라벨", "원본 코드", "관찰된 공통점"], rows, [0.22, 0.30, 0.48],
               header_color="#dcfce7", scale=2.2)
    _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_9_loss_patterns(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("진 차트의 공통점", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 8, "진 차트의 공통점")

    rows = [
        ["깊은 눌림", "DEEP_PULLBACK",
         "D+1~D+3 중 -5% 이상 하락 · 매수세 약화 · MAE > 5%"],
        ["긴 윗꼬리", "LONG_UPPER_WICK",
         "D0 윗꼬리 길어 매도세 강함 · D+1 갭하락 · 종가 약함"],
        ["갭 과열", "GAP_OVERHEAT",
         "D+1 시가가 D0 종가 대비 크게 갭상승 → 곧바로 매도세 → -2% 빠르게 터치"],
        ["D0 종가 약세", "D0_CLOSE_WEAK",
         "거래대금은 컸지만 종가가 일중 하단 마감 → 약한 매수세 · 다음날 추세 끊김"],
    ]
    ax = fig.add_axes([0.04, 0.20, 0.92, 0.64]); ax.axis("off")
    _add_table(ax, ["한글 라벨", "원본 코드", "관찰된 공통점"], rows, [0.22, 0.30, 0.48],
               header_color="#fee2e2", scale=2.2)
    _footer(fig); pdf.savefig(fig); plt.close(fig)


def page_10_next(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=A4_LANDSCAPE)
    fig.suptitle("다음 점수제 보정 방향", fontsize=16, fontweight="bold", y=0.965)
    _section_header(fig, 0.86, 9, "다음 점수제 보정 방향 (Codex 영역)")

    sections = [
        ("점수 가중치 검토", [
            "짧은 윗꼬리 + 강한 종가 = 가산점 (일부 variant 반영, 확정 검토).",
            "깊은 눌림 / 긴 윗꼬리 / 갭 과열 = 감점 (현재 일부 감점 반영).",
            "pullback 깊이 정량화 (pullback_depth_pct) — 깊은 눌림 변환 임계 정의 필요.",
        ]),
        ("진입 기준", [
            "D0 종가 진입 vs D+1 시가 진입 — 모든 variant 에서 D+1 시가 진입이 평균 15~25%p 승률 하락.",
            "→ 운영 적용 시에는 슬리피지·호가 공백·체결 불확실성을 더한 D+1 시가 보정 모델 필요.",
            "현재 단계에서는 D0 종가 = 연구 기준선, D+1 시가 = 보수적 참고치.",
        ]),
        ("robust 검증", [
            "단일 variant 채택은 과최적화 위험. 4,566 variant 중앙값 + 상위권 공통 구조 확인 후 운영 전환.",
            "‘얕은눌림 paper watch (S10)’ 와 ‘pullback 단독 (ONLY_PULLBACK)’ 이 robust 후보군.",
            "Pullback Reclaim 트리거형 (D+1~D+3 회복 확인) 과 결합한 두 단계 필터 검토.",
        ]),
        ("운영 경계선 (변경 금지)", [
            "현재 LIVE 웹훅은 P0 거래대금 기준 유지. V2 는 Shadow / 연구용.",
            "후보 선정 / 점수 산식 / D0 조건 / 웹훅 발송 로직 — 변경 시 Codex + 사용자 승인.",
            "주문 / 계좌 API / 자동매매 / 실거래 자동주문 — 일절 사용 안 함.",
        ]),
    ]
    y = 0.79
    for title, bullets in sections:
        ax_t = fig.add_axes([0.04, y - 0.035, 0.92, 0.035]); ax_t.axis("off")
        ax_t.text(0.0, 0.5, title, fontsize=12, fontweight="bold", color="#1f2937", va="center")
        height = 0.02 + 0.040 * len(bullets)
        ax_b = fig.add_axes([0.04, y - 0.035 - height, 0.92, height]); ax_b.axis("off")
        ax_b.text(0.0, 1.0, "\n".join(f"  •  {line}" for line in bullets),
                  fontsize=10.5, color="#374151", va="top", linespacing=1.7, wrap=True)
        y -= (0.035 + height + 0.010)

    _footer(fig); pdf.savefig(fig); plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=r"C:\Users\PYJ\Downloads\V2_SCORE_CHART_AUDIT_REPORT_20260513.pdf")
    parser.add_argument("--charts-per-page", type=int, default=4, choices=[2, 4],
                        help="승리/패배 페이지당 차트 수")
    args = parser.parse_args()

    summary = _read(SUMMARY_CSV)
    samples = _read(SAMPLES_CSV)
    if summary.empty and samples.empty:
        print(f"[err] no audit data at {AUDIT_DIR}")
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        page_1_conclusion(pdf, summary)
        page_2_why(pdf)
        page_3_definition(pdf)
        page_4_summary(pdf, summary)
        page_charts(pdf, samples, "win", 5, "승리 차트 대표",
                    header_color="#dcfce7", charts_per_page=args.charts_per_page)
        page_charts(pdf, samples, "loss", 6, "패배 차트 대표",
                    header_color="#fee2e2", charts_per_page=args.charts_per_page)
        page_8_win_patterns(pdf)
        page_9_loss_patterns(pdf)
        page_10_next(pdf)
    print(f"PDF saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
