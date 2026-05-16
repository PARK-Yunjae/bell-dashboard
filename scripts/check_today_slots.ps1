# ClosingBell 오늘 슬롯 결과 한눈에 점검 - 14:15 / 15:00 / 17:05
#
# 사용법: 사후 (15:01 이후, 17:06 이후) 실행
#   powershell -ExecutionPolicy Bypass -File C:\Coding\projects\bell-dashboard\scripts\check_today_slots.ps1
#   또는 다른 날짜:
#   powershell -ExecutionPolicy Bypass -File ...\check_today_slots.ps1 -Date 2026-05-15

param([string]$Date = (Get-Date -Format "yyyy-MM-dd"))

$ErrorActionPreference = "Continue"

function Write-Line($title, $color = "Cyan") {
  Write-Host ""
  Write-Host ("=" * 70) -ForegroundColor $color
  Write-Host "  $title" -ForegroundColor $color
  Write-Host ("=" * 70) -ForegroundColor $color
}

function Check-File($path, $label) {
  if (Test-Path $path) {
    $info = Get-Item $path
    Write-Host ("  [OK]   $label") -ForegroundColor Green
    Write-Host ("         mtime: $($info.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')), size: $([math]::Round($info.Length/1KB, 1)) KB") -ForegroundColor DarkGray
    return $true
  } else {
    Write-Host ("  [MISS] $label") -ForegroundColor Red
    Write-Host ("         $path") -ForegroundColor DarkGray
    return $false
  }
}

Write-Host ""
Write-Host "ClosingBell 슬롯 점검 - target_date = $Date" -ForegroundColor Yellow
Write-Host "현재 시각: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray

$stamp = $Date -replace "-", ""

