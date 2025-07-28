"""
Project Genji - Advanced Prefect Flows
Enhanced workflows with monitoring, error handling, and notifications
"""

import os
import sys
import json
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from prefect import flow, task, get_run_logger
from prefect.task_runners import ThreadPoolTaskRunner
from prefect.blocks.system import Secret
from prefect.artifacts import create_table_artifact, create_markdown_artifact
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from python_analysis_module.data_collector import DataCollector
from python_analysis_module.main import GenjiAnalyzer

@task(retries=3, retry_delay_seconds=60, tags=["data-collection"])
def enhanced_data_collection() -> Dict[str, any]:
    """
    Enhanced data collection with detailed metrics and error tracking
    """
    logger = get_run_logger()
    logger.info("🔄 Starting enhanced data collection...")
    
    start_time = datetime.now()
    collection_metrics = {
        "start_time": start_time.isoformat(),
        "sources_processed": 0,
        "articles_collected": 0,
        "errors": [],
        "processing_time_seconds": 0,
        "success_rate": 0.0
    }
    
    try:
        collector = DataCollector()
        
        # Track metrics for each source
        source_results = []
        total_sources = len(collector.rss_sources)
        
        for source in collector.rss_sources:
            source_start = datetime.now()
            try:
                articles = collector.collect_rss_articles(source)
                source_results.append({
                    "source": source["name"],
                    "articles_found": len(articles),
                    "status": "success",
                    "processing_time": (datetime.now() - source_start).total_seconds()
                })
                collection_metrics["sources_processed"] += 1
                
            except Exception as e:
                error_msg = f"Failed to collect from {source['name']}: {str(e)}"
                collection_metrics["errors"].append(error_msg)
                logger.error(error_msg)
                source_results.append({
                    "source": source["name"],
                    "articles_found": 0,
                    "status": "error",
                    "error": str(e)
                })
        
        # Store articles in database
        conn = collector.get_database_connection()
        articles_stored = 0
        
        for source in collector.rss_sources:
            try:
                articles = collector.collect_rss_articles(source)
                for article in articles:
                    if collector.store_article(conn, article):
                        articles_stored += 1
            except Exception as e:
                logger.error(f"Error storing articles from {source['name']}: {e}")
        
        conn.commit()
        conn.close()
        
        # Calculate final metrics
        end_time = datetime.now()
        collection_metrics.update({
            "end_time": end_time.isoformat(),
            "articles_collected": articles_stored,
            "processing_time_seconds": (end_time - start_time).total_seconds(),
            "success_rate": collection_metrics["sources_processed"] / total_sources * 100,
            "source_details": source_results
        })
        
        logger.info(f"✅ Enhanced data collection completed: {collection_metrics}")
        return collection_metrics
        
    except Exception as e:
        collection_metrics["errors"].append(f"Critical error: {str(e)}")
        logger.error(f"❌ Enhanced data collection failed: {e}")
        raise

