#!/bin/bash

# Script để kiểm tra và tạo lại tài khoản Postgres
# Sử dụng: ./check_postgres_account.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Kiểm tra container Postgres đang chạy
check_postgres_container() {
    print_status "Kiểm tra container Postgres..."
    
    if docker ps | grep -q "postgres-image-upload-development"; then
        print_success "Container Postgres đang chạy"
        return 0
    else
        print_warning "Container Postgres không chạy"
        return 1
    fi
}

# Kiểm tra thông tin tài khoản Postgres
check_postgres_account() {
    print_status "Kiểm tra thông tin tài khoản Postgres..."
    
    # Lấy thông tin từ container
    POSTGRES_USER=$(docker exec postgres-image-upload-development env | grep POSTGRES_USER | cut -d'=' -f2)
    POSTGRES_DB=$(docker exec postgres-image-upload-development env | grep POSTGRES_DB | cut -d'=' -f2)
    
    echo "PostgreSQL User: $POSTGRES_USER"
    echo "PostgreSQL Database: $POSTGRES_DB"
    
    # Thử kết nối với password mặc định
    if docker exec postgres-image-upload-development psql -U postgres -d image_upload_development -c "SELECT 1;" > /dev/null 2>&1; then
        print_success "Kết nối thành công với password mặc định"
        return 0
    else
        print_warning "Không thể kết nối với password mặc định"
        return 1
    fi
}

# Tạo lại tài khoản Postgres
reset_postgres_account() {
    print_warning "Bạn có muốn tạo lại tài khoản Postgres? (Tất cả dữ liệu sẽ bị mất!)"
    read -p "Nhập 'yes' để tiếp tục: " confirm
    
    if [ "$confirm" = "yes" ]; then
        print_status "Dừng và xóa container cũ..."
        docker-compose -f ../docker-compose.development.yml down -v
        
        print_status "Tạo lại container với tài khoản mới..."
        docker-compose -f ../docker-compose.development.yml up -d
        
        print_status "Chờ Postgres khởi động..."
        sleep 10
        
        if check_postgres_account; then
            print_success "Tài khoản Postgres đã được tạo lại thành công!"
            echo "Thông tin kết nối:"
            echo "  Host: localhost"
            echo "  Port: 5433"
            echo "  Database: image_upload_development"
            echo "  User: postgres"
            echo "  Password: password"
        else
            print_error "Không thể tạo lại tài khoản Postgres"
            exit 1
        fi
    else
        print_status "Hủy bỏ việc tạo lại tài khoản"
    fi
}

# Đổi password Postgres
change_postgres_password() {
    print_status "Đổi password Postgres..."
    
    read -p "Nhập password mới: " new_password
    
    if docker exec postgres-image-upload-development psql -U postgres -d image_upload_development -c "ALTER USER postgres WITH PASSWORD '$new_password';" > /dev/null 2>&1; then
        print_success "Password đã được đổi thành công!"
        echo "Password mới: $new_password"
    else
        print_error "Không thể đổi password"
        exit 1
    fi
}

# Menu chính
show_menu() {
    echo ""
    echo "🐘 PostgreSQL Account Management"
    echo "================================"
    echo "1. Kiểm tra container Postgres"
    echo "2. Kiểm tra tài khoản Postgres"
    echo "3. Tạo lại tài khoản (mất dữ liệu)"
    echo "4. Đổi password"
    echo "5. Thoát"
    echo ""
    read -p "Chọn tùy chọn (1-5): " choice
    
    case $choice in
        1)
            check_postgres_container
            ;;
        2)
            if check_postgres_container; then
                check_postgres_account
            fi
            ;;
        3)
            if check_postgres_container; then
                reset_postgres_account
            fi
            ;;
        4)
            if check_postgres_container; then
                change_postgres_password
            fi
            ;;
        5)
            print_status "Thoát..."
            exit 0
            ;;
        *)
            print_error "Lựa chọn không hợp lệ"
            ;;
    esac
}

# Chạy menu
show_menu 