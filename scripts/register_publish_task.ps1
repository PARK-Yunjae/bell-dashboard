# BellGuard GitHub publish automation - env var + Task Scheduler registration.
#
# Registers:
#   1. User env CLOSINGBELL_ONLINE_V2_GIT_PUSH = "true"
#   2. Windows Task Scheduler "ClosingBell_Publish_GitHub_1910" on weekdays at 19:10
#
# Usage:
#   .\scripts\register_publish_task.ps1
#
# Unregister:
#   .\scripts\register_publish_task.ps1 -Unregister

param(
    [switch]$Unregister,
    [string]$PublishTime = "19:10"
)

$ErrorActionPreference = "Stop"
$TaskName = "ClosingBell_Publish_GitHub_1910"
$LegacyTaskNames = @("ClosingBell_Publish_GitHub_1715")
$Script = "C:\Coding\projects\bell-dashboard\scripts\publish_online_v2_to_github.ps1"

if ($Unregister) {
    [Environment]::SetEnvironmentVariable("CLOSINGBELL_ONLINE_V2_GIT_PUSH", $null, "User")
    Write-Host "[ok] user env CLOSINGBELL_ONLINE_V2_GIT_PUSH removed"

    $targets = @($TaskName) + $LegacyTaskNames
    foreach ($target in $targets) {
        $exist = Get-ScheduledTask -TaskName $target -ErrorAction SilentlyContinue
        if ($exist) {
            Unregister-ScheduledTask -TaskName $target -Confirm:$false
            Write-Host "[ok] Task '$target' unregistered"
        } else {
            Write-Host "[skip] Task '$target' is not registered"
        }
    }
    exit 0
}

[Environment]::SetEnvironmentVariable("CLOSINGBELL_ONLINE_V2_GIT_PUSH", "true", "User")
Write-Host "[ok] user env CLOSINGBELL_ONLINE_V2_GIT_PUSH=true set" -ForegroundColor Green
Write-Host "     New PowerShell sessions will see this value automatically."

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`"" `
    -WorkingDirectory "C:\Coding\projects\bell-dashboard"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $PublishTime
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$UserId = if ($env:USERDOMAIN) { "$env:USERDOMAIN\$env:USERNAME" } else { $env:USERNAME }
$Principal = New-ScheduledTaskPrincipal -UserId $UserId -LogonType Interactive

$exist = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($exist) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[info] existing Task '$TaskName' removed before re-register"
}
foreach ($legacy in $LegacyTaskNames) {
    $legacyTask = Get-ScheduledTask -TaskName $legacy -ErrorAction SilentlyContinue
    if ($legacyTask) {
        Unregister-ScheduledTask -TaskName $legacy -Confirm:$false
        Write-Host "[info] legacy Task '$legacy' removed"
    }
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Description "Bell Dashboard online_v2 GitHub publish after BellGuard daily refresh" `
    -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal

Write-Host "[ok] Task Scheduler registered: $TaskName (weekdays $PublishTime)" -ForegroundColor Green
Write-Host ""
Write-Host "Check:"
Write-Host "  Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo"
Write-Host ""
Write-Host "Manual test:"
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host ""
Write-Host "Unregister:"
Write-Host "  .\scripts\register_publish_task.ps1 -Unregister"
