#!/usr/bin/env python3
"""Classify verified GitHub ids against the catalog. Nothing is imported.

Usage:
    python scripts/instagram_id_dry_run.py --catalog data/catalog.json --ids ids.json

ids.json is either ["owner/name", ...] or {"verified_ids": ["owner/name", ...]}.
Objects that carry drive, screenshot, or file_id are refused so private
research links stay out of the report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORBIDDEN_KEYS = {"drive", "screenshot", "file_id"}


def classify_ids(catalog_ids: set[str], verified_ids: list) -> dict:
    present: list[str] = []
    absent: list[str] = []
    invalid: list = []
    duplicate_input: list[str] = []
    seen: set[str] = set()
    for raw in verified_ids:
        if not _valid_id(raw):
            invalid.append(raw)
            continue
        if raw in seen:
            duplicate_input.append(raw)
            continue
        seen.add(raw)
        if raw in catalog_ids:
            present.append(raw)
        else:
            absent.append(raw)
    return {
        "present": present,
        "absent": absent,
        "invalid": invalid,
        "duplicate_input": duplicate_input,
    }


def _valid_id(value: object) -> bool:
    return (
        isinstance(value, str)
        and value.count("/") == 1
        and all(part != "" for part in value.split("/"))
    )


def _ids_from_payload(payload: object) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        leaked = FORBIDDEN_KEYS.intersection(payload)
        if leaked:
            raise PermissionError("refusing private research keys: " + ", ".join(sorted(leaked)))
        ids = payload.get("verified_ids", payload.get("ids"))
        if not isinstance(ids, list):
            raise ValueError("ids payload needs a list or verified_ids")
        return ids
    raise ValueError("ids payload must be a list or an object")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify verified GitHub ids without importing them")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--ids", required=True)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.ids).read_text(encoding="utf-8-sig"))
    try:
        verified = _ids_from_payload(payload)
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8-sig"))
    catalog_ids = {
        entry.get("id")
        for entry in catalog.get("entries", [])
        if isinstance(entry.get("id"), str)
    }
    report = classify_ids(catalog_ids, verified)
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    if report["invalid"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
