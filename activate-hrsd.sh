#!/bin/bash

# HRSD Job Matching App Environment Activation Script

echo "🤖 Activating HRSD Job Matching Environment..."
echo "========================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

# Activate the environment
echo "🔄 Activating conda environment: hrsd-job-matcher"
conda activate hrsd-job-matcher

# Check if activation was successful
if [ $? -eq 0 ]; then
    echo "✅ Environment activated successfully"
    echo "📦 Python version: $(python --version)"
    echo "🚀 Ready to run the HRSD Job Matching App!"
    echo ""
    echo "To start the backend server:"
    echo "  uvicorn app:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "To start the React frontend (in another terminal):"
    echo "  cd frontend && npm start"
    echo ""
else
    echo "❌ Failed to activate environment"
    exit 1
fi
