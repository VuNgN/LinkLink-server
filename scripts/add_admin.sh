#!/bin/bash

# Admin User Management Script
# This script provides easy access to admin user management tools

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
    echo "🛠️  Admin User Management Tool"
    echo "=============================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  create    - Create a new admin user (interactive)"
    echo "  list      - List all existing admin users"
    echo "  remove    - Remove an admin user (interactive)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 create"
    echo "  $0 list"
    echo ""
    echo "Prerequisites:"
    echo "  1. Docker containers running: ./docker-manage.sh start"
    echo "  2. Database initialized: python database/database_setup.py"
}

# Check if Python script exists
check_script() {
    if [ ! -f "database/add_admin_user.py" ]; then
        print_error "Admin user script not found: database/add_admin_user.py"
        exit 1
    fi
}

# Check if Docker containers are running
check_docker() {
    if ! docker-compose ps | grep -q "Up"; then
        print_warning "Docker containers are not running!"
        print_status "Starting Docker containers..."
        ./docker-manage.sh start
        sleep 5
    fi
}

# Create admin user
create_admin() {
    print_status "Creating new admin user..."
    check_script
    check_docker
    python database/add_admin_user.py create
}

# List admin users
list_admins() {
    print_status "Listing admin users..."
    check_script
    check_docker
    python database/add_admin_user.py list
}

# Remove admin user
remove_admin() {
    print_status "Removing admin user..."
    check_script
    check_docker
    python database/add_admin_user.py remove
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    case "$1" in
        "create")
            create_admin
            ;;
        "list")
            list_admins
            ;;
        "remove")
            remove_admin
            ;;
        "help"|"-h"|"--help")
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

# Run main function with all arguments
main "$@" 