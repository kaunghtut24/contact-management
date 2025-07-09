#!/usr/bin/env python3
"""
Standalone OCR Microservice
Handles image processing, OCR, and intelligent contact extraction
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import io
import os
import logging
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OCR Microservice",
    description="Intelligent OCR processing for contact management",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Optional imports with graceful fallback
try:
    import pytesseract
    from PIL import Image, ImageEnhance
    OCR_AVAILABLE = True
    logger.info("✅ OCR dependencies loaded successfully")
except ImportError as e:
    OCR_AVAILABLE = False
    logger.warning(f"⚠️ OCR dependencies not available: {e}")

try:
    import openai
    LLM_AVAILABLE = True
    logger.info("✅ OpenAI client available")
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("⚠️ OpenAI client not available")

# Additional LLM providers
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
    logger.info("✅ Anthropic client available")
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("⚠️ Anthropic client not available")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logger.info("✅ Gemini client available")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ Gemini client not available")

# In-memory job storage (use Redis in production)
job_storage = {}

class OCRProcessor:
    """Handles OCR processing with multiple strategies"""
    
    def __init__(self):
        self.strategies = [
            self.fast_ocr,
            self.enhanced_ocr,
            self.fallback_ocr
        ]
    
    def preprocess_image(self, image: Image.Image, strategy: str = "fast") -> Image.Image:
        """Preprocess image for OCR with different strategies"""
        try:
            # Convert to RGB if needed
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            width, height = image.size
            
            # Strategy-based preprocessing
            if strategy == "fast":
                # Ultra-fast preprocessing
                max_dim = 800
                if width > max_dim or height > max_dim:
                    scale = min(max_dim/width, max_dim/height)
                    new_size = (int(width * scale), int(height * scale))
                    image = image.resize(new_size, Image.Resampling.NEAREST)
                
                # Convert to grayscale
                return image.convert('L')
            
            elif strategy == "enhanced":
                # Better quality preprocessing
                max_dim = 1200
                if width > max_dim or height > max_dim:
                    scale = min(max_dim/width, max_dim/height)
                    new_size = (int(width * scale), int(height * scale))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convert to grayscale and enhance
                gray = image.convert('L')
                enhancer = ImageEnhance.Contrast(gray)
                return enhancer.enhance(1.2)
            
            else:  # fallback
                # Minimal processing
                return image.convert('L')
                
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image.convert('L') if image.mode != 'L' else image
    
    async def fast_ocr(self, image: Image.Image) -> str:
        """Fast OCR with minimal preprocessing"""
        processed = self.preprocess_image(image, "fast")
        return pytesseract.image_to_string(processed, config='--psm 6 --oem 1')
    
    async def enhanced_ocr(self, image: Image.Image) -> str:
        """Enhanced OCR with better preprocessing"""
        processed = self.preprocess_image(image, "enhanced")
        return pytesseract.image_to_string(processed, config='--psm 6 --oem 3')
    
    async def fallback_ocr(self, image: Image.Image) -> str:
        """Fallback OCR with different settings"""
        processed = self.preprocess_image(image, "fallback")
        return pytesseract.image_to_string(processed, config='--psm 4 --oem 1')
    
    async def process_image(self, image_data: bytes, timeout: int = 30) -> Dict[str, Any]:
        """Process image with multiple OCR strategies"""
        if not OCR_AVAILABLE:
            raise HTTPException(status_code=503, detail="OCR service not available")
        
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            file_size_mb = len(image_data) / (1024 * 1024)
            
            logger.info(f"Processing image: {width}x{height}, {file_size_mb:.1f}MB")
            
            # Try strategies in order with timeout
            for i, strategy in enumerate(self.strategies):
                try:
                    strategy_timeout = max(5, timeout // len(self.strategies))
                    text = await asyncio.wait_for(
                        strategy(image), 
                        timeout=strategy_timeout
                    )
                    
                    if text.strip():
                        logger.info(f"Strategy {i+1} succeeded, extracted {len(text)} characters")
                        return {
                            "success": True,
                            "text": text.strip(),
                            "strategy_used": i + 1,
                            "image_info": {
                                "width": width,
                                "height": height,
                                "size_mb": file_size_mb
                            }
                        }
                except asyncio.TimeoutError:
                    logger.warning(f"Strategy {i+1} timed out after {strategy_timeout}s")
                    continue
                except Exception as e:
                    logger.warning(f"Strategy {i+1} failed: {e}")
                    continue
            
            # All strategies failed
            return {
                "success": False,
                "error": "All OCR strategies failed or timed out",
                "image_info": {
                    "width": width,
                    "height": height,
                    "size_mb": file_size_mb
                }
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                "success": False,
                "error": f"Image processing failed: {str(e)}"
            }

class LLMProcessor:
    """Handles LLM-powered contact extraction and categorization with multiple providers"""

    def __init__(self):
        self.providers = {}
        self.default_provider = None

        # Initialize OpenAI
        if LLM_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")  # For OpenAI-compatible APIs
            if api_key:
                self.providers["openai"] = {
                    "client": openai.OpenAI(api_key=api_key, base_url=base_url),
                    "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    "type": "openai"
                }
                if not self.default_provider:
                    self.default_provider = "openai"
                logger.info("✅ OpenAI client initialized")

        # Initialize Anthropic
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.providers["anthropic"] = {
                    "client": anthropic.Anthropic(api_key=api_key),
                    "model": os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                    "type": "anthropic"
                }
                if not self.default_provider:
                    self.default_provider = "anthropic"
                logger.info("✅ Anthropic client initialized")

        # Initialize Gemini
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.providers["gemini"] = {
                    "client": genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-pro")),
                    "model": os.getenv("GEMINI_MODEL", "gemini-pro"),
                    "type": "gemini"
                }
                if not self.default_provider:
                    self.default_provider = "gemini"
                logger.info("✅ Gemini client initialized")

        # Initialize OpenAI-compatible APIs (Groq, Together, etc.)
        openai_compatible_providers = [
            ("groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1", "mixtral-8x7b-32768"),
            ("together", "TOGETHER_API_KEY", "https://api.together.xyz/v1", "meta-llama/Llama-2-7b-chat-hf"),
            ("perplexity", "PERPLEXITY_API_KEY", "https://api.perplexity.ai", "llama-3.1-sonar-small-128k-online"),
            ("deepseek", "DEEPSEEK_API_KEY", "https://api.deepseek.com", "deepseek-chat"),
        ]

        for provider_name, env_key, base_url, default_model in openai_compatible_providers:
            api_key = os.getenv(env_key)
            if api_key:
                model_key = f"{provider_name.upper()}_MODEL"
                self.providers[provider_name] = {
                    "client": openai.OpenAI(api_key=api_key, base_url=base_url),
                    "model": os.getenv(model_key, default_model),
                    "type": "openai_compatible"
                }
                if not self.default_provider:
                    self.default_provider = provider_name
                logger.info(f"✅ {provider_name.title()} client initialized")

        if not self.providers:
            logger.warning("⚠️ No LLM providers configured")
        else:
            logger.info(f"🤖 Default LLM provider: {self.default_provider}")
    
    async def extract_contacts(self, text: str, provider: str = None) -> List[Dict[str, Any]]:
        """Extract structured contact information using LLM"""
        if not self.providers:
            # Fallback to rule-based extraction
            return self.rule_based_extraction(text)

        # Use specified provider or default
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider

        provider_config = self.providers[provider_name]

        try:
            prompt = self._create_extraction_prompt(text)

            if provider_config["type"] == "openai" or provider_config["type"] == "openai_compatible":
                result = await self._extract_with_openai_api(provider_config, prompt)
            elif provider_config["type"] == "anthropic":
                result = await self._extract_with_anthropic(provider_config, prompt)
            elif provider_config["type"] == "gemini":
                result = await self._extract_with_gemini(provider_config, prompt)
            else:
                raise ValueError(f"Unknown provider type: {provider_config['type']}")

            contacts = json.loads(result)
            logger.info(f"LLM ({provider_name}) extracted {len(contacts)} contacts")
            return contacts

        except Exception as e:
            logger.warning(f"LLM extraction failed with {provider_name}: {e}, falling back to rule-based")
            return self.rule_based_extraction(text)

    def _create_extraction_prompt(self, text: str) -> str:
        """Create extraction prompt for contact information"""
        return f"""
