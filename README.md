# 🔐 Contact Management System

A secure, full-stack contact management system with JWT authentication, OCR capabilities, and modern web interface.

## ✨ Features

- **🔐 Secure Authentication**: JWT-based authentication with role-based access control
- **📱 Modern UI**: React frontend with Tailwind CSS
- **🔍 Advanced Search**: Search and filter contacts by multiple criteria
- **📄 OCR Support**: Extract contacts from images and documents using Tesseract OCR
- **🤖 NLP Processing**: Automatic contact categorization using SpaCy
- **📊 Batch Operations**: Bulk delete and export functionality
- **🌐 Production Ready**: Deployed on Render (backend) and Vercel (frontend)

## 🏗️ Architecture

- **Frontend**: React + Vite + Tailwind CSS (Deployed on Vercel)
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (Deployed on Render)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Database**: PostgreSQL (Neon) with SSL connections
- **OCR**: Tesseract OCR with Python integration
- **NLP**: SpaCy for contact categorization

## 🚀 Live Demo

- **Frontend**: [https://contact-management-six-alpha.vercel.app](https://contact-management-six-alpha.vercel.app)
- **Backend API**: [https://contact-management-ffsl.onrender.com](https://contact-management-ffsl.onrender.com)
- **API Documentation**: [https://contact-management-ffsl.onrender.com/docs](https://contact-management-ffsl.onrender.com/docs)

## 🔑 Default Credentials

The system uses environment variables for secure credential management. Contact your administrator for login credentials.

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL database
- Tesseract OCR (for document processing)

## 🛠️ Local Development Setup

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaunghtut24/contact-management.git
   cd contact-management/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Install Tesseract OCR**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

5. **Set environment variables**
   ```bash
   export JWT_SECRET_KEY="your-secret-key-here"
   export ADMIN_USERNAME="admin"
   export ADMIN_EMAIL="admin@example.com"
   export ADMIN_PASSWORD="your-secure-password"
   export DATABASE_URL="sqlite:///./contact_management.sqlite"
   ```

6. **Run the backend**
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set environment variables**
   ```bash
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

## 🌐 Production Deployment

### Backend (Render)

1. **Fork this repository**
2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Create new Web Service
   - Connect your GitHub repository
   - Select `production` branch

3. **Configure Environment Variables**
   ```bash
   JWT_SECRET_KEY=your-32-character-secret-key
   ADMIN_USERNAME=admin
   ADMIN_EMAIL=admin@yourcompany.com
   ADMIN_PASSWORD=YourSecurePassword123!
   DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require
   ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
   TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
   TESSERACT_PATH=/usr/bin/tesseract
   ```

4. **Deploy**
   - Render will automatically build and deploy using `build.sh`
   - Tesseract OCR will be installed during build process

### Frontend (Vercel)

1. **Connect to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Import your GitHub repository
   - Select `main` branch

2. **Configure Environment Variables**
   ```bash
   VITE_API_BASE_URL=https://your-backend.onrender.com
   ```

3. **Deploy**
   - Vercel will automatically build and deploy

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes | - |
| `ADMIN_USERNAME` | Admin username | Yes | admin |
| `ADMIN_EMAIL` | Admin email | Yes | - |
| `ADMIN_PASSWORD` | Admin password | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `ALLOWED_ORIGINS` | CORS allowed origins | Yes | - |
| `TESSERACT_PATH` | Path to Tesseract binary | No | /usr/bin/tesseract |
| `TESSDATA_PREFIX` | Tesseract data directory | No | /usr/share/tesseract-ocr/4.00/tessdata/ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | No | 30 |

### Security Features

- **Password Hashing**: bcrypt with 12 rounds
- **JWT Tokens**: HS256 algorithm with configurable expiry
- **Role-Based Access**: Admin, User, and Viewer roles
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## 📚 API Documentation

The API documentation is automatically generated and available at:
- Local: http://localhost:8000/docs
- Production: https://contact-management-ffsl.onrender.com/docs

### Key Endpoints

- `POST /auth/login/simple` - User authentication
- `GET /auth/me` - Get current user info
- `POST /auth/create-admin` - Create admin user (one-time)
- `GET /contacts` - List contacts with search/filter
- `POST /contacts` - Create new contact
- `PUT /contacts/{id}` - Update contact
- `DELETE /contacts/{id}` - Delete contact
- `GET /export` - Export contacts to CSV
- `POST /upload` - Upload and parse contact files

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation
- Review the deployment guides in the repository

## 🔄 Updates

- **v2.0.0**: Added JWT authentication and security features
- **v1.5.0**: Implemented OCR and NLP processing
- **v1.0.0**: Initial release with basic contact management
