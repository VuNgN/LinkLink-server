#!/bin/bash

# Docker Management Script for PostgreSQL Image Upload Server
# This script provides easy commands to manage Docker containers

set -e

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

# Show usage
show_usage() {
    echo "🐳 Docker Management Script for PostgreSQL Image Upload Server"
    echo "============================================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start PostgreSQL and pgAdmin containers"
    echo "  stop      - Stop all containers"
    echo "  restart   - Restart all containers"
    echo "  status    - Show container status"
    echo "  logs      - Show container logs"
    echo "  backup    - Create database backup"
    echo "  restore   - Restore database from backup"
    echo "  reset     - Reset database (WARNING: This will delete all data)"
    echo "  shell     - Open PostgreSQL shell"
    echo "  pgadmin   - Open pgAdmin in browser"
    echo "  clean     - Remove containers and volumes (WARNING: This will delete all data)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs"
    echo "  $0 backup"
}

# Start containers
start_containers() {
    print_status "Starting Docker containers..."
    docker-compose up -d
    print_success "Containers started successfully"
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    if docker-compose exec -T postgres pg_isready -U postgres -d image_upload_db > /dev/null 2>&1; then
        print_success "PostgreSQL is ready!"
    else
        print_warning "PostgreSQL might still be starting up..."
    fi
}

# Stop containers
stop_containers() {
    print_status "Stopping Docker containers..."
    docker-compose down
    print_success "Containers stopped successfully"
}

# Restart containers
restart_containers() {
    print_status "Restarting Docker containers..."
    docker-compose restart
    print_success "Containers restarted successfully"
}

# Show status
show_status() {
    echo "📊 Container Status:"
    docker-compose ps
    echo ""
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        echo "🔗 Access Information:"
        echo "  • PostgreSQL: localhost:5432"
        echo "  • Database: image_upload_db"
        echo "  • Username: postgres"
        echo "  • Password: password"
        echo ""
        echo "🌐 pgAdmin: http://localhost:8080"
        echo "  • Email: admin@example.com"
        echo "  • Password: admin123"
    fi
}

# Show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f
}

# Create backup
create_backup() {
    local backup_dir="./backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/backup_$timestamp.sql"
    
    print_status "Creating database backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$backup_dir"
    
    # Create backup
    docker-compose exec -T postgres pg_dump -U postgres image_upload_db > "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "Backup created: $backup_file"
        echo "Backup size: $(du -h "$backup_file" | cut -f1)"
    else
        print_error "Backup failed"
        exit 1
    fi
}

# Restore backup
restore_backup() {
    if [ -z "$1" ]; then
        print_error "Please specify backup file to restore"
        echo "Usage: $0 restore <backup_file>"
        echo ""
        echo "Available backups:"
        ls -la ./backups/ 2>/dev/null || echo "No backups found"
        exit 1
    fi
    
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_warning "This will overwrite the current database!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restoring database from backup..."
        docker-compose exec -T postgres psql -U postgres -d image_upload_db < "$backup_file"
        print_success "Database restored successfully"
    else
        print_status "Restore cancelled"
    fi
}

# Reset database
reset_database() {
    print_warning "This will delete all data in the database!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Resetting database..."
        
        # Drop and recreate database
        docker-compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS image_upload_db;"
        docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE image_upload_db;"
        
        # Reinitialize database
        python database_setup.py
        
        print_success "Database reset successfully"
    else
        print_status "Reset cancelled"
    fi
}

# Open PostgreSQL shell
open_shell() {
    print_status "Opening PostgreSQL shell..."
    docker-compose exec postgres psql -U postgres -d image_upload_db
}

# Open pgAdmin
open_pgadmin() {
    print_status "Opening pgAdmin in browser..."
    
    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Containers are not running. Start them first with: $0 start"
        exit 1
    fi
    
    # Try to open browser
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8080
    elif command -v open &> /dev/null; then
        open http://localhost:8080
    else
        print_status "Please open your browser and go to: http://localhost:8080"
        print_status "Email: admin@example.com"
        print_status "Password: admin123"
    fi
}

# Clean everything
clean_all() {
    print_warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up Docker resources..."
        
        # Stop and remove containers
        docker-compose down -v
        
        # Remove volumes
        docker volume rm $(docker volume ls -q | grep postgres) 2>/dev/null || true
        
        # Remove data directories
        rm -rf docker/postgres/data/*
        rm -rf docker/pgadmin/data/*
        
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Migrate album DB
migrate_album_db() {
    print_status "Running album DB migration (album_migration.sql)..."
    if [ ! -f database/album_migration.sql ]; then
        print_error "Migration file database/album_migration.sql not found!"
        exit 1
    fi
    docker-compose cp database/album_migration.sql postgres:/album_migration.sql
    docker-compose exec -T postgres psql -U postgres -d image_upload_db -f /album_migration.sql
    docker-compose exec -T postgres rm /album_migration.sql
    print_success "Album DB migration completed."
}

# Main execution
main() {
    case "${1:-help}" in
        start)
            start_containers
            ;;
        stop)
            stop_containers
            ;;
        restart)
            restart_containers
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup "$2"
            ;;
        reset)
            reset_database
            ;;
        shell)
            open_shell
            ;;
        pgadmin)
            open_pgadmin
            ;;
        clean)
            clean_all
            ;;
        migrate-album)
            migrate_album_db
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 