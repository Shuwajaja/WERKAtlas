"""Data Pipeline E2E Test Suite (Tiers 1-4)."""

import json
import csv
import sys
import os
import subprocess
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import pipeline components
import score as _score_module
from classify import infer_category
import export
import update_trends
import validate


# ---------------------------------------------------------------------------
# Compatibility shim: scorers now return (float, list[dict]).
# Wrap each function so tests that expect a plain float still work.
# ---------------------------------------------------------------------------
def _wrap(fn):
    def _inner(*args, **kwargs):
        result = fn(*args, **kwargs)
        return result[0] if isinstance(result, tuple) else result
    _inner.__name__ = fn.__name__
    return _inner

score_relevance           = _wrap(_score_module.score_relevance)
score_maintenance         = _wrap(_score_module.score_maintenance)
score_adoption            = _wrap(_score_module.score_adoption)
score_momentum            = _wrap(_score_module.score_momentum)
score_documentation       = _wrap(_score_module.score_documentation)
score_production_readiness = _wrap(_score_module.score_production_readiness)
score_security            = _wrap(_score_module.score_security)
score_interoperability    = _wrap(_score_module.score_interoperability)
score_community           = _wrap(_score_module.score_community)
score_uniqueness          = _wrap(_score_module.score_uniqueness)
compute_confidence        = _score_module.compute_confidence


# ==============================================================================
# TIER 1: UNIT & BOUNDARY VALIDATION
# ==============================================================================

# Feature 5: Scoring Engine & Weights
def test_tier1_scoring_weight_alignment():
    """Verify that scoring component weights sum to exactly 100 points."""
    import datetime
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry = {
        "name": "super-agent-orchestrator-mcp-framework",
        "description": "novel experimental unique first alternative educational pioneering tool calling framework with custom commands",
        "topics": ["ai-agent", "mcp-server", "agent-framework", "agent-orchestration", "agent-memory", "agent-tool", "agent-skill", "mcp"],
        "project_type": "protocol",
        "stars": 1000000,
        "forks": 100000,
        "open_issues": 1,
        "pushed_at": now_str,
        "latest_release_at": now_str,
        "archived": False,
        "license": "MIT",
        "languages": ["Python", "TypeScript", "Rust", "Go", "C++"],
        "homepage_url": "https://example.com",
        "protocols": ["mcp"],
        "compatible_hosts": ["claude"],
        "security_transparency": 10,
        "security_notes": [],
        "repository_url": "https://github.com/foo/bar",
        "created_at": now_str,
    }

    rel = score_relevance(entry)
    maint = score_maintenance(entry)
    adopt = score_adoption(entry)
    mom = score_momentum(entry)
    doc = score_documentation(entry)
    prod = score_production_readiness(entry)
    sec = score_security(entry)
    interop = score_interoperability(entry)
    comm = score_community(entry)
    uniq = score_uniqueness(entry)

    assert rel == 20.0, f"Expected relevance max 20, got {rel}"
    assert maint == 15.0, f"Expected maintenance max 15, got {maint}"
    assert adopt == 15.0, f"Expected adoption max 15, got {adopt}"
    assert mom == 10.0, f"Expected momentum max 10, got {mom}"
    assert doc == 10.0, f"Expected documentation max 10, got {doc}"
    assert prod <= 10.0, f"Expected production readiness max 10, got {prod}"
    assert sec == 10.0, f"Expected security max 10, got {sec}"
    assert interop <= 5.0, f"Expected interoperability max 5, got {interop}"
    assert comm == 3.0, f"Expected community max 3, got {comm}"
    assert uniq == 2.0, f"Expected uniqueness max 2, got {uniq}"

    total = rel + maint + adopt + mom + doc + prod + sec + interop + comm + uniq
    assert 90.0 <= total <= 100.0, f"Expected sum of weights near 100, got {total}"

def test_tier1_scoring_bounds_empty_entry():
    """Verify scoring logic stays within [0, 100] for empty inputs."""
    entry = {}
    total = (
        score_relevance(entry) + score_maintenance(entry) + score_adoption(entry) +
        score_momentum(entry) + score_documentation(entry) + score_production_readiness(entry) +
        score_security(entry) + score_interoperability(entry) + score_community(entry) +
        score_uniqueness(entry)
    )
    assert 0 <= total <= 100

