#!/usr/bin/env python3
"""Read-only priority backlog for evidence-based WERKAtlas metadata refresh.

No network requests, no catalog writes and no inferred licenses.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _date(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.astimezone(timezone.utc)
    except ValueError:
        return None


def build_backlog(
    catalog: dict,
    *,
    as_of: datetime,
    limit: int = 50,
    stale_days: int = 90,
) -> dict:
    """Sort verifiable metadata gaps, not inferred implementation quality."""
    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")
    if limit < 1 or limit > 500:
        raise ValueError("limit must be 1..500")
    if stale_days < 1:
        raise ValueError("stale_days must be positive")
    as_of = as_of.astimezone(timezone.utc)
    entries = catalog.get("entries", [])
    rows = []
    counts = {
        "total": len(entries),
        "license_missing": 0,
        "maintenance_unclear": 0,
        "checked_at_stale_or_unknown": 0,
        "pushed_at_missing": 0,
        "official_evidence_missing": 0,
    }
    for entry in entries:
        missing = []
        if not entry.get("license"):
            missing.append("license")
            counts["license_missing"] += 1
        if entry.get("maintenance_status") in (None, "", "unclear"):
            missing.append("maintenance_status")
            counts["maintenance_unclear"] += 1
        checked = _date(entry.get("checked_at"))
        if checked is None or (as_of - checked).total_seconds() > stale_days * 86400 or checked > as_of:
            missing.append("checked_at")
            counts["checked_at_stale_or_unknown"] += 1
        if not entry.get("pushed_at"):
            missing.append("pushed_at")
            counts["pushed_at_missing"] += 1
        if not entry.get("official_evidence"):
            counts["official_evidence_missing"] += 1
        if not missing:
            continue
        score = entry.get("score")
        if not isinstance(score, (float, int)) or isinstance(score, bool):
            score = None
        stars = entry.get("stars")
        if not isinstance(stars, int) or isinstance(stars, bool):
            stars = None
        rows.append({
            "id": entry.get("id"),
            "repository_url": entry.get("repository_url"),
            "existing_score_stale_possible": score,
            "stars_snapshot": stars,
            "checked_at": entry.get("checked_at"),
            "missing_or_stale": missing,
            "action": "Verify current facts from official repository and attach source evidence in a review PR",
        })
    rows.sort(key=lambda row: (
        -(row["existing_score_stale_possible"] if row["existing_score_stale_possible"] is not None else -1),
        -(row["stars_snapshot"] if row["stars_snapshot"] is not None else -1),
        row["id"] or "",
    ))
    return {
        "as_of": as_of.isoformat(),
        "stale_days": stale_days,
        "counts": counts,
        "total_needing_review": len(rows),
        "selected": rows[:limit],
        "note": "Backlog only; existing scores/stars may be stale. License, maintenance and suitability remain unverified until independently sourced.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a read-only WERKAtlas metadata review backlog")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--as-of", help="ISO date/time, defaults to today's UTC date")
    args = parser.parse_args()
    stamp = _date(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if stamp is None:
        parser.error("invalid --as-of date")
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8-sig"))
    result = build_backlog(catalog, as_of=stamp, limit=args.limit, stale_days=args.stale_days)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
