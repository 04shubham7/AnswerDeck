# AnswerDeck

**AnswerDeck** is a production-ready RAG (Retrieval-Augmented Generation) application that combines semantic search with AI-powered chat.

## Quick Links

- 📖 [Full Documentation](./README.md)
- 🔌 [API Reference](./docs/API.md)
- 👨‍💻 [Developer Guide](./docs/DEVELOPER.md)
- 🏗️ [Architecture](./docs/ARCHITECTURE.md)
- 🚀 [Deployment Guide](./docs/DEPLOYMENT.md)
- 🤝 [Contributing](./CONTRIBUTING.md)

## Features

✨ **Semantic Search** | 🤖 **AI Chat** | ⚡ **Fast & Scalable** | 🎨 **Beautiful UI** | 🔒 **Production Ready** | 📦 **Containerized**

## Tech Stack

### Backend
- FastAPI + Uvicorn
- LangChain + Google Gemini
- Qdrant Vector Database
- pytest for testing

### Frontend
- React 18 + TypeScript
- CSS3 + Responsive Design
- Fetch API

### Infrastructure
- Docker & Docker Compose
- GitHub Actions CI/CD
- Nginx Reverse Proxy

## Getting Started

```bash
# Clone repository
git clone https://github.com/04shubham7/AnswerDeck.git
cd AnswerDeck

# Setup environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Start with Docker Compose
docker-compose up

# Or develop locally
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Access:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Project Structure

```
.
├── src/                   # Backend source
│   ├── api/              # FastAPI application
│   ├── core/rag/         # RAG services
│   └── pipelines/        # Data pipelines
├── frontend/             # React application
├── tests/                # Test suite
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
└── docker-compose*.yml   # Container setup
```

## API Endpoints

```bash
# Chat with context
POST /api/v1/chat/
{"content": "Your question here", "k": 3}

# Search documents
GET /api/v1/chat/search?q=query&k=5

# Health check
GET /api/v1/health
```

## Testing

```bash
# Backend tests
pytest tests/ -v --cov=src

# Frontend tests
cd frontend && npm test
```

## Deployment

**Development:**
```bash
docker-compose up
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

See [Deployment Guide](./docs/DEPLOYMENT.md) for detailed instructions.

## CI/CD

Automated workflows for:
- Backend linting, testing, building
- Frontend building and validation
- Docker image building and pushing
- E2E testing

## Documentation

- **[API Documentation](./docs/API.md)** - Complete endpoint reference
- **[Developer Guide](./docs/DEVELOPER.md)** - Setup and development
- **[Architecture](./docs/ARCHITECTURE.md)** - System design
- **[Deployment](./docs/DEPLOYMENT.md)** - Production deployment
- **[Contributing](./CONTRIBUTING.md)** - How to contribute

## Key Features

- 🔍 Semantic search over documents
- 🤖 AI-powered responses with context
- 📚 Easy document indexing
- 🚀 Production-ready with monitoring
- 🧪 Comprehensive test coverage
- 📖 Full API documentation
- 🔄 Automated CI/CD pipelines
- 🐳 Docker containerization

## Roadmap

- [ ] User authentication
- [ ] Chat history persistence
- [ ] Multi-document indexing
- [ ] Custom embeddings models
- [ ] GraphQL API
- [ ] Mobile application
- [ ] Advanced analytics
- [ ] WebSocket streaming

## Support

- 📖 [Documentation](./docs)
- 🐛 [GitHub Issues](https://github.com/04shubham7/AnswerDeck/issues)
- 💬 [Discussions](https://github.com/04shubham7/AnswerDeck/discussions)

## License

MIT License - See LICENSE file for details

## Contributors

Built with ❤️ for better document understanding

---

**[Full README](./README.md)** | **[Get Started](#getting-started)** | **[Documentation](./docs)**
