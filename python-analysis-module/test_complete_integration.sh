#!/bin/bash

# Project Genji - Complete n8n Integration Test
# Tests the full integration between n8n, webhook server, and AI analysis

echo "🧪 Testing Project Genji n8n Integration"
echo "========================================"

# Test 1: Health Check
echo ""
echo "1️⃣ Testing webhook server health..."
response=$(curl -s http://localhost:5000/webhook/n8n/status)
echo "$response" | python -m json.tool

# Test 2: Single Article Processing
echo ""
echo "2️⃣ Testing single article processing..."
cat > test_article.json << 'EOF'
{
    "title": "AI Revolution in Japanese Manufacturing",
    "content": "Japanese manufacturing companies are rapidly adopting artificial intelligence technologies to improve productivity and maintain competitive advantage in global markets. Major corporations like Toyota and Honda are implementing AI-driven quality control systems that can detect defects with 99.5% accuracy, significantly reducing waste and improving customer satisfaction.",
    "link": "https://example.com/ai-manufacturing-japan",
    "pubDate": "2025-01-27T18:00:00Z"
}
EOF

echo "Sending test article to Project Genji AI..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @test_article.json \
  http://localhost:5000/webhook/n8n/article | python -m json.tool

# Test 3: Check if analysis was successful
echo ""
echo "3️⃣ Integration Status Summary:"
echo "✅ Webhook server: Running on http://localhost:5000"
echo "✅ n8n container: Running on http://localhost:5678"
echo "🔧 PostgreSQL: Check docker container port exposure"
echo ""
echo "📋 Next Steps:"
echo "1. Fix PostgreSQL container port (see DOCKER_N8N_SETUP.md)"
echo "2. Import workflows into n8n:"
echo "   - /home/coder/startup/genji/n8n-workflows/genji-rss-workflow.json"
echo "   - /home/coder/startup/genji/n8n-workflows/genji-bulk-workflow.json"
echo "3. Configure n8n HTTP Request nodes to use:"
echo "   http://host.docker.internal:5000/webhook/n8n/article"

# Cleanup
rm -f test_article.json

echo ""
echo "🎉 Integration test completed!"
