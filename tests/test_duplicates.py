"""Test duplicate detection."""

import json
from pathlib import Path


def test_no_duplicate_repos():
    """Test that no duplicate repository URLs exist in the catalog."""
    path = Path(__file__).parent.parent / "data" / "catalog.json"
    if not path.exists():
        return
    
    with open(path) as f:
        data = json.load(f)
    
    entries = data.get("entries", data if isinstance(data, list) else [])
    repos = [e.get("repository", "") for e in entries if e.get("repository")]
    duplicates = {r for r in repos if repos.count(r) > 1}
    
    assert not duplicates, f"Duplicate repositories found: {duplicates}"


def test_no_duplicate_ids():
    """Test that no duplicate IDs exist."""
    path = Path(__file__).parent.parent / "data" / "catalog.json"
    if not path.exists():
        return
    
    with open(path) as f:
        data = json.load(f)
    
    entries = data.get("entries", data if isinstance(data, list) else [])
    ids = [e.get("id", "") for e in entries if e.get("id")]
    duplicates = {i for i in ids if ids.count(i) > 1}
    
    assert not duplicates, f"Duplicate IDs found: {duplicates}"
