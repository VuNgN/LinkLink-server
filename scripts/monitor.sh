#!/bin/bash

# Monitoring script for Image Upload Server
# Usage: ./scripts/monitor.sh [staging|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
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

COMPOSE_FILE="docker-compose.$ENVIRONMENT.yml"
API_PORT=$(if [ "$ENVIRONMENT" = "staging" ]; then echo "8001"; else echo "8002"; fi)

print_header "Monitoring $ENVIRONMENT environment..."

# Check if containers are running
print_info "Checking container status..."
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    print_info "Containers are running"
    docker-compose -f "$COMPOSE_FILE" ps
else
    print_error "Containers are not running"
    exit 1
fi

# Health check
print_info "Performing health check..."
if curl -f http://localhost:$API_PORT/health > /dev/null 2>&1; then
    print_info "Health check passed"
else
    print_error "Health check failed"
fi

# Check disk usage
print_info "Checking disk usage..."
df -h | grep -E "(Filesystem|/dev/)"

# Check memory usage
print_info "Checking memory usage..."
free -h

# Check container resource usage
print_info "Checking container resource usage..."
docker stats --no-stream

# Check logs for errors
print_info "Checking recent logs for errors..."
docker-compose -f "$COMPOSE_FILE" logs --tail=50 | grep -i error || print_info "No errors found in recent logs"

# Database connection check
print_info "Checking database connection..."
if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    print_info "Database connection is healthy"
else
    print_error "Database connection failed"
fi

# API response time
print_info "Checking API response time..."
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:$API_PORT/health)
print_info "API response time: ${RESPONSE_TIME}s"

# Check uploads directory
print_info "Checking uploads directory..."
if [ -d "uploads" ]; then
    UPLOAD_COUNT=$(find uploads -type f | wc -l)
    UPLOAD_SIZE=$(du -sh uploads 2>/dev/null | cut -f1)
    print_info "Uploads: $UPLOAD_COUNT files, $UPLOAD_SIZE"
else
    print_warning "Uploads directory not found"
fi

# Check logs directory
print_info "Checking logs directory..."
if [ -d "logs" ]; then
    LOG_SIZE=$(du -sh logs 2>/dev/null | cut -f1)
    print_info "Logs size: $LOG_SIZE"
else
    print_warning "Logs directory not found"
fi

print_header "Monitoring completed!" 