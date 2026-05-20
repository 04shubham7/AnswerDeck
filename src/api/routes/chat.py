"""Chat API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from src.api.schemas import ChatMessage, ChatResponse
from src.core.rag.chat.service import get_chat_service

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage, k: Optional[int] = Query(None, ge=1, le=10)):
    """Process a chat message and return response with context."""
    try:
        chat_service = get_chat_service()
        result = chat_service.chat(message.content, k=k)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat request")


@router.get("/search")
async def search(q: str = Query(..., min_length=1), k: Optional[int] = Query(None, ge=1, le=10)):
    """Search for relevant documents without generating a response."""
    try:
        from src.core.rag.search.service import get_search_service
        search_service = get_search_service()
        results = search_service.search(q, k=k)
        return {"query": q, "results": results, "result_count": len(results)}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Error processing search request")
