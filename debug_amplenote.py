#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools
import requests
import json

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("=" * 100)
    print("DEBUGGING AMPLENOTE API")
    print("=" * 100)
    
    try:
        headers = await amplenote._get_headers()
        
        # Get all notes
        response = requests.get(f"{amplenote.base_url}/notes", headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("\nRefreshing token...")
            await auth.refresh_amplenote_token()
            headers = await amplenote._get_headers()
            response = requests.get(f"{amplenote.base_url}/notes", headers=headers, timeout=10)
        
        print(f"\nAPI Response Status: {response.status_code}")
        print(f"Raw response: {response.text[:500]}\n")
        
        if response.status_code == 200:
            all_notes = response.json()
            print(f"Total notes: {len(all_notes)}")
            print(f"Type: {type(all_notes)}\n")
            
            # Show first few items
            for i, item in enumerate(all_notes[:5]):
                print(f"\nNote {i+1}:")
                print(f"  Type: {type(item)}")
                print(f"  Value: {item}")
                
                # Try to fetch details
                if isinstance(item, str):
                    note_uuid = item
                elif isinstance(item, dict):
                    note_uuid = item.get('uuid')
                else:
                    continue
                
                print(f"  Fetching details for UUID: {note_uuid}")
                detail_response = requests.get(f"{amplenote.base_url}/notes/{note_uuid}", headers=headers, timeout=5)
                print(f"  Detail status: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    details = detail_response.json()
                    print(f"  Name: {details.get('name', 'NO NAME')}")
                    print(f"  Has body: {len(details.get('body', '')) > 0}")
                else:
                    print(f"  Error: {detail_response.text[:200]}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
