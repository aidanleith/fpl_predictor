import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import players

app = FastAPI()

# Get environment - defaults to production
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Configure CORS based on environment
if ENVIRONMENT == "development":
    # Development - more permissive for local testing
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]
    allow_credentials = True
    allow_methods = ["*"]
    allow_headers = ["*"]
else:
    # Production - get the actual Railway domain from environment
    # Railway automatically sets RAILWAY_PUBLIC_DOMAIN
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    
    if railway_domain:
        allowed_origins = [f"https://{railway_domain}"]
    else:
        
        allowed_origins = ["https://ip.railway.app"]
    
    allow_credentials = False  # More secure
    allow_methods = ["GET", "POST", "OPTIONS"] 
    allow_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(players.router)

@app.get("/api")
def read_root():
    return {"message": "API is up and running"}

@app.get("/")
def serve_frontend():
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)