#!/usr/bin/env python3
"""
Amplenote tools for MCP Server
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class AmplenoteTools:
    """Amplenote operations for MCP server"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.base_url = "https://api.amplenote.com/v4"
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token"""
        token = await self.auth_manager.get_amplenote_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    async def create_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new note in Amplenote"""
        headers = await self._get_headers()
        
        try:
            note_data = {'name': title, 'text': content}
            
            if tags:
                # Amplenote expects tags as array of objects with 'text' field
                note_data['tags'] = [{'text': tag} for tag in tags]
            
            logger.info(f"Sending to Amplenote - Title: {title}, Body length: {len(content)}")
            logger.debug(f"Note data structure: {note_data}")
            
            response = requests.post(
                f"{self.base_url}/notes",
                headers=headers,
                json=note_data
            )
            
            logger.info(f"Amplenote response status: {response.status_code}")
            logger.debug(f"Amplenote response: {response.text}")
            
            if response.status_code == 401:
                logger.warning("Amplenote token expired, attempting automatic refresh...")
                
                # Try to refresh the token automatically
                try:
                    new_token = await self.auth_manager.refresh_amplenote_token()
                    logger.info("Token refreshed successfully, retrying request...")
                    
                    # Retry the request with new token
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.post(
                        f"{self.base_url}/notes",
                        headers=headers,
                        json=note_data
                    )
                    
                    if response.status_code >= 400:
                        logger.error(f"Amplenote API error after refresh: {response.status_code} - {response.text}")
                        raise Exception(f"Amplenote API error: {response.status_code}")
                    
                    # Success after refresh
                    note = response.json()
                    logger.info(f"Created Amplenote note after token refresh: {title}")
                    return note
                    
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh Amplenote token: {refresh_error}")
                    print("\n" + "=" * 70)
                    print("⚠️  AMPLENOTE TOKEN REFRESH FAILED")
                    print("=" * 70)
                    print("\nAutomatic token refresh failed.")
                    print("\nTo manually refresh the token, run:")
                    print('  cd "G:\\My Drive\\06_Master_Guides\\Scripts"')
                    print("  node refresh_amplenote_token.js")
                    print("\nThen run process new again.")
                    print("=" * 70 + "\n")
                    raise Exception("Amplenote token refresh failed - manual intervention required")
            elif response.status_code >= 400:
                logger.error(f"Amplenote API error: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            note = response.json()
            logger.info(f"Created Amplenote note: {title}")
            return note
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Already handled above, just re-raise
                raise
            logger.error(f"Error creating Amplenote note: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating Amplenote note: {e}")
            raise
    
    async def get_notes(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notes from Amplenote"""
        headers = await self._get_headers()
        
        try:
            url = f"{self.base_url}/notes"
            if tag:
                url += f"?tag={tag}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                logger.warning("Amplenote token expired, attempting automatic refresh...")
                
                try:
                    new_token = await self.auth_manager.refresh_amplenote_token()
                    logger.info("Token refreshed successfully, retrying request...")
                    
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code >= 400:
                        logger.error(f"Amplenote API error after refresh: {response.status_code} - {response.text}")
                        raise Exception(f"Amplenote API error: {response.status_code}")
                
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh Amplenote token: {refresh_error}")
                    raise Exception("Amplenote token refresh failed - manual intervention required")
            
            response.raise_for_status()
            
            response_data = response.json()
            # API returns dict with 'notes' key containing array of note objects
            if isinstance(response_data, dict) and 'notes' in response_data:
                notes = response_data['notes']
            elif isinstance(response_data, list):
                notes = response_data
            else:
                logger.warning(f"Unexpected API response format: {type(response_data)}")
                notes = []
            
            logger.info(f"Retrieved {len(notes)} notes from Amplenote")
            return notes
        
        except Exception as e:
            logger.error(f"Error getting Amplenote notes: {e}")
            raise
    
    async def find_daily_note(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find today's daily note by title pattern"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        headers = await self._get_headers()
        
        try:
            response = requests.get(f"{self.base_url}/notes", headers=headers)
            response.raise_for_status()
            notes_data = response.json()
            
            # Handle different response formats
            if isinstance(notes_data, dict) and 'notes' in notes_data:
                notes = notes_data['notes']
            elif isinstance(notes_data, list):
                notes = notes_data
            else:
                logger.warning(f"Unexpected notes response format: {type(notes_data)}")
                return None
            
            # Look for daily note with date in title
            for note in notes:
                if isinstance(note, str):
                    continue
                note_title = note.get('name', '') if isinstance(note, dict) else ''
                if date in note_title or datetime.now().strftime("%B %d, %Y") in note_title:
                    logger.info(f"Found daily note: {note_title}")
                    return note
            
            logger.info(f"No daily note found for {date}")
            return None
        
        except Exception as e:
            logger.error(f"Error finding daily note: {e}")
            return None
    
    async def get_note_content(self, note_uuid: str) -> str:
        """Get the full content of a note"""
        headers = await self._get_headers()
        
        try:
            response = requests.get(f"{self.base_url}/notes/{note_uuid}", headers=headers)
            response.raise_for_status()
            note = response.json()
            return note.get('body', '')
        
        except Exception as e:
            logger.error(f"Error getting note content: {e}")
            raise
    
    async def replace_note_content(self, note_uuid: str, content: str) -> bool:
        """Replace all content in a note using PUT request"""
        headers = await self._get_headers()
        
        try:
            # Use PUT to completely replace note text
            response = requests.put(
                f"{self.base_url}/notes/{note_uuid}",
                headers=headers,
                json={'text': content}
            )
            response.raise_for_status()
            logger.info(f"Replaced content in note: {note_uuid}")
            return True
        
        except Exception as e:
            logger.error(f"Error replacing note content: {e}")
            logger.error(f"Response: {response.text if 'response' in locals() else 'No response'}")
            return False
    
    async def update_note(self, note_uuid: str, content: str) -> Dict[str, Any]:
        """Update an existing note's content"""
        headers = await self._get_headers()
        
        try:
            response = requests.put(
                f"{self.base_url}/notes/{note_uuid}",
                headers=headers,
                json={'text': content}
            )
            
            if response.status_code >= 400:
                logger.error(f"Amplenote API error updating note: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            logger.info(f"Updated note: {note_uuid}")
            return response.json() if response.text else {"success": True}
        
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            raise
    
    async def delete_note(self, note_uuid: str) -> bool:
        """Delete a note"""
        headers = await self._get_headers()
        
        try:
            response = requests.delete(
                f"{self.base_url}/notes/{note_uuid}",
                headers=headers
            )
            
            if response.status_code >= 400:
                logger.error(f"Amplenote API error deleting note: {response.status_code} - {response.text}")
                return False
            
            response.raise_for_status()
            logger.info(f"Deleted note: {note_uuid}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return False
    
    async def insert_content(self, note_uuid: str, text: str) -> bool:
        """Insert content into note using actions endpoint"""
        headers = await self._get_headers()
        
        try:
            action_data = {
                'type': 'INSERT_NODES',
                'nodes': [
                    {
                        'type': 'paragraph',
                        'content': [
                            {
                                'type': 'text',
                                'text': text
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/notes/{note_uuid}/actions",
                headers=headers,
                json=action_data
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            logger.error(f"Error inserting content: {e}")
            return False
    
    async def insert_task(self, note_uuid: str, text: str, important: bool = False) -> bool:
        """Insert a task/checkbox into note"""
        headers = await self._get_headers()
        
        try:
            attrs = {}
            if important:
                attrs['flags'] = 'I'
            
            action_data = {
                'type': 'INSERT_NODES',
                'nodes': [
                    {
                        'type': 'check_list_item',
                        'attrs': attrs,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': text
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/notes/{note_uuid}/actions",
                headers=headers,
                json=action_data
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            logger.error(f"Error inserting task: {e}")
            return False
    
    async def _generate_daily_summary(self, plan: Dict[str, Any]) -> str:
        """Use AI to generate executive summary of the day"""
        try:
            # Collect all content for analysis
            emails = [item for item in plan['do_now'] if item.get('source') == 'Email']
            tasks = [item for item in plan['do_now'] if item.get('source') == 'Todoist']
            events = [item for item in plan['do_now'] if item.get('source') == 'Calendar']
            upcoming = plan['do_soon'][:5]  # Next 5 items
            
            # Build comprehensive context
            context = "Today's Overview:\n\n"
            
            if emails:
                context += "EMAILS:\n"
                for email in emails[:5]:
                    context += f"- {email.get('title', '')}\n"
                    context += f"  From: {email.get('from', '')}\n"
                    if email.get('thread_context'):
                        context += f"  Context: {email.get('thread_context', '')[:150]}\n"
                    elif email.get('preview'):
                        context += f"  Preview: {email.get('preview', '')[:150]}\n"
                context += "\n"
            
            if events:
                context += "EVENTS:\n"
                for event in events:
                    time_str = f" at {event.get('time', '')}" if event.get('time') else ""
                    context += f"- {event.get('title', '')}{time_str}\n"
                context += "\n"
            
            if tasks:
                context += "TASKS:\n"
                for task in tasks:
                    context += f"- {task.get('title', '')}\n"
                context += "\n"
            
            if upcoming:
                context += "UPCOMING:\n"
                for item in upcoming:
                    due = f" (Due: {item.get('due', '')})" if item.get('due') else ""
                    context += f"- {item.get('title', '')}{due}\n"
            
            # Generate AI summary
            import requests
            prompt = f"""Analyze this day's schedule and create a bulleted executive summary.

{context}

Create 3-5 bullet points covering:
- Key actions needed (especially responses to emails or follow-ups)
- Important deadlines or time-sensitive items
- Notable updates or responses received
- Any conflicts or scheduling considerations

Format as bullet points starting with • or -. Be specific about WHO responded and WHAT they said if relevant."""

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer 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",
                    "HTTP-Referer": "https://adourish.github.io",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    summary = result['choices'][0]['message']['content'].strip()
                    return summary
            
            return "Focus on urgent emails and scheduled events today."
            
        except Exception as e:
            logger.warning(f"Failed to generate daily summary: {e}")
            return "Review your tasks and emails to prioritize your day."
    
    async def update_daily_note_with_plan(self, plan: Dict[str, Any]) -> bool:
        """Create/update single daily plan note with content using actions endpoint"""
        try:
            # Use a single static title - no dates
            static_title = "📋 Daily Plan"
            
            # Use daily-plan tag for filtering
            all_notes = await self.get_notes(tag='daily-plan')
            
            logger.info(f"Found {len(all_notes)} notes with 'daily-plan' tag")
            
            # Find the existing daily plan note (should only be one)
            existing_note_uuid = None
            
            # Search through ALL notes to find the static title
            logger.info(f"Searching all {len(all_notes)} notes for static daily plan: {static_title}")
            
            # Check notes for the static title (use metadata from get_notes if available)
            for note_item in all_notes:
                try:
                    # note_item is a dict with metadata from get_notes
                    if isinstance(note_item, dict):
                        uuid = note_item.get('uuid')
                        name = note_item.get('name', '')
                        
                        # Check if this is THE daily plan note
                        if name == static_title:
                            existing_note_uuid = uuid
                            logger.info(f"✓ Found existing daily plan note: {static_title} (UUID: {uuid})")
                            break
                        
                except Exception as e:
                    logger.warning(f"Error checking note: {e}")
                    continue
            
            if existing_note_uuid:
                # Note exists - delete it and create fresh to avoid appending
                logger.info(f"Deleting existing daily plan note: {existing_note_uuid}")
                await self.delete_note(existing_note_uuid)
            
            # Create fresh note
            logger.info(f"Creating new daily plan note")
            note = await self.create_note(
                title=static_title,
                content="",
                tags=['daily-plan', 'process-new']
            )
            note_uuid = note['uuid']
            logger.info(f"Created new daily plan note: {note_uuid}")
            
            # Build entire note content as a string, then replace all at once
            content_lines = []
            
            # Add header with AI-generated executive summary
            content_lines.append(f"# 📋 Daily Plan")
            content_lines.append(f"*{datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}*")
            content_lines.append("")
            
            # Generate and add AI summary
            daily_summary = await self._generate_daily_summary(plan)
            content_lines.append("## 📊 Executive Summary")
            content_lines.append("")
            content_lines.append(daily_summary)
            content_lines.append("")
            content_lines.append("---")
            content_lines.append("")
            
            # Add DO NOW section - clean, prioritized list
            content_lines.append("## 🎯 Priority Actions")
            content_lines.append("")
            
            if plan['do_now']:
                for i, item in enumerate(plan['do_now'][:8], 1):  # Top 8 items
                    source = item.get('source', '')
                    source_emoji = {'Email': '📧', 'Calendar': '📅', 'Todoist': '✅'}.get(source, '•')
                    
                    # Use AI summary for emails, original title for others
                    ai_summary = item.get('ai_summary')
                    logger.info(f"Item {i}: source={source}, has_ai_summary={bool(ai_summary)}, ai_summary='{ai_summary}'")
                    
                    if source == 'Email' and ai_summary:
                        title = ai_summary
                        logger.info(f"Using AI summary: {title}")
                    else:
                        title = item['title']
                        logger.info(f"Using original title: {title}")
                    
                    # Create checkbox with priority number
                    content_lines.append(f"- [ ] **{i}. {source_emoji} {title}**")
                    
                    # Add context for emails
                    if source == 'Email':
                        if item.get('thread_context'):
                            # Clean thread context - just the key info
                            context = item['thread_context'].split('\n')[0]  # First line only
                            if len(context) > 150:
                                context = context[:150] + "..."
                            content_lines.append(f"  *{context}*")
                        
                        # Add sender
                        if item.get('from'):
                            sender = item['from'].split('<')[0].strip()  # Just name, no email
                            content_lines.append(f"  From: {sender}")
                    
                    # Add time for calendar events
                    elif source == 'Calendar' and item.get('time'):
                        content_lines.append(f"  ⏰ {item['time']}")
                    
                    content_lines.append("")
            else:
                content_lines.append("*No urgent items for today*")
                content_lines.append("")
            
            # Add DO SOON section
            content_lines.append("## ⏰ This Week")
            content_lines.append("")
            
            if plan['do_soon']:
                for item in plan['do_soon'][:7]:  # Top 7 items
                    source_emoji = {'Todoist': '✅', 'Calendar': '📅', 'Email': '📧'}.get(item.get('source'), '•')
                    title = item['title']
                    
                    # Format due date nicely
                    due_date = item.get('due', '')
                    if due_date:
                        try:
                            from datetime import datetime as dt
                            date_obj = dt.strptime(due_date, '%Y-%m-%d')
                            due_str = date_obj.strftime('%a %b %d')  # "Mon Mar 01"
                        except:
                            due_str = due_date
                    else:
                        due_str = ""
                    
                    time_str = f" at {item['time']}" if item.get('time') else ""
                    
                    content_lines.append(f"- [ ] {source_emoji} **{title}**{time_str}")
                    if due_str:
                        content_lines.append(f"  📅 {due_str}")
                    content_lines.append("")
            else:
                content_lines.append("*No upcoming items*")
                content_lines.append("")
            
            # Add footer with quick stats
            content_lines.append("---")
            content_lines.append("")
            content_lines.append(f"*{len(plan['do_now'])} priority actions • {len(plan['do_soon'])} upcoming items*")
            
            # Insert all content lines
            for line in content_lines:
                await self.insert_content(note_uuid, line)
            
            logger.info(f"Daily plan note created successfully: https://www.amplenote.com/notes/{note_uuid}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating daily plan note: {e}")
            return False
    
    def _format_plan_for_amplenote(self, plan: Dict[str, Any]) -> str:
        """Format the plan data as markdown for Amplenote"""
        lines = []
        lines.append("## Process New Results")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}*\n")
        
        # DO NOW section
        lines.append("### 🎯 DO NOW")
        if plan['do_now']:
            for item in plan['do_now']:
                if item['source'] == 'Email':
                    lines.append(f"- [ ] **{item['title']}**")
                    lines.append(f"  - From: {item.get('from', 'Unknown')}")
                    if item.get('preview'):
                        lines.append(f"  - {item['preview'][:150]}...")
                else:
                    time_str = f" at {item['time']}" if item.get('time') else ""
                    lines.append(f"- [ ] **[{item['source']}]** {item['title']}{time_str}")
        else:
            lines.append("- *No urgent items*")
        
        # DO SOON section
        lines.append("\n### ⏰ DO SOON")
        if plan['do_soon']:
            for item in plan['do_soon']:
                due_str = f" (due: {item.get('due', 'N/A')})" if item.get('due') else ""
                time_str = f" at {item['time']}" if item.get('time') else ""
                lines.append(f"- [ ] **[{item['source']}]** {item['title']}{time_str}{due_str}")
        else:
            lines.append("- *No upcoming items*")
        
        # MONITOR section
        lines.append("\n### 📋 MONITOR")
        if plan['monitor']:
            for item in plan['monitor']:
                lines.append(f"- [ ] {item['title']}")
        else:
            lines.append("- *No items to monitor*")
        
        return "\n".join(lines)
