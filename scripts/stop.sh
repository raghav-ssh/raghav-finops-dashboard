#!/bin/bash

# Stop script for FinOps Reporting

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping FinOps Reporting services...${NC}"

# Stop backend
if pgrep -f "python.*api.py" > /dev/null; then
    pkill -f "python.*api.py"
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo -e "${YELLOW}Backend not running${NC}"
fi

# Stop frontend
if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo -e "${GREEN}✓ Frontend stopped${NC}"
else
    echo -e "${YELLOW}Frontend not running${NC}"
fi

# Clean up log files (optional)
if [ "$1" == "--clean" ]; then
    rm -f backend.log frontend.log
    echo -e "${GREEN}✓ Log files cleaned${NC}"
fi

echo -e "${GREEN}All services stopped${NC}"
