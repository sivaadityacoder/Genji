#!/bin/bash

# Project Genji - Prefect 3.x Setup Script
# Complete setup for Prefect 3.x workflow orchestration

set -e

echo "🚀 Setting up Prefect 3.x for Project Genji..."

# Activate virtual environment
source venv/bin/activate

# Install/upgrade Prefect and related packages
echo "📦 Installing Prefect 3.x dependencies..."
pip install -r requirements.txt

# Set Prefect configuration for local development
echo "🔧 Configuring Prefect..."
prefect config set PREFECT_UI_URL=http://localhost:4200

echo "✅ Prefect 3.x setup completed!"
echo ""
echo "Next steps:"
echo "1. Start Prefect server: ./start_prefect_server.sh"
echo "2. Deploy flows: ./deploy_prefect_flows.sh"
echo "3. Run pipeline manually: ./run_prefect_pipeline.sh"
echo ""
echo "Then access the UI at: http://localhost:4200"
