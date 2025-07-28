#!/bin/bash

# Project Genji - Final n8n Integration Demo
# Shows the complete working integration

echo "🎉 PROJECT GENJI n8n INTEGRATION - FINAL DEMO"
echo "=============================================="

echo ""
echo "✅ STATUS CHECK:"
echo "=================="

# Check webhook server health
echo "🌐 Webhook Server Health:"
curl -s http://localhost:5000/webhook/n8n/status | python -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Status: {data['status']}\")
print(f\"   Database: {data['database']}\")
print(f\"   Timestamp: {data['timestamp']}\")
"

echo ""
echo "📊 Available Endpoints:"
echo "   POST http://localhost:5000/webhook/n8n/article   (Single article)"
echo "   POST http://localhost:5000/webhook/n8n/articles  (Bulk articles)"
echo "   GET  http://localhost:5000/webhook/n8n/status    (Health check)"

echo ""
echo "🗄️ Database Connection:"
cd /home/coder/startup/genji
source venv/bin/activate
python -c "
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM market_insights;')
    count = cur.fetchone()[0]
    print(f'   Articles in database: {count}')
    conn.close()
except Exception as e:
    print(f'   Database error: {e}')
"

echo ""
echo "🚀 INTEGRATION READY FOR n8n!"
echo "=============================="
echo "1. Open n8n at: http://localhost:5678"
echo "2. Import workflows from: n8n-workflows/"
echo "3. Configure HTTP Request nodes to use:"
echo "   http://host.docker.internal:5000/webhook/n8n/article"
echo ""
echo "🎯 Your AI-powered market intelligence system is ready!"
echo "   • RSS feeds → n8n → Project Genji → AI Analysis → Database"
echo "   • View results in Streamlit dashboard"
echo ""
