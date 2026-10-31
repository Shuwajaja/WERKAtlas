#!/usr/bin/env python3
"""Batch public GitHub GraphQL facts for WERKAtlas, without changing the catalog.

Use with scripts/with_github_token.ps1 on Windows. Never print or persist tokens.
A missing licenseInfo.spdxId is UNKNOWN, not proof of any license.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def query_for(ids: list[str]) -> str:
    lines=[]
    for idx,project_id in enumerate(ids):
        owner,name=project_id.split("/",1)
        lines.append(f'r{idx}:repository(owner:{json.dumps(owner)},name:{json.dumps(name)})'
                     '{nameWithOwner stargazerCount forkCount isArchived pushedAt licenseInfo{spdxId}}')
    return "query {"+" ".join(lines)+" rateLimit { remaining cost resetAt } }"


def response_to_items(ids: list[str], response: dict, fetched_at: str) -> list[dict]:
    data=response.get("data") or {}
    errors=response.get("errors") or []
    results=[]
    for index,project_id in enumerate(ids):
        record=data.get(f"r{index}")
        if not isinstance(record,dict) or record.get("nameWithOwner","").casefold()!=project_id.casefold():
            results.append({"id":project_id,"status":"unavailable","review_required":True})
            continue
        lic=record.get("licenseInfo") or {}
        spdx=lic.get("spdxId")
        verified_license=spdx if isinstance(spdx,str) and spdx not in ("NOASSERTION","NONE","") else None
        results.append({
            "id":project_id,"status":"ok","checked_at":fetched_at,
            "source":"https://api.github.com/graphql",
            "verified_facts":{
                "stars":record.get("stargazerCount"),
                "forks":record.get("forkCount"),
                "archived":record.get("isArchived"),
                "pushed_at":record.get("pushedAt"),
                "license":verified_license,
            },
            "unknown_fields":["license"] if verified_license is None else [],
            "review_required":True,
        })
    return results


def fetch_graphql(url: str, token: str, query: str) -> dict:
    body=json.dumps({"query":query}).encode("utf-8")
    request=urllib.request.Request(url,data=body,method="POST",headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "Content-Type":"application/json",
        "User-Agent":"WERKAtlas-local-graphql/1.0",
    })
    with urllib.request.urlopen(request,timeout=30) as response:
        return json.load(response)


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description="Official GitHub bulk metadata, review-only")
    parser.add_argument("--catalog",default=str(ROOT/"data/catalog.json"))
    parser.add_argument("--limit",type=int,default=100)
    parser.add_argument("--offset",type=int,default=0)
    parser.add_argument("--batch",type=int,default=25)
    parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    token=os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is unavailable. Use existing Git credential helper securely.",file=sys.stderr)
        return 2
    if not 1<=args.limit<=2000 or args.offset<0 or not 1<=args.batch<=40:
        parser.error("limit 1..2000, offset>=0, batch 1..40")
    dest=Path(args.output)
    if dest.exists() or dest.with_suffix(dest.suffix+".partial").exists():
        parser.error("Refusing to overwrite existing reports")
    catalog=json.loads(Path(args.catalog).read_text(encoding="utf-8-sig"))
    ids=[e["id"] for e in catalog["entries"]][args.offset:args.offset+args.limit]
    fetched_at=datetime.now(timezone.utc).isoformat()
    report={"generated_at":fetched_at,"requested":len(ids),"results":[],
            "note":"Official GitHub GraphQL metadata, review-only. No catalog changes."}
    partial=dest.with_suffix(dest.suffix+".partial")
    dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        for start in range(0,len(ids),args.batch):
            batch=ids[start:start+args.batch]
            response=fetch_graphql("https://api.github.com/graphql",token,query_for(batch))
            report["results"].extend(response_to_items(batch,response,fetched_at))
            partial.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print(f"Verified batch {start//args.batch+1}: {len(report['results'])}/{len(ids)}",file=sys.stderr)
            time.sleep(0.15)
        report["verified"]=sum(row["status"]=="ok" for row in report["results"])
        report["licenses_with_spdx"]=sum(row.get("verified_facts",{}).get("license") is not None for row in report["results"])
        dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        partial.unlink(missing_ok=True)
        print(json.dumps({"requested":len(ids),"verified":report["verified"],
                          "licenses_with_spdx":report["licenses_with_spdx"],"report":str(dest)}))
        return 0 if report["verified"]==len(ids) else 2
    except (OSError,ValueError,KeyError) as exc:
        print(f"GitHub GraphQL incomplete ({type(exc).__name__}). Partial checkpoint retained.",file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