@task(retries=2, retry_delay_seconds=30, tags=["ai-analysis"])
def enhanced_ai_analysis(collection_metrics: Dict[str, any]) -> Dict[str, any]:
    """
    Enhanced AI analysis with detailed processing metrics
    """
    logger = get_run_logger()
    
    if collection_metrics["articles_collected"] == 0:
        logger.info("ℹ️ No new articles to analyze")
        return {
            "articles_processed": 0,
            "analysis_metrics": {},
            "errors": [],
            "skipped": True
        }
    
    logger.info(f"🧠 Starting enhanced AI analysis...")
    
    start_time = datetime.now()
    analysis_metrics = {
        "start_time": start_time.isoformat(),
        "articles_processed": 0,
        "successful_analyses": 0,
        "failed_analyses": 0,
        "avg_processing_time_ms": 0,
        "sentiment_distribution": {"Positive": 0, "Negative": 0, "Neutral": 0},
        "business_impact_distribution": {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0},
        "errors": [],
        "gemini_api_calls": 0,
        "total_tokens_processed": 0
    }
    
    try:
        analyzer = GenjiAnalyzer()
        conn = analyzer.get_database_connection()
        
        # Get unanalyzed articles with details
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, raw_text, LENGTH(raw_text) as text_length
                FROM market_insights 
                WHERE summary_jp IS NULL 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            articles = cur.fetchall()
        
        processing_times = []
        
        for article_id, title, raw_text, text_length in articles:
            try:
                article_start = datetime.now()
                
                # Perform AI analysis
                analysis_result = analyzer.analyze_text_with_gemini(raw_text, title)
                analysis_metrics["gemini_api_calls"] += 1
                analysis_metrics["total_tokens_processed"] += text_length
                
                if analysis_result:
                    # Update database
                    success = analyzer.update_article_analysis(conn, article_id, analysis_result)
                    
                    if success:
                        analysis_metrics["successful_analyses"] += 1
                        
                        # Track sentiment distribution
                        sentiment = analysis_result.get("sentiment_label", "Unknown")
                        if sentiment in analysis_metrics["sentiment_distribution"]:
                            analysis_metrics["sentiment_distribution"][sentiment] += 1
                        
                        # Track business impact distribution
                        impact = analysis_result.get("business_impact", "Unknown")
                        if impact in analysis_metrics["business_impact_distribution"]:
                            analysis_metrics["business_impact_distribution"][impact] += 1
                        
                        # Track processing time
                        processing_time = (datetime.now() - article_start).total_seconds() * 1000
                        processing_times.append(processing_time)
                        
                        logger.info(f"✅ Analyzed article {article_id}: {sentiment} sentiment, {impact} impact")
                    else:
                        analysis_metrics["failed_analyses"] += 1
                        analysis_metrics["errors"].append(f"Database update failed for article {article_id}")
                else:
                    analysis_metrics["failed_analyses"] += 1
                    analysis_metrics["errors"].append(f"AI analysis failed for article {article_id}")
                
            except Exception as e:
                analysis_metrics["failed_analyses"] += 1
                error_msg = f"Error processing article {article_id}: {str(e)}"
                analysis_metrics["errors"].append(error_msg)
                logger.error(error_msg)
        
        conn.close()
        
        # Calculate final metrics
        analysis_metrics.update({
            "end_time": datetime.now().isoformat(),
            "articles_processed": len(articles),
            "avg_processing_time_ms": sum(processing_times) / len(processing_times) if processing_times else 0,
            "success_rate": analysis_metrics["successful_analyses"] / len(articles) * 100 if articles else 0,
            "total_processing_time_seconds": (datetime.now() - start_time).total_seconds()
        })
        
        logger.info(f"✅ Enhanced AI analysis completed: {analysis_metrics}")
        return analysis_metrics
        
    except Exception as e:
        analysis_metrics["errors"].append(f"Critical analysis error: {str(e)}")
        logger.error(f"❌ Enhanced AI analysis failed: {e}")
        raise

