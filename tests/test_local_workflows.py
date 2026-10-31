"""Local, no-Actions workflow tests: all commands must preserve the catalog."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from local_workflow import find_projects, _dump  # noqa: E402


def test_exact_keywords_only_when_requested():
    entries=[
        {"id":"acme/voice","name":"Voice", "description":"Realtime voice streaming", "score":81,
         "license":"MIT","repository_url":"https://github.com/acme/voice"},
        {"id":"acme/sip","name":"SIP Voice", "description":"SIP voice integration", "score":75,
         "license":"MIT","repository_url":"https://github.com/acme/sip"},
    ]
    strict=find_projects(entries,"voice sip",require_all=True)
    assert [e["id"] for e in strict["results"]]==["acme/sip"]
    loose=find_projects(entries,"voice sip")
    assert len(loose["results"])==2
    assert "sip" in loose["results"][1]["unmatched_terms"]


def test_unverified_license_filter_never_assumes_missing_is_mit():
    entries=[{"id":"acme/one","name":"Voice","description":"voice","license":None,"score":99},
             {"id":"acme/two","name":"Voice","description":"voice","license":"MIT","score":50}]
    result=find_projects(entries,"voice",license="MIT")
    assert [x["id"] for x in result["results"]]==["acme/two"]


def test_report_refuses_existing_file_and_canonical_data_directory(tmp_path):
    output=tmp_path/"report.json"
    _dump({"ok":True},str(output))
    assert json.loads(output.read_text())=={"ok":True}
    import pytest
    with pytest.raises(ValueError,match="overwrite"):
        _dump({"ok":False},str(output))
    with pytest.raises(ValueError,match="canonical"):
        _dump({"ok":True},str(ROOT/"data"/"accidental-report.json"))


def test_makefile_default_safe_and_no_destructive_clean():
    text=(ROOT/"Makefile").read_text(encoding="utf-8")
    assert ".DEFAULT_GOAL := verify" in text
    assert "all: verify" in text
    assert "data/catalog.json data/catalog.csv" not in text
    assert "--as-of 2026-10-28" not in text
    assert "collect enrich classify score render clean setup:" in text


def test_no_catalog_changes_from_read_only_cli(tmp_path):
    import subprocess
    original=(ROOT/"data"/"catalog.json").read_bytes()
    dest=tmp_path/"projects.json"
    completed=subprocess.run([sys.executable,"scripts/local_workflow.py","recommend",
                              "--query","voice sip","--require-all","--output",str(dest)],
                             cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert completed.returncode==0,completed.stderr
    data=json.loads(dest.read_text(encoding="utf-8"))
    assert data["require_all_terms"] is True
    assert all(not e["unmatched_terms"] for e in data["results"])
    assert (ROOT/"data"/"catalog.json").read_bytes()==original
