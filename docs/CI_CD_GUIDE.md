# 🚀 CI/CD Pipeline Guide

Comprehensive guide for the Image Upload Server CI/CD pipeline implementation.

## 📋 Overview

The CI/CD pipeline is implemented using **GitHub Actions** and includes:

- ✅ **Automated Testing** - Unit, integration, and security tests
- ✅ **Code Quality** - Linting and code coverage
- ✅ **Security Scanning** - Vulnerability and dependency scanning
- ✅ **Multi-Environment Deployment** - Staging and production
- ✅ **Monitoring** - Health checks and performance monitoring

## 🔄 Pipeline Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Push     │───▶│   Backend Job   │───▶│  Frontend Job   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Integration Job │───▶│  Deploy Jobs    │
                       └─────────────────┘    └─────────────────┘
```

## 🧪 Testing Strategy

### 1. **Unit Tests**
- **Location**: `tests/unit/`
- **Framework**: pytest
- **Coverage**: Business logic and services
- **Command**: `pytest tests/unit/ -v --cov=app`

### 2. **Integration Tests**
- **Location**: `tests/integration/`
- **Framework**: pytest + httpx
- **Coverage**: API endpoints and database integration
- **Command**: `pytest tests/integration/ -v`

### 3. **Security Tests**
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Trivy**: Container and filesystem scanning
- **npm audit**: Frontend dependency scanning

## 🔒 Security Scanning

### Backend Security
```yaml
- name: Security scan backend (bandit)
  run: |
    bandit -r app/ -f json -o bandit-report.json || true

- name: Security scan backend (safety)
  run: |
    safety check --json --output safety-report.json || true

- name: Security scan backend (trivy)
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: fs
    scan-ref: app
```

### Frontend Security
```yaml
- name: Security scan frontend (npm audit)
  run: npm audit --audit-level=moderate

- name: Security scan frontend (trivy)
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: fs
    scan-ref: frontend
```

## 🐳 Deployment Environments

### Staging Environment
- **Trigger**: Push to `develop` branch
- **Docker Compose**: `docker-compose.staging.yml`
- **Ports**: 
  - API: 8001
  - PostgreSQL: 5433
  - pgAdmin: 8081
- **Database**: `image_upload_staging`

### Production Environment
- **Trigger**: Push to `main` branch
- **Docker Compose**: `docker-compose.prod.yml`
- **Ports**:
  - API: 8002
  - PostgreSQL: 5434
  - Nginx: 80/443
- **Database**: `image_upload_prod`

## 🛠️ Local Development

### Running Tests Locally
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test types
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run security scans
bandit -r app/
safety check
```

### Running Docker Environments
```bash
# Development
docker-compose up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring & Observability

### Health Checks
- **Endpoint**: `/health`
- **Frequency**: 30s intervals
- **Checks**: Database connection, service status

### Metrics Collection
- **Response Time**: API endpoint performance
- **Error Rates**: Failed requests tracking
- **Resource Usage**: CPU, memory, disk usage

### Logging
- **Format**: Structured JSON logging
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Rotation**: 10MB files, 7 days retention

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=image_upload_db

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret

# Application
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### GitHub Secrets
Required secrets for CI/CD:
- `PGUSER`: PostgreSQL username
- `PGPASSWORD`: PostgreSQL password
- `PGDATABASE`: PostgreSQL database name
- `SECRET_KEY`: Application secret key

## 🚀 Deployment Commands

### Automated Deployment
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production
```

### Manual Deployment
```bash
# Build and start staging
docker-compose -f docker-compose.staging.yml up -d --build

# Build and start production
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Indexes for performance
CREATE INDEX idx_images_username ON images(username);
CREATE INDEX idx_refresh_tokens_username ON refresh_tokens(username);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

### Application Optimization
```python
# Connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Tests Failing**
```bash
# Check test database connection
docker-compose exec postgres pg_isready -U postgres

# Run tests with verbose output
pytest -v --tb=long
```

#### 2. **Deployment Failing**
```bash
# Check container logs
docker-compose -f docker-compose.staging.yml logs

# Check container status
docker-compose -f docker-compose.staging.yml ps
```

#### 3. **Security Scan Issues**
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for known vulnerabilities
safety check
```

### Debug Commands
```bash
# Monitor application
./scripts/monitor.sh staging

# Check health
curl http://localhost:8001/health

# View logs
docker-compose -f docker-compose.staging.yml logs -f
```

## 📚 Best Practices

### 1. **Code Quality**
- ✅ Write unit tests for all business logic
- ✅ Maintain >80% code coverage
- ✅ Use type hints throughout
- ✅ Follow PEP 8 style guidelines

### 2. **Security**
- ✅ Never commit secrets to Git
- ✅ Use environment variables for configuration
- ✅ Regular dependency updates
- ✅ Security scanning in CI/CD

### 3. **Deployment**
- ✅ Test in staging before production
- ✅ Use blue-green deployment strategy
- ✅ Monitor application health
- ✅ Keep deployment logs

### 4. **Monitoring**
- ✅ Set up alerts for critical failures
- ✅ Monitor resource usage
- ✅ Track performance metrics
- ✅ Regular log analysis

## 🔄 Continuous Improvement

### Metrics to Track
- **Test Coverage**: Aim for >80%
- **Build Time**: Optimize for <10 minutes
- **Deployment Success Rate**: Target >95%
- **Security Vulnerabilities**: Zero critical issues

### Regular Reviews
- **Weekly**: Security scan results
- **Monthly**: Performance metrics review
- **Quarterly**: Pipeline optimization
- **Annually**: Architecture review

---

**This CI/CD pipeline provides a robust foundation for continuous delivery with security, testing, and monitoring built-in! 🚀** 