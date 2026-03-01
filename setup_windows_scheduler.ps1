# MCP Daily Planning - Windows Scheduler Setup
# Run as Administrator

$taskName = "MCP Daily Planning"
$scriptPath = "C:\Users\sol90\CascadeProjects\mcptools\run_process_new_v2.py"
$workingDir = "C:\Users\sol90\CascadeProjects\mcptools"
$logDir = "$workingDir\logs"

# Create logs directory
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Create action with logging
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "$scriptPath > $logDir\scheduler_$(Get-Date -Format 'yyyyMMdd').log 2>&1" `
    -WorkingDirectory $workingDir

# Create triggers
$triggers = @(
    (New-ScheduledTaskTrigger -Daily -At 6am),
    (New-ScheduledTaskTrigger -Daily -At 9am),
    (New-ScheduledTaskTrigger -Daily -At 12pm),
    (New-ScheduledTaskTrigger -Daily -At 3pm),
    (New-ScheduledTaskTrigger -Daily -At 6pm)
)

# Settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Register new task
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $triggers `
    -Settings $settings `
    -Description "Runs MCP Daily Planning analysis every 3 hours (6am, 9am, 12pm, 3pm, 6pm)"

Write-Host "✅ Task '$taskName' created successfully" -ForegroundColor Green
Write-Host "Scheduled times: 6am, 9am, 12pm, 3pm, 6pm" -ForegroundColor Cyan
Write-Host "Logs will be saved to: $logDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test now, run: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
