#!/usr/bin/env python3
"""Read-only audit of the WERKAtlas catalog.

Hard errors exit 1. Soft findings are counted and do not fail the run.
Missing model fields stay unknown; this script never fills them.

Usage:
    python scripts/audit_catalog.py \
        --catalog data/catalog.json \
        --schema data/catalog.schema.json \
        --taxonomy data/taxonomy.json \
        --as-of 2026-10-28
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

FUTURE_FIELDS = (
    "agent_type",
    "unique_features",
    "cost",
    "integration_type",
    "system_fit",
    "verification",
)

SOFT_KEYS = (
    "license_missing",
    "maintenance_unclear",
    "description_under_12_words",
    "description_over_30_words",
    "checked_at_stale",
    "source_urls_missing",
    "discovered_from_missing",
    *(f"unknown_{field}" for field in FUTURE_FIELDS),
)

SCORE_TOLERANCE = 0.2
OFFICIAL_STATUS = {"official", "community", "unclear"}
CONFIDENCE = {"high", "medium", "low"}


def parse_timestamp(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    if len(text) == 10:
        parsed = datetime.fromisoformat(text).replace(tzinfo=timezone.utc)
    else:
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def taxonomy_ids(taxonomy: dict) -> set[str]:
    found: set[str] = set()
    for group in taxonomy.get("categories", {}).values():
        found.update(group.get("subcategories", {}))
    return found


def _entries(catalog: dict | list) -> tuple[list, int | None]:
    if isinstance(catalog, list):
        return catalog, None
    entries = catalog.get("entries", [])
    declared = catalog.get("count")
    if not isinstance(declared, int):
        declared = None
    return entries, declared


def _present(value: object) -> bool:
    return value not in (None, "", [], {})


def audit_catalog(
    catalog: dict | list,
    schema: dict,
    taxonomy: dict,
    *,
    as_of: datetime,
    stale_days: int = 90,
) -> dict:
    entries, declared = _entries(catalog)
    required = schema.get("required", [])
    project_types = set(
        schema.get("properties", {}).get("project_type", {}).get("enum", [])
    )
    known_categories = taxonomy_ids(taxonomy)
    hard: list[str] = []
    soft: Counter[str] = Counter()
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    if declared is not None and declared != len(entries):
        hard.append(f"count {declared} does not match len(entries) {len(entries)}")

    seen_ids: dict[str, int] = {}
    seen_lower: dict[str, str] = {}
    seen_repos: dict[str, int] = {}

    for index, entry in enumerate(entries):
        eid = entry.get("id")
        label = eid or entry.get("repository") or f"entry-{index}"
        valid_id = (
            isinstance(eid, str)
            and eid.count("/") == 1
            and all(part != "" for part in eid.split("/"))
        )
        if not valid_id:
            hard.append(f"{label}: id must be owner/name with one slash")
        else:
            if eid in seen_ids:
                hard.append(f"{eid}: duplicate id")
            else:
                seen_ids[eid] = index
                lowered = eid.lower()
                previous = seen_lower.get(lowered)
                if previous is not None and previous != eid:
                    hard.append(
                        f"{eid}: case-insensitive id collision with {previous}"
                    )
                else:
                    seen_lower[lowered] = eid
            owner = eid.split("/", 1)[0]
            if entry.get("owner") != owner:
                hard.append(
                    f"{eid}: owner {entry.get('owner')!r} does not match id prefix {owner!r}"
                )
            expected_url = f"https://github.com/{eid}"
            if entry.get("repository_url") != expected_url:
                hard.append(f"{eid}: repository_url must be {expected_url}")

        repository = entry.get("repository")
        if isinstance(repository, str):
            if repository in seen_repos:
                hard.append(f"{label}: duplicate repository {repository}")
            else:
                seen_repos[repository] = index
            if isinstance(eid, str) and repository != eid:
                hard.append(f"{label}: id {eid} does not match repository {repository}")
        else:
            hard.append(f"{label}: repository is missing")

        for field in required:
            if entry.get(field) in (None, ""):
                hard.append(f"{label}: missing required field {field}")

        project_type = entry.get("project_type")
        if project_type is not None and project_types and project_type not in project_types:
            hard.append(f"{label}: invalid project_type {project_type}")

        category = entry.get("primary_category")
        if isinstance(category, str) and category not in known_categories:
            hard.append(f"{label}: primary_category {category} is not in taxonomy")

        status = entry.get("official_status")
        if status is not None and status not in OFFICIAL_STATUS:
            hard.append(f"{label}: invalid official_status {status}")

        confidence = entry.get("confidence")
        if confidence is not None and confidence not in CONFIDENCE:
            hard.append(f"{label}: invalid confidence {confidence}")

        score = entry.get("score")
        if score is not None:
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                hard.append(f"{label}: score is not a number")
            else:
                if score < 0 or score > 100:
                    hard.append(f"{label}: score {score} outside 0..100")
                components = entry.get("score_components")
                if isinstance(components, dict) and components:
                    try:
                        total = sum(float(value) for value in components.values())
                    except (TypeError, ValueError):
                        hard.append(f"{label}: score_components are not numeric")
                    else:
                        if abs(float(score) - total) > SCORE_TOLERANCE:
                            hard.append(
                                f"{label}: score {score} differs from component sum {total} "
                                f"by more than {SCORE_TOLERANCE}"
                            )

        stars = entry.get("stars")
        if stars is not None and (
            isinstance(stars, bool) or not isinstance(stars, int) or stars < 0
        ):
            hard.append(f"{label}: stars must be a non-negative integer")

        if not _present(entry.get("license")):
            soft["license_missing"] += 1
        if entry.get("maintenance_status") == "unclear":
            soft["maintenance_unclear"] += 1
        word_count = len((entry.get("description") or "").split())
        if word_count < 12:
            soft["description_under_12_words"] += 1
        if word_count > 30:
            soft["description_over_30_words"] += 1
        if not _present(entry.get("source_urls")):
            soft["source_urls_missing"] += 1
        if not _present(entry.get("discovered_from")):
            soft["discovered_from_missing"] += 1

        checked_at = entry.get("checked_at")
        if isinstance(checked_at, str) and checked_at:
            try:
                stamp = parse_timestamp(checked_at)
            except ValueError:
                hard.append(f"{label}: checked_at is not ISO-8601")
            else:
                if (as_of - stamp).days > stale_days:
                    soft["checked_at_stale"] += 1

        for field in FUTURE_FIELDS:
            if not _present(entry.get(field)):
                soft[f"unknown_{field}"] += 1

    soft_findings = {key: int(soft.get(key, 0)) for key in SOFT_KEYS}
    return {
        "entry_count": len(entries),
        "declared_count": declared,
        "hard_errors": hard,
        "soft_findings": soft_findings,
        "passed": not hard,
    }


def _load(path: str) -> dict | list:
    file_path = Path(path)
    with file_path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only WERKAtlas catalog audit")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--schema", default="data/catalog.schema.json")
    parser.add_argument("--taxonomy", default="data/taxonomy.json")
    parser.add_argument("--as-of", default="2026-10-28")
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--report", help="Write the JSON report to this path")
    args = parser.parse_args(argv)

    report = audit_catalog(
        _load(args.catalog),
        _load(args.schema),
        _load(args.taxonomy),
        as_of=parse_timestamp(args.as_of),
        stale_days=args.stale_days,
    )
    print(f"entries: {report['entry_count']}")
    print(f"declared_count: {report['declared_count']}")
    print(f"hard errors: {len(report['hard_errors'])}")
    for error in report["hard_errors"]:
        print(f"  {error}")
    print("soft findings:")
    for key, value in report["soft_findings"].items():
        print(f"  {key}: {value}")
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"report: {report_path}")
    if report["passed"]:
        print("AUDIT PASSED")
        return 0
    print("AUDIT FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
