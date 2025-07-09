# 🌐 Production Deployment Guide

This guide covers deploying the Contact Management System to production using three cloud providers:
- **Database**: Neon PostgreSQL
- **Frontend**: Vercel
- **Backend**: Render

## 🗄️ Database Setup (Neon PostgreSQL)

### 1. Create Neon Account
1. Visit [Neon Console](https://console.neon.tech/)
2. Sign up with GitHub or email
3. Create a new project

### 2. Configure Database
```sql
-- Database will be created automatically
-- Note the connection details:
-- Host: ep-xxx.us-east-1.aws.neon.tech
-- Database: neondb
-- Username: your-username
-- Password: your-password
```

### 3. Get Connection String
```
postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

## 🎨 Frontend Deployment (Vercel)

### 1. Prepare Repository
```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### 2. Deploy to Vercel
1. Visit [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import from GitHub: `kaunghtut24/contact-management`
4. Configure build settings:

**Build Settings:**
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 3. Environment Variables
Add in Vercel Dashboard → Settings → Environment Variables:
```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

### 4. Custom Domain (Optional)
1. Go to Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

## 🚀 Backend Deployment (Render)

### 1. Create Render Account
1. Visit [Render Dashboard](https://dashboard.render.com/)
2. Sign up with GitHub
3. Connect your GitHub repository

### 2. Create Web Service
1. Click "New" → "Web Service"
2. Connect repository: `kaunghtut24/contact-management`
3. Configure service:

**Service Configuration:**
```
Name: contact-management-backend
Environment: Python 3
Region: Oregon (US West)
Branch: production
Root Directory: backend
Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
Start Command: python -m uvicorn api:app --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables
Add in Render Dashboard → Environment:
```env
# Database
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# JWT Configuration
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Admin User
ADMIN_USERNAME=your-admin-username
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourSecurePassword123!

# Environment
ENVIRONMENT=production

# CORS Configuration
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app

# OCR Configuration
TESSDATA_PREFIX=./tessdata
TESSERACT_PATH=/usr/bin/tesseract
```

### 4. Configure Build
Create `backend/render.yaml`:
```yaml
services:
  - type: web
    name: contact-management-api
    env: python
    region: oregon
    plan: starter
    buildCommand: |
      pip install -r requirements.txt
      python -m spacy download en_core_web_sm
      apt-get update && apt-get install -y tesseract-ocr
    startCommand: python -m uvicorn api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: ADMIN_USERNAME
        sync: false
      - key: ADMIN_EMAIL
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        sync: false
      - key: TESSDATA_PREFIX
        value: ./tessdata
      - key: TESSERACT_PATH
        value: /usr/bin/tesseract
```

## 🔧 Configuration Files

### Backend Dockerfile (Optional)
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Ensure tessdata directory is accessible
RUN ls -la tessdata/ && \
    echo "✅ Tessdata files:" && \
    ls -lh tessdata/*.traineddata

# Create necessary directories
RUN mkdir -p uploads logs

# Set environment variables
ENV TESSDATA_PREFIX=./tessdata
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build Script
Create `backend/build.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Starting production build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Install Tesseract
echo "🔍 Installing Tesseract OCR..."
if command -v apt-get &> /dev/null; then
    apt-get update && apt-get install -y tesseract-ocr
elif command -v yum &> /dev/null; then
    yum install -y tesseract
fi

# Verify Tesseract installation
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract installed: $(tesseract --version | head -1)"
else
    echo "❌ Tesseract installation failed"
    exit 1
fi

# Set Tesseract environment variables
export TESSERACT_PATH=/usr/bin/tesseract

# Use bundled tessdata if available
if [ -d "./tessdata" ] && [ -f "./tessdata/eng.traineddata" ]; then
    export TESSDATA_PREFIX="./tessdata"
    echo "✅ Using bundled tessdata directory"
else
    echo "🔍 Using system tessdata directory"
fi

echo "🔧 Tesseract environment configured:"
echo "   TESSERACT_PATH=$TESSERACT_PATH"
echo "   TESSDATA_PREFIX=$TESSDATA_PREFIX"

# List available language files
echo "📋 Available Tesseract language files:"
if [ -d "$TESSDATA_PREFIX" ]; then
    ls -la "$TESSDATA_PREFIX"/*.traineddata 2>/dev/null || echo "   No .traineddata files found"
else
    echo "   Tessdata directory not found: $TESSDATA_PREFIX"
fi

echo "✅ Build completed successfully!"
```

## 🔐 Security Configuration

### 1. Environment Variables Security
- Use strong, unique passwords
- Generate secure JWT secret keys
- Never commit secrets to version control
- Use different credentials for each environment

### 2. Database Security
- Enable SSL connections (Neon provides this by default)
- Use connection pooling
- Regular backups (Neon handles this)
- Monitor database performance

### 3. API Security
- HTTPS only in production
- Proper CORS configuration
- Rate limiting (implement if needed)
- Input validation and sanitization

## 📊 Monitoring and Maintenance

### 1. Health Checks
```bash
# Backend health
curl https://your-backend.onrender.com/health

# Database connection
curl https://your-backend.onrender.com/auth/system-info

# OCR status
curl https://your-backend.onrender.com/ocr/status
```

### 2. Logs Monitoring
- **Render**: Dashboard → Logs
- **Vercel**: Dashboard → Functions → Logs
- **Neon**: Console → Monitoring

### 3. Performance Monitoring
- Monitor response times
- Database query performance
- Memory and CPU usage
- Error rates and patterns

## 🚀 Deployment Workflow

### 1. Development to Production
```bash
# 1. Test locally
npm run dev  # Frontend
python -m uvicorn api:app --reload  # Backend

# 2. Commit changes
git add .
git commit -m "Feature: Add new functionality"

# 3. Deploy to production branch
git checkout production
git merge main
git push origin production

# 4. Verify deployments
# - Render will auto-deploy backend
# - Vercel will auto-deploy frontend
```

### 2. Rollback Strategy
```bash
# Rollback to previous version
git checkout production
git reset --hard HEAD~1
git push --force origin production
```

## 🔍 Troubleshooting

### Common Production Issues

**1. Database Connection Errors**
- Verify Neon connection string
- Check SSL requirements
- Monitor connection limits

**2. CORS Issues**
- Update ALLOWED_ORIGINS environment variable
- Verify frontend URL in backend config

**3. OCR Not Working**
- Check Tesseract installation in build logs
- Verify tessdata files are bundled
- Monitor memory usage during OCR processing

**4. Build Failures**
- Check build logs in Render dashboard
- Verify all dependencies in requirements.txt
- Ensure Python version compatibility

## 📞 Support and Resources

- **Neon Documentation**: https://neon.tech/docs
- **Vercel Documentation**: https://vercel.com/docs
- **Render Documentation**: https://render.com/docs
- **GitHub Repository**: https://github.com/kaunghtut24/contact-management

## 🎯 Production URLs

After successful deployment:
- **Frontend**: https://contact-management-six-alpha.vercel.app
- **Backend**: https://contact-management-ffsl.onrender.com
- **API Docs**: https://contact-management-ffsl.onrender.com/docs
