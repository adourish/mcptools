#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from amplenote_tools import AmplenoteTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amplenote = AmplenoteTools(auth)
    
    # Get notes with process-new tag
    notes = await amplenote.get_notes(tag='process-new')
    
    print(f"Found {len(notes)} notes with 'process-new' tag\n")
    
    # Get the most recent daily plan notes
    daily_plans = []
    for note_item in notes[:10]:
        try:
            if isinstance(note_item, str):
                uuid = note_item
            elif isinstance(note_item, dict):
                uuid = note_item.get('uuid')
            else:
                continue
            
            if not uuid:
                continue
            
            # Get note details
            headers = await amplenote._get_headers()
            import requests
            response = requests.get(f"{amplenote.base_url}/notes/{uuid}", headers=headers)
            
            if response.status_code == 200:
                note_data = response.json()
                note_title = note_data.get('name', '')
                
                if note_title.startswith("📋 Daily Plan - "):
                    daily_plans.append({
                        'uuid': uuid,
                        'title': note_title,
                        'body': note_data.get('body', '')[:2000]  # First 2000 chars
                    })
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print(f"Found {len(daily_plans)} daily plan notes\n")
    print("=" * 100)
    
    if daily_plans:
        latest = daily_plans[0]
        print(f"LATEST DAILY PLAN: {latest['title']}")
        print("=" * 100)
        print(latest['body'])
        print("\n" + "=" * 100)
        print("ANALYSIS")
        print("=" * 100)
        
        # Check for duplicates
        lines = latest['body'].split('\n')
        seen_items = {}
        duplicates = []
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean and not line_clean.startswith('#') and not line_clean.startswith('*') and not line_clean.startswith('-'):
                if line_clean in seen_items:
                    duplicates.append((line_clean, seen_items[line_clean], i))
                else:
                    seen_items[line_clean] = i
        
        if duplicates:
            print(f"\nFound {len(duplicates)} duplicate items:")
            for dup, first_line, second_line in duplicates[:10]:
                print(f"  • {dup[:80]}")
                print(f"    First at line {first_line}, duplicate at line {second_line}")
        
        # Check for Sarah Clark mentions
        sarah_mentions = [i for i, line in enumerate(lines) if 'sarah clark' in line.lower()]
        if sarah_mentions:
            print(f"\n'Sarah Clark' mentioned {len(sarah_mentions)} times at lines: {sarah_mentions}")

if __name__ == '__main__':
    asyncio.run(main())
