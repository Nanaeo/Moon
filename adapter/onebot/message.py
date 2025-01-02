from adapter.message import Message, MessageSerializer
from typing import Any, Dict, List

class OnebotMessage(Message):
    @staticmethod
    def from_string(message_str: str) -> 'OnebotMessage':
        return OnebotMessage(MessageSerializer.from_string(message_str).segments)

    @staticmethod
    def from_dict(message_dict: Dict[str, Any]) -> 'OnebotMessage':
        return OnebotMessage(MessageSerializer.from_dict(message_dict).segments)

    def to_dict(self) -> List[Dict[str, Any]]:
        return MessageSerializer.to_dict(self)

    def to_string(self) -> str:
        return MessageSerializer.to_string(self)