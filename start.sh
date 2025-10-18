#!/bin/bash

# AI Trading Bot Generator - Start Script

echo "🚀 Starting AI Trading Bot Generator..."
echo ""

# Start backend
echo "📡 Starting FastAPI backend on port 8000..."
cd "$(dirname "$0")"
source venv/bin/activate
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting React frontend on port 5173..."
cd ..
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo ""
echo "📡 Backend:  http://localhost:8000"
echo "⚛️  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
