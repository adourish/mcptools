# Scheduling the MCP Daily Planning System

This guide shows how to run the daily planning process automatically every few hours.

---

## Option 1: Windows Task Scheduler (Recommended for Windows)

### Setup via PowerShell Script

1. **Create the scheduled task:**

```powershell
# Configuration
$taskName = "MCP Daily Planning"
$scriptPath = "C:\Users\sol90\CascadeProjects\mcptools\run_process_new_v2.py"
$workingDir = "C:\Users\sol90\CascadeProjects\mcptools"
$pythonPath = "python"  # or full path like "C:\Python312\python.exe"

# Create action
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# Create triggers (every 3 hours, starting at 6 AM)
$trigger1 = New-ScheduledTaskTrigger -Daily -At 6am
$trigger2 = New-ScheduledTaskTrigger -Daily -At 9am
$trigger3 = New-ScheduledTaskTrigger -Daily -At 12pm
$trigger4 = New-ScheduledTaskTrigger -Daily -At 3pm
$trigger5 = New-ScheduledTaskTrigger -Daily -At 6pm

# Settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register task
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger1,$trigger2,$trigger3,$trigger4,$trigger5 `
    -Settings $settings `
    -Description "Runs MCP Daily Planning analysis every 3 hours"
```

2. **Run the setup script:**

```powershell
# Save as setup_scheduler.ps1 and run
.\setup_scheduler.ps1
```

### Manual Setup via GUI

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: `MCP Daily Planning`
4. Trigger: **Daily**
5. Start time: `6:00 AM`
6. Action: **Start a program**
   - Program: `python`
   - Arguments: `run_process_new_v2.py`
   - Start in: `C:\Users\sol90\CascadeProjects\mcptools`
7. Click **Finish**
8. Right-click the task → **Properties**
9. Go to **Triggers** tab → **New** → Add more triggers for 9am, 12pm, 3pm, 6pm
10. Go to **Settings** tab:
    - ✅ Allow task to be run on demand
    - ✅ Run task as soon as possible after scheduled start is missed
    - ✅ If task fails, restart every: 10 minutes

### Verify Task

```powershell
# List scheduled tasks
Get-ScheduledTask -TaskName "MCP Daily Planning"

# Run task manually to test
Start-ScheduledTask -TaskName "MCP Daily Planning"

# Check last run result
Get-ScheduledTaskInfo -TaskName "MCP Daily Planning"
```

---

## Option 2: Python Scheduler (Cross-Platform)

Create a wrapper script that runs continuously and schedules the process.

### Create `scheduler.py`

```python
#!/usr/bin/env python3
"""
Continuous scheduler for MCP Daily Planning
Runs the process every N hours
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path
from run_process_new_v2 import process_new_comprehensive, DEFAULT_ENV_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_planning_process():
    """Wrapper to run async process in sync context"""
    try:
        logger.info("=" * 80)
        logger.info(f"SCHEDULED RUN STARTING - {datetime.now()}")
        logger.info("=" * 80)
        
        asyncio.run(process_new_comprehensive(env_path=DEFAULT_ENV_PATH))
        
        logger.info("=" * 80)
        logger.info(f"SCHEDULED RUN COMPLETED - {datetime.now()}")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"Scheduled run failed: {e}", exc_info=True)

def main():
    """Main scheduler loop"""
    # Schedule runs every 3 hours
    schedule.every(3).hours.do(run_planning_process)
    
    # Also schedule specific times
    schedule.every().day.at("06:00").do(run_planning_process)
    schedule.every().day.at("09:00").do(run_planning_process)
    schedule.every().day.at("12:00").do(run_planning_process)
    schedule.every().day.at("15:00").do(run_planning_process)
    schedule.every().day.at("18:00").do(run_planning_process)
    
    logger.info("MCP Daily Planning Scheduler started")
    logger.info("Scheduled runs: 6am, 9am, 12pm, 3pm, 6pm")
    logger.info("Press Ctrl+C to stop")
    
    # Run immediately on startup
    run_planning_process()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
```

### Install Dependencies

```bash
pip install schedule
```

### Run Scheduler

```bash
# Run in foreground (for testing)
python scheduler.py

# Run in background (Windows)
start /B python scheduler.py

# Run in background (Linux/Mac)
nohup python scheduler.py > scheduler.log 2>&1 &
```

---

## Option 3: Systemd Service (Linux)

### Create Service File

Create `/etc/systemd/system/mcp-daily-planning.service`:

```ini
[Unit]
Description=MCP Daily Planning Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/mcptools
ExecStart=/usr/bin/python3 /path/to/mcptools/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Create Timer File

Create `/etc/systemd/system/mcp-daily-planning.timer`:

```ini
[Unit]
Description=Run MCP Daily Planning every 3 hours

[Timer]
OnCalendar=*-*-* 06,09,12,15,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable timer
sudo systemctl enable mcp-daily-planning.timer

# Start timer
sudo systemctl start mcp-daily-planning.timer

# Check status
sudo systemctl status mcp-daily-planning.timer

