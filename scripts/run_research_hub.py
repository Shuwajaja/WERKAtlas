#!/usr/bin/env python3
"""Local daily research coordinator, no GitHub Actions or catalog modifications.

News refreshes every invocation. Once-per-day GitHub radar/report is skipped
if its date already has a summary file; avoids overwriting immutable reports.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def commands_for(day: str, daily_summary_exists: bool, *, python: str=sys.executable) -> list[list[str]]:
    actions=[[python,str(ROOT/"scripts/news_radar.py"),"--output",
             str(ROOT/"web/public/news/latest.json"),"--days","21"]]
    if not daily_summary_exists:
        actions.append([python,str(ROOT/"scripts/daily_local.py"),"--day",day,"--batch-size","10"])
    return actions


def main(argv=None):
    parser=argparse.ArgumentParser(description="Refresh local news and daily GitHub research")
    parser.add_argument("--day",default=datetime.now().date().isoformat())
    parser.add_argument("--news-only",action="store_true")
    args=parser.parse_args(argv)
    day=args.day
    try:
        datetime.fromisoformat(day)
    except ValueError:
        parser.error("Invalid --day")
    exists=(ROOT/"research/local-daily"/f"{day}-summary.json").exists()
    commands=commands_for(day,exists)
    if args.news_only:commands=commands[:1]
    status=[]
    for cmd in commands:
        result=subprocess.run(cmd,cwd=ROOT,check=False,timeout=150)
        status.append({"task":Path(cmd[1]).name,"exit_code":result.returncode})
    print(json.dumps({"day":day,"daily_github_skipped":exists,"tasks":status}))
    return 0 if all(s["exit_code"]==0 for s in status) else 2

if __name__=="__main__":raise SystemExit(main())
