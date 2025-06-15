import re
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareDataExtractor:
    """Extract structured data from healthcare documents."""
    
    def __init__(self):
        # Common patterns for healthcare documents
        self.patterns = {
            'patient_name': r'(?i)(?:patient|name)[:\s]*(\w+(?:\s+\w+)*)',
            'date_of_birth': r'(?i)(?:dob|date of birth)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'member_id': r'(?i)(?:member\s*id|policy\s*number)[:\s]*(\w+)',
            'date_of_service': r'(?i)(?:date of service|service date|dos)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'provider_name': r'(?i)(?:provider|doctor|physician)[:\s]*(\w+(?:\s+\w+)*)',
            'diagnosis_code': r'(?i)(?:diagnosis|dx)[\s\w]*code[\s:]*([A-Z]\d{2,5}(?:\.\d+)?)',
            'procedure_code': r'(?i)(?:procedure|tx|treatment)[\s\w]*code[\s:]*([A-Z]\d{1,4}[A-Z]?\d{0,4})',
            'amount': r'(?i)(?:amount|total|charge|balance)[\s:]*\$?\s*(\d+(?:\.\d{2})?)',
            'phone': r'(?i)(?:phone|tel|mobile)[\s:]*([\(]?\d{3}[-\s\.\)]?\s*\d{3}[-\s\.]?\s*\d{4})'
        }
        
        # Document type specific patterns
        self.doc_type_patterns = {
            'insurance_claim': {
                'claim_number': r'(?i)(?:claim\s*#?|id)[\s:]*([A-Z0-9-]+)',
                'group_number': r'(?i)group\s*#?[\s:]*(\w+)',
                'adjustment_reason': r'(?i)adjustment\s*reason[\s:]*(\w[\w\s]+?)(?=\n|$)',
                'patient_responsibility': r'(?i)patient\s*responsibility[\s:]*\$?\s*(\d+\.\d{2})'
            },
            'prescription': {
                'medication': r'(?i)medication[\s:]*([\w\s-]+)(?=\n|$)',
                'dosage': r'(?i)dosage[\s:]*([\d\s\w/]+)(?=\n|$)',
                'frequency': r'(?i)frequency[\s:]*([\w\s]+)(?=\n|$)',
                'refills': r'(?i)refills?[\s:]*(\d+)',
                'prescriber': r'(?i)prescriber[\s:]*([\w\s\.]+)(?=\n|$)'
            },
            'medical_report': {
                'report_type': r'(?i)report\s*type[\s:]*([\w\s]+)(?=\n|$)',
                'findings': r'(?i)findings[\s:]*([\w\s\.,-]+)(?=\n|\Z)',
                'impression': r'(?i)impression[\s:]*([\w\s\.,-]+)(?=\n|\Z)',
                'recommendations': r'(?i)recommendations?[\s:]*([\w\s\.,-]+)(?=\n|\Z)'
            }
        }

    def extract_structured_data(self, text: str, doc_type: str = None) -> Dict[str, Any]:
        """
        Extract structured data from document text.
        
        Args:
            text: Extracted text from OCR
            doc_type: Document type (e.g., 'insurance_claim', 'prescription')
            
        Returns:
            Dictionary of extracted fields and their values
        """
        if not text:
            return {}
            
        # Initialize result with basic metadata
        result = {
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'document_type': doc_type or 'unknown',
            'extracted_fields': {}
        }
        
        try:
            # Extract common fields
            common_fields = self._extract_using_patterns(text, self.patterns)
            result['extracted_fields'].update(common_fields)
            
            # Extract document type specific fields
            if doc_type and doc_type in self.doc_type_patterns:
                doc_specific = self._extract_using_patterns(
                    text, 
                    self.doc_type_patterns[doc_type]
                )
                result['extracted_fields'].update(doc_specific)
            
            # Post-process extracted data
            result['extracted_fields'] = self._post_process_fields(
                result['extracted_fields']
            )
            
            # Add validation results
            result['validation'] = self._validate_extracted_data(
                result['extracted_fields'], 
                doc_type
            )
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _extract_using_patterns(self, text: str, patterns: Dict) -> Dict[str, str]:
        """Extract fields using regex patterns."""
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                # Get the first capturing group (the value we want)
                value = match.group(1).strip() if match.groups() else match.group(0).strip()
                extracted[field] = value
        return extracted
    
    def _post_process_fields(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Clean and normalize extracted fields."""
        processed = {}
        for key, value in fields.items():
            if not value:
                continue
                
            # Clean up the value
            cleaned = value.strip()
            
            # Convert numeric fields
            if key in ['amount', 'patient_responsibility']:
                try:
                    cleaned = float(cleaned.replace('$', '').replace(',', '').strip())
                except (ValueError, AttributeError):
                    pass
            
            # Convert date fields
            elif 'date' in key.lower() or 'dob' in key.lower():
                cleaned = self._parse_date(cleaned)
            
            processed[key] = cleaned
            
        return processed
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string into ISO format."""
        if not date_str:
            return None
            
        try:
            # Try common date formats
            for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.date().isoformat()
                except ValueError:
                    continue
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {str(e)}")
            
        return date_str  # Return original if parsing fails
    
    def _validate_extracted_data(self, fields: Dict[str, Any], doc_type: str = None) -> Dict[str, Any]:
        """Validate extracted data against business rules."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required fields by document type
        required_fields = {
            'insurance_claim': ['patient_name', 'member_id', 'date_of_service'],
            'prescription': ['patient_name', 'medication', 'dosage'],
            'medical_report': ['patient_name', 'report_type']
        }
        
        # Check required fields
        if doc_type in required_fields:
            for field in required_fields[doc_type]:
                if field not in fields or not fields[field]:
                    validation['is_valid'] = False
                    validation['errors'].append(f"Missing required field: {field}")
        
        # Validate date formats
        for field, value in fields.items():
            if isinstance(value, str) and ('date' in field.lower() or 'dob' in field.lower()):
                try:
                    datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    validation['warnings'].append(f"Invalid date format for {field}: {value}")
        
        return validation

# Example usage
if __name__ == "__main__":
    # Example text from a document
    sample_text = """
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
    
    extractor = HealthcareDataExtractor()
    result = extractor.extract_structured_data(sample_text, 'insurance_claim')
    
    import json
    print(json.dumps(result, indent=2))
