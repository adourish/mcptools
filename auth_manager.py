#!/usr/bin/env python3
"""
Authentication Manager for MCP Server
Handles OAuth tokens with automatic refresh
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages OAuth tokens with automatic refresh"""
    
    def __init__(self, env_path: Path):
        self.env_path = env_path
        self.gmail_token_path = Path(r'G:\My Drive\03_Areas\Keys\Gmail\token.json')
        
        # Load environment config
        with open(env_path, 'r') as f:
            self.env_config = json.load(f)
        
        # Cache for credentials
        self._gmail_creds = None
        self._todoist_token = None
        self._amplenote_token = None
        self._openrouter_key = None
        
        logger.info("AuthManager initialized")
    
    async def get_gmail_credentials(self) -> Credentials:
        """Get Gmail credentials, refreshing if needed"""
        if self._gmail_creds and not self._gmail_creds.expired:
            return self._gmail_creds
        
        # Load from token file
        if self.gmail_token_path.exists():
            with open(self.gmail_token_path, 'r') as f:
                token_data = json.load(f)
            
            self._gmail_creds = Credentials(
                token=token_data['token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            
            # Refresh if expired
            if self._gmail_creds.expired and self._gmail_creds.refresh_token:
                logger.info("Refreshing Gmail token")
                self._gmail_creds.refresh(Request())
                
                # Save refreshed token
                token_data['token'] = self._gmail_creds.token
                with open(self.gmail_token_path, 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                logger.info("Gmail token refreshed and saved")
        
        return self._gmail_creds
    
    async def get_todoist_token(self) -> str:
        """Get Todoist API token"""
        if not self._todoist_token:
            self._todoist_token = self.env_config['environments']['todoist']['credentials']['apiToken']
        return self._todoist_token
    
    async def get_amplenote_token(self) -> str:
        """Get Amplenote API token, refreshing if needed"""
        if self._amplenote_token:
            return self._amplenote_token
        
        try:
            amplenote_config = self.env_config['environments']['amplenote']
            
            # Try different token locations in config
            if 'oauth' in amplenote_config and 'accessToken' in amplenote_config['oauth']:
                self._amplenote_token = amplenote_config['oauth']['accessToken']
            elif 'credentials' in amplenote_config and 'accessToken' in amplenote_config['credentials']:
                self._amplenote_token = amplenote_config['credentials']['accessToken']
            elif 'accessToken' in amplenote_config:
                self._amplenote_token = amplenote_config['accessToken']
            else:
                raise KeyError("Could not find Amplenote access token in config")
            
            return self._amplenote_token
        except Exception as e:
            logger.error(f"Error getting Amplenote token: {e}")
            raise
    
    async def get_openrouter_key(self) -> Optional[str]:
        """Get OpenRouter API key from environments config"""
        if self._openrouter_key:
            return self._openrouter_key
        
        try:
            # Try to get OpenRouter key from environments config
            if 'openrouter' in self.env_config.get('environments', {}):
                openrouter_config = self.env_config['environments']['openrouter']
                if 'credentials' in openrouter_config and 'apiKey' in openrouter_config['credentials']:
                    self._openrouter_key = openrouter_config['credentials']['apiKey']
                elif 'apiKey' in openrouter_config:
                    self._openrouter_key = openrouter_config['apiKey']
            
            if self._openrouter_key:
                logger.info("Loaded OpenRouter API key from environments config")
            else:
                logger.warning("OpenRouter API key not found in environments config - AI features will be disabled")
            
            return self._openrouter_key
        except Exception as e:
            logger.warning(f"Error loading OpenRouter key: {e} - AI features will be disabled")
            return None
    
    async def refresh_amplenote_token(self) -> str:
        """Refresh Amplenote access token using refresh token"""
        try:
            amplenote_config = self.env_config['environments']['amplenote']
            
            refresh_token = amplenote_config['credentials']['refreshToken']
            client_id = amplenote_config['oauth']['clientId']
            
            logger.info("Refreshing Amplenote access token...")
            
            # Make refresh request
            response = requests.post(
                'https://api.amplenote.com/oauth/token',
                json={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': client_id
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update config with new tokens
                amplenote_config['credentials']['accessToken'] = token_data['access_token']
                if 'refresh_token' in token_data:
                    amplenote_config['credentials']['refreshToken'] = token_data['refresh_token']
                
                # Save updated config
                with open(self.env_path, 'w') as f:
                    json.dump(self.env_config, f, indent=2)
                
                # Update cache
                self._amplenote_token = token_data['access_token']
                
                logger.info(f"Amplenote token refreshed successfully (expires in {token_data.get('expires_in', 'unknown')} seconds)")
                return self._amplenote_token
            else:
                logger.error(f"Amplenote token refresh failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to refresh Amplenote token: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error refreshing Amplenote token: {e}")
            raise
    
    async def refresh_all_tokens(self):
        """Refresh all tokens that need refreshing"""
        logger.info("Checking all tokens for refresh")
        
        try:
            # Refresh Gmail
            await self.get_gmail_credentials()
            logger.info("Gmail token checked/refreshed")
        except Exception as e:
            logger.error(f"Error refreshing Gmail token: {e}")
        
        # Todoist tokens don't expire
        # Amplenote tokens - add refresh logic if needed
        
        logger.info("Token refresh check complete")
