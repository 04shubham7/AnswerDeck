# Developer Guide

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup environment:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Frontend Setup

1. Navigate to frontend:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Database Setup

Start Qdrant vector database:

```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

## Development Workflow

### Starting Services

**Backend:**
```bash
python main.py
```

**Frontend:**
```bash
cd frontend
npm start
```

**Both (Docker Compose):**
```bash
docker-compose up
```

### Code Style

We use strict code quality standards:

```bash
# Format code
black src tests
isort src tests

# Check style
flake8 src tests
pylint src

# Type checking
mypy src
```

### Testing

Run the test suite:

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_rag_core.py

# With coverage
pytest --cov=src --cov-report=html
```

## Architecture

### Backend Architecture

```
FastAPI Server
    ↓
API Routes (Chat, Health)
    ↓
RAG Services (Chat, Search, Embeddings)
    ↓
Vector DB (Qdrant) + LLM (Google Gemini)
```

### Frontend Architecture

```
React App
    ↓
Components (Chat, Messages, Input)
    ↓
API Client
    ↓
Backend API
```

## Adding Features

### Add Backend Endpoint

1. Create route file in `src/api/routes/`
2. Define request/response schemas in `src/api/schemas/`
3. Implement business logic in `src/core/`
4. Include router in `src/api/server.py`

### Add Frontend Component

1. Create component in `src/components/`
2. Create CSS file alongside
3. Export from component's index
4. Import and use in parent component

### Add Test

1. Create test file in `tests/unit/` or `tests/integration/`
2. Use pytest fixtures from `tests/conftest.py`
3. Follow naming: `test_<feature>.py`
4. Run with `pytest`

## Debugging

### Backend Debugging

Enable debug mode:

```python
from src.logger import setup_logger
logger = setup_logger(__name__)
logger.debug("Debug message")
```

### Frontend Debugging

Use browser DevTools:
- Open DevTools (F12)
- Check Network tab for API calls
- Use Console for errors

## Performance Optimization

### Backend
- Use async/await for I/O operations
- Cache embeddings and search results
- Batch process documents

### Frontend
- Code-split React components
- Lazy load images
- Memoize expensive computations

## Database Operations

### Indexing Documents

```python
from src.pipelines.indexing.processor import IndexingPipeline

pipeline = IndexingPipeline()
docs = pipeline.load_pdf("path/to/pdf")
pipeline.index_documents(docs)
```

### Querying

```python
from src.core.rag.search.service import get_search_service

search = get_search_service()
results = search.search("query", k=5)
```

## Deployment

### Local Development

```bash
docker-compose up
```

### Production

1. Build Docker images
2. Push to container registry
3. Deploy with Kubernetes or VM
4. Configure secrets

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Kill process or use different port |
| Qdrant not responding | Check Docker container, restart |
| API returns 500 | Check logs, verify .env config |
| Frontend can't reach API | Check CORS, API URL configuration |

### Logs

View application logs:

```bash
# Recent logs
tail -f logs/app.log

# Docker logs
docker-compose logs backend
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## Resources

- [API Documentation](API.md)
- [Architecture Docs](ARCHITECTURE.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [LangChain Docs](https://docs.langchain.com/)
