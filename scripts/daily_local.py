#!/usr/bin/env python3
"""Run a bounded, local, review-only WERKAtlas morning research cycle.

No GitHub Actions, catalog writes, external command execution or automatic commits.
Each date has immutable files. If Windows is off, no cycle occurs that day.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from metadata_probe import sample_catalog, fetch_metadata  # noqa: E402
from radar_local import discover, github_search  # noqa: E402
from verified_trends import from_report, compare  # noqa: E402


def run_day(catalog: dict, *, day: str, workdir: Path,
            probe_fetch=fetch_metadata, radar_fetch=github_search,
            batch_size: int = 10) -> dict:
    if not 1 <= batch_size <= 30:
        raise ValueError("batch_size 1..30")
    if len(day)!=10 or datetime.fromisoformat(day).date().isoformat()!=day:
        raise ValueError("day must be YYYY-MM-DD")
    workdir.mkdir(parents=True,exist_ok=True)
    filenames={key:workdir/f"{day}-{key}.json" for key in ("metadata","radar","snapshot","trend","summary")}
    if any(path.exists() for path in filenames.values()):
        raise ValueError(f"Day already has artifacts: {day}; refusing duplicate run")
    days_since_start=(datetime.fromisoformat(day).date()-datetime(2026,10,31).date()).days
    offset=max(0,days_since_start)*batch_size % max(1,len(catalog["entries"]))
    metadata=sample_catalog(catalog,limit=batch_size,offset=offset,
                            fetch=probe_fetch,checked_at=datetime.now(timezone.utc).isoformat())
    radar=discover({e["id"].casefold() for e in catalog["entries"]},
                   "voice agent sip",radar_fetch,limit=10)
    snapshot=from_report(metadata) if metadata["fetched"] else None
    older=[]
    for path in sorted(workdir.glob("*-snapshot.json"),reverse=True):
        try:
            current=json.loads(path.read_text(encoding="utf-8"))
            if current["observed_at"][:10] < day:older.append(current)
        except (ValueError,KeyError):
            continue
    eligible=[p for p in older if snapshot and (datetime.fromisoformat(snapshot["observed_at"]) - datetime.fromisoformat(p["observed_at"])).total_seconds()>=7*86400]
    trend=compare(eligible[0],snapshot,minimum_days=7) if eligible and snapshot else {
        "status":"insufficient_history","trends":[]}
    summary={"day":day,"metadata_fetched":metadata["fetched"],
             "metadata_requested":metadata["requested"],"new_radar_candidates":radar["count"],
             "trend_status":trend["status"],"catalog_modified":False,"review_required":True}
    result={"metadata":metadata,"radar":radar,"snapshot":snapshot,"trend":trend,"summary":summary}
    for key,obj in result.items():
        if obj is not None:
            filenames[key].write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary


def main(argv=None):
    parser=argparse.ArgumentParser(description="Local daily review-only WERKAtlas research")
    parser.add_argument("--catalog",default=str(ROOT/"data/catalog.json"))
    parser.add_argument("--workdir",default=str(ROOT/"research/local-daily"))
    parser.add_argument("--day",default=datetime.now().date().isoformat())
    parser.add_argument("--batch-size",type=int,default=10)
    args=parser.parse_args(argv)
    try:
        catalog=json.loads(Path(args.catalog).read_text(encoding="utf-8-sig"))
        result=run_day(catalog,day=args.day,workdir=Path(args.workdir),batch_size=args.batch_size)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result["metadata_fetched"]==result["metadata_requested"] else 2
    except (OSError,ValueError,KeyError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
