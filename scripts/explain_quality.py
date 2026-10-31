#!/usr/bin/env python3
"""Explainable, independent quality and task-fit estimates from *known* Atlas facts.

Missing evidence must lower coverage rather than silently become a zero or a high
score. Unlike the legacy generic score, these are analysis-only projections.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp"))
from recommend import _normalize, _terms, ALIASES  # noqa: E402


def _time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _quality_signals(entry: dict, as_of: datetime) -> list[dict]:
    signals = []
    def signal(name, weight, value, evidence):
        signals.append({"name": name, "weight": weight, "value": value, "evidence": evidence})
    archived = entry.get("archived")
    signal("not_archived", 25, None if archived is None else (0 if archived else 1), "archived")
    pushed = _time(entry.get("pushed_at"))
    if pushed and pushed <= as_of:
        age = (as_of - pushed).days
        signal("maintenance_activity", 30, max(0, 1 - age / 365), "pushed_at")
    else:
        signal("maintenance_activity", 30, None, "pushed_at (unknown/stale source)")
    license = entry.get("license")
    good_license = isinstance(license, str) and license.upper() not in {"", "NONE", "NOASSERTION"}
    # Presence of an SPDX identifier is not proof of commercial rights.
    signal("license_identified", 20, 1 if good_license else None, "license; obligations need review")
    docs = entry.get("homepage_url")
    signal("homepage_declared", 10, 1 if docs else None, "homepage_url")
    source = entry.get("source_urls")
    signal("source_link", 10, 1 if source else None, "source_urls")
    security = entry.get("security_notes")
    signal("security_review", 5, 1 if security else None, "security_notes; not a vulnerability audit")
    return signals


def evaluate(entry: dict, query: str, *, as_of: datetime) -> dict:
    if as_of.tzinfo is None:
        raise ValueError("timezone required")
    signals = _quality_signals(entry, as_of.astimezone(timezone.utc))
    known = [s for s in signals if s["value"] is not None]
    covered = sum(s["weight"] for s in known)
    quality = round(100 * sum(s["value"] * s["weight"] for s in known) / covered, 1) if covered else None
    terms = _terms(query)
    fields = ("name", "description", "topics", "capabilities", "protocols", "project_type")
    haystack = _normalize(" ".join(" ".join(x) if isinstance(x, list) else str(x or "")
                                      for field in fields for x in [entry.get(field)]))
    matches = [term for term in terms
               if any(variant in haystack for variant in ALIASES.get(term, (term,)))]
    fit = round(100 * len(matches) / len(terms), 1) if terms else None
    return {
        "id": entry.get("id"),
        "legacy_score": entry.get("score"),
        "quality_observed_score": quality,
        "quality_coverage_percent": covered,
        "quality_label": "insufficient_evidence" if covered < 70 else "provisional",
        "quality_signals": signals,
        "task_fit_keyword_percent": fit,
        "task_fit_matched": matches,
        "task_fit_unmatched": [x for x in terms if x not in matches],
        "task_fit_warning": "Keyword match, not verified functional compatibility.",
        "as_of": as_of.isoformat(),
        "license_verification": "not_verified",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only separate quality and task-fit explanation")
    parser.add_argument("--catalog", default=str(ROOT / "data/catalog.json"))
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 50:
        parser.error("--limit must be 1..50")
    data = json.loads(Path(args.catalog).read_text(encoding="utf-8-sig"))
    as_of = datetime.now(timezone.utc)
    ranked = [evaluate(e, args.query, as_of=as_of) for e in data["entries"]]
    ranked = [e for e in ranked if e["task_fit_matched"]]
    ranked.sort(key=lambda e: (-len(e["task_fit_matched"]),
                               -e["quality_coverage_percent"], e["id"]))
    report = {"query": args.query, "generated_at": as_of.isoformat(),
              "results": ranked[:args.limit],
              "warning": "Analysis of catalog snapshot only; source and license not independently verified."}
    blob = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = Path(args.output)
        if target.exists():
            parser.error("Refusing to overwrite existing report")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(blob, encoding="utf-8")
        print(f"Created {target}")
    else:
        print(blob)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
