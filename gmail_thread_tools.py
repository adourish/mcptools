#!/usr/bin/env python3
"""
Gmail Thread Tools - Group and analyze email threads
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class GmailThreadTools:
    """Tools for grouping and analyzing email threads"""
    
    def __init__(self, gmail_tools):
        self.gmail = gmail_tools
    
    def normalize_subject(self, subject: str) -> str:
        """Normalize subject line by removing RE:, FW:, etc."""
        normalized = subject
        
        # Remove common prefixes
        prefixes = ['RE:', 'Re:', 'RE: [External]', 'Re: [External]', 'FW:', 'Fwd:', 'Fw:']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def group_emails_by_thread(self, emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group emails into threads based on normalized subject
        
        Returns:
            Dict mapping normalized subject to list of emails in that thread
        """
        threads = defaultdict(list)
        
        for email in emails:
            subject = email.get('subject', 'No Subject')
            normalized = self.normalize_subject(subject)
            threads[normalized].append(email)
        
        # Sort each thread by date (oldest first)
        for thread_subject in threads:
            threads[thread_subject].sort(key=lambda e: e.get('date', ''))
        
        logger.info(f"Grouped {len(emails)} emails into {len(threads)} threads")
        
        return dict(threads)
    
    async def get_thread_emails(self, days: int = 14) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get emails from last N days and group them into threads
        
        Args:
            days: Number of days to look back (default 14 for 2 weeks)
            
        Returns:
            Dict mapping thread subject to list of emails in chronological order
        """
        logger.info(f"Fetching emails from last {days} days for thread analysis...")
        
        # Get all emails from the period
        emails = await self.gmail.get_urgent_emails(days=days)
        
        # Group into threads
        threads = self.group_emails_by_thread(emails)
        
        # Log thread statistics
        thread_sizes = [len(emails) for emails in threads.values()]
        if thread_sizes:
            logger.info(f"Thread statistics:")
            logger.info(f"  - Total threads: {len(threads)}")
            logger.info(f"  - Avg emails per thread: {sum(thread_sizes) / len(thread_sizes):.1f}")
            logger.info(f"  - Largest thread: {max(thread_sizes)} emails")
            logger.info(f"  - Single email threads: {sum(1 for s in thread_sizes if s == 1)}")
            logger.info(f"  - Multi-email threads: {sum(1 for s in thread_sizes if s > 1)}")
        
        return threads
    
    def get_priority_threads(self, threads: Dict[str, List[Dict[str, Any]]], max_threads: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter to most important threads based on:
        - Whitelisted senders
        - Priority keywords
        - Recent activity
        - Thread length (more emails = more important conversation)
        
        Args:
            threads: All email threads
            max_threads: Maximum number of threads to return
            
        Returns:
            Dict of priority threads
        """
        scored_threads = []
        
        for subject, emails in threads.items():
            score = 0
            latest_email = emails[-1]
            sender = latest_email.get('from', '')
            
            # Whitelisted sender = high priority
            if self.gmail.is_whitelisted_sender(sender):
                score += 100
            
            # Check for priority content in any email
            for email in emails:
                if self.gmail.has_priority_content(
                    email.get('subject', ''),
                    email.get('body', '')
                ):
                    score += 50
                    break
            
            # Multi-email threads are more important (active conversation)
            if len(emails) > 1:
                score += len(emails) * 10
            
            # Recent activity is more important
            # (This is implicit since we're looking at recent emails)
            
            # Check for action keywords
            text = (latest_email.get('subject', '') + ' ' + latest_email.get('body', '')).lower()
            if any(word in text for word in ['urgent', 'asap', 'today', 'deadline', 'action required']):
                score += 30
            
            scored_threads.append((score, subject, emails))
        
        # Sort by score descending
        scored_threads.sort(reverse=True, key=lambda x: x[0])
        
        # Return top threads
        priority_threads = {}
        for score, subject, emails in scored_threads[:max_threads]:
            priority_threads[subject] = emails
            logger.info(f"Priority thread (score={score}): {subject} ({len(emails)} emails)")
        
        return priority_threads
