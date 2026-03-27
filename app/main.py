from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return "Quiz App is sprinting"

@app.get("/health")
async def health():
    return "health is ok"