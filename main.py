# main.py

import uvicorn
from fastapi import FastAPI
from app.routers import board_router, user_router

app = FastAPI()

# Include routers
app.include_router(board_router.router, prefix="/boards", tags=["boards"])
app.include_router(user_router.router, prefix="/users", tags=["users"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
