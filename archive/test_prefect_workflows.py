#!/usr/bin/env python3
"""
Project Genji - Prefect Workflow Testing and Validation
Complete testing suite for Prefect workflows
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_environment_setup():
    """Test that all environment variables are properly set"""
    print("🔧 Testing environment setup...")
    
    required_vars = [
        "GOOGLE_API_KEY",
        "DB_HOST", 
        "DB_PORT",
        "DB_NAME",
        "DB_USER", 
        "DB_PASSWORD"
    ]
    
    # Load from .env file
    from dotenv import load_dotenv
    load_dotenv('python-analysis-module/.env')
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please configure your .env file properly")
        return False
    
    print("✅ Environment setup is valid")
    return True

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🗄️ Testing database connection...")
    
    try:
        from python_analysis_module.main import GenjiAnalyzer
        
        analyzer = GenjiAnalyzer()
        conn = analyzer.get_database_connection()
        
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ Database connected: {version}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_gemini_api():
    """Test Google Gemini API connection"""
    print("🤖 Testing Google Gemini API...")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv('python-analysis-module/.env')
        
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content("Test connection. Respond with 'OK'.")
        
        if "OK" in response.text or "ok" in response.text.lower():
            print("✅ Gemini API connection successful")
            return True
        else:
            print(f"⚠️ Gemini API responded but with unexpected content: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False

def test_data_collection():
    """Test data collection functionality"""
    print("📊 Testing data collection...")
    
    try:
        from python_analysis_module.data_collector import DataCollector
        
        collector = DataCollector()
        
        # Test collecting from first source only
        if collector.rss_sources:
            source = collector.rss_sources[0]
            articles = collector.collect_rss_articles(source)
            
            if articles:
                print(f"✅ Data collection successful: {len(articles)} articles from {source['name']}")
                return True
            else:
                print(f"⚠️ Data collection returned no articles from {source['name']}")
                return False
        else:
            print("❌ No RSS sources configured")
            return False
            
    except Exception as e:
        print(f"❌ Data collection failed: {e}")
        return False

def test_ai_analysis():
    """Test AI analysis functionality"""
    print("🧠 Testing AI analysis...")
    
    try:
        from python_analysis_module.main import GenjiAnalyzer
        
        analyzer = GenjiAnalyzer()
        
        # Test with sample text
        sample_text = "Apple Inc. announced strong quarterly earnings, showing significant growth in iPhone sales across Asian markets."
        sample_title = "Apple Reports Strong Q4 Earnings"
        
        result = analyzer.analyze_text_with_gemini(sample_text, sample_title)
        
        if result and isinstance(result, dict):
            required_keys = ["summary_jp", "summary_en", "sentiment_label", "topics"]
            if all(key in result for key in required_keys):
                print("✅ AI analysis successful")
                print(f"   Sentiment: {result.get('sentiment_label')}")
                print(f"   Topics: {result.get('topics', [])[:3]}")
                return True
            else:
                print(f"⚠️ AI analysis missing required fields: {result}")
                return False
        else:
            print("❌ AI analysis returned invalid result")
            return False
            
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return False

def test_prefect_flow():
    """Test Prefect flow execution"""
    print("🔄 Testing Prefect flow execution...")
    
    try:
        # Import the flow
        sys.path.append(str(Path(__file__).parent))
        from genji_pipeline import genji_pipeline_flow
        
        print("Running a test execution of the Prefect flow...")
        result = genji_pipeline_flow()
        
        if isinstance(result, dict) and "status" in result:
            print("✅ Prefect flow executed successfully")
            print(f"   Articles collected: {result.get('articles_collected', 0)}")
            print(f"   Articles analyzed: {result.get('articles_analyzed', 0)}")
            return True
        else:
            print(f"⚠️ Prefect flow returned unexpected result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Prefect flow execution failed: {e}")
        return False

def test_streamlit_dashboard():
    """Test that Streamlit dashboard can load"""
    print("🌐 Testing Streamlit dashboard...")
    
    try:
        # Test imports
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        
        # Test data loading function
        sys.path.append(str(project_root / "streamlit-dashboard"))
        
        # Simple import test
        with open(project_root / "streamlit-dashboard" / "app.py", 'r') as f:
            content = f.read()
            if "def load_data()" in content and "st.set_page_config" in content:
                print("✅ Streamlit dashboard code structure is valid")
                return True
            else:
                print("⚠️ Streamlit dashboard code structure issues")
                return False
                
    except Exception as e:
        print(f"❌ Streamlit dashboard test failed: {e}")
        return False

def run_full_integration_test():
    """Run a complete integration test"""
    print("\n" + "="*60)
    print("🚀 RUNNING FULL INTEGRATION TEST")
    print("="*60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Database Connection", test_database_connection),
        ("Gemini API", test_gemini_api),
        ("Data Collection", test_data_collection),
        ("AI Analysis", test_ai_analysis),
        ("Streamlit Dashboard", test_streamlit_dashboard),
        ("Prefect Flow", test_prefect_flow)
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("🎉 Project Genji is ready for production!")
    elif success_rate >= 70:
        print("⚠️ Project Genji needs some fixes before production")
    else:
        print("❌ Project Genji requires significant fixes")
    
    return results

def main():
    """Main test execution"""
    print("🧪 Project Genji - Prefect Workflow Testing Suite")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = run_full_integration_test()
    
    # Save results to file
    test_results_file = project_root / "test_results.json"
    with open(test_results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_tests": len(results),
                "passed_tests": sum(results.values()),
                "success_rate": sum(results.values()) / len(results) * 100
            }
        }, f, indent=2)
    
    print(f"\n📄 Test results saved to: {test_results_file}")
    print("\n🔗 Next Steps:")
    print("1. Fix any failed tests")
    print("2. Run: ./setup_prefect.sh")
    print("3. Run: ./start_prefect_server.sh")
    print("4. Run: ./deploy_prefect_flows.sh")
    print("5. Run: ./start_prefect_agent.sh")
    print("6. Access UI at: http://localhost:4200")

if __name__ == "__main__":
    main()
