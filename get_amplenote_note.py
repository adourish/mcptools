#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools
import requests
import sys

async def main():
    if len(sys.argv) < 2:
        print("Usage: python get_amplenote_note.py <note_uuid>")
        sys.exit(1)
    
    note_uuid = sys.argv[1]
    
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    try:
        headers = await amplenote._get_headers()
        
        response = requests.get(f"{amplenote.base_url}/notes/{note_uuid}", headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("Refreshing token...")
            await auth.refresh_amplenote_token()
            headers = await amplenote._get_headers()
            response = requests.get(f"{amplenote.base_url}/notes/{note_uuid}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            note = response.json()
            print(note.get('text', ''))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
