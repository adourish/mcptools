"""
File System Tools for MCP Server
Handles scanning Downloads and Inbox folders for unfiled items
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class FileSystemTools:
    """Tools for scanning local file system"""
    
    def __init__(self):
        self.inbox_path = r'G:\My Drive\01_Operate\Inbox'
        self.downloads_path = os.path.expanduser('~\\Downloads')
    
    def check_new_files(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Check for new files in Inbox and Downloads folders"""
        file_items = []
        status_messages = []
        
        # Check Inbox folder
        if os.path.exists(self.inbox_path):
            try:
                files = [f for f in os.listdir(self.inbox_path) 
                        if os.path.isfile(os.path.join(self.inbox_path, f))]
                if files:
                    status_messages.append(f"📁 Inbox: {len(files)} files need filing")
                    file_items.append({
                        'title': f'File {len(files)} items from Inbox folder',
                        'source': 'File Organization',
                        'due': datetime.now().strftime('%Y-%m-%d'),
                        'priority': 'normal',
                        'location': self.inbox_path,
                        'count': len(files)
                    })
            except Exception as e:
                logger.warning(f"Could not scan Inbox folder: {e}")
        
        # Check Downloads folder
        if os.path.exists(self.downloads_path):
            try:
                recent_files = []
                for f in os.listdir(self.downloads_path):
                    file_path = os.path.join(self.downloads_path, f)
                    if os.path.isfile(file_path):
                        mtime = os.path.getmtime(file_path)
                        if (datetime.now().timestamp() - mtime) < (7 * 24 * 3600):
                            recent_files.append(f)
                
                if recent_files:
                    status_messages.append(f"💾 Downloads: {len(recent_files)} recent files")
                    file_items.append({
                        'title': f'Process {len(recent_files)} recent downloads',
                        'source': 'File Organization',
                        'due': datetime.now().strftime('%Y-%m-%d'),
                        'priority': 'normal',
                        'location': self.downloads_path,
                        'count': len(recent_files)
                    })
            except Exception as e:
                logger.warning(f"Could not scan Downloads folder: {e}")
        
        if file_items:
            logger.info(f"Found {len(file_items)} file organization tasks")
        
        return file_items, status_messages
