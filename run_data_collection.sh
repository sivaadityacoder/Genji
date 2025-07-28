#!/bin/bash

# Run Data Collection for Project Genji

echo "🔄 Starting data collection..."

# Activate virtual environment
source venv/bin/activate

# Run data collection
python python-analysis-module/data_collector.py

echo "✅ Data collection completed!"
