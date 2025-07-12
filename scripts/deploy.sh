#!/bin/bash

# Deployment script for Image Upload Server
# Usage: ./scripts/deploy.sh [staging|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
if [ $# -eq 0 ]; then
    print_error "Please specify environment: staging or production"
    echo "Usage: $0 [staging|production]"
    exit 1
fi

ENVIRONMENT=$1

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    print_error "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

print_info "Starting deployment to $ENVIRONMENT environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose file exists
COMPOSE_FILE="docker-compose.$ENVIRONMENT.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Docker Compose file $COMPOSE_FILE not found"
    exit 1
fi

# Load environment variables
ENV_FILE=".env.$ENVIRONMENT"
if [ -f "$ENV_FILE" ]; then
    print_info "Loading environment variables from $ENV_FILE"
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    print_warning "Environment file $ENV_FILE not found, using default values"
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p docker/postgres/${ENVIRONMENT}_data
mkdir -p docker/pgadmin/${ENVIRONMENT}_data
mkdir -p uploads
mkdir -p logs

# Set permissions
chmod 755 uploads
chmod 755 logs

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans

# Build and start containers
print_info "Building and starting containers..."
docker-compose -f "$COMPOSE_FILE" up -d --build

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_info "Checking service status..."
docker-compose -f "$COMPOSE_FILE" ps

# Health check
print_info "Performing health check..."
if curl -f http://localhost:$(if [ "$ENVIRONMENT" = "staging" ]; then echo "8001"; else echo "8002"; fi)/health > /dev/null 2>&1; then
    print_info "Health check passed!"
else
    print_error "Health check failed!"
    docker-compose -f "$COMPOSE_FILE" logs
    exit 1
fi

# Show deployment info
print_info "Deployment completed successfully!"
echo ""
echo "🌐 Access Information:"
if [ "$ENVIRONMENT" = "staging" ]; then
    echo "  • API: http://localhost:8001"
    echo "  • API Docs: http://localhost:8001/docs"
    echo "  • pgAdmin: http://localhost:8081"
    echo "  • PostgreSQL: localhost:5433"
else
    echo "  • API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Nginx: http://localhost:80"
    echo "  • PostgreSQL: localhost:5434"
fi
echo ""
echo "📊 Container Status:"
docker-compose -f "$COMPOSE_FILE" ps
echo ""
echo "📝 Logs:"
echo "  • View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  • Stop services: docker-compose -f $COMPOSE_FILE down"
echo "" 