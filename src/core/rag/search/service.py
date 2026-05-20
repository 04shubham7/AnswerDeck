"""Vector search service for semantic document retrieval."""

import logging
from typing import List, Dict, Any
from langchain_qdrant import QdrantVectorStore
from src.config import get_config
from src.core.rag.embeddings.service import get_embeddings_service

logger = logging.getLogger(__name__)
config = get_config()


class SearchService:
    """Service for vector-based semantic search."""
    
    def __init__(self):
        """Initialize search service with Qdrant vector store."""
        embeddings_service = get_embeddings_service()
        self.vector_store = QdrantVectorStore.from_existing_collection(
            url=config.QDRANT_URL,
            collection_name=config.QDRANT_COLLECTION_NAME,
            embedding=embeddings_service.model,
        )
        logger.info(f"Initialized search service with collection: {config.QDRANT_COLLECTION_NAME}")
    
    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query."""
        if k is None:
            k = config.SEARCH_RESULTS_K
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            search_results = [
                {
                    "content": result.page_content,
                    "metadata": result.metadata,
                    "page": result.metadata.get("page_label", "N/A"),
                    "source": result.metadata.get("source", "N/A")
                }
                for result in results
            ]
            logger.info(f"Search query returned {len(search_results)} results")
            return search_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise


# Singleton instance
_search_service = None


def get_search_service() -> SearchService:
    """Get or create search service."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
