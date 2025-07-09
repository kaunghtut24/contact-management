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
import shutil
try:
    import pytesseract
    from PIL import Image

    def find_tesseract():
        # Try environment variable first
        env_path = os.getenv('TESSERACT_PATH')
        if env_path and os.path.isfile(env_path):
            return env_path

        # Try shutil.which (Python's built-in)
        which_result = shutil.which('tesseract')
        if which_result:
            return which_result

        # Common Tesseract paths to try
        common_paths = ['/usr/bin/tesseract', '/usr/local/bin/tesseract']
        for path in common_paths:
            if os.path.isfile(path):
                return path
        return None

    tesseract_path = find_tesseract()

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f'🔧 Found Tesseract at: {tesseract_path}')

        # Test tesseract
        version = pytesseract.get_tesseract_version()
        print(f'✅ Tesseract OCR available: {version}')
    else:
        print('⚠️  Tesseract not found - OCR will be disabled')

except ImportError as e:
    print(f'⚠️  OCR dependencies missing: {e}')
    print('   Install with: pip install pytesseract pillow')
except Exception as e:
    print(f'⚠️  Tesseract configuration error: {e}')
    print('   OCR will be disabled')
"

# Create necessary directories
mkdir -p uploads
mkdir -p logs

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
