#!/bin/bash

# HRSD Job Matching App Startup Script

echo "🤖 Starting HRSD Job Matching System..."
echo "========================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

# Activate the HRSD environment
echo "🔄 Activating conda environment: hrsd-job-matcher"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate hrsd-job-matcher

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate hrsd-job-matcher environment"
    echo "Please run: conda create -n hrsd-job-matcher python=3.13"
    exit 1
fi

echo "✅ Environment activated successfully"

# Check if required environment variables are set
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set. Please set it with:"
    echo "   export GROQ_API_KEY='your-api-key-here'"
    echo ""
fi

if [ -z "$MILVUS_HOST" ]; then
    echo "⚠️  MILVUS_HOST not set. Using default localhost"
    export MILVUS_HOST="localhost"
fi

if [ -z "$MILVUS_PORT" ]; then
    export MILVUS_PORT="19530"
fi

# Start the FastAPI backend
echo "🚀 Starting FastAPI backend server..."
echo "📱 Backend will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================"

# Run the HRSD app
python app_hrsd.py