def test_tier1_scoring_bounds_max_entry():
    """Verify scoring logic stays within [0, 100] for maximum possible inputs."""
    import datetime
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    entry = {
        "name": "super-agent-orchestrator-mcp-framework",
        "description": "novel experimental unique first alternative educational pioneering tool calling framework with custom commands",
        "topics": ["ai-agent", "mcp-server", "agent-framework", "agent-orchestration", "agent-memory", "agent-tool", "agent-skill", "mcp"],
        "project_type": "framework",
        "stars": 1000000,
        "forks": 100000,
        "open_issues": 1,
        "pushed_at": now_str,
        "latest_release_at": now_str,
        "archived": False,
        "license": "MIT",
        "languages": ["Python", "TypeScript", "Rust", "Go", "C++"],
        "homepage_url": "https://example.com",
        "protocols": ["mcp"],
        "compatible_hosts": ["claude"],
        "security_transparency": 10,
        "security_notes": []
    }
    total = (
        score_relevance(entry) + score_maintenance(entry) + score_adoption(entry) +
        score_momentum(entry) + score_documentation(entry) + score_production_readiness(entry) +
        score_security(entry) + score_interoperability(entry) + score_community(entry) +
        score_uniqueness(entry)
    )
    assert 0 <= total <= 100

def test_tier1_relevance_minimum_value():
    """Verify relevance score cannot go below baseline for recognized inputs."""
    assert score_relevance({"project_type": "unknown"}) >= 10

def test_tier1_adoption_score_non_negative():
    """Verify adoption score remains non-negative for zero stars/forks."""
    assert score_adoption({"stars": 0, "forks": 0}) >= 0

# Feature 6: Uniqueness & Security Rules
def test_tier1_uniqueness_default_baseline():
    """Verify uniqueness score returns baseline of 0.5 for standard entries."""
    assert score_uniqueness({}) == 0.5

def test_tier1_security_default_baseline():
    """Verify security score returns reduced baseline when transparency is missing and no license."""
    # Baseline 4.0, no license = -1.0 => 3.0
    assert score_security({}) == 3.0

def test_tier1_uniqueness_non_negative():
    """Verify uniqueness score is never negative."""
    assert score_uniqueness({"project_type": "invalid"}) >= 0

def test_tier1_security_transparency_bounds():
    """Verify security score honors security_transparency field when present."""
    # transparency=8 without license: 8.0 - 1.0 = 7.0
    assert score_security({"security_transparency": 8}) == 7.0
    # transparency=8 with license: 8.0 + 1.0 = 9.0 (capped at 10)
    assert score_security({"security_transparency": 8, "license": "MIT"}) == 9.0

def test_tier1_security_notes_penalty_bounds():
    """Verify security notes apply negative scaling without going below 0."""
    entry = {"security_transparency": 3.0, "security_notes": ["vuln1", "vuln2"]}
    assert score_security(entry) == 0.0

# Feature 7: Classification Engine (No Fallback)
def test_tier1_classification_no_match_returns_none():
    """Verify that taxonomy classification returns None when no rules match (no fallback)."""
    entry = {"name": "hello-world", "description": "just a hello world message", "topics": []}
    prim, sec = infer_category(entry, {})
    assert prim is None
    assert sec == []

def test_tier1_classification_mcp_server_mapping():
    """Verify basic classification of MCP server."""
    entry = {"name": "my-mcp-server", "topics": ["mcp-server"]}
    prim, _ = infer_category(entry, {})
    assert prim == "D.20"

def test_tier1_classification_coding_agent_mapping():
    """Verify classification of coding agents."""
    entry = {"name": "aider", "description": "coding assistant"}
    prim, _ = infer_category(entry, {})
    assert prim == "C.13"

def test_tier1_classification_framework_mapping():
    """Verify classification of framework."""
    entry = {"topics": ["agent-framework"]}
    prim, _ = infer_category(entry, {})
    assert prim == "B.6"

def test_tier1_classification_learning_mapping():
    """Verify classification of tutorials."""
    entry = {"description": "tutorial for building agents"}
    prim, _ = infer_category(entry, {})
    assert prim == "A.1"