@task(tags=["monitoring"])
def create_performance_dashboard(
    collection_metrics: Dict[str, any], 
    analysis_metrics: Dict[str, any]
) -> str:
    """
    Create performance dashboard artifacts in Prefect UI
    """
    logger = get_run_logger()
    
    # Create data collection summary table
    collection_data = []
    if "source_details" in collection_metrics:
        for source in collection_metrics["source_details"]:
            collection_data.append([
                source["source"],
                source["articles_found"],
                source["status"],
                f"{source.get('processing_time', 0):.2f}s" if "processing_time" in source else "N/A"
            ])
    
    create_table_artifact(
        key="data-collection-summary",
        table=collection_data,
        description="Data Collection Performance by Source"
    )
    
    # Create analysis performance summary
    if not analysis_metrics.get("skipped", False):
        sentiment_data = [
            ["Positive", analysis_metrics["sentiment_distribution"]["Positive"]],
            ["Negative", analysis_metrics["sentiment_distribution"]["Negative"]],
            ["Neutral", analysis_metrics["sentiment_distribution"]["Neutral"]]
        ]
        
        create_table_artifact(
            key="sentiment-analysis-summary",
            table=sentiment_data,
            description="Sentiment Analysis Distribution"
        )
        
        # Create comprehensive markdown report
        markdown_report = f"""
# Project Genji Pipeline Performance Report

## 📊 Data Collection Summary
- **Sources Processed**: {collection_metrics['sources_processed']}
- **Articles Collected**: {collection_metrics['articles_collected']}
- **Success Rate**: {collection_metrics['success_rate']:.1f}%
- **Processing Time**: {collection_metrics['processing_time_seconds']:.2f}s

## 🧠 AI Analysis Summary
- **Articles Processed**: {analysis_metrics['articles_processed']}
- **Successful Analyses**: {analysis_metrics['successful_analyses']}
- **Success Rate**: {analysis_metrics.get('success_rate', 0):.1f}%
- **Average Processing Time**: {analysis_metrics['avg_processing_time_ms']:.0f}ms
- **Gemini API Calls**: {analysis_metrics['gemini_api_calls']}

## 📈 Sentiment Distribution
- Positive: {analysis_metrics['sentiment_distribution']['Positive']}
- Negative: {analysis_metrics['sentiment_distribution']['Negative']}
- Neutral: {analysis_metrics['sentiment_distribution']['Neutral']}

## 🎯 Business Impact Distribution
- High: {analysis_metrics['business_impact_distribution']['High']}
- Medium: {analysis_metrics['business_impact_distribution']['Medium']}
- Low: {analysis_metrics['business_impact_distribution']['Low']}
- Unknown: {analysis_metrics['business_impact_distribution']['Unknown']}

## ⚠️ Errors
### Data Collection Errors: {len(collection_metrics.get('errors', []))}
### Analysis Errors: {len(analysis_metrics.get('errors', []))}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        create_markdown_artifact(
            key="pipeline-performance-report",
            markdown=markdown_report,
            description=f"Comprehensive pipeline performance report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    
    logger.info("📊 Performance dashboard artifacts created")
    return "Dashboard created successfully"

@flow(
    name="genji-production-pipeline",
    description="Production-grade Project Genji pipeline with monitoring and error handling",
    task_runner=ThreadPoolTaskRunner(max_workers=4),
    log_prints=True,
    timeout_seconds=3600
)
def production_genji_pipeline() -> Dict[str, any]:
    """
    Production-grade Prefect flow with comprehensive monitoring
    """
    logger = get_run_logger()
    logger.info("🚀 Starting production Project Genji pipeline...")
    
    # Step 1: Enhanced data collection
    collection_metrics = enhanced_data_collection()
    
    # Step 2: Enhanced AI analysis
    analysis_metrics = enhanced_ai_analysis(collection_metrics)
    
    # Step 3: Create performance dashboard
    dashboard_result = create_performance_dashboard(collection_metrics, analysis_metrics)
    
    # Step 4: Validate database health
    health_metrics = validate_database_health()
    
    # Compile comprehensive results
    pipeline_result = {
        "pipeline_id": f"genji-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "execution_time": datetime.now().isoformat(),
        "collection_metrics": collection_metrics,
        "analysis_metrics": analysis_metrics,
        "health_metrics": health_metrics,
        "dashboard_status": dashboard_result,
        "overall_status": "success",
        "total_errors": len(collection_metrics.get("errors", [])) + len(analysis_metrics.get("errors", []))
    }
    
    logger.info(f"🎉 Production pipeline completed: {pipeline_result['pipeline_id']}")
    return pipeline_result

@task
def validate_database_health() -> Dict[str, any]:
    """Enhanced database health validation"""
    logger = get_run_logger()
    logger.info("🏥 Running comprehensive database health check...")
    
    try:
        analyzer = GenjiAnalyzer()
        conn = analyzer.get_database_connection()
        
        health_data = {}
        
        with conn.cursor() as cur:
            # Basic counts
            cur.execute("SELECT COUNT(*) FROM market_insights")
            health_data["total_articles"] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM market_insights WHERE summary_jp IS NOT NULL")
            health_data["analyzed_articles"] = cur.fetchone()[0]
            
            # Recent activity (24 hours)
            cur.execute("""
                SELECT COUNT(*) FROM market_insights 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)
            health_data["articles_24h"] = cur.fetchone()[0]
            
            # Analysis performance (24 hours)
            cur.execute("""
                SELECT COUNT(*) FROM analysis_logs 
                WHERE created_at > NOW() - INTERVAL '24 hours' AND status = 'completed'
            """)
            health_data["successful_analyses_24h"] = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) FROM analysis_logs 
                WHERE created_at > NOW() - INTERVAL '24 hours' AND status = 'failed'
            """)
            health_data["failed_analyses_24h"] = cur.fetchone()[0]
            
            # Average processing times
            cur.execute("""
                SELECT AVG(processing_time_ms) FROM analysis_logs 
                WHERE created_at > NOW() - INTERVAL '24 hours' AND processing_time_ms IS NOT NULL
            """)
            avg_time = cur.fetchone()[0]
            health_data["avg_processing_time_ms"] = float(avg_time) if avg_time else 0
            
            # Sentiment distribution (last 100 articles)
            cur.execute("""
                SELECT sentiment_label, COUNT(*) FROM market_insights 
                WHERE sentiment_label IS NOT NULL 
                ORDER BY analyzed_at DESC 
                LIMIT 100
            """)
            sentiment_data = cur.fetchall()
            health_data["recent_sentiment_distribution"] = {
                row[0]: row[1] for row in sentiment_data
            }
        
        conn.close()
        
        # Calculate health scores
        analysis_rate = (health_data["analyzed_articles"] / health_data["total_articles"] * 100) if health_data["total_articles"] > 0 else 0
        error_rate = (health_data["failed_analyses_24h"] / (health_data["successful_analyses_24h"] + health_data["failed_analyses_24h"]) * 100) if (health_data["successful_analyses_24h"] + health_data["failed_analyses_24h"]) > 0 else 0
        
        health_data.update({
            "analysis_rate_percent": analysis_rate,
            "error_rate_24h_percent": error_rate,
            "health_score": max(0, 100 - error_rate),  # Simple health score
            "timestamp": datetime.now().isoformat(),
            "status": "healthy" if error_rate < 10 and analysis_rate > 80 else "warning" if error_rate < 25 else "critical"
        })
        
        logger.info(f"✅ Database health check completed: {health_data['status']} status")
        return health_data
        
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        raise

if __name__ == "__main__":
    # Test the production pipeline
    result = production_genji_pipeline()
    print(f"Production pipeline result: {json.dumps(result, indent=2, default=str)}")
