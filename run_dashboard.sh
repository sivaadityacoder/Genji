#!/bin/bash

# Run Streamlit Dashboard for Project Genji

echo "🌐 Starting Project Genji dashboard..."

# Activate virtual environment
source venv/bin/activate

# Start Streamlit dashboard
streamlit run streamlit-dashboard/app.py

echo "✅ Dashboard started! Access it at http://localhost:8501"
