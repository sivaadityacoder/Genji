#!/bin/bash

# Project Genji Setup Script
# This script sets up the complete Project Genji environment

set -e  # Exit on any error

echo "🚀 Setting up Project Genji..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "python-analysis-module/.env" ]; then
    echo "📝 Creating .env file..."
    cp python-analysis-module/.env.example python-analysis-module/.env
    echo "⚠️ Please edit python-analysis-module/.env with your actual API keys and database credentials"
fi

# Make scripts executable
chmod +x setup.sh
chmod +x run_data_collection.sh
chmod +x run_analysis.sh
chmod +x run_dashboard.sh

echo "✅ Project Genji setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit python-analysis-module/.env with your API keys"
echo "2. Set up PostgreSQL database using docs/database_setup.sql"
echo "3. Run data collection: ./run_data_collection.sh"
echo "4. Run AI analysis: ./run_analysis.sh" 
echo "5. Start dashboard: ./run_dashboard.sh"
echo ""
echo "📖 See README.md for detailed instructions"
