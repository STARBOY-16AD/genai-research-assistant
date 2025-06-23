from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class SourceChunk:
    text: str
    chunk_id: str
    relevance_score: float

@dataclass
class DocumentInfo:
    document_id: str
    filename: str
    summary: str
    chunk_count: int
    uploaded_at: str

@dataclass
class QuestionResponse:
    question: str
    answer: str
    justification: str
    confidence: float
    source_chunks: List[SourceChunk]
    session_id: str

@dataclass
class ChallengeQuestion:
    question_id: str
    question: str
    reasoning: str

@dataclass
class ChallengeResponse:
    session_id: str
    questions: List[ChallengeQuestion]
    total_questions: int

@dataclass
class EvaluationResponse:
    question_id: str
    score: int
    feedback: str
    expected_answer: str
    reference_chunks: List[SourceChunk]

@dataclass
class ChallengeProgress:
    session_id: str
    total_questions: int
    answered_questions: int
    average_score: float