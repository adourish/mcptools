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
    
    # Get the most recent daily plan
    note_uuid = '4575969e-11f7-11f1-8591-8d95d89a72a0'
    
    print("Fetching daily plan note to examine checkbox format...")
    response = requests.get(
        f'https://api.amplenote.com/v4/notes/{note_uuid}',
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        note = response.json()
        content = note.get('text', '')
        
        print(f"\nNote: {note.get('name', '')}")
        print(f"Content length: {len(content)} characters")
        print(f"\n{'=' * 80}")
        print("FIRST 2000 CHARACTERS (showing checkbox format):")
        print(f"{'=' * 80}\n")
        print(content[:2000])
        
        # Look for task patterns
        print(f"\n{'=' * 80}")
        print("TASK PATTERNS FOUND:")
        print(f"{'=' * 80}")
        
        lines = content.split('\n')
        task_lines = [line for line in lines if '- [ ]' in line or '- [x]' in line or '- [X]' in line]
        
        print(f"\nFound {len(task_lines)} task lines")
        print("\nFirst 10 task examples:")
        for i, task in enumerate(task_lines[:10], 1):
            print(f"{i}. {task}")
        
    else:
        print(f"Error: {response.status_code}")

if __name__ == '__main__':
    asyncio.run(main())
