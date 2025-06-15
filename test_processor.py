import os
import sys
from src.document_processor import HealthcareDocumentProcessor

def test_document_processing(document_path):
    """Test the document processing pipeline with a sample document."""
    print(f"Testing document: {document_path}")
    
    # Initialize the processor
    processor = HealthcareDocumentProcessor()
    
    try:
        # Process the document
        result = processor.process_document(document_path)
        
        # Print results
        print("\n=== Processing Results ===")
        print(f"Document Type: {result['classification']['document_type']}")
        print(f"Confidence: {result['classification']['confidence']}")
        print(f"Pages: {result['classification']['pages']}")
        
        print("\n=== Extracted Text (first 500 chars) ===")
        print(result['extracted_text']['text'][:500] + "...")
        
        print("\n=== Metadata ===")
        for key, value in result['metadata'].items():
            print(f"{key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_processor.py <path_to_document>")
        sys.exit(1)
        
    document_path = sys.argv[1]
    if not os.path.exists(document_path):
        print(f"Error: File not found: {document_path}")
        sys.exit(1)
        
    success = test_document_processing(document_path)
    sys.exit(0 if success else 1)
