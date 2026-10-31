"""Evidence-aware recommendation behavior; no inferred licenses or quality claims."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp"))
from recommend import recommend_projects  # noqa: E402
from server import handle_message  # noqa: E402

DATA = [
    {
        "id": "demo/voicekit", "name": "VoiceKit", "description": "SIP phone voice agent",
        "topics": ["voice", "sip"], "primary_category": "A.1", "project_type": "framework",
        "primary_language": "Python", "languages": ["Python"], "license": "MIT",
        "archived": False, "score": 63, "checked_at": "2026-07-07",
        "repository_url": "https://github.com/demo/voicekit",
    },
    {
        "id": "demo/oldvoice", "name": "Old Voice", "description": "voice telephony SIP",
        "project_type": "framework", "primary_language": "Python", "license": "MIT",
        "archived": True, "score": 90,
    },
    {
        "id": "demo/other", "name": "Other", "description": "voice agent",
        "project_type": "framework", "primary_language": "TypeScript", "license": None,
        "score": 99,
    },
]


def test_ranked_search_and_explicit_evidence():
    result = recommend_projects(DATA, "voice sip", limit=10)
    assert result[0]["id"] == "demo/voicekit"
    assert result[0]["matched_terms"] == ["voice", "sip"]
    assert "license" not in result[0]["unknown_fields"]
    assert result[0]["ranking_note"].startswith("Lexical")


def test_unknown_license_does_not_pass_mit_filter():
    result = recommend_projects(DATA, "voice", license="MIT", language="Python")
    assert [x["id"] for x in result] == ["demo/voicekit"]


def test_archive_is_opt_in():
    assert "demo/oldvoice" not in {x["id"] for x in recommend_projects(DATA, "voice")}
    assert "demo/oldvoice" in {x["id"] for x in recommend_projects(DATA, "voice", include_archived=True)}


def test_unknown_fields_remain_unknown_and_unmatched_terms_visible():
    result = recommend_projects(DATA, "voice incompatibleterm")
    assert result[0]["unmatched_terms"] == ["incompatibleterm"]
    unknown = next(x for x in result if x["id"] == "demo/other")
    assert "license" in unknown["unknown_fields"]


def test_mcp_recommend_is_read_only_and_bounded():
    before = json.dumps(DATA, sort_keys=True)
    response = handle_message({
        "jsonrpc": "2.0", "id": 42, "method": "tools/call",
        "params": {"name": "recommend", "arguments": {"query": "telefonagent", "limit": 2}},
    }, DATA, {})
    result = json.loads(response["result"]["content"][0]["text"])
    assert len(result) <= 2
    assert any(x["id"] == "demo/voicekit" for x in result)
    assert json.dumps(DATA, sort_keys=True) == before


def test_empty_query_not_return_everything():
    assert recommend_projects(DATA, "") == []
    assert recommend_projects(DATA, "mit und der") == []


def test_filters_fail_closed_on_missing_fields():
    assert recommend_projects(DATA, "voice", min_score=100) == []
    assert recommend_projects(DATA, "voice", project_type="MCP server") == []
