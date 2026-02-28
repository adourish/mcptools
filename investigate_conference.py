#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools
from calendar_tools import CalendarTools
from datetime import datetime, timedelta

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    calendar = CalendarTools(auth)
    
    print("=" * 100)
    print("INVESTIGATING PARENT-TEACHER CONFERENCE MISS")
    print("=" * 100)
    
    # Search emails for conference mentions
    print("\n1. SEARCHING EMAILS FOR 'CONFERENCE'...")
    conference_emails = await gmail.search('conference OR "parent teacher" OR "parent-teacher"', max_results=20)
    
    print(f"\nFound {len(conference_emails)} emails mentioning conference:\n")
    for email in conference_emails[:10]:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Date: {email['date']}")
        
        # Check if it would be filtered
        full_msg = await gmail.get_email(email['id'])
        sender = full_msg['from']
        subject = full_msg['subject']
        body = full_msg.get('body', '')
        
        is_important = gmail.is_important_sender(sender)
        is_unimportant = gmail.is_unimportant_email(subject, body, sender)
        
        print(f"  → Important sender: {is_important}")
        print(f"  → Unimportant email: {is_unimportant}")
        print(f"  → Would be included: {is_important and not is_unimportant}")
        print()
    
    # Check calendar events
    print("\n2. CHECKING CALENDAR FOR TODAY'S EVENTS...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get events for today
    events = await calendar.get_events(days_ahead=1)
    
    print(f"\nFound {len(events)} calendar events:\n")
    for event in events:
        print(f"Event: {event['summary']}")
        print(f"Date: {event['date']}")
        print(f"Time: {event['time']}")
        print(f"Organizer: {event.get('organizer', 'Unknown')}")
        print()
    
    # Check if there are events being filtered
    print("\n3. CHECKING RAW CALENDAR (NO FILTERS)...")
    service = await calendar._get_service()
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=1)).isoformat() + 'Z'
    
    raw_events = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    all_events = raw_events.get('items', [])
    print(f"\nRaw calendar has {len(all_events)} events (before filtering):\n")
    
    for event in all_events:
        summary = event.get('summary', 'No title')
        start = event['start'].get('dateTime', event['start'].get('date'))
        organizer = event.get('organizer', {}).get('email', 'Unknown')
        creator = event.get('creator', {}).get('email', 'Unknown')
        
        print(f"Event: {summary}")
        print(f"Start: {start}")
        print(f"Organizer: {organizer}")
        print(f"Creator: {creator}")
        
        # Check why it might be filtered
        if 'ahartnet@gmail.com' in organizer.lower() or 'ahartnet@gmail.com' in creator.lower():
            print("  ❌ FILTERED: Created/organized by Alexandra Hartnett")
        
        attendees = event.get('attendees', [])
        if any(word in summary.lower() for word in ['birthday', 'anniversary', 'bday']):
            if not attendees or len(attendees) <= 1:
                print("  ❌ FILTERED: Birthday/anniversary with no attendees")
        
        print()

if __name__ == '__main__':
    asyncio.run(main())
