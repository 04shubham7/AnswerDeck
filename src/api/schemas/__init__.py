"""API schemas and models."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message model."""
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")


class ChatResponse(BaseModel):
    """Chat response model."""
    query: str = Field(..., description="Original user query")
    response: str = Field(..., description="Generated response")
    context_count: int = Field(..., description="Number of context documents retrieved")
    context: List[Dict[str, Any]] = Field(..., description="Retrieved context documents")


class DocumentUpload(BaseModel):
    """Document upload model."""
    filename: str = Field(..., min_length=1, description="Document filename")
    file_path: str = Field(..., description="Path to uploaded file")


class IndexingStatus(BaseModel):
    """Indexing status model."""
    status: str = Field(..., description="Current status (pending, processing, completed, failed)")
    documents_processed: int = Field(0, description="Number of documents processed")
    documents_total: int = Field(0, description="Total documents to process")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
