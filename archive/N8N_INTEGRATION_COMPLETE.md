# 🚀 Project Genji n8n Integration - Quick Setup Guide

## Current Status
✅ **Webhook Server**: Running perfectly on http://localhost:5000  
✅ **n8n Container**: Running on http://localhost:5678  
🔧 **PostgreSQL**: Container running but port not exposed  

## Fix PostgreSQL Connection (Run in PowerShell)

```powershell
# Stop and remove current postgres container
docker stop some-postgres
docker rm some-postgres

# Start PostgreSQL with exposed port and correct database
docker run -d \
  --name some-postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=genji_db \
  -p 5432:5432 \
  postgres

# Create the required database tables
docker exec -i some-postgres psql -U postgres -d genji_db << 'EOF'
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
);

CREATE TABLE IF NOT EXISTS analysis_logs (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES market_insights(id),
    operation VARCHAR(50),
    status VARCHAR(20),
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF
```

## Import n8n Workflows

1. **Open n8n**: Go to http://localhost:5678
2. **Import workflows**:
   - Click "+" → "Import from File"
   - Import: `n8n-workflows/genji-rss-workflow.json`
   - Import: `n8n-workflows/genji-bulk-workflow.json`

3. **Configure HTTP Request nodes** in both workflows:
   - Change URL from `http://localhost:5000` to `http://host.docker.internal:5000`
   - This allows n8n container to reach your WSL webhook server

## Test Everything

After fixing PostgreSQL, run:
```bash
cd /home/coder/startup/genji/python-analysis-module
./test_complete_integration.sh
```

## Workflow URLs for n8n Configuration

- **Single Article**: `http://host.docker.internal:5000/webhook/n8n/article`
- **Bulk Articles**: `http://host.docker.internal:5000/webhook/n8n/articles`
- **Health Check**: `http://host.docker.internal:5000/webhook/n8n/status`

## Expected Flow

1. **n8n** fetches RSS feeds every 4-6 hours
2. **n8n** sends articles to Project Genji webhook
3. **Project Genji** stores articles in PostgreSQL
4. **Google Gemini AI** analyzes content (Japanese + English)
5. **Results** stored back in database
6. **Streamlit dashboard** shows insights

---

**Your Project Genji n8n integration is 95% complete! Just fix the PostgreSQL port and you're ready to go! 🎉**
