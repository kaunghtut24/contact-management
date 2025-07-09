# Upload Timeout and JWT Signature Fixes

## Issues Addressed

1. **Upload Timeout Error**: "Upload timed out. Please try with a smaller image or check your connection."
2. **JWT Signature Verification Failed**: After changing JWT secret key at Render

## Fixes Applied

### 1. Upload Timeout Fixes

#### Backend Changes (`backend/api.py`)

**Added Multi-Level Timeout Protection:**

1. **Overall Request Timeout (30 seconds)**:
   ```python
   @app.post("/upload")
   async def upload_file(...):
       try:
           return await asyncio.wait_for(_process_upload_file(file, db), timeout=30.0)
       except asyncio.TimeoutError:
           return {"message": "File upload timed out", "timeout": True}
   ```

2. **OCR Processing Timeout (20 seconds)**:
   ```python
   with ThreadPoolExecutor(max_workers=1) as executor:
       try:
           future = executor.submit(parse_func, content)
           contacts_data = future.result(timeout=20)
       except FutureTimeoutError:
           return {"message": "OCR processing timed out", "timeout": True}
   ```

3. **Fast OCR Function**: Uses optimized single-strategy OCR instead of multiple strategies

#### Frontend Changes

**Extended Frontend Timeout (`frontend/src/utils/api.js`)**:
```javascript
upload: (file) => {
  return api.post('/upload', formData, {
    timeout: 45000, // 45 seconds (backend times out at 30s)
  });
},
```

**Improved Error Handling (`frontend/src/components/UploadPage.jsx`)**:
```javascript
} catch (error) {
  let errorMessage = 'Error uploading file: ';
  
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    errorMessage += 'Upload timed out. Please try with a smaller image or check your connection.';
  } else if (error.response?.data?.timeout) {
    errorMessage += 'Processing timed out. Please try with a smaller or clearer image.';
  }
  // ... more error handling
}
```

### 2. JWT Signature Verification Fixes

#### Backend Changes (`backend/api.py`)

**Improved JWT Error Handling**:
```python
except JWTError as e:
    error_msg = str(e)
    if "Signature verification failed" in error_msg:
        logger.info(f"JWT signature verification failed - likely due to secret key change: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired due to security update. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

#### Frontend Changes (`frontend/src/utils/api.js`)

**Enhanced 401 Error Handling**:
```javascript
if (error.response?.status === 401) {
  const errorDetail = error.response?.data?.detail || '';
  if (errorDetail.includes('security update') || errorDetail.includes('signature')) {
    console.warn('JWT signature changed - clearing auth and redirecting to login');
  } else {
    console.error('Authentication failed - redirecting to login');
  }
  // Clear auth and reload
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.reload();
}
```

## Timeout Strategy

### Multi-Layer Timeout Protection:

1. **Frontend**: 45-second timeout for the HTTP request
2. **Backend Overall**: 30-second timeout for the entire upload process
3. **Backend OCR**: 20-second timeout specifically for OCR processing
4. **Fast OCR**: Optimized single-strategy OCR processing

### Timeout Hierarchy:
```
Frontend (45s) > Backend Overall (30s) > Backend OCR (20s)
```

This ensures:
- OCR times out first (20s) with graceful error handling
- If OCR doesn't timeout but other processing is slow, overall backend times out (30s)
- Frontend waits longer (45s) to receive the backend timeout response

## Expected Results

### Upload Timeout Fixes:
- ✅ **No more 30-second frontend timeouts** - Backend handles timeouts gracefully
- ✅ **Better user feedback** - Clear timeout messages with actionable advice
- ✅ **Faster OCR processing** - Optimized single-strategy approach
- ✅ **Graceful degradation** - System continues to work even when OCR times out

### JWT Signature Fixes:
- ✅ **Clear error messages** - Users understand why they need to login again
- ✅ **Automatic cleanup** - Auth tokens are cleared when signature fails
- ✅ **Better logging** - Distinguishes between signature failures and other JWT errors
- ✅ **Smooth user experience** - Automatic redirect to login after clearing auth

## Testing

After deployment, test with:

1. **Large image files** - Should timeout gracefully at 20 seconds with clear message
2. **Complex images** - Should process within timeout or fail gracefully
3. **Authentication** - Should automatically redirect to login when JWT signature fails
4. **Normal uploads** - Should work faster with optimized processing

## Deployment Notes

- These fixes are backward compatible
- No database changes required
- JWT secret key change is expected to invalidate existing tokens
- Users will need to login again after JWT secret change (this is normal security behavior)
