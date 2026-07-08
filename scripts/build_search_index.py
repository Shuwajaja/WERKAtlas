#!/usr/bin/env python3
"""
build_search_index.py — Build a compact search index for the Atlas Explorer.

Reads catalog.json and writes data/search-index.json.
The index contains only the fields needed for client-side search, filtering,
and sorting in the Astro site — keeping the payload small.

Usage:
    python scripts/build_search_index.py
    python scripts/build_search_index.py --input data/catalog.json --output data/search-index.json
"""

import argparse
import json
import sys
from pathlib import Path


# Fields included in the compact search index.
# All other fields are only fetched on project detail pages.
INDEX_FIELDS = {
    "id",
    "name",
    "repository",
    "owner",
    "description",
    "primary_category",
    "secondary_categories",
    "project_type",
    "score",
    "score_label",
    "stars",
    "forks",
    "license",
    "primary_language",
    "languages",
    "protocols",
    "capabilities",
    "official_status",
    "maintenance_status",
    "archived",
    "pushed_at",
    "latest_release_at",
    "checked_at",
}


def slim_entry(entry: dict) -> dict:
    """Extract only index-relevant fields."""
    result = {}
    for field in INDEX_FIELDS:
        value = entry.get(field)
        result[field] = value
    # Derive a URL-safe slug from the repository field
    repo = entry.get("repository", "")
    result["slug"] = repo.replace("/", "-").lower() if repo else entry.get("id", "").replace("/", "-").lower()
    return result


def main():
    parser = argparse.ArgumentParser(description="Build compact search index for Atlas Explorer")
    parser.add_argument("--input",  default="data/catalog.json")
    parser.add_argument("--output", default="data/search-index.json")
    args = parser.parse_args()

    print("=" * 60)
    print("WERKAtlas — Search Index Builder (build_search_index.py)")
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

    index_entries = [slim_entry(e) for e in entries]

    output = {
        "snapshot_date": data.get("snapshot_date", "unknown"),
        "count":         len(index_entries),
        "fields":        sorted(INDEX_FIELDS) + ["slug"],
        "entries":       index_entries,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, separators=(",", ":"), ensure_ascii=False)

    size_kb = output_path.stat().st_size / 1024
    print(f"\nIndex entries:  {len(index_entries)}")
    print(f"Output:         {output_path}")
    print(f"File size:      {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
