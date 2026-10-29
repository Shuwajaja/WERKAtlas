"""One GitHub metadata diff. The catalog file stays untouched."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from refresh_github_report import build_refresh_report  # noqa: E402


def test_report_proposes_stars_and_does_not_invent_license_when_github_has_none():
    entry = {
        "id": "acme/widget",
        "stars": 10,
        "license": None,
        "archived": False,
        "description": "bleibt",
    }
    github = {
        "stargazerCount": 12,
        "isArchived": False,
        "licenseInfo": None,
        "pushedAt": "2026-10-01T00:00:00Z",
    }
    report = build_refresh_report(entry, github)
    assert report["changes"]["stars"] == {"from": 10, "to": 12}
    assert "license" not in report["changes"]
    assert "description" not in report["changes"]
    assert "license" in report["skipped_unknown"]


def test_noassertion_and_existing_license_are_not_rewritten():
    empty = {"id": "acme/widget", "license": None, "stars": 1}
    filled = {"id": "acme/widget", "license": "Apache-2.0", "stars": 1}
    noassertion = {"stargazerCount": 1, "licenseInfo": {"spdxId": "NOASSERTION"}}
    different = {"stargazerCount": 1, "licenseInfo": {"spdxId": "MIT"}}
    assert "license" not in build_refresh_report(empty, noassertion)["changes"]
    assert "license" not in build_refresh_report(filled, different)["changes"]
    proposed = build_refresh_report(empty, different)
    assert proposed["changes"]["license"] == {"from": None, "to": "MIT"}


def test_cli_prints_a_report_without_writing_the_catalog(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    github_path = tmp_path / "github.json"
    catalog = {
        "count": 1,
        "entries": [
            {
                "id": "acme/widget",
                "stars": 3,
                "forks": 1,
                "archived": False,
                "license": None,
                "description": "bleibt stehen",
            }
        ],
    }
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    before = catalog_path.read_bytes()
    github_path.write_text(
        json.dumps(
            {
                "stargazerCount": 9,
                "forkCount": 1,
                "isArchived": True,
                "licenseInfo": {"spdxId": "MIT"},
                "pushedAt": "2026-10-02T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "refresh_github_report.py"),
            "--id",
            "acme/widget",
            "--catalog",
            str(catalog_path),
            "--github",
            str(github_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["changes"]["stars"]["to"] == 9
    assert report["changes"]["archived"]["to"] is True
    assert report["changes"]["license"]["to"] == "MIT"
    assert "description" not in report["changes"]
    assert catalog_path.read_bytes() == before
