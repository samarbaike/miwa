import asyncio
from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.database import engine
from app.models.match import Match, MatchMode, MatchStatus
from app.models.question import MultipleChoice


async def run_matchmaking(app: FastAPI):
    #grabbing managers from app.state
    pool = app.state.pool
    global_manager = app.state.global_manager

    while True:
        pool.tick()
        while True:
            match = pool.try_pair()
            if match is None:
                break

            player1 = match[0].player
            player2 = match[1].player

            print(f"Match found in background: {match[0].player.username} and {match[1].player.username}")

            with Session(engine) as db:
                query = select(MultipleChoice.id).filter(MultipleChoice.category == match[0].category).order_by(func.random()).limit(10)
                q_ids = db.execute(query).scalars().all()
                
                new_match = Match(
                    player1_id = player1.id,
                    player2_id = player2.id,
                    status = MatchStatus.IN_PROGRESS,
                    mode = MatchMode.RANKED,
                    questions_data = q_ids
                )

                db.add(new_match)
                db.commit()
                db.refresh(new_match)

                match_id = new_match.id

            await global_manager.notify_match_found(player1.id, match_id)
            await global_manager.notify_match_found(player2.id, match_id)

        await asyncio.sleep(10)