# ATS System - Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid API keys

### 2. Configuration
- [ ] OpenAI API key configured in `.env`
- [ ] Database URL configured (if using PostgreSQL)
- [ ] Redis configured (for Celery/caching)
- [ ] Log level set appropriately

### 3. Testing
- [ ] Run verification script: `python verify_setup.py`
- [ ] Run example: `python example.py`
- [ ] Run unit tests: `pytest tests/`
- [ ] Test API endpoints locally

## Deployment Options

### Option 1: Local Development

**Best for**: Testing, development, demos

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start API server
python src/api/main.py

# Or with uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Access**: http://localhost:8000

---

### Option 2: Docker Container

**Best for**: Isolated deployment, consistent environments

#### Build Image
```bash
docker build -t ats-system:latest .
```

#### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ats-api \
  ats-system:latest
```

#### Check Logs
```bash
docker logs -f ats-api
```

---

### Option 3: Docker Compose (Full Stack)

**Best for**: Production-like setup with database and Redis

#### Start All Services
```bash
docker-compose up -d
```

#### Services Started
- ATS API (Port 8000)
- PostgreSQL (Port 5432)
- Redis (Port 6379)
- Celery Worker

#### Check Status
```bash
docker-compose ps
```

#### View Logs
```bash
docker-compose logs -f ats-api
```

#### Stop Services
```bash
docker-compose down
```

---

### Option 4: Cloud Deployment

#### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
eb init -p python-3.11 ats-system
```

3. Create environment:
```bash
eb create ats-production
```

4. Deploy:
```bash
eb deploy
```

5. Open app:
```bash
eb open
```

#### AWS ECS (Docker)

1. Build and tag:
```bash
docker build -t ats-system .
docker tag ats-system:latest YOUR_ECR_REPO:latest
```

2. Push to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_REPO
docker push YOUR_ECR_REPO:latest
```

3. Create ECS task definition and service (via AWS Console or CLI)

#### Heroku

1. Install Heroku CLI

2. Create app:
```bash
heroku create ats-system-app
```

3. Add buildpack:
```bash
heroku buildpacks:set heroku/python
```

4. Set config vars:
```bash
heroku config:set OPENAI_API_KEY=your_key_here
```

5. Deploy:
```bash
git push heroku main
```

#### Google Cloud Run

1. Build container:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ats-system
```

2. Deploy:
```bash
gcloud run deploy ats-system \
  --image gcr.io/YOUR_PROJECT/ats-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

1. Create resource group:
```bash
az group create --name ats-rg --location eastus
```

2. Create container:
```bash
az container create \
  --resource-group ats-rg \
  --name ats-system \
  --image YOUR_REGISTRY/ats-system:latest \
  --dns-name-label ats-system \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your_key
```

---

## Environment Variables (Production)

### Required
```env
OPENAI_API_KEY=sk-...
```

### Optional but Recommended
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_HOST=redis-host
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://redis-host:6379/0
CELERY_RESULT_BACKEND=redis://redis-host:6379/0

# Logging
LOG_LEVEL=INFO

# Security (add in production)
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-frontend.com
```

---

## Security Configuration

### 1. API Authentication

Add to `src/api/main.py`:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

# Add to endpoints
@app.post("/evaluate", dependencies=[Depends(verify_token)])
async def evaluate_candidate(...):
    ...
```

### 2. HTTPS

Use reverse proxy (nginx/Caddy) or cloud load balancer for SSL/TLS.

**Example nginx config:**
```nginx
server {
    listen 443 ssl;
    server_name ats-system.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Rate Limiting

Install:
```bash
pip install slowapi
```

Add to `src/api/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/evaluate")
@limiter.limit("10/minute")
async def evaluate_candidate(request: Request, ...):
    ...
```

---

## Database Setup (PostgreSQL)

### 1. Create Database

```sql
CREATE DATABASE ats_db;
CREATE USER ats_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ats_db TO ats_user;
```

### 2. Run Migrations

```bash
alembic upgrade head
```

### 3. Update .env

```env
DATABASE_URL=postgresql://ats_user:secure_password@localhost:5432/ats_db
```

---

## Monitoring & Logging

### 1. Application Logs

Logs are written to `logs/ats.log` by default.

**Production logging config:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/ats.log',
    maxBytes=10000000,
    backupCount=5
)
handler.setLevel(logging.INFO)
logger.addHandler(handler)
```

### 2. Health Check Endpoint

Already implemented at `/health`

**Monitor with:**
```bash
curl http://your-domain.com/health
```

### 3. Monitoring Services

#### Datadog
```bash
pip install ddtrace
ddtrace-run python src/api/main.py
```

#### New Relic
```bash
pip install newrelic
newrelic-admin run-program python src/api/main.py
```

#### Sentry
```bash
pip install sentry-sdk
```

Add to `src/api/main.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Run multiple instances** behind a load balancer
2. **Use Redis** for shared state/caching
3. **Use PostgreSQL** instead of SQLite
4. **Deploy Celery workers** for background processing

### Vertical Scaling

- Increase CPU/memory for API containers
- Use faster LLM models (gpt-4o-mini for speed)
- Implement response caching
- Optimize database queries

### Cost Optimization

1. **Use gpt-4o-mini** instead of gpt-4 (10x cheaper)
2. **Cache parsed resumes** (avoid re-parsing)
3. **Batch process** when possible
4. **Set rate limits** to prevent abuse
5. **Monitor API usage** via OpenAI dashboard

---

## Backup & Recovery

### Database Backups

```bash
# Backup
pg_dump ats_db > backup_$(date +%Y%m%d).sql

# Restore
psql ats_db < backup_20260710.sql
```

### Application Data

Backup directories:
- `data/resumes/`
- `data/job_descriptions/`
- `logs/`

---

## Performance Tuning

### 1. Enable Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def parse_resume(file_path: str):
    ...
```

### 2. Async Processing

Use Celery for long-running evaluations:

```python
from celery import Celery

celery = Celery('ats', broker='redis://localhost:6379')

@celery.task
def evaluate_candidate_async(resume_path, job_desc, job_id):
    ...
```

### 3. Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## Troubleshooting

### Issue: High API Costs

**Solution:**
- Switch to gpt-4o-mini
- Implement caching
- Set request limits
- Reduce prompt sizes

### Issue: Slow Response Times

**Solution:**
- Use async/await properly
- Implement background processing
- Add Redis caching
- Optimize prompts

### Issue: Out of Memory

**Solution:**
- Increase container memory
- Implement request queuing
- Process in batches
- Clear temp files regularly

---

## Maintenance

### Regular Tasks

- [ ] Monitor API usage and costs
- [ ] Review logs for errors
- [ ] Update dependencies monthly
- [ ] Backup database weekly
- [ ] Test disaster recovery
- [ ] Review security patches

### Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Docker image
docker pull openai/openai:latest
docker-compose up -d --build

# Database migrations
alembic upgrade head
```

---

## Support

For deployment issues:
1. Check logs: `docker logs ats-api`
2. Verify configuration: `python verify_setup.py`
3. Test locally first
4. Review documentation
5. Open GitHub issue

---

## License

MIT License - See LICENSE file for details.
