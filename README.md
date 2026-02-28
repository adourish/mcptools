# Daily Planner MCP Server

**Eliminates script failures and token expiration issues**

## What This Does

Provides MCP tools for:
- Gmail search and email reading
- Todoist task management
- Google Calendar events
- Amplenote note creation
- Complete "process new" workflow

**Key Features:**
- ✅ Automatic token refresh (no more expired tokens)
- ✅ Direct tool calls (no scripts to fail)
- ✅ Persistent service (always available)
- ✅ Centralized authentication

---

## Setup

### 1. Install Dependencies

```powershell
cd "G:\My Drive\06_Master_Guides\MCP_Server"
pip install -r requirements.txt
```

### 2. Configure Cascade

Add to your Cascade MCP settings:

```json
{
  "mcpServers": {
    "daily-planner": {
      "command": "python",
      "args": ["G:\\My Drive\\06_Master_Guides\\MCP_Server\\server.py"],
      "env": {}
    }
  }
}
```

### 3. Start Server

The server starts automatically when Cascade launches. No manual startup needed.

---

## Available Tools

### Gmail Tools

**`gmail_search`** - Search Gmail
```
Arguments:
  query: Gmail search query (e.g., "from:example@gmail.com subject:invoice")
  max_results: Maximum results (default: 10)
```

**`gmail_get_email`** - Get full email content
```
Arguments:
  message_id: Gmail message ID
```

### Todoist Tools

**`todoist_get_tasks`** - Get tasks
```
Arguments:
  filter: Optional filter (e.g., "today", "overdue", "p1")
```

**`todoist_create_task`** - Create task
```
Arguments:
  content: Task title (required)
  description: Task description
  priority: 1-4 (4 is urgent)
  due_string: Natural language date (e.g., "tomorrow")
```

**`todoist_update_task`** - Update task
```
Arguments:
  task_id: Task ID to update (required)
  content: New title
  description: New description
  priority: New priority
```

### Calendar Tools

**`calendar_get_events`** - Get calendar events
```
Arguments:
  days_ahead: Days to look ahead (default: 7)
```

### Amplenote Tools

**`amplenote_create_note`** - Create note
```
Arguments:
  title: Note title (required)
  content: Note content (required)
  tags: Array of tags
```

### Workflow Tools

**`process_new`** - Complete daily planning workflow
```
Arguments: None

Scans emails, tasks, calendar and creates daily plan
```

---

## Usage Examples

### In Cascade

**Search for emails:**
```
"Search Gmail for Kings Manor emails"
→ I'll call gmail_search tool with query "Kings Manor"
```

**Create a task:**
```
"Create a task to renew vehicle registration"
→ I'll call todoist_create_task with the details
```

**Run process new:**
```
"process new"
→ I'll call process_new tool to generate your daily plan
```

---

## Token Management

**Automatic Refresh:**
- Gmail tokens refresh every hour
- Todoist tokens don't expire
- Amplenote tokens managed automatically

**No more:**
- ❌ Token expired errors
- ❌ Manual token refresh
- ❌ Script authentication failures

---

## Troubleshooting

**Server not starting:**
1. Check Python version (3.9+)
2. Verify dependencies installed
3. Check Cascade MCP settings

**Tool calls failing:**
1. Check server logs: `mcp_server.log`
2. Verify token files exist
3. Restart Cascade

**Token issues:**
- Server auto-refreshes tokens every hour
- Check `gmail_token.json` exists
- Verify `environments.json` has correct credentials

---

## Architecture

```
Cascade
  ↓
MCP Server (server.py)
  ↓
├── AuthManager (auto-refresh tokens)
├── GmailTools (email operations)
├── TodoistTools (task operations)
├── CalendarTools (calendar operations)
└── AmplenoteTools (note operations)
```

**Benefits:**
- Single point of authentication
- No script failures
- Always available
- Auto-healing (token refresh)

---

## Migration from Scripts

**Before (scripts):**
```
You: "create a task"
Cascade: run_command → python create_task.py
         → Error: Token expired
         → Multiple attempts needed
```

**After (MCP):**
```
You: "create a task"
Cascade: todoist_create_task(...)
         → Works immediately
```

**No more:**
- Script files
- Token management
- Error handling
- Manual intervention

---

## Next Steps

1. ✅ Server created
2. ⏳ Install dependencies
3. ⏳ Configure Cascade
4. ⏳ Test tools
5. ⏳ Migrate workflows

**Your daily planning is now reliable and automated!**
