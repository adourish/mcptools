#!/usr/bin/env python3
import asyncio
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    
    # Search for the Royal Caribbean email
    results = await gmail.search('Royal Caribbean vacay', max_results=5)
    
    if results:
        msg = await gmail.get_email(results[0]['id'])
        
        print("=" * 100)
        print("SPAM EMAIL ANALYSIS")
        print("=" * 100)
        print(f"\nSubject: {msg['subject']}")
        print(f"From: {msg['from']}")
        print(f"Date: {msg['date']}")
        print(f"\nBody preview (first 500 chars):")
        print(msg['body'][:500])
        
        print("\n\n" + "=" * 100)
        print("FILTERING ANALYSIS")
        print("=" * 100)
        
        sender = msg['from']
        subject = msg['subject']
        body = msg['body']
        
        print(f"\nWhitelisted sender: {gmail.is_whitelisted_sender(sender)}")
        print(f"Important sender: {gmail.is_important_sender(sender)}")
        print(f"Has priority content: {gmail.has_priority_content(subject, body)}")
        print(f"Is unimportant: {gmail.is_unimportant_email(subject, body, sender)}")
        
        # Check what urgency keywords it might have matched
        text = (subject + ' ' + body).lower()
        urgency_words = ['urgent', 'asap', 'today', 'deadline', 'due', 'important', 'action required', 'respond', 'confirm']
        matched = [word for word in urgency_words if word in text]
        
        print(f"\nMatched urgency keywords: {matched if matched else 'None'}")
        
        # Check for promotional indicators
        promo_indicators = ['save', 'savings', 'discount', 'deal', 'offer', 'sale', 'promo', 'limited time', 'act now', 'click here', 'unsubscribe']
        promo_matched = [word for word in promo_indicators if word in text]
        
        print(f"Promotional indicators found: {promo_matched}")
        
        print("\n\n" + "=" * 100)
        print("WHY IT GOT THROUGH")
        print("=" * 100)
        
        if matched:
            print(f"\n✗ Matched urgency keyword: '{matched[0]}'")
            print("  This caused it to be flagged as urgent despite being promotional")
        
        if not gmail.is_unimportant_email(subject, body, sender):
            print("\n✗ Not caught by skip_keywords filter")
            print("  Current skip_keywords don't include 'savings', 'vacay', 'instant savings'")

if __name__ == '__main__':
    asyncio.run(main())
