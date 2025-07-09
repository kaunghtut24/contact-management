# Render Deployment Timeout Fixes

## Issue
Upload timeouts occurring on Render deployment due to platform-specific constraints and resource limitations.

## Root Causes
1. **Render Request Timeout**: Render has a 30-second request timeout limit
2. **Resource Constraints**: Limited CPU/memory on Render free tier
3. **OCR Processing Time**: Large images taking too long to process
4. **Network Latency**: Additional overhead in cloud environment

## Render-Specific Fixes Applied

### 1. Uvicorn Server Configuration
**File**: `backend/render.yaml`
```yaml
startCommand: "uvicorn api:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 65 --timeout-graceful-shutdown 10"
```
- `--timeout-keep-alive 65`: Keeps connections alive longer
- `--timeout-graceful-shutdown 10`: Graceful shutdown handling

### 2. Environment-Based Timeout Configuration
**File**: `backend/render.yaml`
```yaml
# Timeout Configuration for Render
- key: OCR_TIMEOUT_SMALL
  value: 15
- key: OCR_TIMEOUT_MEDIUM
  value: 20
- key: OCR_TIMEOUT_LARGE
  value: 25
- key: UPLOAD_TIMEOUT_OVERALL
  value: 30
```

### 3. Dynamic Timeout Scaling (Render-Optimized)
**File**: `backend/api.py`

**Overall Request Timeout**:
- **< 1MB files**: 20 seconds max
- **1-1.5MB files**: 25 seconds max  
- **> 1.5MB files**: 30 seconds max (Render limit)

**OCR Processing Timeout**:
- **< 1MB files**: 15 seconds (configurable via `OCR_TIMEOUT_SMALL`)
- **1-1.5MB files**: 20 seconds (configurable via `OCR_TIMEOUT_MEDIUM`)
- **> 1.5MB files**: 25 seconds (configurable via `OCR_TIMEOUT_LARGE`)

### 4. Render-Specific OCR Optimizations
**File**: `backend/app/parsers/parse.py`

**Production Environment Detection**:
```python
is_render = os.getenv("ENVIRONMENT") == "production"

if is_render:
    # Maximum optimization for Render
    processed_image = preprocess_business_card_image(image)
    ocr_config = '--psm 6 --oem 1 -c tessedit_do_invert=0'
```

**Aggressive Image Preprocessing**:
- **Render**: Max 800px dimension (vs 1200px locally)
- **Render**: Skip image enhancement to save time
- **Render**: Use legacy OCR engine (faster)

### 5. Frontend Timeout Adjustments
**File**: `frontend/src/utils/api.js`
```javascript
timeout: 35000, // 35 seconds for Render deployment (backend max 30s)
```

**File**: `frontend/src/components/UploadPage.jsx`
- **File size limit**: Reduced to 1.5MB (from 2MB)
- **Progress messages**: Updated to reflect Render timeouts
- **User expectations**: Set realistic time estimates

## Timeout Hierarchy for Render

```
Frontend (35s) > Backend Overall (30s) > OCR Processing (15-25s)
```

### Timeout Matrix:
| File Size | OCR Timeout | Overall Timeout | Frontend Timeout |
|-----------|-------------|-----------------|------------------|
| < 1MB     | 15s         | 20s             | 35s              |
| 1-1.5MB   | 20s         | 25s             | 35s              |
| > 1.5MB   | 25s         | 30s             | 35s              |

## Performance Optimizations for Render

### 1. Image Processing
- **Aggressive resizing**: Max 800px for Render vs 1200px locally
- **Skip enhancements**: No contrast/sharpness adjustments on Render
- **Fastest resampling**: Use NEAREST instead of LANCZOS

### 2. OCR Configuration
- **Legacy engine**: Use `--oem 1` (faster than default `--oem 3`)
- **Minimal config**: Skip unnecessary OCR options
- **No inversion**: Disable `tessedit_do_invert` for speed

### 3. File Size Limits
- **Frontend validation**: Reject images > 1.5MB
- **Clear messaging**: Explain Render server limitations
- **User guidance**: Suggest image compression techniques

## Environment Variables for Render Dashboard

Set these in your Render service environment variables:

```bash
# Timeout Configuration
OCR_TIMEOUT_SMALL=15
OCR_TIMEOUT_MEDIUM=20
OCR_TIMEOUT_LARGE=25
UPLOAD_TIMEOUT_OVERALL=30

# Environment Detection
ENVIRONMENT=production

# Existing variables (keep as-is)
DATABASE_URL=your_neon_postgres_url
JWT_SECRET_KEY=your_jwt_secret
ALLOWED_ORIGINS=https://contact-management-six-alpha.vercel.app
```

## Expected Results After Deployment

### ✅ Improvements:
- **No more 30s timeouts**: Requests complete within Render's limits
- **Faster OCR processing**: Optimized for cloud environment
- **Better user experience**: Realistic time estimates and file size limits
- **Reliable uploads**: Consistent performance on Render infrastructure

### 📊 Performance Targets:
- **Small images (< 1MB)**: Process in 10-15 seconds
- **Medium images (1-1.5MB)**: Process in 15-20 seconds
- **Large images (> 1.5MB)**: Rejected with clear message

## Monitoring and Troubleshooting

### Log Messages to Watch:
```
"Render deployment detected, using maximum optimization"
"Resized image from 2000x1500 to 800x600 (Render: True)"
"Processing 1.2MB file with 25s overall timeout"
"OCR processing timed out for file: image.jpg (1.2MB) after 20s"
```

### If Timeouts Still Occur:
1. **Reduce timeout values** in Render environment variables
2. **Lower image size limit** to 1MB in frontend validation
3. **Check Render logs** for specific bottlenecks
4. **Consider upgrading** Render plan for more resources

## Deployment Steps

1. **Commit changes** to your repository
2. **Push to main branch** (triggers Render deployment)
3. **Set environment variables** in Render dashboard
4. **Monitor deployment logs** for optimization messages
5. **Test with various image sizes** to verify timeout fixes

## Rollback Plan

If issues occur, you can quickly rollback by:
1. Reverting the timeout environment variables to higher values
2. Changing `ENVIRONMENT` to `development` to disable Render optimizations
3. Increasing frontend file size limit back to 2MB

This provides a comprehensive solution for Render's timeout constraints while maintaining functionality.
