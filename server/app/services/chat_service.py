 # WebSocket management
from typing import Dict, Set
from fastapi import WebSocket

# Manages all active WebSocket connections.
class ConnectionManager:
   
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Accept connection and store it"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Remove connection when user disconnects"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, receiver_id: int):
        """
        Send message to a specific user if they're online.
        If receiver is offline, message is still saved in database.
        """
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            await websocket.send_json(message)

    def is_online(self, user_id: int) -> bool:
        """Check if a user is currently connected"""
        return user_id in self.active_connections

# Single instance used across the entire app
manager = ConnectionManager()
