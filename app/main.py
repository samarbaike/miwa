from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message" : "Quiz App is sprinting"}

@app.get("/health")
def health():
    return {"status" : "ok"}