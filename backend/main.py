from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import players

app = FastAPI()

app.include_router(players.router)

# Allow requests from your front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with specific origins like ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "API is up and running"}