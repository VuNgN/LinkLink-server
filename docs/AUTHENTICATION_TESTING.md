# 🔐 Authentication Flow Testing Guide

Complete guide for testing the authentication system in the Image Upload Server.

## 🎯 Overview

The authentication system includes:
- **User Registration** - Create new accounts
- **User Login** - Authenticate and get JWT tokens
- **Token Refresh** - Get new access tokens
- **Logout** - Invalidate tokens
- **Protected Endpoints** - Access control

## 🧪 Manual Testing with curl

### 1. **Health Check**
```bash
curl -X GET "http://localhost:8000/health"
```
**Expected Response:**
```json
{
  "status": "healthy",
  "architecture": "clean", 
  "database": "postgresql"
}
```

### 2. **User Registration**

#### ✅ Successful Registration
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser123", "password": "mypassword123"}'
```
**Expected Response:**
```json
{
  "message": "User registered successfully"
}
```

#### ❌ Username Already Exists
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser123", "password": "differentpassword"}'
```
**Expected Response:**
```json
{
  "detail": "Username already registered"
}
```

### 3. **User Login**

#### ✅ Successful Login
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser123", "password": "mypassword123"}'
```
**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2025-06-29T05:01:50.832872"
}
```

#### ❌ Wrong Password
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser123", "password": "wrongpassword"}'
```
**Expected Response:**
```json
{
  "detail": "Incorrect username or password"
}
```

#### ❌ User Not Found
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "nonexistentuser", "password": "anypassword"}'
```
**Expected Response:**
```json
{
  "detail": "Incorrect username or password"
}
```

### 4. **Access Protected Endpoints**

#### ✅ With Valid Access Token
```bash
# First, get the access token from login
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Then use it to access protected endpoints
curl -X GET "http://localhost:8000/api/v1/images" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```
**Expected Response:**
```json
[]
```

#### ❌ Without Access Token
```bash
curl -X GET "http://localhost:8000/api/v1/images"
```
**Expected Response:**
```json
{
  "detail": "Not authenticated"
}
```

#### ❌ With Invalid Access Token
```bash
curl -X GET "http://localhost:8000/api/v1/images" \
  -H "Authorization: Bearer invalid_token_here"
```
**Expected Response:**
```json
{
  "detail": "Could not validate credentials"
}
```

### 5. **Token Refresh**

#### ✅ Successful Token Refresh
```bash
# Use the refresh token from login
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/v1/refresh?refresh_token=$REFRESH_TOKEN"
```
**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2025-06-29T05:01:50.832872"
}
```

#### ❌ Invalid Refresh Token
```bash
curl -X POST "http://localhost:8000/api/v1/refresh?refresh_token=invalid_refresh_token"
```
**Expected Response:**
```json
{
  "detail": "Invalid refresh token"
}
```

### 6. **Logout**

#### ✅ Successful Logout
```bash
# Need both access token and refresh token
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/v1/logout?refresh_token=$REFRESH_TOKEN" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```
**Expected Response:**
```json
{
  "message": "Logged out successfully"
}
```

## 🧪 Automated Testing

### Run Complete Test Suite
```bash
python test_client.py
```

### Test Specific Functions
```python
# In test_client.py, you can modify the test data:
register_data = {
    "username": "your_test_user",
    "password": "your_test_password"
}

login_data = {
    "username": "your_test_user", 
    "password": "your_test_password"
}
```

## 🔧 Testing with Environment Variables

### Set Up Test Environment
```bash
# Create test environment
export TEST_USERNAME="testuser123"
export TEST_PASSWORD="testpass123"
export API_BASE_URL="http://localhost:8000"

# Test registration
curl -X POST "$API_BASE_URL/api/v1/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$TEST_USERNAME\", \"password\": \"$TEST_PASSWORD\"}"
```

## 🐳 Testing with Docker

### Start Services
```bash
./docker-setup.sh
```

### Check Database
```bash
# Access PostgreSQL shell
./docker-manage.sh shell

# In PostgreSQL shell:
\dt                    # List tables
SELECT * FROM users;   # View users
SELECT * FROM refresh_tokens;  # View tokens
```

### Check Logs
```bash
./docker-manage.sh logs
```

## 🔍 Debugging Authentication Issues

### 1. **Check Server Status**
```bash
curl -X GET "http://localhost:8000/health"
```

### 2. **Check Database Connection**
```bash
# In PostgreSQL shell
./docker-manage.sh shell
```

### 3. **Check Token Validity**
```bash
# Decode JWT token (without verification)
echo "your_jwt_token_here" | cut -d. -f2 | base64 -d | jq .
```

### 4. **Check API Documentation**
Open: http://localhost:8000/docs

## 📊 Test Scenarios

### Scenario 1: Complete User Journey
1. ✅ Register new user
2. ✅ Login with correct credentials
3. ✅ Access protected endpoint
4. ✅ Refresh token
5. ✅ Logout
6. ❌ Try to access protected endpoint after logout

### Scenario 2: Security Testing
1. ❌ Login with wrong password
2. ❌ Access protected endpoint without token
3. ❌ Use expired token
4. ❌ Use invalid refresh token

### Scenario 3: Edge Cases
1. ✅ Register with special characters in username
2. ✅ Register with long password
3. ❌ Register with empty username/password
4. ❌ Register with duplicate username

## 🛠️ Common Issues & Solutions

### Issue: "Username already registered"
**Solution:** Use a different username for testing

### Issue: "Incorrect username or password"
**Solution:** 
- Check if user exists in database
- Verify password is correct
- Check if user is active

### Issue: "Not authenticated"
**Solution:**
- Include Authorization header with Bearer token
- Check if token is valid and not expired

### Issue: "Invalid refresh token"
**Solution:**
- Use the refresh token from login response
- Check if token is expired
- Verify token format

## 📈 Performance Testing

### Load Testing with Apache Bench
```bash
# Test registration endpoint
ab -n 100 -c 10 -p register_data.json -T application/json \
   http://localhost:8000/api/v1/register

# Test login endpoint
ab -n 100 -c 10 -p login_data.json -T application/json \
   http://localhost:8000/api/v1/login
```

### Create test data files:
**register_data.json:**
```json
{"username": "testuser", "password": "testpass"}
```

**login_data.json:**
```json
{"username": "testuser", "password": "testpass"}
```

## 🔒 Security Testing Checklist

- [ ] ✅ Password hashing (bcrypt)
- [ ] ✅ JWT token expiration
- [ ] ✅ Refresh token rotation
- [ ] ✅ User isolation (users can only access their data)
- [ ] ✅ Input validation
- [ ] ✅ SQL injection protection
- [ ] ✅ CORS configuration
- [ ] ✅ Rate limiting (if implemented)

---

**This guide covers all aspects of testing the authentication system. Use these examples to verify your implementation works correctly! 🚀** 