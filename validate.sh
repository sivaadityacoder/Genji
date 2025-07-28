#!/bin/bash

# Project Genji - System Validation Script
# This script validates that all components are properly configured

echo "🔍 Validating Project Genji Configuration..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 exists"
        return 0
    else
        echo -e "${RED}❌${NC} $1 missing"
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} Directory $1 exists"
        return 0
    else
        echo -e "${RED}❌${NC} Directory $1 missing"
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 is executable"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $1 is not executable (run: chmod +x $1)"
        return 1
    fi
}

# Validation counters
PASSED=0
FAILED=0

echo "📁 Checking Project Structure..."

# Core directories
check_directory "python-analysis-module" && ((PASSED++)) || ((FAILED++))
check_directory "streamlit-dashboard" && ((PASSED++)) || ((FAILED++))
check_directory "n8n-workflows" && ((PASSED++)) || ((FAILED++))
check_directory "docs" && ((PASSED++)) || ((FAILED++))

echo ""
echo "📄 Checking Core Files..."

# Core Python files
check_file "python-analysis-module/main.py" && ((PASSED++)) || ((FAILED++))
check_file "python-analysis-module/data_collector.py" && ((PASSED++)) || ((FAILED++))
check_file "streamlit-dashboard/app.py" && ((PASSED++)) || ((FAILED++))

# Configuration files
check_file "requirements.txt" && ((PASSED++)) || ((FAILED++))
check_file "python-analysis-module/.env.example" && ((PASSED++)) || ((FAILED++))
check_file "Dockerfile" && ((PASSED++)) || ((FAILED++))
check_file "docker-compose.yml" && ((PASSED++)) || ((FAILED++))

# Scripts
check_file "setup.sh" && ((PASSED++)) || ((FAILED++))
check_file "run_data_collection.sh" && ((PASSED++)) || ((FAILED++))
check_file "run_analysis.sh" && ((PASSED++)) || ((FAILED++))
check_file "run_dashboard.sh" && ((PASSED++)) || ((FAILED++))

echo ""
echo "🔧 Checking Script Permissions..."

# Check executable permissions
check_executable "setup.sh" && ((PASSED++)) || ((FAILED++))
check_executable "run_data_collection.sh" && ((PASSED++)) || ((FAILED++))
check_executable "run_analysis.sh" && ((PASSED++)) || ((FAILED++))
check_executable "run_dashboard.sh" && ((PASSED++)) || ((FAILED++))

echo ""
echo "📚 Checking Documentation..."

# Documentation files
check_file "README.md" && ((PASSED++)) || ((FAILED++))
check_file "docs/TECHNICAL_DOC.md" && ((PASSED++)) || ((FAILED++))
check_file "docs/USER_MANUAL.md" && ((PASSED++)) || ((FAILED++))
check_file "docs/database_setup.sql" && ((PASSED++)) || ((FAILED++))
check_file "PROJECT_STATUS.md" && ((PASSED++)) || ((FAILED++))

echo ""
echo "🔗 Checking Workflow Configuration..."

# n8n workflow
check_file "n8n-workflows/genji-pipeline.json" && ((PASSED++)) || ((FAILED++))

echo ""
echo "🐍 Checking Python Dependencies..."

# Check if requirements.txt has essential packages
if [ -f "requirements.txt" ]; then
    if grep -q "google-generativeai" requirements.txt; then
        echo -e "${GREEN}✅${NC} Google Generative AI dependency found"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} Google Generative AI dependency missing"
        ((FAILED++))
    fi
    
    if grep -q "streamlit" requirements.txt; then
        echo -e "${GREEN}✅${NC} Streamlit dependency found"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} Streamlit dependency missing"
        ((FAILED++))
    fi
    
    if grep -q "psycopg2-binary" requirements.txt; then
        echo -e "${GREEN}✅${NC} PostgreSQL dependency found"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} PostgreSQL dependency missing"
        ((FAILED++))
    fi
fi

echo ""
echo "📊 Validation Summary"
echo "==================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

TOTAL=$((PASSED + FAILED))
SUCCESS_RATE=$((PASSED * 100 / TOTAL))

echo "Success Rate: $SUCCESS_RATE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All validations passed! Project Genji is ready for deployment.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure your .env file with API keys"
    echo "2. Set up PostgreSQL database"
    echo "3. Run ./setup.sh to install dependencies"
    echo "4. Start the system with the run_*.sh scripts"
else
    echo -e "${YELLOW}⚠️ Some validations failed. Please fix the issues above before proceeding.${NC}"
fi

echo ""
echo "For help and documentation, see:"
echo "- README.md (Getting started guide)"
echo "- docs/TECHNICAL_DOC.md (Technical details)"
echo "- docs/USER_MANUAL.md (User guide)"
echo "- PROJECT_STATUS.md (Build status)"
