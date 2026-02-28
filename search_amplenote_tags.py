#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools
import requests

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    print("=" * 100)
    print("TESTING AMPLENOTE API ENDPOINTS")
    print("=" * 100)
    
    try:
        headers = await amplenote._get_headers()
        
        # Try different API endpoints
        endpoints_to_test = [
            "/notes",
            "/tags",
            "/notes?tag=mushroom",
            "/notes?tag=uncle",
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n{'=' * 100}")
            print(f"Testing: GET {amplenote.base_url}{endpoint}")
            print('=' * 100)
            
            response = requests.get(f"{amplenote.base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 401:
                print("Token expired, refreshing...")
                await auth.refresh_amplenote_token()
                headers = await amplenote._get_headers()
                response = requests.get(f"{amplenote.base_url}{endpoint}", headers=headers, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response type: {type(data)}")
                print(f"Response length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"First item: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")
                    
                print(f"Full response (first 500 chars): {str(data)[:500]}")
            else:
                print(f"Error: {response.text[:200]}")
        
        # Now try to get note details with the UUID from the original file
        print(f"\n{'=' * 100}")
        print("Trying to fetch note by UUID from original file")
        print('=' * 100)
        
        original_uuid = "183606bc-bb0a-11f0-82e9-af5947ece790"
        response = requests.get(f"{amplenote.base_url}/notes/{original_uuid}", headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            note = response.json()
            print(f"Found note!")
            print(f"Name: {note.get('name', 'NO NAME')}")
            print(f"URL: https://www.amplenote.com/notes/{original_uuid}")
        else:
            print(f"Not found or error: {response.text[:200]}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
