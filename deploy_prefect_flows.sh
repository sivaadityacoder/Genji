#!/bin/bash

# Project Genji - Deploy Prefect 3.x Flows
# Deploys all Prefect workflows for production use

set -e

echo "� Deploying Prefect 3.x flows for Project Genji..."

# Activate virtual environment
source venv/bin/activate

# Deploy the working pipeline flows
echo "📦 Deploying working pipeline flows..."
cd prefect-workflows
python deploy_v3.py

echo "✅ All Prefect 3.x flows deployed successfully!"
echo ""
echo "🎯 Available deployments:"
echo "- simple-genji-pipeline (for testing)"
echo "- real-genji-pipeline (for production)"
echo ""
echo "💡 Next steps:"
echo "1. View deployments: prefect deployment ls"
echo "2. Run flow: prefect deployment run 'simple-genji-pipeline/default'"
echo "3. Monitor: http://localhost:4200"
echo "You can now view them in the Prefect UI at http://localhost:4200"
