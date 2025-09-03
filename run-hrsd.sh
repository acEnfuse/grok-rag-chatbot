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
    echo "❌ GROQ_API_KEY not set. Please set it with:"
    echo "   export GROQ_API_KEY='your_groq_api_key_here'"
    exit 1
fi

if [ -z "$MILVUS_HOST" ]; then
    export MILVUS_HOST="34.169.82.181"
fi

if [ -z "$MILVUS_PORT" ]; then
    export MILVUS_PORT="19530"
fi

if [ -z "$MILVUS_TOKEN" ]; then
    export MILVUS_TOKEN="root:Milvus"
fi

echo "✅ Environment variables set:"
echo "   GROQ_API_KEY: ${GROQ_API_KEY:0:20}..."
echo "   MILVUS_HOST: $MILVUS_HOST"
echo "   MILVUS_PORT: $MILVUS_PORT"
echo "   MILVUS_TOKEN: $MILVUS_TOKEN"

# Start the FastAPI backend
echo "🚀 Starting FastAPI backend server..."
echo "📱 Backend will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================"

# Run the HRSD app with uvicorn
uvicorn app_hrsd:app --reload --host 0.0.0.0 --port 8000