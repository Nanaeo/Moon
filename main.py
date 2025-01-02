import asyncio
from adapter.onebot.client import OneBotClient
from adapter.onebot.message import OnebotMessage

bot = OneBotClient(uri="ws://127.0.0.1:3001/")

@bot.event('message')
async def on_message(data):
    message = OnebotMessage.from_dict(data['message'])
    for segment in message.segments:
        if segment.type == 'text':
           print('[文本] ' ,segment.data['text'])
        elif segment.type == 'image':
           print(f'[图片] {segment.data["summary"]} ({segment.data["url"]})')
        elif segment.type == 'at':
            print(f'[At] {segment.data["qq"]}')
        elif segment.type == 'face':
            print(f'[表情] {segment.data["id"]}')
        elif segment.type == 'file':
            print(f'[文件] [{segment.data["name"]}]({segment.data["url"]})')
        elif segment.type == 'reply':
            print(f'[回复] {segment.data["id"]}')
        elif segment.type == 'video':
            print(f'[视频] [{segment.data["summary"]}]({segment.data["url"]})')
           

async def main():
    await bot.connect()

asyncio.run(main())