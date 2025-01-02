import aiohttp
import json
from datetime import datetime, timezone

class TokenManager:
    def __init__(self, cookie=None, expiration=None, proxy=None):
        self.token = ""
        self.cookie = cookie
        self.expiration = datetime.fromisoformat(expiration) if expiration else None
        self.proxy = proxy

    async def is_token_expired(self):
        return datetime.now(timezone.utc) >= self.expiration if self.expiration else True

    async def fetch_new_token(self):
        url = "https://github.com/github-copilot/chat/token"
        headers = {
            'Referer': 'https://github.com/copilot',
            'GitHub-Verified-Fetch': 'true',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://github.com',
            "Cookie": self.cookie
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, proxy=self.proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data['token']
                    self.expiration = datetime.fromisoformat(data['expiration'])
                else:
                    raise Exception("Failed to fetch new token")

    async def get_token(self):
        if await self.is_token_expired():
            await self.fetch_new_token()
        return self.token

class GithubCopilot:
    def __init__(self, token, proxy=None):
        self.token = token
        self.proxy = proxy

    async def create_thread(self):
        url = "https://api.individual.githubcopilot.com/github/chat/threads"
        headers = {
            'Authorization': f'GitHub-Bearer {self.token}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, proxy=self.proxy) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception("Failed to create thread")
    async def get_context(self,repo):
        urlencoded = repo.replace("/", "%2F")
        url = f"https://github.com/github-copilot/chat/implicit-context/NapNeko/NapCatQQ/{urlencoded}"
        headers = {
            'Referer': 'https://github.com/copilot',
            'GitHub-Verified-Fetch': 'true',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://github.com',
            'Authorization': f'GitHub-Bearer {self.token}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, proxy=self.proxy) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception("Failed to get context")

    async def create_context(self, context,references, content, streaming=False):
        return {
            "content": content,
            "intent": "conversation",
            "references": context,
            "context": references,
            "currentURL": "https://github.com/NapNeko/NapCatQQ",
            "streaming": streaming,
            "confirmations": [],
            "customInstructions": [],
            "mode": "assistive"
        }

    async def chat_copilot(self, thread, request):
        url = f"https://api.individual.githubcopilot.com/github/chat/threads/{thread}/messages"
        headers = {
            'Authorization': f'GitHub-Bearer {self.token}',
            'Accept': 'text/event-stream'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=request, proxy=self.proxy) as response:
                if response.status == 200:
                    complete_data = ""
                    async for line in response.content:
                        if line.startswith(b"data: "):
                            data = json.loads(line[6:])
                            if data.get("type") == "content":
                                complete_data += data["body"]
                    return complete_data
                else:
                    raise Exception("Failed to get response from chat_copilot")