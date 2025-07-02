# # main.py
# from fastapi import FastAPI
# from app.api.routes import router as api_router

# app = FastAPI(title="Market Data Service")

# app.include_router(api_router)

import uvicorn
from app.api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
