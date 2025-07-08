# 🚀 Render Cloud Deployment Guide

## Overview

This guide will help you deploy the Contact Management System to Render cloud platform with automatic SpaCy model installation.

## 📋 Prerequisites

- GitHub repository with your code
- Render account (free tier available)
- Neon PostgreSQL database (already configured)

## 🔧 Backend Deployment on Render

### Step 1: Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select the repository: `kaunghtut24/contact-management`
5. Configure the service:

**Basic Settings:**
- **Name**: `contact-management-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `production`
- **Root Directory**: `backend`

**Build & Deploy:**
- **Build Command**: `./build.sh`
- **Start Command**: `./start.sh`

### Step 2: Environment Variables

Add these environment variables in Render dashboard:

```bash
DATABASE_URL=postgresql://neondb_owner:npg_oCyiNY6RD4gF@ep-white-river-a8irxian-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
ALLOWED_ORIGINS=https://your-frontend.onrender.com,http://localhost:5173
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/tmp/uploads/
TESSERACT_PATH=/usr/bin/tesseract
ENVIRONMENT=production
DEBUG=false
SPACY_MODEL=en_core_web_sm
```

### Step 3: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install Python dependencies
   - Download SpaCy English model
   - Create necessary directories
   - Start the FastAPI server

## 🎨 Frontend Deployment on Render

### Step 1: Create Static Site

1. In Render Dashboard, click "New" → "Static Site"
2. Connect the same GitHub repository
3. Configure:

**Basic Settings:**
- **Name**: `contact-management-frontend`
- **Branch**: `production`
- **Root Directory**: `frontend`

**Build & Deploy:**
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`

### Step 2: Environment Variables

Add this environment variable:

```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
```

## 🔗 Configuration Files Included

### `backend/build.sh`
- Installs Python dependencies
- Downloads SpaCy English model
- Creates necessary directories
- Sets permissions

### `backend/start.sh`
- Checks SpaCy model availability
- Downloads model if missing
- Starts FastAPI server

### `backend/render.yaml`
- Render service configuration
- Environment variables setup
- Build and start commands

## ✅ Verification Steps

### Test Backend
1. Wait for deployment to complete
2. Visit: `https://your-backend.onrender.com/health`
3. Expected response: `{"status":"healthy","message":"Contact Management System API is running"}`

### Test Frontend
1. Visit: `https://your-frontend.onrender.com`
2. Should load without CORS errors
3. Try uploading a file to test functionality

## 🐛 Troubleshooting

### SpaCy Model Issues
- Check build logs for SpaCy download errors
- Verify `SPACY_MODEL=en_core_web_sm` is set
- Build script automatically handles model installation

### Database Connection
- Ensure `DATABASE_URL` is correctly set
- Check Neon database is active
- Verify connection string format

### CORS Errors
- Update `ALLOWED_ORIGINS` with correct frontend URL
- Ensure no trailing slashes in URLs
- Redeploy backend after changes

## 📊 Render Advantages

- **Free Tier**: Good for development and testing
- **Auto-scaling**: Handles traffic spikes
- **SSL**: Automatic HTTPS certificates
- **Git Integration**: Auto-deploy on push
- **Build Scripts**: Custom build processes supported

## 🎯 Next Steps

1. Deploy backend to Render
2. Note the backend URL
3. Update frontend environment variables
4. Deploy frontend to Render
5. Test complete application

Your Contact Management System will be fully deployed on Render cloud!
