"""
Project Genji - Prefect Deployment Configuration
Automated deployment setup for production scheduling
"""

from prefect import flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule, CronSchedule
from prefect.infrastructure import Process
from prefect.blocks.system import Secret
from datetime import timedelta
import os

# Import our flows
from genji_pipeline import genji_pipeline_flow, daily_report_flow

def create_deployments():
    """Create and register Prefect deployments"""
    
    # Main pipeline deployment - runs every 4 hours
    pipeline_deployment = Deployment.build_from_flow(
        flow=genji_pipeline_flow,
        name="genji-pipeline-production",
        version="1.0.0",
        description="Production deployment of Project Genji market intelligence pipeline",
        tags=["genji", "production", "market-intelligence", "ai"],
        schedule=IntervalSchedule(interval=timedelta(hours=4)),
        work_pool_name="default-agent-pool",
        infrastructure=Process(
            env={
                "PREFECT_LOGGING_LEVEL": "INFO",
                "PYTHONPATH": "/home/coder/startup/genji"
            }
        ),
        parameters={}
    )
    
    # Daily report deployment - runs at 8 AM JST every day
    daily_report_deployment = Deployment.build_from_flow(
        flow=daily_report_flow,
        name="genji-daily-report",
        version="1.0.0",
        description="Daily comprehensive report for Project Genji",
        tags=["genji", "reporting", "daily"],
        schedule=CronSchedule(cron="0 8 * * *", timezone="Asia/Tokyo"),
        work_pool_name="default-agent-pool",
        infrastructure=Process(
            env={
                "PREFECT_LOGGING_LEVEL": "INFO",
                "PYTHONPATH": "/home/coder/startup/genji"
            }
        ),
        parameters={}
    )
    
    return pipeline_deployment, daily_report_deployment

def deploy_all():
    """Deploy all flows to Prefect"""
    print("🚀 Deploying Project Genji flows to Prefect...")
    
    pipeline_deployment, daily_report_deployment = create_deployments()
    
    # Deploy the main pipeline
    pipeline_deployment_id = pipeline_deployment.apply()
    print(f"✅ Pipeline deployment created: {pipeline_deployment_id}")
    
    # Deploy the daily report
    daily_deployment_id = daily_report_deployment.apply()
    print(f"✅ Daily report deployment created: {daily_deployment_id}")
    
    print("\n📋 Deployment Summary:")
    print("=" * 50)
    print(f"Main Pipeline: {pipeline_deployment.name}")
    print(f"  - Schedule: Every 4 hours")
    print(f"  - ID: {pipeline_deployment_id}")
    print(f"\nDaily Report: {daily_report_deployment.name}")
    print(f"  - Schedule: Daily at 8 AM JST")
    print(f"  - ID: {daily_deployment_id}")
    
    print("\n🎯 Next Steps:")
    print("1. Start Prefect agent: `prefect agent start -p default-agent-pool`")
    print("2. View UI: `prefect server start` then visit http://localhost:4200")
    print("3. Monitor flows in the Prefect dashboard")

if __name__ == "__main__":
    deploy_all()