Extract contact information from the following text and return as JSON array.
Each contact should have these fields: name, designation, company, email, phone, website, address, categories.

Categories should be one or more of: Government, Embassy, Consulate, High Commissioner, Deputy High Commissioner,
Associations, Exporter, Importer, Logistics, Event management, Consultancy, Manufacturer, Distributors, Producers, Others.

Rules:
1. Return only valid JSON array, no other text
2. If no clear contacts found, return empty array []
3. Ensure all fields are strings (use empty string "" if not found)
4. Categories should be array of strings
5. Clean and format phone numbers consistently
6. Validate email addresses

Text to process:
{text}

JSON Response:"""

    async def _extract_with_openai_api(self, provider_config: Dict, prompt: str) -> str:
        """Extract using OpenAI API or compatible"""
        response = await asyncio.to_thread(
            provider_config["client"].chat.completions.create,
            model=provider_config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

    async def _extract_with_anthropic(self, provider_config: Dict, prompt: str) -> str:
        """Extract using Anthropic Claude"""
        response = await asyncio.to_thread(
            provider_config["client"].messages.create,
            model=provider_config["model"],
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    async def _extract_with_gemini(self, provider_config: Dict, prompt: str) -> str:
        """Extract using Google Gemini"""
        response = await asyncio.to_thread(
            provider_config["client"].generate_content,
            prompt
        )
        return response.text.strip()
    
    def rule_based_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Fallback rule-based contact extraction"""
        import re
        
        # Basic patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{8,15}'
        
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        phones = re.findall(phone_pattern, text)
        
        # Simple extraction - one contact per email found
        contacts = []
        lines = text.split('\n')
        
        for email in emails:
            contact = {
                "name": "",
                "designation": "",
                "company": "",
                "email": email,
                "phone": phones[0] if phones else "",
                "website": "",
                "address": "",
                "categories": ["Others"]
            }
            
            # Try to find name and company near email
            for i, line in enumerate(lines):
                if email in line:
                    # Look for name in previous lines
                    for j in range(max(0, i-3), i):
                        if lines[j].strip() and not any(char in lines[j] for char in '@.com'):
                            contact["name"] = lines[j].strip()
                            break
                    break
            
            contacts.append(contact)
        
        return contacts if contacts else [{
            "name": "",
            "designation": "",
            "company": "",
            "email": "",
            "phone": phones[0] if phones else "",
            "website": "",
            "address": "",
            "categories": ["Others"]
        }]

