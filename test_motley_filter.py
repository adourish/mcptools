#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    
    # Test the Motley Fool email
    sender = "The Motley Fool <fool@motley.fool.com>"
    subject = "Today: Live Q&A with Tom in 3 hours"
    body = "Here's your link to join... The Motley Fool"
    
    print("Testing Motley Fool email filtering:")
    print(f"Sender: {sender}")
    print(f"Subject: {subject}")
    print()
    
    print(f"is_whitelisted_sender: {gmail.is_whitelisted_sender(sender)}")
    print(f"is_important_sender: {gmail.is_important_sender(sender)}")
    print(f"has_priority_content: {gmail.has_priority_content(subject, body)}")
    print(f"is_unimportant_email: {gmail.is_unimportant_email(subject, body, sender)}")
    print()
    
    # Check skip_senders patterns
    sender_lower = sender.lower()
    matched_patterns = [pattern for pattern in gmail.skip_senders if pattern in sender_lower]
    print(f"Matched skip_sender patterns: {matched_patterns}")
    
    # Check if it would be included
    if gmail.is_whitelisted_sender(sender) or gmail.has_priority_content(subject, body):
        print("\n✓ Would be INCLUDED (whitelisted or priority)")
    elif not gmail.is_important_sender(sender):
        print("\n✓ Would be FILTERED OUT (not important sender)")
    elif gmail.is_unimportant_email(subject, body, sender):
        print("\n✓ Would be FILTERED OUT (unimportant email)")
    else:
        print("\n❌ Would be INCLUDED (passed all filters)")

if __name__ == '__main__':
    asyncio.run(main())
