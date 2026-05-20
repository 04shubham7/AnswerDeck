# AnswerDeck - RAG-Powered Semantic Chat

[![Backend CI](https://github.com/04shubham7/AnswerDeck/workflows/Backend%20CI%20Pipeline/badge.svg)](https://github.com/04shubham7/AnswerDeck/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/04shubham7/AnswerDeck/workflows/Frontend%20CI%20Pipeline/badge.svg)](https://github.com/04shubham7/AnswerDeck/actions/workflows/frontend-ci.yml)
[![codecov](https://codecov.io/gh/04shubham7/AnswerDeck/branch/master/graph/badge.svg)](https://codecov.io/gh/04shubham7/AnswerDeck)

AnswerDeck is a full-stack Retrieval-Augmented Generation (RAG) application that combines semantic search with AI-powered chat to answer questions based on document context.

## Features

🔍 **Semantic Search** - Find relevant content using vector embeddings  
💬 **AI Chat** - Get intelligent responses augmented with retrieved context  
⚡ **Fast & Scalable** - Built with modern async frameworks  
🎨 **Beautiful UI** - Responsive React frontend with real-time updates  
🔒 **Production Ready** - Comprehensive testing, error handling, and monitoring  
📦 **Containerized** - Easy deployment with Docker and Docker Compose  

## Tech Stack

### Backend
- **Framework**: FastAPI + Uvicorn
- **Vector DB**: Qdrant
- **LLM**: Google Generative AI (Gemini)
- **RAG**: LangChain
- **Testing**: pytest

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: CSS3 + Responsive Design
- **API**: Fetch API

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Code Quality**: pylint, flake8, black, mypy

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Google API Key (for Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/04shubham7/AnswerDeck.git
   cd AnswerDeck
   ```

2. **Setup backend**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/api/docs
   - Backend: http://localhost:8000

## Development

### Running Backend

```bash
# Start API server
python main.py

# Or using CLI
python cli.py serve --host 0.0.0.0 --port 8000

# Start Qdrant vector DB (required)
docker run -d -p 6333:6333 qdrant/qdrant
```

### Running Frontend

```bash
cd frontend
npm start
```

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
flake8 src tests
pylint src

# Type check
mypy src
```

## Project Structure

```
.
├── src/                          # Backend source code
│   ├── api/                      # FastAPI application
│   │   ├── routes/              # API endpoints
│   │   ├── schemas/             # Pydantic models
│   │   └── server.py            # FastAPI app factory
│   ├── core/                     # RAG core logic
│   │   └── rag/
│   │       ├── embeddings/      # Vector embeddings
│   │       ├── search/          # Semantic search
│   │       └── chat/            # Chat generation
│   ├── pipelines/               # Data processing
│   │   └── indexing/            # Document indexing
│   ├── config.py                # Configuration
│   └── logger.py                # Logging setup
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── App.tsx              # Main app
│   │   └── index.css            # Styles
│   └── package.json
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── conftest.py              # Pytest configuration
├── .github/workflows/            # CI/CD pipelines
├── docker-compose.yml           # Local development setup
├── Dockerfile.backend           # Backend container
├── requirements.txt             # Python dependencies
└── main.py                      # Backend entry point
```

## API Documentation

### Chat Endpoint

**POST** `/api/v1/chat/`

Request:
```json
{
  "content": "What is the documentation about?"
}
```

Response:
```json
{
  "query": "What is the documentation about?",
  "response": "The documentation covers...",
  "context_count": 3,
  "context": [
    {
      "content": "...",
      "page": 1,
      "source": "document.pdf",
      "metadata": {}
    }
  ]
}
```

### Search Endpoint

**GET** `/api/v1/chat/search?q=query&k=5`

Retrieve relevant documents without generating a response.

### Health Check

**GET** `/api/v1/health`

Check API status.

## Indexing Documents

### Using CLI

```bash
# Index a PDF document
python cli.py index path/to/document.pdf

# Force recreate collection
python cli.py index path/to/document.pdf --force-recreate
```

### Using Python API

```python
from src.pipelines.indexing.processor import IndexingPipeline

pipeline = IndexingPipeline()
documents = pipeline.load_pdf("path/to/document.pdf")
pipeline.index_documents(documents)
```

## Configuration

Create a `.env` file with:

```bash
# Environment
ENVIRONMENT=development

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=learning_vectors

# Google Generative AI
GOOGLE_API_KEY=your_api_key_here

# Document Processing
PDF_CHUNK_SIZE=3000
PDF_CHUNK_OVERLAP=200

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Deployment

### Docker Compose (Local)

```bash
docker-compose up -d
```

### Docker (Production)

Build images:
```bash
docker build -f Dockerfile.backend -t answerdeck-backend .
docker build -f frontend/Dockerfile -t answerdeck-frontend ./frontend
```

Run containers:
```bash
docker run -d -p 8000:8000 \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e QDRANT_URL=http://qdrant:6333 \
  answerdeck-backend

docker run -d -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api:8000/api/v1 \
  answerdeck-frontend
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Testing

We maintain high test coverage:
- Unit tests for core components
- Integration tests for API endpoints
- E2E tests for complete workflows

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Troubleshooting

### API Connection Issues

```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Check if backend is running
curl http://localhost:8000/api/v1/health
```

### Google API Key

1. Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env` file
3. Ensure key has access to Gemini APIs

## Performance

- **Semantic Search**: <100ms for typical queries
- **Response Generation**: 1-3s depending on context
- **Vector Indexing**: ~10 documents per minute

## Security Considerations

- API uses CORS (configure in production)
- Input validation on all endpoints
- Environment variables for sensitive data
- No secrets in version control

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- 📧 Email: support@answerdeck.com
- 🐛 [GitHub Issues](https://github.com/04shubham7/AnswerDeck/issues)
- 📚 [Documentation](https://docs.answerdeck.com)

## Roadmap

- [ ] Multi-document indexing
- [ ] User authentication
- [ ] Chat history persistence
- [ ] Custom embeddings models
- [ ] Web UI improvements
- [ ] GraphQL API
- [ ] Kubernetes deployment

---

**Built with ❤️ for better document understanding**
