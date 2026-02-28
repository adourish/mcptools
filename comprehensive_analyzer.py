#!/usr/bin/env python3
"""
Comprehensive Email Thread Analyzer
Analyzes email threads over 2 weeks to understand context, outcomes, and action items
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

class ComprehensiveAnalyzer:
    """Analyzes email threads, tasks, and calendar to provide comprehensive context"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.openrouter_key = None
        self._openrouter_key_loaded = False
    
    async def _ensure_openrouter_key(self) -> bool:
        """Ensure OpenRouter API key is loaded from auth_manager"""
        if not self._openrouter_key_loaded:
            self.openrouter_key = await self.auth_manager.get_openrouter_key()
            self._openrouter_key_loaded = True
        return self.openrouter_key is not None
    
    async def analyze_email_thread(self, emails: List[Dict[str, Any]], thread_subject: str) -> Dict[str, Any]:
        """
        Analyze a complete email thread to understand context, outcomes, and action items
        
        Args:
            emails: List of emails in the thread (chronologically ordered)
            thread_subject: The subject line of the thread
            
        Returns:
            Dict with analysis including:
            - summary: What this conversation is about
            - outcome: What has been resolved or decided
            - action_items: What needs to be done
            - follow_up_needed: Whether follow-up is required
            - priority: Urgency level
            - context: Full context for understanding
        """
        if not await self._ensure_openrouter_key():
            return self._fallback_analysis(emails, thread_subject)
        
        # Build comprehensive thread context
        thread_text = self._build_thread_context(emails)
        
        # Create analysis prompt
        prompt = f"""Analyze this email thread comprehensively and provide actionable insights.

THREAD SUBJECT: {thread_subject}

THREAD CONTENT (chronological order, oldest to newest):
{thread_text}

Please analyze this thread and provide:

1. **SUMMARY** (2-3 sentences): What is this conversation about? What's the main topic/issue?

2. **OUTCOME** (1-2 sentences): What has been resolved, decided, or concluded? If nothing resolved yet, state "Ongoing - no resolution yet"

3. **ACTION ITEMS** (bullet list): What specific actions do I need to take? Be concrete and actionable. If none, state "None - informational only"

4. **FOLLOW-UP NEEDED** (Yes/No + reason): Do I need to follow up? When and why?

5. **PRIORITY** (High/Medium/Low + reason): How urgent is this based on the content and timeline?

6. **KEY CONTEXT** (1 sentence): The most important thing to remember about this thread.

Format your response as:
SUMMARY: [your summary]
OUTCOME: [outcome or status]
ACTION ITEMS: [list or "None"]
FOLLOW_UP: [Yes/No - reason]
PRIORITY: [level - reason]
CONTEXT: [key context]
"""
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://adourish.github.io",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    analysis_text = result['choices'][0]['message']['content'].strip()
                    return self._parse_analysis(analysis_text, emails, thread_subject)
                else:
                    logger.warning(f"OpenRouter response missing choices: {result}")
                    return self._fallback_analysis(emails, thread_subject)
            else:
                logger.warning(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._fallback_analysis(emails, thread_subject)
                
        except Exception as e:
            logger.warning(f"Thread analysis failed: {e}")
            return self._fallback_analysis(emails, thread_subject)
    
    def _build_thread_context(self, emails: List[Dict[str, Any]]) -> str:
        """Build chronological thread context from emails"""
        thread_lines = []
        
        for i, email in enumerate(emails, 1):
            sender = email.get('from', 'Unknown')
            date = email.get('date', 'Unknown date')
            body = email.get('body', email.get('preview', ''))[:800]  # First 800 chars
            
            thread_lines.append(f"--- Email {i} ---")
            thread_lines.append(f"From: {sender}")
            thread_lines.append(f"Date: {date}")
            thread_lines.append(f"Content: {body}")
            thread_lines.append("")
        
        return "\n".join(thread_lines)
    
    def _parse_analysis(self, analysis_text: str, emails: List[Dict[str, Any]], thread_subject: str) -> Dict[str, Any]:
        """Parse the AI analysis response into structured data"""
        lines = analysis_text.split('\n')
        analysis = {
            'summary': '',
            'outcome': '',
            'action_items': [],
            'follow_up_needed': False,
            'follow_up_reason': '',
            'priority': 'medium',
            'priority_reason': '',
            'context': '',
            'thread_subject': thread_subject,
            'email_count': len(emails),
            'latest_sender': emails[-1].get('from', 'Unknown') if emails else 'Unknown',
            'latest_date': emails[-1].get('date', 'Unknown') if emails else 'Unknown'
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                analysis['summary'] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('OUTCOME:'):
                current_section = 'outcome'
                analysis['outcome'] = line.replace('OUTCOME:', '').strip()
            elif line.startswith('ACTION ITEMS:'):
                current_section = 'action_items'
                action_text = line.replace('ACTION ITEMS:', '').strip()
                if action_text and action_text.lower() != 'none':
                    analysis['action_items'].append(action_text)
            elif line.startswith('FOLLOW_UP:') or line.startswith('FOLLOW-UP:'):
                current_section = 'follow_up'
                follow_text = line.replace('FOLLOW_UP:', '').replace('FOLLOW-UP:', '').strip()
                analysis['follow_up_needed'] = follow_text.lower().startswith('yes')
                analysis['follow_up_reason'] = follow_text
            elif line.startswith('PRIORITY:'):
                current_section = 'priority'
                priority_text = line.replace('PRIORITY:', '').strip()
                if 'high' in priority_text.lower():
                    analysis['priority'] = 'high'
                elif 'low' in priority_text.lower():
                    analysis['priority'] = 'low'
                else:
                    analysis['priority'] = 'medium'
                analysis['priority_reason'] = priority_text
            elif line.startswith('CONTEXT:'):
                current_section = 'context'
                analysis['context'] = line.replace('CONTEXT:', '').strip()
            elif current_section == 'action_items' and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                item = line.lstrip('-•* ').strip()
                if item and item.lower() != 'none':
                    analysis['action_items'].append(item)
            elif current_section and line and not line.startswith(('SUMMARY', 'OUTCOME', 'ACTION', 'FOLLOW', 'PRIORITY', 'CONTEXT')):
                # Continuation of previous section
                if current_section == 'summary':
                    analysis['summary'] += ' ' + line
                elif current_section == 'outcome':
                    analysis['outcome'] += ' ' + line
                elif current_section == 'context':
                    analysis['context'] += ' ' + line
        
        return analysis
    
    def _fallback_analysis(self, emails: List[Dict[str, Any]], thread_subject: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        latest_email = emails[-1] if emails else {}
        
        return {
            'summary': f"Email thread: {thread_subject}",
            'outcome': "Unknown - AI analysis unavailable",
            'action_items': ["Review email thread and determine action needed"],
            'follow_up_needed': True,
            'follow_up_reason': "Manual review required",
            'priority': 'medium',
            'priority_reason': 'Default priority - manual review needed',
            'context': f"{len(emails)} emails in thread",
            'thread_subject': thread_subject,
            'email_count': len(emails),
            'latest_sender': latest_email.get('from', 'Unknown'),
            'latest_date': latest_email.get('date', 'Unknown')
        }
    
    async def create_comprehensive_daily_summary(
        self,
        email_analyses: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> str:
        """
        Create clean summary with top 3 actions for DakBoard title
        
        Returns:
            Clean string with top 3 action items only
        """
        actions = []
        
        # Collect all actions with priority
        all_items = []
        
        # High priority first
        for analysis in email_analyses:
            if analysis.get('action_items') and analysis['priority'] == 'high':
                for action in analysis['action_items'][:1]:  # First action only
                    all_items.append((action, 'high'))
        
        # Medium priority next
        for analysis in email_analyses:
            if analysis.get('action_items') and analysis['priority'] == 'medium':
                for action in analysis['action_items'][:1]:
                    all_items.append((action, 'medium'))
        
        # Take top 3 actions
        for action, priority in all_items[:3]:
            # Shorten if too long
            if len(action) > 70:
                action = action[:67] + "..."
            actions.append(f"• {action}")
        
        # If no actions, show count
        if not actions:
            if email_analyses:
                return f"{len(email_analyses)} threads to review"
            else:
                return "No urgent actions"
        
        return " | ".join(actions)
