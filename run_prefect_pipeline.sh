#!/bin/bash

# Project Genji - Run Prefect 3.x Pipeline
# Executes the Prefect workflows manually for testing

set -e

echo "🚀 Running Project Genji Prefect 3.x pipeline..."

# Activate virtual environment
source venv/bin/activate

# Run the working pipeline directly
echo "🧪 Executing working pipeline..."
cd prefect-workflows
python working_pipeline.py

echo ""
echo "✅ Pipeline execution completed!"
echo ""
echo "💡 To run via deployment:"
echo "prefect deployment run 'simple-genji-pipeline/default'"
