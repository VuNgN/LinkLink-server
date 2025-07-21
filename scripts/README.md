# 📁 Scripts Directory

Thư mục này chứa tất cả các script để quản lý và triển khai dự án.

## 🚀 **Scripts Deployment & Management**

### **check_postgres_account.sh**
Script để kiểm tra và quản lý tài khoản PostgreSQL.
```bash
./check_postgres_account.sh
```
**Tính năng:**
- Kiểm tra container Postgres đang chạy
- Kiểm tra thông tin tài khoản
- Tạo lại tài khoản (mất dữ liệu)
- Đổi password

### **docker-manage.sh**
Script quản lý Docker containers (PostgreSQL, pgAdmin).
```bash
./docker-manage.sh [COMMAND]
```
**Commands:**
- `start` - Khởi động containers
- `stop` - Dừng containers
- `restart` - Khởi động lại containers
- `status` - Xem trạng thái containers
- `logs` - Xem logs
- `backup` - Tạo backup database
- `restore` - Khôi phục từ backup
- `reset` - Reset database (mất dữ liệu)
- `shell` - Mở PostgreSQL shell
- `pgadmin` - Mở pgAdmin trong browser
- `clean` - Xóa containers và volumes

### **docker-setup.sh**
Script tự động setup Docker environment.
```bash
./docker-setup.sh
```
**Tính năng:**
- Cài đặt Docker và Docker Compose
- Tạo thư mục cần thiết
- Khởi động containers
- Kiểm tra health

### **deploy.sh**
Script triển khai ứng dụng.
```bash
./deploy.sh [environment]
```
**Environments:**
- `development` - Triển khai môi trường development
- `production` - Triển khai môi trường production

### **monitor.sh**
Script giám sát hệ thống.
```bash
./monitor.sh
```
**Tính năng:**
- Kiểm tra trạng thái containers
- Kiểm tra logs
- Kiểm tra performance
- Kiểm tra disk usage

## 🔧 **Scripts Configuration**

### **add_admin.sh**
Script tạo tài khoản admin.
```bash
./add_admin.sh [username] [email] [password]
```

### **setup_ssh_agent.sh**
Script setup SSH agent cho deployment.
```bash
./setup_ssh_agent.sh
```

### **env.development**
File cấu hình môi trường development.
```bash
# Copy và chỉnh sửa
cp env.development ../.env
```

## 📋 **Cách sử dụng**

### **1. Cấp quyền thực thi:**
```bash
chmod +x scripts/*.sh
```

### **2. Chạy từ thư mục gốc:**
```bash
# Kiểm tra Postgres
./scripts/check_postgres_account.sh

# Quản lý Docker
./scripts/docker-manage.sh start

# Setup môi trường
./scripts/docker-setup.sh
```

### **3. Chạy từ thư mục scripts:**
```bash
cd scripts

# Kiểm tra Postgres
./check_postgres_account.sh

# Quản lý Docker
./docker-manage.sh start
```

## 🔒 **Security Notes**

- Đổi password mặc định trong production
- Không commit file `.env` chứa secrets
- Sử dụng SSH keys thay vì password
- Backup database thường xuyên

## 🐛 **Troubleshooting**

### **Container không start:**
```bash
./docker-manage.sh logs
```

### **Database connection error:**
```bash
./check_postgres_account.sh
```

### **Permission denied:**
```bash
chmod +x scripts/*.sh
```

## 📞 **Support**

Nếu gặp vấn đề, kiểm tra:
1. Docker đã được cài đặt
2. Ports không bị conflict
3. File permissions đúng
4. Environment variables đã được set 