# src/backend/main.py
"""
FastAPI Main Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from pathlib import Path

from .api.routes import router
from .core.config import settings

# Create FastAPI app
app = FastAPI(
    title="GenAI Research Assistant API",
    description="AI-powered document analysis and reasoning assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "GenAI Research Assistant API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to GenAI Research Assistant API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )