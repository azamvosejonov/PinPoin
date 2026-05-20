from fastapi import WebSocket
class SupportConnectionManager:
    def __init__(self):
        # {ticket_id: {user_id: WebSocket}}
        self.connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, ticket_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if ticket_id not in self.connections:
            self.connections[ticket_id] = {}
        self.connections[ticket_id][user_id] = websocket

    def disconnect(self, ticket_id: int, user_id: int):
        if ticket_id in self.connections:
            self.connections[ticket_id].pop(user_id, None)
            if not self.connections[ticket_id]:
                del self.connections[ticket_id]

    async def broadcast_to_ticket(self, ticket_id: int, message: dict, exclude_user_id: int = None):
        """Ticket ga ulangan barcha foydalanuvchilarga xabar yuboradi"""
        if ticket_id not in self.connections:
            return
        dead = []
        for uid, ws in self.connections[ticket_id].items():
            if uid == exclude_user_id:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(uid)
        for uid in dead:
            self.disconnect(ticket_id, uid)

manager = SupportConnectionManager()
