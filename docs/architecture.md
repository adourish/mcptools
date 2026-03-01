# MCP Daily Planning System - Architecture Documentation

## System Overview

The MCP Daily Planning System is an automated workflow that analyzes emails, calendar events, and tasks to create actionable daily plans in Todoist.

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AuthManager                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ - env_path: Path                                                         │
│ - env_config: Dict                                                       │
│ - _gmail_creds: Credentials                                              │
│ - _todoist_token: str                                                    │
│ - _amplenote_token: str                                                  │
│ - _openrouter_key: str                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│ + get_gmail_credentials() -> Credentials                                 │
│ + get_todoist_token() -> str                                             │
│ + get_amplenote_token() -> str                                           │
│ + get_openrouter_key() -> str                                            │
│ + refresh_amplenote_token() -> str                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    △
                                    │ uses
                    ┌───────────────┼───────────────┐
                    │               │               │
        ┌───────────▼──────┐  ┌────▼─────┐  ┌──────▼──────┐
        │   GmailTools     │  │TodoistTools│ │CalendarTools│
        ├──────────────────┤  ├───────────┤  ├─────────────┤
        │- auth_manager    │  │- auth_mgr │  │- auth_mgr   │
        │- service         │  │- base_url │  │- service    │
        ├──────────────────┤  ├───────────┤  ├─────────────┤
        │+ search()        │  │+ get_tasks│  │+ get_events │
        │+ get_email()     │  │+ create   │  │             │
        │+ get_urgent()    │  │+ delete   │  │             │
        └──────────────────┘  └───────────┘  └─────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │ used by
                    ┌───────────────▼───────────────┐
                    │   GmailThreadTools             │
                    ├────────────────────────────────┤
                    │ - gmail_tools: GmailTools      │
                    ├────────────────────────────────┤
                    │ + group_emails_by_thread()     │
                    │ + get_priority_threads()       │
                    │ + calculate_thread_priority()  │
                    └────────────────────────────────┘
                                    │
                                    │ provides threads to
                    ┌───────────────▼───────────────┐
                    │  ComprehensiveAnalyzer         │
                    ├────────────────────────────────┤
                    │ - openrouter_key: str          │
                    ├────────────────────────────────┤
                    │ + analyze_email_thread()       │
                    │ + create_daily_summary()       │
                    │ - _build_thread_context()      │
                    │ - _parse_analysis()            │
                    │ - _fallback_analysis()         │
                    └────────────────────────────────┘
                                    │
                                    │ analysis used by
                    ┌───────────────▼───────────────┐
                    │   run_process_new_v2.py        │
                    │   (Main Orchestrator)          │
                    ├────────────────────────────────┤
                    │ Coordinates all components to: │
                    │ 1. Fetch emails (2 weeks)      │
                    │ 2. Group into threads          │
                    │ 3. Analyze with AI             │
                    │ 4. Get calendar events         │
                    │ 5. Create Todoist tasks        │
                    │ 6. Update Amplenote note       │
                    └────────────────────────────────┘
                                    │
                                    │ creates tasks in
                    ┌───────────────▼───────────────┐
                    │      TodoistTools              │
                    │  (Task Management)             │
                    └────────────────────────────────┘
                                    │
                                    │ optionally updates
                    ┌───────────────▼───────────────┐
                    │    AmplenoteTools              │
                    │  (Note Management)             │
                    └────────────────────────────────┘
