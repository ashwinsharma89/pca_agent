# PCA Agent - Complete Deployment Package 🚀

## Overview

Production-ready Post Campaign Analysis Agent with comprehensive security, testing, monitoring, and deployment capabilities.

---

## 🎯 Quick Links

- **API Documentation**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **GitHub Repository**: https://github.com/ashwinsharma89/pca_agent
- **Docker Setup**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## ✨ Features

### Core Functionality
- ✅ Campaign analysis with AI insights
- ✅ Natural language to SQL queries
- ✅ Executive insights generation
- ✅ Multi-provider LLM support (OpenAI, Anthropic, Gemini)
- ✅ Knowledge base with RAG

### Security
- ✅ JWT authentication with role-based access
- ✅ User management system (no hardcoded credentials)
- ✅ SQL injection protection (4-layer validation)
- ✅ Password complexity requirements
- ✅ Account lockout protection
- ✅ Password reset functionality

### Performance
- ✅ Redis-based caching
- ✅ Database connection pooling
- ✅ Query optimization
- ✅ Rate limiting (API & LLM)
- ✅ Distributed rate limiting support

### Observability
- ✅ Structured JSON logging
- ✅ Prometheus metrics
- ✅ Distributed tracing
- ✅ Grafana dashboards
- ✅ LLM cost tracking
- ✅ Alerting system

### Testing
- ✅ 83+ unit tests
- ✅ Integration tests
- ✅ LLM mocking utilities
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ 70%+ code coverage

### Deployment
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Production-ready configuration
- ✅ Health checks
- ✅ Auto-restart policies
- ✅ Resource limits

---

## 🚀 Getting Started

### Option 1: Local Development (No Docker)

```bash
# 1. Clone repository
git clone https://github.com/ashwinsharma89/pca_agent.git
cd pca_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Initialize database
python scripts/init_database.py
python scripts/init_users.py

# 5. Start API
uvicorn src.api.main_v3:app --reload

# 6. Start Streamlit (optional)
streamlit run app_modular.py
```

### Option 2: Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/ashwinsharma89/pca_agent.git
cd pca_agent

# 2. Configure environment
cp .env.docker .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker-compose exec api python scripts/init_database.py
docker-compose exec api python scripts/init_users.py

# 5. Access services
# API: http://localhost:8000
# Streamlit: http://localhost:8501
# Grafana: http://localhost:3000
```

### Option 3: Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Docker Swarm setup
- Kubernetes deployment
- Cloud platform deployment (AWS, GCP, Azure)
- SSL/TLS configuration
- Monitoring setup
- Backup strategies

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PCA Agent System                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Streamlit   │────────▶│   FastAPI    │                 │
│  │  Frontend    │         │   Backend    │                 │
│  │  (Port 8501) │         │  (Port 8000) │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                   │                          │
│                    ┌──────────────┼──────────────┐          │
│                    │              │              │          │
│                    ▼              ▼              ▼          │
│            ┌──────────┐   ┌──────────┐   ┌──────────┐     │
│            │PostgreSQL│   │  Redis   │   │   LLM    │     │
│            │ Database │   │  Cache   │   │ Providers│     │
│            └──────────┘   └──────────┘   └──────────┘     │
│                    │              │              │          │
│                    └──────────────┼──────────────┘          │
│                                   │                          │
│                    ┌──────────────┴──────────────┐          │
│                    │                             │          │
│                    ▼                             ▼          │
│            ┌──────────────┐            ┌──────────────┐    │
│            │  Prometheus  │            │   Grafana    │    │
│            │  Monitoring  │───────────▶│  Dashboards  │    │
│            └──────────────┘            └──────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
pca_agent/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── v1/                # API v1 endpoints
│   │   ├── middleware/        # Auth, rate limiting
│   │   └── main_v3.py        # Main application
│   ├── agents/                # AI agents
│   ├── database/              # Database models & repos
│   ├── services/              # Business logic
│   └── utils/                 # Utilities
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── scripts/                   # Utility scripts
├── monitoring/                # Monitoring configs
├── streamlit_components/      # Modular UI components
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Container definition
└── requirements.txt           # Python dependencies
```

