from fastapi import WebSocket, WebSocketException, status


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, match_id: int):
        await websocket.accept()

        if match_id not in self.active_connections:
            self.active_connections[match_id] = []
        
        self.active_connections[match_id].append(websocket)

    def disconnect(self, websocket: WebSocket, match_id:int):
        self.active_connections[match_id].remove(websocket)
    
        if len(self.active_connections[match_id]) == 0:
            del self.active_connections[match_id]

    async def broadcast(self, message: dict, match_id: int):
        for connection in self.active_connections[match_id]:
            await connection.send_json(message)

manager = ConnectionManager()