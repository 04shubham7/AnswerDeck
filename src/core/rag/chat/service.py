"""Chat service for RAG-based conversations."""

import logging
from typing import List, Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.config import get_config
from src.core.rag.search.service import get_search_service

logger = logging.getLogger(__name__)
config = get_config()


class ChatService:
    """Service for RAG-based chat interactions."""
    
    def __init__(self):
        """Initialize chat service with Google Generative AI."""
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")
        
        self.llm = ChatGoogleGenerativeAI(model=config.GOOGLE_CHAT_MODEL)
        self.search_service = get_search_service()
        logger.info(f"Initialized chat service with model: {config.GOOGLE_CHAT_MODEL}")
    
    def search_context(self, query: str, k: int = None) -> Tuple[List[Dict], str]:
        """Search for relevant context based on query."""
        search_results = self.search_service.search(query, k=k)
        context = "\n\n\n".join(
            [
                f"Page Content: {result['content']}\nPage Number: {result['page']}\nFile Location: {result['source']}"
                for result in search_results
            ]
        )
        return search_results, context
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response based on query and context."""
        try:
            system_prompt = f"""You are a helpful AI assistant. Use the provided context to answer questions accurately.
            
Context:
{context}

If the context doesn't contain relevant information, say so clearly."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def chat(self, query: str, k: int = None) -> Dict[str, Any]:
        """Complete chat interaction: search context and generate response."""
        try:
            search_results, context = self.search_context(query, k=k)
            response = self.generate_response(query, context)
            
            return {
                "query": query,
                "response": response,
                "context": search_results,
                "context_count": len(search_results)
            }
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise


# Singleton instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create chat service."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
