"""
Project Genji - Prefect 3.x Deployment System
Updated for Prefect 3.x with proper deployment methods
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

# Import the working pipeline
sys.path.append(str(Path(__file__).parent))
from working_pipeline import simple_genji_pipeline, real_genji_pipeline

def deploy_simple_pipeline():
    """Deploy the simple pipeline with scheduling"""
    print("🚀 Deploying Simple Genji Pipeline...")
    
    # Deploy with serve() method for Prefect 3.x
    simple_genji_pipeline.serve(
        name="genji-simple-deployment",
        tags=["genji", "simple", "testing"],
        description="Simple Project Genji pipeline for testing and demonstration",
        interval=timedelta(hours=1),  # Run every hour for testing
        host="0.0.0.0",
        port=8000
    )

def deploy_real_pipeline():
    """Deploy the real pipeline with scheduling"""
    print("🚀 Deploying Real Genji Pipeline...")
    
    # Deploy with serve() method for Prefect 3.x
    real_genji_pipeline.serve(
        name="genji-production-deployment",
        tags=["genji", "production", "market-intelligence"],
        description="Production Project Genji market intelligence pipeline",
        interval=timedelta(hours=4),  # Run every 4 hours
        host="0.0.0.0",
        port=8001
    )

def create_scheduled_deployment():
    """Create a scheduled deployment using Prefect 3.x deploy method"""
    print("📦 Creating scheduled deployment...")
    
    # Use the new deploy method for Prefect 3.x
    deployment_id = real_genji_pipeline.deploy(
        name="genji-scheduled",
        work_pool_name="default",
        image="python:3.12",
        tags=["genji", "scheduled", "production"],
        description="Scheduled Project Genji pipeline running every 4 hours",
        interval=timedelta(hours=4),
        timezone="Asia/Tokyo"
    )
    
    print(f"✅ Deployment created with ID: {deployment_id}")
    return deployment_id

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Project Genji Prefect workflows")
    parser.add_argument("--type", choices=["simple", "real", "scheduled"], 
                       default="simple", help="Type of deployment")
    
    args = parser.parse_args()
    
    if args.type == "simple":
        deploy_simple_pipeline()
    elif args.type == "real":
        deploy_real_pipeline()
    elif args.type == "scheduled":
        create_scheduled_deployment()
    
    print("🎉 Deployment completed!")
