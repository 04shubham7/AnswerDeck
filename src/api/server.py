"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import __version__
from src.config import get_config
from src.api.routes import chat, health
import logging

logger = logging.getLogger(__name__)
config = get_config()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=config.API_TITLE,
        version=__version__,
        description="AnswerDeck RAG API - Retrieval-Augmented Generation Chat",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(chat.router)
    app.include_router(health.router)
    
    @app.on_event("startup")
    async def startup():
        logger.info(f"Starting {config.API_TITLE} v{__version__}")
        logger.info(f"Environment: {'production' if not config.DEBUG else 'development'}")
    
    @app.on_event("shutdown")
    async def shutdown():
        logger.info(f"Shutting down {config.API_TITLE}")
    
    return app


app = create_app()
