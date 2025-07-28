#!/bin/bash

# Start Prefect Agent
echo "🤖 Starting Prefect agent..."

# Activate virtual environment
source venv/bin/activate

# Start the agent with the default work pool
echo "Starting Prefect agent for default-agent-pool..."
prefect agent start -p default-agent-pool
