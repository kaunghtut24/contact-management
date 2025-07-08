# 🚀 Vercel Deployment Checklist

## Your Configuration

- **Frontend URL**: https://contact-management-six-alpha.vercel.app
- **Backend URL**: https://contact-management-vi36.vercel.app
- **Database**: Neon PostgreSQL (already set up with tables)

## ✅ Deployment Steps

### 1. Backend Environment Variables (Vercel Dashboard)

Go to your backend project → Settings → Environment Variables:

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

### 2. Frontend Environment Variables (Vercel Dashboard)

Go to your frontend project → Settings → Environment Variables:

```bash
VITE_API_BASE_URL=https://contact-management-vi36.vercel.app
```

### 3. Redeploy Projects

1. **Backend**: Go to Deployments tab → Click "Redeploy" on latest deployment
2. **Frontend**: Go to Deployments tab → Click "Redeploy" on latest deployment

### 4. Test Your Application

1. Visit: https://contact-management-six-alpha.vercel.app
2. Check browser console for errors
3. Try uploading a file
4. Verify contacts are displayed
5. Check API docs: https://contact-management-vi36.vercel.app/docs

## 🔍 Troubleshooting

### If you get CORS errors:
- Verify ALLOWED_ORIGINS includes your exact frontend URL
- Make sure there are no trailing slashes
- Redeploy backend after changing environment variables

### If database connection fails:
- Check DATABASE_URL is exactly as provided
- Ensure Neon database is active (not sleeping)
- Check Vercel function logs for detailed errors

### If frontend can't reach backend:
- Verify VITE_API_BASE_URL is correct
- Check network tab in browser dev tools
- Ensure backend is deployed and responding

## 📊 Verification Commands

Test locally before deploying:
```bash
cd backend
python test_neon_connection.py
```

Check API health:
```bash
curl https://contact-management-vi36.vercel.app/health
```

## 🎯 Success Indicators

- [ ] Backend environment variables set
- [ ] Frontend environment variables set
- [ ] Both projects redeployed
- [ ] Frontend loads without console errors
- [ ] API endpoints respond correctly
- [ ] File upload works
- [ ] Contacts display properly
- [ ] Database operations work

## 📞 If Issues Persist

1. Check Vercel function logs (Functions tab in dashboard)
2. Test API endpoints directly: https://contact-management-vi36.vercel.app/docs
3. Verify database connection from Neon dashboard
4. Check browser network tab for failed requests
