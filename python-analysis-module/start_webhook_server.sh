#!/bin/bash

# Project Genji - Start Webhook Server
# Starts the Flask webhook server for n8n integration

set -e

echo "🚀 Starting Project Genji webhook server for n8n integration..."

# Activate virtual environment
source ../venv/bin/activate

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ .env file not found. Please copy .env.webhook.template to .env and configure it."
    exit 1
fi

# Start the webhook server
echo "🌐 Starting webhook server on http://localhost:5000..."
echo "📡 Available endpoints:"
echo "   POST /webhook/n8n/article   - Process single article"
echo "   POST /webhook/n8n/articles  - Process multiple articles"
echo "   GET  /webhook/n8n/status    - Health check"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================="

cd /home/coder/startup/genji/python-analysis-module
python n8n_integration.py
