# Project Genji - Docker Setup for n8n Integration

## Current Status ✅
Your webhook server is running successfully at http://localhost:5000

## Issue 🔧
Your PostgreSQL container port 5432 is not exposed to the host, so the webhook can't connect.

## Solution Options:

### Option 1: Restart PostgreSQL with Exposed Port (Recommended)
```bash
# Stop current postgres container
docker stop some-postgres
docker rm some-postgres

# Start postgres with exposed port
docker run -d \
  --name some-postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=genji_db \
  -p 5432:5432 \
  postgres
```

### Option 2: Use Docker Network (Advanced)
```bash
# Create a shared network
docker network create genji-network

# Restart containers on the same network
docker stop some-postgres n8n
docker rm some-postgres n8n

docker run -d \
  --name postgres-genji \
  --network genji-network \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=genji_db \
  -p 5432:5432 \
  postgres

docker run -d \
  --name n8n-genji \
  --network genji-network \
  -p 5678:5678 \
  n8nio/n8n
```

## Test Connection After Fix:
```bash
curl http://localhost:5000/webhook/n8n/status
```

## n8n Workflow Configuration:

### In your n8n workflows, use these webhook URLs:
- Single article: `http://host.docker.internal:5000/webhook/n8n/article`
- Bulk articles: `http://host.docker.internal:5000/webhook/n8n/articles`
- Health check: `http://host.docker.internal:5000/webhook/n8n/status`

Note: Use `host.docker.internal` instead of `localhost` when calling from n8n container to WSL.

## Update .env file:
```bash
# Update database password in /home/coder/startup/genji/.env
DB_PASSWORD=mysecretpassword
```
