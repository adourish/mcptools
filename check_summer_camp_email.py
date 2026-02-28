#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    
    # Search for the summer camp email
    messages = await gmail.search('subject:"Summer Camp" from:membershiptoolkit.com', max_results=5)
    
    print(f"Found {len(messages)} summer camp emails\n")
    
    for msg in messages:
        full_msg = await gmail.get_email(msg['id'])
        subject = full_msg.get('subject', '')
        sender = full_msg.get('from', '')
        date = full_msg.get('date', '')
        
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print(f"Date: {date}")
        
        # Test filtering
        sender_lower = sender.lower()
        
        # Check if it should be filtered
        should_filter = gmail.is_important_sender(sender)
        
        print(f"is_important_sender: {should_filter}")
        print(f"Should be filtered out: {not should_filter}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
