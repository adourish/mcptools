#!/usr/bin/env python3
"""
Comprehensive Process New Workflow - V2
Analyzes email threads over 2 weeks with full context and creates single consolidated daily plan
"""

import asyncio
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

from auth_manager import AuthManager
from gmail_tools import GmailTools
from gmail_thread_tools import GmailThreadTools
from comprehensive_analyzer import ComprehensiveAnalyzer
from todoist_tools import TodoistTools
from calendar_tools import CalendarTools
from amplenote_tools import AmplenoteTools

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default environment path (can be overridden via command line)
DEFAULT_ENV_PATH = Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json')

async def process_new_comprehensive(env_path: Path = DEFAULT_ENV_PATH):
    """Execute comprehensive process new workflow with 2-week thread analysis
    
    Args:
        env_path: Path to environments.json file (default: DEFAULT_ENV_PATH)
    """
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE PROCESS NEW WORKFLOW - V2")
    logger.info("Analyzing email threads over 2 weeks with full context")
    logger.info(f"Using environment file: {env_path}")
    logger.info("=" * 80)
    
    # Initialize tools
    auth_manager = AuthManager(env_path)
    gmail = GmailTools(auth_manager)
    thread_tools = GmailThreadTools(gmail)
    analyzer = ComprehensiveAnalyzer(auth_manager)
    todoist = TodoistTools(auth_manager)
    calendar = CalendarTools(auth_manager)
    amplenote = AmplenoteTools(auth_manager)
    
    # Step 1: Fetch email threads from last 2 weeks
    logger.info("\n📧 STEP 1: Fetching email threads (2 week lookback)...")
    all_threads = await thread_tools.get_thread_emails(days=14)
    logger.info(f"   Found {len(all_threads)} total threads")
    
    # Step 2: Filter to priority threads
    logger.info("\n🎯 STEP 2: Identifying priority threads...")
    priority_threads = thread_tools.get_priority_threads(all_threads, max_threads=15)
    logger.info(f"   Selected {len(priority_threads)} priority threads for analysis")
    
    # Step 3: Analyze each priority thread comprehensively
    logger.info("\n🔍 STEP 3: Analyzing threads comprehensively...")
    thread_analyses = []
    
    for i, (subject, emails) in enumerate(priority_threads.items(), 1):
        logger.info(f"\n   Analyzing thread {i}/{len(priority_threads)}: {subject}")
        logger.info(f"      - {len(emails)} emails in thread")
        logger.info(f"      - Latest from: {emails[-1].get('from', 'Unknown')}")
        
        analysis = await analyzer.analyze_email_thread(emails, subject)
        thread_analyses.append(analysis)
        
        # Log key findings
        logger.info(f"      ✓ Priority: {analysis['priority'].upper()}")
        logger.info(f"      ✓ Action items: {len(analysis['action_items'])}")
        logger.info(f"      ✓ Follow-up needed: {'YES' if analysis['follow_up_needed'] else 'NO'}")
        if analysis['action_items']:
            logger.info(f"      ✓ First action: {analysis['action_items'][0][:80]}")
    
    # Step 4: Get tasks and calendar
    logger.info("\n✅ STEP 4: Fetching Todoist tasks...")
    tasks = await todoist.get_tasks()
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = [t for t in tasks if t.get('due') and t.get('due', {}).get('date') == today]
    logger.info(f"   Found {len(today_tasks)} tasks due today")
    
    logger.info("\n📅 STEP 5: Fetching calendar events...")
    events = await calendar.get_events(days_ahead=7)  # Get full week
    today_events = [e for e in events if e.get('date') == datetime.now().strftime("%Y-%m-%d")]
    logger.info(f"   Found {len(today_events)} events today")
    logger.info(f"   Found {len(events)} events in next 7 days")
    
    # Step 5: Create comprehensive summary
    logger.info("\n📝 STEP 6: Creating comprehensive daily summary...")
    comprehensive_summary = await analyzer.create_comprehensive_daily_summary(
        thread_analyses,
        today_tasks,
        today_events
    )
    
    logger.info(f"\n{'=' * 80}")
    logger.info("COMPREHENSIVE DAILY SUMMARY")
    logger.info(f"{'=' * 80}")
    logger.info(f"\n{comprehensive_summary}\n")
    
    # Step 6: Create detailed breakdown for Amplenote
    logger.info("\n📋 STEP 7: Preparing detailed breakdown...")
    
    detailed_breakdown = {
        "summary": comprehensive_summary,
        "generated_at": datetime.now().isoformat(),
        "threads_analyzed": len(thread_analyses),
        "high_priority": [],
        "medium_priority": [],
        "low_priority": [],
        "follow_ups_needed": [],
        "tasks_today": today_tasks,
        "events_today": today_events
    }
    
    # Categorize analyses
    for analysis in thread_analyses:
        item = {
            "subject": analysis['thread_subject'],
            "summary": analysis['summary'],
            "outcome": analysis['outcome'],
            "action_items": analysis['action_items'],
            "follow_up": analysis['follow_up_reason'] if analysis['follow_up_needed'] else None,
            "context": analysis['context'],
            "latest_from": analysis['latest_sender'],
            "email_count": analysis['email_count']
        }
        
        if analysis['priority'] == 'high':
            detailed_breakdown['high_priority'].append(item)
        elif analysis['priority'] == 'medium':
            detailed_breakdown['medium_priority'].append(item)
        else:
            detailed_breakdown['low_priority'].append(item)
        
        if analysis['follow_up_needed']:
            detailed_breakdown['follow_ups_needed'].append(item)
    
    # Log breakdown
    logger.info(f"   🔴 High priority: {len(detailed_breakdown['high_priority'])} threads")
    logger.info(f"   ⚠️  Medium priority: {len(detailed_breakdown['medium_priority'])} threads")
    logger.info(f"   ℹ️  Low priority: {len(detailed_breakdown['low_priority'])} threads")
    logger.info(f"   📧 Follow-ups needed: {len(detailed_breakdown['follow_ups_needed'])} threads")
    
    # Step 7: Save comprehensive output
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(detailed_breakdown, f, indent=2)
    
    logger.info(f"\n💾 Full analysis saved to: {output_file}")
    
    # Step 8: Create individual Todoist tasks for each action
    logger.info("\n📋 STEP 8: Creating individual Todoist tasks...")
    
    try:
        # Delete old daily plan tasks first
        all_tasks = await todoist.get_tasks()
        for task in all_tasks:
            content = task.get('content', '')
            labels = task.get('labels', [])
            if content.startswith('📋') or 'daily-plan' in labels:
                await todoist.delete_task(task['id'])
                logger.info(f"   Deleted old task: {content[:50]}")
        
        created_count = 0
        
        # Create tasks for high priority items
        for item in detailed_breakdown['high_priority']:
            if item.get('action_items'):
                action = item['action_items'][0]
                sender = item.get('latest_from', 'Unknown').split('<')[0].strip()
                
                # Build description with context
                description_parts = [
                    f"From: {sender}",
                    f"Subject: {item['subject']}",
                    "",
                    f"Why: {item['context']}",
                    "",
                    f"Outcome: {item['outcome']}"
                ]
                
                # Add additional actions if any
                if len(item['action_items']) > 1:
                    description_parts.append("")
                    description_parts.append("Additional actions:")
                    for additional_action in item['action_items'][1:]:
                        description_parts.append(f"• {additional_action}")
                
                description = "\n".join(description_parts)
                
                await todoist.create_task(
                    content=action,
                    description=description,
                    priority=4,  # High priority (red)
                    due_string='today',
                    labels=['daily-plan']
                )
                created_count += 1
                logger.info(f"   ✅ Created: {action[:60]}")
        
        # Create tasks for medium priority items
        for item in detailed_breakdown['medium_priority'][:3]:  # Top 3 medium
            if item.get('action_items'):
                action = item['action_items'][0]
                sender = item.get('latest_from', 'Unknown').split('<')[0].strip()
                
                description = f"From: {sender}\nSubject: {item['subject']}\n\n{item.get('summary', '')}"
                
                await todoist.create_task(
                    content=action,
                    description=description,
                    priority=3,  # Medium priority (orange)
                    due_string='today',
                    labels=['daily-plan']
                )
                created_count += 1
                logger.info(f"   ✅ Created: {action[:60]}")
        
        # Create tasks for important calendar events (next 3 days)
        logger.info("\n   Creating tasks for calendar events...")
        for event in today_events + [e for e in events if e.get('date') != today]:
            summary = event.get('summary', '')
            date = event.get('date', '')
            time = event.get('time', '')
            
            # Skip recurring events like regular Taekwondo unless there's something special
            if 'Cancelled' in summary or 'Brunch' in summary or 'Pickup' in summary or 'Dr' in summary:
                # Create task for this event
                task_content = summary
                if time and time != 'All day':
                    task_content = f"{summary} at {time}"
                
                description = f"Calendar event on {date}"
                if time:
                    description += f" at {time}"
                
                # Determine priority based on keywords
                priority = 3  # Medium by default
                if 'Cancelled' in summary:
                    priority = 4  # High - need to remember cancellation
                elif 'Dr' in summary or 'Pickup' in summary:
                    priority = 4  # High - important appointments
                
                await todoist.create_task(
                    content=task_content,
                    description=description,
                    priority=priority,
                    due_string=date,
                    labels=['daily-plan', 'calendar']
                )
                created_count += 1
                logger.info(f"   ✅ Created calendar task: {task_content[:60]}")
        
        logger.info(f"\n   ✅ Created {created_count} total tasks")
        
    except Exception as e:
        logger.error(f"   ❌ Error creating Todoist tasks: {e}")
    
    # Step 9: Update Amplenote with detailed analysis
    logger.info("\n📝 STEP 9: Updating Amplenote daily note...")
    try:
        # Create formatted plan for Amplenote
        amplenote_plan = {
            "do_now": [],
            "do_soon": [],
            "monitor": [],
            "reference": [],
            "documents": {},
            "reference_emails": gmail.reference_emails,
            "stats": {
                "threads_analyzed": len(thread_analyses),
                "high_priority": len(detailed_breakdown['high_priority']),
                "medium_priority": len(detailed_breakdown['medium_priority']),
                "follow_ups": len(detailed_breakdown['follow_ups_needed'])
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Add high priority items to do_now
        for item in detailed_breakdown['high_priority']:
            amplenote_plan["do_now"].append({
                "title": item['subject'],
                "source": "Email Thread",
                "summary": item['summary'],
                "outcome": item['outcome'],
                "action_items": item['action_items'],
                "context": item['context'],
                "from": item['latest_from'],
                "email_count": item['email_count'],
                "priority": "high"
            })
        
        # Add medium priority to do_soon
        for item in detailed_breakdown['medium_priority']:
            amplenote_plan["do_soon"].append({
                "title": item['subject'],
                "source": "Email Thread",
                "summary": item['summary'],
                "action_items": item['action_items'],
                "priority": "medium"
            })
        
        amplenote_success = await amplenote.update_daily_note_with_plan(amplenote_plan)
        if amplenote_success:
            logger.info("   ✅ Amplenote daily note updated successfully")
        else:
            logger.warning("   ⚠️  Could not update Amplenote daily note")
            
    except Exception as e:
        logger.error(f"   ❌ Error updating Amplenote: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("COMPREHENSIVE ANALYSIS COMPLETE")
    logger.info("=" * 80)
    
    return detailed_breakdown

async def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='MCP Daily Planning System - Comprehensive email and calendar analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default environment path
  python run_process_new_v2.py
  
  # Use custom environment path
  python run_process_new_v2.py --env-path /path/to/environments.json
  
  # Use custom path with spaces
  python run_process_new_v2.py --env-path "C:\\My Path\\environments.json"
        """
    )
    
    parser.add_argument(
        '--env-path',
        type=Path,
        default=DEFAULT_ENV_PATH,
        help=f'Path to environments.json file (default: {DEFAULT_ENV_PATH})'
    )
    
    args = parser.parse_args()
    
    # Validate environment file exists
    if not args.env_path.exists():
        logger.error(f"Environment file not found: {args.env_path}")
        logger.error(f"Please create the file or specify a different path with --env-path")
        return False
    
    try:
        result = await process_new_comprehensive(env_path=args.env_path)
        return result
    except Exception as e:
        logger.error(f"Error running comprehensive process: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
