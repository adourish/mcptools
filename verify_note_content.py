#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
import requests

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    
    token = await auth.get_amplenote_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    note_uuid = '61bedc06-12ac-11f1-80fd-b11b3bc3cb91'
    
    print("Fetching note from Amplenote...")
    response = requests.get(
        f'https://api.amplenote.com/v4/notes/{note_uuid}',
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        note = response.json()
        content = note.get('text', '')
        name = note.get('name', '')
        tags = note.get('tags', [])
        
        print(f"\n✅ Note Retrieved Successfully!")
        print(f"Title: {name}")
        print(f"Tags: {', '.join(tags)}")
        print(f"Content Length: {len(content)} characters")
        print(f"\n{'=' * 80}")
        print("CONTENT VERIFICATION:")
        print(f"{'=' * 80}")
        
        # Check for key sections
        sections = [
            'PHASE 0: Shopping & Preparation',
            'PHASE 1: Inoculation Day',
            'PHASE 2: Colonization Watch',
            'PHASE 3: Transfer to Tubs',
            'PHASE 4: Pinning Watch',
            'PHASE 5: Harvest',
            'PHASE 6: Flushing'
        ]
        
        print("\nSection Check:")
        for section in sections:
            if section in content:
                print(f"  ✅ {section}")
            else:
                print(f"  ❌ {section} - MISSING!")
        
        # Check for task checkboxes
        checkbox_count = content.count('- [ ]')
        print(f"\nTask Checkboxes: {checkbox_count} found")
        
        # Show first 500 characters
        print(f"\n{'=' * 80}")
        print("FIRST 500 CHARACTERS:")
        print(f"{'=' * 80}")
        print(content[:500])
        print("...")
        
        # Show last 200 characters
        print(f"\n{'=' * 80}")
        print("LAST 200 CHARACTERS:")
        print(f"{'=' * 80}")
        print("...")
        print(content[-200:])
        
        print(f"\n{'=' * 80}")
        print("VERIFICATION COMPLETE")
        print(f"{'=' * 80}")
        print(f"\nNote URL: https://www.amplenote.com/notes/{note_uuid}")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == '__main__':
    asyncio.run(main())
