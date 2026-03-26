from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return "Quiz App is sprinting"

@app.get("/health")
def health():
    return "health is ok"