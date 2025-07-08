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

# Create necessary directories
mkdir -p uploads
mkdir -p logs

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
