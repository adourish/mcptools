#!/usr/bin/env python3
"""
Check what tasks are currently in Todoist
"""

import asyncio
from pathlib import Path
from auth_manager import AuthManager
from todoist_tools import TodoistTools

async def main():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    todoist = TodoistTools(auth)
    
    print("Fetching Todoist tasks...")
    headers = await todoist._get_headers()
    
    import requests
    response = requests.get(f"{todoist.base_url}/tasks", headers=headers)
    
    if response.status_code == 200:
        tasks = response.json()
        tasks = tasks.get('results', []) if isinstance(tasks, dict) else tasks
        
        print(f"\nTotal tasks: {len(tasks)}")
        print("\nDaily plan tasks (🎯 TODAY and ⏰ SOON):")
        
        for task in tasks:
            content = task.get('content', '')
            if content.startswith('🎯 TODAY:') or content.startswith('⏰ SOON:'):
                print(f"\n{'='*60}")
                print(f"Task: {content}")
                desc = task.get('description', '')
                if desc:
                    print(f"Description preview: {desc[:200]}...")
                else:
                    print("No description")
    else:
        print(f"Error: {response.status_code}")

if __name__ == '__main__':
    asyncio.run(main())
