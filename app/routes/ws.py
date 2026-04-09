from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/match/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id:int):
    #accepting the connection in the route
    await websocket.accept()

    #getting the manager from app.state
    room_manager = websocket.app.state.room_manager

    #telling manger to connect this websocket to this match
    await room_manager.connect(websocket, match_id, player_id)
    
    try:
        #Keepin' the line open forever, waiting for messages
        while True:
            # Wait for a message from this specific player
            data = await websocket.receive_json()
            
            #just bounceing the message back to everyone in the room
            await room_manager.broadcast(match_id, data)
            
    except WebSocketDisconnect:
        # 3. If the player's internet drops, tell the manager to disconnect them
        room_manager.disconnect(match_id, player_id)