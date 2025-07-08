# 🚀 Vercel Deployment Fix Guide

## Issues Identified

Based on your configuration, here are the main issues preventing proper deployment:

### 1. CORS Configuration Mismatch
- Your backend `.env` had incorrect CORS origins
- Frontend URL wasn't included in ALLOWED_ORIGINS

### 2. Database Configuration Issue
- SQLite doesn't work on Vercel's serverless environment
- Need to use PostgreSQL, MySQL, or a cloud database

### 3. Environment Variables Mismatch
- Frontend and backend URLs need to match exactly
- Environment variables need to be set correctly in Vercel dashboard

## 🔧 Step-by-Step Fix

### Step 1: Update Backend Environment Variables in Vercel

Go to your backend Vercel project → Settings → Environment Variables and set:

```bash
# Database - Use a cloud database (not SQLite)
DATABASE_URL=postgresql://username:password@host:port/database_name

# CORS - Include your frontend URL
ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app,http://localhost:5173

# Server Configuration
HOST=0.0.0.0
PORT=8000

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/tmp/uploads/

# OCR
TESSERACT_PATH=/usr/bin/tesseract

# Production
ENVIRONMENT=production
DEBUG=false
```

### Step 2: Update Frontend Environment Variables in Vercel

Go to your frontend Vercel project → Settings → Environment Variables and set:

```bash
# Backend API URL - Use your actual backend URL
VITE_API_BASE_URL=https://contact-management-vi36.vercel.app
```

### Step 3: Database Setup

Since SQLite doesn't work on Vercel, you need a cloud database:

#### Option A: Supabase (Free tier available)
1. Create account at https://supabase.com
2. Create new project
3. Get connection string from Settings → Database
4. Update DATABASE_URL in backend Vercel environment variables

#### Option B: Railway (Free tier available)
1. Create account at https://railway.app
2. Create PostgreSQL database
3. Get connection string
4. Update DATABASE_URL in backend Vercel environment variables

#### Option C: Neon (Free tier available)
1. Create account at https://neon.tech
2. Create database
3. Get connection string
4. Update DATABASE_URL in backend Vercel environment variables

### Step 4: Redeploy Both Projects

1. **Backend**: Trigger a new deployment in Vercel dashboard
2. **Frontend**: Trigger a new deployment in Vercel dashboard

### Step 5: Test the Connection

1. Visit your frontend URL: `https://contact-management-six-alpha.vercel.app`
2. Check browser console for any CORS errors
3. Try uploading a file to test backend connectivity
4. Check Vercel function logs for any errors

## 🐛 Common Issues and Solutions

### Issue: "CORS Error"
**Solution**: Ensure ALLOWED_ORIGINS in backend includes exact frontend URL (with https://)

### Issue: "Database Connection Error"
**Solution**: 
- Verify DATABASE_URL is correct
- Ensure database is accessible from Vercel
- Check database credentials

### Issue: "Function Timeout"
**Solution**: 
- Increase maxDuration in vercel.json (already updated)
- Optimize database queries
- Consider using Vercel Pro for longer timeouts

### Issue: "File Upload Fails"
**Solution**: 
- Vercel serverless functions have limited storage
- Consider using cloud storage (AWS S3, Cloudinary)
- Files in /tmp are temporary

## 📋 Verification Checklist

- [ ] Backend environment variables updated in Vercel
- [ ] Frontend environment variables updated in Vercel
- [ ] Database connection string is valid
- [ ] CORS origins include frontend URL
- [ ] Both projects redeployed
- [ ] Frontend can connect to backend API
- [ ] File upload works (if using cloud storage)
- [ ] Database operations work

## 🔗 Your Current URLs

- **Frontend**: https://contact-management-six-alpha.vercel.app
- **Backend**: https://contact-management-vi36.vercel.app
- **API Docs**: https://contact-management-vi36.vercel.app/docs

## 📞 Next Steps

1. Set up a cloud database (recommended: Supabase)
2. Update environment variables in both Vercel projects
3. Redeploy both projects
4. Test the application

Let me know if you need help with any of these steps!
