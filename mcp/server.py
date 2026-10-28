#!/usr/bin/env python3
"""Read-only WERKAtlas MCP server.

Tools: search, get_project, list_categories.
Transport: newline-delimited JSON-RPC on stdin/stdout (MCP stdio spec).
The process does not write the catalog, open a shell, or install anything.

Usage:
    python mcp/server.py --catalog data/catalog.json --taxonomy data/taxonomy.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "werkatlas"
SERVER_VERSION = "2.0.0"
MAX_LIMIT = 50
MAX_QUERY_CHARS = 200
SEARCH_FIELDS = ("id", "name", "repository", "description", "primary_category", "project_type")


def search_projects(entries: list, query: str, category: str | None, limit: int) -> list[dict]:
    bounded = _limit(limit)
    needle = (query or "").strip().lower()[:MAX_QUERY_CHARS]
    found = []
    for entry in entries:
        if category and entry.get("primary_category") != category:
            continue
        if needle and needle not in _haystack(entry):
            continue
        found.append(dict(entry))
        if len(found) >= bounded:
            break
    return found


def get_project(entries: list, project_id: str) -> dict | None:
    for entry in entries:
        if entry.get("id") == project_id:
            return dict(entry)
    return None


def list_categories(taxonomy: dict) -> list[dict]:
    categories = []
    for group_id, group in taxonomy.get("categories", {}).items():
        for subcategory_id, subcategory in group.get("subcategories", {}).items():
            categories.append(
                {
                    "id": subcategory_id,
                    "name": subcategory.get("name", ""),
                    "group": group_id,
                }
            )
    return categories


def handle_message(message: dict, entries: list, taxonomy: dict) -> dict | None:
    method = message.get("method")
    if isinstance(method, str) and method.startswith("notifications/"):
        return None
    msg_id = message.get("id")
    if method == "initialize":
        return _result(
            msg_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
    if method == "ping":
        return _result(msg_id, {})
    if method == "tools/list":
        return _result(msg_id, {"tools": _tool_definitions()})
    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name == "search":
            payload = search_projects(
                entries,
                str(arguments.get("query") or ""),
                arguments.get("category"),
                arguments.get("limit", 10),
            )
            return _tool_result(msg_id, payload)
        if name == "get_project":
            project = get_project(entries, str(arguments.get("id") or ""))
            if project is None:
                return _error(msg_id, -32004, f"unknown project: {arguments.get('id')}")
            return _tool_result(msg_id, project)
        if name == "list_categories":
            return _tool_result(msg_id, list_categories(taxonomy))
        return _error(msg_id, -32602, f"unknown tool: {name}")
    return _error(msg_id, -32601, f"unknown method: {method}")


def encode_message(payload: dict) -> bytes:
    """One JSON-RPC object per line, no embedded newlines."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def read_message(buffer: bytes) -> tuple[dict | None, bytes]:
    """Parse one newline-delimited JSON message from buffer."""
    newline = buffer.find(b"\n")
    if newline == -1:
        return None, buffer
    line = buffer[:newline].strip()
    rest = buffer[newline + 1 :]
    if not line:
        return read_message(rest) if rest else (None, rest)
    return json.loads(line.decode("utf-8")), rest


def serve(entries: list, taxonomy: dict) -> None:
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    buffer = b""
    while True:
        chunk = stdin.read(1)
        if not chunk:
            return
        buffer += chunk
        while True:
            message, buffer = read_message(buffer)
            if message is None:
                break
            response = handle_message(message, entries, taxonomy)
            if response is not None:
                stdout.write(encode_message(response))
                stdout.flush()


def _haystack(entry: dict) -> str:
    parts = [str(entry.get(field) or "") for field in SEARCH_FIELDS]
    return " ".join(parts).lower()


def _limit(value: object) -> int:
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = 10
    return max(1, min(number, MAX_LIMIT))


def _result(msg_id: object, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id: object, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _tool_result(msg_id: object, payload: object) -> dict:
    return _result(
        msg_id,
        {
            "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
            "isError": False,
        },
    )


def _tool_definitions() -> list[dict]:
    return [
        {
            "name": "search",
            "description": "Find catalog projects by text and optional category id. Read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "category": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT},
                },
            },
        },
        {
            "name": "get_project",
            "description": "Return one catalog project by owner/name id. Read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
        {
            "name": "list_categories",
            "description": "List taxonomy subcategory ids and names. Read-only.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def _load(path: str) -> dict:
    with Path(path).open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only WERKAtlas MCP server")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--taxonomy", default="data/taxonomy.json")
    args = parser.parse_args(argv)
    catalog = _load(args.catalog)
    taxonomy = _load(args.taxonomy)
    entries = catalog.get("entries", catalog if isinstance(catalog, list) else [])
    serve(entries, taxonomy)
    return 0


if __name__ == "__main__":
    sys.exit(main())