# -----------------------------------------------------
Write-Line "1. 스케줄러 상태 (Windows Task Scheduler)"
$tasks = @(
  @{Name = "ClosingBell_Data_Preclose_1415";   Slot = "14:15 preclose"},
  @{Name = "ClosingBell_Data_V2Minute_1502";   Slot = "15:02 V2 minute"},
  @{Name = "ClosingBell_Webhook_Preclose_1415"; Slot = "15:00 webhook"},
  @{Name = "ClosingBell_Data_PostClose_1705";  Slot = "17:05 postclose"}
)
foreach ($t in $tasks) {
  try {
    $st = Get-ScheduledTask -TaskName $t.Name -ErrorAction Stop
    $info = Get-ScheduledTaskInfo -TaskName $t.Name -ErrorAction Stop
    $color = if ($st.State -eq "Ready" -or $st.State -eq "Running") { "Green" }
             elseif ($st.State -eq "Disabled") { "Yellow" }
             else { "Red" }
    Write-Host ("  [{0}] {1,-32} state={2,-10} last={3:yyyy-MM-dd HH:mm} next={4:yyyy-MM-dd HH:mm} result={5}" -f `
      $t.Slot, $t.Name, $st.State, $info.LastRunTime, $info.NextRunTime, $info.LastTaskResult) -ForegroundColor $color
  } catch {
    Write-Host ("  [ERR]  $($t.Name) - not found") -ForegroundColor Red
  }
}

# -----------------------------------------------------
Write-Line "2. 14:15 Preclose 산출물 (V2 raw / Top3 / D0 pool)"
$preclose_dir = "C:\Coding\data\closingbell\shared\v2_candidates\$stamp"
Check-File "$preclose_dir\v2_top3_candidates_$stamp.csv"      "V2 Top3 후보 CSV"  | Out-Null
Check-File "$preclose_dir\v2_top3_candidates_$stamp.json"     "V2 Top3 JSON"     | Out-Null
Check-File "$preclose_dir\v2_top3_excluded_$stamp.csv"        "제외 후보 CSV"    | Out-Null
Check-File "$preclose_dir\v2_top3_manifest_$stamp.json"       "manifest"         | Out-Null

# Read manifest details
$manifest = "$preclose_dir\v2_top3_manifest_$stamp.json"
if (Test-Path $manifest) {
  try {
    $m = Get-Content $manifest -Raw | ConvertFrom-Json
    Write-Host ""
    Write-Host "  -> manifest 핵심 필드:" -ForegroundColor Cyan
    Write-Host ("    target_date       = {0}" -f $m.target_date)
    Write-Host ("    status            = {0}" -f $m.status)
    Write-Host ("    source_mode       = {0}" -f $m.source_mode)
    Write-Host ("    source_pool       = {0}" -f $m.source_pool)
    Write-Host ("    score_policy      = {0}" -f $m.score_policy)
    Write-Host ("    selected_count    = {0} / 3" -f $m.selected_count)
    Write-Host ("    raw_count         = {0}" -f $m.raw_count)
    Write-Host ("    fallback_used     = {0}" -f $m.fallback_used)
    Write-Host ("    excluded_count    = {0}" -f $m.excluded_count)
    if ($m.program_buy_feature_used -ne $null) {
      Write-Host ("    program feature  = {0} (off=정상)" -f $m.program_buy_feature_used)
    }

    # 통과 게이트
    Write-Host ""
    $pass1 = $m.selected_count -eq 3
    $pass2 = $m.source_mode -eq "operational_d0_pool_v2_score"
    $pass3 = $m.fallback_used -eq $false
    $col1 = if ($pass1) {"Green"} else {"Red"}
    $col2 = if ($pass2) {"Green"} else {"Red"}
    $col3 = if ($pass3) {"Green"} else {"Red"}
    Write-Host ("    [{0}] selected_count == 3" -f $(if ($pass1) {"OK"} else {"FAIL"})) -ForegroundColor $col1
    Write-Host ("    [{0}] source_mode == operational_d0_pool_v2_score" -f $(if ($pass2) {"OK"} else {"FAIL"})) -ForegroundColor $col2
    Write-Host ("    [{0}] fallback_used == false" -f $(if ($pass3) {"OK"} else {"FAIL"})) -ForegroundColor $col3
  } catch {
    Write-Host "  [WARN] manifest JSON 파싱 실패: $_" -ForegroundColor Yellow
  }
}

# V2 Top3 후보 명단
$top3csv = "$preclose_dir\v2_top3_candidates_$stamp.csv"
if (Test-Path $top3csv) {
  Write-Host ""
  Write-Host "  -> 오늘 V2 Top3 후보:" -ForegroundColor Cyan
  Import-Csv $top3csv | Select-Object v2_rank, stock_code, stock_name, score_total_100, entry_status, entry_price_1500 | Format-Table -AutoSize
}

# -----------------------------------------------------
Write-Line "3. 15:00 웹훅 발송 결과"
$snap_dir = "C:\Coding\data\closingbell\shared\snapshots\v2_top3_$stamp"
Check-File "$snap_dir\snapshot.json"          "snapshot.json"      | Out-Null
Check-File "$snap_dir\result.json"            "result.json"        | Out-Null
Check-File "$snap_dir\rendered_message.md"    "rendered_message"   | Out-Null

$result = "$snap_dir\result.json"
if (Test-Path $result) {
  try {
    $r = Get-Content $result -Raw | ConvertFrom-Json
    Write-Host ""
    Write-Host "  -> result.json 핵심:" -ForegroundColor Cyan
    Write-Host ("    status            = {0}" -f $r.status)
    Write-Host ("    send_attempted    = {0}" -f $r.send_attempted)
    if ($r.send_result) {
      $sr = $r.send_result
      Write-Host ("    webhook_mode      = {0}" -f $sr.webhook_mode)
      Write-Host ("    provider_status   = {0}" -f $sr.provider_result.status_code)
      Write-Host ("    provider_reason   = {0}" -f $sr.provider_result.reason)
      Write-Host ("    url_present       = {0}" -f $sr.url_present)
      Write-Host ("    idempotency_key   = {0}" -f $sr.idempotency_key)
    }

    Write-Host ""
    $sent_ok = ($r.status -eq "sent")
    $http_ok = $false
    if ($r.send_result -and $r.send_result.provider_result) {
      $code = $r.send_result.provider_result.status_code
      $http_ok = ($code -eq 204 -or $code -eq 200)
    }
    $col_s = if ($sent_ok) {"Green"} else {"Red"}
    $col_h = if ($http_ok) {"Green"} else {"Red"}
    Write-Host ("    [{0}] status == sent" -f $(if ($sent_ok) {"OK"} else {"FAIL"})) -ForegroundColor $col_s
    Write-Host ("    [{0}] HTTP 200/204 응답" -f $(if ($http_ok) {"OK"} else {"FAIL"})) -ForegroundColor $col_h

    # 메시지 길이
    $msg_path = "$snap_dir\rendered_message.md"
    if (Test-Path $msg_path) {
      $msg_len = (Get-Content $msg_path -Raw).Length
      $col_l = if ($msg_len -lt 1800) {"Green"} else {"Red"}
      Write-Host ("    [{0}] message length = {1} chars (< 1800 필요)" -f $(if ($msg_len -lt 1800) {"OK"} else {"FAIL"}), $msg_len) -ForegroundColor $col_l
    }
  } catch {
    Write-Host "  [WARN] result.json 파싱 실패: $_" -ForegroundColor Yellow
  }
}

# -----------------------------------------------------
Write-Line "4. 17:05 Postclose 갱신 결과"
$bd_dir = "C:\Coding\data\closingbell\research_index\v2_no_program_backdata_1y_$stamp"
Check-File "$bd_dir\v2_no_program_backdata_1y_detail_$stamp.csv"  "1년 백데이터 detail"  | Out-Null
Check-File "$bd_dir\v2_no_program_backdata_1y_daily_summary_$stamp.csv"  "1년 일별 요약" | Out-Null

$phase0_dir = "C:\Coding\data\closingbell\research_index\phase0_realistic_fill_pilot_$stamp"
Check-File "$phase0_dir\phase0_realistic_fill_summary_$stamp.csv"  "Phase 0 fill summary"  | Out-Null
Check-File "$phase0_dir\phase0_realistic_fill_first_touch_summary_$stamp.csv"  "Phase 0 first-touch summary"  | Out-Null

# online_v2 export 갱신 확인
$online_manifest = "C:\Coding\projects\bell-dashboard\data\closingbell\online_v2\latest\manifest.json"
if (Test-Path $online_manifest) {
  try {
    $om = Get-Content $online_manifest -Raw | ConvertFrom-Json
    Write-Host ""
    Write-Host "  -> online_v2 latest manifest:" -ForegroundColor Cyan
    Write-Host ("    target_date    = {0}" -f $om.target_date)
    Write-Host ("    created_at     = {0}" -f $om.created_at)
    $ok = ($om.target_date -eq $Date)
    $col = if ($ok) {"Green"} else {"Yellow"}
    Write-Host ("    [{0}] target_date == {1}" -f $(if ($ok) {"OK"} else {"WAIT/STALE"}), $Date) -ForegroundColor $col
  } catch {}
}

# Sent log 검사
Write-Host ""
Write-Host "  -> 오늘 sent_log 마지막 V2 발송 기록:" -ForegroundColor Cyan
$slog = "C:\Coding\data\closingbell\shared\sent_log\paper_watch_sent_log.jsonl"
if (Test-Path $slog) {
  $lines = Get-Content $slog | Where-Object { $_ -match "V2 Top3" -and $_ -match $Date }
  if ($lines) {
    $last = $lines[-1] | ConvertFrom-Json
    Write-Host ("    created_at:  {0}" -f $last.created_at)
    Write-Host ("    status:      {0}" -f $last.status)
    Write-Host ("    sent:        {0}" -f $last.send_attempted)
    Write-Host ("    mode:        {0}" -f $last.webhook_mode)
  } else {
    Write-Host "    (오늘 V2 발송 기록 없음)" -ForegroundColor Yellow
  }
}

# -----------------------------------------------------
Write-Line "5. 최종 판정"
Write-Host ""
Write-Host "  사용자 확인 체크리스트:" -ForegroundColor Yellow
Write-Host "    [ ] 14:15 슬롯 - V2 Top3 3개 생성, source_mode operational, fallback false"
Write-Host "    [ ] 15:00 슬롯 - Discord 발송 status=sent, HTTP 204/200, message < 1800자"
Write-Host "    [ ] 17:05 슬롯 - 백데이터 detail/Phase0/online_v2 target_date 갱신"
Write-Host ""
Write-Host "현재 KST: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
Write-Host ""
