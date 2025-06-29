# 🛠️ Admin Panel

This folder contains the administrative interface for the LinkLink Image Upload Server.

## 📁 Contents

- **`index.html`** - Main admin panel landing page
- **`admin_interface.html`** - Full admin interface for user management
- **`open_admin.sh`** - Script to launch admin interface in browser
- **`README.md`** - This documentation file

## 🚀 Access

### Quick Launch (Recommended)
```bash
# From the admin directory
./open_admin.sh

# Or from the project root
./admin/open_admin.sh
```

### Manual Access
```bash
# Open admin panel
open admin/index.html

# Or directly access the interface
open admin/admin_interface.html
```

### Production
```
https://yourdomain.com/admin/
https://yourdomain.com/admin/admin_interface.html
```

## 🔐 Security

⚠️ **Important Security Notes:**

1. **Access Control**: The admin interface should be protected with proper authentication
2. **HTTPS**: Always use HTTPS in production
3. **IP Restrictions**: Consider restricting admin access to specific IP addresses
4. **Session Management**: Implement proper session timeout and logout

## 🎯 Features

### User Management
- ✅ View pending user registrations
- ✅ Approve/reject new user accounts
- ✅ Manage existing user accounts
- ✅ View user statistics

### System Monitoring
- ✅ Database connection status
- ✅ Server health monitoring
- ✅ User activity tracking

### Database Management
- ✅ View database statistics
- ✅ Monitor storage usage
- ✅ Backup management

## 🔧 Configuration

### Environment Variables
Make sure these are set in your `.env` file:

```bash
# Admin email for notifications
ADMIN_EMAIL=admin@example.com

# Email configuration for notifications
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

### API Endpoints
The admin interface uses these API endpoints:

- `GET /api/v1/admin/pending-users` - Get pending registrations
- `POST /api/v1/admin/approve-user` - Approve/reject user
- `GET /api/v1/admin/stats` - Get system statistics

## 🛡️ Security Best Practices

1. **Authentication Required**: All admin endpoints require valid JWT tokens
2. **Role-Based Access**: Implement admin role checking
3. **Audit Logging**: Log all admin actions
4. **Input Validation**: Validate all admin inputs
5. **Rate Limiting**: Implement rate limiting for admin endpoints

## 📞 Support

For admin panel issues or questions:
- 📧 Email: admin@example.com
- 📚 Documentation: `../docs/`
- 🐛 Issues: Create an issue in the project repository

## 🔄 Updates

The admin interface is automatically updated when:
- New user registrations are submitted
- Admin actions are performed
- System status changes

---

**Last Updated**: January 2024
**Version**: 2.1.0 