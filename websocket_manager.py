import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time location tracking"""
    
    def __init__(self):
        # courier_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # courier_id -> latest location
        self.courier_locations: Dict[str, dict] = {}
    
    async def connect(self, courier_id: str, websocket: WebSocket):
        await websocket.accept()
        if courier_id not in self.active_connections:
            self.active_connections[courier_id] = set()
        self.active_connections[courier_id].add(websocket)
        logger.info(f"Courier {courier_id} connected. Total connections: {len(self.active_connections[courier_id])}")
    
    def disconnect(self, courier_id: str, websocket: WebSocket):
        if courier_id in self.active_connections:
            self.active_connections[courier_id].discard(websocket)
            if not self.active_connections[courier_id]:
                del self.active_connections[courier_id]
                if courier_id in self.courier_locations:
                    del self.courier_locations[courier_id]
        logger.info(f"Courier {courier_id} disconnected")
    
    async def send_personal_message(self, message: dict, courier_id: str):
        if courier_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[courier_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to courier {courier_id}: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(courier_id, connection)
    
    async def broadcast_to_admins(self, message: dict):
        """Broadcast message to all admin connections"""
        for courier_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {courier_id}: {e}")
    
    async def update_location(self, courier_id: str, location_data: dict):
        """Update courier location and notify admins"""
        self.courier_locations[courier_id] = location_data
        
        # Broadcast to admin clients
        await self.broadcast_to_admins({
            "type": "location_update",
            "courier_id": courier_id,
            "location": location_data
        })
    
    def get_all_courier_locations(self) -> Dict[str, dict]:
        """Get all courier locations"""
        return self.courier_locations.copy()


manager = ConnectionManager()
