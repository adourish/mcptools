"""
Google Drive Tools for MCP Server
Handles Google Drive file scanning and document tracking
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class DriveTools:
    """Tools for interacting with Google Drive"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.service = None
    
    async def _get_service(self):
        """Get or create Drive service"""
        if not self.service:
            creds = await self.auth_manager.get_gmail_credentials()
            if creds:
                self.service = build('drive', 'v3', credentials=creds)
        return self.service
    
    async def get_recent_documents(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recently modified Google Drive documents"""
        try:
            service = await self._get_service()
            if not service:
                logger.warning("Drive service not available")
                return []
            
            after_date = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
            
            results = service.files().list(
                q=f"modifiedTime > '{after_date}' and (mimeType contains 'document' or mimeType contains 'spreadsheet' or mimeType contains 'presentation')",
                pageSize=10,
                fields="files(id, name, mimeType, modifiedTime, owners, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            docs = []
            
            for file in files:
                docs.append({
                    'name': file['name'],
                    'type': self._get_file_type(file['mimeType']),
                    'modified': file['modifiedTime'],
                    'owner': file.get('owners', [{}])[0].get('displayName', 'Unknown'),
                    'location': 'Google Drive',
                    'url': file.get('webViewLink', '')
                })
            
            logger.info(f"Retrieved {len(docs)} recent Google Drive documents")
            return docs
            
        except Exception as e:
            logger.error(f"Error fetching Google Drive docs: {e}")
            return []
    
    def _get_file_type(self, mime_type: str) -> str:
        """Convert MIME type to friendly file type"""
        if 'document' in mime_type or 'word' in mime_type:
            return 'Document'
        elif 'spreadsheet' in mime_type or 'excel' in mime_type:
            return 'Spreadsheet'
        elif 'presentation' in mime_type or 'powerpoint' in mime_type:
            return 'Presentation'
        elif 'pdf' in mime_type:
            return 'PDF'
        else:
            return 'File'
