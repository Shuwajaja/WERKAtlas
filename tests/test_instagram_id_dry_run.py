"""Verified GitHub ids can be classified. They are not imported."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from instagram_id_dry_run import classify_ids  # noqa: E402


def test_dry_run_splits_present_and_absent_without_writing():
    report = classify_ids({"acme/widget"}, ["acme/widget", "other/repo", "acme/widget"])
    assert report["present"] == ["acme/widget"]
    assert report["absent"] == ["other/repo"]
    assert report["duplicate_input"] == ["acme/widget"]
    assert report["invalid"] == []


def test_invalid_ids_are_separated():
    report = classify_ids(set(), ["no-slash", "acme/", "/repo", "acme/widget"])
    assert report["invalid"] == ["no-slash", "acme/", "/repo"]
    assert report["absent"] == ["acme/widget"]


def test_cli_rejects_private_drive_keys_and_does_not_write_catalog(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps({"entries": [{"id": "acme/widget"}]}),
        encoding="utf-8",
    )
    before = catalog_path.read_bytes()
    blocked = tmp_path / "blocked.json"
    blocked.write_text(
        json.dumps({"verified_ids": ["acme/widget"], "file_id": "secret"}),
        encoding="utf-8",
    )
    blocked_run = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "instagram_id_dry_run.py"),
            "--catalog",
            str(catalog_path),
            "--ids",
            str(blocked),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert blocked_run.returncode == 2
    assert catalog_path.read_bytes() == before

    allowed = tmp_path / "ids.json"
    allowed.write_text(json.dumps({"verified_ids": ["acme/widget", "other/repo"]}), encoding="utf-8")
    allowed_run = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "instagram_id_dry_run.py"),
            "--catalog",
            str(catalog_path),
            "--ids",
            str(allowed),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert allowed_run.returncode == 0, allowed_run.stderr
    report = json.loads(allowed_run.stdout)
    assert report["present"] == ["acme/widget"]
    assert report["absent"] == ["other/repo"]
    assert catalog_path.read_bytes() == before
