#!/bin/bash

# HRSD Job Matching System - Complete Startup Script

echo "🚀 Starting HRSD Job Matching System (Backend + Frontend)..."
echo "=========================================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📁 Script directory: $SCRIPT_DIR"

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend..."
    cd "$SCRIPT_DIR"
    ./run-hrsd.sh &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    return $BACKEND_PID
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend..."
    cd "$SCRIPT_DIR"
    ./run-frontend.sh &
    FRONTEND_PID=$!
    echo "✅ Frontend started with PID: $FRONTEND_PID"
    return $FRONTEND_PID
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start both services
start_backend
BACKEND_PID=$?

# Wait a moment for backend to initialize
echo "⏳ Waiting for backend to initialize..."
sleep 5

start_frontend
FRONTEND_PID=$?

echo ""
echo "🎉 HRSD Job Matching System is running!"
echo "========================================"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo "========================================"

# Wait for user to stop
wait
