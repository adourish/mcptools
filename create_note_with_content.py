#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
import requests

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    
    # Read the V3.0 guide
    guide_path = Path(r'G:\My Drive\04_Resources\Notes\Amplenote_Organized\uncle-bens-mushroom-guide-V3.0.md')
    full_content = guide_path.read_text(encoding='utf-8')
    
    # Remove title lines
    lines = full_content.split('\n')
    content = '\n'.join(lines[3:])
    
    token = await auth.get_amplenote_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Delete old empty note
    old_uuid = '61bedc06-12ac-11f1-80fd-b11b3bc3cb91'
    print(f"Deleting old note...")
    requests.delete(f'https://api.amplenote.com/v4/notes/{old_uuid}', headers=headers, timeout=10)
    
    # Step 1: Create note with title and tags only
    print(f"Creating note...")
    create_data = {
        'name': 'Uncle Bens Mushroom Growing Method V3.0',
        'tags': [
            {'text': 'mushroom'},
            {'text': 'growing'},
            {'text': 'uncle-bens'},
            {'text': 'guide'},
            {'text': 'INBOX'}
        ]
    }
    
    create_response = requests.post(
        'https://api.amplenote.com/v4/notes',
        headers=headers,
        json=create_data,
        timeout=10
    )
    
    if create_response.status_code != 201:
        print(f"❌ Create failed: {create_response.status_code}")
        print(create_response.text)
        return
    
    note = create_response.json()
    note_uuid = note['uuid']
    print(f"✅ Note created: {note_uuid}")
    
    # Step 2: Update note with content using PATCH
    print(f"Adding content ({len(content)} characters)...")
    update_data = {
        'text': content
    }
    
    update_response = requests.patch(
        f'https://api.amplenote.com/v4/notes/{note_uuid}',
        headers=headers,
        json=update_data,
        timeout=30
    )
    
    print(f"Update status: {update_response.status_code}")
    
    if update_response.status_code == 200:
        print(f"\n✅ SUCCESS! Note created with full content!")
        print(f"URL: https://www.amplenote.com/notes/{note_uuid}")
        
        # Verify content
        verify_response = requests.get(
            f'https://api.amplenote.com/v4/notes/{note_uuid}',
            headers=headers,
            timeout=10
        )
        
        if verify_response.status_code == 200:
            verify_note = verify_response.json()
            verify_content = verify_note.get('text', '')
            checkbox_count = verify_content.count('- [ ]')
            
            print(f"\nVERIFICATION:")
            print(f"  Content length: {len(verify_content)} characters")
            print(f"  Task checkboxes: {checkbox_count}")
            print(f"  Has Phase 0: {'✅' if 'PHASE 0' in verify_content else '❌'}")
            print(f"  Has Phase 6: {'✅' if 'PHASE 6' in verify_content else '❌'}")
    else:
        print(f"❌ Update failed: {update_response.text}")

if __name__ == '__main__':
    asyncio.run(main())
