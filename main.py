from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.health import router as health_router
from backend.app.routes.restaurant_routes import router as restaurant_router

app = FastAPI(
    title="Food Delivery API", 
    version="0.1.0"
)

# Add CORS permisions 
# https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1234", "http://127.0.0.1:1234"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(restaurant_router)
