"""
FastAPI routes for the GenAI Research Assistant
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict
from ..core.document_processor import DocumentProcessor
from ..core.ai_engine import AIEngine
from ..core.config import settings
from loguru import logger
import os
import aiofiles
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    try:
        if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
            raise HTTPException(status_code=400, detail=f"Invalid file extension. Allowed: {settings.ALLOWED_EXTENSIONS}")

        file_path = os.path.join("uploads", file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())

        processor = DocumentProcessor()
        document_id = await processor.process_document(file_path, file.filename)

        return {
            "document_id": document_id,
            "filename": file.filename,
            "chunk_count": len(processor.get_document_chunks(document_id)),
            "success": True,
            "message": "Document uploaded and processed successfully"
        }
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_question(data: dict):
    """Answer questions about the document"""
    try:
        question = data.get("question")
        document_ids = data.get("document_ids", [])
        if not question or not document_ids:
            raise HTTPException(status_code=400, detail="Question and document IDs required")

        engine = AIEngine()
        response = await engine.answer_question(question, document_ids)
        return {
            "question": question,
            "answer": response["answer"],
            "source_chunks": response["source_chunks"],
            "session_id": str(uuid.uuid4())
        }
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_document(data: dict):
    """Generate document summary"""
    try:
        document_id = data.get("document_id")
        if not document_id:
            raise HTTPException(status_code=400, detail="Document ID required")

        engine = AIEngine()
        summary = await engine.generate_summary(document_id)
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/challenge")
async def generate_challenge(data: dict):
    """Generate challenge questions from the document"""
    try:
        document_id = data.get("document_id")
        num_questions = data.get("num_questions", 3)
        if not document_id:
            raise HTTPException(status_code=400, detail="Document ID required")

        engine = AIEngine()
        chunks = engine.document_processor.get_document_chunks(document_id)
        if not chunks:
            raise HTTPException(status_code=404, detail="No content available")

        content = "\n".join([chunk["content"] for chunk in chunks])
        prompt = f"Generate {num_questions} challenging questions with reasoning based on this content: {content[:1000]}"

        if engine.use_anthropic:
            response = engine.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            questions_text = response.content[0].text
        else:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            questions_text = response.choices[0].message.content

        # Parse questions (assuming AI returns numbered list)
        questions = []
        for i, q in enumerate(questions_text.split("\n\n")[:num_questions], 1):
            if q.strip():
                questions.append({
                    "question_id": str(uuid.uuid4()),
                    "question": q.split("\nReasoning:")[0].strip(),
                    "reasoning": q.split("\nReasoning:")[1].strip() if "\nReasoning:" in q else "Based on document content.",
                    "expected_answer": "Sample answer"  # Replace with actual answer generation if needed
                })

        session_id = str(uuid.uuid4())
        return {
            "session_id": session_id,
            "questions": questions,
            "total_questions": len(questions)
        }
    except Exception as e:
        logger.error(f"Error generating challenge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate")
async def evaluate_response(data: dict):
    """Evaluate user's response to challenge question"""
    try:
        session_id = data.get("session_id")
        question_id = data.get("question_id")
        user_answer = data.get("user_answer")
        if not all([session_id, question_id, user_answer]):
            raise HTTPException(status_code=400, detail="Session ID, question ID, and user answer required")

        engine = AIEngine()
        # Placeholder evaluation
        prompt = f"Evaluate this answer: '{user_answer}' for correctness and relevance to the question ID {question_id}. Provide a score (0-100), feedback, and reference chunks."

        if engine.use_anthropic:
            response = engine.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            evaluation_text = response.content[0].text
        else:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            evaluation_text = response.choices[0].message.content

        # Parse evaluation (assuming structured response)
        evaluation = {
            "score": 80,  # Placeholder, parse from evaluation_text if structured
            "feedback": evaluation_text,
            "expected_answer": "Sample expected answer",
            "reference_chunks": engine.document_processor.get_document_chunks(data.get("document_id", ""))
        }
        return evaluation
    except Exception as e:
        logger.error(f"Error evaluating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))