#!/usr/bin/env python3
"""
Delete the old dated daily plan note and prepare for the new static one
"""

import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("Fetching all daily plan notes...")
    notes = await amplenote.get_notes(tag='daily-plan')
    
    for note in notes:
        if isinstance(note, dict):
            name = note.get('name', '')
            uuid = note.get('uuid', '')
            
            # Delete any note with a date in the title
            if '2026-02-26' in name or 'Thursday' in name or 'PM)' in name:
                print(f"Deleting dated note: {name}")
                await amplenote.delete_note(uuid)
    
    print("\n✅ Cleanup complete - ready for static daily plan note")

if __name__ == '__main__':
    asyncio.run(main())
