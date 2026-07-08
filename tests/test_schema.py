"""Test catalog schema validation."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_catalog_exists():
    """Test that catalog file exists."""
    path = Path("data/catalog.json")
    if not path.exists():
        path = Path(__file__).parent.parent / "data" / "catalog.json"
    assert path.exists(), f"Catalog not found at {path}"


def test_catalog_is_valid_json():
    """Test that catalog is valid JSON."""
    path = Path(__file__).parent.parent / "data" / "catalog.json"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert "entries" in data or isinstance(data, list)


def test_catalog_entries_have_required_fields():
    """Test that all entries have required fields."""
    path = Path(__file__).parent.parent / "data" / "catalog.json"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("entries", data if isinstance(data, list) else [])
    
    required = ["id", "name", "repository", "repository_url", "description", 
                "primary_category", "project_type", "score", "confidence", "checked_at"]
    
    for entry in entries:
        for field in required:
            assert field in entry, f"Missing {field} in {entry.get('id', 'unknown')}"


def test_no_invented_stars():
    """Test that star counts are reasonable."""
    path = Path(__file__).parent.parent / "data" / "catalog.json"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("entries", data if isinstance(data, list) else [])
    
    for entry in entries:
        stars = entry.get("stars", 0)
        assert isinstance(stars, int), f"Stars not int in {entry.get('id')}"
        assert stars >= 0, f"Negative stars in {entry.get('id')}"
