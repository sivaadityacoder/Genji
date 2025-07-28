#!/bin/bash

# Project Genji - Clean Startup Script
# Optimized startup with proper error handling

set -e

echo "🚀 Starting Project Genji (Clean Version)"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "clean_n8n_integration.py" ]; then
    echo "❌ Error: Run this script from python-analysis-module directory"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ../logs
mkdir -p ../backup

# Activate virtual environment
echo "🐍 Activating virtual environment..."
cd ..
source venv/bin/activate
cd python-analysis-module

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q flask requests psycopg2-binary google-generativeai python-dotenv

# Test database connection
echo "🗄️ Testing database connection..."
python -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('../.env.clean')

try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'genji_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'aditya'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )
    print('✅ Database connection successful')
    
    # Create tables if they don't exist
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS market_insights (
            id SERIAL PRIMARY KEY,
            title TEXT,
            raw_text TEXT,
            url TEXT UNIQUE,
            source VARCHAR(100),
            category VARCHAR(50),
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            summary_jp TEXT,
            summary_en TEXT,
            sentiment_label VARCHAR(20),
            sentiment_score DECIMAL(3,2),
            topics TEXT[],
            key_entities TEXT[],
            business_impact VARCHAR(20),
            analyzed_at TIMESTAMP,
            analysis_version VARCHAR(10)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES market_insights(id),
            operation VARCHAR(50),
            status VARCHAR(20),
            error_message TEXT,
            processing_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print('✅ Database tables ready')
    conn.close()
    
except Exception as e:
    print(f'❌ Database error: {e}')
    print('🔧 Fix: Update PostgreSQL container or .env.clean file')
    import sys
    sys.exit(1)
"

# Test API key (if provided)
echo "🤖 Testing AI configuration..."
python -c "
import os
from dotenv import load_dotenv

load_dotenv('../.env.clean')
api_key = os.getenv('GOOGLE_API_KEY', '')

if api_key == 'your_valid_gemini_api_key_here' or not api_key:
    print('⚠️ AI analysis disabled: No valid API key configured')
    print('🔧 Fix: Update GOOGLE_API_KEY in .env.clean file')
else:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content('Test', timeout=5)
        print('✅ AI analysis enabled: API key validated')
    except Exception as e:
        print(f'⚠️ AI analysis disabled: {str(e)[:50]}...')
"

echo ""
echo "🌐 Starting webhook server..."
echo "   URL: http://localhost:5000"
echo "   Status: http://localhost:5000/webhook/n8n/status"
echo "   n8n URL to use: http://172.18.6.71:5000/webhook/n8n/article"
echo ""
echo "Press Ctrl+C to stop"
echo "===================="

# Use the clean environment file
cp ../.env.clean ../.env

# Start the clean server
python clean_n8n_integration.py
