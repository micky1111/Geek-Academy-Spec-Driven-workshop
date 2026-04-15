from __future__ import annotations

import json
import os
from typing import Any

import aiohttp


class SupportOpsMcpClient:
    def __init__(self, endpoint: str | None = None, timeout_seconds: float = 3.0) -> None:
        self._endpoint = endpoint or os.getenv("SUPPORT_OPS_MCP_URL", "http://127.0.0.1:5058/mcp")
        self._timeout_seconds = timeout_seconds

    async def lookup_customer(self, customer_email: str) -> dict[str, Any] | None:
        if not customer_email:
            return None
        payload = await self.call_tool(
            "lookup_customer",
            {
                "customer_email": customer_email,
            },
        )
        if not payload.get("found"):
            return None
        customer = payload.get("customer")
        return customer if isinstance(customer, dict) else None

    async def create_support_ticket(
        self,
        customer_email: str,
        subject: str,
        *,
        priority: str = "normal",
        notes: str = "",
    ) -> dict[str, Any] | None:
        return await self.call_tool(
            "create_support_ticket",
            {
                "customer_email": customer_email,
                "subject": subject,
                "priority": priority,
                "notes": notes,
            },
        )

    async def create_refund_request(
        self,
        customer_email: str,
        *,
        amount: float | None,
        reason: str,
    ) -> dict[str, Any] | None:
        return await self.call_tool(
            "create_refund_request",
            {
                "customer_email": customer_email,
                "amount": amount,
                "reason": reason,
            },
        )

    async def create_escalation(
        self,
        *,
        customer_email: str | None,
        reason: str,
        summary: str,
    ) -> dict[str, Any] | None:
        args: dict[str, Any] = {
            "reason": reason,
            "summary": summary,
        }
        if customer_email:
            args["customer_email"] = customer_email
        return await self.call_tool("create_escalation", args)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self._endpoint, json=request) as response:
                    response.raise_for_status()
                    body = await response.json()
        except Exception:
            return {}

        if "error" in body:
            return {}

        result = body.get("result", {})
        structured = result.get("structuredContent")
        if isinstance(structured, dict):
            return structured

        content = result.get("content")
        if isinstance(content, list) and content:
            text = content[0].get("text")
            if isinstance(text, str):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    return {}

        return {}
