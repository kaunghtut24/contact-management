# 🚀 Local Development Guide

This guide will help you set up the Contact Management System for local development.

## 📋 Prerequisites

- **Python 3.9+** with pip
- **Node.js 16+** with npm
- **Git**
- **Conda** (recommended) or virtualenv

## 🛠️ Backend Setup

### 1. Clone Repository
```bash
git clone https://github.com/kaunghtut24/contact-management.git
cd contact-management-system
```

### 2. Create Conda Environment
```bash
# Create conda environment
conda create -n contact-management python=3.9
conda activate contact-management

# Or use venv
python -m venv contact-management
source contact-management/bin/activate  # Linux/Mac
# contact-management\Scripts\activate  # Windows
```

### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt

# Install additional OCR dependencies
pip install pytesseract pillow

# Install spaCy model for NLP
python -m spacy download en_core_web_sm
```

### 4. Install Tesseract OCR
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 5. Configure Environment Variables
Create `backend/.env` file:
```env
# Database Configuration
DATABASE_URL=sqlite:///./contact_management_local.sqlite

# JWT Configuration
JWT_SECRET_KEY=local-development-secret-key-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Admin User Configuration
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@localhost.dev
ADMIN_PASSWORD=LocalAdmin123!

# Environment
ENVIRONMENT=development

# CORS Configuration (for development)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# OCR Configuration
TESSDATA_PREFIX=./tessdata
```

### 6. Start Backend Server
```bash
# Using the provided script
chmod +x ../start_local_dev.sh
../start_local_dev.sh

# Or manually
export DATABASE_URL="sqlite:///./contact_management_local.sqlite"
export JWT_SECRET_KEY="local-development-secret-key-32-characters-long"
export ADMIN_USERNAME="admin"
export ADMIN_EMAIL="admin@localhost.dev"
export ADMIN_PASSWORD="LocalAdmin123!"
export ENVIRONMENT="development"

python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Create Admin User
```bash
curl -X POST "http://localhost:8000/auth/create-admin"
```

## 🎨 Frontend Setup

### 1. Install Dependencies
```bash
cd ../frontend
npm install
```

### 2. Configure Environment
Create `frontend/.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Frontend Server
```bash
npm run dev
```

## 🔧 Development Workflow

### Backend Development
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: SQLite file in backend directory
- **Hot Reload**: Enabled with `--reload` flag

### Frontend Development
- **Dev Server**: http://localhost:5173
- **Hot Reload**: Enabled by default
- **API Calls**: Configured to use localhost:8000

### Admin Credentials
```
Username: admin
Password: LocalAdmin123!
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Test API endpoints
curl -X POST "http://localhost:8000/auth/login/simple" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "LocalAdmin123!"}'

# Test OCR status
curl "http://localhost:8000/ocr/status"
```

### Frontend Testing
```bash
cd frontend

# Run tests (if available)
npm test

# Build for production testing
npm run build
npm run preview
```

## 🔍 Troubleshooting

### Common Issues

**1. CORS Errors**
- Ensure `ENVIRONMENT=development` is set
- Check frontend is running on port 5173
- Verify backend CORS configuration

**2. Database Issues**
- Delete SQLite file and restart backend
- Check file permissions in backend directory

**3. OCR Not Working**
- Verify Tesseract installation: `tesseract --version`
- Check tessdata files in `backend/tessdata/`
- Ensure TESSDATA_PREFIX is set correctly

**4. Import Errors**
- Activate conda environment
- Reinstall requirements: `pip install -r requirements.txt`
- Install missing packages individually

**5. Port Conflicts**
- Backend: Change port in uvicorn command
- Frontend: Use `npm run dev -- --port 3000`

### Debug Commands
```bash
# Check Python environment
which python
pip list

# Check Node environment
which node
npm list

# Check running processes
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port

# Check environment variables
env | grep -E "(DATABASE_URL|JWT_SECRET|ENVIRONMENT)"
```

## 📁 Project Structure
```
contact-management-system/
├── backend/
│   ├── api.py              # Main FastAPI application
│   ├── app/
│   │   └── parsers/
│   │       └── parse.py    # OCR and file parsing
│   ├── tessdata/           # Bundled Tesseract data
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── utils/         # API utilities
│   │   └── App.jsx        # Main app component
│   ├── package.json       # Node dependencies
│   └── .env.local         # Frontend environment
└── start_local_dev.sh     # Development startup script
```

## 🚀 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test File Upload**: Try uploading business cards
3. **Check OCR**: Test image processing functionality
4. **Customize**: Modify components and API endpoints
5. **Deploy**: Follow the Production Deployment Guide

## 📞 Support

- **GitHub Issues**: https://github.com/kaunghtut24/contact-management/issues
- **Documentation**: Check API docs at /docs endpoint
- **Logs**: Check terminal output for detailed error messages
