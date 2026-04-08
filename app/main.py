from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.routes import auth, user,  matches, ws
from app.database import engine, Base
from app.models.user import Player
from app.models.session import SessionTable
from app.services.matchmaking_service import MatchmakingPool, miwa_pool

print("INFO:     Connecting to Supabase...")
Base.metadata.create_all(bind=engine)
print("INFO:     Tables created successfully!")


async def run_matchmaking():
    while True:
        miwa_pool.tick()
        while True:
            match = miwa_pool.try_pair()
            if match is None:
                break
            print(f"Match found in background: {match[0].player.username} and {match[1].player.username}")
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(run_matchmaking())
    yield

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