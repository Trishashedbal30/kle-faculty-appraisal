"""Official MCP server for the local KLE appraisal connector."""
from __future__ import annotations

import argparse
import ipaddress
import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from .connector import Connector
from .memory import retrieve
from .store import Store

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _loopback_host(value: str) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("MCP SSE must bind to a numeric loopback address.") from exc
    if not address.is_loopback:
        raise argparse.ArgumentTypeError("External MCP binding is disabled until caller authentication is implemented.")
    return value


def _make_user(role: str, faculty_id: str | None = None):
    return {"id": faculty_id or "mcp-user", "role": role, "faculty_id": faculty_id}


def _resolve_store(db_path: str | None = None):
    demo_dir = PROJECT_ROOT / "runtime-demo"
    if demo_dir.is_symlink():
        raise ValueError("MCP requires the repository-local synthetic runtime-demo directory.")
    demo_root = demo_dir.resolve()
    store_path = Path(db_path) if db_path else demo_root / "app.db"
    if not store_path.is_absolute():
        store_path = PROJECT_ROOT / store_path
    store_path = store_path.resolve()
    try:
        store_path.relative_to(demo_root)
    except ValueError as exc:
        raise ValueError("MCP database must be inside runtime-demo; real application databases are not allowed.") from exc

    os.environ["APP_DB"] = str(store_path)
    store = Store()
    meta = store.get("meta", "import", {})
    notes = meta.get("notes", []) if isinstance(meta, dict) else []
    if not any(isinstance(note, str) and note.startswith("SYNTHETIC SANDBOX:") for note in notes):
        raise ValueError("MCP requires an initialized synthetic demo database; authentication is not implemented.")
    return store


def build_server(db_path: str | None = None) -> MCPServer:
    store = _resolve_store(db_path)
    connector = Connector(store)
    server = MCPServer(
        "kle-faculty-appraisal",
        title="KLE Faculty Appraisal Connector",
        description="Local synthetic-demo connector only. Caller authentication is not implemented; external access is prohibited.",
        version="1.0.0",
    )

    @server.tool(name="get_faculty_profile", description="Return a profile from the synthetic demo database. The caller is not authenticated.")
    def get_faculty_profile(faculty_id: str, actor_role: str = "faculty", actor_faculty_id: str | None = None):
        user = _make_user(actor_role, actor_faculty_id or (faculty_id if actor_role == "faculty" else None))
        return connector.profile(user, faculty_id)

    @server.tool(name="check_source_consent", description="Return the consent record from the synthetic demo database.")
    def check_source_consent(faculty_id: str, source_id: str, actor_role: str = "faculty", actor_faculty_id: str | None = None):
        user = _make_user(actor_role, actor_faculty_id or (faculty_id if actor_role == "faculty" else None))
        consent = store.get("consents", f"{faculty_id}:{source_id}")
        if not consent:
            return {"faculty_id": faculty_id, "source_id": source_id, "granted": False, "reason": "No matching consent record"}
        if actor_role == "faculty":
            if user.get("faculty_id") != faculty_id:
                raise ValueError("Faculty access is restricted to the matching faculty ID.")
        return {"faculty_id": faculty_id, "source_id": source_id, "granted": bool(consent.get("granted")), "consent": consent}

    @server.tool(name="list_activity_records", description="List activity records from the synthetic demo database.")
    def list_activity_records(faculty_id: str, category: str | None = None, actor_role: str = "faculty", actor_faculty_id: str | None = None):
        user = _make_user(actor_role, actor_faculty_id or (faculty_id if actor_role == "faculty" else None))
        rows = connector.candidates(user, faculty_id, category)
        out = []
        for row in rows:
            consent = store.get("consents", f"{faculty_id}:{row['source_id']}")
            if not consent or not consent.get("granted"):
                continue
            evidence = store.get("evidence", f"{faculty_id}:{row['id']}")
            source = store.get("sources", row["source_id"])
            out.append({
                "id": row["id"],
                "category": row["category"],
                "kind": row["kind"],
                "title": row["title"],
                "value": row.get("value"),
                "year": row.get("year"),
                "month": row.get("month"),
                "locator": row.get("locator"),
                "source_id": row["source_id"],
                "source_name": source.get("name") if source else None,
                "evidence_status": (evidence or {}).get("status"),
                "record_hash": (evidence or {}).get("record_hash"),
            })
        return {"faculty_id": faculty_id, "category": category, "records": out}

    @server.tool(name="get_approved_policy", description="Return a policy from the synthetic demo database and check its integrity.")
    def get_approved_policy(policy_id: str, actor_role: str = "admin"):
        user = _make_user(actor_role)
        return connector.policy(policy_id)

    @server.tool(name="search_evidence", description="Search evidence in the synthetic demo database; caller identity is not authenticated.")
    def search_evidence(faculty_id: str, query: str, category: str | None = None, actor_role: str = "faculty", actor_faculty_id: str | None = None):
        user = _make_user(actor_role, actor_faculty_id or (faculty_id if actor_role == "faculty" else None))
        return retrieve(store, user, faculty_id, query, category)

    return server


def main():
    parser = argparse.ArgumentParser(description="Run the official MCP server for the KLE Faculty Appraisal connector.")
    parser.add_argument("--db", help="Synthetic demo SQLite database path under runtime-demo/ only.")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="MCP transport to expose.")
    parser.add_argument("--host", type=_loopback_host, default="127.0.0.1", help="Loopback bind address for SSE transport; external access is disabled.")
    parser.add_argument("--port", type=int, default=8002, help="Port for the SSE transport.")
    args = parser.parse_args()
    run_server(args.transport, args.host, args.port, args.db)


def run_server(transport: str, host: str, port: int, db_path: str | None = None):
    if transport not in {"stdio", "sse"}:
        raise ValueError("MCP transport must be stdio or sse.")
    host = _loopback_host(host)
    server = build_server(db_path)
    if transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    main()
