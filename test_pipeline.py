import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.document_processor import HealthcareDocumentProcessor
from src.data_extractor import HealthcareDataExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Load environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verify required environment variables
    required_vars = [
        'AZURE_FORM_RECOGNIZER_ENDPOINT',
        'AZURE_FORM_RECOGNIZER_KEY',
        'AZURE_COMPUTER_VISION_ENDPOINT',
        'AZURE_COMPUTER_VISION_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please create a .env file with the required variables.")
        return False
    
    return True

def process_document(document_path: str, output_dir: str = "output"):
    """Process a document and save the results."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize processor
        processor = HealthcareDocumentProcessor()
        
        # Process the document
        logger.info(f"Processing document: {document_path}")
        start_time = datetime.utcnow()
        result = processor.process_document(document_path)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(document_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}_results.json")
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        # Print summary
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Results saved to: {output_file}")
        
        # Print structured data summary
        if 'structured_data' in result and 'extracted_fields' in result['structured_data']:
            logger.info("\nExtracted Fields:")
            for field, value in result['structured_data']['extracted_fields'].items():
                logger.info(f"  - {field}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return False

def test_data_extractor(output_dir="test_output"):
    """Test the data extractor with sample text.
    
    Args:
        output_dir: Directory to save test results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a timestamp for this test run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_results_{timestamp}.txt")
    
    print(f"\n=== Testing Data Extractor ===")
    print(f"Results will be saved to: {os.path.abspath(output_file)}")
    
    # Open output file
    with open(output_file, 'w') as f:
        f.write(f"=== Test Run: {timestamp} ===\n\n")
    
    # Sample documents for testing
    test_cases = [
        {
            "type": "insurance_claim",
            "text": """
            PATIENT INFORMATION
            Name: John Doe
            Date of Birth: 01/15/1980
            Member ID: ABC123456
            
            CLAIM DETAILS
            Claim #: CLM987654
            Date of Service: 05/10/2023
            Provider: Dr. Smith
            Diagnosis Code: E11.65
            Procedure Code: 99213
            Total Amount: $150.00
            """
        },
        {
            "type": "prescription",
            "text": """
            PRESCRIPTION
            
            Patient: Jane Smith
            Date: 06/15/2023
            
            Medication: Amoxicillin
            Dosage: 500mg
            Frequency: Every 8 hours
            Refills: 2
            
            Prescriber: Dr. Johnson
            DEA: AB1234567
            """
        }
    ]
    
    extractor = HealthcareDataExtractor()
    
    # Process each test case
    for idx, test in enumerate(test_cases, 1):
        test_header = f"\nTest Case {idx}: {test['type'].upper()}"
        separator = "=" * len(test_header)
        
        # Print to console
        print(f"\n{separator}")
        print(test_header)
        print(f"{separator}")
        
        # Write to file
        with open(output_file, 'a') as f:
            f.write(f"\n{separator}")
            f.write(f"\n{test_header}")
            f.write(f"\n{separator}\n\n")
            f.write("=== INPUT TEXT ===\n")
            f.write(test['text'] + "\n\n")
        
        # Process the document
        result = extractor.extract_structured_data(test['text'], test['type'])
        
        # Prepare output
        output = []
        
        # Add extracted fields
        if 'extracted_fields' in result and result['extracted_fields']:
            output.append("=== EXTRACTED FIELDS ===")
            for field, value in result['extracted_fields'].items():
                output.append(f"{field}: {value}")
        else:
            output.append("No fields were extracted.")
        
        # Add validation results
        if 'validation' in result:
            output.append("\n=== VALIDATION ===")
            output.append(f"Is Valid: {result['validation']['is_valid']}")
            
            if result['validation']['errors']:
                output.append("\nErrors:")
                for error in result['validation']['errors']:
                    output.append(f"- {error}")
                    
            if result['validation']['warnings']:
                output.append("\nWarnings:")
                for warning in result['validation']['warnings']:
                    output.append(f"- {warning}")
        
        # Print to console
        print("\n".join(output))
        
        # Write to file
        with open(output_file, 'a') as f:
            f.write("\n".join(output) + "\n\n")
    
    print(f"\nTest results saved to: {os.path.abspath(output_file)}")
    return output_file

def main():
    """Main function to run the document processing pipeline."""
    # Test data extractor with sample text
    test_data_extractor()
    
    # Check if a document path is provided as command line argument
    if len(sys.argv) > 1:
        document_path = sys.argv[1]
        if not os.path.exists(document_path):
            logger.error(f"Document not found: {document_path}")
            sys.exit(1)
            
        if not setup_environment():
            sys.exit(1)
            
        success = process_document(document_path)
        sys.exit(0 if success else 1)
    else:
        print("Usage: python test_pipeline.py <path_to_document>")
        print("\nExample: python test_pipeline.py sample_docs/sample_claim.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
