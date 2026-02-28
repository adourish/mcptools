#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools
import requests

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("=" * 100)
    print("SEARCHING AMPLENOTE FOR 'UNCLE BENS' MUSHROOM NOTE")
    print("=" * 100)
    
    # Use the amplenote_tools method to get notes with proper auth
    try:
        # Get fresh headers with token
        headers = await amplenote._get_headers()
        
        # Search using Amplenote API
        response = requests.get(f"{amplenote.base_url}/notes", headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("\nToken expired, refreshing...")
            # Force token refresh
            await auth.refresh_amplenote_token()
            headers = await amplenote._get_headers()
            response = requests.get(f"{amplenote.base_url}/notes", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Error fetching notes: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        all_notes = response.json()
        print(f"\nSearching through {len(all_notes)} notes...\n")
        
        # API returns list of UUID strings
        note_uuids = all_notes if isinstance(all_notes, list) else []
        
        # Search for uncle bens or mushroom
        matches = []
        
        print("Listing all notes first...")
        all_note_names = []
        
        for i, note_uuid in enumerate(note_uuids):
            # Handle both string UUIDs and dict objects
            if isinstance(note_uuid, dict):
                note_uuid = note_uuid.get('uuid')
            
            if not note_uuid:
                continue
            
            # Fetch note content
            note_response = requests.get(f"{amplenote.base_url}/notes/{note_uuid}", headers=headers, timeout=5)
            if note_response.status_code == 200:
                note_data = note_response.json()
                name = note_data.get('name', '')
                body = note_data.get('body', '')
                
                all_note_names.append(name)
                
                search_text = (name + ' ' + body).lower()
                # Search for uncle bens or mushroom method (without quotes)
                if ('uncle ben' in search_text) or \
                   ('mushroom' in search_text and 'method' in search_text):
                    print(f"Found: {name}")
                    matches.append({
                        'uuid': note_uuid,
                        'name': name,
                        'body': body,
                        'url': f"https://www.amplenote.com/notes/{note_uuid}"
                    })
        
        print(f"\nAll note titles in Amplenote:")
        for name in all_note_names:
            print(f"  - {name}")
        
        print(f"\n{'=' * 100}")
        print(f"Found {len(matches)} matching notes")
        print(f"{'=' * 100}\n")
        
        # Show full content of matches
        for match in matches:
            print(f"\n{'=' * 100}")
            print(f"NOTE: {match['name']}")
            print(f"URL: {match['url']}")
            print(f"{'=' * 100}\n")
            print(match['body'][:2000])  # First 2000 chars
            if len(match['body']) > 2000:
                print(f"\n... (truncated, {len(match['body'])} total characters)")
            print()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
