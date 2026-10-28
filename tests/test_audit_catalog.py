"""Read-only catalog audit. Hard errors fail the run; missing facts stay unknown."""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_catalog import audit_catalog  # noqa: E402

AS_OF = datetime(2026, 10, 28, tzinfo=timezone.utc)
SCHEMA = {
    "required": [
        "id",
        "name",
        "owner",
        "repository",
        "repository_url",
        "description",
        "primary_category",
        "project_type",
        "official_status",
        "score",
        "confidence",
        "checked_at",
    ],
    "properties": {"project_type": {"enum": ["library", "framework"]}},
}
TAXONOMY = {
    "categories": {
        "D": {"subcategories": {"D.20": {"name": "MCP servers"}}},
    }
}


def entry(**overrides):
    base = {
        "id": "acme/widget",
        "name": "Widget",
        "owner": "acme",
        "repository": "acme/widget",
        "repository_url": "https://github.com/acme/widget",
        "description": "one two three four five six seven eight nine ten eleven twelve",
        "primary_category": "D.20",
        "project_type": "library",
        "official_status": "community",
        "score": 10,
        "confidence": "medium",
        "checked_at": "2026-10-01T00:00:00+00:00",
        "score_components": {"relevance": 10},
        "license": "MIT",
        "maintenance_status": "active",
        "source_urls": ["https://github.com/acme/widget"],
        "discovered_from": ["unit-test"],
        "agent_type": "library",
        "unique_features": ["known"],
        "cost": "stated",
        "integration_type": "library",
        "system_fit": "stated",
        "verification": ["https://github.com/acme/widget"],
        "stars": 1,
    }
    base.update(overrides)
    return base


def audit(entries, count=None, stale_days=90):
    catalog = {"entries": entries}
    if count is not None:
        catalog["count"] = count
    return audit_catalog(
        catalog,
        SCHEMA,
        TAXONOMY,
        as_of=AS_OF,
        stale_days=stale_days,
    )


def test_valid_entry_passes_without_soft_findings():
    report = audit([entry()], count=1)
    assert report["passed"] is True
    assert report["hard_errors"] == []
    assert report["entry_count"] == 1
    assert report["declared_count"] == 1
    assert all(value == 0 for value in report["soft_findings"].values())


def test_duplicate_id_and_repository_are_hard_errors():
    report = audit([entry(), entry()], count=2)
    assert report["passed"] is False
    assert "acme/widget: duplicate id" in report["hard_errors"]
    assert "acme/widget: duplicate repository acme/widget" in report["hard_errors"]


def test_case_collision_is_a_hard_error():
    other = entry(
        id="Acme/widget",
        owner="Acme",
        repository="Acme/widget",
        repository_url="https://github.com/Acme/widget",
    )
    report = audit([entry(), other], count=2)
    assert any("case-insensitive id collision" in error for error in report["hard_errors"])


def test_owner_url_and_repository_mismatch_are_hard_errors():
    report = audit(
        [
            entry(
                owner="other",
                repository="acme/other",
                repository_url="https://example.com/acme/widget",
            )
        ],
        count=1,
    )
    text = "\n".join(report["hard_errors"])
    assert "owner 'other' does not match id prefix 'acme'" in text
    assert "repository_url must be https://github.com/acme/widget" in text
    assert "does not match repository acme/other" in text


def test_count_category_type_and_score_mismatch_are_hard_errors():
    report = audit(
        [
            entry(
                primary_category="Z.99",
                project_type="spaceship",
                score=10,
                score_components={"relevance": 9},
            )
        ],
        count=2,
    )
    text = "\n".join(report["hard_errors"])
    assert "count 2 does not match len(entries) 1" in text
    assert "primary_category Z.99 is not in taxonomy" in text
    assert "invalid project_type spaceship" in text
    assert "differs from component sum" in text


def test_float_noise_within_tolerance_is_not_a_hard_error():
    report = audit([entry(score=10.05, score_components={"relevance": 10})], count=1)
    assert report["hard_errors"] == []


def test_missing_facts_are_soft_and_not_invented():
    report = audit(
        [
            entry(
                license=None,
                maintenance_status="unclear",
                description="too short",
                checked_at="2026-07-07T16:39:26+00:00",
                source_urls=[],
                discovered_from=[],
                agent_type=None,
                unique_features=[],
                cost=None,
                integration_type=None,
                system_fit=None,
                verification=[],
            )
        ],
        count=1,
    )
    assert report["passed"] is True
    soft = report["soft_findings"]
    assert soft["license_missing"] == 1
    assert soft["maintenance_unclear"] == 1
    assert soft["description_under_12_words"] == 1
    assert soft["description_over_30_words"] == 0
    assert soft["checked_at_stale"] == 1
    assert soft["source_urls_missing"] == 1
    assert soft["discovered_from_missing"] == 1
    for field in (
        "agent_type",
        "unique_features",
        "cost",
        "integration_type",
        "system_fit",
        "verification",
    ):
        assert soft[f"unknown_{field}"] == 1


def test_negative_stars_are_a_hard_error():
    report = audit([entry(stars=-1)], count=1)
    assert any("stars must be a non-negative integer" in error for error in report["hard_errors"])


def test_main_catalog_has_no_hard_errors_and_records_unknowns():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "data" / "catalog.schema.json").read_text(encoding="utf-8"))
    taxonomy = json.loads((ROOT / "data" / "taxonomy.json").read_text(encoding="utf-8"))
    report = audit_catalog(catalog, schema, taxonomy, as_of=AS_OF, stale_days=90)
    assert report["passed"] is True
    assert report["hard_errors"] == []
    assert report["entry_count"] == 1468
    assert report["declared_count"] == 1468
    assert report["soft_findings"] == {
        "license_missing": 1428,
        "maintenance_unclear": 1466,
        "description_under_12_words": 585,
        "description_over_30_words": 65,
        "checked_at_stale": 1468,
        "source_urls_missing": 0,
        "discovered_from_missing": 0,
        "unknown_agent_type": 1468,
        "unknown_unique_features": 1468,
        "unknown_cost": 1468,
        "unknown_integration_type": 1468,
        "unknown_system_fit": 1468,
        "unknown_verification": 1468,
    }


def test_cli_does_not_modify_the_catalog(tmp_path):
    catalog_path = ROOT / "data" / "catalog.json"
    before = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "audit_catalog.py"),
            "--catalog",
            str(catalog_path),
            "--schema",
            str(ROOT / "data" / "catalog.schema.json"),
            "--taxonomy",
            str(ROOT / "data" / "taxonomy.json"),
            "--as-of",
            "2026-10-28",
            "--report",
            str(tmp_path / "audit.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    after = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert before == after
    report = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["entry_count"] == 1468
