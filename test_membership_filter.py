#!/usr/bin/env python3

# Test the membership toolkit filter
sender = "Afterschool Activities <notify@membershiptoolkit.com>"
sender_lower = sender.lower()

skip_patterns = [
    'notify@membershiptoolkit.com',
    'afterschool activities',
    'membershiptoolkit.com'
]

print(f"Sender: {sender}")
print(f"Sender (lowercase): {sender_lower}")
print()

for pattern in skip_patterns:
    if pattern in sender_lower:
        print(f"✅ Pattern '{pattern}' MATCHES")
    else:
        print(f"❌ Pattern '{pattern}' does NOT match")
