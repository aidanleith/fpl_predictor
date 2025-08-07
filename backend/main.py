from fastapi import FastAPI
from backend.app.routes import players

app = FastAPI()

app.include_router(players.router)

@app.get("/")
def read_root():
    return {"message": "API is up and running"}