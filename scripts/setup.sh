#!/bin/bash

# scripts/setup.sh: Setup script for GenAI Research Assistant

set -e

# Project root directory
PROJECT_DIR=$(dirname "$(dirname "$(realpath "$0")")")
VENV_DIR="$PROJECT_DIR/venv"

echo "Setting up GenAI Research Assistant project..."

# Check for Python 3.8+
if ! python3 --version | grep -q "3.[8-9]\|3.1[0-9]"; then
    echo "Error: Python 3.8 or higher is required."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Skipping..."
    rm -rf "$VENV_DIR"
fi
python3 -m venv "$VENV_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r "$PROJECT_DIR/requirements.txt"

# Copy .env.example to .env if .env doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; ]; then
    echo "Creating .env from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo ".env created. Please update it with your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)."
else
    echo ".env already exists. Skipping..."
fi

# Create necessary directories
echo "Creating upload and data directories..."
mkdir -p "$PROJECT_DIR/uploads"
mkdir -p "$PROJECT_DIR/data/vector_db"
mkdir -p "$PROJECT_DIR/logs"

echo "Setup complete! To activate the virtual environment:"
echo "source $VENV_DIR/bin/activate"
echo "To run the application:"
echo "./scripts/run.sh"