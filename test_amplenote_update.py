#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
import requests
import json

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    
    token = await auth.get_amplenote_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    note_uuid = '9a4bac48-12ac-11f1-bf7b-0b2b9d9f987d'
    
    # Try different field names for content
    test_content = "# Test Content\n\nThis is a test to see which field works.\n\n- [ ] Task 1\n- [ ] Task 2"
    
    attempts = [
        {'text': test_content},
        {'body': test_content},
        {'content': test_content},
        {'markdown': test_content}
    ]
    
    for i, update_data in enumerate(attempts, 1):
        field_name = list(update_data.keys())[0]
        print(f"\nAttempt {i}: Using field '{field_name}'")
        
        response = requests.patch(
            f'https://api.amplenote.com/v4/notes/{note_uuid}',
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        # Verify
        verify_response = requests.get(
            f'https://api.amplenote.com/v4/notes/{note_uuid}',
            headers=headers,
            timeout=10
        )
        
        if verify_response.status_code == 200:
            note = verify_response.json()
            content_length = len(note.get('text', ''))
            print(f"  Content length after update: {content_length}")
            
            if content_length > 0:
                print(f"  ✅ SUCCESS! Field '{field_name}' works!")
                print(f"  Content preview: {note.get('text', '')[:100]}")
                break
        else:
            print(f"  Verify failed: {verify_response.status_code}")
    
    # Also try using the actions API
    print(f"\n\nAttempt with INSERT_NODES action:")
    action_data = {
        'type': 'INSERT_NODES',
        'nodes': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': test_content
                    }
                ]
            }
        ]
    }
    
    action_response = requests.post(
        f'https://api.amplenote.com/v4/notes/{note_uuid}/actions',
        headers=headers,
        json=action_data,
        timeout=10
    )
    
    print(f"  Action status: {action_response.status_code}")
    if action_response.status_code not in [200, 204]:
        print(f"  Response: {action_response.text[:200]}")

if __name__ == '__main__':
    asyncio.run(main())
