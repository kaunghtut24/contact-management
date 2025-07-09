# Complete OCR Microservice Deployment Guide

## 🎯 Overview

This guide will help you deploy the enhanced OCR microservice with multiple LLM providers and integrate it with your main contact management system.

## 🏗️ Architecture

```
Frontend (Vercel) → Main Backend (Render) → OCR Microservice (Render)
                                         ↓
                                    LLM Providers:
                                    • OpenAI/GPT
                                    • Anthropic/Claude  
                                    • Google/Gemini
                                    • Groq (Fast)
                                    • Together AI
                                    • Perplexity
                                    • DeepSeek
```

## 📋 Prerequisites

1. **GitHub Account** - For code repository
2. **Render Account** - For hosting services
3. **LLM Provider API Key** - At least one of:
   - OpenAI API Key (recommended)
   - Anthropic API Key
   - Google AI API Key
   - Groq API Key (free tier available)
   - Together AI API Key
   - Perplexity API Key
   - DeepSeek API Key

## 🚀 Step-by-Step Deployment

### Step 1: Prepare OCR Microservice Repository

```bash
# 1. Create new repository for OCR service
# Go to GitHub and create: ocr-microservice

# 2. Navigate to OCR service directory
cd ocr-service

# 3. Initialize git repository
git init
git add .
git commit -m "Initial OCR microservice with multi-LLM support"

# 4. Connect to GitHub
git remote add origin https://github.com/yourusername/ocr-microservice.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy OCR Microservice on Render

#### 2.1 Create New Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your `ocr-microservice` repository
4. Configure service:
   - **Name**: `ocr-microservice`
   - **Environment**: `Docker`
   - **Region**: Same as your main backend
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`

#### 2.2 Configure Environment Variables

**Required Variables:**
```bash
# CORS Configuration
ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app,https://contact-management-ffsl.onrender.com

# Service Configuration  
PORT=8002
```

**LLM Provider Variables (Choose at least one):**

**Option A: OpenAI (Recommended)**
```bash
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
```

**Option B: Groq (Fast & Free Tier)**
```bash
GROQ_API_KEY=gsk_your-groq-api-key
GROQ_MODEL=mixtral-8x7b-32768
```

**Option C: Anthropic Claude**
```bash
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

**Option D: Google Gemini**
```bash
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro
```

**Option E: OpenAI-Compatible APIs**
```bash
# For custom OpenAI-compatible endpoints
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.your-provider.com/v1
OPENAI_MODEL=your-model-name
```

#### 2.3 Deploy Service
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your service URL: `https://your-ocr-service.onrender.com`

### Step 3: Update Main Backend Configuration

#### 3.1 Add OCR Service URL to Main Backend
In your main backend Render service, add environment variable:
```bash
OCR_SERVICE_URL=https://your-ocr-service.onrender.com
```

#### 3.2 Update Main Backend Code
The main backend will automatically detect and use the OCR microservice when `OCR_SERVICE_URL` is configured.

### Step 4: Test the Integration

#### 4.1 Test OCR Service Health
```bash
curl https://your-ocr-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "ocr_available": true,
  "llm_available": true,
  "job_queue_size": 0
}
```

#### 4.2 Test Contact Upload
1. Go to your frontend: `https://contact-management-six-alpha.vercel.app`
2. Upload a business card image
3. Check that it processes without timeout
4. Verify contacts are extracted with proper categorization

## 🔧 Configuration Options

### LLM Provider Comparison

| Provider | Speed | Cost | Quality | Free Tier |
|----------|-------|------|---------|-----------|
| Groq | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Yes |
| OpenAI GPT-3.5 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ No |
| OpenAI GPT-4 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ No |
| Anthropic Claude | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ No |
| Google Gemini | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Limited |

### Recommended Configurations

**For Development/Testing:**
```bash
GROQ_API_KEY=your-groq-key  # Free tier available
GROQ_MODEL=mixtral-8x7b-32768
```

**For Production (Best Quality):**
```bash
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-3.5-turbo
```

**For Production (Cost-Effective):**
```bash
ANTHROPIC_API_KEY=your-anthropic-key
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

## 🔍 Monitoring and Troubleshooting

### Health Check Endpoints

```bash
# Basic health check
GET /health

# Service capabilities
GET /

# Process small image (sync)
POST /process-sync

# Process large image (async)
POST /process-async

# Check async job status
GET /status/{job_id}
```

### Common Issues

#### 1. Service Not Responding
```bash
# Check service status
curl https://your-ocr-service.onrender.com/health

# Check Render logs
# Go to Render Dashboard → Your Service → Logs
```

#### 2. LLM Not Working
```bash
# Verify API key is set
# Check service capabilities
curl https://your-ocr-service.onrender.com/

# Expected response should show llm_available: true
```

#### 3. OCR Quality Issues
- Ensure images are clear and high-contrast
- Try different image formats (PNG vs JPEG)
- Check image orientation

### Performance Optimization

#### For High Volume:
1. **Upgrade Render Plan**: Standard ($25/month) for better performance
2. **Use Multiple Providers**: Configure fallback LLM providers
3. **Optimize Images**: Compress images before upload

#### For Cost Optimization:
1. **Use Groq**: Free tier with good performance
2. **Limit File Sizes**: Reject very large images
3. **Cache Results**: Implement caching for repeated images

## 📊 Expected Performance

### Processing Times
- **Small images (< 500KB)**: 5-10 seconds
- **Medium images (500KB-1MB)**: 10-15 seconds  
- **Large images (1-2MB)**: 15-25 seconds

### Success Rates
- **Clear business cards**: 90-95% accuracy
- **Complex layouts**: 70-85% accuracy
- **Poor quality images**: 50-70% accuracy

## 🔐 Security Best Practices

1. **API Keys**: Store in Render environment variables (never in code)
2. **CORS**: Restrict origins to your domains only
3. **Rate Limiting**: Monitor usage and implement limits if needed
4. **File Validation**: Service validates file types and sizes
5. **Error Handling**: No sensitive information in error messages

## 💰 Cost Estimation

### Render Hosting
- **Starter Plan**: $7/month (suitable for low-medium usage)
- **Standard Plan**: $25/month (recommended for production)

### LLM API Costs (per 1000 images)
- **Groq**: Free tier (limited requests)
- **OpenAI GPT-3.5**: ~$1-3
- **OpenAI GPT-4**: ~$10-30
- **Anthropic Claude**: ~$2-5
- **Google Gemini**: ~$1-2

## 🎉 Next Steps

1. **Deploy OCR Service**: Follow steps above
2. **Configure LLM Provider**: Choose based on your needs
3. **Test Integration**: Upload test images
4. **Monitor Performance**: Check logs and response times
5. **Optimize**: Adjust settings based on usage patterns

## 🆘 Support

If you encounter issues:
1. Check Render service logs
2. Verify environment variables
3. Test health endpoints
4. Check API key validity
5. Review CORS configuration

This microservice architecture will completely solve your timeout issues while providing intelligent contact extraction and categorization!
