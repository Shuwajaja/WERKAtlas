"""Catalog reconciliation against the 110 verified Instagram GitHub identities."""

import json
from pathlib import Path

from scripts.apply_instagram_reconciliation import (
    DISCOVERY_TAG,
    MUTABLE_FIELDS,
    protected_hash,
)
from scripts.validate import validate_schema

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "instagram-github-2026-10-28"


def _load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_every_verified_repo_is_added_excluded_or_already_present():
    metadata = _load(RESEARCH / "github-metadata.json")
    additions = {item["id"] for item in _load(RESEARCH / "additions.json")}
    exclusions = set(_load(RESEARCH / "exclusions.json"))
    baseline_ids = {entry_id.lower() for entry_id in _load(RESEARCH / "baseline-protected-sha256.json")["ids"]}
    assert len(metadata) == 110
    assert additions.isdisjoint(exclusions)
    for repo_id in metadata:
        assert repo_id in additions or repo_id in exclusions or repo_id.lower() in baseline_ids
    for repo_id in additions | exclusions:
        assert repo_id.lower() not in baseline_ids


def test_original_entries_keep_protected_fields():
    catalog = _load(ROOT / "data" / "catalog.json")
    baseline = _load(RESEARCH / "baseline-protected-sha256.json")
    by_id = {entry["id"]: entry for entry in catalog["entries"]}
    assert baseline["mutable_fields"] == list(MUTABLE_FIELDS)
    assert len(baseline["ids"]) == 1468
    for entry_id in baseline["ids"]:
        assert entry_id in by_id, entry_id
        assert protected_hash(by_id[entry_id]) == baseline["hashes"][entry_id]


def test_new_entries_match_github_metadata_and_schema():
    catalog = _load(ROOT / "data" / "catalog.json")
    schema = _load(ROOT / "data" / "catalog.schema.json")
    metadata = _load(RESEARCH / "github-metadata.json")
    additions = _load(RESEARCH / "additions.json")
    by_id = {entry["id"]: entry for entry in catalog["entries"]}
    assert catalog["count"] == len(catalog["entries"]) == 1468 + len(additions)
    for spec in additions:
        entry = by_id[spec["id"]]
        meta = metadata[spec["id"]]
        assert entry["description"] == spec["description"]
        assert 12 <= len(entry["description"].split()) <= 30
        assert entry["stars"] == meta["stargazerCount"]
        assert entry["forks"] == meta["forkCount"]
        assert entry["archived"] is meta["isArchived"]
        assert entry["repository_url"] == f"https://github.com/{spec['id']}"
        assert DISCOVERY_TAG in entry["discovered_from"]
        assert entry["source_urls"]
        if spec["official_status"] == "official":
            assert entry["official_evidence"]
        assert validate_schema(entry, schema) == []


def test_archived_repositories_and_license_fills():
    catalog = _load(ROOT / "data" / "catalog.json")
    metadata = _load(RESEARCH / "github-metadata.json")
    by_id = {entry["id"]: entry for entry in catalog["entries"]}
    for repo_id in (
        "FlowiseAI/Flowise",
        "gsd-build/get-shit-done",
        "google-gemini/deprecated-generative-ai-python",
    ):
        assert by_id[repo_id]["archived"] is True
        assert metadata[repo_id]["isArchived"] is True
    assert by_id["upstash/context7"]["license"] == "MIT"
    assert by_id["microsoft/markitdown"]["license"] == "MIT"
    assert any("service terms" in note for note in by_id["anthropics/skills"]["limitations"])


def test_excluded_repositories_stay_out_of_the_catalog():
    catalog = _load(ROOT / "data" / "catalog.json")
    exclusions = _load(RESEARCH / "exclusions.json")
    present = {entry["id"].lower() for entry in catalog["entries"]}
    leaked = sorted(repo_id for repo_id in exclusions if repo_id.lower() in present)
    assert leaked == []
