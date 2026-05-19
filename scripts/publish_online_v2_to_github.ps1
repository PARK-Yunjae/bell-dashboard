param(
    [string]$Message = "",
    [switch]$Push,
    [switch]$NoPush,
    [switch]$DryRun,
    [switch]$SkipFreshnessGuard
)

# ClosingBell BellGuard online_v2 GitHub publish 자동화.
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
#   4. BellGuard D0 strict manifest 가 오늘 날짜/Top3 3개/웹훅 준비 상태일 때만 publish

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

# === 안전장치 0: 오늘 BellGuard 데이터가 준비됐는지 확인 ===
if (-not $SkipFreshnessGuard) {
    $todayIso = Get-Date -Format "yyyy-MM-dd"
    $manifestPath = Join-Path $Project "data\closingbell\online_v2\latest\bellguard_d0_strict_1y\bellguard_d0_strict_manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        Write-Host "[skip] BellGuard manifest is missing: $manifestPath" -ForegroundColor Yellow
        exit 0
    }
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Write-Host "[skip] BellGuard manifest parse failed: $($_.Exception.Message)" -ForegroundColor Yellow
        exit 0
    }
    $latestSignalDate = [string]$manifest.latest_signal_date
    $top3Rows = [int]$manifest.latest_top3_rows
    $webhookReady = [bool]$manifest.webhook_ready
    $datasetName = [string]$manifest.dataset_name
    $generator = [string]$manifest.generator
    $selectionPolicy = [string]$manifest.selection_policy
    $scoreModelVersion = [string]$manifest.score_model_version
    $sourceMaxDate = ""
    if ($manifest.source_manifest -and $manifest.source_manifest.event_max_d0_date) {
        $sourceMaxDate = [string]$manifest.source_manifest.event_max_d0_date
    }
    if ($datasetName -ne "bellguard_d0_strict_1y") {
        Write-Host "[skip] BellGuard dataset mismatch: dataset=$datasetName" -ForegroundColor Yellow
        exit 0
    }
    if (-not $generator.Contains("build_bellguard_d0_strict_dashboard_20260517.py")) {
        Write-Host "[skip] BellGuard generator is not the operational Codex builder: generator=$generator" -ForegroundColor Yellow
        exit 0
    }
    if (-not $selectionPolicy.StartsWith("active_d0_3d_pool")) {
        Write-Host "[skip] BellGuard selection policy mismatch: policy=$selectionPolicy" -ForegroundColor Yellow
        exit 0
    }
    if (-not $selectionPolicy.Contains("signal-date")) {
        Write-Host "[skip] BellGuard selection policy is not signal-context: policy=$selectionPolicy" -ForegroundColor Yellow
        exit 0
    }
    if (-not $scoreModelVersion.StartsWith("BELLGUARD_SIGNAL_CONTEXT")) {
        Write-Host "[skip] BellGuard score model mismatch: score_model_version=$scoreModelVersion" -ForegroundColor Yellow
        exit 0
    }
    if ($sourceMaxDate -and $sourceMaxDate -ne $latestSignalDate) {
        Write-Host "[skip] BellGuard source max date mismatch: source=$sourceMaxDate latest=$latestSignalDate" -ForegroundColor Yellow
        exit 0
    }
    if ($latestSignalDate -ne $todayIso) {
        Write-Host "[skip] BellGuard latest date mismatch: latest=$latestSignalDate today=$todayIso" -ForegroundColor Yellow
        exit 0
    }
    if ($top3Rows -ne 3 -or -not $webhookReady) {
        Write-Host "[skip] BellGuard publish guard failed: top3=$top3Rows webhook_ready=$webhookReady" -ForegroundColor Yellow
        exit 0
    }
    Write-Host "[ok] BellGuard freshness guard passed: $latestSignalDate Top3=$top3Rows model=$scoreModelVersion" -ForegroundColor Green
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

# === PDF 자동 재생성 (manifest KPI 기반 동적 빌더, 데이터 변경 반영) ===
$VenvPy = "C:\Coding\projects\_venvs\closingbell-py312\Scripts\python.exe"
if ($DryRun) {
    Write-Host "[dry-run] skipping PDF rebuild" -ForegroundColor Cyan
} elseif (Test-Path $VenvPy) {
    $pdfBuilders = @(
        "scripts\build_bellguard_reach_rate_brief.py",
        "scripts\build_bellguard_explainer_pdf.py"
    )
    foreach ($builder in $pdfBuilders) {
        if (Test-Path $builder) {
            Write-Host "[pdf] rebuilding $builder ..." -ForegroundColor Cyan
            $tmpOut = [System.IO.Path]::GetTempFileName()
            $tmpErr = [System.IO.Path]::GetTempFileName()
            try {
                $proc = Start-Process -FilePath $VenvPy -ArgumentList @($builder) -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr
                $exitCode = $proc.ExitCode
            } finally {
                Remove-Item -LiteralPath $tmpOut,$tmpErr -ErrorAction SilentlyContinue
            }
            if ($exitCode -ne 0) {
                Write-Host "[warn] PDF build failed: $builder (continuing)" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "[skip] venv python missing, skipping PDF rebuild" -ForegroundColor Yellow
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
    $Message = "daily: BellGuard online_v2 갱신 $today"
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