# View logs
journalctl -u mcp-daily-planning -f
```

---

## Option 4: Cron (Linux/Mac)

### Edit Crontab

```bash
crontab -e
```

### Add Cron Jobs

```cron
# Run at 6am, 9am, 12pm, 3pm, 6pm daily
0 6,9,12,15,18 * * * cd /path/to/mcptools && /usr/bin/python3 run_process_new_v2.py >> /var/log/mcp-daily-planning.log 2>&1
```

### Verify Cron

```bash
# List cron jobs
crontab -l

# Check cron logs
grep CRON /var/log/syslog
```

---

## Option 5: Docker Container with Cron

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Add crontab
RUN echo "0 6,9,12,15,18 * * * cd /app && python run_process_new_v2.py >> /var/log/cron.log 2>&1" | crontab -

# Run cron in foreground
CMD ["cron", "-f"]
```

### Build and Run

```bash
# Build image
docker build -t mcp-daily-planning .

# Run container
docker run -d \
  --name mcp-scheduler \
  -v /path/to/environments.json:/app/environments.json \
  mcp-daily-planning

# View logs
docker logs -f mcp-scheduler
```

---

## Recommended Setup

**For Windows users:** Use **Windows Task Scheduler** (Option 1)
- Native, reliable, no extra dependencies
- Survives reboots
- Easy to manage via GUI

**For Linux/Mac users:** Use **Systemd Timer** (Option 3) or **Cron** (Option 4)
- Native to OS
- Reliable and well-tested
- Easy to monitor

**For always-on servers:** Use **Python Scheduler** (Option 2) or **Docker** (Option 5)
- Portable across platforms
- Easy to containerize
- Good for cloud deployments

---

## Monitoring and Logs

### Check Logs

**Windows Task Scheduler:**
```powershell
# View task history
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | 
  Where-Object {$_.Message -like "*MCP Daily Planning*"} | 
  Select-Object -First 10
```

**Python Scheduler:**
```bash
# Redirect output to log file
python scheduler.py > logs/scheduler.log 2>&1
```

**Systemd:**
```bash
journalctl -u mcp-daily-planning -n 50
```

### Email Notifications on Failure

Add to `scheduler.py`:

```python
import smtplib
from email.message import EmailMessage

def send_error_email(error_msg):
    msg = EmailMessage()
    msg['Subject'] = 'MCP Daily Planning Failed'
    msg['From'] = 'scheduler@yourdomain.com'
    msg['To'] = 'you@yourdomain.com'
    msg.set_content(f'Error: {error_msg}')
    
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('your_email', 'your_password')
        smtp.send_message(msg)

# In run_planning_process():
except Exception as e:
    logger.error(f"Scheduled run failed: {e}", exc_info=True)
    send_error_email(str(e))
```

---

## Troubleshooting

### Task Not Running

1. **Check Python path:**
   ```bash
   where python  # Windows
   which python3  # Linux/Mac
   ```

2. **Verify working directory:**
   - Ensure all paths are absolute
   - Check file permissions

3. **Test manually:**
   ```bash
   cd C:\Users\sol90\CascadeProjects\mcptools
   python run_process_new_v2.py
   ```

### Environment File Not Found

If using custom path, update scheduler:

**Windows Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "run_process_new_v2.py --env-path 'C:\path\to\environments.json'" `
    -WorkingDirectory $workingDir
```

**Python Scheduler:**
```python
ENV_PATH = Path(r'C:\custom\path\to\environments.json')
asyncio.run(process_new_comprehensive(env_path=ENV_PATH))
```

### High CPU/Memory Usage

Limit concurrent runs:

```python
import filelock

lock = filelock.FileLock("/tmp/mcp-daily-planning.lock")

def run_planning_process():
    try:
        with lock.acquire(timeout=1):
            asyncio.run(process_new_comprehensive())
    except filelock.Timeout:
        logger.warning("Previous run still in progress, skipping")
```

---

## Best Practices

1. **Start with fewer runs** - Test with 2-3 runs per day first
2. **Monitor for a week** - Ensure stability before increasing frequency
3. **Set up logging** - Always log to file for debugging
4. **Handle failures gracefully** - Don't let one failure stop the scheduler
5. **Test environment file access** - Ensure credentials are accessible
6. **Consider rate limits** - Gmail/Todoist APIs have limits
7. **Use absolute paths** - Avoid relative path issues
8. **Set up alerts** - Know when something goes wrong

---

## Performance Considerations

### API Rate Limits

| Service | Limit | Notes |
|---------|-------|-------|
| Gmail API | 250 quota units/user/second | ~1 billion/day |
| Todoist API | No published limit | Be reasonable |
| OpenRouter | Varies by plan | Check your plan |
| Amplenote | No published limit | Be reasonable |

**Recommendation:** Running every 3 hours (8x/day) is well within limits.

### Execution Time

- Average: 30-60 seconds
- Peak: Up to 2 minutes with 15 threads

**Recommendation:** Set timeout to 5 minutes in scheduler.

---

## Example: Complete Windows Setup Script

Save as `setup_windows_scheduler.ps1`:

```powershell
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
```

Run it:
```powershell
.\setup_windows_scheduler.ps1
```
