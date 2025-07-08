#!/bin/bash

# Build script for Render cloud deployment
# This script will be executed during the build process

echo "🚀 Starting Render build process..."

# Install system dependencies for OCR
echo "🔧 Installing system dependencies..."
# Note: Render should automatically install packages from aptfile
# If aptfile doesn't work, try manual installation
if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    apt-get install -y tesseract-ocr tesseract-ocr-eng
else
    echo "⚠️  apt-get not available, relying on aptfile for system dependencies"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download SpaCy English model
echo "🧠 Downloading SpaCy English model..."
python -m spacy download en_core_web_sm --user

# Alternative installation method if the first fails
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "🔄 Trying alternative SpaCy installation..."
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
fi

# Verify SpaCy model installation
echo "✅ Verifying SpaCy model installation..."
python -c "
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
    print('✅ SpaCy model loaded successfully')
except OSError:
    print('⚠️  SpaCy model not found, but installation completed')
    print('Model will be downloaded at runtime if needed')
"

# Verify Tesseract installation
echo "🔍 Verifying Tesseract installation..."
if command -v tesseract >/dev/null 2>&1; then
    tesseract --version
    echo "✅ Tesseract is available"
else
    echo "⚠️  Tesseract not found in PATH - OCR will be disabled"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x build.sh

echo "🎉 Build process completed successfully!"
