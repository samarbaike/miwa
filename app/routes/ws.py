from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/match/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int):
    # 1. Tell the manager to connect this websocket to this match
    await manager.connect(websocket, match_id)
    
    try:
        # 2. Keep the line open forever, waiting for messages
        while True:
            # Wait for a message from this specific player
            data = await websocket.receive_json()
            
            # For today (the smoke test), just bounce the message back to everyone in the room
            await manager.broadcast(data, match_id)
            
    except WebSocketDisconnect:
        # 3. If the player's internet drops, tell the manager to disconnect them
        manager.disconnect(websocket, match_id)