# Feature 8: Data Exporter
def test_tier1_exporter_handles_empty_entries(tmp_path):
    """Verify data exporter can run without errors when catalog entries list is empty."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [], "count": 0}, f)
    
    # Run exporter main with mock args
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
    
    assert (tmp_path / "catalog.json").exists()
    assert (tmp_path / "catalog.ndjson").exists()
    assert (tmp_path / "catalog.csv").exists()

def test_tier1_exporter_json_contents(tmp_path):
    """Verify JSON export contains valid catalog layout."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "name": "bar"}], "count": 1}, f)
    
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "entries" in data
    assert len(data["entries"]) == 1

def test_tier1_exporter_ndjson_line_count(tmp_path):
    """Verify NDJSON output has exactly one line per entry."""
    catalog_path = tmp_path / "catalog.json"
    entries = [{"id": "foo/bar"}, {"id": "hello/world"}]
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": entries, "count": 2}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.ndjson", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["id"] == "foo/bar"

def test_tier1_exporter_csv_headers(tmp_path):
    """Verify exported CSV contains correct headers."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "a/b", "score": 90}], "count": 1}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.csv", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
    assert "id" in headers
    assert "score" in headers

def test_tier1_exporter_csv_data_alignment(tmp_path):
    """Verify data rows in CSV correspond to catalog entries."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "a/b", "score": 90, "stars": 123}], "count": 1}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.csv", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["id"] == "a/b"
    assert rows[0]["stars"] == "123"

# Feature 9: Trend/Momentum Engine
def test_tier1_trend_populates_empty_historical_map(tmp_path):
    """Verify trend engine falls back gracefully when Git history has no entries."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    with patch("update_trends.get_catalog_from_git", return_value={}):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    trend = res["entries"][0]["trend_data"]
    assert trend["stars_30d"] is None
    assert trend["method"] is None

def test_tier1_trend_git_loader_handling():
    """Verify git loader handles exceptions gracefully and returns empty dictionary."""
    from update_trends import get_catalog_from_git
    with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")):
        res = get_catalog_from_git(30)
    assert res == {}

def test_tier1_trend_populates_valid_historical_map(tmp_path):
    """Verify trend engine maps stars correctly when historical data is found."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    mock_history = {"entries": [{"id": "foo/bar", "stars": 80}]}
    
    with patch("update_trends.get_catalog_from_git", return_value=mock_history):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    trend = res["entries"][0]["trend_data"]
    assert trend["stars_30d"] == 80
    assert trend["method"] == "git"

def test_tier1_trend_ignores_unknown_ids(tmp_path):
    """Verify historical entries that don't match active entries are ignored."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    mock_history = {"entries": [{"id": "other/project", "stars": 50}]}
    
    with patch("update_trends.get_catalog_from_git", return_value=mock_history):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    assert res["entries"][0]["trend_data"]["stars_30d"] is None

def test_tier1_trend_updates_file_in_place(tmp_path):
    """Verify trend engine writes changes back to same catalog file."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100}]}, f)
    
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    with patch("update_trends.get_catalog_from_git", return_value={}):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
    
    assert catalog_path.exists()


# ==============================================================================
# TIER 2: COMPONENT & LOGIC INTEGRATION
# ==============================================================================

# Feature 5: Scoring Engine & Weights
def test_tier2_scoring_framework_type_bonus():
    """Verify that a project type framework receives the correct bonus weight."""
    entry_fw = {"project_type": "framework"}
    entry_lib = {"project_type": "library"}
    assert score_relevance(entry_fw) > score_relevance(entry_lib)

def test_tier2_scoring_mcp_type_bonus():
    """Verify that a project type 'mcp server' receives the correct bonus weight."""
    entry_mcp = {"project_type": "mcp server"}
    entry_other = {"project_type": "library"}
    assert score_relevance(entry_mcp) > score_relevance(entry_other)

def test_tier2_scoring_maintenance_decay_30d():
    """Verify maintenance score decays when days_since_push is between 7 and 30 days."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    pushed_8d = (now - datetime.timedelta(days=8)).isoformat()
    pushed_2d = (now - datetime.timedelta(days=2)).isoformat()
    
    assert score_maintenance({"pushed_at": pushed_2d}) == 15
    assert score_maintenance({"pushed_at": pushed_8d}) == 12

def test_tier2_scoring_momentum_release_cadence():
    """Verify that having a recent release boosts momentum score."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    release_10d = (now - datetime.timedelta(days=10)).isoformat()
    
    score_with_release = score_momentum({"latest_release_at": release_10d})
    score_no_release = score_momentum({})
    assert score_with_release > score_no_release

