GenAI Research Assistant

Overview:
The GenAI Research Assistant is an AI-powered web application designed for document analysis and interactive learning. It allows users to upload documents (PDF, TXT, DOCX), generate summaries, ask questions, and engage in a "Challenge Me" mode with AI-generated questions. Built with a Streamlit frontend and FastAPI backend, it leverages AI models (OpenAI, Anthropic) and a ChromaDB vector store for efficient document processing and retrieval. The project is developed in Python 3.10.9 and runs on Windows, with the frontend at http://localhost:8502 and backend at http://localhost:8000.
Features

Document Upload: Upload PDF, TXT, or DOCX files with a progress bar and preview (first 500 characters).
Document Summary: Generate bulleted summaries of uploaded documents using AI models.
Ask Anything: Query documents with multi-document support, view up to 5 source chunks, and maintain a searchable conversation history with clear/download options.
Challenge Me Mode: Generate 3-5 AI-crafted questions per document, submit answers, and receive scores (0-100), feedback, and reference chunks.
UI Enhancements: 
Theme toggle (light/dark).
Searchable conversation history.
Smooth navigation and responsive design.


AI Integration: Supports OpenAI and Anthropic (Claude) models for advanced reasoning and Q&A.
Backend: FastAPI with CORS, ChromaDB for vector storage, and robust document processing.
Error Handling: User-friendly success/error messages and debug logging.

Project Structure
genai-research-assistant/
├── src/
│   ├── backend/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── ai_engine.py
│   │   │   ├── document_processor.py
│   │   │   └── config.py
│   │   └── main.py
│   ├── frontend/
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py
│   │   │   ├── ask_anything.py
│   │   │   ├── summary.py
│   │   │   └── challenge_mode.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── ui_helpers.py
│   │   └── app.py
├── uploads/
├── data/
│   └── vector_db/
├── logs/
├── tests/
│   └── test_ai_engine.py
├── .env
├── requirements.txt
├── stop_streamlit.ps1
└── README.md

Prerequisites

Python: 3.10.9
OS: Windows (tested on Windows 10/11)
Tools: 
VS Code with PowerShell or cmd terminal
Git (optional for version control)


API Keys: 
OpenAI API key (OPENAI_API_KEY)
Anthropic API key (ANTHROPIC_API_KEY)



Installation

Clone the Repository (if using Git):
git clone https://github.com/STARBOY-16AD/genai-research-assistant
cd genai-research-assistant

Or use the existing directory:
cd C:\Users\Sumanjeet\Documents\PROJECTS\genai-research-assistant


Create and Activate Virtual Environment:
python -m venv venv
.\venv\Scripts\Activate.ps1


Install Dependencies:Save the following as requirements.txt:
streamlit==1.39.0
fastapi==0.115.2
uvicorn==0.32.0
chromadb==0.5.15
openai==1.51.2
anthropic==0.37.1
pdfplumber==0.11.4
python-docx==1.1.2
sentence-transformers==3.2.0
loguru==0.7.2
pydantic-settings==2.6.0
PyPDF2==3.0.1
aiofiles==24.1.0
requests==2.32.3

Install:
pip install -r requirements.txt


Set Up Environment Variables:Create .env in the project root:
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

Replace your_openai_key and your_anthropic_key with your API keys.

Create Directories:
mkdir uploads
mkdir data\vector_db
mkdir logs
mkdir src\frontend\components
mkdir src\frontend\utils


Verify __init__.py Files:Ensure empty __init__.py files exist:
New-Item -Path src\frontend\components\__init__.py -ItemType File
New-Item -Path src\frontend\utils\__init__.py -ItemType File



Running the Application

Start the Backend:
cd C:\Users\Sumanjeet\Documents\PROJECTS\genai-research-assistant
.\venv\Scripts\Activate.ps1
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug


Verify: http://localhost:8000/api/v1 returns {"message":"Welcome to GenAI Research Assistant API"}.


Start the Frontend (use cmd for reliable Ctrl+C):Open a new terminal (Ctrl + ~, set to cmd):
cd C:\Users\Sumanjeet\Documents\PROJECTS\genai-research-assistant
venv\Scripts\activate
python -m streamlit run src/frontend/app.py --server.port 8502 --server.address 0.0.0.0

Or in PowerShell:
python -m streamlit run src/frontend/app.py --server.port 8502 --server.address 0.0.0.0 --server.fileWatcherType none --logger.level debug


Access the App:

Open http://localhost:8502 in a browser.
Upload a document, test features, and check debug messages (DEBUG: API URL is ...).



Usage

Upload Document:

Navigate to http://localhost:8502.
Upload a PDF, TXT, or DOCX file (<10MB).
View progress bar and document preview.


Document Summary:

Select "Summary" mode.
Choose a document and click "Generate Summary" for a bulleted summary.


Ask Anything:

Select "Ask Anything" mode.
Choose one or more documents.
Ask a question, view answers with up to 5 source chunks.
Search, clear, or download conversation history.


Challenge Me:

Select "Challenge Me" mode.
Generate 3-5 questions, answer them, and receive scores (0-100), feedback, and references.


UI Features:

Toggle between light/dark themes in the sidebar.
Navigate modes and documents seamlessly.



Troubleshooting

Network Error: http://localhost:8000/api/v1 cannot be reached:

Verify backend:Invoke-RestMethod -Uri http://localhost:8000/api/v1


Check debug messages at http://localhost:8502 (e.g., DEBUG: Response status: ...).
Ensure CORS in src/backend/main.py includes http://localhost:8502.
Test port:Test-NetConnection -ComputerName localhost -Port 8000


Clear Streamlit cache:Remove-Item -Path .streamlit\cache -Recurse -Force -ErrorAction SilentlyContinue




Ctrl+C Not Working:

Use cmd for running Streamlit.
Stop processes:Get-Process | Where-Object {$_.Path -like "*python.exe*" -and $_.CommandLine -like "*streamlit*"} | Stop-Process -Force


Or use stop_streamlit.ps1.


ImportError:

Verify __init__.py files in src/frontend/components and src/frontend/utils.
Check absolute imports in frontend files.


Dependencies:
pip show streamlit fastapi chromadb openai anthropic pdfplumber python-docx
pip install -r requirements.txt



Testing
Run unit tests for the AI engine:
pytest tests/test_ai_engine.py

Example test file:
import pytest
from src.backend.core.ai_engine import AIEngine

@pytest.fixture
def ai_engine():
    return AIEngine()

@pytest.mark.asyncio
async def test_answer_question(ai_engine):
    result = await ai_engine.answer_question("Test question", ["doc1"])
    assert "answer" in result
    assert "source_chunks" in result

Deployment

Docker:
Use Dockerfile and docker-compose.yml (request if needed).
Build and run:docker-compose up --build





Contributing

Fork the repository.
Create a feature branch (git checkout -b feature-name).
Commit changes (git commit -m "Add feature").
Push (git push origin feature-name).
Open a pull request.

License
MIT License (modify as needed).
