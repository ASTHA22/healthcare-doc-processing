import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# Use absolute import for better compatibility
from src.data_extractor import HealthcareDataExtractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareDocumentProcessor:
    """Process healthcare documents with classification and OCR capabilities."""
    
    def __init__(self):
        """Initialize the document processor with Azure credentials."""
        load_dotenv()  # Load environment variables from .env file
        
        # Initialize Form Recognizer client
        form_recognizer_endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        form_recognizer_key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        
        # Initialize Computer Vision client
        vision_endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
        vision_key = os.getenv("AZURE_COMPUTER_VISION_KEY")
        
        # Initialize clients
        self.form_recognizer_client = DocumentAnalysisClient(
            endpoint=form_recognizer_endpoint,
            credential=AzureKeyCredential(form_recognizer_key)
        )
        
        self.vision_client = ComputerVisionClient(
            endpoint=vision_endpoint,
            credentials=CognitiveServicesCredentials(vision_key)
        )
        
        # Load document types from environment
        self.document_types = os.getenv("DOCUMENT_TYPES", "").split(",")
        
        # Initialize data extractor
        self.data_extractor = HealthcareDataExtractor()
    
    def classify_document(self, document_path: str) -> Dict:
        """
        Classify a document using Azure Form Recognizer.
        
        Args:
            document_path: Path to the document to classify
            
        Returns:
            Dict containing classification results
        """
        try:
            with open(document_path, "rb") as f:
                poller = self.form_recognizer_client.begin_analyze_document(
                    "prebuilt-document",
                    document=f
                )
                result = poller.result()
                
            # Extract key information
            doc_type = self._determine_document_type(result)
            
            return {
                "document_type": doc_type,
                "confidence": 0.9,  # Placeholder, actual confidence would come from the model
                "pages": len(result.pages),
                "fields": {k: v.value for k, v in result.documents[0].fields.items()}
            }
            
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            raise
    
    def extract_text(self, document_path: str) -> Dict:
        """
        Extract text from a document using OCR.
        
        Args:
            document_path: Path to the document to process
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            with open(document_path, "rb") as f:
                # Using Computer Vision for OCR
                read_operation = self.vision_client.read_in_stream(
                    image=f,
                    raw=True
                )
                
                # Get the operation location (URL with the operation ID)
                operation_location = read_operation.headers["Operation-Location"]
                operation_id = operation_location.split("/")[-1]
                
                # Wait for the operation to complete
                import time
                while True:
                    result = self.vision_client.get_read_result(operation_id)
                    if result.status.lower() not in ['notstarted', 'running']:
                        break
                    time.sleep(1)
                
                # Extract the text
                extracted_text = []
                if result.status == OperationStatusCodes.succeeded:
                    for page in result.analyze_result.read_results:
                        for line in page.lines:
                            extracted_text.append(line.text)
                
                return {
                    "text": "\n".join(extracted_text),
                    "language": result.analyze_result.language if hasattr(result.analyze_result, 'language') else "unknown",
                    "pages": len(result.analyze_result.read_results) if hasattr(result.analyze_result, 'read_results') else 0
                }
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise
    
    def process_document(self, document_path: str) -> Dict:
        """
        Process a document through the entire pipeline.
        
        Args:
            document_path: Path to the document to process
            
        Returns:
            Dict containing processing results
        """
        try:
            start_time = datetime.utcnow()
            
            # Step 1: Classify the document
            classification = self.classify_document(document_path)
            doc_type = classification.get('document_type', 'unknown')
            
            # Step 2: Extract text using OCR
            ocr_result = self.extract_text(document_path)
            extracted_text = ocr_result.get('text', '')
            
            # Step 3: Extract structured data
            structured_data = self.data_extractor.extract_structured_data(
                text=extracted_text,
                doc_type=doc_type
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Combine results
            return {
                "classification": classification,
                "extracted_text": {
                    "text": extracted_text,
                    "language": ocr_result.get('language', 'unknown'),
                    "pages": ocr_result.get('pages', 1)
                },
                "structured_data": structured_data,
                "metadata": {
                    "filename": os.path.basename(document_path),
                    "file_size": os.path.getsize(document_path),
                    "processing_time_seconds": round(processing_time, 2),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    def _determine_document_type(self, analysis_result) -> str:
        """
        Determine the document type based on analysis results.
        This is a simplified example - in production, you'd want to implement
        more sophisticated logic based on your document types.
        """
        # This is a placeholder - implement your own document type detection logic
        # based on the analysis_result content
        if "claim" in str(analysis_result).lower():
            return "insurance_claim"
        elif "prescription" in str(analysis_result).lower():
            return "prescription"
        elif "report" in str(analysis_result).lower():
            return "medical_report"
        else:
            return "unknown"

# Example usage
if __name__ == "__main__":
    # Example usage
    processor = HealthcareDocumentProcessor()
    
    # Example document path - replace with actual path to test document
    test_doc = "path/to/your/document.pdf"
    
    if os.path.exists(test_doc):
        result = processor.process_document(test_doc)
        print("Document processing results:")
        print(f"Document Type: {result['classification']['document_type']}")
        print(f"Extracted Text: {result['extracted_text']['text'][:200]}...")  # Print first 200 chars
    else:
        print(f"Test document not found at {test_doc}")
