#!/usr/bin/env python3
import asyncio
import re
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    
    print("Fetching all emails from last 30 days...")
    query = 'newer_than:30d'
    results = await gmail.search(query, max_results=100)
    
    print(f"Analyzing {len(results)} emails...\n")
    
    # Categories to check
    categories = {
        'financial': {
            'keywords': ['bill', 'payment', 'invoice', 'statement', 'balance', 'charge', 'fee', 'tax', 'refund', 'credit card', 'bank', 'account'],
            'emails': []
        },
        'medical': {
            'keywords': ['doctor', 'appointment', 'medical', 'health', 'prescription', 'pharmacy', 'insurance', 'claim', 'patient'],
            'emails': []
        },
        'government': {
            'keywords': ['dmv', 'irs', 'tax', 'registration', 'license', 'permit', 'county', 'state', 'federal', 'government'],
            'emails': []
        },
        'home_property': {
            'keywords': ['hoa', 'homeowners', 'property', 'maintenance', 'repair', 'utilities', 'water', 'electric', 'gas', 'internet'],
            'emails': []
        },
        'appointments': {
            'keywords': ['appointment', 'scheduled', 'booking', 'reservation', 'meeting', 'visit'],
            'emails': []
        },
        'subscriptions': {
            'keywords': ['subscription', 'membership', 'renew', 'renewal', 'expires', 'expiring', 'auto-renew'],
            'emails': []
        },
        'legal_important': {
            'keywords': ['legal', 'contract', 'agreement', 'terms', 'policy change', 'privacy policy', 'consent'],
            'emails': []
        },
        'work_related': {
            'keywords': ['salesforce', 'hrsa', 'rei systems', 'adourish', 'work', 'project', 'meeting'],
            'emails': []
        },
        'time_sensitive': {
            'keywords': ['expires today', 'last chance', 'ending soon', 'final notice', 'reminder', 'overdue'],
            'emails': []
        },
        'family_personal': {
            'keywords': ['birthday', 'anniversary', 'celebration', 'party', 'invitation', 'rsvp'],
            'emails': []
        }
    }
    
    for r in results:
        msg = await gmail.get_email(r['id'])
        subject = msg['subject']
        body = msg.get('body', '')[:1000]
        sender = msg['from']
        text = (subject + ' ' + body).lower()
        
        is_filtered = gmail.is_unimportant_email(subject, body)
        
        # Check each category
        for cat_name, cat_data in categories.items():
            if any(keyword in text for keyword in cat_data['keywords']):
                cat_data['emails'].append({
                    'subject': subject,
                    'from': sender,
                    'filtered': is_filtered
                })
    
    # Print results
    print("=" * 100)
    print("ANALYSIS BY CATEGORY")
    print("=" * 100)
    
    for cat_name, cat_data in categories.items():
        emails = cat_data['emails']
        if not emails:
            continue
            
        filtered_count = sum(1 for e in emails if e['filtered'])
        filter_rate = (filtered_count / len(emails) * 100) if emails else 0
        
        print(f"\n{cat_name.upper().replace('_', ' ')}")
        print(f"Total: {len(emails)} | Filtered: {filtered_count} ({filter_rate:.0f}%)")
        print("-" * 100)
        
        # Show examples of filtered emails
        filtered_examples = [e for e in emails if e['filtered']][:5]
        included_examples = [e for e in emails if not e['filtered']][:5]
        
        if filtered_examples:
            print("\nFILTERED OUT (examples):")
            for e in filtered_examples:
                print(f"  X {e['subject'][:75]}")
                print(f"    From: {e['from'][:70]}")
        
        if included_examples:
            print("\nINCLUDED (examples):")
            for e in included_examples:
                print(f"  ✓ {e['subject'][:75]}")
                print(f"    From: {e['from'][:70]}")
    
    # Find high-priority senders being filtered
    print("\n\n" + "=" * 100)
    print("HIGH-PRIORITY SENDERS ANALYSIS")
    print("=" * 100)
    
    sender_stats = {}
    for r in results:
        msg = await gmail.get_email(r['id'])
        sender = msg['from']
        subject = msg['subject']
        body = msg.get('body', '')[:1000]
        is_filtered = gmail.is_unimportant_email(subject, body)
        
        # Extract domain
        domain_match = re.search(r'@([\w\.-]+)', sender)
        domain = domain_match.group(1) if domain_match else 'unknown'
        
        if domain not in sender_stats:
            sender_stats[domain] = {'total': 0, 'filtered': 0, 'examples': []}
        
        sender_stats[domain]['total'] += 1
        if is_filtered:
            sender_stats[domain]['filtered'] += 1
            if len(sender_stats[domain]['examples']) < 2:
                sender_stats[domain]['examples'].append(subject[:60])
    
    # Show domains with high filter rates
    print("\nDomains with emails being filtered (sorted by filter rate):")
    sorted_domains = sorted(
        [(d, s) for d, s in sender_stats.items() if s['total'] >= 2],
        key=lambda x: x[1]['filtered'] / x[1]['total'],
        reverse=True
    )
    
    for domain, stats in sorted_domains[:20]:
        filter_rate = (stats['filtered'] / stats['total'] * 100)
        if filter_rate > 0:
            print(f"\n{domain}")
            print(f"  Total: {stats['total']} | Filtered: {stats['filtered']} ({filter_rate:.0f}%)")
            if stats['examples']:
                print(f"  Examples: {', '.join(stats['examples'])}")

if __name__ == '__main__':
    asyncio.run(main())
