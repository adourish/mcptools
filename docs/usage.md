# MCP Daily Planning System - Usage Guide

## Quick Start

### Basic Command

```bash
python run_process_new_v2.py
```

That's it! The script will:
1. Fetch emails from the last 2 weeks
2. Analyze them with AI
3. Get calendar events for the next 7 days
4. Create individual Todoist tasks
5. Optionally update Amplenote note

---

## Prerequisites

### 1. Environment File

The script looks for credentials at a **hardcoded path**:

```
G:\My Drive\03_Areas\Keys\Environments\environments.json
```

**If you need a different path**, you must edit `run_process_new_v2.py` line 27:

```python
ENV_PATH = Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json')
```

### 2. Required Credentials in environments.json

```json
{
  "environments": {
    "gmail": {
      "credentials": {
        "installed": {
          "client_id": "your-client-id",
          "client_secret": "your-client-secret",
          "redirect_uris": ["http://localhost"]
        }
      }
    },
    "todoist": {
      "credentials": {
        "apiToken": "your-todoist-token"
      }
    },
    "amplenote": {
      "oauth": {
        "accessToken": "your-amplenote-token",
        "refreshToken": "your-refresh-token",
        "expiresAt": "2026-03-01T00:00:00Z"
      }
    },
    "openrouter": {
      "credentials": {
        "apiKey": "sk-or-v1-your-key"
      }
    }
  }
}
```

### 3. Gmail Token

First run will prompt for Gmail OAuth:
- Browser will open for authorization
- Token saved to: `G:\My Drive\03_Areas\Keys\Gmail\token.json`
- Subsequent runs use saved token

---

## Command Line Options

### Current Implementation

**No command line arguments supported.** The script uses hardcoded defaults:

| Setting | Value | Location in Code |
|---------|-------|------------------|
| Environment file | `G:\My Drive\03_Areas\Keys\Environments\environments.json` | Line 27 |
| Email lookback | 14 days | Line 48 |
| Max threads | 15 | Line 52 |
| Calendar lookahead | 7 days | Line 82 |
| Output directory | `./output/` | Line 144 |

### To Change Settings

Edit `run_process_new_v2.py` directly:

```python
# Line 48 - Change email lookback period
emails = await gmail.search(query="in:inbox newer_than:14d")  # Change 14d

# Line 52 - Change max threads to analyze
priority_threads = thread_tools.get_priority_threads(all_threads, max_threads=15)  # Change 15

# Line 82 - Change calendar lookahead
events = await calendar.get_events(days_ahead=7)  # Change 7

# Line 144 - Change output directory
output_dir = Path(__file__).parent / "output"  # Change "output"
```

---

## Running the Process

### Method 1: Direct Python

```bash
cd C:\Users\sol90\CascadeProjects\mcptools
python run_process_new_v2.py
```

### Method 2: From Any Directory

```bash
python C:\Users\sol90\CascadeProjects\mcptools\run_process_new_v2.py
```

### Method 3: Windows Scheduled Task

Create a scheduled task to run automatically:

```powershell
# Task name
$taskName = "Daily Planning Process"

# Action
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\sol90\CascadeProjects\mcptools\run_process_new_v2.py" -WorkingDirectory "C:\Users\sol90\CascadeProjects\mcptools"

# Trigger (daily at 6 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 6am

# Register task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger
```

---

## Output

### Console Output

