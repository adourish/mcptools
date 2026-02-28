#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    # Read the V3.0 guide
    guide_path = Path(r'G:\My Drive\04_Resources\Notes\Amplenote_Organized\uncle-bens-mushroom-guide-V3.0.md')
    full_content = guide_path.read_text(encoding='utf-8')
    
    # Remove title lines
    lines = full_content.split('\n')
    content_lines = lines[3:]  # Skip title, subtitle, blank line
    
    # Initialize tools
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("Creating note...")
    
    # Create empty note
    note = await amplenote.create_note(
        title='Uncle Bens Mushroom Growing Method V3.0',
        content="",
        tags=['mushroom', 'growing', 'uncle-bens', 'guide', 'INBOX']
    )
    
    note_uuid = note['uuid']
    print(f"✅ Note created: {note_uuid}")
    print(f"URL: https://www.amplenote.com/notes/{note_uuid}")
    
    print(f"\nAdding content line by line ({len(content_lines)} lines)...")
    
    # Insert content line by line (like daily note does)
    for i, line in enumerate(content_lines):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(content_lines)} lines...")
        
        await amplenote.insert_content(note_uuid, line)
    
    print(f"✅ All {len(content_lines)} lines inserted!")
    
    # Verify
    print(f"\nVerifying content...")
    actual_content = await amplenote.get_note_content(note_uuid)
    
    print(f"\nVERIFICATION:")
    print(f"  Content length: {len(actual_content)} characters")
    print(f"  Task checkboxes: {actual_content.count('- [ ]')}")
    print(f"  Has PHASE 0: {'✅' if 'PHASE 0' in actual_content else '❌'}")
    print(f"  Has PHASE 6: {'✅' if 'PHASE 6' in actual_content else '❌'}")
    
    if len(actual_content) > 1000:
        print(f"\n✅ SUCCESS! Note created with full content!")
        print(f"URL: https://www.amplenote.com/notes/{note_uuid}")
    else:
        print(f"\n⚠️ Content may be incomplete")

if __name__ == '__main__':
    asyncio.run(main())
