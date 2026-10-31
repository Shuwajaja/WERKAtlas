#!/usr/bin/env python3
"""Offline snapshot/trend calculation from *verified* GitHub reports.

Only compares truly observed star counts from different dates. Never uses an
old catalog score as if it were current GitHub data and never edits catalog.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_date(text: str):
    stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc)


def from_report(report: dict) -> dict:
    observed = {}
    for item in report.get("results", []):
        if item.get("status") != "ok":
            continue
        stars = (item.get("verified_facts") or {}).get("stars")
        if isinstance(stars, int) and not isinstance(stars, bool) and stars >= 0:
            observed[item["id"]] = stars
    if not observed:
        raise ValueError("No verified star observations; run a fresh GitHub probe")
    return {
        "observed_at": report["checked_at"],
        "source": "official GitHub metadata probe",
        "stars": observed,
    }


def compare(previous: dict, current: dict, *, minimum_days: int = 7) -> dict:
    old = parse_date(previous["observed_at"])
    new = parse_date(current["observed_at"])
    delta_days = (new - old).total_seconds() / 86400
    if delta_days < minimum_days:
        return {"status": "insufficient_time_span", "days": round(delta_days, 2),
                "minimum_days": minimum_days, "trends": []}
    trends = []
    for key in sorted(set(previous["stars"]) & set(current["stars"])):
        old_stars, new_stars = previous["stars"][key], current["stars"][key]
        growth = new_stars - old_stars
        trends.append({
            "id": key, "from_stars": old_stars, "to_stars": new_stars,
            "growth": growth,
            "growth_percent": round(growth / old_stars * 100, 2) if old_stars else None,
        })
    trends.sort(key=lambda row: (-row["growth"], row["id"]))
    return {
        "status": "observed", "start": old.isoformat(), "end": new.isoformat(),
        "days": round(delta_days, 2), "trends": trends,
        "note": "Observed interval is not automatically an exact 7d/30d window.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline verified snapshot and actual time-series comparison")
    sub = parser.add_subparsers(dest="cmd", required=True)
    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--report", required=True)
    snapshot.add_argument("--output", required=True)
    trend = sub.add_parser("compare")
    trend.add_argument("--previous", required=True)
    trend.add_argument("--current", required=True)
    trend.add_argument("--minimum-days", type=int, default=7)
    trend.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        output = Path(args.output).resolve()
        if output.exists():
            raise ValueError("Refusing to overwrite existing snapshot/report")
        if args.cmd == "snapshot":
            result = from_report(json.loads(Path(args.report).read_text(encoding="utf-8-sig")))
        else:
            result = compare(
                json.loads(Path(args.previous).read_text(encoding="utf-8-sig")),
                json.loads(Path(args.current).read_text(encoding="utf-8-sig")),
                minimum_days=args.minimum_days,
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{result.get('status', 'snapshot')} -> {output}")
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
