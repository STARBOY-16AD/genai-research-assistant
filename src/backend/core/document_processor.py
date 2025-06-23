# src/backend/core/document_processor.py
"""
Document processing utilities for PDF, TXT, and DOCX files
"""
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import settings

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from uploaded file based on extension"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext == '.txt':
            return self._extract_from_txt(file_path)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber for better accuracy"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        
        return text.strip()
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return '\n'.join(text)
    
    def chunk_document(self, text: str, doc_id: str) -> List[Dict]:
        """Split document into chunks with metadata"""
        # Simple sentence-based chunking
        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < settings.CHUNK_SIZE:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append({
                        'id': f"{doc_id}_chunk_{chunk_id}",
                        'text': current_chunk.strip(),
                        'doc_id': doc_id,
                        'chunk_index': chunk_id,
                        'metadata': {
                            'start_char': len(''.join([c['text'] for c in chunks])),
                            'end_char': len(''.join([c['text'] for c in chunks])) + len(current_chunk)
                        }
                    })
                    chunk_id += 1
                current_chunk = sentence + ". "
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'id': f"{doc_id}_chunk_{chunk_id}",
                'text': current_chunk.strip(),
                'doc_id': doc_id,
                'chunk_index': chunk_id,
                'metadata': {
                    'start_char': len(''.join([c['text'] for c in chunks])),
                    'end_char': len(''.join([c['text'] for c in chunks])) + len(current_chunk)
                }
            })
        
        return chunks
    
    def store_document_embeddings(self, chunks: List[Dict], doc_id: str):
        """Store document chunks in vector database"""
        collection_name = f"doc_{doc_id}"
        
        try:
            # Delete existing collection if it exists
            self.chroma_client.delete_collection(collection_name)
        except:
            pass
        
        collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"description": f"Document chunks for {doc_id}"}
        )
        
        # Prepare data for ChromaDB
        texts = [chunk['text'] for chunk in chunks]
        ids = [chunk['id'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Add documents to collection
        collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas
        )
    
    def search_relevant_chunks(self, query: str, doc_id: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant chunks based on query"""
        collection_name = f"doc_{doc_id}"
        
        try:
            collection = self.chroma_client.get_collection(collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            relevant_chunks = []
            for i, doc in enumerate(results['documents'][0]):
                relevant_chunks.append({
                    'text': doc,
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0,
                    'metadata': results['metadatas'][0][i]
                })
            
            return relevant_chunks
        except Exception as e:
            print(f"Error searching chunks: {e}")
            return []
    
    def get_document_hash(self, file_path: str) -> str:
        """Generate hash for document to use as ID"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    
    def process_uploaded_document(self, file_path: str) -> Tuple[str, str, List[Dict]]:
        """Complete document processing pipeline"""
        # Generate document ID
        doc_id = self.get_document_hash(file_path)
        
        # Extract text
        text = self.extract_text_from_file(file_path)
        
        # Chunk document
        chunks = self.chunk_document(text, doc_id)
        
        # Store embeddings
        self.store_document_embeddings(chunks, doc_id)
        
        return doc_id, text, chunks