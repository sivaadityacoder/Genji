# Fix PostgreSQL Password and Configure n8n HTTP Node

## Step 1: Update PostgreSQL Container Password

Run these commands in PowerShell to update the PostgreSQL password:

```powershell
# Connect to the PostgreSQL container and update password
docker exec -it some-postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'aditya';"

# Or restart with the correct password:
docker stop some-postgres
docker rm some-postgres
docker run -d --name some-postgres -e POSTGRES_PASSWORD=aditya -e POSTGRES_DB=genji_db -p 5432:5432 postgres
```

## Step 2: Configure n8n HTTP Request Node

In your n8n workflow, click on the "Send to Project Genji" HTTP node and configure:

### HTTP Request Node Configuration:
- **Method**: `POST`
- **URL**: `http://host.docker.internal:5000/webhook/n8n/article`
- **Authentication**: None
- **Headers**: 
  ```
  Content-Type: application/json
  ```

### Body Configuration:
Select "JSON" and use this structure:
```json
{
  "title": "{{ $json.title }}",
  "content": "{{ $json.contentSnippet || $json.description }}",
  "link": "{{ $json.link }}",
  "pubDate": "{{ $json.pubDate || $json.isoDate }}"
}
```

## Step 3: Why use `host.docker.internal`?

- Your n8n is running in a Docker container
- Your webhook server is running in WSL2 (outside Docker)
- `localhost` from inside the container refers to the container itself
- `host.docker.internal` allows Docker containers to access the host machine

## Step 4: Test the Configuration

After updating the HTTP node, you can test it by:
1. Clicking "Test step" on the HTTP node
2. Or running the entire workflow manually
3. Check the webhook server logs for incoming requests

## Alternative: If host.docker.internal doesn't work

Try these URLs in order:
1. `http://host.docker.internal:5000/webhook/n8n/article`
2. `http://172.17.0.1:5000/webhook/n8n/article` (Docker bridge IP)
3. `http://192.168.1.x:5000/webhook/n8n/article` (Your actual WSL IP)

To find your WSL IP:
```bash
ip addr show eth0 | grep inet
```
