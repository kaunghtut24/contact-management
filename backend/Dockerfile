FROM python:3.9-slim

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Find and set correct Tesseract data path
RUN find /usr -name "*.traineddata" -type f 2>/dev/null | head -1 | xargs dirname > /tmp/tessdata_path || echo "/usr/share/tesseract-ocr/tessdata" > /tmp/tessdata_path

# Set Tesseract environment variables with dynamic path detection
ENV TESSERACT_PATH=/usr/bin/tesseract
RUN export TESSDATA_PREFIX=$(cat /tmp/tessdata_path) && \
    echo "TESSDATA_PREFIX=$TESSDATA_PREFIX" >> /etc/environment && \
    echo "Found Tesseract data at: $TESSDATA_PREFIX" && \
    ls -la $TESSDATA_PREFIX/ || echo "Tessdata directory not found, will use default"

# Set fallback environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download SpaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]