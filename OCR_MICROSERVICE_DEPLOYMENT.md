# OCR Microservice Deployment Guide

## Overview

This solution separates OCR processing into a dedicated microservice to solve timeout issues and provide better scalability. The microservice can be deployed on Render, Vercel, or other platforms independently from the main application.

## Architecture

```
Frontend (Vercel) → Main Backend (Render) → OCR Microservice (Render/Vercel)
                                         ↓
                                    OpenAI API (optional)
```

## Features

### 🚀 **OCR Microservice Capabilities**
- **Multiple OCR Strategies**: Fast, Enhanced, and Fallback processing
- **Intelligent Preprocessing**: Automatic image optimization based on size
- **LLM Integration**: OpenAI-powered contact extraction and categorization
- **Async Processing**: Handle large files with background processing
- **Health Monitoring**: Built-in health checks and status endpoints
- **Timeout Management**: Proper timeout handling for different file sizes

### 📊 **Processing Methods**
1. **Sync Processing** (≤ 1MB files): Immediate response within 30 seconds
2. **Async Processing** (> 1MB files): Background processing with job polling

## Deployment Options

### Option 1: Render Deployment (Recommended)

#### 1. Create New Render Service
```bash
# Navigate to OCR service directory
cd ocr-service

# Initialize git repository
git init
git add .
git commit -m "Initial OCR microservice"

# Push to GitHub (create new repo: ocr-microservice)
git remote add origin https://github.com/yourusername/ocr-microservice.git
git push -u origin main
```

#### 2. Configure Render Service
- **Service Type**: Web Service
- **Environment**: Docker
- **Repository**: Your OCR microservice repo
- **Build Command**: Docker build
- **Start Command**: Automatic (from Dockerfile)

#### 3. Environment Variables
```bash
# Required
ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app,https://contact-management-ffsl.onrender.com

# Optional (for LLM features)
OPENAI_API_KEY=your_openai_api_key

# Service Configuration
PORT=8002
TESSERACT_PATH=/usr/bin/tesseract
TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
```

#### 4. Update Main Backend
Add to your main backend's environment variables:
```bash
OCR_SERVICE_URL=https://your-ocr-service.onrender.com
```

### Option 2: Vercel Deployment (Alternative)

#### 1. Deploy to Vercel
```bash
cd ocr-service
vercel --prod
```

#### 2. Configure Environment Variables in Vercel Dashboard
```bash
ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app,https://contact-management-ffsl.onrender.com
OPENAI_API_KEY=your_openai_api_key  # Optional
```

#### 3. Update Main Backend
```bash
OCR_SERVICE_URL=https://your-ocr-service.vercel.app
```

## Integration with Main Backend

### 1. Install HTTP Client
```bash
# Add to backend/requirements.txt
httpx==0.25.2
```

### 2. Update Upload Endpoint
The main backend will automatically use the OCR microservice when `OCR_SERVICE_URL` is configured.

### 3. Fallback Behavior
If OCR microservice is unavailable, the system falls back to local OCR processing (if available) or returns appropriate error messages.

## API Endpoints

### OCR Microservice Endpoints

#### `GET /`
Health check with service capabilities

#### `GET /health`
Detailed health status

#### `POST /process-sync`
Synchronous image processing (≤ 1MB files)
- **Input**: Multipart file upload
- **Output**: Immediate JSON response with contacts
- **Timeout**: 30 seconds

#### `POST /process-async`
Asynchronous image processing (> 1MB files)
- **Input**: Multipart file upload
- **Output**: Job ID for polling
- **Timeout**: Background processing up to 60 seconds

#### `GET /status/{job_id}`
Check async job status
- **Input**: Job ID from async endpoint
- **Output**: Job status and results (when complete)

## Performance Characteristics

### File Size Handling
- **< 1MB**: Sync processing, ~10-15 seconds
- **1-2MB**: Async processing, ~20-30 seconds
- **> 2MB**: Rejected with clear error message

### OCR Strategies
1. **Fast OCR**: Basic preprocessing, legacy engine (fastest)
2. **Enhanced OCR**: Better preprocessing, modern engine (better quality)
3. **Fallback OCR**: Different PSM mode for difficult images

### LLM Integration
- **With OpenAI**: Intelligent contact extraction and categorization
- **Without OpenAI**: Rule-based extraction (fallback)

## Monitoring and Troubleshooting

### Health Checks
```bash
# Check OCR service health
curl https://your-ocr-service.onrender.com/health

# Expected response
{
  "status": "healthy",
  "ocr_available": true,
  "llm_available": true,
  "job_queue_size": 0
}
```

### Common Issues

#### 1. Service Unavailable
- **Symptom**: "OCR microservice is not available"
- **Solution**: Check service deployment and health endpoint

#### 2. Timeout Issues
- **Symptom**: Processing times out
- **Solution**: Use async endpoint for larger files

#### 3. Poor OCR Quality
- **Symptom**: No text extracted or poor results
- **Solution**: Ensure images are clear, high-contrast, and properly oriented

## Cost Optimization

### Render Deployment
- **Starter Plan**: $7/month, suitable for moderate usage
- **Standard Plan**: $25/month, better performance for high usage

### Vercel Deployment
- **Hobby Plan**: Free tier with function limits
- **Pro Plan**: $20/month with higher limits

### OpenAI Integration
- **Optional**: Can be disabled to reduce costs
- **Usage**: ~$0.001-0.01 per image processed

## Security Considerations

1. **CORS Configuration**: Restrict origins to your domains
2. **API Keys**: Store OpenAI API key securely in environment variables
3. **File Validation**: Service validates file types and sizes
4. **Rate Limiting**: Consider adding rate limiting for production

## Migration Steps

### 1. Deploy OCR Microservice
Choose Render or Vercel and deploy the OCR service

### 2. Update Main Backend
Add OCR_SERVICE_URL environment variable

### 3. Test Integration
Verify that image uploads now use the microservice

### 4. Monitor Performance
Check logs and response times

### 5. Optimize as Needed
Adjust timeouts, file size limits, or upgrade service plans

## Benefits of This Architecture

✅ **Solves Timeout Issues**: Dedicated service with proper resource allocation
✅ **Better Scalability**: OCR service can be scaled independently
✅ **Improved Performance**: Optimized specifically for OCR processing
✅ **LLM Integration**: Optional AI-powered contact extraction
✅ **Fault Tolerance**: Graceful fallback when service unavailable
✅ **Cost Effective**: Pay only for OCR processing resources
✅ **Easy Maintenance**: Separate deployments and updates

This microservice architecture provides a robust solution for handling OCR processing without the constraints of the main application's timeout limits.
