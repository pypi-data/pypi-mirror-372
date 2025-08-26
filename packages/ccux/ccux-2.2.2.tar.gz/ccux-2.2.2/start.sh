#!/bin/bash

# CCUX Start Script
# This script starts both the backend and frontend servers

echo "🚀 Starting CCUX - AI Landing Page Generator"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    echo -e "${YELLOW}Killing existing process on port $1...${NC}"
    lsof -ti:$1 | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check current directory
if [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
    echo -e "${RED}❌ Error: Please run this script from the main project directory${NC}"
    echo -e "${YELLOW}The directory should contain both 'backend' and 'frontend' folders${NC}"
    exit 1
fi

# Check if ports are already in use
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 (backend) is already in use${NC}"
    read -p "Kill existing process and restart? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port 8000
    else
        echo -e "${RED}Cannot start backend on port 8000${NC}"
        exit 1
    fi
fi

if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 (frontend) is already in use${NC}"
    read -p "Kill existing process and restart? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_port 3000
    else
        echo -e "${RED}Cannot start frontend on port 3000${NC}"
        exit 1
    fi
fi

echo

# Start Backend
echo -e "${BLUE}📡 Starting Backend API Server...${NC}"
echo "   Location: backend/"
echo "   Port: 8000"
echo "   API Docs: http://localhost:8000/docs"

cd backend
if [[ ! -f "main.py" ]]; then
    echo -e "${RED}❌ Error: main.py not found in backend directory${NC}"
    exit 1
fi

# Check if virtual environment exists and activate it
if [[ -d "../.venv" ]]; then
    echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
    source ../.venv/bin/activate
elif [[ -d ".venv" ]]; then
    echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Start backend in background
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait a moment for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
sleep 3

# Check if backend is responding
if check_port 8000; then
    echo -e "${GREEN}✅ Backend is running on http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check backend.log for errors"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend Development Server...${NC}"
echo "   Location: frontend/"
echo "   Port: 3000"
echo "   URL: http://localhost:3000"

cd ../frontend
if [[ ! -f "package.json" ]]; then
    echo -e "${RED}❌ Error: package.json not found in frontend directory${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Check if node_modules exists
if [[ ! -d "node_modules" ]]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to initialize...${NC}"
sleep 5

# Check if frontend is responding
if check_port 3000; then
    echo -e "${GREEN}✅ Frontend is running on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo "Check frontend.log for errors"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo
echo -e "${GREEN}🎉 CCUX is now running successfully!${NC}"
echo "============================================="
echo -e "${BLUE}📱 Frontend Dashboard:${NC} http://localhost:3000"
echo -e "${BLUE}🔧 Backend API:${NC}       http://localhost:8000"
echo -e "${BLUE}📚 API Documentation:${NC} http://localhost:8000/docs"
echo
echo -e "${YELLOW}💡 Quick Actions:${NC}"
echo "   • Create new project: http://localhost:3000/new"
echo "   • View API health: http://localhost:8000/healthz"
echo
echo -e "${YELLOW}📋 Process Information:${NC}"
echo "   • Backend PID: $BACKEND_PID"
echo "   • Frontend PID: $FRONTEND_PID"
echo "   • Logs: backend.log & frontend.log"
echo
echo -e "${YELLOW}🛑 To stop CCUX, run:${NC} ./stop.sh"
echo -e "${YELLOW}📊 To view logs, run:${NC} tail -f backend.log frontend.log"
echo
echo -e "${GREEN}🚀 Ready to generate amazing landing pages!${NC}"

# Save PIDs for stop script
echo "BACKEND_PID=$BACKEND_PID" > .pids
echo "FRONTEND_PID=$FRONTEND_PID" >> .pids

# Keep script running to monitor services
echo -e "${BLUE}🔍 Monitoring services... Press Ctrl+C to stop${NC}"
trap 'echo -e "\n${YELLOW}🛑 Stopping CCUX services...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f .pids; exit 0' INT

# Monitor both processes
while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; do
    sleep 5
done

echo -e "${RED}❌ One or both services stopped unexpectedly${NC}"
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
rm -f .pids