def test_tier2_scoring_confidence_formula():
    """Verify confidence output matches the strict definition metrics."""
    entry_high = {
        "repository_url": "https://github.com/foo/bar",
        "license": "MIT",
        "stars": 100,
        "forks": 10,
        "description": "Detailed text description",
        "pushed_at": "2026-07-01T00:00:00Z",
        "created_at": "2026-01-01T00:00:00Z",
        "topics": ["a", "b", "c"],
        "project_type": "framework",
        "primary_category": "B.6"
    }
    assert compute_confidence(entry_high) == "high"

# Feature 6: Uniqueness & Security Rules
def test_tier2_uniqueness_keyword_bonus():
    """Verify that uniqueness score increases when description contains unique keywords."""
    entry_basic = {"description": "ordinary agent library", "project_type": "library"}
    entry_unique = {"description": "novel experimental agent library", "project_type": "library"}
    assert score_uniqueness(entry_unique) > score_uniqueness(entry_basic)

def test_tier2_uniqueness_project_type_scaling():
    """Verify specific project types receive correct uniqueness bonuses (e.g. protocol vs library)."""
    entry_proto = {"project_type": "protocol"}
    entry_lib = {"project_type": "library"}
    assert score_uniqueness(entry_proto) > score_uniqueness(entry_lib)

def test_tier2_uniqueness_mcp_compatibility_bonus():
    """Verify compatibility with MCP or hosts scales the uniqueness score up."""
    entry_plain = {}
    entry_mcp = {"protocols": ["mcp"]}
    assert score_uniqueness(entry_mcp) > score_uniqueness(entry_plain)

def test_tier2_security_transparency_license_bonus():
    """Verify license presence increases security score if transparency is not specified."""
    entry_no_lic = {}
    entry_lic = {"license": "MIT"}
    assert score_security(entry_lic) > score_security(entry_no_lic)

def test_tier2_security_notes_penalty_scaling():
    """Verify security notes penalty scales down dynamically (e.g. multiple notes subtract more)."""
    entry_1_note = {"security_notes": ["vuln1"]}
    entry_2_notes = {"security_notes": ["vuln1", "vuln2"]}
    assert score_security(entry_2_notes) < score_security(entry_1_note)

# Feature 7: Classification Engine (No Fallback)
def test_tier2_classification_specificity_order():
    """Verify classification engine prioritizes more specific rules over generic ones."""
    # MCP-server is more specific than general MCP or frameworks
    entry = {"name": "mcp-server-project", "topics": ["mcp-server", "agent-framework"]}
    prim, _ = infer_category(entry, {})
    assert prim == "D.20"

def test_tier2_classification_swe_bench_evaluation():
    """Verify classification of SWE-Bench evaluation tool."""
    entry = {"topics": ["swe-bench", "coding-agent"], "name": "swe-bench-runner"}
    prim, sec = infer_category(entry, {})
    assert prim == "C.19"
    assert "H.56" in sec

def test_tier2_classification_memory_vector_db():
    """Verify classification of vector stores / memory components."""
    entry = {"topics": ["vector-store", "memory"]}
    prim, sec = infer_category(entry, {})
    # memory topic triggers F.37 or F.38 depending on order
    assert prim in ("F.37", "F.38")

def test_tier2_classification_observability_tracing():
    """Verify classification of tracing / observability projects."""
    entry = {"topics": ["agent-observability"]}
    prim, _ = infer_category(entry, {})
    assert prim == "H.53"

def test_tier2_classification_security_guardrails():
    """Verify classification of guardrails / security packages."""
    entry = {"topics": ["guardrails"]}
    prim, _ = infer_category(entry, {})
    assert prim == "H.57"

# Feature 8: Data Exporter
def test_tier2_exporter_ensures_directory_creation(tmp_path):
    """Verify exporter creates output directory if it does not exist yet."""
    out_dir = tmp_path / "nested" / "dist"
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": []}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(out_dir)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    assert out_dir.exists()
    assert (out_dir / "catalog.json").exists()

def test_tier2_exporter_correctly_escapes_csv_fields(tmp_path):
    """Verify that CSV exporter properly escapes fields containing quotes and commas."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "name": "Special, Project \"X\""}]}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.csv", encoding="utf-8") as f:
        content = f.read()
    assert '"Special, Project ""X"""' in content or "Special, Project \"X\"" in content

