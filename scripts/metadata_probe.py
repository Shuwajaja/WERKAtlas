#!/usr/bin/env python3
"""Read-only GitHub metadata sampler for WERKAtlas. NEVER edits data/catalog.json.

It obtains facts directly from the official GitHub REST API; missing/NOASSERTION
license stays unknown. Reports are dated and can be reviewed as separate PRs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("stars", "forks", "archived", "pushed_at", "license")
AGENT = "WERKAtlas-local-readonly/1.0"


def license_id(repository: dict) -> str | None:
    value = repository.get("license")
    if not isinstance(value, dict):
        return None
    spdx = value.get("spdx_id")
    return spdx if isinstance(spdx, str) and spdx and spdx.upper() not in {"NOASSERTION", "NONE"} else None


def proposed_change(entry: dict, repository: dict, checked_at: str) -> dict:
    # Validate identity before trusting the remote response.
    if repository.get("full_name", "").casefold() != entry["id"].casefold():
        raise ValueError("Repository identity mismatch")
    facts = {
        "stars": repository.get("stargazers_count"),
        "forks": repository.get("forks_count"),
        "archived": repository.get("archived"),
        "pushed_at": repository.get("pushed_at"),
        "license": license_id(repository),
    }
    changes = {}
    unresolved = []
    for field in FIELDS:
        value = facts[field]
        valid = isinstance(value, bool) if field == "archived" else (
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            if field in {"stars", "forks"} else isinstance(value, str) and bool(value.strip())
        )
        if not valid:
            unresolved.append(field)
            continue
        old = entry.get(field)
        if old != value:
            changes[field] = {"before": old, "after": value}
    return {
        "id": entry["id"],
        "source": f"https://api.github.com/repos/{urllib.parse.quote(entry['id'], safe='/')}",
        "checked_at": checked_at,
        "proposed_changes": changes,
        "verified_facts": {key: value for key, value in facts.items() if key not in unresolved},
        "unknown_remote": unresolved,
        "license_current_status": "verified_spdx" if facts["license"] else "unknown",
        "review_required": True,
    }


def fetch_metadata(project_id: str, *, token: str | None = None) -> dict:
    url = "https://api.github.com/repos/" + urllib.parse.quote(project_id, safe="/")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": AGENT}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=12) as response:
        if response.status != 200:
            raise RuntimeError(f"GitHub HTTP {response.status}")
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected GitHub response type")
    return payload


def _priority(entry: dict) -> tuple:
    score = entry.get("score")
    stars = entry.get("stars")
    return (-(score if isinstance(score, (int, float)) else -1),
            -(stars if isinstance(stars, int) else -1), entry.get("id", ""))


def sample_catalog(catalog: dict, *, limit: int = 10, offset: int = 0, fetch=fetch_metadata,
                   checked_at: str | None = None, delay: float = 0.0) -> dict:
    if not 1 <= limit <= 50 or offset < 0:
        raise ValueError("limit must be 1..50 and offset >= 0")
    checked_at = checked_at or datetime.now(timezone.utc).isoformat()
    chosen = sorted((e for e in catalog.get("entries", [])
                     if e.get("id") and (not e.get("license") or
                         str(e.get("license")).upper() in {"NOASSERTION", "NONE"} or
                         e.get("maintenance_status") in {"unclear", None})),
                    key=_priority)[offset:offset+limit]
    results = []
    for entry in chosen:
        try:
            remote = fetch(entry["id"])
            report = proposed_change(entry, remote, checked_at)
            report["status"] = "ok"
        except (OSError, ValueError, RuntimeError, urllib.error.HTTPError) as exc:
            # No fabricated data on rate limit, deletion or network failure.
            report = {"id": entry["id"], "status": "unavailable", "error_type": type(exc).__name__,
                      "review_required": True}
        results.append(report)
        if delay:
            time.sleep(delay)
    return {
        "checked_at": checked_at,
        "fetched": sum(x["status"] == "ok" for x in results),
        "requested": len(chosen),
        "results": results,
        "note": "Read-only official GitHub facts. Existing scores and descriptions are untouched.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Review-only official GitHub metadata sampling")
    parser.add_argument("--catalog", default=str(ROOT / "data" / "catalog.json"))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--output", required=True)
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args(argv)
    try:
        input_path = Path(args.catalog)
        catalog = json.loads(input_path.read_text(encoding="utf-8-sig"))
        output = Path(args.output).resolve()
        if output.exists():
            raise ValueError("Refuse to overwrite existing metadata report")
        if input_path.resolve() == output:
            raise ValueError("Refuse to write canonical catalog")
        report = sample_catalog(catalog, limit=args.limit, offset=args.offset,
                                fetch=lambda name: fetch_metadata(name, token=os.environ.get("GITHUB_TOKEN")),
                                delay=max(0.0, args.delay))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"GitHub metadata proposals: {report['fetched']}/{report['requested']} verified responses -> {output}")
        return 0 if report["fetched"] == report["requested"] else 2
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
