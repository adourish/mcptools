#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

# Find the most recent output file
output_dir = Path(r'G:\My Drive\06_Master_Guides\MCP_Server\output')
json_files = list(output_dir.glob('process_new_output_*.json'))

if json_files:
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Latest output file: {latest_file.name}\n")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 100)
    print("DO NOW ITEMS")
    print("=" * 100)
    for item in data.get('do_now', []):
        print(f"\nTitle: {item.get('title', 'N/A')}")
        print(f"Source: {item.get('source', 'N/A')}")
        if item.get('from'):
            print(f"From: {item['from']}")
        if item.get('preview'):
            print(f"Preview: {item['preview'][:150]}...")
    
    print("\n\n" + "=" * 100)
    print("DO SOON ITEMS")
    print("=" * 100)
    for item in data.get('do_soon', []):
        print(f"\nTitle: {item.get('title', 'N/A')}")
        print(f"Source: {item.get('source', 'N/A')}")
        if item.get('due'):
            print(f"Due: {item['due']}")
    
    print("\n\n" + "=" * 100)
    print("ANALYSIS")
    print("=" * 100)
    
    # Check for spam/promotional content
    spam_indicators = ['vacay', 'sale', 'discount', 'deal', 'save', 'offer', 'promo']
    
    potential_spam = []
    for item in data.get('do_now', []):
        title = item.get('title', '').lower()
        preview = item.get('preview', '').lower()
        text = title + ' ' + preview
        
        if any(indicator in text for indicator in spam_indicators):
            potential_spam.append({
                'title': item.get('title'),
                'from': item.get('from', 'Unknown'),
                'reason': [ind for ind in spam_indicators if ind in text]
            })
    
    if potential_spam:
        print(f"\nFound {len(potential_spam)} potential spam/promotional items:")
        for spam in potential_spam:
            print(f"\n  ❌ {spam['title'][:70]}")
            print(f"     From: {spam['from'][:60]}")
            print(f"     Spam indicators: {', '.join(spam['reason'])}")
    else:
        print("\n✓ No obvious spam/promotional content detected")
    
    print(f"\n\nTotal DO NOW items: {len(data.get('do_now', []))}")
    print(f"Total DO SOON items: {len(data.get('do_soon', []))}")
    print(f"Total MONITOR items: {len(data.get('monitor', []))}")
else:
    print("No output files found")
