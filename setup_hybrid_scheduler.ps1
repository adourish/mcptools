# MCP Daily Planning - Hybrid Scheduler Setup
# This creates a Task Scheduler backup that runs scheduler.py
# If scheduler.py crashes, Task Scheduler will restart it

$taskName = "MCP Daily Planning Scheduler"
$scriptPath = "C:\Users\sol90\CascadeProjects\mcptools\scheduler.py"
$workingDir = "C:\Users\sol90\CascadeProjects\mcptools"
$pythonPath = "python"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MCP DAILY PLANNING - HYBRID SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "This setup creates a Task Scheduler task that:" -ForegroundColor Yellow
Write-Host "  1. Starts scheduler.py when Windows boots" -ForegroundColor Yellow
Write-Host "  2. Restarts scheduler.py if it crashes" -ForegroundColor Yellow
Write-Host "  3. Keeps scheduler.py running continuously" -ForegroundColor Yellow
Write-Host ""

# Create action to run scheduler.py
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# Create trigger - run at system startup
$trigger = New-ScheduledTaskTrigger -AtStartup

# Settings for continuous running with auto-restart
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Register new task
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Runs scheduler.py continuously. Scheduler handles timing (6am, 9am, 12pm, 3pm, 6pm). Task Scheduler ensures it stays running."

Write-Host "✅ Task '$taskName' created successfully" -ForegroundColor Green
Write-Host ""
Write-Host "SETUP COMPLETE" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "What happens now:" -ForegroundColor Yellow
Write-Host "  • scheduler.py will start when Windows boots" -ForegroundColor White
Write-Host "  • It runs continuously and executes at: 6am, 9am, 12pm, 3pm, 6pm" -ForegroundColor White
Write-Host "  • If it crashes, Task Scheduler restarts it within 1 minute" -ForegroundColor White
Write-Host "  • Logs saved to: $workingDir\logs\" -ForegroundColor White
Write-Host ""
Write-Host "To start now (without rebooting):" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host ""
Write-Host "To check if it's running:" -ForegroundColor Cyan
Write-Host "  Get-Process python | Where-Object {`$_.CommandLine -like '*scheduler.py*'}" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Cyan
Write-Host "  Get-Content $workingDir\logs\scheduler_*.log -Tail 50 -Wait" -ForegroundColor White
Write-Host ""
Write-Host "To stop the scheduler:" -ForegroundColor Cyan
Write-Host "  Stop-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host ""
