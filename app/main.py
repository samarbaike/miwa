from fastapi import FastAPI
from app.routes import auth

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
async def root():
    return "Quiz App is sprinting"

@app.get("/health")
async def health():
    return "health is ok"