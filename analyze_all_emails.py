#!/usr/bin/env python3
import asyncio
import re
from pathlib import Path
from auth_manager import AuthManager
from gmail_tools import GmailTools
from datetime import datetime

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    gmail = GmailTools(auth)
    
    # Get all emails from last month
    print("Fetching all emails from last 30 days...")
    query = 'newer_than:30d'
    results = await gmail.search(query, max_results=100)
    
    print(f"Found {len(results)} total emails\n")
    
    # Categories to detect
    school_related = []
    date_mentions = []
    deadline_mentions = []
    exam_mentions = []
    trip_mentions = []
    important_keywords = []
    
    # Patterns to look for
    date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b'
    
    for r in results:
        msg = await gmail.get_email(r['id'])
        subject = msg['subject']
        body = msg.get('body', '')[:1000]  # First 1000 chars
        sender = msg['from']
        text = (subject + ' ' + body).lower()
        
        # School-related
        if any(word in text for word in ['fcps', 'school', 'teacher', 'classroom', 'student', 'pta', 'principal']):
            school_related.append({
                'subject': subject,
                'from': sender,
                'date': msg['date'],
                'filtered': gmail.is_unimportant_email(subject, body)
            })
        
        # Dates mentioned
        dates = re.findall(date_pattern, subject + ' ' + body[:500])
        if dates:
            date_mentions.append({
                'subject': subject,
                'from': sender,
                'dates': dates[:3],  # First 3 dates
                'filtered': gmail.is_unimportant_email(subject, body)
            })
        
        # Deadlines
        if any(word in text for word in ['deadline', 'due date', 'due by', 'submit by', 'expires']):
            deadline_mentions.append({
                'subject': subject,
                'from': sender,
                'filtered': gmail.is_unimportant_email(subject, body)
            })
        
        # Exams/tests
        if any(word in text for word in ['exam', 'test', 'quiz', 'assessment', 'evaluation']):
            exam_mentions.append({
                'subject': subject,
                'from': sender,
                'filtered': gmail.is_unimportant_email(subject, body)
            })
        
        # Trips/field trips
        if any(word in text for word in ['field trip', 'trip', 'excursion', 'visit', 'permission slip']):
            trip_mentions.append({
                'subject': subject,
                'from': sender,
                'filtered': gmail.is_unimportant_email(subject, body)
            })
        
        # Important keywords
        if any(word in text for word in ['urgent', 'important', 'action required', 'asap', 'critical']):
            important_keywords.append({
                'subject': subject,
                'from': sender,
                'filtered': gmail.is_unimportant_email(subject, body)
            })
    
    # Print results
    print("=" * 100)
    print("SCHOOL-RELATED EMAILS")
    print("=" * 100)
    filtered_count = sum(1 for e in school_related if e['filtered'])
    print(f"Total: {len(school_related)} | Filtered out: {filtered_count}\n")
    for e in school_related[:15]:
        status = "❌ FILTERED" if e['filtered'] else "✅ INCLUDED"
        print(f"{status} | {e['subject'][:70]}")
        print(f"         From: {e['from'][:60]}\n")
    
    print("\n" + "=" * 100)
    print("EMAILS WITH SPECIFIC DATES")
    print("=" * 100)
    filtered_count = sum(1 for e in date_mentions if e['filtered'])
    print(f"Total: {len(date_mentions)} | Filtered out: {filtered_count}\n")
    for e in date_mentions[:15]:
        status = "❌ FILTERED" if e['filtered'] else "✅ INCLUDED"
        print(f"{status} | {e['subject'][:70]}")
        print(f"         Dates: {', '.join(e['dates'])}")
        print(f"         From: {e['from'][:60]}\n")
    
    print("\n" + "=" * 100)
    print("DEADLINE MENTIONS")
    print("=" * 100)
    filtered_count = sum(1 for e in deadline_mentions if e['filtered'])
    print(f"Total: {len(deadline_mentions)} | Filtered out: {filtered_count}\n")
    for e in deadline_mentions[:10]:
        status = "❌ FILTERED" if e['filtered'] else "✅ INCLUDED"
        print(f"{status} | {e['subject'][:70]}")
        print(f"         From: {e['from'][:60]}\n")
    
    print("\n" + "=" * 100)
    print("EXAM/TEST MENTIONS")
    print("=" * 100)
    filtered_count = sum(1 for e in exam_mentions if e['filtered'])
    print(f"Total: {len(exam_mentions)} | Filtered out: {filtered_count}\n")
    for e in exam_mentions:
        status = "❌ FILTERED" if e['filtered'] else "✅ INCLUDED"
        print(f"{status} | {e['subject'][:70]}")
        print(f"         From: {e['from'][:60]}\n")
    
    print("\n" + "=" * 100)
    print("TRIP MENTIONS")
    print("=" * 100)
    filtered_count = sum(1 for e in trip_mentions if e['filtered'])
    print(f"Total: {len(trip_mentions)} | Filtered out: {filtered_count}\n")
    for e in trip_mentions:
        status = "❌ FILTERED" if e['filtered'] else "✅ INCLUDED"
        print(f"{status} | {e['subject'][:70]}")
        print(f"         From: {e['from'][:60]}\n")
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"School-related: {len(school_related)} total, {sum(1 for e in school_related if e['filtered'])} filtered")
    print(f"Date mentions: {len(date_mentions)} total, {sum(1 for e in date_mentions if e['filtered'])} filtered")
    print(f"Deadlines: {len(deadline_mentions)} total, {sum(1 for e in deadline_mentions if e['filtered'])} filtered")
    print(f"Exams/tests: {len(exam_mentions)} total, {sum(1 for e in exam_mentions if e['filtered'])} filtered")
    print(f"Trips: {len(trip_mentions)} total, {sum(1 for e in trip_mentions if e['filtered'])} filtered")

if __name__ == '__main__':
    asyncio.run(main())
