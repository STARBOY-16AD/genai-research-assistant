GenAI Research Assistant
GenAI Research Assistant is an AI-powered tool for analyzing documents (PDF, TXT, DOCX) through summarization, question-answering, and challenge-based comprehension testing. Built with FastAPI for the backend and Streamlit for the frontend, it leverages OpenAI or Anthropic LLMs and ChromaDB for vector storage to provide intelligent document processing.
Features

Document Upload: Upload PDF, TXT, or DOCX files (up to 10MB) for analysis.
Summarization: Generate concise summaries of uploaded documents.
Ask Anything: Ask questions about the document, with answers sourced from relevant sections.
Challenge Mode: Test your understanding with AI-generated questions that require reasoning.
Vector Search: Uses sentence embeddings and ChromaDB for efficient context retrieval.
Responsive UI: Streamlit-based interface with navigation, progress tracking, and source references.

Project Structure
genai-research-assistant/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── backend/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes.py
│   │   │   └── models.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── document_processor.py
│   │   │   ├── ai_engine.py
│   │   │   └── storage.py
│   │   └── utils/
│   │       └── helpers.py
│   ├── frontend/
│   │   ├── app.py
│   │   ├── components/
│   │   │   ├── upload.py
│   │   │   ├── summary.py
│   │   │   ├── ask_anything.py
│   │   │   └── challenge_mode.py
│   │   └── utils/
│   │       └── ui_helpers.py
│   └── shared/
│       └── models.py
├── tests/
│   ├── test_api.py
│   ├── test_document_processor.py
│   └── test_ai_engine.py
├── uploads/
├── data/
└── scripts/
    ├── setup.sh
    └── run.sh

Prerequisites

Python 3.8+
Virtualenv (recommended)
API keys for OpenAI or Anthropic (optional for alternative LLM)

Setup

Clone the Repository:
git clone <repository-url>
cd genai-research-assistant


Run Setup Script:
chmod +x scripts/setup.sh
./scripts/setup.sh

This creates a virtual environment, installs dependencies, and sets up .env.

Configure Environment Variables:

Copy .env.example to .env:cp .env.example .env


Edit .env to add your API keys:OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key




Activate Virtual Environment:
source venv/bin/activate



Running the Application

Run Both Backend and Frontend:
chmod +x scripts/run.sh
./scripts/run.sh


Backend: http://localhost:8000
Frontend: http://localhost:8501


Access the App:

Open http://localhost:8501 in your browser.
Upload a document, view its summary, ask questions, or start a challenge.



Testing
Run unit tests to verify functionality:
source venv/bin/activate
pytest tests/ -v

Tests cover:

API endpoints (test_api.py)
Document processing (test_document_processor.py)
AI engine functionality (test_ai_engine.py)

Usage

Upload Document:

Go to the upload section, select a PDF, TXT, or DOCX file, and click "Upload and Process".
Maximum file size: 10MB.


View Summary:

After uploading, select "Document Summary" to see an AI-generated summary.


Ask Questions:

Choose "Ask Anything" to query the document. Answers include justifications and source references.


Challenge Mode:

Select "Challenge Me" to generate 3–5 questions testing comprehension and reasoning.
Submit answers and receive scores with feedback.



Dependencies
Key dependencies (see requirements.txt):

FastAPI & Uvicorn: Backend API
Streamlit: Frontend interface
PyPDF2, pdfplumber, python-docx: Document processing
openai, anthropic: LLM integration
sentence-transformers, chromadb: Vector search
pytest, httpx: Testing

Contributing

Fork the repository.
Create a feature branch: git checkout -b feature/your-feature.
Commit changes: git commit -m "Add your feature".
Push to the branch: git push origin feature/your-feature.
Open a pull request.

License
MIT License. See LICENSE for details.
Contact
For issues or suggestions, open a GitHub issue or contact the maintainers.
