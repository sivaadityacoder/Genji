#!/bin/bash

# Project Genji - Clean Test Suite
# Comprehensive testing with clear error reporting

echo "🧪 PROJECT GENJI CLEAN TEST SUITE"
echo "================================="

# Test configuration
BASE_URL="http://localhost:5000"
WEBHOOK_URL="$BASE_URL/webhook/n8n/article"
STATUS_URL="$BASE_URL/webhook/n8n/status"
BULK_URL="$BASE_URL/webhook/n8n/articles"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_status() {
    echo -e "\n📊 Testing system status..."
    response=$(curl -s -w "%{http_code}" -o /tmp/status_test.json "$STATUS_URL")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ Status endpoint working${NC}"
        cat /tmp/status_test.json | python -m json.tool
        return 0
    else
        echo -e "${RED}❌ Status endpoint failed (HTTP $response)${NC}"
        return 1
    fi
}

test_single_article() {
    echo -e "\n📝 Testing single article processing..."
    
    test_data='{
        "title": "Clean Test: AI Innovation in Japanese Manufacturing",
        "content": "Japanese manufacturing companies are implementing advanced AI systems to optimize production efficiency and maintain global competitiveness. This technological transformation is reshaping traditional manufacturing processes.",
        "link": "https://example.com/clean-test-article",
        "pubDate": "2025-01-27T20:00:00Z"
    }'
    
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$test_data" \
        -o /tmp/single_test.json \
        "$WEBHOOK_URL")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ Single article processing successful${NC}"
        cat /tmp/single_test.json | python -m json.tool
        return 0
    else
        echo -e "${RED}❌ Single article processing failed (HTTP $response)${NC}"
        cat /tmp/single_test.json
        return 1
    fi
}

test_bulk_articles() {
    echo -e "\n📚 Testing bulk article processing..."
    
    bulk_data='{
        "articles": [
            {
                "title": "Bulk Test 1: Tokyo Tech Startups",
                "content": "Tokyo technology startups are receiving record venture capital investments.",
                "link": "https://example.com/bulk-test-1",
                "pubDate": "2025-01-27T20:10:00Z"
            },
            {
                "title": "Bulk Test 2: Japanese AI Research",
                "content": "Japanese universities are leading breakthrough AI research initiatives.",
                "link": "https://example.com/bulk-test-2",
                "pubDate": "2025-01-27T20:20:00Z"
            }
        ]
    }'
    
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$bulk_data" \
        -o /tmp/bulk_test.json \
        "$BULK_URL")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ Bulk article processing successful${NC}"
        cat /tmp/bulk_test.json | python -m json.tool
        return 0
    else
        echo -e "${RED}❌ Bulk article processing failed (HTTP $response)${NC}"
        cat /tmp/bulk_test.json
        return 1
    fi
}

test_error_handling() {
    echo -e "\n🚫 Testing error handling..."
    
    # Test invalid JSON
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "invalid json" \
        -o /tmp/error_test.json \
        "$WEBHOOK_URL")
    
    if [ "$response" = "400" ] || [ "$response" = "500" ]; then
        echo -e "${GREEN}✅ Error handling working (HTTP $response)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Unexpected error response (HTTP $response)${NC}"
        return 1
    fi
}

# Main test execution
main() {
    echo "🔍 Testing webhook server at: $BASE_URL"
    
    # Check if server is running
    if ! curl -s "$STATUS_URL" > /dev/null; then
        echo -e "${RED}❌ Server not responding at $BASE_URL${NC}"
        echo "🔧 Start the server with: ./start_clean.sh"
        exit 1
    fi
    
    # Run tests
    tests_passed=0
    total_tests=4
    
    test_status && ((tests_passed++))
    test_single_article && ((tests_passed++))
    test_bulk_articles && ((tests_passed++))
    test_error_handling && ((tests_passed++))
    
    # Results
    echo -e "\n📊 TEST RESULTS"
    echo "==============="
    echo -e "Tests passed: ${GREEN}$tests_passed${NC}/$total_tests"
    
    if [ $tests_passed -eq $total_tests ]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
        echo ""
        echo "🔗 n8n Configuration:"
        echo "   URL: http://172.18.6.71:5000/webhook/n8n/article"
        echo "   Method: POST"
        echo "   Content-Type: application/json"
        echo ""
        echo "🚀 Your clean Project Genji integration is ready!"
    else
        echo -e "${YELLOW}⚠️ Some tests failed. Review the errors above.${NC}"
    fi
    
    # Cleanup
    rm -f /tmp/*_test.json
}

# Run tests
main
