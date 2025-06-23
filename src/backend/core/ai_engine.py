import openai
import anthropic
from typing import List, Dict, Optional
from .config import settings
from .document_processor import DocumentProcessor
from ..utils.helpers import configure_logger
from loguru import logger

class AIEngine:
    def __init__(self):
        self.logger = configure_logger(__name__)
        self.document_processor = DocumentProcessor()
        self.use_anthropic = bool(settings.ANTHROPIC_API_KEY)
        if self.use_anthropic:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            openai.api_key = settings.OPENAI_API_KEY

    async def answer_question(self, question: str, document_ids: List[str]) -> Dict:
        try:
            chunks = self.document_processor.get_relevant_chunks(question, document_ids)
            if not chunks:
                return {"answer": "No relevant information found.", "source_chunks": []}

            context = "\n".join([chunk["content"] for chunk in chunks])
            prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer concisely in markdown format."

            if self.use_anthropic:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=settings.MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.content[0].text
            else:
                response = openai.ChatCompletion.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=settings.MAX_TOKENS
                )
                answer = response.choices[0].message.content

            return {
                "answer": answer,
                "source_chunks": chunks,
                "confidence": 0.9,  # Placeholder
                "justification": "Based on relevant document chunks."
            }
        except Exception as e:
            self.logger.error(f"Error answering question: {str(e)}")
            return {"answer": f"Error: {str(e)}", "source_chunks": [], "confidence": 0.0, "justification": ""}

    async def generate_summary(self, document_id: str) -> str:
        try:
            chunks = self.document_processor.get_document_chunks(document_id)
            if not chunks:
                return "No content available for summary."

            content = "\n".join([chunk["content"] for chunk in chunks])
            prompt = f"Summarize the following content in 3-5 bullet points, under {settings.SUMMARY_MAX_WORDS} words:\n{content}"

            if self.use_anthropic:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response.content[0].text
            else:
                response = openai.ChatCompletion.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                summary = response.choices[0].message.content

            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return f"Error: {str(e)}"

    def generate_challenge_questions(self, text: str, doc_id: str, num_questions: int) -> List[Dict]:
        try:
            prompt = f"Generate {num_questions} challenging questions with reasoning based on this content: {text[:1000]}"
            if self.use_anthropic:
                response = self.anthropic_client.messages.create(
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

            questions = []
            for i, q in enumerate(questions_text.split("\n\n")[:num_questions], 1):
                if q.strip():
                    questions.append({
                        "question_id": str(uuid.uuid4()),
                        "question": q.split("\nReasoning:")[0].strip(),
                        "reasoning": q.split("\nReasoning:")[1].strip() if "\nReasoning:" in q else "Based on document content.",
                        "expected_answer": "Sample answer"  # Replace with actual answer generation if needed
                    })
            return questions
        except Exception as e:
            self.logger.error(f"Error generating challenge questions: {str(e)}")
            return []

    def evaluate_challenge_response(self, question: str, user_answer: str, expected_answer: str, doc_id: str) -> Dict:
        try:
            prompt = f"Evaluate this answer: '{user_answer}' for correctness and relevance to the question: '{question}'. Provide a score (0-100), feedback, and reference chunks."
            if self.use_anthropic:
                response = self.anthropic_client.messages.create(
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

            return {
                "score": 80,  # Placeholder, parse from evaluation_text if structured
                "feedback": evaluation_text,
                "expected_answer": expected_answer,
                "reference_chunks": self.document_processor.get_document_chunks(doc_id)
            }
        except Exception as e:
            self.logger.error(f"Error evaluating response: {str(e)}")
            return {"score": 0, "feedback": str(e), "expected_answer": expected_answer, "reference_chunks": []}