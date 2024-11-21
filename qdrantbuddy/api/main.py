from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import logging
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Enable CORS if needed (you can configure allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router with our post route
app.include_router(router)

# Add some basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    # Start the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
