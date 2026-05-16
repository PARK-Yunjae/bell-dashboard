param(
    [string]$Message = "Update online V2 dashboard data",
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$Project = "C:\Coding\projects\bell-dashboard"
Set-Location $Project

if (-not (Test-Path -LiteralPath ".git")) {
    Write-Host "[skip] bell-dashboard is not a git repository yet. Run git init and add a remote first."
    exit 0
}

$remote = git remote 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($remote -join ""))) {
    Write-Host "[skip] no git remote configured. Add a GitHub remote before enabling push."
    exit 0
}

git add app.py .gitignore ONLINE_V2_DATA.md STREAMLIT_CLOUD.md README.md `
        requirements.txt CLOUDFLARE_TUNNEL.md data/closingbell/online_v2 scripts
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "[ok] no changes to publish"
    exit 0
}

git commit -m $Message
if ($Push -or $env:CLOSINGBELL_ONLINE_V2_GIT_PUSH -eq "true") {
    git push
} else {
    Write-Host "[ok] committed locally. Set CLOSINGBELL_ONLINE_V2_GIT_PUSH=true or pass -Push to push."
}