```
================================================================================
COMPREHENSIVE PROCESS NEW WORKFLOW - V2
Analyzing email threads over 2 weeks with full context
================================================================================

🔍 STEP 1: Fetching recent emails (2 weeks lookback)...
   Found 127 emails in last 2 weeks

🎯 STEP 2: Identifying priority threads...
   Grouped into 42 threads
   Selected 15 priority threads for analysis

🔍 STEP 3: Analyzing threads comprehensively...
   Analyzing thread 1/15: Weekly Agenda 3/2-3/6
      - 3 emails in thread
      - Latest from: "Prescott, Lisa K"
      ✓ Priority: MEDIUM
      ✓ Action items: 1
      ✓ Follow-up needed: NO
      ✓ First action: Review the attached agenda for important dates...

[... continues for all threads ...]

✅ STEP 4: Fetching Todoist tasks...
   Found 4 tasks due today

📅 STEP 5: Fetching calendar events...
   Found 0 events today
   Found 6 events in next 7 days

📝 STEP 6: Creating comprehensive daily summary...
   • Review the attached agenda for important dates...
   • Confirm with Sarah Williams whether to proceed...
   • Purchase tickets for "Scream 7" if interested

📋 STEP 7: Preparing detailed breakdown...
    🔴 High priority: 0 threads
    ⚠️  Medium priority: 3 threads
    ℹ️  Low priority: 2 threads
    📧 Follow-ups needed: 3 threads

💾 Full analysis saved to: C:\Users\sol90\CascadeProjects\mcptools\output\comprehensive_analysis_20260228_193030.json

📋 STEP 8: Creating individual Todoist tasks...
   Deleted old task: Review the attached agenda...
   Deleted old task: Confirm with Sarah Williams...
   Deleted old task: Purchase tickets for "Scream 7"...
   ✅ Created: Review the attached agenda for important dates and activities
   ✅ Created: Confirm with Sarah Williams whether to proceed with a higher
   ✅ Created: Purchase tickets for "Scream 7" if interested

   Creating tasks for calendar events...
   ✅ Created calendar task: Brunch with KO at 12:00 PM
   ✅ Created calendar task: Cancelled TKD March 4 Wednesday at 06:30 PM
   ✅ Created calendar task: Couch Pickup at 06:00 AM
   ✅ Created calendar task: Dr Howard at 05:00 PM

   ✅ Created 7 total tasks

📝 STEP 9: Updating Amplenote daily note...
    ✅ Amplenote daily note updated successfully

================================================================================
COMPREHENSIVE ANALYSIS COMPLETE
================================================================================
```

### File Output

**JSON Analysis File:**
- Location: `./output/comprehensive_analysis_YYYYMMDD_HHMMSS.json`
- Contains: Full thread analyses, priorities, action items, context

**Todoist Tasks:**
- Individual tasks created with `daily-plan` label
- High priority (red) for urgent items
- Medium priority (orange) for important items
- Calendar events tagged with `calendar` label

**Amplenote Note (Optional):**
- Title: `📋 Daily Plan`
- Tags: `daily-plan`, `process-new`
- URL logged in console output

---

## Execution Time

Typical execution: **30-60 seconds**

Breakdown:
- Email fetch: ~5 seconds
- Thread grouping: ~1 second
- AI analysis (15 threads): ~20-30 seconds
- Calendar fetch: ~2 seconds
- Task creation: ~5 seconds
- Amplenote update: ~3 seconds

---

## Troubleshooting

### Error: "environments.json not found"

**Problem:** Environment file not at expected path

**Solution:**
```python
# Edit run_process_new_v2.py line 27
ENV_PATH = Path(r'C:\path\to\your\environments.json')
```

### Error: "Gmail token expired"

**Problem:** OAuth token needs refresh

**Solution:**
```bash
# Delete old token
del "G:\My Drive\03_Areas\Keys\Gmail\token.json"

# Run script again - will prompt for re-auth
python run_process_new_v2.py
```

### Error: "OpenRouter API error"

**Problem:** Invalid or missing OpenRouter API key

**Solution:**
1. Check `environments.json` has valid `openrouter.credentials.apiKey`
2. Verify key starts with `sk-or-v1-`
3. Test key at https://openrouter.ai/

### Error: "Amplenote token expired"

**Problem:** Amplenote OAuth token expired

**Solution:**
- Script automatically refreshes token
- If refresh fails, update `environments.json` with new token

### No tasks created

**Problem:** No high/medium priority emails found

**Solution:**
- Check email filters (whitelist/blacklist in `gmail_tools.py`)
- Lower priority threshold
- Increase max threads analyzed (line 52)

---

## Advanced Usage

### Custom Environment Path

Create a wrapper script:

```python
# my_daily_plan.py
import asyncio
from pathlib import Path
from run_process_new_v2 import process_new_comprehensive

# Override ENV_PATH
import run_process_new_v2
run_process_new_v2.ENV_PATH = Path(r'C:\my\custom\path\environments.json')

if __name__ == "__main__":
    asyncio.run(process_new_comprehensive())
```

### Dry Run (No Task Creation)

Comment out task creation:

```python
# Line 193-254 in run_process_new_v2.py
# Comment out the entire task creation block
# await todoist.create_task(...)
```

### Debug Mode

Enable debug logging:

```python
# Line 21 in run_process_new_v2.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Future Enhancements

Planned command line arguments:

```bash
# Not yet implemented
python run_process_new_v2.py \
  --env-path /path/to/environments.json \
  --lookback-days 7 \
  --max-threads 10 \
  --no-amplenote \
  --dry-run
```

To implement, add argument parsing:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--env-path', default=ENV_PATH)
parser.add_argument('--lookback-days', type=int, default=14)
parser.add_argument('--max-threads', type=int, default=15)
parser.add_argument('--no-amplenote', action='store_true')
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()
```
