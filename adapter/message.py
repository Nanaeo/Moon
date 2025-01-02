import json
from typing import Dict, List, Iterator, Type, Union, Optional, Any

class MessageSegment:
    def __init__(self, type: str, data: Dict[str, Any]):
        self.type = type
        self.data = data

    def __str__(self) -> str:
        return json.dumps({"type": self.type, "data": self.data})

    @staticmethod
    def from_dict(segment_dict: Dict[str, Union[str, Dict[str, Any]]]) -> 'MessageSegment':
        segment_classes: Dict[str, Type[MessageSegment]] = {
            'text': TextSegment,
            'image': ImageSegment,
            'at': AtSegment,
            'face': FaceSegment,
            'file': FileSegment,
            'reply': ReplySegment,
            'video': VideoSegment
        }
        segment_type = segment_dict['type']
        segment_data = segment_dict['data']
        segment_class = segment_classes.get(segment_type, MessageSegment)
        try:
            return segment_class(**segment_data)
        except TypeError:
            return MessageSegment(segment_type, segment_data)

class TextSegment(MessageSegment):
    def __init__(self, text: str):
        super().__init__('text', {'text': text})

class ImageSegment(MessageSegment):
    def __init__(self, url: str):
        super().__init__('image', {'url': url})

class AtSegment(MessageSegment):
    def __init__(self, qq: str):
        super().__init__('at', {'qq': qq})

class FaceSegment(MessageSegment):
    def __init__(self, id: str):
        super().__init__('face', {'id': id})

class FileSegment(MessageSegment):
    def __init__(self, url: str):
        super().__init__('file', {'url': url})

class ReplySegment(MessageSegment):
    def __init__(self, id: str):
        super().__init__('reply', {'id': id})

class VideoSegment(MessageSegment):
    def __init__(self, url: str, summary: str):
        super().__init__('video', {'url': url})

class Message:
    def __init__(self, segments: Optional[List[MessageSegment]] = None):
        self.segments = segments if segments else []

    def write(self, segment: MessageSegment) -> 'Message':
        self.segments.append(segment)
        return self

    def read(self, index: int) -> MessageSegment:
        return self.segments[index]

    def __str__(self) -> str:
        return MessageSerializer.to_string(self)

    def __iter__(self) -> Iterator[MessageSegment]:
        return iter(self.segments)

class MessageBuilder:
    def __init__(self):
        self.message = Message()

    def text(self, text: str) -> 'MessageBuilder':
        return self.append(TextSegment(text))

    def image(self, url: str) -> 'MessageBuilder':
        return self.append(ImageSegment(url))

    def at(self, qq: str) -> 'MessageBuilder':
        return self.append(AtSegment(qq))

    def face(self, id: str) -> 'MessageBuilder':
        return self.append(FaceSegment(id))

    def file(self, url: str) -> 'MessageBuilder':
        return self.append(FileSegment(url))

    def reply(self, id: str) -> 'MessageBuilder':
        return self.append(ReplySegment(id))

    def append(self, segment: MessageSegment) -> 'MessageBuilder':
        self.message.write(segment)
        return self

    def build(self) -> Message:
        return self.message

class MessageSerializer:
    @staticmethod
    def from_string(message_str: str) -> Message:
        return MessageSerializer.from_dict(json.loads(message_str))

    @staticmethod
    def from_dict(message_dict: List[Dict[str, Union[str, Dict[str, Any]]]]) -> Message:
        message = Message()
        for segment_dict in message_dict:
            segment_obj = MessageSegment.from_dict(segment_dict)
            if segment_obj:
                message.segments.append(segment_obj)
        return message

    @staticmethod
    def to_dict(message: Message) -> List[Dict[str, Union[str, Dict[str, Any]]]]:
        return [json.loads(str(segment)) for segment in message.segments]

    @staticmethod
    def to_string(message: Message) -> str:
        return json.dumps(MessageSerializer.to_dict(message))