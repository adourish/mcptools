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
    content = guide_path.read_text(encoding='utf-8')
    
    # Create note in Amplenote
    print("Creating Amplenote note with V3.0 mushroom guide...")
    
    note = await amplenote.create_note(
        title='Uncle Bens Mushroom Growing Method V3.0',
        content=content,
        tags=['mushroom', 'growing', 'uncle-bens', 'guide']
    )
    
    print(f"\n✅ Successfully created Amplenote note!")
    print(f"Title: {note.get('name', 'Uncle Bens Mushroom Growing Method V3.0')}")
    print(f"UUID: {note.get('uuid', 'N/A')}")
    print(f"URL: https://www.amplenote.com/notes/{note.get('uuid', '')}")
    print(f"\nThe note includes interactive task checkboxes that you can check off as you progress!")

if __name__ == '__main__':
    asyncio.run(main())
