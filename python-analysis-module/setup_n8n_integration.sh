#!/bin/bash

# Project Genji - n8n Integration Setup
# Sets up the webhook server and n8n workflow integration

set -e

echo "🔗 Setting up Project Genji n8n Integration..."

# Activate virtual environment
source ../venv/bin/activate

# Install additional dependencies for n8n integration
echo "📦 Installing Flask and additional dependencies..."
pip install flask requests

# Update requirements.txt
echo "📝 Updating requirements.txt..."
cat >> ../requirements.txt << EOF

# n8n Integration dependencies
flask>=2.3.0
requests>=2.31.0
EOF

# Create webhook service configuration
echo "⚙️ Creating webhook service configuration..."
cat > webhook_service.conf << EOF
[program:genji_webhook]
command=/home/coder/startup/genji/venv/bin/python /home/coder/startup/genji/python-analysis-module/n8n_integration.py
directory=/home/coder/startup/genji/python-analysis-module
autostart=true
autorestart=true
stderr_logfile=/var/log/genji_webhook.err.log
stdout_logfile=/var/log/genji_webhook.out.log
environment=PATH="/home/coder/startup/genji/venv/bin"
EOF

# Create environment template for webhooks
echo "📋 Creating environment template..."
cat > ../.env.webhook.template << EOF
# Webhook server configuration
WEBHOOK_PORT=5000
WEBHOOK_HOST=0.0.0.0

# Database configuration (same as main app)
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Google API configuration (same as main app)
GOOGLE_API_KEY=your_google_api_key_here
EOF

echo "✅ n8n Integration setup completed!"
echo ""
echo "🔧 Next steps:"
echo "1. Copy .env.webhook.template to .env and fill in your credentials"
echo "2. Start the webhook server: ./start_webhook_server.sh"
echo "3. Import n8n workflows from n8n-workflows/ directory"
echo "4. Configure n8n to use webhook endpoints at http://localhost:5000"
echo ""
echo "📡 Webhook endpoints:"
echo "   Single article: POST http://localhost:5000/webhook/n8n/article"
echo "   Bulk articles:  POST http://localhost:5000/webhook/n8n/articles"
echo "   Health check:   GET  http://localhost:5000/webhook/n8n/status"
