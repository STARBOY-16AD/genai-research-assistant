#!/bin/bash

# scripts/run.sh: Run script for GenAI Research Assistant

set -e

PROJECT_DIR=$(dirname "$(dirname "$(realpath "$0")")")
VENV_DIR="$PROJECT_DIR/venv"

echo "Starting GenAI Research Assistant..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Error: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Start FastAPI backend in background
echo "Starting FastAPI backend on http://localhost:8000..."
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait briefly to ensure backend starts
sleep 2

# Start Streamlit frontend
echo "Starting Streamlit frontend on http://localhost:8501..."
streamlit run src/frontend/app.py --server.port 8501 --server.address 0.0.0.0 &

# Keep script running to monitor processes
wait