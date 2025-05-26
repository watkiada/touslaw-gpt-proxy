"""
Windows installation script for OCR dependencies
"""
import os
import sys
import subprocess
import logging
import urllib.request
import zipfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class OCRInstaller:
    """
    Installer for OCR dependencies on Windows
    """
    
    def __init__(self, install_dir=None):
        """
        Initialize OCR installer
        
        Args:
            install_dir: Installation directory (default: app directory)
        """
        if install_dir is None:
            self.install_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
        else:
            self.install_dir = install_dir
        
        # Create installation directory if it doesn't exist
        os.makedirs(self.install_dir, exist_ok=True)
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self):
        """
        Set up logging configuration
        """
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'ocr_installer.log')
        
        # Configure file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def install_tesseract(self):
        """
        Install Tesseract OCR on Windows
        
        Returns:
            Path to Tesseract executable
        """
        logger.info("Installing Tesseract OCR...")
        
        # Tesseract download URL
        tesseract_url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe"
        tesseract_installer = os.path.join(self.install_dir, "tesseract-installer.exe")
        
        # Download Tesseract installer
        try:
            logger.info(f"Downloading Tesseract installer from {tesseract_url}")
            urllib.request.urlretrieve(tesseract_url, tesseract_installer)
            logger.info("Download completed")
        except Exception as e:
            logger.error(f"Error downloading Tesseract installer: {str(e)}")
            return None
        
        # Install Tesseract
        tesseract_install_dir = os.path.join(self.install_dir, "Tesseract-OCR")
        try:
            logger.info(f"Installing Tesseract to {tesseract_install_dir}")
            
            # Run installer with silent options
            cmd = [
                tesseract_installer,
                "/S",  # Silent install
                f"/D={tesseract_install_dir}"  # Installation directory
            ]
            
            subprocess.run(cmd, check=True)
            logger.info("Tesseract installation completed")
            
            # Clean up installer
            os.remove(tesseract_installer)
        except Exception as e:
            logger.error(f"Error installing Tesseract: {str(e)}")
            return None
        
        # Verify installation
        tesseract_exe = os.path.join(tesseract_install_dir, "tesseract.exe")
        if not os.path.exists(tesseract_exe):
            logger.error(f"Tesseract executable not found at {tesseract_exe}")
            return None
        
        logger.info(f"Tesseract installed successfully at {tesseract_exe}")
        return tesseract_exe
    
    def install_python_dependencies(self):
        """
        Install Python dependencies for OCR
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Installing Python dependencies for OCR...")
        
        # List of required packages
        packages = [
            "pytesseract",
            "easyocr",
            "pdf2image",
            "Pillow",
            "numpy",
            "spacy",
            "python-dateutil"
        ]
        
        # Install packages
        try:
            logger.info(f"Installing packages: {', '.join(packages)}")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade"] + packages, check=True)
            logger.info("Package installation completed")
        except Exception as e:
            logger.error(f"Error installing Python packages: {str(e)}")
            return False
        
        # Install spaCy English model
        try:
            logger.info("Installing spaCy English model")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            logger.info("spaCy model installation completed")
        except Exception as e:
            logger.error(f"Error installing spaCy model: {str(e)}")
            return False
        
        return True
    
    def install_poppler(self):
        """
        Install Poppler for PDF processing on Windows
        
        Returns:
            Path to Poppler bin directory
        """
        logger.info("Installing Poppler for PDF processing...")
        
        # Poppler download URL
        poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip"
        poppler_zip = os.path.join(self.install_dir, "poppler.zip")
        
        # Download Poppler
        try:
            logger.info(f"Downloading Poppler from {poppler_url}")
            urllib.request.urlretrieve(poppler_url, poppler_zip)
            logger.info("Download completed")
        except Exception as e:
            logger.error(f"Error downloading Poppler: {str(e)}")
            return None
        
        # Extract Poppler
        poppler_dir = os.path.join(self.install_dir, "poppler")
        try:
            logger.info(f"Extracting Poppler to {poppler_dir}")
            
            # Remove existing directory if it exists
            if os.path.exists(poppler_dir):
                shutil.rmtree(poppler_dir)
            
            # Extract zip file
            with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
            
            # Rename extracted directory
            extracted_dir = os.path.join(self.install_dir, "poppler-23.08.0-0")
            if os.path.exists(extracted_dir):
                os.rename(extracted_dir, poppler_dir)
            
            logger.info("Poppler extraction completed")
            
            # Clean up zip file
            os.remove(poppler_zip)
        except Exception as e:
            logger.error(f"Error extracting Poppler: {str(e)}")
            return None
        
        # Verify installation
        poppler_bin = os.path.join(poppler_dir, "Library", "bin")
        if not os.path.exists(poppler_bin):
            logger.error(f"Poppler bin directory not found at {poppler_bin}")
            return None
        
        logger.info(f"Poppler installed successfully at {poppler_bin}")
        return poppler_bin
    
    def update_environment_variables(self, tesseract_path=None, poppler_path=None):
        """
        Update environment variables for OCR tools
        
        Args:
            tesseract_path: Path to Tesseract executable
            poppler_path: Path to Poppler bin directory
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("Updating environment variables...")
        
        try:
            # Update PATH environment variable
            path_var = os.environ.get('PATH', '')
            
            if tesseract_path:
                tesseract_dir = os.path.dirname(tesseract_path)
                if tesseract_dir not in path_var:
                    os.environ['PATH'] = f"{tesseract_dir};{path_var}"
                    logger.info(f"Added {tesseract_dir} to PATH")
            
            if poppler_path:
                if poppler_path not in path_var:
                    os.environ['PATH'] = f"{poppler_path};{path_var}"
                    logger.info(f"Added {poppler_path} to PATH")
            
            # Set Tesseract path for pytesseract
            if tesseract_path:
                os.environ['TESSERACT_CMD'] = tesseract_path
                logger.info(f"Set TESSERACT_CMD to {tesseract_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error updating environment variables: {str(e)}")
            return False
    
    def install_all(self):
        """
        Install all OCR dependencies
        
        Returns:
            Dictionary with installation results
        """
        logger.info("Starting OCR dependencies installation...")
        
        results = {
            'success': True,
            'tesseract_path': None,
            'poppler_path': None,
            'python_deps': False
        }
        
        # Install Tesseract
        tesseract_path = self.install_tesseract()
        results['tesseract_path'] = tesseract_path
        
        # Install Poppler
        poppler_path = self.install_poppler()
        results['poppler_path'] = poppler_path
        
        # Install Python dependencies
        python_deps = self.install_python_dependencies()
        results['python_deps'] = python_deps
        
        # Update environment variables
        env_updated = self.update_environment_variables(tesseract_path, poppler_path)
        results['env_updated'] = env_updated
        
        # Check overall success
        if not tesseract_path or not poppler_path or not python_deps or not env_updated:
            results['success'] = False
        
        if results['success']:
            logger.info("OCR dependencies installation completed successfully")
        else:
            logger.warning("OCR dependencies installation completed with issues")
        
        return results


if __name__ == "__main__":
    # Run installer when script is executed directly
    installer = OCRInstaller()
    results = installer.install_all()
    
    # Print results
    print("\nInstallation Results:")
    print(f"Overall Success: {'Yes' if results['success'] else 'No'}")
    print(f"Tesseract Path: {results['tesseract_path'] or 'Not installed'}")
    print(f"Poppler Path: {results['poppler_path'] or 'Not installed'}")
    print(f"Python Dependencies: {'Installed' if results['python_deps'] else 'Failed'}")
    print(f"Environment Variables: {'Updated' if results.get('env_updated', False) else 'Not updated'}")
    
    if not results['success']:
        print("\nSome components failed to install. Please check the log file for details.")
        sys.exit(1)
    
    print("\nOCR dependencies installation completed successfully.")
    sys.exit(0)
