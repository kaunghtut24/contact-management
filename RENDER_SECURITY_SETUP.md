# 🔐 Render Security Setup Guide

## 🚨 **DEPLOYMENT HEALTH CHECK FIX**

If you're getting a health check timeout error, the API has been fixed to:
- ✅ Start without JWT_SECRET_KEY (with warning)
- ✅ Use fallback secret for development/testing
- ✅ Fixed start script to use correct API file (`api:app`)
- ✅ Added root endpoint (`/`) for basic connectivity testing

**The API will start successfully even without environment variables, but you should still set them for security!**

## Required Environment Variables for Production Deployment

### 🚨 **CRITICAL SECURITY VARIABLES (REQUIRED)**

These variables MUST be set in Render's Environment Variables section for secure production deployment:

#### **1. JWT Secret Key**
```bash
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long-and-random
```
- **Purpose**: Signs and verifies JWT tokens
- **Requirements**: Minimum 32 characters, cryptographically random
- **Generate with**: `openssl rand -base64 32` or `python -c "import secrets; print(secrets.token_urlsafe(32))"`

#### **2. Admin User Credentials**
```bash
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_FULL_NAME=System Administrator
ADMIN_PASSWORD=YourSecureAdminPassword123!
```
- **Purpose**: Creates initial admin user from secure environment variables
- **Requirements**: Strong password (min 12 chars, mixed case, numbers, symbols)

### 🔧 **OPTIONAL SECURITY VARIABLES**

#### **3. Default User Credentials (Optional)**
```bash
DEFAULT_USER_USERNAME=user
DEFAULT_USER_EMAIL=user@yourcompany.com
DEFAULT_USER_FULL_NAME=Default User
DEFAULT_USER_PASSWORD=YourSecureUserPassword123!
```
- **Purpose**: Creates a default user account (admin can create via API)

#### **4. JWT Configuration**
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
- **Purpose**: JWT token expiration time
- **Default**: 30 minutes
- **Recommendation**: 15-60 minutes for production

### 🗄️ **DATABASE & SYSTEM VARIABLES**

```bash
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:5173
TESSERACT_PATH=/usr/bin/tesseract
ENVIRONMENT=production
DEBUG=false
```

## 📋 **Step-by-Step Render Setup**

### **Step 1: Access Render Dashboard**
1. Go to [https://dashboard.render.com/](https://dashboard.render.com/)
2. Navigate to your backend service
3. Click on "Environment" tab

### **Step 2: Add Security Environment Variables**

Click "Add Environment Variable" for each of these:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `JWT_SECRET_KEY` | `[Generate 32+ char random string]` | 🚨 CRITICAL |
| `ADMIN_USERNAME` | `admin` | Your admin username |
| `ADMIN_EMAIL` | `admin@yourcompany.com` | Admin email |
| `ADMIN_FULL_NAME` | `System Administrator` | Admin display name |
| `ADMIN_PASSWORD` | `[Strong password]` | 🚨 CRITICAL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry |
| `DATABASE_URL` | `[Your Neon PostgreSQL URL]` | 🚨 CRITICAL |
| `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` | CORS origins |
| `TESSERACT_PATH` | `/usr/bin/tesseract` | OCR path |
| `ENVIRONMENT` | `production` | Environment flag |
| `DEBUG` | `false` | Debug mode |

### **Step 3: Generate Secure Values**

#### **Generate JWT Secret Key:**
```bash
# Method 1: Using OpenSSL
openssl rand -base64 32

# Method 2: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 3: Online (use reputable generator)
# https://generate-secret.vercel.app/32
```

#### **Create Strong Passwords:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Avoid dictionary words
- Use password manager

### **Step 4: Deploy and Verify**

1. **Save environment variables** in Render
2. **Trigger deployment** (automatic or manual)
3. **Verify security** using API endpoints:

```bash
# Check health
curl https://your-backend.onrender.com/health

# Check OCR status
curl https://your-backend.onrender.com/ocr/status

# Create admin user (one-time)
curl -X POST https://your-backend.onrender.com/auth/create-admin

# Login as admin
curl -X POST https://your-backend.onrender.com/auth/login/simple \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "YourAdminPassword"}'

# Check security info (with admin token)
curl -X GET https://your-backend.onrender.com/security/info \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛡️ **Security Best Practices**

### **Environment Variables Security:**
- ✅ Never commit secrets to Git
- ✅ Use Render's encrypted environment variables
- ✅ Rotate secrets regularly
- ✅ Use different secrets for different environments
- ✅ Monitor access logs

### **Password Security:**
- ✅ bcrypt with 12 rounds (implemented)
- ✅ Strong password requirements
- ✅ No default passwords in production
- ✅ Environment variable configuration

### **JWT Security:**
- ✅ Strong secret key (32+ characters)
- ✅ Reasonable expiration time (30 minutes)
- ✅ HS256 algorithm
- ✅ Proper token validation

### **Database Security:**
- ✅ SSL/TLS connections (sslmode=require)
- ✅ Connection string in environment variables
- ✅ No hardcoded credentials

## 🚨 **Security Checklist**

Before going live, ensure:

- [ ] `JWT_SECRET_KEY` is set and strong (32+ chars)
- [ ] `ADMIN_PASSWORD` is set and strong
- [ ] `DATABASE_URL` is configured with SSL
- [ ] `ALLOWED_ORIGINS` includes only your frontend domain
- [ ] `DEBUG=false` in production
- [ ] All secrets are in environment variables, not code
- [ ] Admin user created successfully
- [ ] Authentication endpoints working
- [ ] Security info endpoint accessible by admin

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"JWT_SECRET_KEY environment variable is required"**
   - Solution: Set `JWT_SECRET_KEY` in Render environment variables

2. **"ADMIN_PASSWORD environment variable is required"**
   - Solution: Set `ADMIN_PASSWORD` in Render environment variables

3. **"Admin user already exists"**
   - Solution: Admin user was already created, use login endpoint

4. **CORS errors**
   - Solution: Update `ALLOWED_ORIGINS` with correct frontend URL

5. **Database connection errors**
   - Solution: Verify `DATABASE_URL` is correct and includes `sslmode=require`

## 📞 **Support**

If you encounter issues:
1. Check Render deployment logs
2. Verify all environment variables are set
3. Test endpoints individually
4. Check security info endpoint for configuration status
