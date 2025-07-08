#!/bin/bash

# Startup script for Render deployment
# This ensures SpaCy model is available before starting the app

echo "🚀 Starting Contact Management API..."

# Check if SpaCy model is available
echo "🧠 Checking SpaCy model availability..."
python -c "
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
    print('✅ SpaCy model is available')
except OSError:
    print('❌ SpaCy model not found, downloading...')
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    print('✅ SpaCy model downloaded')
"

# Check OCR availability
echo "🔍 Checking OCR dependencies..."
python -c "
import os
try:
    import pytesseract
    from PIL import Image

    # Configure tesseract path
    tesseract_path = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f'🔧 Tesseract path: {tesseract_path}')

    # Test tesseract
    version = pytesseract.get_tesseract_version()
    print(f'✅ Tesseract OCR available: {version}')

except ImportError as e:
    print(f'⚠️  OCR dependencies missing: {e}')
    print('Image parsing will be disabled')
except Exception as e:
    print(f'⚠️  Tesseract configuration error: {e}')
    print('Image parsing will be disabled')
"

# Create necessary directories
mkdir -p uploads
mkdir -p logs

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