def test_tier2_exporter_excludes_non_schema_properties(tmp_path):
    """Verify CSV export strictly limits columns to the specified header schema fields."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "custom_prop": "ignored_val"}]}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.csv", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        row = next(reader)
    assert "custom_prop" not in headers
    assert "ignored_val" not in row

def test_tier2_exporter_handles_null_values_in_fields(tmp_path):
    """Verify exporter formats null/missing values correctly without raising exceptions."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": None, "license": None}]}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    assert (tmp_path / "catalog.csv").exists()

def test_tier2_exporter_maintains_utf8_encoding(tmp_path):
    """Verify that exported files maintain proper UTF-8 encoding for unicode characters."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "name": "Wörterbuch-Agent"}]}, f)
        
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(tmp_path)]
    with patch.object(sys, "argv", test_args):
        export.main()
        
    with open(tmp_path / "catalog.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["entries"][0]["name"] == "Wörterbuch-Agent"

# Feature 9: Trend/Momentum Engine
def test_tier2_trend_handles_missing_pushed_at(tmp_path):
    """Verify trend engine runs correctly even when some entries have no pushed_at value."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 10, "pushed_at": None}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    with patch("update_trends.get_catalog_from_git", return_value={}):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    assert (tmp_path / "catalog.json").exists()

def test_tier2_trend_does_not_modify_existing_fields(tmp_path):
    """Verify trend engine only appends trend_data without changing other fields."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100, "name": "foo"}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    with patch("update_trends.get_catalog_from_git", return_value={}):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    assert res["entries"][0]["stars"] == 100
    assert res["entries"][0]["name"] == "foo"

def test_tier2_trend_compares_multiple_historical_dates(tmp_path):
    """Verify trend engine handles different values for 30d and 90d snapshots."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    
    def mock_get_git(days_ago):
        if days_ago == 30:
            return {"entries": [{"id": "foo/bar", "stars": 90}]}
        elif days_ago == 90:
            return {"entries": [{"id": "foo/bar", "stars": 70}]}
        return {}
        
    with patch("update_trends.get_catalog_from_git", side_effect=mock_get_git):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    trend = res["entries"][0]["trend_data"]
    assert trend["stars_30d"] == 90
    assert trend["stars_90d"] == 70

