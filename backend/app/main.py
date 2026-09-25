from pathlib import Path

from fastapi import FastAPI

from backend.app.routes.restaurant_routes import router as restaurant_router

app = FastAPI(
    title="Food Delivery API", 
    version="0.1.0"
)

app.include_router(restaurant_router)