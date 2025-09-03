#!/bin/bash

# HRSD Job Matching Frontend Startup Script

echo "🎨 Starting HRSD Job Matching Frontend..."
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

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

echo "✅ npm found: $(which npm)"

# Navigate to frontend directory
echo "📁 Navigating to frontend directory..."
cd "$(dirname "$0")/frontend"

if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

echo "✅ Found package.json"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Start the React development server
echo "🚀 Starting React development server..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================"

npm start
