#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    
    # Search for school-related emails
    print("Searching for school closing emails...")
    results = await gmail.search('fairfax county schools OR school closing OR fcps OR "school delay"', max_results=10)
    
    print(f"\nFound {len(results)} school-related emails:\n")
    for r in results:
        print(f"Subject: {r['subject']}")
        print(f"From: {r['from']}")
        print(f"Date: {r['date']}")
        print("-" * 80)
    
    # Now check if they would be filtered
    print("\n\nChecking which emails would be filtered out:\n")
    for r in results:
        msg = await gmail.get_email(r['id'])
        subject = msg['subject']
        body = msg.get('body', '')
        sender = msg['from']
        
        is_important = gmail.is_important_sender(sender)
        is_unimportant = gmail.is_unimportant_email(subject, body)
        
        print(f"Subject: {subject[:60]}")
        print(f"  Important sender: {is_important}")
        print(f"  Unimportant content: {is_unimportant}")
        print(f"  Would be included: {is_important and not is_unimportant}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