```

---

## Process Flow

```
START: run_process_new_v2.py
│
├─ STEP 1: Fetch Recent Emails (2 weeks lookback)
│  │
│  ├─ GmailTools.search(query="in:inbox newer_than:14d")
│  ├─ GmailTools.get_email(email_id) for each email
│  └─ Returns: List[Dict] of email objects
│
├─ STEP 2: Group Emails into Threads
│  │
│  ├─ GmailThreadTools.group_emails_by_thread(emails)
│  │  └─ Groups by subject (removes RE:, FW: prefixes)
│  │
│  ├─ GmailThreadTools.get_priority_threads(threads, max=15)
│  │  └─ Scores threads by:
│  │     - Recency (newer = higher score)
│  │     - Email count (more emails = higher score)
│  │     - Sender importance (whitelist/blacklist)
│  │
│  └─ Returns: Top 15 priority threads
│
├─ STEP 3: Analyze Each Thread with AI
│  │
│  ├─ For each thread:
│  │  │
│  │  ├─ ComprehensiveAnalyzer.analyze_email_thread(emails, subject)
│  │  │  │
│  │  │  ├─ Build thread context (chronological emails)
│  │  │  │
│  │  │  ├─ Send to OpenRouter API (GPT-4o-mini)
│  │  │  │  └─ Prompt: Extract specific actions, avoid spam
│  │  │  │
│  │  │  ├─ Parse AI response:
│  │  │  │  - Summary (what happened)
│  │  │  │  - Outcome (what's resolved)
│  │  │  │  - Action items (specific, concrete only)
│  │  │  │  - Follow-up needed (yes/no + who/when)
│  │  │  │  - Priority (high/medium/low)
│  │  │  │  - Context (why it matters)
│  │  │  │
│  │  │  └─ Returns: Analysis Dict
│  │
│  └─ Returns: List[Analysis] for all threads
│
├─ STEP 4: Fetch Todoist Tasks
│  │
│  ├─ TodoistTools.get_tasks()
│  ├─ Filter tasks due today
│  └─ Returns: List[Task]
│
├─ STEP 5: Fetch Calendar Events
│  │
│  ├─ CalendarTools.get_events(days_ahead=7)
│  ├─ Filter events for today
│  └─ Returns: List[Event]
│
├─ STEP 6: Create Daily Summary
│  │
│  ├─ ComprehensiveAnalyzer.create_comprehensive_daily_summary()
│  │  └─ Extracts top 3 action items from high/medium priority threads
│  │
│  └─ Returns: Clean summary string
│
├─ STEP 7: Prepare Detailed Breakdown
│  │
│  ├─ Categorize threads by priority:
│  │  - High priority (urgent/time-sensitive)
│  │  - Medium priority (important but not urgent)
│  │  - Low priority (FYI/informational)
│  │  - Follow-ups needed
│  │
│  ├─ Save to JSON file (output/comprehensive_analysis_*.json)
│  │
│  └─ Returns: Breakdown Dict
│
├─ STEP 8: Create Individual Todoist Tasks
│  │
│  ├─ Delete old tasks with 'daily-plan' label
│  │  └─ TodoistTools.delete_task(task_id)
│  │
│  ├─ Create tasks for HIGH priority email threads:
│  │  │
│  │  ├─ For each high priority item with action_items:
│  │  │  │
│  │  │  ├─ Task content = First action item
│  │  │  ├─ Description = From, Subject, Why, Outcome
│  │  │  ├─ Priority = 4 (red - high)
│  │  │  ├─ Due = today
│  │  │  ├─ Labels = ['daily-plan']
│  │  │  │
│  │  │  └─ TodoistTools.create_task(...)
│  │
│  ├─ Create tasks for MEDIUM priority email threads (top 3):
│  │  │
│  │  │  ├─ Priority = 3 (orange - medium)
│  │  │  ├─ Due = today
│  │  │  └─ Labels = ['daily-plan']
│  │
│  ├─ Create tasks for CALENDAR events:
│  │  │
│  │  ├─ Filter important events:
│  │  │  - Contains "Cancelled" → Priority 4 (high)
│  │  │  - Contains "Dr" or "Pickup" → Priority 4 (high)
│  │  │  - Contains "Brunch" → Priority 3 (medium)
│  │  │  - Skip routine recurring events
│  │  │
│  │  ├─ For each important event:
│  │  │  │
│  │  │  ├─ Task content = Event summary + time
│  │  │  ├─ Description = Calendar event on [date] at [time]
│  │  │  ├─ Due = event date
│  │  │  ├─ Labels = ['daily-plan', 'calendar']
│  │  │  │
│  │  │  └─ TodoistTools.create_task(...)
│  │
│  └─ Log: Created X total tasks
│
├─ STEP 9: Update Amplenote Daily Note (Optional)
│  │
│  ├─ AmplenoteTools.find_or_create_daily_note()
│  │
│  ├─ Build markdown content:
│  │  - Header with date
│  │  - Today's Actions section
│  │  - This Week section
│  │  - Footer with stats
│  │
│  ├─ Delete old daily plan note
│  ├─ Create new note with content
│  │
│  └─ Returns: Success/Failure
│
└─ END: Log completion summary
   - X threads analyzed
   - X tasks created
   - Output saved to JSON
```

---

## Key Design Patterns

### 1. **Dependency Injection**
- `AuthManager` is injected into all tool classes
- Centralizes credential management
- Enables easy testing and credential rotation

### 2. **Lazy Loading**
- API keys loaded only when needed
- Reduces startup time
- Prevents unnecessary API calls

### 3. **Fallback Strategy**
- If AI analysis fails, use simple fallback
- Ensures system always produces output
- Graceful degradation

### 4. **Cleanup Pattern**
- Delete old tasks before creating new ones
- Uses `daily-plan` label for identification
- Prevents task accumulation

### 5. **Priority-Based Processing**
- Threads scored and ranked
- Only top 15 threads analyzed (cost optimization)
- High priority items processed first

---

## Data Flow

```
Gmail API
   │
   ├─→ Raw Emails (2 weeks)
   │
   └─→ GmailThreadTools
          │
          ├─→ Grouped Threads
          │
          └─→ Priority Threads (top 15)
                 │
                 └─→ ComprehensiveAnalyzer
                        │
                        ├─→ OpenRouter API (GPT-4o-mini)
                        │      │
                        │      └─→ AI Analysis
                        │             - Summary
                        │             - Action Items
                        │             - Priority
                        │             - Context
                        │
                        └─→ Structured Analysis
                               │
                               ├─→ JSON Output File
                               │
                               └─→ Todoist Tasks
                                      │
                                      └─→ DakBoard Display
```

---

## Configuration Files

### environments.json
```json
{
  "environments": {
    "todoist": {
      "credentials": {
        "apiToken": "..."
      }
    },
    "amplenote": {
      "oauth": {
        "accessToken": "...",
        "refreshToken": "..."
      }
    },
    "openrouter": {
      "credentials": {
        "apiKey": "sk-or-v1-..."
      }
    }
  }
}
```

### Labels Used
- `daily-plan` - All auto-generated tasks
- `calendar` - Calendar-based tasks

---

## API Integrations

1. **Gmail API** - Fetch emails
2. **Google Calendar API** - Fetch events
3. **Todoist API v1** - Task management
4. **Amplenote API v4** - Note management (optional)
5. **OpenRouter API** - AI analysis (GPT-4o-mini)

---

## Output Artifacts

1. **Todoist Tasks** - Individual actionable items
2. **JSON Analysis** - `output/comprehensive_analysis_YYYYMMDD_HHMMSS.json`
3. **Amplenote Note** - Optional daily plan note
4. **Console Logs** - Detailed execution trace

---

## Error Handling

- **API Failures**: Fallback to simple analysis
- **Token Expiry**: Automatic token refresh (Amplenote)
- **Missing Data**: Graceful defaults
- **Rate Limits**: Not currently handled (future improvement)

---

## Performance Considerations

- **Email Lookback**: 14 days (configurable)
- **Thread Limit**: Top 15 threads (cost optimization)
- **AI Model**: GPT-4o-mini (fast, cheap)
- **Max Tokens**: 500 per analysis
- **Execution Time**: ~30-60 seconds total

---

## Future Improvements

1. Rate limiting and retry logic
2. Caching of AI analyses
3. User-configurable filters
4. Support for multiple calendars
5. Integration with more task managers
6. Web UI for configuration
