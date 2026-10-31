"""Offline-only regression tests for manual research and date-scoped local automation."""
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from daily_local import run_day
from metadata_probe import sample_catalog
from verified_trends import from_report, compare


def _remote(name):
    return {"full_name":name,"stargazers_count":12,"forks_count":1,
            "license":{"spdx_id":"MIT"},"pushed_at":"2026-10-30T00:00:00Z",
            "archived":False}


def test_probe_offset_and_no_catalog_change():
    catalog={"entries":[{"id":f"demo/{n}","score":100-n,"stars":0,
                         "license":None,"maintenance_status":"unclear"}
                        for n in range(6)]}
    before=json.dumps(catalog)
    report=sample_catalog(catalog,offset=3,limit=2,
                          fetch=lambda name:_remote(name),delay=0)
    assert [x["id"] for x in report["results"]]==["demo/3","demo/4"]
    assert all(x["status"]=="ok" for x in report["results"])
    assert catalog==json.loads(before)


def test_daily_runner_does_not_write_catalog_and_stops_duplicate(tmp_path):
    catalog={"entries":[{"id":"demo/a","score":99,"stars":0,
                         "license":None,"maintenance_status":"unclear"}]}
    initial=json.dumps(catalog)
    result=run_day(catalog,day="2026-10-31",workdir=tmp_path,
                   probe_fetch=lambda name:_remote(name),
                   radar_fetch=lambda query,limit:[{"full_name":"demo/new","stargazers_count":1}],
                   batch_size=1)
    assert result["metadata_fetched"]==1
    assert result["new_radar_candidates"]==1
    assert result["trend_status"]=="insufficient_history"
    assert len(list(tmp_path.glob("2026-10-31-*.json")))==5
    assert json.dumps(catalog)==initial
    with pytest.raises(ValueError,match="already"):
        run_day(catalog,day="2026-10-31",workdir=tmp_path,
                probe_fetch=lambda name:_remote(name),
                radar_fetch=lambda q,n:[],batch_size=1)


def test_snapshot_requires_actual_observation():
    with pytest.raises(ValueError,match="No verified"):
        from_report({"checked_at":"2026-10-31T00:00:00Z","results":[{"status":"unavailable","id":"demo/a"}]})


def test_no_fake_growth_when_less_than_week():
    a={"observed_at":"2026-10-30T00:00:00Z","stars":{"demo/a":10}}
    b={"observed_at":"2026-10-31T00:00:00Z","stars":{"demo/a":14}}
    assert compare(a,b,minimum_days=7)["status"]=="insufficient_time_span"
