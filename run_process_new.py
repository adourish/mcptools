#!/usr/bin/env python3
"""
Standalone script to run the process_new workflow
This directly calls the daily planner functions without needing the MCP server running
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from auth_manager import AuthManager
from gmail_tools import GmailTools
from todoist_tools import TodoistTools
from calendar_tools import CalendarTools
from amplenote_tools import AmplenoteTools
from drive_tools import DriveTools
from filesystem_tools import FileSystemTools

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ENV_PATH = Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json')

async def process_new():
    """Execute complete process new workflow"""
    logger.info("=" * 60)
    logger.info("Starting PROCESS NEW workflow")
    logger.info("=" * 60)
    
    auth_manager = AuthManager(ENV_PATH)
    gmail = GmailTools(auth_manager)
    todoist = TodoistTools(auth_manager)
    calendar = CalendarTools(auth_manager)
    amplenote = AmplenoteTools(auth_manager)
    drive = DriveTools(auth_manager)
    filesystem = FileSystemTools()
    
    # Disabled: File organization not useful for daily planning
    # logger.info("\n📁 Checking for new files...")
    # file_items, file_status = filesystem.check_new_files()
    # if file_status:
    #     for status in file_status:
    #         logger.info(f"   {status}")
    # else:
    #     logger.info("   No new files to process")
    file_items = []  # Set to empty list since file checking is disabled
    
    logger.info("\n�📧 Fetching urgent emails...")
    emails = await gmail.get_urgent_emails(days=30)
    logger.info(f"   Found {len(emails)} urgent emails")
    logger.info(f"   Found {len(gmail.reference_emails)} reference emails")
    
    logger.info("\n📖 Fetching full email content...")
    detailed_emails = []
    for email in emails:
        try:
            full_email = await gmail.get_email(email['id'])
            detailed_emails.append(full_email)
        except Exception as e:
            logger.warning(f"   Could not fetch full content for: {email['subject']}")
            detailed_emails.append(email)
    emails = detailed_emails
    
    logger.info("\n✅ Fetching Todoist tasks...")
    tasks = await todoist.get_tasks()
    logger.info(f"   Found {len(tasks)} tasks")
    
    logger.info("\n📅 Fetching calendar events...")
    events = await calendar.get_events(days_ahead=7)
    logger.info(f"   Found {len(events)} events")
    
    # Disabled: Google Drive documents not useful for daily planning
    # logger.info("\n📄 Fetching Google Drive documents...")
    # drive_docs = await drive.get_recent_documents(days=7)
    # logger.info(f"   Found {len(drive_docs)} recent documents")
    drive_docs = []  # Set to empty list since Drive fetching is disabled
    
    plan = {
        "do_now": [],
        "do_soon": [],
        "monitor": [],
        "reference": [],
        "documents": {},
        "reference_emails": gmail.reference_emails,
        "stats": {},
        "generated_at": datetime.now().isoformat()
    }
    
    logger.info("\n🎯 Categorizing items...")
    
    # File organization disabled - not useful for daily planning
    # for file_item in file_items:
    #     plan["do_now"].append(file_item)
    
    # Deduplicate emails by subject similarity (e.g., multiple school closing updates)
    seen_subjects = {}
    deduplicated_emails = []
    
    for email in emails:
        subject = email["subject"]
        subject_lower = subject.lower()
        
        # Check for similar subjects (school closings, updates about same event)
        is_duplicate = False
        for seen_subject in seen_subjects.keys():
            seen_lower = seen_subject.lower()
            
            # If subjects share significant keywords, consider them duplicates
            # Keep only the most recent (UPDATE: prefix indicates newer version)
            if ('school' in subject_lower and 'school' in seen_lower and 
                ('closed' in subject_lower and 'closed' in seen_lower or
                 'delay' in subject_lower and 'delay' in seen_lower or
                 'open' in subject_lower and 'open' in seen_lower)):
                
                # Keep the one with "UPDATE:" prefix or the newer one
                if 'update:' in subject_lower and 'update:' not in seen_lower:
                    # Replace old with new
                    seen_subjects[subject] = email
                    del seen_subjects[seen_subject]
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_subjects[subject] = email
    
    # Add deduplicated emails to plan (filter by email age, not subject dates)
    from datetime import datetime as dt, timedelta
    from email.utils import parsedate_to_datetime
    
    # Different cutoffs for different email types
    school_event_cutoff = datetime.now() - timedelta(hours=24)  # 24h for school/events
    general_cutoff = datetime.now() - timedelta(hours=48)  # 48h for other emails
    
    for email in seen_subjects.values():
        subject = email["subject"]
        body = email.get('body', '')
        email_date_str = email.get("date", "")
        sender = email.get("from", "").lower()
        
        # Filter by email received date (more reliable than parsing subject)
        skip_old_email = False
        if email_date_str:
            try:
                # Parse email date header
                email_date = parsedate_to_datetime(email_date_str)
                
                # Make timezone-aware if needed
                if email_date.tzinfo is None:
                    email_date = email_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
                
                # Determine cutoff based on email type
                # School/event notifications expire quickly
                is_school_event = any(keyword in subject.lower() for keyword in 
                    ['school', 'sacc', 'btb', 'closed', 'delay', 'dismissal', 'canceled', 'cancelled'])
                
                cutoff = school_event_cutoff if is_school_event else general_cutoff
                
                # Skip old emails
                if email_date < cutoff:
                    skip_old_email = True
                    hours_old = (datetime.now().astimezone() - email_date).total_seconds() / 3600
                    logger.info(f"Skipping old email ({hours_old:.1f}h old): {subject[:60]}")
            except (ValueError, TypeError, AttributeError) as e:
                # If we can't parse the date, include the email (better safe than sorry)
                logger.warning(f"Could not parse email date for: {subject[:60]}")
        
        if skip_old_email:
            continue
        
        body_preview = body[:200].replace('\n', ' ').strip()
        if len(body) > 200:
            body_preview += '...'
        
        # Generate AI summary and thread context for emails
        ai_summary = None
        thread_context = None
        
        try:
            # Check if this is an email chain
            is_reply = any(subject.startswith(prefix) for prefix in ['RE:', 'Re:', 'RE: [External]', 'FW:', 'Fwd:'])
            
            # Generate AI task summary
            ai_summary = await todoist._generate_task_summary(
                subject=subject,
                sender=email.get("from", ""),
                preview=body_preview
            )
            
            # Generate thread context for email chains
            if is_reply:
                thread_context = await todoist._generate_thread_context(
                    subject=subject,
                    sender=email.get("from", ""),
                    preview=body_preview
                )
        except Exception as e:
            logger.warning(f"AI generation failed for email '{subject[:50]}': {e}")
        
        plan["do_now"].append({
            "title": subject,
            "source": "Email",
            "from": email.get("from", "Unknown"),
            "date": email.get("date", "Unknown"),
            "preview": body_preview,
            "email_id": email.get("id", ""),
            "due": datetime.now().strftime("%Y-%m-%d"),
            "priority": "high",
            "ai_summary": ai_summary,
            "thread_context": thread_context
        })
    
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).strftime("%Y-%m-%d")
    
    for task in tasks:
        if task.get("due"):
            due_date = task["due"].get("date")
            if due_date == today:
                plan["do_now"].append({
                    "title": task["content"],
                    "source": "Todoist",
                    "due": due_date,
                    "priority": "high" if task.get("priority", 1) >= 3 else "normal"
                })
            elif due_date:
                plan["do_soon"].append({
                    "title": task["content"],
                    "source": "Todoist",
                    "due": due_date,
                    "priority": "normal" if task.get("priority", 1) < 3 else "high"
                })
        else:
            plan["monitor"].append({
                "title": task["content"],
                "source": "Todoist",
                "priority": "low"
            })
    
    for event in events:
        if event.get("date") == today:
            plan["do_now"].append({
                "title": event["summary"],
                "source": "Calendar",
                "due": event["date"],
                "time": event.get("time"),
                "priority": "normal"
            })
        else:
            plan["do_soon"].append({
                "title": event["summary"],
                "source": "Calendar",
                "due": event["date"],
                "time": event.get("time"),
                "priority": "normal"
            })
    
    logger.info("\n" + "=" * 60)
    logger.info("PROCESS NEW RESULTS")
    logger.info("=" * 60)
    logger.info(f"\n🎯 DO NOW: {len(plan['do_now'])} items")
    for item in plan['do_now']:
        if item['source'] == 'Email':
            logger.info(f"\n   📧 {item['title']}")
            logger.info(f"      From: {item.get('from', 'Unknown')}")
            logger.info(f"      Date: {item.get('date', 'Unknown')}")
            if item.get('preview'):
                logger.info(f"      Preview: {item['preview']}")
        else:
            logger.info(f"   • [{item['source']}] {item['title']}")
    
    logger.info(f"\n⏰ DO SOON: {len(plan['do_soon'])} items")
    for item in plan['do_soon'][:5]:
        logger.info(f"   • [{item['source']}] {item['title']} (due: {item.get('due', 'N/A')})")
    if len(plan['do_soon']) > 5:
        logger.info(f"   ... and {len(plan['do_soon']) - 5} more")
    
    logger.info(f"\n📋 MONITOR: {len(plan['monitor'])} items")
    
    if gmail.reference_emails:
        logger.info(f"\n� REFERENCE: {len(gmail.reference_emails)} important emails")
        for ref in gmail.reference_emails[:3]:
            logger.info(f"   • {ref['subject'][:50]} (from {ref['from']})")
    
    if drive_docs:
        logger.info(f"\n📄 DOCUMENTS: {len(drive_docs)} recent files")
        for doc in drive_docs[:3]:
            logger.info(f"   • {doc['name']} ({doc['type']})")
    
    # Add statistics
    plan["stats"] = {
        "total_items": len(plan["do_now"]) + len(plan["do_soon"]) + len(plan["monitor"]),
        "do_now": len(plan["do_now"]),
        "do_soon": len(plan["do_soon"]),
        "monitor": len(plan["monitor"]),
        "reference_emails": len(gmail.reference_emails),
        "documents": len(drive_docs)
    }
    
    # Save to output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"process_new_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)
    
    logger.info(f"\n💾 Full results saved to: {output_file}")
    
    # Create DakBoard Todoist tasks
    logger.info("\n📋 Creating Todoist tasks for DakBoard...")
    todoist_success = await todoist.create_daily_plan_tasks(plan["do_now"], plan["do_soon"])
    if todoist_success:
        logger.info("   ✅ Todoist tasks created successfully")
    else:
        logger.warning("   ⚠️  Could not create Todoist tasks")
    
    logger.info("\n📝 Updating Amplenote daily note...")
    try:
        amplenote_success = await amplenote.update_daily_note_with_plan(plan)
        if amplenote_success:
            logger.info("   ✅ Amplenote daily note updated successfully")
        else:
            logger.warning("   ⚠️  Could not update Amplenote daily note")
    except Exception as e:
        if "token expired" in str(e).lower():
            logger.warning("   ⚠️  Amplenote token expired - see instructions above")
        else:
            logger.warning(f"   ⚠️  Could not update Amplenote daily note: {e}")
    
    logger.info("=" * 60)
    
    return plan

async def main():
    try:
        result = await process_new()
        return result
    except Exception as e:
        logger.error(f"Error running process_new: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
