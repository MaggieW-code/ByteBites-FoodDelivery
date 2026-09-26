from fastapi import FastAPI

from backend.app.routes.health import router as health_router
from backend.app.routes.restaurant_routes import router as restaurant_router

app = FastAPI(
    title="Food Delivery API", 
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(restaurant_router)
