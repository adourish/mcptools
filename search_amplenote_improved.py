#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools
import requests

async def search_amplenote(search_term: str):
    """Search Amplenote notes using the improved API endpoint"""
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("=" * 100)
    print(f"SEARCHING AMPLENOTE FOR: {search_term}")
    print("=" * 100)
    
    try:
        headers = await amplenote._get_headers()
        
        # Use the /notes endpoint which returns full metadata
        response = requests.get(f"{amplenote.base_url}/notes", headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("\nRefreshing token...")
            await auth.refresh_amplenote_token()
            headers = await amplenote._get_headers()
            response = requests.get(f"{amplenote.base_url}/notes", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        all_notes = data.get('notes', [])
        
        print(f"\nSearching through {len(all_notes)} notes...\n")
        
        # Search by name first (fast)
        matches = []
        search_lower = search_term.lower()
        
        for note in all_notes:
            name = note.get('name', '')
            uuid = note.get('uuid', '')
            tags = note.get('tags', [])
            
            # Quick search in name and tags
            if search_lower in name.lower() or any(search_lower in tag.lower() for tag in tags):
                matches.append({
                    'uuid': uuid,
                    'name': name,
                    'tags': tags,
                    'url': f"https://www.amplenote.com/notes/{uuid}"
                })
                print(f"✓ Found: {name}")
                print(f"  Tags: {', '.join(tags) if tags else 'None'}")
                print(f"  URL: https://www.amplenote.com/notes/{uuid}\n")
        
        if not matches:
            print("No matches found in note names/tags. Searching note content...")
            
            # If no matches in names, search content (slower)
            for note in all_notes[:20]:  # Limit to first 20 to avoid timeout
                uuid = note.get('uuid', '')
                name = note.get('name', '')
                
                # Fetch full note content
                note_response = requests.get(f"{amplenote.base_url}/notes/{uuid}", headers=headers, timeout=5)
                if note_response.status_code == 200:
                    note_data = note_response.json()
                    body = note_data.get('text', '')
                    
                    if search_lower in body.lower():
                        matches.append({
                            'uuid': uuid,
                            'name': name,
                            'tags': note.get('tags', []),
                            'url': f"https://www.amplenote.com/notes/{uuid}",
                            'body_preview': body[:200]
                        })
                        print(f"✓ Found in content: {name}")
                        print(f"  URL: https://www.amplenote.com/notes/{uuid}\n")
        
        print(f"\n{'=' * 100}")
        print(f"Found {len(matches)} matching notes")
        print(f"{'=' * 100}\n")
        
        return matches
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

async def main():
    import sys
    
    # Get search term from command line or use default
    search_term = sys.argv[1] if len(sys.argv) > 1 else "uncle ben"
    
    matches = await search_amplenote(search_term)
    
    # Show all matches
    if matches:
        print("\nMatching notes:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match['name']}")
            print(f"   {match['url']}")

if __name__ == '__main__':
    asyncio.run(main())
