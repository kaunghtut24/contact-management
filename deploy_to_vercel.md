# 🚀 Complete Vercel Deployment Guide

## Current Configuration Summary

- **Frontend URL**: https://contact-management-six-alpha.vercel.app
- **Backend URL**: https://contact-management-vi36.vercel.app  
- **Database**: Neon PostgreSQL (already configured with tables)

## 🔧 Step 1: Backend Deployment

### Environment Variables for Backend Vercel Project

Set these in your backend Vercel project → Settings → Environment Variables:

```bash
DATABASE_URL=postgresql://neondb_owner:npg_oCyiNY6RD4gF@ep-white-river-a8irxian-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app,http://localhost:5173
HOST=0.0.0.0
PORT=8000
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/tmp/uploads/
TESSERACT_PATH=/usr/bin/tesseract
ENVIRONMENT=production
DEBUG=false
```

## 🎨 Step 2: Frontend Deployment

### Environment Variables for Frontend Vercel Project

Set these in your frontend Vercel project → Settings → Environment Variables:

```bash
VITE_API_BASE_URL=https://contact-management-vi36.vercel.app
```

## 🔄 Step 3: Redeploy Both Projects

1. **Backend**: Go to Vercel dashboard → Backend project → Deployments → Click "Redeploy" on latest
2. **Frontend**: Go to Vercel dashboard → Frontend project → Deployments → Click "Redeploy" on latest

## ✅ Step 4: Verification

### Test Backend API
```bash
curl https://contact-management-vi36.vercel.app/health
```
Expected response: `{"status":"healthy","message":"Contact Management System API is running"}`

### Test Frontend
1. Visit: https://contact-management-six-alpha.vercel.app
2. Open browser dev tools → Console (should have no CORS errors)
3. Try uploading a test file
4. Verify contacts are displayed

### Test API Documentation
Visit: https://contact-management-vi36.vercel.app/docs

## 🐛 Troubleshooting

### CORS Errors
- Ensure ALLOWED_ORIGINS exactly matches frontend URL
- No trailing slashes in URLs
- Redeploy backend after environment variable changes

### Database Connection Issues
- Verify Neon database is active (not sleeping)
- Check DATABASE_URL is exactly correct
- Review Vercel function logs for detailed errors

### Frontend API Connection Issues
- Verify VITE_API_BASE_URL matches backend URL exactly
- Check browser Network tab for failed requests
- Ensure backend health endpoint responds

## 📋 Files Updated in This Fix

- ✅ `backend/.env` - Updated with Neon PostgreSQL
- ✅ `backend/.env.production` - Fixed for Neon instead of PlanetScale  
- ✅ `backend/.env.vercel` - Template with correct values
- ✅ `frontend/.env` - Local development configuration
- ✅ `frontend/.env.production` - Production configuration
- ✅ `frontend/.env.example` - Template for environment variables
- ✅ `docker-compose.yml` - Fixed environment variable syntax
- ❌ `frontend/src/api.js` - Removed duplicate API configuration

## 🎯 Success Checklist

- [ ] Backend environment variables updated in Vercel
- [ ] Frontend environment variables updated in Vercel  
- [ ] Both projects redeployed
- [ ] Backend health endpoint responds
- [ ] Frontend loads without console errors
- [ ] API documentation accessible
- [ ] File upload functionality works
- [ ] Contacts display properly
- [ ] Database operations successful

## 📞 Next Steps After Deployment

1. Test all functionality thoroughly
2. Monitor Vercel function logs for any errors
3. Consider setting up monitoring/alerting
4. Document any additional configuration needed
