# 🐳 Docker Setup & Management

Complete guide for setting up and managing the Image Upload Server using Docker and Docker Compose.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Docker Services](#-docker-services)
- [Setup Scripts](#-setup-scripts)
- [Management Commands](#-management-commands)
- [Backup & Restore](#-backup--restore)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### Automatic Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/image-upload-server.git
cd image-upload-server

# Make scripts executable
chmod +x docker-setup.sh docker-manage.sh

# Run automatic setup
./docker-setup.sh
```

This will:
- ✅ Create necessary directories
- ✅ Generate `.env` file with proper configuration
- ✅ Start PostgreSQL and pgAdmin containers
- ✅ Initialize database with tables and default admin user
- ✅ Verify all services are running

### Manual Setup

```bash
# 1. Create environment file
cp env.example .env

# 2. Start services
docker-compose up -d

# 3. Initialize database
python database_setup.py

# 4. Verify setup
docker-compose ps
```

## 🏗️ Docker Services

### PostgreSQL Database

```yaml
postgres:
  image: postgres:15-alpine
  container_name: postgres-image-upload
  environment:
    POSTGRES_DB: image_upload_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: password
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./docker/postgres/init:/docker-entrypoint-initdb.d
  ports:
    - "5432:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 10s
    timeout: 5s
    retries: 5
  restart: unless-stopped
```

**Features:**
- **Persistent Storage**: Data survives container restarts
- **Health Checks**: Automatic monitoring
- **Initialization Scripts**: Auto-run SQL scripts on first startup
- **Alpine Linux**: Lightweight image

### pgAdmin (Database Management)

```yaml
pgadmin:
  image: dpage/pgadmin4:latest
  container_name: pgadmin-image-upload
  environment:
    PGADMIN_DEFAULT_EMAIL: admin@example.com
    PGADMIN_DEFAULT_PASSWORD: admin123
    PGADMIN_CONFIG_SERVER_MODE: 'False'
  volumes:
    - pgadmin_data:/var/lib/pgadmin
  ports:
    - "8080:80"
  depends_on:
    postgres:
      condition: service_healthy
  restart: unless-stopped
```

**Features:**
- **Web Interface**: Easy database management
- **Persistent Settings**: Saved configurations
- **Auto-connection**: Pre-configured PostgreSQL connection
- **Security**: HTTPS-ready

## 📜 Setup Scripts

### docker-setup.sh

```bash
#!/bin/bash
# Automatic Docker setup script

echo "🐳 Setting up Image Upload Server with Docker..."

# Create directories
mkdir -p uploads
mkdir -p docker/postgres/init
mkdir -p backups

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

# Start containers
echo "🚀 Starting Docker containers..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database..."
python database_setup.py

echo "✅ Setup complete!"
echo ""
echo "🌐 Access Information:"
echo "   API Server:     http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   pgAdmin:        http://localhost:8080"
echo "   PostgreSQL:     localhost:5432"
echo ""
echo "🔑 Default Credentials:"
echo "   pgAdmin:        admin@example.com / admin123"
echo "   PostgreSQL:     postgres / password"
echo "   Admin User:     admin / admin123"
```

### docker-manage.sh

```bash
#!/bin/bash
# Docker management script

case "$1" in
    start)
        echo "🚀 Starting containers..."
        docker-compose up -d
        ;;
    stop)
        echo "🛑 Stopping containers..."
        docker-compose down
        ;;
    restart)
        echo "🔄 Restarting containers..."
        docker-compose restart
        ;;
    logs)
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    status)
        echo "📊 Container status..."
        docker-compose ps
        ;;
    backup)
        echo "💾 Creating backup..."
        ./docker-manage.sh stop
        tar -czf "backups/backup-$(date +%Y%m%d-%H%M%S).tar.gz" \
            docker/postgres/data uploads/ .env
        ./docker-manage.sh start
        echo "✅ Backup created"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "❌ Please specify backup file"
            exit 1
        fi
        echo "📥 Restoring from backup..."
        ./docker-manage.sh stop
        tar -xzf "$2"
        ./docker-manage.sh start
        echo "✅ Restore complete"
        ;;
    reset)
        echo "⚠️  Resetting all data..."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./docker-manage.sh stop
            docker-compose down -v
            rm -rf uploads/*
            ./docker-setup.sh
            echo "✅ Reset complete"
        fi
        ;;
    shell)
        echo "🐚 Opening PostgreSQL shell..."
        docker-compose exec postgres psql -U postgres -d image_upload_db
        ;;
    pgadmin)
        echo "🌐 Opening pgAdmin..."
        xdg-open http://localhost:8080 2>/dev/null || \
        open http://localhost:8080 2>/dev/null || \
        echo "Please open: http://localhost:8080"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|backup|restore|reset|shell|pgadmin}"
        echo ""
        echo "Commands:"
        echo "  start     - Start containers"
        echo "  stop      - Stop containers"
        echo "  restart   - Restart containers"
        echo "  logs      - Show logs"
        echo "  status    - Show status"
        echo "  backup    - Create backup"
        echo "  restore   - Restore from backup"
        echo "  reset     - Reset all data"
        echo "  shell     - Open PostgreSQL shell"
        echo "  pgadmin   - Open pgAdmin"
        exit 1
        ;;
esac
```

## 🔧 Management Commands

### Basic Operations

```bash
# Start all services
./docker-manage.sh start

# Stop all services
./docker-manage.sh stop

# Restart services
./docker-manage.sh restart

# View logs
./docker-manage.sh logs

# Check status
./docker-manage.sh status
```

### Database Operations

```bash
# Access PostgreSQL shell
./docker-manage.sh shell

# Open pgAdmin web interface
./docker-manage.sh pgadmin

# Direct PostgreSQL connection
docker-compose exec postgres psql -U postgres -d image_upload_db
```

### Data Management

```bash
# Create backup
./docker-manage.sh backup

# Restore from backup
./docker-manage.sh restore backups/backup-20231201-143022.tar.gz

# Reset all data (⚠️ destructive)
./docker-manage.sh reset
```

## 💾 Backup & Restore

### Automatic Backups

```bash
# Create backup with timestamp
./docker-manage.sh backup

# Backup includes:
# - PostgreSQL data
# - Uploaded images
# - Environment configuration
```

### Manual Backups

```bash
# Stop services
docker-compose down

# Backup PostgreSQL data
docker run --rm -v postgres_image_upload_postgres_data:/data \
    -v $(pwd)/backups:/backup alpine tar czf \
    /backup/postgres-$(date +%Y%m%d).tar.gz -C /data .

# Backup uploads
tar czf backups/uploads-$(date +%Y%m%d).tar.gz uploads/

# Restart services
docker-compose up -d
```

### Restore Process

```bash
# Stop services
./docker-manage.sh stop

# Extract backup
tar xzf backup-file.tar.gz

# Start services
./docker-manage.sh start

# Verify data
./docker-manage.sh shell
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :5432
sudo netstat -tlnp | grep :8080

# Kill process or change ports in docker-compose.yml
```

#### 2. Permission Denied

```bash
# Fix script permissions
chmod +x docker-setup.sh docker-manage.sh

# Fix directory permissions
chmod 755 uploads/
chmod 755 backups/

# Fix Docker permissions (if needed)
sudo usermod -aG docker $USER
```

#### 3. Database Connection Failed

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart containers
docker-compose restart

# Check network
docker network ls
docker network inspect linklink_default
```

#### 4. Volume Issues

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect postgres_image_upload_postgres_data

# Remove volume (⚠️ data loss)
docker volume rm postgres_image_upload_postgres_data
```

### Debug Commands

```bash
# View all containers
docker ps -a

# View container logs
docker-compose logs postgres
docker-compose logs pgadmin

# Execute commands in container
docker-compose exec postgres psql -U postgres -c "\l"
docker-compose exec postgres psql -U postgres -d image_upload_db -c "\dt"

# Check resource usage
docker stats

# View network configuration
docker network inspect linklink_default
```

### Reset Everything

```bash
# Complete reset (⚠️ all data lost)
./docker-manage.sh stop
docker-compose down -v
docker system prune -f
rm -rf uploads/*
./docker-setup.sh
```

## 🚀 Production Deployment

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres-image-upload-prod
    environment:
      POSTGRES_DB: image_upload_db
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"  # Only local access
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - internal

  app:
    build: .
    container_name: image-upload-app
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - uploads:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - internal

volumes:
  postgres_data:
    driver: local
  uploads:
    driver: local

networks:
  internal:
    driver: bridge
```

### Production Environment

```bash
# .env.prod
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/image_upload_db
SECRET_KEY=your-very-long-random-secret-key
POSTGRES_USER=image_upload_user
POSTGRES_PASSWORD=your-strong-password
DB_ECHO=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FILE_SIZE=10485760
```

### Production Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads && chmod 755 uploads

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main_clean.py"]
```

### Production Deployment Commands

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale application
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup production data
docker-compose -f docker-compose.prod.yml exec postgres \
    pg_dump -U image_upload_user image_upload_db > backup.sql
```

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U postgres

# Container health
docker-compose ps
```

### Log Monitoring

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f app

# View recent logs
docker-compose logs --tail=100 postgres
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Volume usage
docker volume ls
du -sh uploads/
```

## 🔒 Security Considerations

### Production Security

1. **Change Default Passwords**
   ```bash
   # In .env file
   POSTGRES_PASSWORD=your-very-strong-password
   SECRET_KEY=your-very-long-random-secret-key
   ```

2. **Network Security**
   ```yaml
   # Only expose necessary ports
   ports:
     - "127.0.0.1:8000:8000"  # Local access only
   ```

3. **Disable pgAdmin in Production**
   ```yaml
   # Comment out pgadmin service
   # pgadmin:
   #   image: dpage/pgadmin4:latest
   ```

4. **Use Secrets Management**
   ```bash
   # Use Docker secrets or external secret management
   docker secret create postgres_password ./postgres_password.txt
   ```

5. **Regular Updates**
   ```bash
   # Update base images
   docker-compose pull
   docker-compose up -d
   ```

---

**For more information, see the main [README.md](README.md) file.** 