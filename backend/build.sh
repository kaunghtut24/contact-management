#!/bin/bash

# Build script for Render cloud deployment
# This script will be executed during the build process

echo "🚀 Starting Render build process..."

# Install system dependencies for OCR
echo "🔧 Installing system dependencies..."
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download SpaCy English model
echo "🧠 Downloading SpaCy English model..."
python -m spacy download en_core_web_sm

# Verify SpaCy model installation
echo "✅ Verifying SpaCy model installation..."
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('SpaCy model loaded successfully')"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x build.sh

echo "🎉 Build process completed successfully!"
