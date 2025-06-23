import pytest
import httpx
import os
from fastapi import FastAPI
from pathlib import Path
from src.backend.main import app
from src.backend.core.config import settings

@pytest.fixture
async def client():
    """Create an HTTP client for testing"""
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF file for testing"""
    pdf_path = tmp_path / "test.pdf"
    # Create a simple PDF (minimal content for testing)
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Test document content) Tj ET\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")
    return pdf_path

@pytest.mark.asyncio
async def test_upload_document(client, sample_pdf, monkeypatch):
    """Test document upload endpoint"""
    # Mock OpenAI API key for summary generation
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    
    files = {"file": ("test.pdf", open(sample_pdf, "rb"), "application/pdf")}
    response = await client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["document_id"]
    assert data["filename"] == "test.pdf"
    assert data["chunk_count"] > 0
    assert len(data["summary"]) > 0

@pytest.mark.asyncio
async def test_ask_question(client, sample_pdf, monkeypatch):
    """Test question endpoint"""
    # First upload document
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    files = {"file": ("test.pdf", open(sample_pdf, "rb"), "application/pdf")}
    upload_response = await client.post("/api/v1/upload", files=files)
    document_id = upload_response.json()["document_id"]
    
    # Ask question
    payload = {
        "document_id": document_id,
        "question": "What is the main content of the document?",
        "session_id": None
    }
    response = await client.post("/api/v1/question", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert data["answer"]
    assert data["confidence"] >= 0.0
    assert data["session_id"]

@pytest.mark.asyncio
async def test_generate_challenge(client, sample_pdf, monkeypatch):
    """Test challenge generation endpoint"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    files = {"file": ("test.pdf", open(sample_pdf, "rb"), "application/pdf")}
    upload_response = await client.post("/api/v1/upload", files=files)
    document_id = upload_response.json()["document_id"]
    
    payload = {
        "document_id": document_id,
        "num_questions": 3
    }
    response = await client.post("/api/v1/challenge", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"]
    assert len(data["questions"]) == 3
    assert all("question_id" in q and "question" in q and "reasoning" in q for q in data["questions"])

@pytest.mark.asyncio
async def test_evaluate_response(client, sample_pdf, monkeypatch):
    """Test evaluation endpoint"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    files = {"file": ("test.pdf", open(sample_pdf, "rb"), "application/pdf")}
    upload_response = await client.post("/api/v1/upload", files=files)
    document_id = upload_response.json()["document_id"]
    
    # Generate challenge
    challenge_payload = {"document_id": document_id, "num_questions": 1}
    challenge_response = await client.post("/api/v1/challenge", json=challenge_payload)
    session_id = challenge_response.json()["session_id"]
    question_id = challenge_response.json()["questions"][0]["question_id"]
    
    # Evaluate response
    eval_payload = {
        "session_id": session_id,
        "question_id": question_id,
        "user_answer": "This is a test answer."
    }
    response = await client.post("/api/v1/evaluate", json=eval_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == question_id
    assert 0 <= data["score"] <= 100
    assert data["feedback"]
    assert data["expected_answer"]