#!/usr/bin/env python3
"""Report one GitHub metadata diff. This script never writes the catalog.

Usage:
    python scripts/refresh_github_report.py --id owner/name --catalog data/catalog.json --github repo.json
    python scripts/refresh_github_report.py --id owner/name --catalog data/catalog.json --fetch
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

GRAPHQL = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    stargazerCount
    forkCount
    isArchived
    pushedAt
    licenseInfo { spdxId }
  }
}
"""


def build_refresh_report(entry: dict, github: dict) -> dict:
    changes: dict[str, dict] = {}
    unchanged: list[str] = []
    skipped: list[str] = []

    _compare_value(changes, unchanged, skipped, "stars", entry.get("stars"), _int_value(github.get("stargazerCount")))
    _compare_value(changes, unchanged, skipped, "forks", entry.get("forks"), _int_value(github.get("forkCount")))
    archived = github.get("isArchived")
    _compare_value(
        changes,
        unchanged,
        skipped,
        "archived",
        entry.get("archived"),
        archived if isinstance(archived, bool) else None,
    )
    pushed = github.get("pushedAt")
    _compare_value(
        changes,
        unchanged,
        skipped,
        "pushed_at",
        entry.get("pushed_at"),
        pushed if isinstance(pushed, str) and pushed else None,
    )
    _compare_license(changes, unchanged, skipped, entry.get("license"), _spdx(github))
    return {
        "id": entry.get("id"),
        "changes": changes,
        "unchanged": unchanged,
        "skipped_unknown": skipped,
    }


def _compare_value(changes, unchanged, skipped, field, old, new) -> None:
    if new is None:
        skipped.append(field)
        return
    if old != new:
        changes[field] = {"from": old, "to": new}
        return
    unchanged.append(field)


def _compare_license(changes, unchanged, skipped, old, spdx) -> None:
    if old:
        if spdx == old:
            unchanged.append("license")
        return
    if spdx:
        changes["license"] = {"from": old, "to": spdx}
        return
    skipped.append("license")


def _int_value(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _spdx(github: dict) -> str | None:
    info = github.get("licenseInfo")
    if not isinstance(info, dict):
        return None
    spdx = info.get("spdxId")
    if not isinstance(spdx, str) or not spdx or spdx == "NOASSERTION":
        return None
    return spdx


def _split_id(project_id: str) -> tuple[str, str]:
    owner, _, name = project_id.partition("/")
    if not owner or not name or "/" in name:
        raise ValueError(f"id must be owner/name: {project_id}")
    return owner, name


def fetch_github(project_id: str) -> dict:
    owner, name = _split_id(project_id)
    completed = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={GRAPHQL}",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "gh api graphql failed")
    payload = json.loads(completed.stdout)
    repository = (payload.get("data") or {}).get("repository")
    if not isinstance(repository, dict):
        raise RuntimeError(f"GitHub returned no repository for {project_id}")
    return repository


def _load(path: str) -> dict:
    with Path(path).open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report one GitHub metadata diff")
    parser.add_argument("--id", required=True)
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--github", help="Path to a GitHub repository JSON object")
    parser.add_argument("--fetch", action="store_true", help="Read one repository with gh api")
    args = parser.parse_args(argv)
    try:
        _split_id(args.id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    catalog = _load(args.catalog)
    entries = catalog.get("entries", [])
    entry = next((item for item in entries if item.get("id") == args.id), None)
    if entry is None:
        print(f"unknown project: {args.id}", file=sys.stderr)
        return 1
    if args.github:
        github = _load(args.github)
    elif args.fetch:
        try:
            github = fetch_github(args.id)
        except (RuntimeError, json.JSONDecodeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        print("pass --github or --fetch", file=sys.stderr)
        return 1
    json.dump(build_refresh_report(entry, github), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
