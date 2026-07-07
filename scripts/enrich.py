#!/usr/bin/env python3
"""
enrich.py — LOOP 2: Metadata enrichment for candidate projects.

Fetches detailed repository metadata and normalizes records.

Usage:
    python scripts/enrich.py --candidates data/candidates.ndjson --catalog data/catalog.json
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


BASE_URL = "https://api.github.com"
USER_AGENT = "agentic-engineering-compendium/1.0"
REQUEST_DELAY = 2.0
MAX_RETRIES = 3
SNAPSHOT_DATE = "2026-07-07"


class RateLimiter:
    def __init__(self):
        self.remaining = 60
        self.reset_time = 0
        self.last_request = 0.0
    
    def wait(self):
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()
    
    def update_from_headers(self, headers):
        remaining = headers.get("X-RateLimit-Remaining")
        if remaining is not None:
            self.remaining = int(remaining)
        reset = headers.get("X-RateLimit-Reset")
        if reset is not None:
            self.reset_time = int(reset)
    
    def check_limit(self):
        if self.remaining <= 2:
            wait_time = max(self.reset_time - time.time(), 0) + 5
            if wait_time > 0 and wait_time < 3600:
                print(f"  Rate limit near: waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                return True
        return False


rate_limiter = RateLimiter()


def github_request(url: str) -> dict | None:
    rate_limiter.wait()
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                rate_limiter.update_from_headers(resp.headers)
                return {"data": json.loads(resp.read().decode())}
        except urllib.error.HTTPError as e:
            if e.code == 403 and rate_limiter.remaining == 0:
                rate_limiter.update_from_headers(e.headers)
                wait_time = max(rate_limiter.reset_time - time.time(), 0) + 10
                print(f"  Rate limited. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                continue
            elif e.code == 404:
                return None
            elif e.code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            else:
                print(f"  HTTP {e.code} on {url}: {e.reason}")
                return None
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  Network error: {e}")
            time.sleep(5 * (attempt + 1))
            continue
    return None


def fetch_repo_details(owner: str, repo: str) -> dict | None:
    """Fetch full repository details including topics."""
    url = f"{BASE_URL}/repos/{owner}/{repo}"
    return github_request(url)


def fetch_repo_languages(owner: str, repo: str) -> dict | None:
    """Fetch repository languages."""
    url = f"{BASE_URL}/repos/{owner}/{repo}/languages"
    return github_request(url)


def fetch_latest_release(owner: str, repo: str) -> dict | None:
    """Fetch latest release."""
    url = f"{BASE_URL}/repos/{owner}/{repo}/releases/latest"
    return github_request(url)


def main():
    parser = argparse.ArgumentParser(description="Enrich candidate metadata")
    parser.add_argument("--candidates", default="data/candidates.ndjson")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--limit", type=int, default=None, help="Max repos to enrich")
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.catalog) or ".", exist_ok=True)
    
    print("=" * 60)
    print("Agentic Engineering Compendium — Metadata Enrichment (LOOP 2)")
    print(f"Snapshot date: {SNAPSHOT_DATE}")
    print("=" * 60)
    
    # Load candidates
    if not os.path.exists(args.candidates):
        print(f"Candidates file not found: {args.candidates}")
        sys.exit(1)
    
    candidates = []
    with open(args.candidates, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    candidates.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    print(f"Loaded {len(candidates)} candidates")
    
    if args.limit:
        candidates = candidates[:args.limit]
    
    # Process each candidate
    enriched = []
    skipped = 0
    
    for i, candidate in enumerate(candidates):
        owner = candidate.get("owner", "")
        repo = candidate.get("name", "")
        repo_id = candidate.get("id", "")
        
        if not owner or not repo:
            skipped += 1
            continue
        
        print(f"[{i+1}/{len(candidates)}] Enriching {repo_id}...")
        
        # Fetch full details
        details = fetch_repo_details(owner, repo)
        if details is None:
            print(f"  Skipping {repo_id}: not found")
            skipped += 1
            continue
        
        item = details["data"]
        
        # Fetch languages
        lang_result = fetch_repo_languages(owner, repo)
        languages = list(lang_result["data"].keys()) if lang_result and lang_result.get("data") else []
        
        # Fetch latest release
        release_result = fetch_latest_release(owner, repo)
        latest_release = None
        if release_result and release_result.get("data"):
            latest_release = release_result["data"].get("published_at")
        
        # Build enriched record
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": item.get("full_name", repo_id),
            "name": item.get("name", repo),
            "owner": item.get("owner", {}).get("login", owner),
            "repository": item.get("full_name", repo_id),
            "repository_url": item.get("html_url", f"https://github.com/{repo_id}"),
            "homepage_url": item.get("homepage"),
            "description": candidate.get("description") or item.get("description"),
            "primary_category": candidate.get("primary_category"),
            "secondary_categories": candidate.get("secondary_categories", []),
            "project_type": candidate.get("project_type"),
            "capabilities": [],
            "protocols": [],
            "compatible_hosts": [],
            "deployment_modes": [],
            "official_status": "unclear",
            "official_evidence": [],
            "primary_language": item.get("language"),
            "languages": languages,
            "topics": item.get("topics", []),
            "license": item.get("license", {}).get("spdx_id") if item.get("license") else None,
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "open_issues": item.get("open_issues_count", 0),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "pushed_at": item.get("pushed_at"),
            "latest_release_at": latest_release,
            "archived": item.get("archived", False),
            "is_fork": item.get("fork", False),
            "maintenance_status": "archived" if item.get("archived") else "unclear",
            "documentation_quality": 0,
            "production_readiness": 0,
            "security_transparency": 0,
            "score_components": {
                "relevance": 0,
                "maintenance": 0,
                "adoption": 0,
                "momentum": 0,
                "documentation": 0,
                "production_readiness": 0,
                "security": 0,
                "interoperability": 0,
                "community": 0,
                "uniqueness": 0,
            },
            "score": 0,
            "confidence": "low",
            "trend_data": {
                "stars_30d": None,
                "stars_90d": None,
                "method": None,
            },
            "install_methods": [],
            "security_notes": [],
            "limitations": [],
            "source_urls": [item.get("html_url", f"https://github.com/{repo_id}")],
            "discovered_from": candidate.get("discovered_from", []),
            "checked_at": now,
        }
        
        enriched.append(record)
        rate_limiter.check_limit()
    
    # Write catalog
    print(f"\nWriting {len(enriched)} enriched records to {args.catalog}...")
    with open(args.catalog, "w", encoding="utf-8") as f:
        json.dump({
            "snapshot_date": SNAPSHOT_DATE,
            "count": len(enriched),
            "schema_version": "1.0",
            "entries": enriched,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Enrichment complete!")
    print(f"  Enriched: {len(enriched)}")
    print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    main()
