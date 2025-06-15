from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from pathlib import Path
# Use absolute import for better compatibility
from src.document_processor import HealthcareDocumentProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Healthcare Document Processing API",
    description="API for classifying and processing healthcare documents",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document processor
processor = HealthcareDocumentProcessor()

class DocumentResponse(BaseModel):
    document_id: str
    document_type: str
    confidence: float
    extracted_text: Optional[str] = None
    error: Optional[str] = None

@app.post("/upload/", response_model=DocumentResponse)
async def upload_document(file: UploadFile):
    """
    Upload and process a document.
    
    This endpoint accepts a document file, saves it temporarily,
    processes it for classification and text extraction, and returns the results.
    """
    try:
        # Generate a unique ID for the document
        doc_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.bin'
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_extension}")
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Processing document: {file.filename} (saved as {file_path})")
        
        # Process the document
        result = processor.process_document(file_path)
        
        # Clean up the uploaded file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary file {file_path}: {str(e)}")
        
        return {
            "document_id": doc_id,
            "document_type": result["classification"]["document_type"],
            "confidence": result["classification"]["confidence"],
            "extracted_text": result["extracted_text"]["text"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
