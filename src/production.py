"""Production configuration for AnswerDeck."""

from pydantic import Field
from src.config import Config
import os


class ProductionSettings(Config):
    """Production environment settings."""
    
    # Security
    DEBUG = False
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Database
    QDRANT_URL = os.getenv("QDRANT_URL")  # Must be set
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # API Security
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS", 
        "https://yourdomain.com"
    ).split(",")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 100))
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/answerdeck/app.log"
    
    # Monitoring
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", 9090))
