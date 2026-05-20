param(
    [string]$Message = "",
    [switch]$Push,
    [switch]$NoPush,
    [switch]$DryRun,
    [switch]$SkipFreshnessGuard
)

# ClosingBell EOD-D0 Active Watch online_v2 GitHub publish 자동화.
#
# 사용:
#   .\publish_online_v2_to_github.ps1                  # 환경변수 또는 기본값에 따라 자동 결정
#   .\publish_online_v2_to_github.ps1 -Push            # 강제 push
#   .\publish_online_v2_to_github.ps1 -NoPush          # commit 만, push 안 함
#   .\publish_online_v2_to_github.ps1 -DryRun          # 변경 사항 확인만
#
# 환경변수:
#   CLOSINGBELL_ONLINE_V2_GIT_PUSH = "true"            # -NoPush 가 아니면 push 활성
#
# 자동 안전장치:
#   1. 100MB 이상 파일 감지시 중단
#   2. 민감 패턴(.env / secrets / discord url) 감지시 중단
#   3. git config user.email 없으면 안내
#   4. EOD-D0 Active Watch manifest 가 오늘 날짜/Top3 3개/Guard PASS 상태일 때만 publish

$ErrorActionPreference = "Stop"
$Project = "C:\Coding\projects\bell-dashboard"
$HealthDir = "C:\Coding\data\closingbell\health"
Set-Location $Project

if (-not (Test-Path -LiteralPath ".git")) {
    Write-Host "[skip] bell-dashboard is not a git repo. Run git init + remote add first." -ForegroundColor Yellow
    exit 0
}

$remote = git remote 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($remote -join ""))) {
    Write-Host "[skip] git remote is not configured. Add GitHub remote first." -ForegroundColor Yellow
    exit 0
}

# git config 확인
$gitEmail = (git config user.email 2>$null)
if ([string]::IsNullOrWhiteSpace($gitEmail)) {
    Write-Host "[skip] git config user.email is missing. Run:" -ForegroundColor Yellow
    Write-Host '       git config --local user.email "your@email.com"' -ForegroundColor Yellow
    Write-Host '       git config --local user.name  "Your Name"' -ForegroundColor Yellow
    exit 0
}

# === 안전장치 0: 오늘 EOD-D0 Active Watch 데이터가 준비됐는지 확인 ===
if (-not $SkipFreshnessGuard) {
    $todayIso = Get-Date -Format "yyyy-MM-dd"
    $manifestPath = Join-Path $Project "data\closingbell\online_v2\latest\eod_d0_active_watch_preview\manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        Write-Host "[skip] EOD Active Watch manifest is missing: $manifestPath" -ForegroundColor Yellow
        exit 0
    }
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Write-Host "[skip] EOD Active Watch manifest parse failed: $($_.Exception.Message)" -ForegroundColor Yellow
        exit 0
    }
    $signalDate = [string]$manifest.signal_date
    $selectedCount = [int]$manifest.selected_count
    $guardStatus = [string]$manifest.guard_status
    $sourceLayer = [string]$manifest.source_layer
    $modelId = [string]$manifest.model_id
    $watchDays = [int]$manifest.watch_days
    $selectionPolicy = [string]$manifest.selection_policy

    if ($sourceLayer -ne "ACTIVE_WATCHLIST") {
        Write-Host "[skip] EOD source layer mismatch: source_layer=$sourceLayer" -ForegroundColor Yellow
        exit 0
    }
    if ($modelId -ne "EOD_D0_BASE_VALUE_TOP3") {
        Write-Host "[skip] EOD model mismatch: model_id=$modelId" -ForegroundColor Yellow
        exit 0
    }
    if ($watchDays -ne 10) {
        Write-Host "[skip] EOD watch_days mismatch: watch_days=$watchDays" -ForegroundColor Yellow
        exit 0
    }
    if ($selectionPolicy -ne "EOD_D0_BASE_VALUE_TOP3__WATCH10D__D0_VALUE_DESC") {
        Write-Host "[skip] EOD selection policy mismatch: policy=$selectionPolicy" -ForegroundColor Yellow
        exit 0
    }
    if ($signalDate -ne $todayIso) {
        Write-Host "[skip] EOD latest date mismatch: signal_date=$signalDate today=$todayIso" -ForegroundColor Yellow
        exit 0
    }
    if ($selectedCount -ne 3 -or $guardStatus -ne "PASS") {
        Write-Host "[skip] EOD publish guard failed: selected=$selectedCount guard=$guardStatus" -ForegroundColor Yellow
        exit 0
    }

    $guardReportPath = Join-Path $Project "data\closingbell\online_v2\latest\eod_d0_active_watch_preview\guard_report.json"
    if (Test-Path -LiteralPath $guardReportPath) {
        try {
            $guardReport = Get-Content -LiteralPath $guardReportPath -Encoding UTF8 | ConvertFrom-Json
            if ($guardReport.status -ne "PASS" -or -not [bool]$guardReport.d0_date_lt_signal_date_all -or -not [bool]$guardReport.entry_1500_dt_lte_1500_all) {
                Write-Host "[skip] EOD detailed guard failed: status=$($guardReport.status) d0_lt=$($guardReport.d0_date_lt_signal_date_all) entry_lte=$($guardReport.entry_1500_dt_lte_1500_all)" -ForegroundColor Yellow
                exit 0
            }
        } catch {
            Write-Host "[skip] EOD guard_report parse failed: $($_.Exception.Message)" -ForegroundColor Yellow
            exit 0
        }
    }
    Write-Host "[ok] EOD Active Watch freshness guard passed: $signalDate Top3=$selectedCount model=$modelId" -ForegroundColor Green
}

# === 안전장치 1: 큰 파일 감지 (100MB 이상) ===
$bigFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.Length -gt 100MB }
if ($bigFiles.Count -gt 0) {
    Write-Host "[abort] Files larger than 100MB detected. Publish stopped:" -ForegroundColor Red
    $bigFiles | ForEach-Object { Write-Host "  $($_.FullName)  $([math]::Round($_.Length/1MB,1)) MB" -ForegroundColor Red }
    exit 1
}

# === 안전장치 2: 민감 정보 검사 ===
$sensitive = @(
    "data/closingbell/shared/sent_log",
    "data/closingbell/user_notes",
    ".env",
    "secrets.toml",
    "kiwoom_token",
    "discord_webhook"
)
foreach ($pat in $sensitive) {
    $found = git ls-files --modified --others --exclude-standard 2>$null | Where-Object { $_ -match $pat }
    if ($found) {
        Write-Host "[abort] Sensitive file/pattern detected: '$pat'" -ForegroundColor Red
        $found | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        Write-Host "       Add it to .gitignore or handle it separately before retrying." -ForegroundColor Yellow
        exit 1
    }
}

# === PDF 자동 재생성 ===
# EOD-D0 Active Watch main route 전환 후에는 BellGuard 전용 PDF 빌더를 자동 실행하지 않는다.
$VenvPy = "C:\Coding\projects\_venvs\closingbell-py312\Scripts\python.exe"
if ($DryRun) {
    Write-Host "[dry-run] skipping PDF rebuild" -ForegroundColor Cyan
} else {
    Write-Host "[skip] BellGuard legacy PDF rebuild disabled for EOD main route" -ForegroundColor Yellow
}

# === publish target / dry-run ===
$publishTargets = @(
    "app.py",
    ".gitignore",
    "README.md",
    "requirements.txt",
    "runtime.txt",
    ".streamlit",
    "data/closingbell/online_v2",
    "scripts",
    "run_dashboard.bat",
    "run_dashboard_quiet.bat"
)

if ($DryRun) {
    $status = git status --porcelain -- $publishTargets
    Write-Host "[dry-run] changes:" -ForegroundColor Cyan
    if ([string]::IsNullOrWhiteSpace(($status -join ""))) {
        Write-Host "  no matching changes"
    } else {
        $status | ForEach-Object { Write-Host "  $_" }
    }
    Write-Host "[dry-run] commit / push not executed."
    exit 0
}

# === add ===
$gitAddArgs = @("add") + $publishTargets
$tmpGitOut = [System.IO.Path]::GetTempFileName()
$tmpGitErr = [System.IO.Path]::GetTempFileName()
try {
    $gitAdd = Start-Process -FilePath "git" -ArgumentList $gitAddArgs -WorkingDirectory $Project -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput $tmpGitOut -RedirectStandardError $tmpGitErr
    if ($gitAdd.ExitCode -ne 0) {
        $errText = Get-Content -LiteralPath $tmpGitErr -Raw -ErrorAction SilentlyContinue
        Write-Host "[error] git add failed: $errText" -ForegroundColor Red
        exit $gitAdd.ExitCode
    }
} finally {
    Remove-Item -LiteralPath $tmpGitOut,$tmpGitErr -ErrorAction SilentlyContinue
}

$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "[ok] no changes to publish" -ForegroundColor Green
    exit 0
}

# DryRun
# Commit message
if ([string]::IsNullOrWhiteSpace($Message)) {
    $today = Get-Date -Format "yyyy-MM-dd"
    $Message = "daily: EOD Active Watch online_v2 갱신 $today"
}
git commit -m $Message
Write-Host "[ok] commit complete: $Message" -ForegroundColor Green

# Push 결정
$shouldPush = $false
if ($Push) { $shouldPush = $true }
elseif ($NoPush) { $shouldPush = $false }
elseif ($env:CLOSINGBELL_ONLINE_V2_GIT_PUSH -eq "true") { $shouldPush = $true }

if ($shouldPush) {
    git push
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[ok] git push succeeded. Streamlit Cloud refresh should be triggered." -ForegroundColor Green
        # Health publish 기록
        if (Test-Path $HealthDir) {
            $today = Get-Date -Format "yyyyMMdd"
            $log = Join-Path $HealthDir "publish_log_$today.txt"
            "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss'))  $Message" | Out-File -FilePath $log -Append -Encoding utf8
        }
    } else {
        Write-Host "[error] git push failed (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} else {
    Write-Host "[ok] commit only. To enable push:" -ForegroundColor Cyan
    Write-Host '       use -Push or set CLOSINGBELL_ONLINE_V2_GIT_PUSH=true' -ForegroundColor Cyan
}
