#!/usr/bin/env python3
"""
snapshot.py — Save a timestamped snapshot of key catalog metrics.

Reads catalog.json and writes:
  data/history/YYYY-MM-DD.json   — daily snapshot
  data/history/latest.json       — always overwritten with the latest snapshot

Each snapshot entry contains only the fields needed for trending computation:
  id, repository, stars, forks, open_issues, pushed_at,
  latest_release_at, score, score_label, checked_at

Usage:
    python scripts/snapshot.py --input data/catalog.json
    python scripts/snapshot.py --input data/catalog.json --date 2026-07-07
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SNAPSHOT_FIELDS = [
    "id",
    "repository",
    "stars",
    "forks",
    "open_issues",
    "pushed_at",
    "latest_release_at",
    "score",
    "score_label",
    "checked_at",
]


def slim(entry: dict) -> dict:
    """Extract only snapshot-relevant fields from a catalog entry."""
    return {field: entry.get(field) for field in SNAPSHOT_FIELDS}


def main():
    parser = argparse.ArgumentParser(description="Save catalog snapshot for trending")
    parser.add_argument("--input", default="data/catalog.json")
    parser.add_argument("--date", default=None, help="Override snapshot date (YYYY-MM-DD)")
    args = parser.parse_args()

    print("=" * 60)
    print("WERKAtlas — Snapshot (snapshot.py)")
    print("=" * 60)

    catalog_path = Path(args.input)
    if not catalog_path.exists():
        print(f"ERROR: catalog not found at {catalog_path}", file=sys.stderr)
        sys.exit(1)

    with open(catalog_path, encoding="utf-8-sig") as f:
        data = json.load(f)

    entries = data.get("entries", [])
    if not entries:
        print("ERROR: catalog has no entries", file=sys.stderr)
        sys.exit(1)

    snapshot_date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_ts   = datetime.now(timezone.utc).isoformat(timespec="seconds")

    snapshot = {
        "snapshot_date": snapshot_date,
        "created_at":    snapshot_ts,
        "count":         len(entries),
        "entries":       [slim(e) for e in entries],
    }

    history_dir = Path("data/history")
    history_dir.mkdir(parents=True, exist_ok=True)

    daily_path  = history_dir / f"{snapshot_date}.json"
    latest_path = history_dir / "latest.json"

    with open(daily_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Snapshot written -> {daily_path}")

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Latest snapshot  -> {latest_path}")

    print(f"\nEntries snapshotted: {len(entries)}")
    print(f"Snapshot date:       {snapshot_date}")


if __name__ == "__main__":
    main()
