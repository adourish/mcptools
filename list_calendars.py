#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from calendar_tools import CalendarTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    calendar = CalendarTools(auth)
    
    service = await calendar._get_service()
    
    print("=" * 100)
    print("AVAILABLE GOOGLE CALENDARS")
    print("=" * 100)
    
    # List all calendars
    calendar_list = service.calendarList().list().execute()
    
    calendars = calendar_list.get('items', [])
    
    print(f"\nFound {len(calendars)} calendars:\n")
    
    for cal in calendars:
        cal_id = cal['id']
        summary = cal.get('summary', 'No name')
        access_role = cal.get('accessRole', 'Unknown')
        primary = cal.get('primary', False)
        
        print(f"Calendar: {summary}")
        print(f"  ID: {cal_id}")
        print(f"  Access: {access_role}")
        print(f"  Primary: {primary}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