# Initialize processors
try:
    ocr_processor = OCRProcessor()
    logger.info("✅ OCR processor initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize OCR processor: {e}")
    ocr_processor = None

try:
    llm_processor = LLMProcessor()
    logger.info("✅ LLM processor initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize LLM processor: {e}")
    # Create a fallback LLM processor
    class FallbackLLMProcessor:
        def __init__(self):
            self.providers = {}
            self.default_provider = None

        async def extract_contacts(self, text: str, provider: str = None) -> List[Dict[str, Any]]:
            return self.rule_based_extraction(text)

        def rule_based_extraction(self, text: str) -> List[Dict[str, Any]]:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text, re.IGNORECASE)
            return [{"name": "", "designation": "", "company": "", "email": email,
                    "phone": "", "website": "", "address": "", "categories": ["Others"]}
                   for email in emails] if emails else [{"name": "", "designation": "",
                   "company": "", "email": "", "phone": "", "website": "", "address": "",
                   "categories": ["Others"]}]

    llm_processor = FallbackLLMProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "OCR Microservice",
        "version": "1.0.0",
        "status": "healthy",
        "capabilities": {
            "ocr_available": OCR_AVAILABLE,
            "llm_available": len(llm_processor.providers) > 0,
            "llm_providers": list(llm_processor.providers.keys()),
            "default_provider": llm_processor.default_provider
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ocr_available": OCR_AVAILABLE,
        "llm_available": len(llm_processor.providers) > 0,
        "llm_providers": list(llm_processor.providers.keys()),
        "default_provider": llm_processor.default_provider,
        "job_queue_size": len(job_storage)
    }

@app.post("/process-sync")
async def process_image_sync(file: UploadFile = File(...)):
    """Synchronous image processing (for small files)"""
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if not OCR_AVAILABLE or ocr_processor is None:
        raise HTTPException(status_code=503, detail="OCR service not available")

    try:
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)

        # Limit sync processing to smaller files
        if file_size_mb > 1.0:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size_mb:.1f}MB) for sync processing. Use async endpoint."
            )

        # Process with OCR
        ocr_result = await ocr_processor.process_image(content, timeout=15)

        if not ocr_result["success"]:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": ocr_result["error"],
                    "image_info": ocr_result.get("image_info")
                }
            )

        # Extract contacts using LLM
        contacts = await llm_processor.extract_contacts(ocr_result["text"])

        return {
            "success": True,
            "filename": file.filename,
            "ocr_result": ocr_result,
            "contacts": contacts,
            "processing_time": "sync"
        }

    except Exception as e:
        logger.error(f"Sync processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process-async")
async def process_image_async(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Asynchronous image processing (for larger files)"""
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Store job info
    job_storage[job_id] = {
        "status": "queued",
        "filename": file.filename,
        "created_at": datetime.utcnow().isoformat(),
        "result": None,
        "error": None
    }

    # Read file content
    content = await file.read()

    # Add background task
    background_tasks.add_task(process_image_background, job_id, content, file.filename)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Processing started. Use /status/{job_id} to check progress."
    }

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    return job_storage[job_id]

async def process_image_background(job_id: str, content: bytes, filename: str):
    """Background task for image processing"""
    try:
        # Update status
        job_storage[job_id]["status"] = "processing"
        job_storage[job_id]["started_at"] = datetime.utcnow().isoformat()

        # Process with OCR (longer timeout for async)
        ocr_result = await ocr_processor.process_image(content, timeout=60)

        if not ocr_result["success"]:
            job_storage[job_id]["status"] = "failed"
            job_storage[job_id]["error"] = ocr_result["error"]
            job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()
            return

        # Extract contacts using LLM
        contacts = await llm_processor.extract_contacts(ocr_result["text"])

        # Store result
        job_storage[job_id]["status"] = "completed"
        job_storage[job_id]["result"] = {
            "filename": filename,
            "ocr_result": ocr_result,
            "contacts": contacts
        }
        job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()

    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")
        job_storage[job_id]["status"] = "failed"
        job_storage[job_id]["error"] = str(e)
        job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
