"""Metadata review prioritization must never fabricate facts or modify catalog."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from metadata_backlog import build_backlog  # noqa: E402

NOW = datetime(2026, 10, 31, tzinfo=timezone.utc)


def entry(id="demo/a", *, score=75, license=None, checked_at="2026-07-07T00:00:00Z",
          maintenance_status="unclear", stars=100, pushed_at=None, official_evidence=None):
    return {
        "id": id, "repository_url": "https://github.com/" + id,
        "score": score, "stars": stars, "license": license, "checked_at": checked_at,
        "maintenance_status": maintenance_status, "pushed_at": pushed_at,
        "official_evidence": official_evidence or [],
    }


def test_missing_facts_are_reported_not_invented():
    sample = {"entries": [entry()]}
    original = json.dumps(sample, sort_keys=True)
    result = build_backlog(sample, as_of=NOW, limit=1)
    assert result["counts"]["license_missing"] == 1
    assert result["counts"]["checked_at_stale_or_unknown"] == 1
    assert "license" in result["selected"][0]["missing_or_stale"]
    assert "license" not in result["selected"][0]
    assert json.dumps(sample, sort_keys=True) == original


def test_deterministic_sorting_and_limit():
    sample = {"entries": [
        entry("demo/b", score=40, stars=1000),
        entry("demo/a", score=90, stars=10),
        entry("demo/c", score=90, stars=1),
    ]}
    result = build_backlog(sample, as_of=NOW, limit=2)
    assert [row["id"] for row in result["selected"]] == ["demo/a", "demo/c"]


def test_unknown_future_or_invalid_check_date_not_fresh():
    sample = {"entries": [
        entry("demo/invalid", checked_at="not-a-date"),
        entry("demo/future", checked_at="2099-01-01T00:00:00Z"),
    ]}
    result = build_backlog(sample, as_of=NOW)
    assert result["counts"]["checked_at_stale_or_unknown"] == 2


def test_real_catalog_read_only_and_complete():
    catalog_path = ROOT / "data" / "catalog.json"
    before = catalog_path.read_bytes()
    catalog = json.loads(before)
    result = build_backlog(catalog, as_of=NOW, limit=50)
    assert result["counts"]["total"] == len(catalog["entries"])
    assert 0 <= result["counts"]["license_missing"] <= result["counts"]["total"]
    assert all(row["repository_url"].startswith("https://github.com/") for row in result["selected"])
    assert hashlib.sha256(catalog_path.read_bytes()).digest() == hashlib.sha256(before).digest()
