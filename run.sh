#!/bin/bash

echo "🤖 Starting RAG Chatbot..."
echo "========================================"

# Check if virtual environment exists
if [ ! -d "rag-chatbot-env" ]; then
    echo "❌ Virtual environment 'rag-chatbot-env' not found!"
    echo "Please run: python3 -m venv rag-chatbot-env"
    echo "Then run: source rag-chatbot-env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "⚠️  Java not found. Please install Java 8+ for document processing."
    echo "   macOS: brew install openjdk@11"
    echo "   Ubuntu: sudo apt-get install openjdk-11-jdk"
    echo ""
    echo "🔄 Continuing anyway... (some features may not work)"
else
    echo "✅ Java found: $(java -version 2>&1 | head -n 1)"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment: rag-chatbot-env"
source rag-chatbot-env/bin/activate

# Check if required packages are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found in virtual environment!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Virtual environment activated"
echo "🚀 Launching Streamlit app..."
echo "📱 Open your browser to: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================"

# Run streamlit with the activated environment
exec streamlit run app.py 