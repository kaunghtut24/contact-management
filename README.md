# Contact Management System

A comprehensive full-stack application for managing contacts with advanced file import capabilities, intelligent categorization, and a modern responsive interface.

## 🌟 Features

### Core Functionality
- **Multi-format File Import**: Support for CSV, Excel, PDF, DOCX, TXT files
- **Intelligent Categorization**: Automatic contact categorization using SpaCy NLP
- **Full CRUD Operations**: Create, read, update, and delete contacts
- **Advanced Search & Filtering**: Search by name, email, phone, or category
- **Data Export**: Export contacts to CSV format

### Enhanced Features ✨
- **Selection System**: Individual and batch contact selection with checkboxes
- **Batch Operations**: Delete or export multiple contacts at once
- **Address Management**: Dedicated address field for contact locations
- **Notes System**: Additional information storage for contacts
- **Horizontal Scrolling**: Responsive table with sticky selection and action columns

### AI-Powered Features 🤖
- **SpaCy NLP Integration**: Advanced natural language processing
- **Smart Categorization**: Context-aware business category assignment
- **Intelligent File Parsing**: Extract structured data from unstructured text

### UI/UX Features
- **Responsive Design**: Modern UI built with React and Tailwind CSS
- **Input Validation**: Comprehensive client and server-side validation
- **Error Handling**: Robust error handling with user-friendly messages
- **Loading States**: Proper feedback during operations

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```batch
setup.bat
```

### Option 2: Manual Setup

#### Prerequisites

- Python 3.9+
- Node.js 16+
- Conda (recommended for Python environment management)
- SpaCy English model (en_core_web_sm)

#### Backend Setup

1. **Create and activate conda environment:**
   ```bash
   cd backend
   conda create -n contact-management python=3.9
   conda activate contact-management
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install SpaCy English model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Initialize database:**
   ```bash
   python init_database.py
   ```

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - API Documentation: http://localhost:8000/docs

### Option 3: Docker Deployment

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
contact-management-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── main.py         # FastAPI application
│   │   ├── database.py     # Database configuration
│   │   ├── config.py       # Application settings
│   │   ├── exceptions.py   # Custom exceptions
│   │   ├── validators.py   # Input validation
│   │   ├── parsers/        # File parsing modules
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Docker configuration
│   └── .env.example       # Environment template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── utils/          # Utility functions
│   │   ├── pages/          # Page components
│   │   └── styles.css      # Global styles
│   ├── package.json        # Node.js dependencies
│   ├── Dockerfile         # Docker configuration
│   └── nginx.conf         # Nginx configuration
├── docker-compose.yml      # Docker Compose configuration
├── setup.sh               # Linux/macOS setup script
├── setup.bat              # Windows setup script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/contact_db

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=uploads/

# OCR Configuration
TESSERACT_PATH=/usr/bin/tesseract
```

### Supported File Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| CSV | `.csv` | Comma-separated values |
| Excel | `.xlsx`, `.xls` | Microsoft Excel files |
| PDF | `.pdf` | Portable Document Format |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| Images | `.jpg`, `.jpeg`, `.png` | Image files (OCR) |

## 📊 API Endpoints

### Contacts
- `GET /contacts` - List all contacts with optional search and filtering
- `GET /contacts/{id}` - Get a specific contact
- `POST /contacts` - Create a new contact
- `PUT /contacts/{id}` - Update a contact
- `DELETE /contacts/{id}` - Delete a contact

### Batch Operations ✨
- `DELETE /contacts/batch` - Delete multiple contacts
- `POST /export/batch` - Export selected contacts to CSV

### File Operations
- `POST /upload` - Upload and parse a file
- `GET /export` - Export all contacts to CSV

### System
- `GET /health` - Health check endpoint
- `GET /docs` - API documentation (Swagger UI)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚢 Deployment

### Production Build

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🛠️ Development

### Adding New File Parsers

1. Create a new parser function in `backend/app/parsers/parse.py`
2. Add the file extension to the validation logic
3. Update the upload endpoint to handle the new format

### Customizing Contact Categories

Update the categories in:
- `backend/app/utils/nlp.py` - Server-side categorization logic
- `frontend/src/utils/constants.js` - Client-side category list

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error:**
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists

**File Upload Fails:**
- Check file size limits
- Ensure Tesseract is installed for image files
- Verify file format is supported

**Frontend Build Issues:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version compatibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ using FastAPI, React, and PostgreSQL**
