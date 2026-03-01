# Quick Start Guide - MCP Daily Planning Scheduler

## Option 2: Python Scheduler (Recommended)

This is the **primary method** - a Python script that runs continuously and executes your daily planning at scheduled times.

---

## Simple Setup (Just Python Scheduler)

### 1. Install Dependencies

```bash
pip install schedule filelock
```

### 2. Run the Scheduler

```bash
# Run with default settings (runs now + scheduled times)
python scheduler.py

# Or run in background (Windows)
start /B python scheduler.py
```

**That's it!** The scheduler will:
- ✅ Run immediately
- ✅ Run at 6am, 9am, 12pm, 3pm, 6pm daily
- ✅ Log everything to `logs/scheduler_YYYYMMDD.log`
- ✅ Prevent concurrent runs with lock file

---

## Hybrid Setup (Python + Task Scheduler Backup)

For maximum reliability, use Task Scheduler to keep `scheduler.py` running.

### 1. Run the Setup Script

```powershell
.\setup_hybrid_scheduler.ps1
```

This creates a Task Scheduler task that:
- Starts `scheduler.py` when Windows boots
- Restarts it automatically if it crashes
- Keeps it running 24/7

### 2. Start It Now

```powershell
Start-ScheduledTask -TaskName "MCP Daily Planning Scheduler"
```

---

## How It Works

### Python Scheduler (`scheduler.py`)
- Runs continuously in the background
- Checks every minute if it's time to run
- Executes at: **6am, 9am, 12pm, 3pm, 6pm**
- Uses lock file to prevent overlapping runs
- Logs to `logs/scheduler_YYYYMMDD.log`

### Task Scheduler (Hybrid Only)
- Monitors `scheduler.py` process
- Restarts it if it crashes
- Ensures it starts on boot
- Acts as a "watchdog"

---

## Monitoring

### Check if Scheduler is Running

```powershell
# Check process
Get-Process python | Where-Object {$_.CommandLine -like '*scheduler.py*'}

# Check Task Scheduler status (hybrid only)
Get-ScheduledTask -TaskName "MCP Daily Planning Scheduler"
```

### View Logs

```powershell
# View today's log
Get-Content logs\scheduler_*.log -Tail 50

# Follow log in real-time
Get-Content logs\scheduler_*.log -Tail 50 -Wait
```

### View Statistics

The scheduler tracks:
- Total runs
- Successful runs
- Failed runs
- Last run time
- Last success time
- Last error

Check the logs for stats after each run.

---

## Command Line Options

```bash
# Use custom environment file
python scheduler.py --env-path "C:\Custom\Path\environments.json"

# Don't run immediately on startup (wait for first scheduled time)
python scheduler.py --no-run-now

# See all options
python scheduler.py --help
```

---

## Stopping the Scheduler

### Simple Setup
```bash
# Press Ctrl+C in the terminal
```

### Hybrid Setup
```powershell
# Stop the Task Scheduler task
Stop-ScheduledTask -TaskName "MCP Daily Planning Scheduler"

# Or kill the process
Get-Process python | Where-Object {$_.CommandLine -like '*scheduler.py*'} | Stop-Process
```

---

## Troubleshooting

### Scheduler Not Running

1. **Check if Python is in PATH:**
   ```bash
   python --version
   ```

2. **Check dependencies:**
   ```bash
   pip list | findstr "schedule filelock"
   ```

3. **Run manually to see errors:**
   ```bash
   python scheduler.py
   ```

### Lock File Issues

If you see "Previous run still in progress" repeatedly:

```bash
# Delete the lock file
del scheduler.lock

# Restart scheduler
python scheduler.py
```

### Environment File Not Found

```bash
# Verify path
python scheduler.py --env-path "G:\My Drive\03_Areas\Keys\Environments\environments.json"
```

### High Memory Usage

The scheduler itself uses minimal memory (~50MB). If memory is high, it's likely the planning process running. This is normal and will complete in 1-2 minutes.

---

## What Gets Created

### Files
- `logs/scheduler_YYYYMMDD.log` - Daily log files
- `scheduler.lock` - Prevents concurrent runs (auto-deleted on clean exit)

### Task Scheduler (Hybrid Only)
- Task: "MCP Daily Planning Scheduler"
- Trigger: At system startup
- Action: Run `python scheduler.py`

---

## Comparison: Simple vs Hybrid

| Feature | Simple | Hybrid |
|---------|--------|--------|
| Auto-start on boot | ❌ Manual | ✅ Automatic |
| Auto-restart on crash | ❌ No | ✅ Yes |
| Survives reboot | ❌ No | ✅ Yes |
| Setup complexity | ⭐ Easy | ⭐⭐ Medium |
| Reliability | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |

**Recommendation:** Use **Hybrid** for production, **Simple** for testing.

---

## Next Steps

1. ✅ Run `python scheduler.py` to test
2. ✅ Check logs to verify it works
3. ✅ Run `.\setup_hybrid_scheduler.ps1` for production
4. ✅ Verify it starts on next reboot

---

## Support

- **Logs:** `logs/scheduler_YYYYMMDD.log`
- **Documentation:** `docs/scheduling.md` (full details)
- **Issues:** Check logs first, then review troubleshooting section
