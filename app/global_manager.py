from fastapi import WebSocket

class GlobalManager:
    def __init__(self):
        self.active_players: dict[int, WebSocket] = {}

    async def connect_player(self, player_id: int, websocket: WebSocket):
        #in the ws router for the connect_player() methods do 
        #
        #await websocket.accept()
        #await global_manager.connect_player(player_id, websocket)
        self.active_players[player_id] = websocket

    def disconnect_player(self, player_id: int):
        if player_id in self.active_players:
            del self.active_players[player_id]

    async def notify_match_found(self, player_id: int, match_id: int):
        if player_id in self.active_players:
            ws = self.active_players[player_id]
            await ws.send_json({
                "event": "match_found",
                "match_id": match_id
            })