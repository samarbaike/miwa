from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.routes import auth, user,  matches, ws
from app.database import engine, Base
from app.room_manager import RoomManager
from app.global_manager import GlobalManager
from app.services.matchmaking_service import MatchmakingPool
from app.services.run_mm_service import run_matchmaking

print("INFO:     Connecting to Supabase...")
Base.metadata.create_all(bind=engine)
print("INFO:     Tables created successfully!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = MatchmakingPool()
    app.state.room_manager = RoomManager()
    app.state.global_manager = GlobalManager()
    app.state.active_games = {}

    task = asyncio.create_task(run_matchmaking(app))
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