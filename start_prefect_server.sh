#!/bin/bash

# Project Genji - Start Prefect 3.x Server
# Launches the Prefect server for workflow orchestration

set -e

echo "🚀 Starting Prefect 3.x server..."

# Activate virtual environment
source venv/bin/activate

# Start Prefect server
echo "🌐 Launching Prefect server on http://localhost:4200..."
prefect server start --host 0.0.0.0 --port 4200
