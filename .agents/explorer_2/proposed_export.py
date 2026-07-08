#!/usr/bin/env python3
"""
export.py — Export catalog to JSON, NDJSON, and CSV formats.

Usage:
    python scripts/export.py --input data/catalog.json --output-dir data/
"""

import argparse
import csv
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Export catalog to multiple formats")
    parser.add_argument("--input", default="data/catalog.json", help="Path to input catalog.json")
    parser.add_argument("--output-dir", default="data", help="Directory to write exports")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input catalog not found at {args.input}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8-sig") as f:
        catalog_data = json.load(f)

    entries = catalog_data.get("entries", [])
    print(f"Loaded {len(entries)} entries from {args.input}")

    # 1. Export JSON (Clean formatted copy)
    json_path = os.path.join(args.output_dir, "catalog.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)
    print(f"Exported JSON to {json_path}")

    # 2. Export NDJSON
    ndjson_path = os.path.join(args.output_dir, "catalog.ndjson")
    with open(ndjson_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Exported NDJSON to {ndjson_path}")

    # 3. Export CSV
    csv_path = os.path.join(args.output_dir, "catalog.csv")
    csv_fields = [
        "id", "name", "owner", "repository", "repository_url", "homepage_url",
        "primary_category", "project_type", "official_status", "score",
        "stars", "forks", "open_issues", "primary_language", "license",
        "checked_at"
    ]
    
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for entry in entries:
            # Flatten or handle potential nulls/nested values if necessary
            writer.writerow(entry)
            
    print(f"Exported CSV to {csv_path}")

if __name__ == "__main__":
    main()
