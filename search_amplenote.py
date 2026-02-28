#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("=" * 100)
    print("SEARCHING AMPLENOTE FOR 'UNCLE BENS' MUSHROOM NOTE")
    print("=" * 100)
    
    # Search for notes containing "uncle bens" or "mushroom"
    headers = await amplenote._get_headers()
    
    import requests
    
    # Get all notes
    response = requests.get(f"{amplenote.base_url}/notes", headers=headers)
    if response.status_code != 200:
        print(f"Error fetching notes: {response.status_code}")
        return
    
    all_notes = response.json()
    print(f"\nSearching through {len(all_notes)} notes...\n")
    
    # Search for uncle bens or mushroom
    matches = []
    for note in all_notes:
        note_uuid = note.get('uuid')
        if not note_uuid:
            continue
        
        # Fetch note details
        note_response = requests.get(f"{amplenote.base_url}/notes/{note_uuid}", headers=headers)
        if note_response.status_code != 200:
            continue
        
        note_data = note_response.json()
        name = note_data.get('name', '')
        body = note_data.get('body', '')
        
        # Check if it mentions uncle bens or mushroom
        search_text = (name + ' ' + body).lower()
        if 'uncle ben' in search_text or 'mushroom' in search_text:
            matches.append({
                'uuid': note_uuid,
                'name': name,
                'body': body
            })
            print(f"Found: {name}")
            print(f"  UUID: {note_uuid}")
            print(f"  URL: https://www.amplenote.com/notes/{note_uuid}")
            print()
    
    print(f"\n{'=' * 100}")
    print(f"Found {len(matches)} matching notes")
    print(f"{'=' * 100}\n")
    
    # Show full content of matches
    for match in matches:
        print(f"\n{'=' * 100}")
        print(f"NOTE: {match['name']}")
        print(f"{'=' * 100}\n")
        print(match['body'])
        print()

if __name__ == '__main__':
    asyncio.run(main())
