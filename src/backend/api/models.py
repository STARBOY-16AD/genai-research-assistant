# src/backend/api/models.py
"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Models
class QuestionRequest(BaseModel):
    document_id: str = Field(..., description="Document ID to query")
    question: str = Field(..., min_length=1, description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")

class ChallengeRequest(BaseModel):
    document_id: str = Field(..., description="Document ID to generate challenges for")
    num_questions: Optional[int] = Field(3, ge=1, le=5, description="Number of questions to generate")

class EvaluationRequest(BaseModel):
    session_id: str = Field(..., description="Challenge session ID")
    question_id: str = Field(..., description="Question ID being answered")
    user_answer: str = Field(..., min_length=1, description="User's answer to evaluate")

# Response Models
class SourceChunk(BaseModel):
    text: str = Field(..., description="Text content of the chunk")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")

class UploadResponse(BaseModel):
    document_id: str = Field(..., description="Generated document ID")
    filename: str = Field(..., description="Original filename")
    summary: str = Field(..., description="Auto-generated summary")
    chunk_count: int = Field(..., description="Number of chunks created")
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Status message")

class QuestionResponse(BaseModel):
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI-generated answer")
    justification: str = Field(..., description="Justification for the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    source_chunks: List[SourceChunk] = Field(..., description="Source chunks used")
    session_id: str = Field(..., description="Session ID for context")

class ChallengeQuestion(BaseModel):
    question_id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="Challenge question text")
    reasoning: str = Field(..., description="Why this question tests comprehension")

class ChallengeResponse(BaseModel):
    session_id: str = Field(..., description="Challenge session ID")
    questions: List[ChallengeQuestion] = Field(..., description="Generated questions")
    total_questions: int = Field(..., description="Total number of questions")

class EvaluationResponse(BaseModel):
    question_id: str = Field(..., description="Question ID that was answered")
    score: int = Field(..., ge=0, le=100, description="Score out of 100")
    feedback: str = Field(..., description="Detailed feedback")
    expected_answer: str = Field(..., description="Expected answer")
    reference_chunks: List[SourceChunk] = Field(..., description="Reference chunks")

class DocumentInfo(BaseModel):
    document_id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    summary: str = Field(..., description="Document summary")
    chunk_count: int = Field(..., description="Number of chunks")
    uploaded_at: str = Field(..., description="Upload timestamp")

class ChallengeProgress(BaseModel):
    session_id: str = Field(..., description="Challenge session ID")
    total_questions: int = Field(..., description="Total questions in challenge")
    answered_questions: int = Field(..., description="Number of answered questions")
    average_score: float = Field(..., description="Average score so far")

# Error Models
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")