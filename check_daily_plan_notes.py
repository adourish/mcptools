#!/usr/bin/env python3
"""
Check what daily plan notes exist and their titles
"""

import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("Fetching notes with 'daily-plan' tag...")
    notes = await amplenote.get_notes(tag='daily-plan')
    
    print(f"\nTotal notes found: {len(notes)}")
    print("\nFirst 20 notes:")
    
    for i, note in enumerate(notes[:20]):
        if isinstance(note, dict):
            name = note.get('name', 'NO NAME')
            uuid = note.get('uuid', 'NO UUID')
            print(f"{i+1}. {name}")
            print(f"   UUID: {uuid}")
        else:
            print(f"{i+1}. {note}")
    
    # Look for the static title
    static_title = "📋 Daily Plan"
    found = False
    for note in notes[:20]:
        if isinstance(note, dict):
            if note.get('name') == static_title:
                print(f"\n✓ Found static daily plan note: {note.get('uuid')}")
                found = True
                break
    
    if not found:
        print(f"\n✗ No note with exact title '{static_title}' found in first 20 notes")

if __name__ == '__main__':
    asyncio.run(main())
