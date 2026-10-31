#!/usr/bin/env python3
"""Manual/local WERKAtlas GitHub radar: suggest official repository URLs, no auto-import."""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def discover(existing: set[str], query: str, fetch, limit: int=10) -> dict:
    if not 1 <= limit <= 50: raise ValueError("limit 1..50")
    candidates=[]
    seen=set(existing)
    for repo in fetch(query, limit):
        name=repo.get("full_name")
        if not isinstance(name,str) or name.count("/") != 1 or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        license_value = repo.get("license") or {}
        spdx = license_value.get("spdx_id") if isinstance(license_value,dict) else None
        candidates.append({
            "id":name,
            "repository_url":f"https://github.com/{name}",
            "description_unverified":repo.get("description"),
            "stars_snapshot":repo.get("stargazers_count"),
            "license_github":None if spdx in (None,"NOASSERTION","NONE") else spdx,
            "archived":repo.get("archived"),
            "pushed_at":repo.get("pushed_at"),
            "status":"review_required",
            "note":"Verify official repo, LICENSE and suitability; do not import automatically.",
        })
    return {"query":query,"checked_at":datetime.now(timezone.utc).isoformat(),
            "count":len(candidates),"candidates":candidates}


def github_search(query: str, limit: int) -> list[dict]:
    url="https://api.github.com/search/repositories?"+urllib.parse.urlencode({
        "q":query,"sort":"updated","order":"desc","per_page":min(limit,50)
    })
    headers={"User-Agent":"WERKAtlas-local-radar/1.0","Accept":"application/vnd.github+json"}
    token=os.getenv("GITHUB_TOKEN")
    if token:headers["Authorization"]="Bearer "+token
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as response:
        return json.load(response).get("items",[])


def main(argv=None):
    parser=argparse.ArgumentParser(description="Read-only discovery report; no GitHub Actions")
    parser.add_argument("--catalog",default=str(ROOT/"data/catalog.json"))
    parser.add_argument("--query",required=True)
    parser.add_argument("--limit",type=int,default=10)
    parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    try:
        dest=Path(args.output)
        if dest.exists(): raise ValueError("Report exists; will not overwrite")
        catalog=json.loads(Path(args.catalog).read_text(encoding="utf-8-sig"))
        existing={x["id"].casefold() for x in catalog["entries"]}
        report=discover(existing,args.query,github_search,limit=args.limit)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(f"Radar candidates: {len(report['candidates'])} -> {dest}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}",file=sys.stderr)
        return 1

if __name__=="__main__":raise SystemExit(main())
