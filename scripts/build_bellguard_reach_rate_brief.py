"""BellGuard 1년 도달률 브리프 PDF — 짧고 가독성 좋은 정리본.

내용 출처: bellguard_pricecap_1y/bellguard_pricecap_manifest.json (100k variant, 메인)
구성: 표지 → 한눈에 → 도달률(상/하) → 먼저 도달 → 평균 진폭 → 도달률≠승률 → 결론 (7 슬라이드)

manifest 의 summary_kpi 를 읽어 그대로 표시하므로, 데이터셋이 바뀌면 PDF 도 자동 반영.

usage:
    & C:\\Coding\\projects\\_venvs\\closingbell-py312\\Scripts\\python.exe \\
      C:\\Coding\\projects\\bell-dashboard\\scripts\\build_bellguard_reach_rate_brief.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

REPO = Path(__file__).resolve().parents[1]
LATEST = REPO / "data" / "closingbell" / "online_v2" / "latest"
MANIFEST = LATEST / "bellguard_pricecap_1y" / "bellguard_pricecap_manifest.json"
OUT_PATH = LATEST / f"CLOSINGBELL_BELLGUARD_REACH_RATE_BRIEF_{datetime.now():%Y%m%d}.pdf"

plt.rcParams["font.family"] = ["Malgun Gothic", "Apple SD Gothic Neo", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42

BG = "#ffffff"
INK = "#0f172a"
MUTED = "#64748b"
BRAND = "#16a34a"
BRAND_DARK = "#15803d"
BRAND_BG = "#ecfdf5"
BRAND_EDGE = "#bbf7d0"
WARN = "#f97316"
WARN_BG = "#fff7ed"
WARN_EDGE = "#fed7aa"
DANGER = "#dc2626"
DANGER_BG = "#fef2f2"
DANGER_EDGE = "#fecaca"
ACCENT = "#2563eb"
ACCENT_BG = "#f0f9ff"
ACCENT_EDGE = "#bae6fd"
LINE = "#e5e7eb"
SOFT_BG = "#f8fafc"

PAGE_W, PAGE_H = 13.33, 7.5  # 16:9


# ────── 헬퍼 ──────


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
            "ClosingBell · 벨가드 1년 도달률 브리프 · 매수 추천 아님 · 자동매매 아님",
            color=MUTED, fontsize=8.5, ha="left", va="center")
    ax.text(0.96, 0.035, f"{slide_no} / {total}    {title}",
            color=MUTED, fontsize=8.5, ha="right", va="center")


def _title_top(ax, kicker, title, kicker_color=BRAND):
    ax.text(0.05, 0.91, kicker, color=kicker_color, fontsize=13, fontweight="bold", ha="left", va="center")
    ax.text(0.05, 0.83, title, color=INK, fontsize=32, fontweight="bold",
            ha="left", va="center", linespacing=1.15)
    ax.add_patch(Rectangle((0.05, 0.78), 0.08, 0.006, facecolor=kicker_color, edgecolor="none"))


def _card(ax, x, y, w, h, *, color="#ffffff", edge=LINE, radius=0.018):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.002,rounding_size={radius}",
        facecolor=color, edgecolor=edge, linewidth=1.2,
    ))


def _hbar(ax, x, y, w, value_pct, *, color, track="#f1f5f9", height=0.026):
    full = w
    fill = full * (value_pct / 100.0)
    ax.add_patch(Rectangle((x, y), full, height, facecolor=track, edgecolor="none"))
    ax.add_patch(Rectangle((x, y), fill, height, facecolor=color, edgecolor="none"))


# ────── manifest 로딩 ──────


def load_kpi() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"manifest 없음: {MANIFEST}")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    main_key = data.get("main_variant", "100k")
    main_kpi: dict = {}
    for v in data.get("summary_kpi", []):
        if v.get("variant") == main_key:
            main_kpi = v
            break
    return {
        "dataset_name": data.get("dataset_name", "—"),
        "generated_at": data.get("generated_at", "—"),
        "main_key": main_key,
        "kpi": main_kpi,
        "all_variants": data.get("summary_kpi", []),
    }


# ────── 슬라이드 ──────


def slide_01_cover(no, total, info):
    fig, ax = _new_slide()
    ax.text(0.05, 0.86, "CLOSINGBELL · BELLGUARD", color=BRAND, fontsize=14, fontweight="bold")
    ax.text(0.05, 0.59,
            "벨가드 1년 도달률\n한눈에 보기",
            color=INK, fontsize=52, fontweight="bold", va="center", linespacing=1.10)
    n = info["kpi"].get("sample_n", "—")
    days = info["kpi"].get("days_with_pick", "—")
    ax.text(0.05, 0.32,
            f"표본 {n}건 · 250 거래일 추적 결과\n"
            f"D0 Strict (3일 active D0 풀) + 가격필터 100,000원 이하",
            color=MUTED, fontsize=17, va="top", linespacing=1.55)
    _card(ax, 0.05, 0.10, 0.62, 0.09, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.145, "Paper Watch · 매수 추천 아님 · 도달률 ≠ 승률",
            color=BRAND_DARK, fontsize=12, fontweight="bold", va="center")
    ax.add_patch(Rectangle((0.83, 0.10), 0.005, 0.78, facecolor=BRAND, edgecolor="none"))
    ax.text(0.86, 0.49, f"{datetime.now():%Y-%m-%d}", color=MUTED, fontsize=14, va="center")
    _footer(ax, no, total, "표지")
    return fig


def slide_02_one_glance(no, total, info):
    fig, ax = _new_slide()
    _title_top(ax, "한 줄로 요약", "위로는 잘 가지만,\n위가 먼저 갈 확률은 절반 미만.")
    k = info["kpi"]
    # 3 큰 카드
    items = [
        ("위 도달률 (5일 안)", f"{k.get('plus3_touch_rate', 0):.1f}%", "+3% 한 번이라도 닿는 비율", BRAND, BRAND_BG, BRAND_EDGE),
        ("위가 먼저 도달", f"{k.get('plus3_first_rate', 0):.1f}%", "+3을 -3보다 먼저 닿는 비율", ACCENT, ACCENT_BG, ACCENT_EDGE),
        ("아래 도달률 (5일 안)", f"{k.get('minus3_touch_rate', 0):.1f}%", "-3% 한 번이라도 닿는 비율", WARN, WARN_BG, WARN_EDGE),
    ]
    for i, (h, v, sub, c, bg, eg) in enumerate(items):
        x = 0.05 + i * 0.31
        _card(ax, x, 0.30, 0.28, 0.36, color=bg, edge=eg)
        ax.text(x + 0.02, 0.62, h, color=INK, fontsize=13, fontweight="bold", va="top")
        ax.text(x + 0.02, 0.50, v, color=c, fontsize=44, fontweight="bold", va="center")
        ax.text(x + 0.02, 0.36, sub, color=MUTED, fontsize=12, va="top", linespacing=1.55)
    # 하단 풀어쓰기
    _card(ax, 0.05, 0.13, 0.90, 0.13, color=SOFT_BG)
    ax.text(0.07, 0.22, "핵심", color=INK, fontsize=11, fontweight="bold")
    ax.text(0.07, 0.17,
            "5일 안에 +3% 위로 한 번은 거의 다 닿지만, “먼저” 닿는 건 절반이 안 됩니다.\n"
            "“도달했다 = 그 가격에 팔았다”가 아니므로, 손절 위치를 먼저 정하는 것이 중요합니다.",
            color=INK, fontsize=14, va="top", linespacing=1.6)
    _footer(ax, no, total, "1 · 한 줄 요약")
    return fig


def slide_03_touch_table(no, total, info):
    fig, ax = _new_slide()
    _title_top(ax, "도달률 — 위 / 아래 짝지어", "5일 안에 한 번이라도 닿는 비율 (높을수록 강한 변동)", kicker_color=INK)
    k = info["kpi"]
    rows = [
        ("+1% / -1%", k.get("plus1_touch_rate"), k.get("minus1_touch_rate")),
        ("+2% / -2%", k.get("plus2_touch_rate"), k.get("minus2_touch_rate")),
        ("+3% / -3%", k.get("plus3_touch_rate"), k.get("minus3_touch_rate")),
        ("+5% / -5%", k.get("plus5_touch_rate"), k.get("minus5_touch_rate")),
    ]
    # 표 영역
    y_top = 0.70
    row_h = 0.115
    bar_x = 0.30
    bar_w = 0.27
    label_w = 0.20
    for i, (label, up, dn) in enumerate(rows):
        y = y_top - i * row_h
        # 라벨
        ax.text(0.06, y, label, color=INK, fontsize=18, fontweight="bold", va="center")
        # 위 막대
        ax.text(bar_x - 0.005, y + 0.025, "위", color=BRAND, fontsize=10, fontweight="bold", ha="right", va="center")
        _hbar(ax, bar_x, y + 0.015, bar_w, up or 0, color=BRAND, height=0.022)
        ax.text(bar_x + bar_w + 0.01, y + 0.026, f"{up or 0:.1f}%", color=BRAND, fontsize=13, fontweight="bold", va="center")
        # 아래 막대
        ax.text(bar_x - 0.005, y - 0.005, "아래", color=WARN, fontsize=10, fontweight="bold", ha="right", va="center")
        _hbar(ax, bar_x, y - 0.015, bar_w, dn or 0, color=WARN, height=0.022)
        ax.text(bar_x + bar_w + 0.01, y - 0.004, f"{dn or 0:.1f}%", color=WARN, fontsize=13, fontweight="bold", va="center")
        # 차이
        diff = (up or 0) - (dn or 0)
        diff_color = BRAND if diff > 0 else WARN
        ax.text(0.85, y + 0.011, f"위 - 아래 = +{diff:.1f}%p", color=diff_color, fontsize=12, fontweight="bold", va="center")
    # 하단 해석
    _card(ax, 0.05, 0.10, 0.90, 0.08, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.5, 0.135,
            "기준이 클수록(±5%) 위 - 아래 격차가 커집니다. 위쪽 변동이 더 크다는 의미입니다.",
            color=INK, fontsize=13, fontweight="bold", ha="center", va="center")
    _footer(ax, no, total, "2 · 도달률")
    return fig


def slide_04_first(no, total, info):
    fig, ax = _new_slide()
    _title_top(ax, "위가 먼저 도달 vs 아래가 먼저 도달", "“도달했다 = 가져갔다” 가 아닙니다.\n어느 쪽이 먼저 닿느냐가 손익을 정합니다.", kicker_color=INK)
    k = info["kpi"]
    p3f = k.get("plus3_first_rate", 0)
    m3f = k.get("minus3_first_rate", 0)
    neutral = max(0, 100 - p3f - m3f)
    # 좌: +3 먼저 큰 카드
    _card(ax, 0.05, 0.20, 0.43, 0.46, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.59, "+3% 가 먼저 도달", color=BRAND_DARK, fontsize=14, fontweight="bold")
    ax.text(0.07, 0.50, f"{p3f:.1f}%", color=BRAND, fontsize=66, fontweight="bold", va="center")
    _hbar(ax, 0.07, 0.34, 0.39, p3f, color=BRAND, height=0.02, track="#dcfce7")
    ax.text(0.07, 0.27,
            f"5일 안에 +3%를 -3%보다 먼저 닿는 비율.\n다섯 중 약 {p3f / 20:.1f}개꼴.",
            color=INK, fontsize=13, va="top", linespacing=1.55)
    # 우: -3 먼저 카드
    _card(ax, 0.52, 0.20, 0.43, 0.46)
    ax.text(0.54, 0.59, "-3% 가 먼저 도달", color=WARN, fontsize=14, fontweight="bold")
    ax.text(0.54, 0.50, f"{m3f:.1f}%", color=WARN, fontsize=66, fontweight="bold", va="center")
    _hbar(ax, 0.54, 0.34, 0.39, m3f, color=WARN, height=0.02)
    ax.text(0.54, 0.27,
            f"5일 안에 -3%를 +3%보다 먼저 닿는 비율.\n손절 먼저 맞을 확률.",
            color=INK, fontsize=13, va="top", linespacing=1.55)
    # 하단: 둘 다 아님
    _card(ax, 0.05, 0.10, 0.90, 0.08, color=SOFT_BG)
    ax.text(0.5, 0.135,
            f"위·아래 어느 쪽도 먼저 닿지 않거나 같은 날 도달: 약 {neutral:.1f}%  ·  "
            f"위 - 아래 = +{p3f - m3f:.1f}%p (약간 유리)",
            color=INK, fontsize=12.5, fontweight="bold", ha="center", va="center")
    _footer(ax, no, total, "3 · 먼저 도달")
    return fig


def slide_05_amplitude(no, total, info):
    fig, ax = _new_slide()
    _title_top(ax, "평균 진폭", "5일 동안 가장 많이 올랐던 폭과\n가장 많이 떨어졌던 폭의 평균.", kicker_color=INK)
    k = info["kpi"]
    gain = k.get("avg_max_gain", 0)
    loss = k.get("avg_max_loss", 0)
    # 양옆 큰 숫자
    _card(ax, 0.05, 0.20, 0.43, 0.46, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.59, "평균 최대 상승 (D+1~D+5)", color=BRAND_DARK, fontsize=14, fontweight="bold")
    ax.text(0.07, 0.49, f"+{gain:.1f}%", color=BRAND, fontsize=64, fontweight="bold", va="center")
    ax.text(0.07, 0.32,
            "후보가 5일 안에 닿았던 “가장 높은 가격” 평균.\n실제 매도 가격이 아닌 상한선 참고치.",
            color=INK, fontsize=13, va="top", linespacing=1.55)
    _card(ax, 0.52, 0.20, 0.43, 0.46, color=DANGER_BG, edge=DANGER_EDGE)
    ax.text(0.54, 0.59, "평균 최대 하락 (D+1~D+5)", color=DANGER, fontsize=14, fontweight="bold")
    sign = "+" if loss > 0 else ""
    ax.text(0.54, 0.49, f"{sign}{loss:.1f}%", color=DANGER if loss < 0 else BRAND,
            fontsize=64, fontweight="bold", va="center")
    ax.text(0.54, 0.32,
            "후보가 5일 안에 닿았던 “가장 낮은 가격” 평균.\n"
            f"양수면 대부분 진입가 위에서 놀았다는 뜻 (단, -3 도달 {k.get('minus3_touch_rate', 0):.0f}%는 별개).",
            color=INK, fontsize=13, va="top", linespacing=1.55)
    _card(ax, 0.05, 0.10, 0.90, 0.08, color=SOFT_BG)
    ax.text(0.5, 0.135,
            "변동성이 크다는 신호. 위·아래 모두 큰 폭이 나오므로 손절·익절 위치를 사전에 정해야 합니다.",
            color=INK, fontsize=13, fontweight="bold", ha="center", va="center")
    _footer(ax, no, total, "4 · 평균 진폭")
    return fig


def slide_06_caution(no, total, info):
    fig, ax = _new_slide()
    _title_top(ax, "주의 — 도달률 ≠ 승률", "5일 안에 한 번이라도 닿는 비율과\n실제 그 가격에 매도했는지는 다릅니다.", kicker_color=DANGER)
    _card(ax, 0.05, 0.34, 0.90, 0.34, color=DANGER_BG, edge=DANGER_EDGE)
    ax.text(0.07, 0.64, "왜 “닿았다”와 “벌었다”가 다른가", color=DANGER, fontsize=13, fontweight="bold")
    notes = [
        "• 도달률은 “5일 안에 그 가격을 단 한 번이라도 찍은 비율”입니다.",
        "• 찍자마자 다시 떨어졌을 수 있고, 실제 매도 가격은 시점과 슬리피지에 따라 달라집니다.",
        "• -3% 한 번이라도 닿은 비율이 70%대인데, 손절을 안 걸어두면 그 자리에서 멈추지 않습니다.",
        "• 그래서 “위 먼저 / 아래 먼저” 비율과 손절·익절 위치가 도달률보다 중요합니다.",
    ]
    for i, n in enumerate(notes):
        ax.text(0.07, 0.56 - i * 0.055, n, color=INK, fontsize=14, va="top")
    # 보는 법 카드
    _card(ax, 0.05, 0.12, 0.90, 0.18)
    ax.text(0.07, 0.27, "이렇게 보세요", color=INK, fontsize=12, fontweight="bold")
    ax.text(0.07, 0.22,
            "1) 도달률로는 “이 정도 변동이 가능한 후보군이구나” 만 확인.\n"
            "2) 위 먼저 / 아래 먼저 비율로 “실제 손익 방향”을 가늠.\n"
            "3) 차트와 호가로 직접 확인 후 손절 위치 먼저 정함.",
            color=MUTED, fontsize=12.5, va="top", linespacing=1.7)
    _footer(ax, no, total, "5 · 주의")
    return fig


def slide_07_closing(no, total, info):
    fig, ax = _new_slide()
    ax.text(0.05, 0.86, "한 줄 결론", color=BRAND, fontsize=14, fontweight="bold")
    k = info["kpi"]
    ax.text(0.05, 0.58,
            f"위 +3 도달 {k.get('plus3_touch_rate', 0):.1f}% — 변동성은 충분히 큼.\n"
            f"위가 먼저 갈 확률 {k.get('plus3_first_rate', 0):.1f}% — 동전 던지기에 약간 유리.",
            color=INK, fontsize=36, fontweight="bold", va="center", linespacing=1.25)
    ax.text(0.05, 0.32,
            "“위로 가능성이 높다”가 아니라 “위·아래 둘 다 큰 후보군”입니다.\n"
            "도달률 자체보다 손절·익절 위치와 차트 확인이 우선입니다.",
            color=MUTED, fontsize=16, va="top", linespacing=1.6)
    _card(ax, 0.05, 0.10, 0.90, 0.14, color=BRAND_BG, edge=BRAND_EDGE)
    ax.text(0.07, 0.21, "다음 행동", color=BRAND_DARK, fontsize=11, fontweight="bold")
    ax.text(0.07, 0.155,
            "차트를 본 뒤 손절 위치 먼저 정하고, 사전 느낌을 메모로 남기세요.",
            color=INK, fontsize=15, fontweight="bold", va="center")
    _footer(ax, no, total, "6 · 결론")
    return fig


# ────── 빌드 ──────


def build_pdf(out_path: Path = OUT_PATH) -> Path:
    info = load_kpi()
    builders = [
        slide_01_cover,
        slide_02_one_glance,
        slide_03_touch_table,
        slide_04_first,
        slide_05_amplitude,
        slide_06_caution,
        slide_07_closing,
    ]
    total = len(builders)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(out_path) as pdf:
        for i, builder in enumerate(builders, start=1):
            fig = builder(i, total, info)
            pdf.savefig(fig, facecolor=BG, bbox_inches="tight", pad_inches=0.0)
            plt.close(fig)
        meta = pdf.infodict()
        meta["Title"] = "ClosingBell · 벨가드 1년 도달률 브리프"
        meta["Subject"] = "+2/+3/-2/-3 도달률, 먼저 도달, 평균 진폭"
        meta["Keywords"] = "ClosingBell, BellGuard, 도달률, paper watch"
        meta["CreationDate"] = datetime.now()
    return out_path


if __name__ == "__main__":
    out = build_pdf()
    print(f"PDF saved: {out}")
    print(f"size: {out.stat().st_size / 1024:.0f} KB")
