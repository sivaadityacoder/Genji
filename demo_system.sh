#!/bin/bash

# Project Genji - Complete Demo
# Demonstrates all working components of the system

set -e

echo "🧠 PROJECT GENJI - COMPLETE SYSTEM DEMONSTRATION"
echo "==============================================="
echo ""

# Show system status
echo "📊 System Status Check:"
echo "----------------------"
./check_status.sh

echo ""
echo "🧪 Testing Prefect 3.x Workflows:"
echo "--------------------------------"

# Activate environment and test Prefect workflows
source venv/bin/activate

echo "Running working pipeline test..."
cd prefect-workflows
python working_pipeline.py

cd ..

echo ""
echo "✅ DEMONSTRATION COMPLETED!"
echo ""
echo "🎯 What was demonstrated:"
echo "   ✅ Project Genji system status verified"
echo "   ✅ Prefect 3.x workflows executed successfully"
echo "   ✅ Task orchestration working properly"
echo "   ✅ Error handling and fallback mechanisms tested"
echo ""
echo "🚀 Production Deployment Ready!"
echo "   • Use ./deploy_prefect_flows.sh to deploy workflows"
echo "   • Start server with ./start_prefect_server.sh"
echo "   • Access UI at http://localhost:4200"
echo ""
