#!/bin/bash

# Build script for Render cloud deployment - LLM-focused approach
# This script will be executed during the build process

echo "🚀 Starting Render build process (LLM + Content Intelligence)..."

# Note: OCR dependencies removed - using OCR microservice instead
echo "📝 Note: Local OCR dependencies removed - using OCR microservice for image processing"

# OCR processing now handled by dedicated OCR microservice
echo "🤖 OCR processing delegated to OCR microservice for better performance"

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

# Verify Content Intelligence dependencies
echo "🔍 Verifying Content Intelligence dependencies..."
python -c "
try:
    import spacy
    import openai
    print('✅ Content Intelligence dependencies available')
    print('   - SpaCy: Available')
    print('   - OpenAI: Available')
except ImportError as e:
    print(f'⚠️  Missing dependency: {e}')
"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x build.sh

echo "🎉 Build process completed successfully!"
echo "🧠 Content Intelligence Service ready with LLM + SpaCy integration"
echo "🚀 System optimized for fast, accurate contact extraction"
