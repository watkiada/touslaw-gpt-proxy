"""
OCR service implementation using Tesseract and EasyOCR
"""
import os
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
import pytesseract
from PIL import Image
import easyocr
import pdf2image
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    """
    Service for OCR text extraction from documents
    """
    
    def __init__(self):
        """
        Initialize OCR service with Tesseract and EasyOCR
        """
        self.tesseract_path = settings.TESSERACT_PATH
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        
        # Initialize EasyOCR reader
        self.reader = None
        self.languages = ['en']  # Default to English
    
    def _lazy_load_easyocr(self):
        """
        Lazy load EasyOCR reader to avoid loading it on startup
        """
        if self.reader is None:
            try:
                self.reader = easyocr.Reader(self.languages)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing EasyOCR: {str(e)}")
                raise
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process document with OCR and extract text
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.pdf']:
            return await self._process_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return await self._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    async def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process PDF document with OCR
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            # Process each page
            pages = []
            for i, image in enumerate(images):
                # Process image with OCR
                page_text, page_data = await self._extract_text_from_image(np.array(image))
                
                pages.append({
                    'page_num': i + 1,
                    'text': page_text,
                    'data': page_data
                })
            
            # Combine results
            full_text = "\n\n".join([page['text'] for page in pages])
            
            return {
                'success': True,
                'text': full_text,
                'pages': pages,
                'page_count': len(pages)
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process image document with OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        logger.info(f"Processing image: {image_path}")
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Process image with OCR
            text, data = await self._extract_text_from_image(np.array(image))
            
            return {
                'success': True,
                'text': text,
                'data': data,
                'page_count': 1
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _extract_text_from_image(self, image: np.ndarray) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract text from image using OCR
        
        Args:
            image: Image as numpy array
            
        Returns:
            Tuple of (extracted text, structured data)
        """
        # Try Tesseract first
        try:
            text = pytesseract.image_to_string(image)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Convert to structured format
            structured_data = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    structured_data.append({
                        'text': data['text'][i],
                        'conf': data['conf'][i],
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            # If Tesseract result is empty or poor quality, try EasyOCR
            if not text.strip() or len(structured_data) < 5:
                logger.info("Tesseract result is empty or poor quality, trying EasyOCR")
                return await self._extract_text_with_easyocr(image)
            
            return text, structured_data
            
        except Exception as e:
            logger.warning(f"Tesseract OCR failed: {str(e)}, trying EasyOCR")
            return await self._extract_text_with_easyocr(image)
    
    async def _extract_text_with_easyocr(self, image: np.ndarray) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract text from image using EasyOCR
        
        Args:
            image: Image as numpy array
            
        Returns:
            Tuple of (extracted text, structured data)
        """
        try:
            self._lazy_load_easyocr()
            result = self.reader.readtext(image)
            
            # Convert to text and structured format
            text_parts = []
            structured_data = []
            
            for detection in result:
                bbox, text, conf = detection
                text_parts.append(text)
                
                # Calculate bounding box properties
                x_min = min(point[0] for point in bbox)
                y_min = min(point[1] for point in bbox)
                x_max = max(point[0] for point in bbox)
                y_max = max(point[1] for point in bbox)
                
                structured_data.append({
                    'text': text,
                    'conf': conf * 100,  # Convert to percentage
                    'x': int(x_min),
                    'y': int(y_min),
                    'width': int(x_max - x_min),
                    'height': int(y_max - y_min)
                })
            
            text = "\n".join(text_parts)
            return text, structured_data
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {str(e)}")
            return "", []

    async def extract_form_fields(self, file_path: str) -> Dict[str, Any]:
        """
        Extract form fields from a document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with extracted form fields
        """
        # Process document with OCR
        ocr_result = await self.process_document(file_path)
        
        if not ocr_result['success']:
            return {
                'success': False,
                'error': ocr_result.get('error', 'OCR processing failed')
            }
        
        # Extract potential form fields
        form_fields = self._identify_form_fields(ocr_result)
        
        return {
            'success': True,
            'form_fields': form_fields
        }
    
    def _identify_form_fields(self, ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify potential form fields from OCR result
        
        Args:
            ocr_result: OCR processing result
            
        Returns:
            List of identified form fields
        """
        form_fields = []
        
        # Process each page
        for page in ocr_result.get('pages', []):
            page_num = page['page_num']
            
            # Look for common form field patterns in the structured data
            for item in page.get('data', []):
                text = item['text'].strip()
                
                # Skip empty or very short text
                if len(text) < 2:
                    continue
                
                # Check if this looks like a form field label
                if text.endswith(':') or text.endswith('?'):
                    # This might be a form field label
                    form_fields.append({
                        'type': 'label',
                        'text': text.rstrip(':?'),
                        'page': page_num,
                        'position': {
                            'x': item['x'],
                            'y': item['y'],
                            'width': item['width'],
                            'height': item['height']
                        }
                    })
                
                # Check for common form field keywords
                keywords = ['name', 'address', 'phone', 'email', 'date', 'signature', 
                           'social security', 'ssn', 'dob', 'birth', 'gender', 'sex',
                           'city', 'state', 'zip', 'country', 'number', 'id', 'license']
                
                if any(keyword in text.lower() for keyword in keywords):
                    form_fields.append({
                        'type': 'potential_field',
                        'text': text,
                        'page': page_num,
                        'position': {
                            'x': item['x'],
                            'y': item['y'],
                            'width': item['width'],
                            'height': item['height']
                        }
                    })
        
        return form_fields
