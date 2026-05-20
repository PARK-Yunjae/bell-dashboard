"""Bell 파이프라인 시간대별 Health Check.

ChatGPT 피드백 2 §4 / BELLGUARD_D0_STRICT_FEEDBACK §7~10 반영.

슬롯:
    1415       14:15 데이터 수집 점검 (D0 candidates, intraday snapshot)
    1500       15:00 V2/벨가드 산출 + 웹훅 발송 점검 (preview/sent log)
    postclose  17:05 장마감 데이터 갱신 점검 (일봉/분봉/수급/DART, overwrite)
    publish    online_v2/latest 갱신 + git status 점검
    all        위 4개 순차 실행 + 종합 보고

usage:
    python scripts/check_bell_pipeline_health.py --slot 1500
    python scripts/check_bell_pipeline_health.py --slot all
    python scripts/check_bell_pipeline_health.py --slot postclose --date 2026-05-15

출력:
    C:\\Coding\\data\\closingbell\\health\\health_{slot}_YYYYMMDD.json
    C:\\Coding\\data\\closingbell\\health\\health_{slot}_YYYYMMDD.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

# 경로
HEALTH_DIR = Path(r"C:\Coding\data\closingbell\health")
CLOSINGBELL = Path(r"C:\Coding\data\closingbell")
MARKET = Path(r"C:\Coding\data\market")
DART = Path(r"C:\Coding\data\dart")
REPO = Path(r"C:\Coding\projects\bell-dashboard")
ONLINE_V2_LATEST = REPO / "data" / "closingbell" / "online_v2" / "latest"
SHARED = CLOSINGBELL / "shared"

SLOT_TITLES = {
    "1415": "14:15 데이터 수집",
    "1500": "15:00 후보 산출 + 웹훅 발송",
    "postclose": "17:05 장마감 데이터 갱신",
    "publish": "online_v2 + GitHub 갱신",
}


# ──────────── 유틸 ────────────


def _last_trading_day(today: date | None = None) -> date:
    """직전 거래일 추정 — 주말 휴장 + 기본 공휴일 보정.

    한국 시장 정확한 캘린더는 KRX API/exchange-calendars 필요. 여기서는 보수적:
    토 → 금, 일 → 금, 그 외 → 어제. (실제 공휴일 보정은 별도 캘린더 필요)
    """
    today = today or date.today()
    d = today
    # 오늘이 평일이면 오늘 자체가 거래일 후보 (오전 점검 시 어제로)
    # 점검 목적이므로 "직전에 정상 끝난 거래일" 의미.
    # 토/일이면 직전 금요일까지 거슬러 올라감.
    while d.weekday() >= 5:  # 5=토, 6=일
        d -= timedelta(days=1)
    return d


def fresh_age(path: Path, *, trading_day_aware: bool = True) -> tuple[bool, str]:
    """파일 신선도.
    trading_day_aware=True (기본): 직전 거래일 이후에 갱신됐으면 신선으로 판정.
        주말이면 금요일 17시 이후 갱신만 신선. 평일은 어제 17시 이후 신선.
    trading_day_aware=False: 단순 24시간 이내.
    """
    if not path.exists():
        return False, "없음"
    mtime_dt = datetime.fromtimestamp(path.stat().st_mtime)
    now_dt = datetime.now()
    age_sec = (now_dt - mtime_dt).total_seconds()
    h = age_sec / 3600
    if trading_day_aware:
        # 직전 완료 거래일 17:00 이후에 갱신됐으면 신선 (PostClose 슬롯 기준).
        # 평일 17:00 전 점검은 아직 당일 postclose 전이므로 전 거래일을 기준으로 삼는다.
        base_day = now_dt.date()
        if base_day.weekday() < 5 and (now_dt.hour, now_dt.minute) < (17, 0):
            base_day -= timedelta(days=1)
        last_td = _last_trading_day(base_day)
        threshold = datetime.combine(last_td, datetime.min.time()).replace(hour=17, minute=0)
        fresh = mtime_dt >= threshold
    else:
        fresh = h < 26
    # 시간 라벨
    if h < 1:
        label = f"{int(age_sec / 60)}분 전"
    elif h < 24:
        label = f"{h:.1f}시간 전"
    else:
        label = f"{h / 24:.1f}일 전"
    if trading_day_aware and not fresh and h < 72:
        label += " (직전 거래일 기준 신선도 미충족)"
    return fresh, label


def fresh_age_after(path: Path, target_date: str, hour: int, minute: int = 0) -> tuple[bool, str]:
    """파일이 target_date의 특정 시각 이후 갱신됐는지 확인."""
    if not path.exists():
        return False, "없음"
    mtime_dt = datetime.fromtimestamp(path.stat().st_mtime)
    try:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
        threshold = datetime.combine(d, datetime.min.time()).replace(hour=hour, minute=minute)
    except Exception:
        threshold = datetime.now() - timedelta(hours=26)
    fresh = mtime_dt >= threshold
    age_sec = (datetime.now() - mtime_dt).total_seconds()
    h = age_sec / 3600
    if h < 1:
        label = f"{int(age_sec / 60)}분 전"
    elif h < 24:
        label = f"{h:.1f}시간 전"
    else:
        label = f"{h / 24:.1f}일 전"
    if not fresh:
        label += f" ({target_date} {hour:02d}:{minute:02d} 이후 갱신 아님)"
    return fresh, label


def latest_file_in(dir_path: Path, pattern: str = "*") -> Path | None:
    if not dir_path.exists():
        return None
    files = list(dir_path.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def parquet_count_recent(dir_path: Path, since_days: int = 2) -> int:
    """최근 N일 안에 갱신된 parquet 파일 수."""
    if not dir_path.exists():
        return 0
    cutoff = datetime.now().timestamp() - since_days * 86400
    cnt = 0
    for p in dir_path.glob("*.parquet"):
        try:
            if p.stat().st_mtime >= cutoff:
                cnt += 1
        except OSError:
            continue
    return cnt


def status_icon(ok: bool, warn: bool = False) -> str:
    if warn:
        return "⚠️"
    return "✅" if ok else "❌"


# ──────────── 슬롯별 점검 ────────────


def check_1415(today: str) -> dict[str, Any]:
    """14:15 데이터 수집 슬롯."""
    items: list[dict] = []
    overall_ok = True

    # 1) D0 candidates 또는 dryrun 파일
    d0_dir = SHARED / "watchlists"
    latest_d0 = latest_file_in(d0_dir, f"d0_pool_dryrun_*.csv") if d0_dir.exists() else None
    if latest_d0:
        ok, age = fresh_age_after(latest_d0, today, 14, 15)
        items.append({
            "check": "D0 pool dryrun",
            "status": status_icon(ok),
            "file": latest_d0.name,
            "age": age,
            "ok": ok,
        })
        overall_ok &= ok
    else:
        items.append({"check": "D0 pool dryrun", "status": "❌", "file": "—", "age": "없음", "ok": False})
        overall_ok = False

    # 2) preclose D0 stage_3d pool (BellGuard 운영 원천)
    stage_pattern = f"one_year_non_ai_backtest_1d_for_preclose_{today.replace('-', '')}_*/stage_3d/d0_pool_1y.csv"
    stage_files = list((CLOSINGBELL / "backtests").glob(stage_pattern))
    if stage_files:
        f = max(stage_files, key=lambda p: p.stat().st_mtime)
        ok, age = fresh_age_after(f, today, 14, 15)
        items.append({
            "check": "BellGuard D0 stage_3d pool",
            "status": status_icon(ok),
            "file": f.name,
            "age": age,
            "ok": ok,
        })
        overall_ok &= ok
    else:
        items.append({
            "check": "BellGuard D0 stage_3d pool",
            "status": "❌",
            "file": "—",
            "age": "폴더 없음",
            "ok": False,
        })
        overall_ok = False

    # 3) Task Scheduler 마지막 실행 시간
    items.append({"check": "Task: ClosingBell_Data_Preclose_1415", "status": "ℹ️",
                  "file": "—", "age": "PowerShell `Get-ScheduledTaskInfo` 로 확인", "ok": True})

    return {"slot": "1415", "title": SLOT_TITLES["1415"], "checked_at": datetime.now().isoformat(timespec="seconds"),
            "target_date": today, "overall_ok": overall_ok, "items": items}


def check_1500(today: str) -> dict[str, Any]:
    """15:00 후보 산출 + 웹훅 발송 슬롯."""
    items: list[dict] = []
    overall_ok = True

    # 1) BellGuard minute refresh code list
    refresh_codes = SHARED / "bellguard_candidates" / today.replace("-", "") / f"bellguard_refresh_codes_{today.replace('-', '')}.csv"
    if refresh_codes.exists():
        ok, age = fresh_age_after(refresh_codes, today, 15, 0)
        items.append({"check": "BellGuard minute refresh codes", "status": status_icon(ok), "file": refresh_codes.name, "age": age, "ok": ok})
        overall_ok &= ok
    else:
        items.append({"check": "BellGuard minute refresh codes", "status": "❌", "file": "—", "age": "없음", "ok": False})
        overall_ok = False

    # 2) BellGuard signal-context Top3 (메인 운영 데이터셋)
    bg_dir = ONLINE_V2_LATEST / "bellguard_d0_strict_1y"
    bg = bg_dir / "bellguard_d0_strict_top3_latest.csv"
    if bg.exists():
        ok, age = fresh_age_after(bg, today, 15, 0)
        manifest_path = bg_dir / "bellguard_d0_strict_manifest.json"
        model_ok = False
        policy_ok = False
        latest_ok = False
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
                model_ok = str(manifest.get("score_model_version", "")).startswith("BELLGUARD_SIGNAL_CONTEXT")
                policy = str(manifest.get("selection_policy", ""))
                policy_ok = policy.startswith("active_d0_3d_pool") and "signal-date" in policy
                latest_ok = str(manifest.get("latest_signal_date", ""))[:10] == today
            except Exception:
                model_ok = policy_ok = latest_ok = False
        guard_ok = ok and model_ok and policy_ok and latest_ok
        items.append({
            "check": "BellGuard signal-context Top3",
            "status": status_icon(guard_ok, warn=not guard_ok),
            "file": bg.name, "age": age, "ok": ok,
            "note": f"model={model_ok}, policy={policy_ok}, latest={latest_ok}",
        })
        overall_ok &= guard_ok
    else:
        items.append({"check": "BellGuard signal-context Top3", "status": "❌",
                      "file": "—", "age": "없음", "ok": False})
        overall_ok = False

    # 3) Discord 발송 로그
    sent_log = SHARED / "sent_log" / "paper_watch_sent_log.jsonl"
    if sent_log.exists():
        ok, age = fresh_age_after(sent_log, today, 15, 0)
        # 마지막 라인 파싱
        try:
            with open(sent_log, "rb") as f:
                f.seek(0, 2)
                size = f.tell()
                f.seek(max(0, size - 8192))
                tail = f.read().decode("utf-8", errors="ignore")
            last_line = tail.strip().split("\n")[-1]
            ev = json.loads(last_line)
            ev_date = ev.get("event_date") or ev.get("snapshot_date") or "—"
            http = ev.get("discord_response_status") or ev.get("status") or "—"
            mode = ev.get("send_mode") or ev.get("mode") or "—"
            items.append({
                "check": "Discord paper_watch_sent_log 최신",
                "status": status_icon(ok),
                "file": f"date={ev_date}, mode={mode}, http={http}",
                "age": age, "ok": ok,
            })
        except Exception as exc:  # noqa: BLE001
            items.append({"check": "sent_log 파싱", "status": "⚠️",
                          "file": sent_log.name, "age": age, "ok": True, "note": str(exc)})
        overall_ok &= ok
    else:
        items.append({"check": "Discord sent_log", "status": "❌",
                      "file": "—", "age": "없음", "ok": False})
        overall_ok = False

    # 4) 웹훅 preview 금지어 검사
    pv = HEALTH_DIR / f"webhook_preview_bellguard_1500_{today.replace('-', '')}.md"
    if pv.exists():
        text = pv.read_text(encoding="utf-8", errors="ignore")
        FORBIDDEN = ["추천", "확정 매수", "무조건", "승률 보장", "자동매수"]
        WHITE = ["매수 추천이 아", "추천이 아닙니다", "추천이 아니라", "추천 아닌"]
        bad = []
        for t in FORBIDDEN:
            if t in text and not any(w in text for w in WHITE):
                bad.append(t)
        items.append({
            "check": "웹훅 preview 금지어 검사",
            "status": "✅" if not bad else "⚠️",
            "file": pv.name,
            "age": "OK" if not bad else f"발견: {bad}",
            "ok": not bad,
        })
        overall_ok &= not bool(bad)
    else:
        items.append({"check": "웹훅 preview", "status": "ℹ️",
                      "file": "—", "age": "오늘 preview 미생성 (수동 실행 필요)", "ok": True})

    return {"slot": "1500", "title": SLOT_TITLES["1500"], "checked_at": datetime.now().isoformat(timespec="seconds"),
            "target_date": today, "overall_ok": overall_ok, "items": items}


def check_postclose(today: str) -> dict[str, Any]:
    """17:05 장마감 데이터 갱신 슬롯."""
    items: list[dict] = []
    overall_ok = True

    # 1) 일봉 parquet 최근 갱신 카운트
    daily_dir = MARKET / "daily_ohlcv"
    daily_recent = parquet_count_recent(daily_dir, since_days=2)
    daily_ok = daily_recent > 1000
    items.append({"check": "일봉 parquet (최근 2일 내 갱신)", "status": status_icon(daily_ok),
                  "file": f"{daily_recent:,}개", "age": f"{daily_dir}", "ok": daily_ok})
    overall_ok &= daily_ok

    # 2) 분봉 parquet 최근 갱신
    min_dir = MARKET / "minute_ohlcv"
    min_recent = parquet_count_recent(min_dir, since_days=2)
    min_ok = min_recent > 500
    items.append({"check": "분봉 parquet (최근 2일 내 갱신)", "status": status_icon(min_ok, warn=not min_ok),
                  "file": f"{min_recent:,}개", "age": f"{min_dir}", "ok": min_ok})
    overall_ok &= min_ok

    # 3) 수급 (inst_trade)
    inst_dir = MARKET / "supply" / "inst_trade"
    inst_recent = parquet_count_recent(inst_dir, since_days=2)
    inst_ok = inst_recent > 500
    items.append({"check": "외인·기관 (inst_trade)", "status": status_icon(inst_ok, warn=not inst_ok),
                  "file": f"{inst_recent:,}개", "age": f"{inst_dir}", "ok": inst_ok})

    # 4) 프로그램
    prog_dir = MARKET / "supply" / "program_per_code"
    prog_recent = parquet_count_recent(prog_dir, since_days=2)
    items.append({"check": "프로그램 매매", "status": status_icon(prog_recent > 0, warn=prog_recent == 0),
                  "file": f"{prog_recent:,}개", "age": f"{prog_dir}", "ok": prog_recent > 0})

    # 5) 글로벌 지수
    glob = MARKET / "global" / "global_merged.csv"
    if glob.exists():
        ok, age = fresh_age(glob)
        items.append({"check": "글로벌 지수", "status": status_icon(ok), "file": glob.name, "age": age, "ok": ok})
        overall_ok &= ok
    else:
        items.append({"check": "글로벌 지수", "status": "❌", "file": "—", "age": "없음", "ok": False})

    # 6) DART 최근 갱신 — 회사 JSON은 정적 성격이라 freshness 근거에서 제외.
    dart_recent = DART / "recent_30d.parquet"
    target_ymd = today.replace("-", "")
    if dart_recent.exists():
        ok_age, age = fresh_age(dart_recent)
        latest_rcept = ""
        rows = 0
        try:
            df = pd.read_parquet(dart_recent, columns=["rcept_dt"])
            rows = int(len(df))
            if rows:
                latest_rcept = str(df["rcept_dt"].astype(str).max())[:8]
        except Exception as exc:  # noqa: BLE001
            latest_rcept = f"read_error: {type(exc).__name__}"
        date_ok = bool(latest_rcept and latest_rcept.isdigit() and latest_rcept >= target_ymd)
        items.append({
            "check": "DART recent_30d",
            "status": status_icon(ok_age and date_ok, warn=not (ok_age and date_ok)),
            "file": f"{dart_recent.name} rows={rows:,} max={latest_rcept}",
            "age": age,
            "ok": ok_age and date_ok,
        })
        overall_ok &= ok_age and date_ok
    else:
        items.append({"check": "DART recent_30d", "status": "❌", "file": "—", "age": "없음", "ok": False})
        overall_ok = False

    dart_processed = latest_file_in(DART / "processed", "disclosure_flags_30d_asof_*.parquet")
    if dart_processed:
        ok, age = fresh_age(dart_processed)
        items.append({"check": "DART processed flags", "status": status_icon(ok, warn=not ok),
                      "file": dart_processed.name, "age": age, "ok": ok})
        overall_ok &= ok
    else:
        items.append({"check": "DART processed flags", "status": "⚠️", "file": "—", "age": "없음", "ok": False})

    # 7) Task Scheduler
    items.append({"check": "Task: ClosingBell_Data_PostClose_1705", "status": "ℹ️",
                  "file": "—", "age": "Get-ScheduledTaskInfo 로 LastRunTime 확인", "ok": True})

    return {"slot": "postclose", "title": SLOT_TITLES["postclose"],
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "target_date": today, "overall_ok": overall_ok, "items": items}


def check_publish(today: str) -> dict[str, Any]:
    """online_v2/latest 갱신 + git status."""
    items: list[dict] = []
    overall_ok = True

    # 1) online_v2/latest manifest 갱신
    manifest = ONLINE_V2_LATEST / "manifest.json"
    if manifest.exists():
        ok, age = fresh_age_after(manifest, today, 15, 0)
        items.append({"check": "online_v2 manifest", "status": status_icon(ok, warn=not ok),
                      "file": manifest.name, "age": age, "ok": True})
    else:
        items.append({"check": "online_v2 manifest", "status": "⚠️", "file": "—", "age": "없음", "ok": True})

    # 2) bellguard_d0_strict_1y signal-context manifest
    bg_manifest = ONLINE_V2_LATEST / "bellguard_d0_strict_1y" / "bellguard_d0_strict_manifest.json"
    if bg_manifest.exists():
        ok, age = fresh_age_after(bg_manifest, today, 15, 0)
        try:
            manifest = json.loads(bg_manifest.read_text(encoding="utf-8-sig"))
            model_ok = str(manifest.get("score_model_version", "")).startswith("BELLGUARD_SIGNAL_CONTEXT")
            policy = str(manifest.get("selection_policy", ""))
            policy_ok = policy.startswith("active_d0_3d_pool") and "signal-date" in policy
        except Exception:
            model_ok = policy_ok = False
        guard_ok = ok and model_ok and policy_ok
        items.append({"check": "BellGuard signal-context manifest", "status": status_icon(guard_ok, warn=not guard_ok),
                      "file": bg_manifest.name, "age": f"{age} / model={model_ok} policy={policy_ok}", "ok": guard_ok})
        overall_ok &= guard_ok

    # 3) git status (bell-dashboard)
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            changed = [l for l in result.stdout.splitlines() if l.strip()]
            n_changed = len(changed)
            if n_changed == 0:
                items.append({"check": "git status", "status": "✅",
                              "file": "clean", "age": "변경 없음", "ok": True})
            else:
                items.append({"check": "git status", "status": "⚠️",
                              "file": f"{n_changed} files changed",
                              "age": "publish 필요", "ok": True})
        else:
            items.append({"check": "git status", "status": "ℹ️",
                          "file": "—", "age": "git 명령 실패 (repo 아님?)", "ok": True})
    except Exception as exc:  # noqa: BLE001
        items.append({"check": "git status", "status": "ℹ️",
                      "file": "—", "age": str(exc)[:80], "ok": True})

    # 4) 마지막 commit
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO), "log", "-1", "--format=%h %s (%ar)"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            items.append({"check": "마지막 commit", "status": "ℹ️",
                          "file": result.stdout.strip()[:100], "age": "—", "ok": True})
    except Exception:  # noqa: BLE001
        pass

    # 5) publish 스크립트 존재
    pub_ps1 = REPO / "scripts" / "publish_online_v2_to_github.ps1"
    items.append({
        "check": "publish_online_v2_to_github.ps1",
        "status": "✅" if pub_ps1.exists() else "❌",
        "file": pub_ps1.name,
        "age": "존재" if pub_ps1.exists() else "없음",
        "ok": pub_ps1.exists(),
    })

    return {"slot": "publish", "title": SLOT_TITLES["publish"],
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "target_date": today, "overall_ok": overall_ok, "items": items}


# ──────────── 보고서 ────────────


def format_md(report: dict[str, Any]) -> str:
    lines = [
        f"# Health Check — {report['title']} ({report['slot']})",
        "",
        f"- 검사 시각: {report['checked_at']}",
        f"- 대상일: {report['target_date']}",
        f"- 종합: **{'✅ 정상' if report['overall_ok'] else '⚠️ 주의'}**",
        "",
        "## 점검 항목",
        "",
        "| 상태 | 항목 | 파일/세부 | 시간 / 비고 |",
        "|:---:|---|---|---|",
    ]
    for it in report["items"]:
        age_note = it["age"]
        if it.get("note"):
            age_note = f"{age_note} / {it['note']}"
        lines.append(
            f"| {it['status']} | {it['check']} | `{it['file']}` | {age_note} |"
        )
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any]) -> tuple[Path, Path]:
    HEALTH_DIR.mkdir(parents=True, exist_ok=True)
    date_compact = report["target_date"].replace("-", "")
    json_p = HEALTH_DIR / f"health_{report['slot']}_{date_compact}.json"
    md_p = HEALTH_DIR / f"health_{report['slot']}_{date_compact}.md"
    json_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_p.write_text(format_md(report), encoding="utf-8")
    return json_p, md_p


def run_slot(slot: str, today: str) -> dict[str, Any]:
    func = {
        "1415": check_1415, "1500": check_1500,
        "postclose": check_postclose, "publish": check_publish,
    }[slot]
    report = func(today)
    j, m = write_report(report)
    badge = "OK  " if report["overall_ok"] else "WARN"
    # ASCII-safe print (Windows cp949 console 호환)
    title = report["title"]
    print(f"[{badge}] {title:30s} -> {m.name}")
    return report


def run_all(today: str) -> None:
    print(f"=== Bell Pipeline Health Check ({today}) ===")
    results = []
    for s in ["1415", "1500", "postclose", "publish"]:
        results.append(run_slot(s, today))
    # 종합 보고
    md = [
        f"# Bell Pipeline Health — {today}",
        "",
        f"검사 시각: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 슬롯별 종합",
        "",
        "| 슬롯 | 상태 | 항목 수 |",
        "|---|---|---:|",
    ]
    for r in results:
        badge = "✅ 정상" if r["overall_ok"] else "⚠️ 주의"
        md.append(f"| {r['slot']} {r['title']} | {badge} | {len(r['items'])} |")
    md_p = HEALTH_DIR / f"health_all_{today.replace('-', '')}.md"
    md_p.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n[OK] 종합 보고: {md_p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", choices=["1415", "1500", "postclose", "publish", "all"], required=True)
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="대상일 YYYY-MM-DD (기본: 오늘)")
    args = ap.parse_args()
    if args.slot == "all":
        run_all(args.date)
    else:
        run_slot(args.slot, args.date)


if __name__ == "__main__":
    main()
