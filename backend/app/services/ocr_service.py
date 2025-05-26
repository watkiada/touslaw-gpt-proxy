"""
OCR service for text extraction from images and scanned documents
"""
import os
import tempfile
from typing import List, Optional
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import easyocr

from app.core.config import settings


class OCRService:
    """Service for OCR text extraction"""
    
    def __init__(self, use_tesseract: bool = True, use_easyocr: bool = False, languages: List[str] = None):
        """
        Initialize OCR service
        
        Args:
            use_tesseract: Whether to use Tesseract OCR
            use_easyocr: Whether to use EasyOCR
            languages: List of language codes for OCR
        """
        self.use_tesseract = use_tesseract
        self.use_easyocr = use_easyocr
        self.languages = languages or settings.OCR_LANGUAGES
        
        # Initialize EasyOCR if enabled
        if self.use_easyocr:
            self.reader = easyocr.Reader(self.languages)
    
    async def process_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
            
        Raises:
            Exception: If OCR fails
        """
        try:
            if self.use_tesseract:
                # Use Tesseract OCR
                return pytesseract.image_to_string(Image.open(image_path), lang='+'.join(self.languages))
            elif self.use_easyocr:
                # Use EasyOCR
                results = self.reader.readtext(image_path)
                return '\n'.join([result[1] for result in results])
            else:
                raise ValueError("No OCR engine enabled")
        except Exception as e:
            raise Exception(f"Error processing image with OCR: {str(e)}")
    
    async def process_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract text from PDF, using OCR for scanned pages
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of extracted text by page
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            # Convert PDF to images
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(pdf_path, dpi=300, output_folder=temp_dir)
                
                # Process each page
                results = []
                for i, image in enumerate(images):
                    # Save image to temp file
                    image_path = os.path.join(temp_dir, f"page_{i}.png")
                    image.save(image_path, "PNG")
                    
                    # Extract text with OCR
                    text = await self.process_image(image_path)
                    results.append(text)
                
                return results
        except Exception as e:
            raise Exception(f"Error processing PDF with OCR: {str(e)}")
    
    async def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Check if PDF is scanned (image-based) or contains text
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF is scanned, False if it contains text
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            # Use poppler-utils to check for text
            import subprocess
            result = subprocess.run(
                ["pdftotext", pdf_path, "-"],
                capture_output=True,
                text=True
            )
            
            # If output is empty or very short, likely a scanned PDF
            return len(result.stdout.strip()) < 100
        except Exception as e:
            raise Exception(f"Error checking if PDF is scanned: {str(e)}")
