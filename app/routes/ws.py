from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func, select
import asyncio

from app.core.events import WSEvents
from app.models.question import MultipleChoice
from app.database import engine
from app.services.game_service import GameService

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
            message = await websocket.receive_json()
            event = message.get("event")
            data = message.get("data", {})
            # provided that user sends json in 
            # {"event" : "SUBMIT_ANSWER", "data" : {"answer" : 2}}
                
            if event == WSEvents.JOIN_MATCH:
            
                #just bounceing the message back to everyone in the room
                await room_manager.broadcast(match_id, {
                    "event" : WSEvents.PLAYER_JOINED,
                    "player_id" : player_id
                    })

                if (
                    len(room_manager.active_connections[match_id]) == 2 and
                    match_id not in websocket.app.state.active_games
                ):
                    with Session(engine) as db:
                        query = select(MultipleChoice.id).order_by(func.random()).limit(10)
                        q_ids = db.execute(query).scalars().all()

                    player1_id, player2_id = list(room_manager.active_connections[match_id].keys())
                    game = GameService(
                        match_id,
                        player1_id,
                        player2_id,
                        q_ids
                    )

                    websocket.app.state.active_games[match_id] = game

                    await game.start_question(websocket.app)

            elif event == WSEvents.SUBMIT_ANSWER:
                answer = data.get("answer")
                #timestamp to calculate time_taken for correct answers
                timestamp = asyncio.get_event_loop().time()

                #fetching game object from active games
                game = websocket.app.state.active_games[match_id]

                #calling handle answer from GameService
                await game.handle_answer(player_id, answer, timestamp, websocket.app)

    except WebSocketDisconnect:
        # 3. If the player's internet drops, tell the manager to disconnect them
        await room_manager.disconnect(match_id, player_id)

@router.websocket("/ws/lobby/{player_id}")
async def lobby_websocket(websocket: WebSocket, player_id: int):
    # 1. Accept the connection
    await websocket.accept()
    
    # 2. Get the GlobalManager
    global_manager = websocket.app.state.global_manager
    
    # 3. Connect the player to the global lobby
    await global_manager.connect_player(player_id, websocket)
    
    try:
        # Keep connection open waiting for server natifications (like match_found)
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        global_manager.disconnect_player(player_id)