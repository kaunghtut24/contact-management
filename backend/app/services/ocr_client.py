"""
OCR Microservice Client
Handles communication with the standalone OCR service
"""
import httpx
import asyncio
import logging
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OCRClient:
    """Client for communicating with OCR microservice"""
    
    def __init__(self):
        self.base_url = os.getenv("OCR_SERVICE_URL", "http://localhost:8002")
        self.timeout = httpx.Timeout(30.0, connect=5.0)
        
    async def health_check(self) -> bool:
        """Check if OCR service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"OCR service health check failed: {e}")
            return False
    
    async def process_image_sync(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Process image synchronously (for files <= 1MB)"""
        try:
            files = {"file": (filename, content, "image/jpeg")}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/process-sync",
                    files=files
                )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "method": "sync"
                }
            else:
                error_detail = response.json().get("detail", "Unknown error")
                return {
                    "success": False,
                    "error": f"OCR service error: {error_detail}",
                    "status_code": response.status_code
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "OCR service timeout",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR service communication failed: {str(e)}"
            }
    
    async def process_image_async(self, filename: str, content: bytes, max_wait: int = 45) -> Dict[str, Any]:
        """Process image asynchronously (for larger files)"""
        try:
            files = {"file": (filename, content, "image/jpeg")}
            
            # Start async processing
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/process-async",
                    files=files
                )
            
            if response.status_code != 200:
                error_detail = response.json().get("detail", "Unknown error")
                return {
                    "success": False,
                    "error": f"OCR service error: {error_detail}",
                    "status_code": response.status_code
                }
            
            job_info = response.json()
            job_id = job_info["job_id"]
            
            # Poll for completion
            poll_interval = 2  # seconds
            waited = 0
            
            while waited < max_wait:
                await asyncio.sleep(poll_interval)
                waited += poll_interval
                
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        status_response = await client.get(
                            f"{self.base_url}/status/{job_id}"
                        )
                    
                    if status_response.status_code == 200:
                        job_status = status_response.json()
                        
                        if job_status["status"] == "completed":
                            return {
                                "success": True,
                                "data": job_status["result"],
                                "method": "async",
                                "processing_time": f"{waited}s"
                            }
                        elif job_status["status"] == "failed":
                            return {
                                "success": False,
                                "error": f"OCR processing failed: {job_status.get('error', 'Unknown error')}",
                                "job_id": job_id
                            }
                        # Continue polling if still processing
                        
                except Exception as poll_error:
                    logger.warning(f"Error polling job {job_id}: {poll_error}")
                    continue
            
            # Timeout waiting for completion
            return {
                "success": False,
                "error": f"OCR processing timed out after {max_wait}s",
                "timeout": True,
                "job_id": job_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR async processing failed: {str(e)}"
            }
    
    async def process_image(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Process image with automatic sync/async selection based on file size"""
        file_size_mb = len(content) / (1024 * 1024)
        
        logger.info(f"Processing {file_size_mb:.1f}MB image using OCR microservice")
        
        # Check service availability first
        if not await self.health_check():
            return {
                "success": False,
                "error": "OCR microservice is not available",
                "service_unavailable": True
            }
        
        # Choose processing method based on file size
        if file_size_mb <= 1.0:
            logger.info(f"Using sync processing for {file_size_mb:.1f}MB file")
            return await self.process_image_sync(filename, content)
        else:
            logger.info(f"Using async processing for {file_size_mb:.1f}MB file")
            return await self.process_image_async(filename, content)

# Global OCR client instance
ocr_client = OCRClient()
