# AnswerDeck API Documentation

## Overview

AnswerDeck provides a RESTful API for semantic search and AI-powered chat over documents.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses a simple key-based approach. No authentication required for local development.

For production, configure API keys in `.env`:
```bash
API_KEY=your_key_here
```

## Endpoints

### Chat

#### POST /chat/

Send a message and get a response with retrieved context.

**Parameters:**
- `content` (string, required): The user message (1-5000 characters)
- `k` (integer, optional): Number of context documents to retrieve (1-10, default: 3)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is Node.js?",
    "k": 3
  }'
```

**Example Response:**
```json
{
  "query": "What is Node.js?",
  "response": "Node.js is a JavaScript runtime built on Chrome's V8 engine...",
  "context_count": 3,
  "context": [
    {
      "content": "Node.js is an open-source, cross-platform JavaScript runtime environment...",
      "metadata": {},
      "page": 1,
      "source": "nodejs.pdf"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Successful response
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Server error

### Search

#### GET /chat/search

Perform semantic search without generating a response.

**Parameters:**
- `q` (string, required): Search query
- `k` (integer, optional): Number of results (1-10, default: 3)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/chat/search?q=modules&k=5"
```

**Example Response:**
```json
{
  "query": "modules",
  "result_count": 5,
  "results": [
    {
      "content": "Node.js has a set of built-in modules...",
      "metadata": {},
      "page": 2,
      "source": "nodejs.pdf"
    }
  ]
}
```

### Health Check

#### GET /health

Check API status.

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Status

#### GET /status

Get application status and configuration.

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/status"
```

**Example Response:**
```json
{
  "api_version": "0.1.0",
  "qdrant_url": "http://localhost:6333",
  "collection_name": "learning_vectors",
  "debug": true,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Error Handling

All errors return a structured response:

```json
{
  "detail": "Error description here"
}
```

### Common Errors

| Status | Error | Solution |
|--------|-------|----------|
| 400 | Invalid request | Check request parameters |
| 404 | Endpoint not found | Verify endpoint URL |
| 500 | Server error | Check backend logs |
| 503 | Service unavailable | Ensure dependencies are running |

## Rate Limiting

For production deployments, implement rate limiting:
- Frontend requests: 100 req/min per IP
- Backend processing: 10 concurrent

## Pagination

Search results support pagination via `k` parameter. Maximum 10 results per request.

## Response Headers

All responses include:
```
Content-Type: application/json
Access-Control-Allow-Origin: *
```

## SDK Integration

### Python

```python
import requests

api_url = "http://localhost:8000/api/v1"

response = requests.post(
    f"{api_url}/chat/",
    json={"content": "What is Node.js?", "k": 3}
)

result = response.json()
print(result["response"])
```

### JavaScript

```javascript
const apiUrl = "http://localhost:8000/api/v1";

const response = await fetch(`${apiUrl}/chat/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ content: "What is Node.js?", k: 3 })
});

const result = await response.json();
console.log(result.response);
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is Node.js?"}'
```

## WebSocket Support (Future)

Planned for real-time streaming responses.

## Versioning

Current API version: `v1`

Future versions will maintain backward compatibility.

## Support

For API support:
- Check [GitHub Issues](https://github.com/04shubham7/AnswerDeck/issues)
- Read [Contributing Guide](CONTRIBUTING.md)
