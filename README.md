# Healthcare Document Processing

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)


This project implements a document processing pipeline for healthcare insurance documents using Azure's AI services. It provides end-to-end document processing including classification, OCR, and structured data extraction.

## ✨ Features

- **Document Classification**: Automatically identify document types (insurance claims, medical reports, prescriptions, etc.)
- **OCR Text Extraction**: Extract text from various document formats with high accuracy
- **Structured Data Extraction**: Convert unstructured text into structured data with validation
- **Multi-stage Processing**: Intelligent pipeline with classification, OCR, and data extraction
- **REST API**: Easy integration with existing systems
- **Configurable**: Support for custom document types and extraction rules
- **Validation**: Built-in validation for extracted data

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Azure account with Form Recognizer and Computer Vision services
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/healthcare-doc-processing.git
   cd healthcare-doc-processing
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

### Usage

#### Run tests with sample data
```bash
python test_pipeline.py
```

#### Start the API server
```bash
uvicorn src.main:app --reload --port 8001
```

Access the API documentation at: http://localhost:8001/docs

## 📁 Project Structure

```
healthcare-doc-processing/
├── src/                      # Source code
│   ├── __init__.py
│   ├── data_extractor.py     # Structured data extraction
│   ├── document_processor.py # Main processing logic
│   └── main.py              # FastAPI application
├── tests/                   # Test files
├── test_pipeline.py         # Test script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Prerequisites

- Python 3.8+
- Azure subscription with:
  - Form Recognizer service
  - Computer Vision service
- Azure CLI (for deployment)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd healthcare-doc-processing
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values with your Azure service credentials

## Running the Application

1. Start the FastAPI server:
   ```bash
   cd src
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /upload/` - Upload and process a document
- `GET /health` - Health check endpoint

### Example Request

```bash
curl -X 'POST' \
  'http://localhost:8000/upload/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/document.pdf;type=application/pdf'
```

## Project Structure

```
healthcare-doc-processing/
├── src/
│   ├── __init__.py
│   ├── document_processor.py  # Core document processing logic
│   └── main.py               # FastAPI application
├── tests/                    # Unit and integration tests
├── uploads/                  # Temporary storage for uploaded files
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Deployment

### Azure App Service

1. Create an App Service plan and web app:
   ```bash
   az group create --name myResourceGroup --location eastus
   az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name <app-name> --runtime "PYTHON:3.9"
   ```

2. Configure application settings:
   ```bash
   az webapp config appsettings set --resource-group myResourceGroup --name <app-name> --settings \
     AZURE_FORM_RECOGNIZER_ENDPOINT="your-endpoint" \
     AZURE_FORM_RECOGNIZER_KEY="your-key" \
     AZURE_COMPUTER_VISION_ENDPOINT="your-endpoint" \
     AZURE_COMPUTER_VISION_KEY="your-key"
   ```

3. Deploy the application:
   ```bash
   az webapp up --resource-group myResourceGroup --name <app-name> --runtime "PYTHON:3.9"
   ```

## Testing

Run the test suite:

```bash
pytest tests/
```

