#!/usr/bin/env python3
"""
Clean up old daily plan notes from Amplenote
Keeps only today's note, deletes all others
"""

import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools
from datetime import datetime

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Fetching daily plan notes...")
    notes = await amplenote.get_notes(tag='process-new')
    
    daily_plans = []
    for note in notes:
        if isinstance(note, dict):
            name = note.get('name', '')
            uuid = note.get('uuid', '')
            if '📋 Daily Plan' in name:
                daily_plans.append({'uuid': uuid, 'name': name})
    
    print(f"\nFound {len(daily_plans)} daily plan notes")
    
    # Separate today's notes from old notes
    todays_notes = []
    old_notes = []
    
    for note in daily_plans:
        if today_date in note['name']:
            todays_notes.append(note)
        else:
            old_notes.append(note)
    
    print(f"\nToday's notes ({today_date}): {len(todays_notes)}")
    for note in todays_notes:
        print(f"  ✓ {note['name']}")
    
    print(f"\nOld notes to delete: {len(old_notes)}")
    for note in old_notes:
        print(f"  ❌ {note['name']}")
    
    if old_notes:
        confirm = input(f"\nDelete {len(old_notes)} old daily plan notes? (yes/no): ")
        if confirm.lower() == 'yes':
            deleted = 0
            for note in old_notes:
                success = await amplenote.delete_note(note['uuid'])
                if success:
                    deleted += 1
                    print(f"  Deleted: {note['name']}")
            print(f"\n✅ Deleted {deleted} old daily plan notes")
        else:
            print("Cancelled - no notes deleted")
    else:
        print("\n✅ No old notes to delete")
    
    # If there are multiple notes for today, keep the most recent one
    if len(todays_notes) > 1:
        print(f"\n⚠️ Found {len(todays_notes)} notes for today - keeping most recent, deleting others")
        # Sort by timestamp in title (most recent last)
        todays_notes.sort(key=lambda x: x['name'])
        
        # Keep the last one, delete the rest
        to_delete = todays_notes[:-1]
        for note in to_delete:
            await amplenote.delete_note(note['uuid'])
            print(f"  Deleted duplicate: {note['name']}")
        
        print(f"  ✓ Kept: {todays_notes[-1]['name']}")

if __name__ == '__main__':
    asyncio.run(main())
