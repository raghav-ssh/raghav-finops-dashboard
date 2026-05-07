#!/bin/bash

# Code Formatting Script for FinOps Reporting

set -e

echo "========================================="
echo "FinOps Reporting - Code Formatting"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Python files to format
PYTHON_FILES="*.py"

echo -e "\n${YELLOW}Formatting Python code with Black...${NC}"
black $PYTHON_FILES --line-length 100

echo -e "\n${YELLOW}Sorting imports with isort...${NC}"
isort $PYTHON_FILES --profile black

echo -e "\n${YELLOW}Running pylint checks...${NC}"
pylint $PYTHON_FILES --disable=C0111,R0913,R0914,R0915 || true

echo -e "\n${YELLOW}Formatting frontend code...${NC}"
cd frontend
npm run lint || true
cd ..

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}Code formatting completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
