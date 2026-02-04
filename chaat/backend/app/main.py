from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.utils.middleware import RequestLoggingMiddleware

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

# CORS for frontend (local dev) + GitHub Pages hosting later
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router)
