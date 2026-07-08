#!/usr/bin/env python3
"""
update_trends.py — Compute and update trend_data (stars_30d, stars_90d) from Git history.

This script leverages Git history to find what the star counts were 30 and 90 days ago,
populates the `trend_data` for each entry, and saves the catalog.

Usage:
    python scripts/update_trends.py --catalog data/catalog.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

def get_catalog_from_git(days_ago: int) -> dict:
    """Retrieve data/catalog.json content from approximately N days ago using git."""
    try:
        # Find the commit hash closest to N days ago
        date_str = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
        cmd_commit = [
            "git", "rev-list", "-n", "1",
            f"--before={date_str}", "HEAD"
        ]
        commit_hash = subprocess.check_output(cmd_commit, text=True).strip()
        
        if not commit_hash:
            return {}
            
        # Retrieve catalog.json at that commit
        cmd_show = ["git", "show", f"{commit_hash}:data/catalog.json"]
        content = subprocess.check_output(cmd_show, text=True)
        return json.loads(content)
    except Exception as e:
        print(f"Warning: Could not retrieve catalog from {days_ago} days ago: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Update catalog trending/momentum data")
    parser.add_argument("--catalog", default="data/catalog.json", help="Path to catalog.json")
    args = parser.parse_args()

    with open(args.catalog, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    entries = catalog.get("entries", [])
    
    # Retrieve historical catalogs
    catalog_30d = get_catalog_from_git(30)
    catalog_90d = get_catalog_from_git(90)

    stars_map_30d = {e["id"]: e.get("stars", 0) for e in catalog_30d.get("entries", [])} if catalog_30d else {}
    stars_map_90d = {e["id"]: e.get("stars", 0) for e in catalog_90d.get("entries", [])} if catalog_90d else {}

    updated_count = 0
    for entry in entries:
        eid = entry.get("id")
        stars_30d = stars_map_30d.get(eid)
        stars_90d = stars_map_90d.get(eid)
        
        entry["trend_data"] = {
            "stars_30d": stars_30d,
            "stars_90d": stars_90d,
            "method": "git" if (stars_30d is not None or stars_90d is not None) else None
        }
        updated_count += 1

    print(f"Updated trend data for {updated_count} entries.")

    with open(args.catalog, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
