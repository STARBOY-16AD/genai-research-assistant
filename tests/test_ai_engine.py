import pytest
import os
from unittest.mock import patch
from src.backend.core.ai_engine import AIEngine
from src.backend.core.config import settings
from src.backend.core.document_processor import DocumentProcessor

@pytest.fixture
def ai_engine(tmp_path, monkeypatch):
    """Create an AIEngine instance with a temporary vector DB path"""
    # Override VECTOR_DB_PATH to use temporary directory
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    settings.VECTOR_DB_PATH = str(tmp_path / "vector_db")
    return AIEngine()

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return (
        "This is a test document about artificial intelligence. "
        "It discusses machine learning and neural networks. "
        "Machine learning enables systems to learn from data."
    )

@pytest.fixture
def doc_processor(tmp_path):
    """Create a DocumentProcessor instance for testing"""
    settings.VECTOR_DB_PATH = str(tmp_path / "vector_db")
    return DocumentProcessor()

@pytest.mark.asyncio
@patch("openai.chat.completions.create")
async def test_generate_summary(mock_openai, ai_engine, sample_text):
    """Test summary generation"""
    mock_response = {
        "choices": [{"message": {"content": "Summary: This document discusses AI, focusing on machine learning and neural networks."}}]
    }
    mock_openai.return_value = mock_response

    summary = ai_engine.generate_summary(sample_text, max_words=20)
    
    assert "machine learning" in summary.lower()
    assert len(summary.split()) <= 20
    mock_openai.assert_called_once()
    assert mock_openai.call_args[1]["model"] == settings.OPENAI_MODEL

@pytest.mark.asyncio
@patch("openai.chat.completions.create")
async def test_answer_question(mock_openai, ai_engine, doc_processor, sample_text):
    """Test question answering"""
    doc_id = "test_doc"
    chunks = doc_processor.chunk_document(sample_text, doc_id)
    doc_processor.store_document_embeddings(chunks, doc_id)
    
    mock_response = {
        "choices": [{
            "message": {
                "content": (
                    "Answer: Machine learning enables systems to learn from data.\n"
                    "Justification: Based on document content.\n"
                    "Confidence: 0.9"
                )
            }
        }]
    }
    mock_openai.return_value = mock_response

    result = ai_engine.answer_question(
        question="What is machine learning?",
        doc_id=doc_id,
        conversation_id="test_session"
    )
    
    assert result["answer"] == "Machine learning enables systems to learn from data."
    assert result["confidence"] == 0.9
    assert len(result["source_chunks"]) > 0
    assert result["justification"]
    mock_openai.assert_called_once()
    assert "What is machine learning?" in mock_openai.call_args[1]["messages"][1]["content"]

@pytest.mark.asyncio
@patch("openai.chat.completions.create")
async def test_generate_challenge_questions(mock_openai, ai_engine, sample_text):
    """Test challenge question generation"""
    mock_response = {
        "choices": [{
            "message": {
                "content": (
                    "Q1: What enables systems to learn from data?\n"
                    "Expected Answer: Machine learning.\n"
                    "Reasoning: Tests recall of key concepts.\n"
                    "Q2: How do neural networks relate to AI?\n"
                    "Expected Answer: They are a subset of AI techniques.\n"
                    "Reasoning: Tests understanding of relationships.\n"
                    "Q3: Why is data important for machine learning?\n"
                    "Expected Answer: It provides the basis for learning.\n"
                    "Reasoning: Tests comprehension of purpose."
                )
            }
        }]
    }
    mock_openai.return_value = mock_response

    questions = ai_engine.generate_challenge_questions(sample_text, doc_id="test_doc", num_questions=3)
    
    assert len(questions) == 3
    assert all("question" in q and "expected_answer" in q and "reasoning" in q and "question_id" in q for q in questions)
    assert questions[0]["question"] == "What enables systems to learn from data?"
    assert questions[0]["expected_answer"] == "Machine learning."
    mock_openai.assert_called_once()
    assert mock_openai.call_args[1]["model"] == settings.OPENAI_MODEL

@pytest.mark.asyncio
@patch("openai.chat.completions.create")
async def test_evaluate_challenge_response(mock_openai, ai_engine, doc_processor, sample_text):
    """Test challenge response evaluation"""
    doc_id = "test_doc"
    chunks = doc_processor.chunk_document(sample_text, doc_id)
    doc_processor.store_document_embeddings(chunks, doc_id)
    
    mock_response = {
        "choices": [{
            "message": {
                "content": (
                    "Score: 90%\n"
                    "Feedback: The answer correctly identifies machine learning as the key concept.\n"
                    "Reference: Document discusses machine learning."
                )
            }
        }]
    }
    mock_openai.return_value = mock_response

    evaluation = ai_engine.evaluate_challenge_response(
        question="What enables systems to learn from data?",
        user_answer="Machine learning allows systems to learn.",
        expected_answer="Machine learning.",
        doc_id=doc_id
    )
    
    assert evaluation["score"] == 90
    assert "The answer correctly identifies" in evaluation["feedback"]
    assert len(evaluation["reference_chunks"]) > 0
    mock_openai.assert_called_once()
    assert "user_answer: Machine learning allows systems to learn." in mock_openai.call_args[1]["messages"][1]["content"].lower()