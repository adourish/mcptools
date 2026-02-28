import asyncio
from amplenote_tools import AmplenoteTools
from auth_manager import AuthManager
from pathlib import Path

async def get_note():
    auth = AuthManager(Path(r'G:\My Drive\03_Areas\Keys\Environments\environments.json'))
    amp = AmplenoteTools(auth)
    content = await amp.get_note_content('4278c53c-1441-11f1-9567-415828fa7b74')
    print('\n=== DAILY PLAN NOTE CONTENT ===\n')
    print(content)

asyncio.run(get_note())
