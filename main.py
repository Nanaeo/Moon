import asyncio
from common.config import config
from typing import List
from adapter.message import MessageSegment, MessageBuilder
from adapter.onebot.client import OneBotClient
from adapter.onebot.message import OnebotMessage
from application.copilot import GithubCopilot, TokenManager

bot = OneBotClient(uri=config['websocket_onebot'])
self_id = config['self_id']
context = {}
proxy = config['proxy']
repo = []
token_manager: TokenManager = None

async def msg2text(msg: List[MessageSegment]) -> str:
    return ''.join(segment.data['text'] for segment in msg if segment.type == 'text')

async def handle_message(data):
    global repo
    message = OnebotMessage.from_dict(data['message'])
    
    if message.segments[0].type == 'at' and message.segments[0].data['qq'] == str(self_id):
        print("Bot was mentioned in a message.")
        
        copilot = GithubCopilot(await token_manager.get_token(), proxy=proxy)
        
        if not repo:
            repo.append(await copilot.get_context(config['repo']))
            print("Repository context obtained.")
        
        text = await msg2text(message.segments[1:])
        print(f"Message content: {text}")

        group_id = data['group_id']
        if group_id not in context or context[group_id]['len'] > 50:
            await create_new_thread(copilot, group_id)
        
        ret = await generate_response(copilot, group_id, text)
        await send_response(group_id, ret)

@bot.event('message')
async def on_message(data):
    await handle_message(data)

async def create_new_thread(copilot, group_id):
    threads = await copilot.create_thread()
    thread_id = threads['thread_id']
    context[group_id] = {"thread_id": thread_id, "len": 0}
    print(f"New thread created for group {group_id} {thread_id}.")

async def generate_response(copilot, group_id, text):
    ret = await copilot.chat_copilot(
        context[group_id]['thread_id'], 
        await copilot.create_context(
            repo,
            repo, 
            config['promote'] + text, True)
    )
    context[group_id]['len'] += 1
    print(ret)
    return ret

async def send_response(group_id, response):
    msg = MessageBuilder()
    await bot.send_api(action='send_msg', params={'group_id': group_id, 'message': msg.text(response).build().to_dict()})
    print(f"Response sent to group {group_id}.")

async def main():
    global token_manager
    token_manager = TokenManager(cookie=config['cookie'], proxy=proxy)
    await bot.connect()

asyncio.run(main())