---

## 🔑 Environment Variables

### Required

```env
# API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Security
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
DB_PASSWORD=your-secure-db-password
```

### Optional

```env
# LLM Providers
GEMINI_API_KEY=your-gemini-key

# Database
USE_SQLITE=true  # or false for PostgreSQL
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# Monitoring
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your-langsmith-key
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_api_auth.py

# Run in Docker
docker-compose exec api pytest
```

---

## 📈 Monitoring

### Metrics

Access Prometheus at http://localhost:9090

**Key Metrics**:
- `api_requests_total` - Request count
- `api_errors_total` - Error count
- `response_time_ms` - Response times
- `llm_tokens_total` - Token usage
- `llm_cost_usd` - LLM costs

### Dashboards

Access Grafana at http://localhost:3000

**Pre-configured**:
- API performance dashboard
- Database metrics
- Redis statistics
- LLM usage and costs

### Logs

```bash
# View API logs
docker-compose logs -f api

# View all logs
docker-compose logs -f

# Application logs
tail -f logs/app.log
```

---

## 🔒 Security

### Authentication

```bash
# Create admin user
docker-compose exec api python scripts/init_users.py

# Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Use token in requests
curl http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Rate Limits

| Tier | API Limit | LLM Limit (OpenAI) |
|------|-----------|-------------------|
| Free | 10/min | 3/min |
| Pro | 100/min | 60/min |
| Enterprise | 1000/min | 500/min |

---

## 🛠️ Maintenance

### Backups

```bash
# Backup database
docker-compose exec postgres pg_dump -U pca_user pca_agent > backup.sql

# Backup Redis
docker-compose exec redis redis-cli --rdb /data/dump.rdb

# Automated backups
./scripts/scheduled_backup.py
```

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart with new version
docker-compose up -d
```

### Health Checks

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check detailed health
curl http://localhost:8000/health/detailed
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DOCKER_SETUP.md](DOCKER_SETUP.md) | Complete Docker guide |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Production deployment |
| [TESTING_INFRASTRUCTURE.md](TESTING_INFRASTRUCTURE.md) | Testing guide |
| [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) | Security features |
| [USER_MANAGEMENT_COMPLETE.md](USER_MANAGEMENT_COMPLETE.md) | User management |
| [REDIS_RATE_LIMITING_COMPLETE.md](REDIS_RATE_LIMITING_COMPLETE.md) | Rate limiting |
| [OBSERVABILITY_STATUS.md](OBSERVABILITY_STATUS.md) | Monitoring features |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🆘 Support

### Getting Help

- **Documentation**: Check the docs folder
- **Issues**: https://github.com/ashwinsharma89/pca_agent/issues
- **Logs**: `docker-compose logs -f`
- **Health**: http://localhost:8000/health/detailed

### Common Issues

1. **Docker not installed**: Install Docker Desktop
2. **Port conflicts**: Change ports in docker-compose.yml
3. **API keys missing**: Add to .env file
4. **Database connection failed**: Check PostgreSQL is running

---

## 🎯 Roadmap

- [x] Core campaign analysis
- [x] Security implementation
- [x] Testing infrastructure
- [x] Docker containerization
- [x] Monitoring stack
- [ ] Multi-tenancy support
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] API marketplace

---

## 📊 Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | 62,000+ |
| **Test Coverage** | 70%+ |
| **API Endpoints** | 15+ |
| **Docker Services** | 6 |
| **Documentation Files** | 12+ |
| **Features Implemented** | 20+ |

---

## ✅ Status

**Current Version**: 3.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: December 1, 2025

---

**Ready to deploy!** 🚀

Choose your deployment method and follow the guides above.
