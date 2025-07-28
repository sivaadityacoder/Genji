"""
Project Genji - Prefect Workflow
Complete data pipeline orchestration using Prefect 3.x
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from prefect import flow, task, get_run_logger
from prefect.task_runners import ThreadPoolTaskRunner
import asyncio

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import our modules
try:
    from python_analysis_module.data_collector import DataCollector
    from python_analysis_module.main import GenjiAnalyzer
except ImportError as e:
    print(f"Warning: Could not import modules - {e}")
    DataCollector = None
    GenjiAnalyzer = None

@task(retries=3, retry_delay_seconds=60)
def collect_market_data() -> int:
    """
    Task to collect market data from RSS sources
    Returns the number of new articles collected
    """
    logger = get_run_logger()
    logger.info("🔄 Starting data collection task...")
    
    if DataCollector is None:
        logger.warning("DataCollector not available - returning 0")
        return 0
    
    try:
        collector = DataCollector()
        new_articles = collector.run_collection()
        
        logger.info(f"✅ Data collection completed. {new_articles} new articles collected")
        return new_articles
        
    except Exception as e:
        logger.error(f"❌ Data collection failed: {e}")
        raise

@task(retries=2, retry_delay_seconds=30)
def run_ai_analysis(new_articles_count: int) -> int:
    """
    Task to run AI analysis on collected articles
    Returns the number of articles successfully analyzed
    """
    logger = get_run_logger()
    
    if new_articles_count == 0:
        logger.info("ℹ️ No new articles to analyze")
        return 0
    
    if GenjiAnalyzer is None:
        logger.warning("GenjiAnalyzer not available - returning 0")
        return 0
    
    logger.info(f"🧠 Starting AI analysis for {new_articles_count} articles...")
    
    try:
        analyzer = GenjiAnalyzer()
        processed_count = analyzer.process_unanalyzed_articles(limit=20)
        
        logger.info(f"✅ AI analysis completed. {processed_count} articles processed")
        return processed_count
        
    except Exception as e:
        logger.error(f"❌ AI analysis failed: {e}")
        raise

@task
def validate_database_health() -> Dict[str, any]:
    """
    Task to validate database health and return system metrics
    """
    logger = get_run_logger()
    logger.info("🏥 Checking database health...")
    
    if GenjiAnalyzer is None:
        logger.warning("GenjiAnalyzer not available - returning mock health data")
        return {
            "total_articles": 0,
            "analyzed_articles": 0,
            "recent_articles": 0,
            "recent_errors": 0,
            "analysis_rate": 0,
            "timestamp": datetime.now().isoformat(),
            "status": "unavailable"
        }
    
    try:
        analyzer = GenjiAnalyzer()
        conn = analyzer.get_database_connection()
        
        with conn.cursor() as cur:
            # Check total articles
            cur.execute("SELECT COUNT(*) FROM market_insights")
            total_articles = cur.fetchone()[0]
            
            # Check analyzed articles
            cur.execute("SELECT COUNT(*) FROM market_insights WHERE summary_jp IS NOT NULL")
            analyzed_articles = cur.fetchone()[0]
            
            # Check recent articles (last 24 hours)
            cur.execute("""
                SELECT COUNT(*) FROM market_insights 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)
            recent_articles = cur.fetchone()[0]
            
            # Check processing errors (last 24 hours)
            cur.execute("""
                SELECT COUNT(*) FROM analysis_logs 
                WHERE status = 'failed' AND created_at > NOW() - INTERVAL '24 hours'
            """)
            recent_errors = cur.fetchone()[0]
        
        conn.close()
        
        health_metrics = {
            "total_articles": total_articles,
            "analyzed_articles": analyzed_articles,
            "recent_articles": recent_articles,
            "recent_errors": recent_errors,
            "analysis_rate": (analyzed_articles / total_articles * 100) if total_articles > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Database health check completed: {health_metrics}")
        return health_metrics
        
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        # Return fallback data instead of raising
        return {
            "total_articles": 0,
            "analyzed_articles": 0,
            "recent_articles": 0,
            "recent_errors": 1,
            "analysis_rate": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@task
def send_status_notification(
    collection_count: int, 
    analysis_count: int, 
    health_metrics: Dict[str, any]
) -> None:
    """
    Task to send status notifications (can be extended with email/Slack)
    """
    logger = get_run_logger()
    
    status_message = f"""
    📊 Project Genji Pipeline Status Report
    =====================================
    
    🔄 Data Collection: {collection_count} new articles
    🧠 AI Analysis: {analysis_count} articles processed
    📈 Total Articles: {health_metrics['total_articles']}
    ✅ Analyzed: {health_metrics['analyzed_articles']} ({health_metrics['analysis_rate']:.1f}%)
    🕐 Recent (24h): {health_metrics['recent_articles']}
    ❌ Errors (24h): {health_metrics['recent_errors']}
    
    Timestamp: {health_metrics['timestamp']}
    """
    
    logger.info(status_message)
    
    # Here you can add email/Slack notifications
    # For now, we'll just log the status

@flow(
    name="genji-market-intelligence-pipeline",
    description="Complete Project Genji data collection and AI analysis pipeline",
    task_runner=ThreadPoolTaskRunner(max_workers=3),
    log_prints=True
)
def genji_pipeline_flow() -> Dict[str, any]:
    """
    Main Prefect flow for Project Genji market intelligence pipeline
    
    This flow orchestrates:
    1. Data collection from RSS sources
    2. AI analysis using Google Gemini
    3. Database health monitoring
    4. Status reporting
    """
    logger = get_run_logger()
    logger.info("🚀 Starting Project Genji pipeline...")
    
    # Step 1: Collect market data
    collection_result = collect_market_data()
    
    # Step 2: Run AI analysis (depends on collection result)
    analysis_result = run_ai_analysis(collection_result)
    
    # Step 3: Check database health
    health_metrics = validate_database_health()
    
    # Step 4: Send status notification
    send_status_notification(collection_result, analysis_result, health_metrics)
    
    # Return pipeline summary
    pipeline_summary = {
        "run_timestamp": datetime.now().isoformat(),
        "articles_collected": collection_result,
        "articles_analyzed": analysis_result,
        "health_metrics": health_metrics,
        "status": "completed"
    }
    
    logger.info(f"🎉 Pipeline completed successfully: {pipeline_summary}")
    return pipeline_summary

@flow(name="genji-daily-report")
def daily_report_flow() -> Dict[str, any]:
    """
    Daily comprehensive report flow
    """
    logger = get_run_logger()
    logger.info("📊 Generating daily report...")
    
    try:
        analyzer = GenjiAnalyzer()
        conn = analyzer.get_database_connection()
        
        with conn.cursor() as cur:
            # Get daily statistics
            cur.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total_articles,
                    COUNT(CASE WHEN summary_jp IS NOT NULL THEN 1 END) as analyzed_articles,
                    AVG(CASE WHEN sentiment_score IS NOT NULL THEN sentiment_score END) as avg_sentiment
                FROM market_insights 
                WHERE created_at > NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            daily_stats = cur.fetchall()
        
        conn.close()
        
        report = {
            "report_date": datetime.now().date().isoformat(),
            "daily_statistics": [
                {
                    "date": str(row[0]),
                    "total_articles": row[1],
                    "analyzed_articles": row[2],
                    "avg_sentiment": float(row[3]) if row[3] else None
                }
                for row in daily_stats
            ]
        }
        
        logger.info(f"📈 Daily report generated: {len(daily_stats)} days of data")
        return report
        
    except Exception as e:
        logger.error(f"❌ Daily report generation failed: {e}")
        raise

if __name__ == "__main__":
    # Run the flow locally for testing
    result = genji_pipeline_flow()
    print(f"Pipeline result: {result}")
