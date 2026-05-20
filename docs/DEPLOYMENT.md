# AnswerDeck Deployment Guide

## Production Deployment

### Prerequisites
- Docker and Docker Compose
- SSL certificates
- Environment variables configured
- Google API Key
- Qdrant instance (managed or self-hosted)

### Environment Setup

1. **Create `.env.production`**

```bash
# Environment
ENVIRONMENT=production
NODE_ENV=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Vector Database
QDRANT_URL=https://your-qdrant-instance.com:6333
QDRANT_API_KEY=your_qdrant_api_key

# Google API
GOOGLE_API_KEY=your_google_api_key

# Security
ALLOWED_ORIGINS=https://answerdeck.com,https://www.answerdeck.com
RATE_LIMIT_PER_MINUTE=100

# Frontend
REACT_APP_API_URL=https://api.answerdeck.com/api/v1

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/answerdeck/app.log

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

### Deployment Steps

1. **Build Images**

```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Start Services**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Verify Services**

```bash
# Check containers
docker-compose -f docker-compose.prod.yml ps

# Check backend
curl https://api.answerdeck.com/api/v1/health

# Check frontend
curl https://answerdeck.com
```

### SSL/TLS Setup

1. **Generate self-signed certificates (development)**

```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem
```

2. **Use Let's Encrypt (production)**

```bash
certbot certonly --standalone -d answerdeck.com -d www.answerdeck.com
```

### Database Configuration

#### Option 1: Managed Qdrant (Recommended)

```bash
# Use Qdrant Cloud
QDRANT_URL=https://your-instance-id.eu-west-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_api_key
```

#### Option 2: Self-hosted Qdrant

See `docker-compose.prod.yml` for Qdrant service configuration.

### Monitoring and Logging

#### Application Logs

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Check specific container
docker logs answerdeck-backend
```

#### Metrics Collection

The application exposes Prometheus metrics at `/metrics` (port 9090).

### Backups

1. **Qdrant Data**

```bash
# Backup collection
docker exec answerdeck-qdrant qdrant-backup \
  http://localhost:6333 \
  --backup-dir /backups

# Copy to host
docker cp answerdeck-qdrant:/backups ./qdrant-backup
```

2. **Redis Cache**

```bash
# Redis persistence is enabled in docker-compose
docker exec answerdeck-redis redis-cli BGSAVE
```

### Scaling

#### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
    # ...
```

#### Load Balancing

Use Nginx or your infrastructure provider's load balancer.

### Security

1. **API Rate Limiting**

Configured in environment:
```bash
RATE_LIMIT_PER_MINUTE=100
```

2. **CORS Configuration**

Set allowed origins:
```bash
ALLOWED_ORIGINS=https://yourdomain.com
```

3. **Secret Management**

- Store secrets in environment variables
- Use secrets management tool (AWS Secrets Manager, etc.)
- Never commit secrets to repository

### Updates

1. **Pull latest changes**

```bash
git pull origin master
```

2. **Rebuild images**

```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

3. **Restart services**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Rollback

If issues occur:

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout <previous-commit>

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't connect to Qdrant | Check QDRANT_URL and API key |
| Frontend can't reach API | Check ALLOWED_ORIGINS and CORS config |
| SSL certificate errors | Renew certificates with certbot |
| High memory usage | Check container limits and optimize queries |
| Slow responses | Check Qdrant performance and network latency |

### Performance Tuning

1. **Backend**

```bash
# Increase worker count
export WORKERS=4
```

2. **Qdrant**

```bash
# Adjust search parameters in config
READ_CONSISTENCY_FACTOR=1
```

3. **Redis**

```bash
# Configure memory policy
maxmemory-policy allkeys-lru
```

## Kubernetes Deployment (Advanced)

For production Kubernetes deployment:

```bash
kubectl apply -f k8s/
```

See `k8s/` directory for Kubernetes manifests.

## Monitoring Stack

### Prometheus

Collects metrics from `/metrics` endpoint.

### Grafana

Visualizes metrics and performance.

### ELK Stack (Optional)

Centralized logging with Elasticsearch, Logstash, Kibana.

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Verify configuration: Check `.env.production`
- Test endpoints: Use curl or Postman
- Check GitHub issues for similar problems
