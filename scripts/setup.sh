#!/bin/bash

# GCP FinOps Reporting Suite - Setup Script

set -e

echo "=========================================="
echo "GCP FinOps Reporting Suite - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Please install Python 3.11 first."
    exit 1
fi
echo "✅ Python 3.11 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env with your configuration"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Create output directories
echo "Creating output directories..."
mkdir -p cost_reports/charts
mkdir -p finops_reports/charts
mkdir -p governance_reports
echo "✅ Output directories created"
echo ""

# Check GCP credentials
echo "Checking GCP credentials..."
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "⚠️  GOOGLE_APPLICATION_CREDENTIALS not set"
    echo "   Please set it to your service account key path:"
    echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-sa.json"
else
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS is set"
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable"
echo "3. Run reports:"
echo "   - python daily_cost_report.py"
echo "   - python finops_report.py"
echo "   - python governance_report.py"
echo "   - python run_all_reports.py (run all)"
echo ""