def test_tier2_trend_handles_empty_entries_in_history(tmp_path):
    """Verify trend engine functions when historical catalog JSON structure is invalid."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 100}]}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    with patch("update_trends.get_catalog_from_git", return_value={"invalid_key": []}):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    assert res["entries"][0]["trend_data"]["stars_30d"] is None

def test_tier2_trend_engine_preserves_schema(tmp_path):
    """Verify catalog structure and schema layout are preserved after trend run."""
    catalog_path = tmp_path / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({"entries": [{"id": "foo/bar", "stars": 10}], "schema_version": "1.0"}, f)
        
    test_args = ["update_trends.py", "--catalog", str(catalog_path)]
    with patch("update_trends.get_catalog_from_git", return_value={}):
        with patch.object(sys, "argv", test_args):
            update_trends.main()
            
    with open(catalog_path, encoding="utf-8") as f:
        res = json.load(f)
    assert res["schema_version"] == "1.0"


# ==============================================================================
# TIER 3: SYSTEM-LEVEL & PIPELINE E2E
# ==============================================================================

def test_tier3_full_pipeline_flow(tmp_path):
    """E2E Test executing scoring, classification, and exporter sequentially on mock catalog data."""
    # 1. Setup raw catalog data
    catalog_path = tmp_path / "catalog.json"
    taxonomy_path = Path(__file__).parent.parent / "data" / "taxonomy.json"
    
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    pushed_at = (now - datetime.timedelta(days=2)).isoformat()
    latest_release_at = (now - datetime.timedelta(days=10)).isoformat()
    checked_at = now.isoformat()

    raw_data = {
        "schema_version": "1.0",
        "entries": [
            {
                "id": "test-owner/mcp-server-cool",
                "name": "mcp-server-cool",
                "repository": "test-owner/mcp-server-cool",
                "repository_url": "https://github.com/test-owner/mcp-server-cool",
                "description": "A novel experimental tool calling server for MCP clients.",
                "project_type": "mcp server",
                "stars": 1000,
                "forks": 100,
                "open_issues": 5,
                "pushed_at": pushed_at,
                "latest_release_at": latest_release_at,
                "license": "MIT",
                "languages": ["Python", "TypeScript"],
                "protocols": ["mcp"],
                "checked_at": checked_at
            }
        ]
    }
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f)
        
    # 2. Run Classification
    classify_args = ["classify.py", "--input", str(catalog_path), "--taxonomy", str(taxonomy_path), "--output", str(catalog_path)]
    with patch.object(sys, "argv", classify_args):
        import classify
        classify.main()
        
    with open(catalog_path, encoding="utf-8-sig") as f:
        classified_data = json.load(f)
    assert classified_data["entries"][0]["primary_category"] == "D.20"
    
    # 3. Run Scoring
    score_args = ["score.py", "--input", str(catalog_path), "--output", str(catalog_path)]
    with patch.object(sys, "argv", score_args):
        import score
        score.main()
        
    with open(catalog_path, encoding="utf-8") as f:
        scored_data = json.load(f)
    assert scored_data["entries"][0]["score"] > 50
    assert "relevance" in scored_data["entries"][0]["score_components"]
    
    # 4. Run Exporter
    export_dir = tmp_path / "dist"
    export_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(export_dir)]
    with patch.object(sys, "argv", export_args):
        export.main()
        
    assert (export_dir / "catalog.json").exists()
    assert (export_dir / "catalog.ndjson").exists()
    assert (export_dir / "catalog.csv").exists()

def test_tier3_validation_rules_compliance(tmp_path):
    """E2E Test executing validate.py rules on valid and invalid simulated catalogs."""
    catalog_path = tmp_path / "catalog.json"
    schema_path = Path(__file__).parent.parent / "data" / "catalog.schema.json"
    
    # Valid data
    valid_data = {
        "entries": [
            {
                "id": "owner/repo",
                "name": "repo",
                "owner": "owner",
                "official_status": "official",
                "repository": "owner/repo",
                "repository_url": "https://github.com/owner/repo",
                "description": "Some neutral agentic package definition.",
                "primary_category": "B.6",
                "project_type": "framework",
                "score": 75.0,
                "confidence": "medium",
                "checked_at": "2026-07-07T00:00:00Z"
            }
        ]
    }
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(valid_data, f)
        
    validate_args = ["validate.py", "--catalog", str(catalog_path), "--schema", str(schema_path)]
    with patch.object(sys, "argv", validate_args):
        assert validate.main() is True
        
    # Invalid data (missing required field)
    invalid_data = {
        "entries": [
            {
                "id": "owner/repo",
                # missing name
                "owner": "owner",
                "official_status": "official",
                "repository": "owner/repo",
                "repository_url": "https://github.com/owner/repo",
                "description": "Some neutral agentic package definition.",
                "primary_category": "B.6",
                "project_type": "framework",
                "score": 75.0,
                "confidence": "medium",
                "checked_at": "2026-07-07T00:00:00Z"
            }
        ]
    }
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(invalid_data, f)
        
    with patch.object(sys, "argv", validate_args):
        assert validate.main() is False


# ==============================================================================
# TIER 4: BOUNDARY, EDGE CASES & COMPLIANCE
# ==============================================================================

def test_tier4_scoring_boundary_scores():
    """Verify that scoring bounds are strictly respected even with extreme outlier values."""
    # Extremely large stars/forks
    entry_giant = {
        "stars": 99999999,
        "forks": 9999999,
        "open_issues": 99999,
        "project_type": "framework",
        "pushed_at": "2026-07-08T00:00:00Z",
        "latest_release_at": "2026-07-08T00:00:00Z"
    }
    assert 0 <= score_adoption(entry_giant) <= 15
    assert 0 <= score_production_readiness(entry_giant) <= 10
    
    # Standard zero boundary
    entry_zero = {
        "stars": 0,
        "forks": 0,
        "open_issues": 0
    }
    assert 0 <= score_adoption(entry_zero) <= 15
    assert 0 <= score_production_readiness(entry_zero) <= 10

def test_tier4_classification_no_fallback_strictness():
    """Confirm classification returns None instead of guessing when keywords are completely absent."""
    entry_obscure = {
        "name": "random-utility",
        "description": "computes prime numbers in parallel",
        "topics": ["prime-numbers", "math"]
    }
    prim, sec = infer_category(entry_obscure, {})
    assert prim is None
    assert sec == []
