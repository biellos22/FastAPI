from fastapi import WebSocket
from redis import Redis
from typing import List, Dict

class ChatManager:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, chat_id: str, websocket: WebSocket):
        self.active_connections[chat_id].remove(websocket)
        if len(self.active_connections[chat_id]) == 0:
            del self.active_connections[chat_id]

    async def broadcast(self, chat_id: str, message: str):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                await connection.send_text(message)
        self.save_message(chat_id, message)

    def save_message(self, chat_id: str, message: str):
        self.redis_client.rpush(f"chat:{chat_id}", message)

    def get_chat_history(self, chat_id: str):
        return self.redis_client.lrange(f"chat:{chat_id}", 0, -1)
