#!/bin/bash

# Startup script for reorganized project

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  FinOps Reporting - Startup${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check environment files
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

if [ ! -f "frontend/.env" ]; then
    echo -e "${RED}Error: frontend/.env file not found${NC}"
    exit 1
fi

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "\n${YELLOW}Starting backend...${NC}"
cd backend
python main.py > ../outputs/logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 3

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Failed to start backend${NC}"
    cat outputs/logs/backend.log
    exit 1
fi

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend running on http://localhost:8001${NC}"
else
    echo -e "${RED}Backend health check failed${NC}"
fi

# Start frontend
echo -e "\n${YELLOW}Starting frontend...${NC}"
cd frontend
npm run dev > ../outputs/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 5

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Failed to start frontend${NC}"
    cat outputs/logs/frontend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Frontend running on http://localhost:5173${NC}"

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}  Services Running!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "\n${YELLOW}Dashboard:${NC} http://localhost:5173"
echo -e "${YELLOW}API Docs:${NC} http://localhost:8001/docs"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "  tail -f outputs/logs/backend.log"
echo -e "  tail -f outputs/logs/frontend.log"
echo -e "\n${YELLOW}Press Ctrl+C to stop${NC}\n"

tail -f outputs/logs/backend.log outputs/logs/frontend.log
