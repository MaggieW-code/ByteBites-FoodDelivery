from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.auth_routes import router as auth_router
from backend.app.routes.health import router as health_router
from backend.app.routes.menu_routes import router as menu_router
from backend.app.routes.restaurant_routes import router as restaurant_router
from backend.app.validation_errors import request_validation_error_handler

app = FastAPI(title="Food Delivery API", version="0.1.0")

# 422 responses that stay valid JSON even for inputs like 1e999
app.add_exception_handler(RequestValidationError, request_validation_error_handler)

# Add CORS permisions
# https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1234",
        "http://127.0.0.1:1234",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health_router)
app.include_router(restaurant_router)
app.include_router(menu_router)
app.include_router(auth_router)
