from fastapi import FastAPI
from app.routes import auth
from app.database import engine, Base

from app.models.user import Player
from app.models.session import SessionTable

print("INFO:     Connecting to Supabase...")
Base.metadata.create_all(bind=engine)
print("INFO:     Tables created successfully!")

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
async def root():
    return "Quiz App is sprinting"

@app.get("/health")
async def health():
    return "health is ok"