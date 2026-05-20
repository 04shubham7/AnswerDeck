"""Configuration management for AnswerDeck application."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)


class Config:
    """Base configuration."""
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_TITLE = "AnswerDeck RAG API"
    API_VERSION = "0.1.0"
    
    # Vector DB Configuration
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "learning_vectors")
    
    # Google GenAI Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_EMBEDDING_MODEL = "models/gemini-embedding-001"
    GOOGLE_CHAT_MODEL = "gemini-pro"
    
    # Document Processing
    PDF_CHUNK_SIZE = int(os.getenv("PDF_CHUNK_SIZE", 3000))
    PDF_CHUNK_OVERLAP = int(os.getenv("PDF_CHUNK_OVERLAP", 200))
    PDF_BATCH_SIZE = int(os.getenv("PDF_BATCH_SIZE", 10))
    PDF_BATCH_SLEEP_SECONDS = int(os.getenv("PDF_BATCH_SLEEP_SECONDS", 60))
    
    # Search Configuration
    SEARCH_RESULTS_K = int(os.getenv("SEARCH_RESULTS_K", 3))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "INFO"


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
