#!/usr/bin/env python3
"""
MCP Server for Daily Planning Automation
Provides tools for Gmail, Calendar, Todoist, and Amplenote with automatic token management
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from auth_manager import AuthManager
from gmail_tools import GmailTools
from todoist_tools import TodoistTools
from calendar_tools import CalendarTools
from amplenote_tools import AmplenoteTools

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / 'config.json'
ENV_PATH = Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json')

class DailyPlannerMCP:
    """MCP Server for daily planning automation"""
    
    def __init__(self):
        self.server = Server("daily-planner")
        self.auth_manager = AuthManager(ENV_PATH)
        
        # Initialize service tools
        self.gmail = GmailTools(self.auth_manager)
        self.todoist = TodoistTools(self.auth_manager)
        self.calendar = CalendarTools(self.auth_manager)
        self.amplenote = AmplenoteTools(self.auth_manager)
        
        # Register tools
        self._register_tools()
        
        # Start token refresh background task
        self.refresh_task = None
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        # Gmail tools
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="gmail_search",
                    description="Search Gmail for emails matching a query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Gmail search query (e.g., 'from:example@gmail.com subject:invoice')"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="gmail_get_email",
                    description="Get full email content by message ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {
                                "type": "string",
                                "description": "Gmail message ID"
                            }
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="todoist_get_tasks",
                    description="Get tasks from Todoist with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter": {
                                "type": "string",
                                "description": "Todoist filter (e.g., 'today', 'overdue', 'p1')"
                            }
                        }
                    }
                ),
                Tool(
                    name="todoist_create_task",
                    description="Create a new task in Todoist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Task title/content"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional)"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority (1-4, where 4 is urgent)",
                                "default": 1
                            },
                            "due_string": {
                                "type": "string",
                                "description": "Natural language due date (e.g., 'tomorrow', 'next Monday')"
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="todoist_update_task",
                    description="Update an existing Todoist task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to update"
                            },
                            "content": {
                                "type": "string",
                                "description": "New task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "New priority (1-4)"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="calendar_get_events",
                    description="Get calendar events for a date range",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days_ahead": {
                                "type": "integer",
                                "description": "Number of days ahead to fetch (default: 7)",
                                "default": 7
                            }
                        }
                    }
                ),
                Tool(
                    name="amplenote_create_note",
                    description="Create a new note in Amplenote",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Note title"
                            },
                            "content": {
                                "type": "string",
                                "description": "Note content (markdown supported)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags to add to the note"
                            }
                        },
                        "required": ["title", "content"]
                    }
                ),
                Tool(
                    name="process_new",
                    description="Run complete 'process new' workflow - scans emails, tasks, calendar, files and creates daily plan",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "gmail_search":
                    result = await self.gmail.search(
                        arguments["query"],
                        arguments.get("max_results", 10)
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "gmail_get_email":
                    result = await self.gmail.get_email(arguments["message_id"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "todoist_get_tasks":
                    result = await self.todoist.get_tasks(arguments.get("filter"))
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "todoist_create_task":
                    result = await self.todoist.create_task(
                        content=arguments["content"],
                        description=arguments.get("description"),
                        priority=arguments.get("priority", 1),
                        due_string=arguments.get("due_string")
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "todoist_update_task":
                    result = await self.todoist.update_task(
                        task_id=arguments["task_id"],
                        content=arguments.get("content"),
                        description=arguments.get("description"),
                        priority=arguments.get("priority")
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "calendar_get_events":
                    result = await self.calendar.get_events(
                        arguments.get("days_ahead", 7)
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "amplenote_create_note":
                    result = await self.amplenote.create_note(
                        title=arguments["title"],
                        content=arguments["content"],
                        tags=arguments.get("tags", [])
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "process_new":
                    result = await self._process_new()
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _process_new(self) -> dict:
        """Execute complete process new workflow"""
        logger.info("Starting process new workflow")
        
        # Gather all data
        emails = await self.gmail.get_urgent_emails(days=30)
        tasks = await self.todoist.get_tasks()
        events = await self.calendar.get_events(days_ahead=7)
        
        # Categorize and create plan
        plan = {
            "do_now": [],
            "do_soon": [],
            "monitor": [],
            "reference": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Add urgent emails to DO NOW
        for email in emails:
            plan["do_now"].append({
                "title": email["subject"],
                "source": "Email",
                "due": datetime.now().strftime("%Y-%m-%d"),
                "priority": "high"
            })
        
        # Add today's tasks to DO NOW
        for task in tasks:
            if task.get("due"):
                due_date = task["due"].get("date")
                if due_date == datetime.now().strftime("%Y-%m-%d"):
                    plan["do_now"].append({
                        "title": task["content"],
                        "source": "Todoist",
                        "due": due_date,
                        "priority": "high" if task.get("priority", 1) >= 3 else "normal"
                    })
        
        # Add today's events to DO NOW
        for event in events:
            if event.get("date") == datetime.now().strftime("%Y-%m-%d"):
                plan["do_now"].append({
                    "title": event["summary"],
                    "source": "Calendar",
                    "due": event["date"],
                    "time": event.get("time"),
                    "priority": "normal"
                })
        
        logger.info(f"Process new complete: {len(plan['do_now'])} DO NOW items")
        return plan
    
    async def start_token_refresh(self):
        """Start background task to refresh tokens"""
        async def refresh_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # Check every hour
                    await self.auth_manager.refresh_all_tokens()
                    logger.info("Tokens refreshed successfully")
                except Exception as e:
                    logger.error(f"Error refreshing tokens: {e}")
        
        self.refresh_task = asyncio.create_task(refresh_loop())
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Daily Planner MCP Server")
        
        # Start token refresh
        await self.start_token_refresh()
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)

async def main():
    server = DailyPlannerMCP()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
