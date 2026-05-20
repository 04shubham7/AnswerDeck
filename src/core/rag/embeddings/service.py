"""Embeddings service for generating vector representations."""

import logging
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class EmbeddingsService:
    """Service for generating and managing embeddings."""
    
    def __init__(self):
        """Initialize embeddings service."""
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")
        
        self.model = GoogleGenerativeAIEmbeddings(
            model=config.GOOGLE_EMBEDDING_MODEL
        )
        logger.info(f"Initialized embeddings with model: {config.GOOGLE_EMBEDDING_MODEL}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.model.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.model.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            raise


# Singleton instance
_embeddings_service = None


def get_embeddings_service() -> EmbeddingsService:
    """Get or create embeddings service."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
