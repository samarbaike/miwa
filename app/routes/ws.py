from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio

from app.core.events import WSEvents
from app.models.match import Match
from app.database import engine
from app.services.game_service import GameService

router = APIRouter()


@router.websocket("/ws/match/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    await websocket.accept()

    room_manager = websocket.app.state.room_manager
    await room_manager.connect(websocket, match_id, player_id)

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            data = message.get("data", {})

            if event == WSEvents.JOIN_MATCH:
                await room_manager.broadcast(match_id, {
                    "event": WSEvents.PLAYER_JOINED,
                    "player_id": player_id,
                })

                existing_game: GameService | None = websocket.app.state.active_games.get(match_id)

                # ── BOT MATCH ────────────────────────────────────────────────
                # matches.py already created and stored the GameService (with
                # ghost attached). Fire the first question as soon as the human
                # connects — no need to wait for a second socket.
                if existing_game is not None and existing_game.is_bot_match:
                    connections = room_manager.active_connections.get(match_id, {})
                    if len(connections) == 1:  # only the human; bot has no socket
                        question_id = await existing_game.start_question(websocket.app)

                        # Schedule ghost's first answer as a background task.
                        # Subsequent questions are scheduled inside GameService
                        # itself (_resolve_question → _ghost_answer).
                        asyncio.create_task(
                            existing_game._ghost_answer(question_id, websocket.app)
                        )

                # ── HUMAN vs HUMAN ───────────────────────────────────────────
                # No game yet; create it once both sockets are connected.
                elif existing_game is None:
                    connections = room_manager.active_connections.get(match_id, {})
                    if len(connections) == 2:
                        with Session(engine) as db:
                            q = db.query(Match).filter(Match.id == match_id).first()
                            q_ids = q.questions_data

                        p1_id, p2_id = list(connections.keys())
                        game = GameService(match_id, p1_id, p2_id, q_ids)
                        websocket.app.state.active_games[match_id] = game

                        await game.start_question(websocket.app)

            elif event == WSEvents.SUBMIT_ANSWER:
                answer = data.get("answer")
                timestamp = asyncio.get_event_loop().time()

                game: GameService = websocket.app.state.active_games[match_id]
                await game.handle_answer(player_id, answer, timestamp, websocket.app)

    except WebSocketDisconnect:
        room_manager.disconnect(match_id, player_id)


@router.websocket("/ws/lobby/{player_id}")
async def lobby_websocket(websocket: WebSocket, player_id: int):
    await websocket.accept()

    global_manager = websocket.app.state.global_manager
    await global_manager.connect_player(player_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        global_manager.disconnect_player(player_id)