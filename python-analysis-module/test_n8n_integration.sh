#!/bin/bash

# Project Genji - Test n8n Integration
# Tests the webhook endpoints and n8n integration

set -e

echo "🧪 Testing Project Genji n8n Integration..."

# Check if webhook server is running
echo "1️⃣ Testing webhook server health..."
response=$(curl -s -w "%{http_code}" http://localhost:5000/webhook/n8n/status -o /tmp/health_check.json)

if [ "$response" = "200" ]; then
    echo "✅ Webhook server is healthy"
    cat /tmp/health_check.json | python -m json.tool
else
    echo "❌ Webhook server not responding (HTTP $response)"
    echo "   Make sure to start it with: ./start_webhook_server.sh"
    exit 1
fi

echo ""
echo "2️⃣ Testing single article processing..."

# Test single article webhook
test_article='{
    "title": "Test Article: AI Revolution in Japanese Business",
    "content": "This is a test article about artificial intelligence transforming Japanese business practices. Companies are adopting AI technologies to improve efficiency and competitiveness in global markets.",
    "link": "https://example.com/test-article",
    "pubDate": "2025-01-27T10:00:00Z"
}'

echo "Sending test article..."
response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$test_article" \
    http://localhost:5000/webhook/n8n/article \
    -o /tmp/single_test.json)

if [ "$response" = "200" ]; then
    echo "✅ Single article processing successful"
    cat /tmp/single_test.json | python -m json.tool
else
    echo "❌ Single article processing failed (HTTP $response)"
    cat /tmp/single_test.json
fi

echo ""
echo "3️⃣ Testing bulk article processing..."

# Test bulk articles webhook
test_bulk='{
    "articles": [
        {
            "title": "Test Article 1: Tech Innovation in Tokyo",
            "content": "Tokyo tech companies are leading innovation in AI and robotics sectors.",
            "link": "https://example.com/test-1",
            "pubDate": "2025-01-27T10:00:00Z"
        },
        {
            "title": "Test Article 2: Japanese Market Trends",
            "content": "Market analysis shows positive trends in Japanese technology exports.",
            "link": "https://example.com/test-2", 
            "pubDate": "2025-01-27T10:30:00Z"
        }
    ]
}'

echo "Sending bulk test articles..."
response=$(curl -s -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$test_bulk" \
    http://localhost:5000/webhook/n8n/articles \
    -o /tmp/bulk_test.json)

if [ "$response" = "200" ]; then
    echo "✅ Bulk article processing successful"
    cat /tmp/bulk_test.json | python -m json.tool
else
    echo "❌ Bulk article processing failed (HTTP $response)"
    cat /tmp/bulk_test.json
fi

echo ""
echo "🎉 n8n Integration testing completed!"
echo ""
echo "📊 Next steps:"
echo "1. Import workflow files into n8n:"
echo "   - n8n-workflows/genji-rss-workflow.json (single article processing)"
echo "   - n8n-workflows/genji-bulk-workflow.json (bulk processing)"
echo "2. Configure n8n HTTP Request nodes to use http://localhost:5000 endpoints"
echo "3. Activate the workflows in n8n interface"
echo "4. Monitor the logs for processing results"

# Cleanup temp files
rm -f /tmp/health_check.json /tmp/single_test.json /tmp/bulk_test.json
