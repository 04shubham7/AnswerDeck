# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│              Chat UI + Message Management                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Server                              │
│         ┌─────────────────────────────────┐                 │
│         │   API Routes                    │                 │
│         │ • /chat          • /search      │                 │
│         │ • /health        • /status      │                 │
│         └─────────────────┬───────────────┘                 │
│         ┌─────────────────▼───────────────┐                 │
│         │   RAG Services                  │                 │
│         │ • ChatService                   │                 │
│         │ • SearchService                 │                 │
│         │ • EmbeddingsService             │                 │
│         └─────────────────┬───────────────┘                 │
│         ┌─────────────────▼───────────────┐                 │
│         │   Data Pipelines                │                 │
│         │ • IndexingPipeline              │                 │
│         │ • Processing                    │                 │
│         └─────────────────┬───────────────┘                 │
└────────────────────────┬─────────────────────────────────────┘
         │                │
    gRPC │                │ Vector Protocol
         │                │
    ┌────▼────┐      ┌────▼──────────┐
    │ Qdrant  │      │ Google Gemini │
    │Vector DB│      │   LLM API     │
    └─────────┘      └───────────────┘
```

## Component Architecture

### 1. Frontend Layer

**React Components:**
- `ChatInterface`: Main chat container
- `MessageList`: Display messages
- `ChatInput`: User input form
- `ContextPanel`: Show retrieved documents
- `Message`: Individual message component

**State Management:**
- Messages state
- Context state
- Loading state
- Error state

### 2. API Layer

**FastAPI Application:**
```
src/api/
├── routes/
│   ├── chat.py          # Chat endpoints
│   └── health.py        # Health check endpoints
├── schemas/
│   └── __init__.py      # Pydantic models
└── server.py            # FastAPI app factory
```

**Key Endpoints:**
- `POST /api/v1/chat/` - Send message
- `GET /api/v1/chat/search` - Search documents
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Status info

### 3. Core RAG Layer

**Services:**

```
src/core/rag/
├── embeddings/
│   └── service.py       # Vector embeddings
├── search/
│   └── service.py       # Semantic search
└── chat/
    └── service.py       # Chat generation
```

**EmbeddingsService:**
- Generates vector representations
- Uses Google Gemini embeddings
- Singleton pattern for efficiency

**SearchService:**
- Queries Qdrant vector database
- Returns relevant documents
- Configurable result count

**ChatService:**
- Combines search and generation
- Uses Google Gemini LLM
- Returns augmented responses

### 4. Pipeline Layer

```
src/pipelines/
└── indexing/
    └── processor.py     # Document processing
```

**IndexingPipeline:**
- Loads PDF documents
- Splits into chunks
- Generates embeddings
- Stores in Qdrant

## Data Flow

### Chat Flow

```
1. User sends message
   ↓
2. Frontend sends HTTP POST to /api/v1/chat/
   ↓
3. Backend receives request
   ↓
4. ChatService.chat() is called
   ↓
5. SearchService searches for context
   ↓
6. Qdrant returns relevant documents
   ↓
7. Context is formatted
   ↓
8. LLM generates response
   ↓
9. Response sent back to frontend
   ↓
10. Frontend displays message and context
```

### Indexing Flow

```
1. PDF file uploaded/selected
   ↓
2. IndexingPipeline.load_pdf()
   ↓
3. Text splitter chunks document
   ↓
4. EmbeddingsService generates vectors
   ↓
5. Vectors stored in Qdrant
   ↓
6. Indexed documents ready for search
```

## Technology Decisions

### Why FastAPI?
- Modern, fast, async/await support
- Automatic API documentation (Swagger/OpenAPI)
- Type hints for validation
- Built-in dependency injection

### Why Qdrant?
- Open-source vector database
- Easy deployment (Docker, cloud)
- Good Python integration
- Excellent query performance

### Why Google Gemini?
- State-of-the-art embeddings and LLM
- Good cost/performance ratio
- Easy integration via LangChain

### Why React?
- Component-based architecture
- Large ecosystem
- Good TypeScript support
- Responsive UI patterns

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers
- Load balancer in front
- Shared Qdrant instance
- Distributed embeddings cache

### Vertical Scaling
- Async processing
- Connection pooling
- Batch indexing
- Query optimization

## Security Architecture

### API Security
- Input validation (Pydantic)
- Rate limiting (future)
- CORS configuration
- Error masking

### Data Security
- .env for secrets
- No hardcoded credentials
- Environment-based config
- Secure API communication

## Testing Strategy

### Unit Tests
- Service layer tests
- Business logic tests
- Mock external dependencies

### Integration Tests
- API endpoint tests
- Full flow tests
- Database integration

### E2E Tests
- Complete user workflows
- Frontend + Backend
- Real services (if applicable)

## Deployment Architecture

### Development
- Local containers
- Docker Compose
- Hot reload enabled

### Production
- Kubernetes/Container Orchestration
- Managed Qdrant (Qdrant Cloud)
- CDN for frontend
- Monitoring and logging

## Future Improvements

1. **Caching Layer**
   - Redis for response caching
   - Embedding cache

2. **Async Processing**
   - Celery for background jobs
   - Message queue (RabbitMQ/Redis)

3. **Database Enhancements**
   - SQL for metadata
   - Read replicas

4. **Monitoring**
   - Prometheus metrics
   - ELK stack for logs
   - APM integration

5. **Advanced RAG**
   - Multiple LLM support
   - Custom embeddings
   - Multi-step reasoning
