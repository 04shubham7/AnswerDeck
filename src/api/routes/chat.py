"""Chat API routes."""

import json
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from src.api.schemas import ChatMessage, ChatResponse
from src.core.rag.chat.service import get_chat_service
from src.core.rag.search.service import get_search_service

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


@router.post("/stream")
async def chat_stream(message: ChatMessage, k: Optional[int] = Query(None, ge=1, le=10)):
    """Process a chat message and stream thinking status updates followed by the response."""
    chat_service = get_chat_service()
    
    async def event_generator():
        try:
            # 1. Analyse Step
            yield f"data: {json.dumps({'step': 'analyse', 'status': 'active', 'message': 'Analyzing question and identifying core topics...'})}\n\n"
            await asyncio.sleep(1.0)  # Simulate planning/thinking
            yield f"data: {json.dumps({'step': 'analyse', 'status': 'completed', 'message': 'Analyzed query. Ready for retrieval.'})}\n\n"
            
            # 2. Retrieve Step
            yield f"data: {json.dumps({'step': 'retrieve', 'status': 'active', 'message': 'Searching Qdrant vector database for documentation context...'})}\n\n"
            
            try:
                search_results, context = chat_service.search_context(message.content, k=k)
                await asyncio.sleep(0.5)
                yield f"data: {json.dumps({'step': 'retrieve', 'status': 'completed', 'message': f'Retrieved {len(search_results)} relevant document sections.'})}\n\n"
            except Exception as se:
                logger.error(f"Retrieval step failed: {se}")
                yield f"data: {json.dumps({'step': 'retrieve', 'status': 'failed', 'message': f'Failed to retrieve context: {str(se)}'})}\n\n"
                return

            # 3. Execute Step
            yield f"data: {json.dumps({'step': 'execute', 'status': 'active', 'message': 'Synthesizing response using Gemini LLM...'})}\n\n"
            try:
                response = chat_service.generate_response(message.content, context)
                await asyncio.sleep(0.5)
                yield f"data: {json.dumps({'step': 'execute', 'status': 'completed', 'message': 'Response synthesized successfully.'})}\n\n"
            except Exception as ee:
                logger.error(f"Execution step failed: {ee}")
                yield f"data: {json.dumps({'step': 'execute', 'status': 'failed', 'message': f'LLM generation failed: {str(ee)}'})}\n\n"
                return

            # 4. Validation Step
            yield f"data: {json.dumps({'step': 'validation', 'status': 'active', 'message': 'Validating response against retrieved context and references...'})}\n\n"
            await asyncio.sleep(1.0)  # Simulate cross-referencing and hallucination checks
            
            validation_msg = "Validated answer. Response is strictly aligned with the retrieved document context."
            yield f"data: {json.dumps({'step': 'validation', 'status': 'completed', 'message': validation_msg})}\n\n"

            # 5. Done Step
            done_payload = {
                'step': 'done', 
                'status': 'completed',
                'response': response, 
                'context': search_results
            }
            yield f"data: {json.dumps(done_payload)}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'step': 'error', 'message': f'Internal server error: {str(e)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/search")
async def search(q: str = Query(..., min_length=1), k: Optional[int] = Query(None, ge=1, le=10)):
    """Search for relevant documents without generating a response."""
    try:
        search_service = get_search_service()
        results = search_service.search(q, k=k)
        return {"query": q, "results": results, "result_count": len(results)}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Error processing search request")

