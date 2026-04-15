# SupportOps MCP Server (Lab 2)

Local streamable HTTP MCP-style server for support operations.

## Run

```powershell
cd support-ops-mcp-python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn server:app --host 127.0.0.1 --port 5058
```

MCP endpoint: `http://127.0.0.1:5058/mcp`

## Tools

- lookup_customer (data access)
- create_support_ticket (business action)
- create_refund_request (business action)
- create_escalation (business action)
