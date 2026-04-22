import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="SupportOps MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_CUSTOMERS_PATH = (
    Path(__file__).resolve().parent.parent / "mock-data-lab2" / "mock_customers.json"
)
_ACTIONS: list[dict[str, Any]] = []


def _load_customers() -> list[dict[str, Any]]:
    if not _CUSTOMERS_PATH.exists():
        return []
    return json.loads(_CUSTOMERS_PATH.read_text(encoding="utf-8"))


def _tool_defs() -> list[dict[str, Any]]:
    return [
        {
            "name": "lookup_customer",
            "description": "Find customer account details by email",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string"},
                },
                "required": ["customer_email"],
            },
        },
        {
            "name": "create_support_ticket",
            "description": "Create a support ticket",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string"},
                    "subject": {"type": "string"},
                    "priority": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["customer_email", "subject"],
            },
        },
        {
            "name": "create_refund_request",
            "description": "Create a refund request record",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string"},
                    "amount": {"type": "number"},
                    "reason": {"type": "string"},
                },
                "required": ["customer_email"],
            },
        },
        {
            "name": "create_escalation",
            "description": "Open escalation to specialist queue",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string"},
                    "reason": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["reason"],
            },
        },
    ]


def _jsonrpc_result(rid: Any, result: dict[str, Any]) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": result})


def _jsonrpc_error(rid: Any, code: int, message: str) -> JSONResponse:
    return JSONResponse(
        {
            "jsonrpc": "2.0",
            "id": rid,
            "error": {"code": code, "message": message},
        },
        status_code=200,
    )


def _tool_call_result(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload),
            }
        ],
        "structuredContent": payload,
        "isError": False,
    }


def _call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()

    if name == "lookup_customer":
        email = str(args.get("customer_email", "")).strip().lower()
        customer = next(
            (c for c in _load_customers() if c.get("customer_email", "").lower() == email),
            None,
        )
        return _tool_call_result({"found": customer is not None, "customer": customer})

    if name == "create_support_ticket":
        ticket_id = f"TKT-{len(_ACTIONS) + 1:05d}"
        record = {
            "ticket_id": ticket_id,
            "type": "support_ticket",
            "created_at": now,
            "customer_email": args.get("customer_email"),
            "subject": args.get("subject"),
            "priority": args.get("priority", "normal"),
            "notes": args.get("notes", ""),
            "status": "open",
        }
        _ACTIONS.append(record)
        return _tool_call_result(record)

    if name == "create_refund_request":
        refund_id = f"RFD-{len(_ACTIONS) + 1:05d}"
        record = {
            "refund_id": refund_id,
            "type": "refund_request",
            "created_at": now,
            "customer_email": args.get("customer_email"),
            "amount": args.get("amount"),
            "reason": args.get("reason", "customer_request"),
            "status": "submitted",
        }
        _ACTIONS.append(record)
        return _tool_call_result(record)

    if name == "create_escalation":
        escalation_id = f"ESC-{len(_ACTIONS) + 1:05d}"
        record = {
            "escalation_id": escalation_id,
            "type": "escalation",
            "created_at": now,
            "customer_email": args.get("customer_email"),
            "reason": args.get("reason"),
            "summary": args.get("summary", ""),
            "status": "queued",
            "sla": "4 business hours",
        }
        _ACTIONS.append(record)
        return _tool_call_result(record)

    raise ValueError(f"Unknown tool: {name}")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "endpoint": "/mcp"}


@app.post("/mcp")
async def mcp_endpoint(payload: dict[str, Any]) -> JSONResponse:
    rid = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if method == "initialize":
        return _jsonrpc_result(
            rid,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "support-ops-mcp", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        )

    if method == "tools/list":
        return _jsonrpc_result(rid, {"tools": _tool_defs()})

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if not name:
            return _jsonrpc_error(rid, -32602, "Missing tool name")
        try:
            result = _call_tool(str(name), dict(args))
        except Exception as ex:
            return _jsonrpc_error(rid, -32000, str(ex))
        return _jsonrpc_result(rid, result)

    return _jsonrpc_error(rid, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5058)
