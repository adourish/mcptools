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
    
    # Remove the markdown header (first 3 lines) since title is already set
    lines = content.split('\n')
    content_without_title = '\n'.join(lines[3:])  # Skip title and subtitle
    
    # Get auth token
    token = await auth.get_amplenote_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    note_uuid = 'f0582b58-12ab-11f1-92e8-a7f6ea10b1b5'
    
    print(f"Adding {len(content_without_title)} characters to note...")
    
    # Use INSERT_NODES action to add markdown content
    action_data = {
        'type': 'INSERT_NODES',
        'nodes': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'text',
                        'text': content_without_title
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f'https://api.amplenote.com/v4/notes/{note_uuid}/actions',
            headers=headers,
            json=action_data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print(f"\n✅ Successfully added content to note!")
            print(f"URL: https://www.amplenote.com/notes/{note_uuid}")
        else:
            print(f"Response: {response.text[:500]}")
            
            # Try alternative method - direct text update
            print("\nTrying alternative method...")
            update_response = requests.patch(
                f'https://api.amplenote.com/v4/notes/{note_uuid}',
                headers=headers,
                json={'text': content},
                timeout=30
            )
            
            print(f"Alternative status: {update_response.status_code}")
            if update_response.status_code == 200:
                print(f"✅ Success with alternative method!")
            else:
                print(f"Alternative response: {update_response.text[:500]}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
