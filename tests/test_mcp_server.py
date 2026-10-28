"""Read-only catalog tools for agents. No shell and no writes."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "mcp"))

from server import (  # noqa: E402
    encode_message,
    get_project,
    handle_message,
    list_categories,
    read_message,
    search_projects,
)

ENTRIES = [
    {
        "id": "acme/widget",
        "name": "Widget",
        "description": "alpha parser for local notes",
        "primary_category": "D.20",
        "project_type": "MCP server",
        "score": 70,
        "stars": 12,
        "license": "MIT",
        "repository_url": "https://github.com/acme/widget",
        "security_notes": ["keeps files in the workspace"],
    },
    {
        "id": "acme/other",
        "name": "Other",
        "description": "unrelated notes",
        "primary_category": "E.29",
        "project_type": "library",
        "score": 40,
        "stars": 1,
        "license": None,
        "repository_url": "https://github.com/acme/other",
    },
]
TAXONOMY = {
    "categories": {
        "D": {"name": "MCP", "subcategories": {"D.20": {"name": "MCP servers"}}},
        "E": {"name": "Skills", "subcategories": {"E.29": {"name": "Agent skills"}}},
    }
}


def test_search_matches_name_and_get_project_returns_the_same_id():
    found = search_projects(ENTRIES, "widget", None, 10)
    assert [item["id"] for item in found] == ["acme/widget"]
    assert get_project(ENTRIES, "acme/widget")["security_notes"] == [
        "keeps files in the workspace"
    ]
    assert get_project(ENTRIES, "missing/repo") is None


def test_search_can_filter_by_category_and_caps_the_limit():
    found = search_projects(ENTRIES, "", "E.29", 50)
    assert [item["id"] for item in found] == ["acme/other"]
    many = [
        {
            "id": f"acme/item-{index}",
            "name": "Item",
            "description": "x",
            "primary_category": "D.20",
        }
        for index in range(60)
    ]
    assert len(search_projects(many, "", None, 500)) == 50


def test_list_categories_uses_the_taxonomy_names():
    categories = list_categories(TAXONOMY)
    assert categories == [
        {"id": "D.20", "name": "MCP servers", "group": "D"},
        {"id": "E.29", "name": "Agent skills", "group": "E"},
    ]


def test_tools_call_rejects_unknown_tool():
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "shell", "arguments": {"command": "rm -rf /"}},
        },
        ENTRIES,
        TAXONOMY,
    )
    assert response["error"]["code"] == -32602
    assert "shell" in response["error"]["message"]


def test_tools_call_search_returns_catalog_text():
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": "parser", "limit": 5}},
        },
        ENTRIES,
        TAXONOMY,
    )
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload[0]["id"] == "acme/widget"
    listed = handle_message(
        {"jsonrpc": "2.0", "id": 8, "method": "tools/list"},
        ENTRIES,
        TAXONOMY,
    )
    names = [tool["name"] for tool in listed["result"]["tools"]]
    assert names == ["search", "get_project", "list_categories"]


def test_framing_round_trip():
    raw = encode_message({"jsonrpc": "2.0", "id": 1, "method": "ping"})
    message, rest = read_message(raw)
    assert rest == b""
    assert message["method"] == "ping"


def test_real_catalog_search_finds_n8n_without_writing(tmp_path):
    catalog_path = ROOT / "data" / "catalog.json"
    before = catalog_path.read_bytes()
    catalog = json.loads(before.decode("utf-8"))
    taxonomy = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    found = search_projects(catalog["entries"], "n8n", None, 5)
    assert any(item["id"] == "n8n-io/n8n" for item in found)
    project = get_project(catalog["entries"], "n8n-io/n8n")
    assert project["repository_url"] == "https://github.com/n8n-io/n8n"
    categories = list_categories(taxonomy)
    assert len(categories) == 81
    assert catalog_path.read_bytes() == before
