# 🚀 Deployment Guide: Vercel + PlanetScale

This guide will help you deploy your Contact Management System to Vercel with PlanetScale database.

## 📋 Prerequisites

- GitHub account
- Vercel account (free)
- PlanetScale account (free)

## 🗄️ Step 1: Setup PlanetScale Database

### 1.1 Create PlanetScale Account
1. Go to [PlanetScale](https://planetscale.com)
2. Sign up for free account
3. Create new database: `contact-management`

### 1.2 Get Connection String
1. In PlanetScale dashboard, go to your database
2. Click "Connect" → "Create password"
3. Select "General" connection
4. Copy the connection string (looks like):
   ```
   mysql://username:password@host:port/database_name?sslaccept=strict
   ```

### 1.3 Initialize Database Schema
```bash
# Set your PlanetScale connection string
export DATABASE_URL="mysql://your-connection-string"

# Run migration script
cd backend
python migrate_to_mysql.py
```

## 🌐 Step 2: Deploy Backend to Vercel

### 2.1 Deploy Backend
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Select the `backend` folder as root directory
5. Click "Deploy"

### 2.2 Configure Environment Variables
In Vercel dashboard → Project → Settings → Environment Variables:

```bash
DATABASE_URL=mysql://your-planetscale-connection-string
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/tmp/uploads/
ENVIRONMENT=production
```

### 2.3 Get Backend URL
After deployment, copy your backend URL:
```
https://your-backend-abc123.vercel.app
```

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Deploy Frontend
1. In Vercel dashboard, click "New Project"
2. Import the same GitHub repository
3. Select the `frontend` folder as root directory
4. Set build command: `npm run build`
5. Set output directory: `dist`
6. Click "Deploy"

### 3.2 Configure Environment Variables
In Vercel dashboard → Project → Settings → Environment Variables:

```bash
VITE_API_BASE_URL=https://your-backend-abc123.vercel.app
```

## 🔗 Step 4: Connect Frontend and Backend

### 4.1 Update CORS Settings
1. Go to backend Vercel project
2. Update `ALLOWED_ORIGINS` environment variable:
   ```
   https://your-frontend-xyz789.vercel.app,http://localhost:5173
   ```

### 4.2 Test Connection
1. Visit your frontend URL
2. Try creating a contact
3. Check if data appears in PlanetScale dashboard

## ✅ Step 5: Verification Checklist

- [ ] PlanetScale database created and connected
- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Contact creation works
- [ ] File upload works
- [ ] Batch operations work

## 🔧 Troubleshooting

### Backend Issues
**Error: "Database connection failed"**
- Check DATABASE_URL format
- Ensure PlanetScale database is active
- Verify connection string has SSL parameters

**Error: "Module not found"**
- Check requirements.txt includes all dependencies
- Redeploy backend after updating requirements

### Frontend Issues
**Error: "API calls failing"**
- Check VITE_API_BASE_URL is correct
- Verify CORS settings in backend
- Check browser network tab for errors

**Error: "Build failed"**
- Ensure all dependencies in package.json
- Check for TypeScript/ESLint errors

### Database Issues
**Error: "Table doesn't exist"**
- Run migration script: `python migrate_to_mysql.py`
- Check PlanetScale dashboard for tables

## 📊 Production URLs

After successful deployment:

- **Frontend**: `https://your-frontend.vercel.app`
- **Backend**: `https://your-backend.vercel.app`
- **API Docs**: `https://your-backend.vercel.app/docs`
- **Database**: PlanetScale dashboard

## 🎯 Performance Tips

1. **Enable Vercel Analytics** for monitoring
2. **Use Vercel Edge Functions** for better performance
3. **Configure caching** for static assets
4. **Monitor PlanetScale** usage and performance

## 💰 Cost Estimation

- **Vercel**: Free for personal projects
- **PlanetScale**: Free tier (1GB storage, 1B row reads/month)
- **Total**: $0/month for small applications

## 🆘 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check PlanetScale connection status
3. Review environment variables
4. Open GitHub issue for help

---

**🎉 Congratulations! Your Contact Management System is now live!**
