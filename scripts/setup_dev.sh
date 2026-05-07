#!/bin/bash

# Development Environment Setup Script for FinOps Reporting

set -e

echo "========================================="
echo "FinOps Reporting - Development Setup"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install development tools
echo -e "\n${YELLOW}Installing development tools...${NC}"
pip install black isort pylint mypy

# Create necessary directories
echo -e "\n${YELLOW}Creating output directories...${NC}"
mkdir -p finops_reports/charts
mkdir -p cost_reports/charts
mkdir -p logs

# Setup environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Please edit .env with your GCP credentials${NC}"
fi

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

# Check Node version
echo "Node version:"
node --version

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
npm install

# Create frontend .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating frontend .env file...${NC}"
    cp .env.example .env
fi

cd ..

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "\nNext steps:"
echo "1. Edit .env with your GCP credentials"
echo "2. Edit frontend/.env with your API URL"
echo "3. Run backend: python api.py"
echo "4. Run frontend: cd frontend && npm run dev"
echo ""
