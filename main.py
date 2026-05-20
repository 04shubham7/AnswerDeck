"""Main entry point for FastAPI application."""

import uvicorn
from src.config import get_config
from src.logger import setup_logger

config = get_config()
logger = setup_logger(__name__)


if __name__ == "__main__":
    uvicorn.run(
        "src.api.server:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )
