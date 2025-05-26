"""
Data extraction service for documents
"""
import os
import re
import logging
from typing import List, Dict, Any, Optional
import spacy
from dateutil import parser as date_parser

from app.services.ocr.ocr_service import OCRService

logger = logging.getLogger(__name__)

class DataExtractionService:
    """
    Service for extracting structured data from documents
    """
    
    def __init__(self):
        """
        Initialize data extraction service
        """
        self.ocr_service = OCRService()
        
        # Load spaCy NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy NLP model")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {str(e)}")
            self.nlp = None
    
    async def extract_data_from_document(self, file_path: str) -> Dict[str, Any]:
        """
        Extract structured data from document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with extracted data
        """
        # Process document with OCR
        ocr_result = await self.ocr_service.process_document(file_path)
        
        if not ocr_result['success']:
            return {
                'success': False,
                'error': ocr_result.get('error', 'OCR processing failed')
            }
        
        # Extract structured data
        extracted_data = await self._extract_structured_data(ocr_result['text'])
        
        return {
            'success': True,
            'text': ocr_result['text'],
            'extracted_data': extracted_data,
            'page_count': ocr_result.get('page_count', 1)
        }
    
    async def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from text using NLP
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with extracted structured data
        """
        if not self.nlp:
            logger.warning("spaCy NLP model not available, skipping NLP-based extraction")
            return self._extract_data_with_regex(text)
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract entities
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        # Extract specific data types
        extracted_data = {
            'entities': entities,
            'dates': self._extract_dates(text, doc),
            'names': self._extract_names(doc),
            'contact_info': self._extract_contact_info(text),
            'case_info': self._extract_case_info(text, doc),
            'monetary_values': self._extract_monetary_values(text, doc)
        }
        
        # Add regex-based extraction for additional fields
        regex_data = self._extract_data_with_regex(text)
        extracted_data.update(regex_data)
        
        return extracted_data
    
    def _extract_dates(self, text: str, doc) -> List[Dict[str, Any]]:
        """
        Extract dates from text
        
        Args:
            text: Document text
            doc: spaCy document
            
        Returns:
            List of extracted dates with context
        """
        dates = []
        
        # Extract dates from spaCy entities
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                try:
                    # Try to parse the date
                    parsed_date = date_parser.parse(ent.text, fuzzy=True)
                    
                    # Get context (text around the date)
                    start_idx = max(0, ent.start_char - 50)
                    end_idx = min(len(text), ent.end_char + 50)
                    context = text[start_idx:end_idx]
                    
                    dates.append({
                        'text': ent.text,
                        'parsed': parsed_date.isoformat(),
                        'context': context
                    })
                except Exception:
                    # Skip dates that can't be parsed
                    pass
        
        # Use regex for additional date formats
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                date_text = match.group(0)
                
                # Skip if already found by spaCy
                if any(date['text'] == date_text for date in dates):
                    continue
                
                try:
                    parsed_date = date_parser.parse(date_text, fuzzy=True)
                    
                    # Get context
                    start_idx = max(0, match.start() - 50)
                    end_idx = min(len(text), match.end() + 50)
                    context = text[start_idx:end_idx]
                    
                    dates.append({
                        'text': date_text,
                        'parsed': parsed_date.isoformat(),
                        'context': context
                    })
                except Exception:
                    # Skip dates that can't be parsed
                    pass
        
        return dates
    
    def _extract_names(self, doc) -> List[Dict[str, str]]:
        """
        Extract person names from document
        
        Args:
            doc: spaCy document
            
        Returns:
            List of extracted names
        """
        names = []
        
        # Extract person names from spaCy entities
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                names.append({
                    'text': ent.text,
                    'type': 'person'
                })
            elif ent.label_ == 'ORG':
                names.append({
                    'text': ent.text,
                    'type': 'organization'
                })
        
        return names
    
    def _extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """
        Extract contact information from text
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with extracted contact information
        """
        contact_info = {
            'emails': [],
            'phones': [],
            'addresses': []
        }
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contact_info['emails'] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_patterns = [
            r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',  # (123) 456-7890
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',   # 123-456-7890
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        contact_info['phones'] = phones
        
        # Extract addresses (simplified approach)
        address_pattern = r'\b\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl|Terrace|Ter)[,\s]+[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        
        # Clean up addresses
        contact_info['addresses'] = [addr.strip() for addr in addresses]
        
        return contact_info
    
    def _extract_case_info(self, text: str, doc) -> Dict[str, Any]:
        """
        Extract case-related information
        
        Args:
            text: Document text
            doc: spaCy document
            
        Returns:
            Dictionary with case information
        """
        case_info = {
            'case_numbers': [],
            'court_references': [],
            'legal_citations': []
        }
        
        # Extract case numbers
        case_number_patterns = [
            r'\bCase\s+No\.?\s+\d+[-A-Za-z0-9]+\b',
            r'\bCase\s+Number:?\s+\d+[-A-Za-z0-9]+\b',
            r'\bCase\s+ID:?\s+\d+[-A-Za-z0-9]+\b',
            r'\b[A-Z]{2,}-\d{2,}-\d{3,}\b'  # Format like CV-21-12345
        ]
        
        for pattern in case_number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            case_info['case_numbers'].extend(matches)
        
        # Extract court references
        court_patterns = [
            r'\b(?:United States|U\.S\.|Superior|District|Circuit|Federal|State|County|Municipal|Supreme) Court\b',
            r'\bCourt of (?:Appeals|Common Pleas|Claims)\b'
        ]
        
        for pattern in court_patterns:
            matches = re.findall(pattern, text)
            case_info['court_references'].extend(matches)
        
        # Extract legal citations
        citation_patterns = [
            r'\b\d+\s+U\.S\.\s+\d+\b',  # US Reports
            r'\b\d+\s+F\.\d+\s+\d+\b',   # Federal Reporter
            r'\b\d+\s+S\.Ct\.\s+\d+\b'   # Supreme Court Reporter
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            case_info['legal_citations'].extend(matches)
        
        return case_info
    
    def _extract_monetary_values(self, text: str, doc) -> List[Dict[str, Any]]:
        """
        Extract monetary values from text
        
        Args:
            text: Document text
            doc: spaCy document
            
        Returns:
            List of extracted monetary values with context
        """
        monetary_values = []
        
        # Extract from spaCy entities
        for ent in doc.ents:
            if ent.label_ == 'MONEY':
                # Get context
                start_idx = max(0, ent.start_char - 50)
                end_idx = min(len(text), ent.end_char + 50)
                context = text[start_idx:end_idx]
                
                monetary_values.append({
                    'text': ent.text,
                    'context': context
                })
        
        # Use regex for additional monetary formats
        money_patterns = [
            r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',  # $1,234.56
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars',  # 1,234.56 dollars
        ]
        
        for pattern in money_patterns:
            for match in re.finditer(pattern, text):
                money_text = match.group(0)
                
                # Skip if already found by spaCy
                if any(money['text'] == money_text for money in monetary_values):
                    continue
                
                # Get context
                start_idx = max(0, match.start() - 50)
                end_idx = min(len(text), match.end() + 50)
                context = text[start_idx:end_idx]
                
                monetary_values.append({
                    'text': money_text,
                    'context': context
                })
        
        return monetary_values
    
    def _extract_data_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Extract data using regex patterns
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        
        # Extract SSNs
        ssn_pattern = r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
        ssns = re.findall(ssn_pattern, text)
        if ssns:
            extracted_data['ssn'] = ssns
        
        # Extract driver's license numbers (generic pattern)
        dl_pattern = r'\b[A-Z]\d{7}\b'  # Example format: A1234567
        dls = re.findall(dl_pattern, text)
        if dls:
            extracted_data['drivers_license'] = dls
        
        # Extract zip codes
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        zips = re.findall(zip_pattern, text)
        if zips:
            extracted_data['zip_codes'] = zips
        
        # Extract potential client IDs
        client_id_pattern = r'\bClient\s+ID:?\s+([A-Za-z0-9-]+)\b'
        client_ids = re.findall(client_id_pattern, text, re.IGNORECASE)
        if client_ids:
            extracted_data['client_ids'] = client_ids
        
        # Extract potential file numbers
        file_number_pattern = r'\bFile\s+(?:No|Number):?\s+([A-Za-z0-9-]+)\b'
        file_numbers = re.findall(file_number_pattern, text, re.IGNORECASE)
        if file_numbers:
            extracted_data['file_numbers'] = file_numbers
        
        return extracted_data
    
    async def categorize_document(self, file_path: str) -> Dict[str, Any]:
        """
        Categorize document type based on content
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with document category and confidence
        """
        # Process document with OCR
        ocr_result = await self.ocr_service.process_document(file_path)
        
        if not ocr_result['success']:
            return {
                'success': False,
                'error': ocr_result.get('error', 'OCR processing failed')
            }
        
        # Categorize document
        category_result = self._determine_document_category(ocr_result['text'])
        
        return {
            'success': True,
            'category': category_result['category'],
            'confidence': category_result['confidence'],
            'subcategory': category_result.get('subcategory'),
            'keywords': category_result.get('keywords', [])
        }
    
    def _determine_document_category(self, text: str) -> Dict[str, Any]:
        """
        Determine document category based on content
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with category, confidence, and subcategory
        """
        # Define document categories with keywords
        categories = {
            'contract': ['agreement', 'contract', 'terms', 'parties', 'hereby', 'obligations', 'clause', 'covenant'],
            'court_filing': ['court', 'plaintiff', 'defendant', 'case', 'docket', 'motion', 'petition', 'filed', 'judge', 'hearing'],
            'correspondence': ['dear', 'sincerely', 'regards', 'letter', 'attention', 'reference'],
            'financial': ['invoice', 'payment', 'amount', 'balance', 'due', 'total', 'fee', 'account', 'transaction'],
            'identification': ['identification', 'license', 'passport', 'id', 'birth', 'certificate', 'ssn', 'social security'],
            'medical': ['medical', 'health', 'doctor', 'patient', 'hospital', 'diagnosis', 'treatment', 'prescription'],
            'form': ['form', 'fill', 'complete', 'questionnaire', 'application', 'intake']
        }
        
        # Define subcategories
        subcategories = {
            'contract': ['employment', 'lease', 'purchase', 'service', 'settlement', 'confidentiality', 'non-disclosure'],
            'court_filing': ['complaint', 'answer', 'motion', 'order', 'judgment', 'subpoena', 'affidavit', 'declaration'],
            'correspondence': ['client', 'opposing_counsel', 'court', 'witness', 'expert', 'internal'],
            'financial': ['invoice', 'receipt', 'statement', 'bill', 'estimate', 'tax'],
            'form': ['intake', 'application', 'questionnaire', 'consent', 'authorization', 'registration']
        }
        
        # Count keyword occurrences for each category
        category_scores = {category: 0 for category in categories}
        found_keywords = {category: [] for category in categories}
        
        # Normalize text for better matching
        text_lower = text.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    category_scores[category] += count
                    found_keywords[category].append(keyword)
        
        # Find the category with the highest score
        if all(score == 0 for score in category_scores.values()):
            return {
                'category': 'unknown',
                'confidence': 0.0
            }
        
        max_score = max(category_scores.values())
        best_category = max(category_scores, key=category_scores.get)
        
        # Calculate confidence (normalized score)
        total_score = sum(category_scores.values())
        confidence = category_scores[best_category] / total_score
        
        # Determine subcategory if available
        subcategory = None
        if best_category in subcategories:
            subcategory_scores = {}
            for sub in subcategories[best_category]:
                subcategory_scores[sub] = 0
                for keyword in sub.split('_'):
                    subcategory_scores[sub] += text_lower.count(keyword.lower())
            
            if any(score > 0 for score in subcategory_scores.values()):
                subcategory = max(subcategory_scores, key=subcategory_scores.get)
        
        return {
            'category': best_category,
            'confidence': confidence,
            'subcategory': subcategory,
            'keywords': found_keywords[best_category]
        }
