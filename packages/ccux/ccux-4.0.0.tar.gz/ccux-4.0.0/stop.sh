#!/bin/bash

# CCUX Stop Script
# This script stops both the backend and frontend servers

echo "🛑 Stopping CCUX Services"
echo "========================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to kill process on port
kill_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}🔄 Stopping $service on port $port...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            echo -e "${RED}❌ Failed to stop $service${NC}"
        else
            echo -e "${GREEN}✅ $service stopped${NC}"
        fi
    else
        echo -e "${YELLOW}ℹ️  $service is not running${NC}"
    fi
}

# Stop services using PIDs if available
if [[ -f ".pids" ]]; then
    echo -e "${YELLOW}📋 Using saved process IDs...${NC}"
    source .pids
    
    if [[ -n "$BACKEND_PID" ]]; then
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${YELLOW}🔄 Stopping backend (PID: $BACKEND_PID)...${NC}"
            kill $BACKEND_PID 2>/dev/null || true
            echo -e "${GREEN}✅ Backend stopped${NC}"
        fi
    fi
    
    if [[ -n "$FRONTEND_PID" ]]; then
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${YELLOW}🔄 Stopping frontend (PID: $FRONTEND_PID)...${NC}"
            kill $FRONTEND_PID 2>/dev/null || true
            echo -e "${GREEN}✅ Frontend stopped${NC}"
        fi
    fi
    
    rm -f .pids
fi

# Fallback: kill by port
kill_port 8000 "Backend API"
kill_port 3000 "Frontend"

# Clean up log files
if [[ -f "backend.log" ]]; then
    echo -e "${YELLOW}🧹 Cleaning up backend.log${NC}"
    rm -f backend.log
fi

if [[ -f "frontend.log" ]]; then
    echo -e "${YELLOW}🧹 Cleaning up frontend.log${NC}"
    rm -f frontend.log
fi

echo
echo -e "${GREEN}🎉 CCUX services stopped successfully!${NC}"
echo
echo -e "${YELLOW}💡 To start CCUX again, run:${NC} ./start.sh"