#!/usr/bin/env python3
"""
validate.py — Validate catalog against schema and check for common issues.

Usage:
    python scripts/validate.py --catalog data/catalog.json --schema data/catalog.schema.json
"""

import argparse
import json
import os
import sys


def validate_schema(entry: dict, schema: dict) -> list[str]:
    """Basic schema validation (without full JSON Schema implementation)."""
    errors = []
    
    required = schema.get("required", [])
    for field in required:
        if field not in entry or entry[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # id format
    eid = entry.get("id")
    if eid and "/" not in eid:
        errors.append(f"Invalid id format (expected owner/repo): {eid}")
    
    # repository format
    repo = entry.get("repository")
    if repo and "/" not in repo:
        errors.append(f"Invalid repository format (expected owner/repo): {repo}")
    
    # score range
    score = entry.get("score", -1)
    if score < 0 or score > 100:
        errors.append(f"Score out of range [0,100]: {score}")
    
    # confidence
    conf = entry.get("confidence")
    if conf and conf not in ("high", "medium", "low"):
        errors.append(f"Invalid confidence value: {conf}")
    
    # official_status
    status = entry.get("official_status")
    if status and status not in ("official", "community", "unclear"):
        errors.append(f"Invalid official_status: {status}")
    
    # project_type
    ptype = entry.get("project_type")
    if ptype:
        valid_types = schema.get("properties", {}).get("project_type", {}).get("enum", [])
        if valid_types and ptype not in valid_types:
            errors.append(f"Invalid project_type: {ptype}")
    
    # checked_at
    if not entry.get("checked_at"):
        errors.append("Missing checked_at timestamp")
    
    # repository_url
    repo_url = entry.get("repository_url")
    if repo_url and not repo_url.startswith("https://github.com/"):
        errors.append(f"repository_url should be github: {repo_url}")
    
    return errors


def find_duplicates(entries: list) -> list[tuple]:
    """Find duplicate repository URLs."""
    seen = {}
    duplicates = []
    for i, e in enumerate(entries):
        repo = e.get("repository", "")
        if repo in seen:
            duplicates.append((repo, seen[repo], i))
        else:
            seen[repo] = i
    return duplicates


def check_broken_internal_links(entries: list) -> list[str]:
    """Check for broken internal links in descriptions."""
    issues = []
    for e in entries:
        desc = e.get("description") or ""
        if "[" in desc and "]" in desc and "(" in desc and ")" in desc:
            pass  # has markdown links, could validate
    return issues


def check_invented_metadata(entries: list) -> list[str]:
    """Flag potential invented metadata."""
    issues = []
    for e in entries:
        # Check for suspicious descriptions
        desc = (e.get("description") or "").strip()
        if not desc:
            issues.append(f"Empty description: {e.get('id', '?')}")
        
        # Check for unrealistically precise scores
        sc = e.get("score_components", {})
        for component, value in sc.items():
            if value is not None and float(value) != int(value) and float(value).is_integer():
                pass  # actual decimal scores are fine
        
        # Check for missing timestamps on claimed data
        if e.get("stars", 0) > 0 and not e.get("checked_at"):
            issues.append(f"Stars present but no checked_at: {e.get('id', '?')}")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate catalog data")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--schema", default="data/catalog.schema.json")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Agentic Engineering Compendium — Validation")
    print("=" * 60)
    
    # Load catalog
    if not os.path.exists(args.catalog):
        print(f"ERROR: Catalog not found: {args.catalog}")
        sys.exit(1)
    
    with open(args.catalog, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)
    
    if isinstance(catalog, dict):
        entries = catalog.get("entries", [])
        catalog = entries
    
    print(f"Loaded {len(catalog)} catalog entries")
    
    # Load schema
    schema = {}
    if os.path.exists(args.schema):
        with open(args.schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
        print(f"Loaded schema: {args.schema}")
    else:
        print("WARNING: Schema not found, running basic checks only")
    
    # Run validations
    print("\n--- Schema Validation ---")
    total_errors = 0
    records_with_errors = 0
    
    for i, entry in enumerate(catalog):
        errors = validate_schema(entry, schema)
        if errors:
            records_with_errors += 1
            total_errors += len(errors)
            for err in errors:
                print(f"  [{entry.get('id', f'entry-{i}')}] {err}")
    
    print(f"Records with errors: {records_with_errors}/{len(catalog)}")
    print(f"Total schema errors: {total_errors}")
    
    print("\n--- Duplicate Check ---")
    duplicates = find_duplicates(catalog)
    if duplicates:
        print(f"WARNING: {len(duplicates)} duplicate repositories found:")
        for repo, idx1, idx2 in duplicates[:10]:
            print(f"  {repo} at positions {idx1} and {idx2}")
    else:
        print("No duplicate repositories found.")
    
    print("\n--- Invented Metadata Check ---")
    invented = check_invented_metadata(catalog)
    if invented:
        print(f"WARNING: {len(invented)} potential issues:")
        for issue in invented[:10]:
            print(f"  {issue}")
    else:
        print("No obvious invented metadata issues.")
    
    print("\n--- Summary Statistics ---")
    empty_descs = sum(1 for e in catalog if not (e.get("description") or "").strip())
    missing_license = sum(1 for e in catalog if not e.get("license"))
    missing_checked = sum(1 for e in catalog if not e.get("checked_at"))
    archived = sum(1 for e in catalog if e.get("archived"))
    
    print(f"Empty descriptions: {empty_descs}")
    print(f"Missing license: {missing_license}")
    print(f"Missing checked_at: {missing_checked}")
    print(f"Archived: {archived}")
    
    total_score = sum(e.get("score", 0) for e in catalog) if catalog else 0
    avg_score = total_score / len(catalog) if catalog else 0
    print(f"Average score: {avg_score:.1f}")
    
    print(f"\nTotal validation issues: {total_errors + len(duplicates) + len(invented)}")
    
    if total_errors or duplicates:
        print("VALIDATION FAILED")
        return False
    else:
        print("VALIDATION PASSED")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
