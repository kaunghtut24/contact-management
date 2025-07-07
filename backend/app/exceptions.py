from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class ContactNotFoundError(Exception):
    def __init__(self, contact_id: int):
        self.contact_id = contact_id
        super().__init__(f"Contact with id {contact_id} not found")

class FileProcessingError(Exception):
    def __init__(self, filename: str, error: str):
        self.filename = filename
        self.error = error
        super().__init__(f"Error processing file {filename}: {error}")

class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error for {field}: {message}")

async def contact_not_found_handler(request: Request, exc: ContactNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Contact with id {exc.contact_id} not found"}
    )

async def file_processing_error_handler(request: Request, exc: FileProcessingError):
    logger.error(f"File processing error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Error processing file {exc.filename}: {exc.error}"}
    )

async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": f"Validation error for {exc.field}: {exc.message}"}
    )
