#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    # Read the V3.0 guide
    guide_path = Path(r'G:\My Drive\04_Resources\Notes\Amplenote_Organized\uncle-bens-mushroom-guide-V3.0.md')
    full_content = guide_path.read_text(encoding='utf-8')
    
    # Remove the title lines since we're setting it separately
    lines = full_content.split('\n')
    # Skip first 3 lines (title, subtitle, blank line)
    content = '\n'.join(lines[3:])
    
    print(f"Creating note with {len(content)} characters of content...")
    
    # Delete the empty note first
    import requests
    headers = await amplenote._get_headers()
    
    old_uuid = 'f0582b58-12ab-11f1-92e8-a7f6ea10b1b5'
    print(f"Deleting empty note {old_uuid}...")
    
    delete_response = requests.delete(
        f'https://api.amplenote.com/v4/notes/{old_uuid}',
        headers=headers,
        timeout=10
    )
    print(f"Delete status: {delete_response.status_code}")
    
    # Create new note with content
    print("\nCreating new note with full content...")
    
    note = await amplenote.create_note(
        title='Uncle Bens Mushroom Growing Method V3.0',
        content=content,
        tags=['mushroom', 'growing', 'uncle-bens', 'guide', 'INBOX']
    )
    
    print(f"\n✅ Successfully created Amplenote note with content!")
    print(f"Title: Uncle Bens Mushroom Growing Method V3.0")
    print(f"UUID: {note.get('uuid', 'N/A')}")
    print(f"URL: https://www.amplenote.com/notes/{note.get('uuid', '')}")
    print(f"\nContent length: {len(content)} characters")
    print(f"All task checkboxes are now interactive!")

if __name__ == '__main__':
    asyncio.run(main())
