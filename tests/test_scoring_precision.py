"""
tests/test_scoring_precision.py

Regression tests for the WERKAtlas scoring system.

Verifies:
  1. Each dimension stays within its documented maximum.
  2. The total score never exceeds 100.0.
  3. score_label is correctly assigned based on thresholds.
  4. score_explanations is a list of dicts with required keys.
  5. Known projects are classified within expected score ranges.
"""
import json
import sys
from pathlib import Path

import pytest

# Make scripts importable without installing as a package
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from score import (
    score_relevance,
    score_maintenance,
    score_adoption,
    score_momentum,
    score_documentation,
    score_production_readiness,
    score_security,
    score_interoperability,
    score_community,
    score_uniqueness,
    compute_score_label,
    compute_confidence,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CATALOG_PATH = Path(__file__).parent.parent / "data" / "catalog.json"

MAXIMA = {
    "relevance": 20.0,
    "maintenance": 15.0,
    "adoption": 15.0,
    "momentum": 10.0,
    "documentation": 10.0,
    "production_readiness": 10.0,
    "security": 10.0,
    "interoperability": 5.0,
    "community": 3.0,
    "uniqueness": 2.0,
}

SCORERS = {
    "relevance":            score_relevance,
    "maintenance":          score_maintenance,
    "adoption":             score_adoption,
    "momentum":             score_momentum,
    "documentation":        score_documentation,
    "production_readiness": score_production_readiness,
    "security":             score_security,
    "interoperability":     score_interoperability,
    "community":            score_community,
    "uniqueness":           score_uniqueness,
}


def _max_entry() -> dict:
    """Synthetic entry with values that should produce maximum possible scores."""
    return {
        "id": "test/max-entry",
        "name": "max-entry-ai-agent-framework-mcp",
        "owner": "test",
        "repository": "test/max-entry",
        "repository_url": "https://github.com/test/max-entry",
        "description": "An ai-agent agent-framework mcp coding-agent multi-agent novel first pioneering educational reference experimental alternative that demonstrates uniqueness.",
        "primary_category": "B.6",
        "project_type": "framework",
        "official_status": "official",
        "score": 0,
        "confidence": "high",
        "checked_at": "2026-07-07T00:00:00Z",
        "topics": ["ai-agent", "agent-framework", "mcp", "multi-agent", "agent-swarm", "coding-agent", "browser-agent"],
        "stars": 100_000,
        "forks": 20_000,
        "open_issues": 0,
        "pushed_at": "2026-07-07T00:00:00Z",
        "latest_release_at": "2026-07-01T00:00:00Z",
        "homepage_url": "https://example.com",
        "license": "MIT",
        "protocols": ["mcp", "a2a", "openapi"],
        "compatible_hosts": ["claude", "cursor", "vscode"],
        "languages": ["Python", "TypeScript", "Go", "Rust", "Java", "C#"],
        "security_transparency": 9,
        "security_notes": [],
        "archived": False,
    }


def _min_entry() -> dict:
    """Synthetic entry with minimal/missing values."""
    return {
        "id": "test/min-entry",
        "name": "unknown-tool",
        "owner": "test",
        "repository": "test/min-entry",
        "repository_url": "https://github.com/test/min-entry",
        "description": "A small utility.",
        "primary_category": None,
        "project_type": "library",
        "official_status": "unclear",
        "score": 0,
        "confidence": "low",
        "checked_at": "2026-07-07T00:00:00Z",
        "topics": [],
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "pushed_at": None,
        "latest_release_at": None,
        "homepage_url": None,
        "license": None,
        "protocols": [],
        "compatible_hosts": [],
        "languages": [],
        "security_transparency": None,
        "security_notes": [],
        "archived": False,
    }


# ---------------------------------------------------------------------------
# Dimension max/min tests
# ---------------------------------------------------------------------------

class TestDimensionBounds:
    def test_all_dimensions_within_max_on_max_entry(self):
        entry = _max_entry()
        for dim, fn in SCORERS.items():
            val, _ = fn(entry)
            assert val <= MAXIMA[dim] + 0.001, (
                f"{dim}: returned {val} > max {MAXIMA[dim]}"
            )

    def test_all_dimensions_non_negative_on_min_entry(self):
        entry = _min_entry()
        for dim, fn in SCORERS.items():
            val, _ = fn(entry)
            assert val >= 0.0, f"{dim}: returned negative value {val}"

    def test_total_never_exceeds_100(self):
        entry = _max_entry()
        total = sum(fn(entry)[0] for fn in SCORERS.values())
        assert total <= 100.0, f"Total score {total} exceeds 100"

    def test_total_on_min_entry_is_non_negative(self):
        entry = _min_entry()
        total = sum(fn(entry)[0] for fn in SCORERS.values())
        assert total >= 0.0

    def test_archived_maintenance_is_zero(self):
        entry = _max_entry()
        entry["archived"] = True
        val, _ = score_maintenance(entry)
        assert val == 0.0

    def test_archived_production_readiness_is_reduced(self):
        entry = _max_entry()
        entry["archived"] = True
        normal, _ = score_production_readiness(_max_entry())
        archived, _ = score_production_readiness(entry)
        assert archived < normal


# ---------------------------------------------------------------------------
# Explanations structure
# ---------------------------------------------------------------------------

class TestScoreExplanations:
    def test_explanations_are_lists(self):
        entry = _max_entry()
        for dim, fn in SCORERS.items():
            _, exps = fn(entry)
            assert isinstance(exps, list), f"{dim}: explanations not a list"

    def test_explanations_have_required_keys(self):
        entry = _max_entry()
        for dim, fn in SCORERS.items():
            _, exps = fn(entry)
            for exp in exps:
                assert "dimension" in exp, f"{dim}: explanation missing 'dimension'"
                assert "impact" in exp, f"{dim}: explanation missing 'impact'"
                assert "text" in exp, f"{dim}: explanation missing 'text'"
                assert exp["impact"] in {"positive", "negative", "neutral"}, (
                    f"{dim}: invalid impact value '{exp['impact']}'"
                )


# ---------------------------------------------------------------------------
# Score labels
# ---------------------------------------------------------------------------

class TestScoreLabels:
    @pytest.mark.parametrize("score,expected", [
        (100.0, "essential"),
        (85.0, "essential"),
        (84.9, "strong"),
        (75.0, "strong"),
        (74.9, "emerging"),
        (65.0, "emerging"),
        (64.9, "watchlist"),
        (50.0, "watchlist"),
        (49.9, "minimal"),
        (0.0,  "minimal"),
    ])
    def test_label_thresholds(self, score, expected):
        assert compute_score_label(score) == expected


# ---------------------------------------------------------------------------
# Full-catalog regression: all existing entries stay within bounds
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not CATALOG_PATH.exists(), reason="catalog.json not found")
class TestCatalogRegression:
    @pytest.fixture(scope="class")
    def entries(self):
        with open(CATALOG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("entries", [])

    def test_all_dimensions_within_max(self, entries):
        errors = []
        for entry in entries:
            for dim, fn in SCORERS.items():
                val, _ = fn(entry)
                if val > MAXIMA[dim] + 0.01:
                    errors.append(f"{entry.get('id')}: {dim}={val} > {MAXIMA[dim]}")
        assert not errors, f"Dimension overflows:\n" + "\n".join(errors[:20])

    def test_no_total_exceeds_100(self, entries):
        errors = []
        for entry in entries:
            total = round(sum(fn(entry)[0] for fn in SCORERS.values()), 2)
            if total > 100.0:
                errors.append(f"{entry.get('id')}: total={total}")
        assert not errors, f"Score overflows:\n" + "\n".join(errors[:10])


# ---------------------------------------------------------------------------
# Known classification-sensitive entries (score-range sanity check)
# ---------------------------------------------------------------------------

KNOWN_ENTRIES = {
    # High-profile, well-maintained frameworks → should score highly
    "microsoft/semantic-kernel": {"min": 60, "max": 100},
    "langchain-ai/langgraph":    {"min": 60, "max": 100},
    # Vector databases → should NOT be in top agent-framework tier
    # (we can only check score range, not category, here)
    "qdrant/qdrant":             {"min": 40, "max": 100},
    "weaviate/weaviate":         {"min": 40, "max": 100},
}


@pytest.mark.skipif(not CATALOG_PATH.exists(), reason="catalog.json not found")
class TestKnownEntryScoreRanges:
    @pytest.fixture(scope="class")
    def entry_map(self):
        with open(CATALOG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return {e["repository"]: e for e in data.get("entries", [])}

    @pytest.mark.parametrize("repo,bounds", KNOWN_ENTRIES.items())
    def test_score_within_bounds(self, entry_map, repo, bounds):
        if repo not in entry_map:
            pytest.skip(f"{repo} not in catalog")
        entry = entry_map[repo]
        total = round(sum(fn(entry)[0] for fn in SCORERS.values()), 1)
        assert bounds["min"] <= total <= bounds["max"], (
            f"{repo}: score {total} outside expected range [{bounds['min']}, {bounds['max']}]"
        )
