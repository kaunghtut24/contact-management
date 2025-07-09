#!/bin/bash

# Build script for Render cloud deployment
# This script will be executed during the build process

echo "🚀 Starting Render build process..."

# Install system dependencies for OCR
echo "🔧 Installing system dependencies..."

# Install Tesseract OCR if not available
if command -v tesseract >/dev/null 2>&1; then
    echo "✅ Tesseract already available: $(tesseract --version | head -1)"
else
    echo "📦 Installing Tesseract OCR..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update
        apt-get install -y tesseract-ocr tesseract-ocr-eng
        echo "✅ Tesseract installed successfully"
    else
        echo "⚠️  apt-get not available, relying on aptfile for installation"
    fi
fi

# Verify Tesseract installation and set environment
if command -v tesseract >/dev/null 2>&1; then
    TESSERACT_VERSION=$(tesseract --version | head -1)
    echo "✅ Tesseract verified: $TESSERACT_VERSION"

    # Find correct Tesseract data path
    echo "🔍 Finding Tesseract data directory..."

    # Try common locations for tessdata
    TESSDATA_PATHS=(
        "/usr/share/tesseract-ocr/tessdata"
        "/usr/share/tesseract-ocr/4.00/tessdata"
        "/usr/share/tesseract-ocr/5.00/tessdata"
        "/usr/share/tessdata"
        "/usr/local/share/tessdata"
    )

    TESSDATA_PREFIX=""
    for path in "${TESSDATA_PATHS[@]}"; do
        if [ -d "$path" ] && [ -f "$path/eng.traineddata" ]; then
            TESSDATA_PREFIX="$path"
            echo "✅ Found Tesseract data at: $TESSDATA_PREFIX"
            break
        fi
    done

    # If not found, try to find it dynamically
    if [ -z "$TESSDATA_PREFIX" ]; then
        echo "🔍 Searching for eng.traineddata file..."
        TESSDATA_FILE=$(find /usr -name "eng.traineddata" -type f 2>/dev/null | head -1)
        if [ -n "$TESSDATA_FILE" ]; then
            TESSDATA_PREFIX=$(dirname "$TESSDATA_FILE")
            echo "✅ Found Tesseract data at: $TESSDATA_PREFIX"
        else
            echo "⚠️  Could not find Tesseract data files"
            TESSDATA_PREFIX="/usr/share/tesseract-ocr/tessdata"
        fi
    fi

    # Set Tesseract environment variables
    export TESSERACT_PATH=/usr/bin/tesseract
    export TESSDATA_PREFIX="$TESSDATA_PREFIX"

    echo "🔧 Tesseract environment configured:"
    echo "   TESSERACT_PATH=$TESSERACT_PATH"
    echo "   TESSDATA_PREFIX=$TESSDATA_PREFIX"

    # List available language files
    echo "📋 Available Tesseract language files:"
    ls -la "$TESSDATA_PREFIX"/*.traineddata 2>/dev/null || echo "   No .traineddata files found"

else
    echo "⚠️  Tesseract installation failed - OCR will be disabled"
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
