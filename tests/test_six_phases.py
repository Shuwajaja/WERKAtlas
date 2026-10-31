"""Offline regression checks for six-phase WERKAtlas improvements."""
import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from metadata_probe import proposed_change, sample_catalog, license_id
from explain_quality import evaluate
from verified_trends import from_report, compare
from radar_local import discover

NOW=datetime(2026,10,31,tzinfo=timezone.utc)


def test_license_noassertion_stays_unknown():
    assert license_id({"license":{"spdx_id":"NOASSERTION"}}) is None
    assert license_id({"license":{"spdx_id":"MIT"}})=="MIT"


def test_metadata_diff_preserves_catalog_and_checks_id():
    entry={"id":"acme/tool","license":None,"stars":1,"forks":2,"archived":False}
    original=copy.deepcopy(entry)
    remote={"full_name":"acme/tool","license":{"spdx_id":"MIT"},"stargazers_count":5,
            "forks_count":2,"archived":False,"pushed_at":"2026-10-30T00:00:00Z"}
    result=proposed_change(entry,remote,"2026-10-31T00:00:00Z")
    assert result["verified_facts"]["stars"]==5
    assert result["proposed_changes"]["license"]["after"]=="MIT"
    assert result["review_required"] and entry==original
    try:
        proposed_change(entry,{**remote,"full_name":"other/tool"},"2026-10-31")
        assert False,"expected rejection"
    except ValueError:
        pass


def test_bulk_probe_handles_missing_remote_without_invention():
    entries={"entries":[{"id":"acme/a","license":None,"score":90,"stars":100},
                        {"id":"acme/b","license":None,"score":80,"stars":50}]}
    def fake_fetch(id):
        if id=="acme/b":raise OSError("test outage")
        return {"full_name":"acme/a","stargazers_count":110,"forks_count":1,
                "archived":False,"pushed_at":"2026-10-30T00:00:00Z","license":None}
    report=sample_catalog(entries,limit=2,fetch=fake_fetch,checked_at="2026-10-31T00:00:00Z")
    assert report["fetched"]==1
    assert report["results"][1]["status"]=="unavailable"
    assert entries["entries"][0]["stars"]==100


def test_separate_quality_from_task_fit_and_unknown_coverage():
    entry={"id":"acme/voice","name":"Voice","description":"voice agent","archived":False,
           "pushed_at":None,"license":None,"score":95}
    result=evaluate(entry,"voice sip",as_of=NOW)
    assert result["legacy_score"]==95
    assert result["quality_coverage_percent"]<70
    assert result["quality_label"]=="insufficient_evidence"
    assert result["task_fit_keyword_percent"]==50
    assert "sip" in result["task_fit_unmatched"]
    assert result["license_verification"]=="not_verified"


def test_trends_require_observed_interval_not_fake_30_day():
    report={"checked_at":"2026-10-01T00:00:00Z",
            "results":[{"status":"ok","id":"acme/a","verified_facts":{"stars":100}},
                       {"status":"unavailable","id":"acme/b"}]}
    older=from_report(report)
    later={"observed_at":"2026-10-31T00:00:00Z","stars":{"acme/a":120}}
    exact=compare(older,later)
    assert exact["status"]=="observed"
    assert exact["days"]==30
    assert exact["trends"][0]["growth"]==20
    assert compare(later,later)["status"]=="insufficient_time_span"


def test_radar_is_review_only_and_deduplicates():
    proposals=[
        {"full_name":"acme/new","license":{"spdx_id":"MIT"},"stargazers_count":2},
        {"full_name":"acme/new","license":{"spdx_id":"MIT"}},
        {"full_name":"acme/old"},
    ]
    result=discover({"acme/old"},"voice",lambda q,n: proposals,limit=10)
    assert result["count"]==1
    assert result["candidates"][0]["status"]=="review_required"


def test_site_exposes_real_snapshot_and_unknown_metadata():
    layout=(ROOT/"web/src/layouts/BaseLayout.astro").read_text(encoding="utf-8")
    explorer=(ROOT/"web/src/pages/explorer.astro").read_text(encoding="utf-8")
    quality=(ROOT/"web/src/pages/quality.astro").read_text(encoding="utf-8")
    assert "catalogSnapshotDate" in layout
    assert "KATALOG-SNAPSHOT" in layout
    assert "keywords.every" in explorer
    assert "data-topics" in explorer
    assert "entry.freshGithub?.license" in explorer
    assert "githubVerified" in quality
    assert "Datenqualität im WERKAtlas" in quality


def test_no_catalog_mutation():
    catalog=ROOT/"data/catalog.json"
    before=catalog.read_bytes()
    data=json.loads(before)
    evaluate(data["entries"][0],"voice",as_of=NOW)
    assert catalog.read_bytes()==before
