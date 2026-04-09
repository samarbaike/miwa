from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.routes import auth, user,  matches, ws
from app.database import engine, Base
from app.room_manager import RoomManager
from app.global_manager import GlobalManager
from app.services.matchmaking_service import MatchmakingPool

print("INFO:     Connecting to Supabase...")
Base.metadata.create_all(bind=engine)
print("INFO:     Tables created successfully!")


async def run_matchmaking(pool: MatchmakingPool):
    while True:
        pool.tick()
        while True:
            match = pool.try_pair()
            if match is None:
                break
            print(f"Match found in background: {match[0].player.username} and {match[1].player.username}")
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = MatchmakingPool()
    app.state.room_manager = RoomManager()
    app.state.global_manager = GlobalManager()
    app.state.active_games = {}

    task = asyncio.create_task(run_matchmaking(app.state.pool))
    yield
    task.cancel()
    
app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(matches.router)
app.include_router(ws.router)
    
@app.get("/")
async def root():
    return "Quiz App is sprinting"

@app.get("/health")
async def health():
    return "health is ok"