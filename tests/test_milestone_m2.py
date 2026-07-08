"""Tests for Milestone M2 pipeline enhancements."""

import sys
import json
import csv
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import score as _score_module
from classify import infer_category
from render import render_trending
import export

# Compatibility shim for tuple-returning API
def _wrap(fn):
    def _inner(*args, **kwargs):
        result = fn(*args, **kwargs)
        return result[0] if isinstance(result, tuple) else result
    return _inner

score_adoption   = _wrap(_score_module.score_adoption)
score_community  = _wrap(_score_module.score_community)
score_uniqueness = _wrap(_score_module.score_uniqueness)


def test_milestone_m2_scoring_weights():
    """Verify Adoption max is 15, Community max is 3, Uniqueness max is 2."""
    # Test Adoption upper bound
    assert score_adoption({"stars": 1000000, "forks": 100000}) == 15.0
    assert score_adoption({"stars": 0, "forks": 0}) == 0.0

    # Test Community upper bound
    assert score_community({"stars": 100000, "forks": 10000}) == 3.0
    assert score_community({"stars": 0, "forks": 0}) == 0.5

    # Test Uniqueness upper bound
    assert score_uniqueness({
        "project_type": "protocol",
        "description": "novel experimental unique first alternative pioneering"
    }) == 2.0
    assert score_uniqueness({}) == 0.5


def test_milestone_m2_trending_momentum_sorting():
    """Verify render_trending sorts entries correctly based on momentum."""
    catalog = {
        "entries": [
            {
                "repository": "slow-growth",
                "stars": 100,
                "trend_data": {"stars_30d": 95} # growth = 5, growth_rate = 5/95, momentum = 5 * (1 + 5/95) = ~5.26
            },
            {
                "repository": "fast-growth",
                "stars": 100,
                "trend_data": {"stars_30d": 50} # growth = 50, growth_rate = 50/50 = 1, momentum = 50 * (1 + 1) = 100
            },
            {
                "repository": "no-trend",
                "stars": 10,
                "trend_data": {"stars_30d": None} # momentum = 0
            }
        ]
    }
    
    result = render_trending(catalog, {}, "2026-07-08")
    
    # Fast growth should be sorted first (represented in Markdown table first)
    lines = result.split("\n")
    table_lines = [l for l in lines if "|" in l and not l.startswith("|---")]
    # Header line is the first one, then the table rows
    assert "fast-growth" in table_lines[1]
    assert "slow-growth" in table_lines[2]
    assert "no-trend" in table_lines[3]


def test_milestone_m2_strict_classification():
    """Verify that strict classification rules map correctly and non-matching returns None."""
    taxonomy = {}
    
    # Specific known edge cases
    assert infer_category({"repository": "openai/openai-python", "name": "openai-python"}, taxonomy)[0] == "E.35"
    assert infer_category({"repository": "weaviate/weaviate", "name": "weaviate", "topics": ["vector-database"]}, taxonomy)[0] == "F.38"
    assert infer_category({"repository": "dolthub/dolt", "name": "dolt"}, taxonomy)[0] == "F.43"
    assert infer_category({"repository": "fixie-ai/ultravox", "name": "ultravox"}, taxonomy)[0] == "G.52"

    # Non-matching returns None
    assert infer_category({"repository": "unknown/random-repo", "name": "random-repo", "description": "some text"}, taxonomy)[0] is None


def test_milestone_m2_exporter_generates_all_formats(tmp_path):
    """Verify that export.py creates JSON, NDJSON, and CSV formats correctly."""
    catalog_path = tmp_path / "catalog.json"
    catalog_data = {
        "entries": [
            {
                "id": "foo/bar",
                "name": "bar",
                "owner": "foo",
                "repository": "foo/bar",
                "repository_url": "https://github.com/foo/bar",
                "primary_category": "B.6",
                "project_type": "framework",
                "official_status": "community",
                "score": 85.0,
                "stars": 1000,
                "forks": 100,
                "open_issues": 10,
                "checked_at": "2026-07-08T00:00:00Z"
            }
        ],
        "count": 1
    }
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f)
        
    export_dir = tmp_path / "exports"
    test_args = ["export.py", "--input", str(catalog_path), "--output-dir", str(export_dir)]
    
    with patch.object(sys, "argv", test_args):
        export.main()
        
    # Check JSON
    with open(export_dir / "catalog.json", encoding="utf-8") as f:
        exported_json = json.load(f)
    assert len(exported_json["entries"]) == 1
    assert exported_json["entries"][0]["id"] == "foo/bar"
    
    # Check NDJSON
    with open(export_dir / "catalog.ndjson", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["id"] == "foo/bar"
    
    # Check CSV
    with open(export_dir / "catalog.csv", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["id"] == "foo/bar"
    assert rows[0]["score"] == "85.0"
