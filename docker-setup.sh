#!/bin/bash

# Docker Setup Script for PostgreSQL Image Upload Server
# This script sets up persistent PostgreSQL container with data persistence

set -e

echo "🚀 Setting up PostgreSQL with Docker for Image Upload Server"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating Docker directories..."
    
    mkdir -p docker/postgres/data
    mkdir -p docker/postgres/init
    mkdir -p docker/pgadmin/data
    
    # Set proper permissions
    chmod 755 docker/postgres/data
    chmod 755 docker/pgadmin/data
    
    print_success "Docker directories created"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Database Configuration for Docker PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/image_upload_db
DB_ECHO=false

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server Configuration
HOST=0.0.0.0
PORT=8000

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/gif,image/webp

# Docker Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=image_upload_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
EOF
        print_success ".env file created"
        print_warning "⚠️  IMPORTANT: Change the SECRET_KEY and passwords in .env file for production!"
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Start Docker containers
start_containers() {
    print_status "Starting Docker containers..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Start containers
    docker-compose up -d
    
    print_success "Docker containers started"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    print_status "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U postgres -d image_upload_db > /dev/null 2>&1; then
            print_success "PostgreSQL is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts: PostgreSQL not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "PostgreSQL failed to start within expected time"
    return 1
}

# Initialize database
initialize_database() {
    print_status "Initializing database..."
    
    # Wait a bit more to ensure PostgreSQL is fully ready
    sleep 5
    
    # Run database setup
    python database_setup.py
    
    print_success "Database initialized successfully"
}

# Show status
show_status() {
    echo ""
    echo "=========================================================="
    print_success "Setup completed successfully!"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
    echo ""
    echo "🔗 Access Information:"
    echo "  • PostgreSQL: localhost:5432"
    echo "  • Database: image_upload_db"
    echo "  • Username: postgres"
    echo "  • Password: password"
    echo ""
    echo "🌐 pgAdmin (Database Management):"
    echo "  • URL: http://localhost:8080"
    echo "  • Email: admin@example.com"
    echo "  • Password: admin123"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Run the server: python main_clean.py"
    echo "  2. Test the API: python test_client.py"
    echo "  3. Access API docs: http://localhost:8000/docs"
    echo ""
    echo "💾 Data Persistence:"
    echo "  • PostgreSQL data: ./docker/postgres/data/"
    echo "  • pgAdmin data: ./docker/pgadmin/data/"
    echo "  • Data will persist after system reboot"
    echo ""
    echo "🔒 Security Note:"
    echo "  • Change default passwords in .env file for production"
    echo "  • .env file is in .gitignore and won't be committed to Git"
    echo ""
}

# Main execution
main() {
    echo "Starting Docker setup for PostgreSQL..."
    
    check_docker
    create_directories
    create_env_file
    start_containers
    wait_for_postgres
    initialize_database
    show_status
}

# Run main function
main "$@" 