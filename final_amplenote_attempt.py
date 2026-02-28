#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
import requests

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    
    # Read content
    guide_path = Path(r'G:\My Drive\04_Resources\Notes\Amplenote_Organized\uncle-bens-mushroom-guide-V3.0.md')
    full_content = guide_path.read_text(encoding='utf-8')
    
    token = await auth.get_amplenote_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Create note with text field in the initial POST
    print("Creating note with text in initial POST request...")
    
    create_data = {
        'name': 'Uncle Bens Mushroom Growing Method V3.0',
        'text': full_content,  # Include text in creation
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
        timeout=30
    )
    
    print(f"Create status: {create_response.status_code}")
    print(f"Response: {create_response.text[:500]}")
    
    if create_response.status_code == 201:
        note = create_response.json()
        note_uuid = note['uuid']
        
        # Immediately verify
        print(f"\nVerifying note {note_uuid}...")
        verify_response = requests.get(
            f'https://api.amplenote.com/v4/notes/{note_uuid}',
            headers=headers,
            timeout=10
        )
        
        if verify_response.status_code == 200:
            verify_note = verify_response.json()
            content = verify_note.get('text', '')
            
            print(f"\n{'=' * 80}")
            print("VERIFICATION RESULTS:")
            print(f"{'=' * 80}")
            print(f"Title: {verify_note.get('name', '')}")
            print(f"Content length: {len(content)} characters")
            print(f"Expected length: {len(full_content)} characters")
            print(f"Task checkboxes: {content.count('- [ ]')}")
            print(f"Has PHASE 0: {'✅' if 'PHASE 0' in content else '❌'}")
            print(f"Has PHASE 6: {'✅' if 'PHASE 6' in content else '❌'}")
            print(f"\nURL: https://www.amplenote.com/notes/{note_uuid}")
            
            if len(content) > 0:
                print(f"\n✅ SUCCESS! Note created with content!")
            else:
                print(f"\n❌ FAILED - Content is still empty")
                print("\nThe Amplenote API may not support adding text during note creation via API.")
                print("You may need to manually copy/paste the content into the note.")

if __name__ == '__main__':
    asyncio.run(main())
