#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    # Read the V3.0 guide
    guide_path = Path(r'G:\My Drive\04_Resources\Notes\Amplenote_Organized\uncle-bens-mushroom-guide-V3.0.md')
    full_content = guide_path.read_text(encoding='utf-8')
    
    # Remove title lines since we set title separately
    lines = full_content.split('\n')
    content = '\n'.join(lines[3:])
    
    # Use the amplenote_tools directly (same as MCP server uses)
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print(f"Creating Amplenote note with {len(content)} characters...")
    
    # This is the same method the MCP server uses
    result = await amplenote.create_note(
        title='Uncle Bens Mushroom Growing Method V3.0',
        content=content,
        tags=['mushroom', 'growing', 'uncle-bens', 'guide', 'INBOX']
    )
    
    print(f"\n✅ Note created!")
    print(f"UUID: {result.get('uuid')}")
    print(f"URL: https://www.amplenote.com/notes/{result.get('uuid')}")
    
    # Verify immediately
    import requests
    headers = await amplenote._get_headers()
    verify_response = requests.get(
        f'https://api.amplenote.com/v4/notes/{result.get("uuid")}',
        headers=headers,
        timeout=10
    )
    
    if verify_response.status_code == 200:
        note = verify_response.json()
        actual_content = note.get('text', '')
        
        print(f"\nVERIFICATION:")
        print(f"  Content length: {len(actual_content)} characters")
        print(f"  Expected: {len(content)} characters")
        print(f"  Task checkboxes: {actual_content.count('- [ ]')}")
        print(f"  Has PHASE 0: {'✅' if 'PHASE 0' in actual_content else '❌'}")
        print(f"  Has PHASE 6: {'✅' if 'PHASE 6' in actual_content else '❌'}")
        
        if len(actual_content) > 0:
            print(f"\n✅ SUCCESS! Content was added to the note!")
        else:
            print(f"\n❌ Content is still empty")

if __name__ == '__main__':
    asyncio.run(main())
