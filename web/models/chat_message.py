"""Chat message data model"""

from datetime import datetime


class ChatMessage:
    """Represents a chat message"""

    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
