#!/bin/bash

# Matatu Fleet Management System - Development Startup Script

echo "🚌 Starting Matatu Fleet Management System"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if backend is already running
if check_port 8001; then
    echo "⚠️  Backend already running on port 8001"
else
    echo "🔧 Starting backend services (PostgreSQL, Redis, Auth Service)..."
    docker-compose up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check health
    echo "🏥 Checking backend health..."
    if curl -s http://localhost:8001/health > /dev/null; then
        echo "✅ Backend is healthy!"
    else
        echo "⚠️  Backend might still be starting up..."
    fi
fi

# Check if frontend is already running
if check_port 3000; then
    echo "⚠️  Frontend already running on port 3000"
else
    echo "🌐 Starting frontend server..."
    cd frontend
    python3 server.py &
    FRONTEND_PID=$!
    cd ..
    
    # Wait a moment for frontend to start
    sleep 2
    
    if check_port 3000; then
        echo "✅ Frontend is running!"
    else
        echo "❌ Frontend failed to start"
    fi
fi

echo ""
echo "🎉 System is ready!"
echo "==================="
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8001"
echo "📖 API Docs:     http://localhost:8001/docs"
echo "🏥 Health Check: http://localhost:8001/health"
echo ""
echo "📋 Quick Test Commands:"
echo "curl http://localhost:8001/health"
echo "curl http://localhost:8001/debug/create-manager-token -X POST"
echo ""
echo "🛑 To stop: docker-compose down && pkill -f 'python3 server.py'"
