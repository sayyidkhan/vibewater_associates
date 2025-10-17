#!/bin/bash

echo "🚀 Setting up backend with uv..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
fi

# Create virtual environment with uv
echo "🔧 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies with uv
echo "📥 Installing dependencies with uv (this is fast!)..."
uv pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment in the future:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the backend:"
echo "  uv run uvicorn app.main:app --reload"
echo "  # or: uvicorn app.main:app --reload (if venv is activated)"
echo ""
echo "To test VectorBT:"
echo "  uv run test_vectorbt.py"
echo "  # or: python test_vectorbt.py (if venv is activated)"
echo ""
