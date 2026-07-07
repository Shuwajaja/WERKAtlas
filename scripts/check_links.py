#!/usr/bin/env python3
"""
check_links.py — Check external links in catalog entries.

Usage:
    python scripts/check_links.py --catalog data/catalog.json
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


USER_AGENT = "agentic-engineering-compendium/1.0"
TIMEOUT = 15
MAX_WORKERS = 5


def check_url(url: str) -> tuple:
    """Check if a URL is accessible."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return (url, resp.status, None)
    except urllib.error.HTTPError as e:
        return (url, e.code, str(e.reason))
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return (url, None, str(e))


def main():
    parser = argparse.ArgumentParser(description="Check external links in catalog")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS)
    args = parser.parse_args()
    
    if not os.path.exists(args.catalog):
        print(f"Catalog not found: {args.catalog}")
        sys.exit(1)
    
    with open(args.catalog, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    entries = data.get("entries", [])
    
    # Collect all URLs
    urls_to_check = []
    for e in entries:
        repo_url = e.get("repository_url")
        if repo_url:
            urls_to_check.append(repo_url)
        hp = e.get("homepage_url")
        if hp:
            urls_to_check.append(hp)
        for su in e.get("source_urls", []):
            urls_to_check.append(su)
    
    # Deduplicate
    urls_to_check = list(set(urls_to_check))
    
    print(f"Checking {len(urls_to_check)} URLs with {args.max_workers} workers...")
    
    results = {"ok": 0, "error": 0, "skipped": 0}
    errors = []
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(check_url, url): url for url in urls_to_check}
        for future in as_completed(futures):
            url, status, error = future.result()
            if status and 200 <= status < 400:
                results["ok"] += 1
            elif status:
                results["error"] += 1
                errors.append((url, status, error))
            else:
                results["error"] += 1
                errors.append((url, None, error))
    
    print(f"\nResults: {results['ok']} OK, {results['error']} errors, {results['skipped']} skipped")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for url, status, reason in errors[:20]:
            status_str = str(status) if status else "NO RESPONSE"
            print(f"  [{status_str}] {url} — {reason}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
    
    return len(errors) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
