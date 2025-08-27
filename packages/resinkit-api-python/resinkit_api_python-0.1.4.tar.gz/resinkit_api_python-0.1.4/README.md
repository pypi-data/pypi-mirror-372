
# Running the service

```bash
nohup uvicorn resinkit_api.main:app --host 0.0.0.0 --port 8602 > /opt/resinkit/api/resinkit_api.log 2>&1 &
```


## Connect to MCP

```json
{
  "mcpServers": {
    "rsk": {
      "type": "http",
      "url": "http://localhost:8603/mcp-server/mcp"
    }
  }
}
```