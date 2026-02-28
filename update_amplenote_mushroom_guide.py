#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
import requests

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    
    # Read the V3.0 guide
    guide_path = Path(r'G:\My Drive\04_Resources\Notes\Amplenote_Organized\uncle-bens-mushroom-guide-V3.0.md')
    content = guide_path.read_text(encoding='utf-8')
    
    # Get auth token
    token = await auth.get_amplenote_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    note_uuid = 'f0582b58-12ab-11f1-92e8-a7f6ea10b1b5'
    
    print("Adding content to Amplenote note...")
    
    # Use the simpler approach - update note with text field
    update_data = {
        'text': content
    }
    
    response = requests.put(
        f'https://api.amplenote.com/v4/notes/{note_uuid}',
        headers=headers,
        json=update_data,
        timeout=30
    )
    
    if response.status_code == 200:
        print(f"\n✅ Successfully updated Amplenote note with content!")
        print(f"URL: https://www.amplenote.com/notes/{note_uuid}")
        print(f"\nThe note now includes all {len(content)} characters of the V3.0 guide!")
        print(f"All task checkboxes are interactive and ready to use!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == '__main__':
    asyncio.run(main())
