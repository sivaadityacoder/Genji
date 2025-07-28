#!/bin/bash

# Project Genji - Status Check
# Shows the current status of all Project Genji components

echo "🧠 PROJECT GENJI - AI MARKET INTELLIGENCE PLATFORM"
echo "=================================================="
echo ""

# Check virtual environment
if [ -d "venv" ]; then
    echo "✅ Python virtual environment: Ready"
else
    echo "❌ Python virtual environment: Not found"
fi

# Check key files
echo ""
echo "📁 Core Components Status:"

if [ -f "python-analysis-module/main.py" ]; then
    echo "✅ AI Analysis Module: Ready"
else
    echo "❌ AI Analysis Module: Missing"
fi

if [ -f "streamlit-dashboard/app.py" ]; then
    echo "✅ Executive Dashboard: Ready"
else
    echo "❌ Executive Dashboard: Missing"
fi

if [ -f "data_collector.py" ]; then
    echo "✅ Data Collector: Ready"
else
    echo "❌ Data Collector: Missing"
fi

if [ -f "prefect-workflows/working_pipeline.py" ]; then
    echo "✅ Prefect 3.x Workflows: Ready"
else
    echo "❌ Prefect 3.x Workflows: Missing"
fi

if [ -f "docker-compose.yml" ]; then
    echo "✅ Docker Configuration: Ready"
else
    echo "❌ Docker Configuration: Missing"
fi

# Check if Prefect is installed
echo ""
echo "🔧 Prefect 3.x Status:"
source venv/bin/activate 2>/dev/null
if python -c "import prefect; print(f'✅ Prefect version: {prefect.__version__}')" 2>/dev/null; then
    echo "✅ Prefect is installed and ready"
else
    echo "❌ Prefect not installed or not accessible"
fi

echo ""
echo "🚀 Quick Start Commands:"
echo "   Setup Prefect:     ./setup_prefect.sh"
echo "   Start Server:      ./start_prefect_server.sh"
echo "   Deploy Flows:      ./deploy_prefect_flows.sh"
echo "   Run Pipeline:      ./run_prefect_pipeline.sh"
echo "   Full System:       ./run_full_system.sh"
echo ""
echo "🌐 Access Points:"
echo "   Prefect UI:        http://localhost:4200"
echo "   Dashboard:         http://localhost:8501"
echo ""
