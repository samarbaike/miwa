from fastapi import WebSocket
import asyncio

class RoomManager:
    def __init__(self):
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, match_id: int, player_id:int):
        #in the ws router for the connect() methods do
        #
        #await websocket.accept()
        #await room_manager.connect_player(player_id, websocket)
        if match_id not in self.active_connections:
            self.active_connections[match_id] = {}
        
        self.active_connections[match_id][player_id] = websocket

    def disconnect(self, match_id:int, player_id: int):
        if match_id in self.active_connections:
            self.active_connections[match_id].pop(player_id, None)
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
    
    async def broadcast(self, match_id: int, message: dict):
        if match_id not in self.active_connections:
            return
        
        connections = self.active_connections[match_id]
        to_remove = []

        async def safe_send(player_id, ws):
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(player_id)

        await asyncio.gather(
            *(safe_send(pid, ws) for pid, ws in connections.items())
        )
            
        #cleanup
        for pid in to_remove:
            del connections[pid]

        if not connections:
            del self.active_connections[match_id]    
            
            
            
            
            
            for ws in self.active_connections[match_id].values():
                await ws.send_json(message)
    
    async def send_to(self, match_id: int, player_id: int, message: dict):
        if match_id in self.active_connections:
            ws = self.active_connections[match_id].get(player_id)
            if ws:
                await ws.send_json(message)
