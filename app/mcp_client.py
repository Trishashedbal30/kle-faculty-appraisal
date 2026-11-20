"""Official MCP client adapter for the local appraisal server."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPClientAdapter:
    """Thin wrapper around a local stdio MCP server for the departmental connector."""

    def __init__(
        self,
        db_path: str | None = None,
        *,
        command: str | None = None,
        args: list[str] | None = None,
        timeout: float = 30.0,
    ):
        self.db_path = str(Path(db_path) if db_path else "")
        self.command = command or sys.executable
        self.args = list(args or ["-m", "app.mcp_server"])
        self.timeout = timeout
        if self.db_path:
            self.args.extend(["--db", self.db_path])
        self._session = None
        self._client = None

    async def __aenter__(self):
        self._params = StdioServerParameters(command=self.command, args=self.args)
        self._client = stdio_client(self._params)
        self._read, self._write = await self._client.__aenter__()
        self._session = ClientSession(self._read, self._write)
        await self._session.__aenter__()
        await asyncio.wait_for(self._session.initialize(), timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if hasattr(self, '_session') and self._session is not None:
            try:
                await self._session.__aexit__(exc_type, exc, tb)
            except Exception:
                pass
            self._session = None
        if hasattr(self, '_client') and self._client is not None:
            try:
                await self._client.__aexit__(exc_type, exc, tb)
            except Exception:
                pass
            self._client = None

    async def list_tools(self):
        return await asyncio.wait_for(self._session.list_tools(), timeout=self.timeout)

    async def call_tool(self, name: str, **kwargs: Any):
        return await asyncio.wait_for(self._session.call_tool(name, arguments=kwargs or None), timeout=self.timeout)

    async def get_faculty_profile(self, faculty_id: str, actor_role: str = "faculty", actor_faculty_id: str | None = None):
        response = await self.call_tool(
            "get_faculty_profile",
            faculty_id=faculty_id,
            actor_role=actor_role,
            actor_faculty_id=actor_faculty_id,
        )
        return _extract_tool_payload(response)

    async def list_activity_records(self, faculty_id: str, category: str | None = None, actor_role: str = "faculty", actor_faculty_id: str | None = None):
        response = await self.call_tool(
            "list_activity_records",
            faculty_id=faculty_id,
            category=category,
            actor_role=actor_role,
            actor_faculty_id=actor_faculty_id,
        )
        return _extract_tool_payload(response)


def _extract_tool_payload(response):
    if hasattr(response, "content"):
        if response.content and hasattr(response.content[0], "text"):
            text = response.content[0].text
            if isinstance(text, str):
                try:
                    import json

                    return json.loads(text)
                except Exception:
                    return text
        if response.content and hasattr(response.content[0], "root"):
            return response.content[0].root
    return response


async def probe(db_path: str | None = None, timeout: float = 30.0):
    async with MCPClientAdapter(db_path=db_path, timeout=timeout) as client:
        tools = await asyncio.wait_for(client.list_tools(), timeout=timeout)
        names = {tool.name for tool in tools.tools}
        return {"tools": sorted(names), "count": len(names)}


if __name__ == "__main__":
    asyncio.run(probe())
