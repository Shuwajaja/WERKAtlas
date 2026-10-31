#!/usr/bin/env python3
"""Create compact, verified GitHub metadata sidecar from GraphQL review results.

No catalog edits. Only 'ok' matching identity records are published.
The source report remains the auditable evidence; SPDX is not a legal signoff.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def build_overlay(report: dict) -> dict:
    entries={}
    failures=[]
    for row in report.get("results", []):
        ident=row.get("id")
        if not isinstance(ident,str) or ident.count("/") != 1:
            continue
        if row.get("status")!="ok":
            failures.append(ident)
            continue
        facts=row.get("verified_facts") or {}
        if not (isinstance(facts.get("stars"),int) and not isinstance(facts.get("stars"),bool)
                and facts["stars"]>=0):
            failures.append(ident)
            continue
        license_id=facts.get("license")
        if license_id is not None and (not isinstance(license_id,str) or license_id.upper() in {"NONE","NOASSERTION"}):
            license_id=None
        entries[ident.lower()]={
            "id":ident,
            "stars":facts["stars"],
            "forks":facts.get("forks"),
            "archived":facts.get("archived"),
            "pushed_at":facts.get("pushed_at"),
            "license":license_id,
            "verified_at":row.get("checked_at") or report.get("generated_at"),
            "source":f"https://github.com/{ident}",
        }
    return {
        "generated_at":report.get("generated_at"),
        "data_source":"GitHub GraphQL API",
        "verification_scope":"repository metadata, not software safety or license rights",
        "verified_count":len(entries),
        "license_spdx_count":sum(bool(item["license"]) for item in entries.values()),
        "unverified_ids":sorted(failures),
        "entries":entries,
    }


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description="Build compact current GitHub facts sidecar")
    parser.add_argument("--report",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    try:
        dest=Path(args.output)
        if dest.exists():raise ValueError("Refusing to overwrite existing overlay")
        overlay=build_overlay(json.loads(Path(args.report).read_text(encoding="utf-8-sig")))
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(overlay,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(f"Official metadata: {overlay['verified_count']} projects; SPDX: {overlay['license_spdx_count']} -> {dest}")
        return 0
    except (OSError,ValueError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 1

if __name__=="__main__":raise SystemExit(main())
