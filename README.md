# Watkibot Law Assistant - Deployment and Usage Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [User Management](#user-management)
6. [Document Management](#document-management)
7. [AI Chat Features](#ai-chat-features)
8. [OCR and Data Extraction](#ocr-and-data-extraction)
9. [PDF Form Filling](#pdf-form-filling)
10. [Letter Generation and Saving](#letter-generation-and-saving)
11. [Troubleshooting](#troubleshooting)
12. [Maintenance](#maintenance)
13. [Future Enhancements](#future-enhancements)

## Introduction

Watkibot Law Assistant is a comprehensive document management and AI assistant platform designed specifically for law firms. It provides powerful features for document organization, OCR processing, AI-powered chat, and automated form filling.

This guide will walk you through the deployment, configuration, and usage of the Watkibot Law Assistant platform on your Windows Server 2022 environment.

## System Requirements

### Hardware Requirements
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB+ recommended
- Storage: 500GB SSD (as specified in your environment)
- Network: Stable internet connection

### Software Requirements
- Operating System: Windows Server 2022
- Database: PostgreSQL (automatically installed)
- Web Browser: Chrome, Firefox, or Edge (latest versions)

## Installation

The installation process is automated through scripts provided with the application.

### Pre-Installation Steps
1. Ensure you have administrator privileges on your Windows Server 2022 instance
2. Temporarily disable any antivirus software that might interfere with the installation
3. Ensure your server has internet access to download dependencies

### Installation Steps
1. Copy the entire `myaidrive_clone` folder to your server
2. Navigate to the `installation` folder
3. Right-click on `install.bat` and select "Run as administrator"
4. The script will automatically install all required dependencies:
   - Python 3.11
   - Node.js 20.x
   - Git
   - PostgreSQL
   - OCR dependencies (Tesseract, etc.)
   - Python packages
   - Node.js packages
5. The installation process may take 15-30 minutes depending on your server's performance and internet connection
6. Once completed, the script will create and start Windows services for the backend and frontend

### Verifying Installation
After installation completes:
1. Open a web browser on the server
2. Navigate to http://localhost:3000
3. You should see the Watkibot Law Assistant login page
4. Use the default credentials:
   - Username: admin@watkibot.com
   - Password: admin123

## Configuration

After installation, you need to configure the application with your API keys.

### API Key Configuration
1. Navigate to the `installation` folder
2. Right-click on `configure.bat` and select "Run as administrator"
3. When prompted, enter your:
   - OpenAI API key
   - Pinecone API key
   - Pinecone environment
   - Pinecone index name (optional, defaults to "watkibot-law-assistant")
   - Preferred OpenAI model (optional, defaults to "gpt-4")
4. The script will create a configuration file with your settings
5. Restart the services as instructed by the script

### Accessing from Other Computers
To access the application from other computers on your network:
1. Open Windows Firewall with Advanced Security
2. Ensure that inbound rules for ports 3000 (frontend) and 8000 (backend) are enabled
3. From other computers, access the application using your server's IP address or hostname:
   - http://[server-ip-or-hostname]:3000

### Setting Up for Internet Access
To make the application accessible from the internet:
1. Configure your router to forward ports 3000 and 8000 to your server
2. Alternatively, set up a reverse proxy using IIS or Nginx
3. Consider using a domain name and SSL certificate for secure access

## User Management

### Changing Default Admin Password
After first login:
1. Click on your username in the top-right corner
2. Select "Settings"
3. Click on "Change Password"
4. Enter your current password and new password
5. Click "Save"

### Creating New Users
1. Log in as an administrator
2. Go to "Settings" > "User Management"
3. Click "Add User"
4. Fill in the required information:
   - Email
   - Name
   - Password
   - Office assignment
   - Role (Admin or User)
5. Click "Create User"

### Managing User Access
1. Go to "Settings" > "User Management"
2. Click on a user to edit their details
3. You can:
   - Change their office assignment
   - Modify their role
   - Reset their password
   - Disable their account

## Document Management

### Office and Case Structure
Watkibot Law Assistant organizes documents in a hierarchical structure:
- Offices: Top-level containers for different law firm locations or departments
- Cases: Client cases within each office
- Folders: Optional sub-organization within cases

### Creating a New Office
1. Go to "Settings" > "Office Management"
2. Click "Add Office"
3. Enter the office name and details
4. Click "Create Office"

### Creating a New Case
1. Navigate to the desired office
2. Click "Add Case"
3. Enter the case details:
   - Case name
   - Client information
   - Case type
   - Description
4. Click "Create Case"

### Uploading Documents
1. Navigate to the desired case
2. Click "Upload Documents"
3. Select files from your computer
4. The system will automatically:
   - Upload the documents
   - Process them with OCR
   - Extract metadata
   - Index them for AI search

### Organizing Documents
1. Within a case, you can create folders by clicking "New Folder"
2. Drag and drop documents between folders
3. Use the search function to find documents by content or metadata

## AI Chat Features

### Starting a New Chat
1. Click on "AI Chat" in the main navigation
2. Select a case context (optional)
3. Type your question in the chat box
4. The AI will respond based on the documents in the selected case

### Chat with Document Context
1. When viewing a document, click "Chat about this document"
2. Ask questions specifically about the document
3. The AI will provide answers based on the document content

### Saving and Managing Chats
1. Chats are automatically saved
2. Access previous chats from the "Chat History" section
3. You can rename, delete, or continue any previous chat

## OCR and Data Extraction

### Automatic OCR Processing
When you upload documents, they are automatically processed with OCR to extract text. This happens in the background and may take a few moments for large documents.

### Viewing Extracted Text
1. Open a document
2. Click on the "Text" tab to see the extracted text
3. The system preserves formatting where possible

### Metadata Extraction
The system automatically extracts key information from documents:
1. Open a document
2. Click on the "Metadata" tab
3. View extracted information such as:
   - Dates
   - Names
   - Legal references
   - Key terms

### Manual OCR Processing
If a document needs to be reprocessed:
1. Open the document
2. Click "Actions" > "Reprocess with OCR"
3. Wait for the processing to complete

## PDF Form Filling

### Uploading PDF Forms
1. Navigate to the desired case
2. Click "Upload Documents"
3. Select PDF forms from your computer
4. The system will detect that these are forms

### AI-Powered Form Filling
1. Open a PDF form
2. Click "Fill Form with AI"
3. The system will:
   - Analyze the form fields
   - Search case documents for relevant information
   - Suggest values for each field
4. Review the suggested values
5. Make any necessary adjustments
6. Click "Apply" to fill the form

### Saving Filled Forms
1. After filling a form, click "Save"
2. The filled form will be saved to the case
3. You can download the filled form or share it directly

## Letter Generation and Saving

### Creating AI-Generated Letters
1. From the dashboard or case view, click "Generate Letter"
2. Select the letter type (e.g., demand letter, engagement letter)
3. Enter the recipient information
4. Provide a subject and content instructions
5. Click "Generate"
6. The AI will create a letter based on your instructions and case documents

### Previewing and Editing Letters
1. After generation, the letter will be displayed in the preview pane
2. Review the content for accuracy
3. Make any necessary edits in the editor
4. Format the letter as needed

### Saving Letters to Case Folders
1. After reviewing and editing, click "Save to Case"
2. Select the format:
   - DOCX: Editable Microsoft Word format
   - PDF: Fixed format for final distribution
3. Enter a filename
4. The letter will be saved to the current case folder
5. The saved document will appear in the case documents list

### Using Firm Letterhead
1. Go to "Settings" > "Letterhead"
2. Upload your firm's letterhead or enter the details:
   - Firm name
   - Address
   - Contact information
   - Logo (optional)
3. When generating letters, select "Use Firm Letterhead"
4. The letterhead will be applied to all generated letters

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start
1. Check Windows Services to ensure both services are running:
   - Open Services (services.msc)
   - Look for "Watkibot Law Assistant - Backend" and "Watkibot Law Assistant - Frontend"
   - Ensure both are "Running"
2. Check log files in `C:\WatkibotLawAssistant\logs`

#### OCR Not Working
1. Verify Tesseract is installed correctly:
   - Open Command Prompt
   - Run `tesseract --version`
2. Check document format is supported
3. Try reprocessing the document manually

#### AI Features Not Working
1. Verify API keys are configured correctly:
   - Check `.env` file in `C:\WatkibotLawAssistant\backend`
2. Ensure internet connectivity to OpenAI and Pinecone services
3. Check log files for specific errors

#### Database Connection Issues
1. Verify PostgreSQL service is running
2. Check database connection settings in `.env` file
3. Try restarting the backend service

### Getting Support
If you encounter issues not covered in this guide:
1. Check the log files in `C:\WatkibotLawAssistant\logs`
2. Contact support with the log files attached

## Maintenance

### Backup Procedures
It's recommended to regularly back up:
1. The PostgreSQL database:
   ```
   pg_dump -U postgres watkibot > watkibot_backup.sql
   ```
2. The document storage directory:
   ```
   C:\WatkibotLawAssistant\documents
   ```

### Updating the Application
When updates are available:
1. Stop the services:
   ```
   net stop WatkibotBackend
   net stop WatkibotFrontend
   ```
2. Back up your data
3. Run the update script provided with the update package
4. Restart the services:
   ```
   net start WatkibotBackend
   net start WatkibotFrontend
   ```

### Log Management
Log files are stored in `C:\WatkibotLawAssistant\logs` and are automatically rotated daily. You may want to periodically archive or delete old log files to save disk space.

## Future Enhancements

The Watkibot Law Assistant platform is designed to be modular and extensible. Future enhancements may include:

1. Additional AI model integrations beyond OpenAI
2. Enhanced document comparison features
3. Court filing integrations
4. Client portal access
5. Mobile application

To request new features or provide feedback, please contact support.

---

Thank you for choosing Watkibot Law Assistant. We hope this platform enhances your law firm's document management and AI capabilities.
