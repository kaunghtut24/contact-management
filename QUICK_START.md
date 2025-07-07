# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- Conda (recommended)

## 1. Clone Repository
```bash
git clone https://github.com/kaunghtut24/contact-management.git
cd contact-management
```

## 2. Backend Setup
```bash
cd backend

# Create conda environment
conda create -n contact-management python=3.9
conda activate contact-management

# Install dependencies
pip install -r requirements.txt

# Install SpaCy English model
python -m spacy download en_core_web_sm

# Initialize database
python init_database.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Frontend Setup (New Terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start frontend server
npm run dev
```

## 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ✨ New Features to Test

### Selection & Batch Operations
1. Select individual contacts using checkboxes
2. Use "Select All" checkbox in header
3. Try "Export Selected" and "Delete Selected" buttons

### Enhanced Columns
- **Address Column**: View and edit contact addresses
- **Notes Column**: Additional contact information
- **Horizontal Scrolling**: Scroll to see all columns

### File Import
- Upload CSV, TXT, PDF, DOCX, Excel files
- Automatic categorization using SpaCy NLP
- Address and notes populated from parsing

## 🎯 Key Features
- ✅ Selection system with batch operations
- ✅ Address and Notes columns
- ✅ Horizontal scrolling with sticky columns
- ✅ SpaCy NLP categorization
- ✅ Multi-format file import
- ✅ Enhanced search and filtering
- ✅ Responsive design

## 🔧 Troubleshooting

**Backend Issues:**
- Ensure conda environment is activated
- Check if SpaCy model is installed: `python -c "import spacy; spacy.load('en_core_web_sm')"`

**Frontend Issues:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version`

**Database Issues:**
- Delete database file and re-run: `rm contact_db.sqlite && python init_database.py`

## 📞 Support
Open an issue on GitHub for support.
