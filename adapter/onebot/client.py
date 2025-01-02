import asyncio
import websockets
import json
import uuid
from typing import Dict, Any, Optional, Callable, List

class OneBotClient:
    def __init__(self, uri: str):
        """
        初始化 OneBotClient 实例。

        :param uri: WebSocket 服务器的 URI
        """
        self.uri = uri
        self.callbacks: Dict[str, asyncio.Future] = {}
        self.event_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    async def connect(self) -> None:
        """
        连接到 WebSocket 服务器并处理消息。
        """
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket
            await self.handle_messages(websocket)

    async def handle_messages(self, websocket: websockets.WebSocketClientProtocol) -> None:
        """
        处理从 WebSocket 接收到的消息。

        :param websocket: WebSocket 客户端协议实例
        """
        async for message in websocket:
            await self.process_message(message)

    async def process_message(self, message: str) -> None:
        """
        处理接收到的消息。

        :param message: 接收到的消息字符串
        """
        message_data = json.loads(message)
        if 'echo' in message_data:
            echo = message_data['echo']
            if echo in self.callbacks:
                self.callbacks[echo].set_result(message_data)
                del self.callbacks[echo]
        else:
            # 处理其他类型的消息
            post_type = message_data.get('post_type')
            if post_type and post_type in self.event_handlers:
                for handler in self.event_handlers[post_type]:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message_data)
                    else:
                        handler(message_data)
                    
    def event(self, event: str):
        """
        装饰器：注册事件处理函数。

        :param event: 事件名称
        """
        def decorator(handler: Callable[[Dict[str, Any]], None]) -> Callable[[Dict[str, Any]], None]:
            if event not in self.event_handlers:
                self.event_handlers[event] = []
            self.event_handlers[event].append(handler)
            return handler
        return decorator
    
    async def send_api(self, action: str, params: Dict[str, Any], wait: bool = False) -> Optional[Dict[str, Any]]:
        """
        发送 API 请求。

        :param action: API 动作
        :param params: API 参数
        :param wait: 是否等待回应
        :return: 如果等待回应，则返回回应数据，否则返回 None
        """
        echo = str(uuid.uuid4())
        message_data = {
            "action": action,
            "params": params,
            "echo": echo
        }
        if wait:
            future = asyncio.get_event_loop().create_future()
            self.callbacks[echo] = future
            await self.websocket.send(json.dumps(message_data))
            return await future
        else:
            await self.websocket.send(json.dumps(message_data))
            return None

    async def register_event(self, event: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        注册事件。

        :param event: 事件名称
        :param handler: 事件处理函数
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def run(self) -> None:
        """
        运行客户端，连接到 WebSocket 服务器。
        """
        asyncio.run(self.connect())