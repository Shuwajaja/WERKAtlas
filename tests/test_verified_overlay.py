"""Verified GitHub facts must not modify or reinterpret the original Atlas catalog."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_verified_overlay import build_overlay
from metadata_graphql import query_for,response_to_items


def test_graphql_ids_are_escaped_and_verified():
    query=query_for(["acme/repo-one","other/repo.two"])
    assert "nameWithOwner" in query
    assert 'owner:"acme"' in query
    sample={"data":{"r0":{"nameWithOwner":"acme/repo-one","stargazerCount":9,
                         "forkCount":2,"isArchived":False,"pushedAt":"2026-10-31T00:00:00Z",
                         "licenseInfo":{"spdxId":"NOASSERTION"}}}}
    result=response_to_items(["acme/repo-one","other/repo.two"],sample,"2026-10-31T00:00:00Z")
    assert result[0]["status"]=="ok"
    assert result[0]["verified_facts"]["license"] is None
    assert result[1]["status"]=="unavailable"


def test_overlay_contains_only_verified_records():
    sample={"generated_at":"2026-10-31","results":[
        {"id":"acme/one","status":"ok","checked_at":"2026-10-31",
         "verified_facts":{"stars":10,"forks":1,"archived":False,"pushed_at":None,"license":"MIT"}},
        {"id":"acme/two","status":"unavailable"},
    ]}
    out=build_overlay(sample)
    assert out["verified_count"]==1
    assert out["license_spdx_count"]==1
    assert "acme/two" not in out["entries"]
    assert "acme/two" in out["unverified_ids"]


def test_full_report_matches_committed_overlay_and_catalog_untouched():
    catalog_path=ROOT/"data/catalog.json"
    catalog_bytes=catalog_path.read_bytes()
    overlay_path=ROOT/"data/verified-github.json"
    overlay=json.loads(overlay_path.read_text(encoding="utf-8"))
    catalog=json.loads(catalog_bytes)
    assert overlay["verified_count"]==len(overlay["entries"])
    assert overlay["license_spdx_count"]==sum(bool(x["license"]) for x in overlay["entries"].values())
    assert len(overlay["unverified_ids"])+overlay["verified_count"]==len(catalog["entries"])
    assert len(catalog["entries"])==1516
    assert all(k==k.lower() for k in overlay["entries"].keys())
    assert catalog_path.read_bytes()==catalog_bytes
