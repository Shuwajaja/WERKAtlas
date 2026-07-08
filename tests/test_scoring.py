"""Test scoring system — updated for tuple-returning API (score, explanations)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_log_stars_ranges():
    """Test log_stars produces correct ranges."""
    from score import log_stars

    assert log_stars(0) == 0.0
    assert 0 < log_stars(100) <= 10
    assert 0 < log_stars(1000) <= 10
    assert 0 < log_stars(100000) <= 10


def test_log_stars_logarithmic():
    """Test log_stars is logarithmic (diminishing returns)."""
    from score import log_stars

    diff_small = log_stars(100) - log_stars(0)
    diff_large = log_stars(10100) - log_stars(10000)
    assert diff_small > diff_large


def _s(fn, entry):
    """Call a scorer and return only the numeric value."""
    result = fn(entry)
    return result[0] if isinstance(result, tuple) else result


def test_entry_scores_in_range():
    """Test that all score components are within valid ranges."""
    from score import (
        score_relevance, score_maintenance, score_adoption,
        score_momentum, score_documentation, score_production_readiness,
        score_security, score_interoperability, score_community, score_uniqueness,
    )

    entry = {
        "name": "test",
        "description": "A test project for agent engineering",
        "topics": ["ai-agent", "agent-framework"],
        "project_type": "framework",
        "stars": 1000,
        "forks": 100,
        "open_issues": 10,
        "pushed_at": "2026-07-01T00:00:00Z",
        "updated_at": "2026-07-01T00:00:00Z",
        "created_at": "2025-01-01T00:00:00Z",
        "latest_release_at": "2026-06-01T00:00:00Z",
        "archived": False,
        "license": "MIT",
        "languages": ["Python", "TypeScript", "Rust"],
        "homepage_url": "https://example.com",
        "protocols": ["mcp"],
        "compatible_hosts": ["claude"],
        "deployment_modes": ["self-hosted"],
        "security_notes": [],
    }

    assert 0 <= _s(score_relevance, entry) <= 20
    assert 0 <= _s(score_maintenance, entry) <= 15
    assert 0 <= _s(score_adoption, entry) <= 15
    assert 0 <= _s(score_momentum, entry) <= 10
    assert 0 <= _s(score_documentation, entry) <= 10
    assert 0 <= _s(score_production_readiness, entry) <= 10
    assert 0 <= _s(score_security, entry) <= 10
    assert 0 <= _s(score_interoperability, entry) <= 5
    assert 0 <= _s(score_community, entry) <= 3
    assert 0 <= _s(score_uniqueness, entry) <= 2


def test_total_score_range():
    """Test total score is in [0, 100]."""
    from score import (
        score_relevance, score_maintenance, score_adoption,
        score_momentum, score_documentation, score_production_readiness,
        score_security, score_interoperability, score_community, score_uniqueness,
    )

    entry = {
        "name": "test", "description": "test", "topics": [], "stars": 500,
        "forks": 50, "open_issues": 5, "pushed_at": None, "updated_at": None,
        "created_at": None, "latest_release_at": None, "archived": False,
        "license": None, "languages": [], "homepage_url": None, "protocols": [],
        "compatible_hosts": [], "deployment_modes": [], "security_notes": [],
        "project_type": "library",
    }

    scorers = [
        score_relevance, score_maintenance, score_adoption,
        score_momentum, score_documentation, score_production_readiness,
        score_security, score_interoperability, score_community, score_uniqueness,
    ]
    total = sum(_s(fn, entry) for fn in scorers)
    assert 0 <= total <= 100


def test_archived_penalty():
    """Test that archived repos score 0 on maintenance."""
    from score import score_maintenance

    archived = {"archived": True}
    active = {"archived": False, "pushed_at": "2026-07-01T00:00:00Z"}

    assert _s(score_maintenance, archived) == 0
    assert _s(score_maintenance, active) > 0
