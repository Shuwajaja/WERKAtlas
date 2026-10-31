#!/usr/bin/env python3
"""Read-only WERKAtlas workflow CLI. No GitHub Actions, no catalog modifications.

Usage:
    python scripts/local_workflow.py verify
    python scripts/local_workflow.py recommend --query "voice sip" --require-all
    python scripts/local_workflow.py backlog --limit 15 --output research/my-report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp"))
sys.path.insert(0, str(ROOT / "scripts"))
from recommend import recommend_projects  # noqa: E402
from metadata_backlog import build_backlog  # noqa: E402


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _dump(data: dict, output: str | None) -> None:
    contents = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output is None:
        sys.stdout.write(contents)
        return
    destination = Path(output).resolve()
    if destination.exists():
        raise ValueError(f"Refusing to overwrite existing report: {destination}")
    if destination.is_relative_to(ROOT / "data"):
        raise ValueError("Reports must not write into the canonical data directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(contents, encoding="utf-8")
    print(f"Report created: {destination}", file=sys.stderr)


def find_projects(entries: list[dict], query: str, *, require_all: bool = False,
                  license: str | None = None, language: str | None = None,
                  limit: int = 10) -> dict:
    if not 1 <= limit <= 50:
        raise ValueError("limit must be 1..50")
    # Filter after ranking; ask for at most 50 lexical candidates, never invent missing evidence.
    candidates = recommend_projects(entries, query, limit=50, license=license, language=language)
    found = [r for r in candidates if not (require_all and r["unmatched_terms"])][:limit]
    return {
        "query": query,
        "require_all_terms": require_all,
        "count": len(found),
        "results": found,
        "note": "Lexical catalog evidence only; not a live GitHub verification.",
    }


def _catalog(args: argparse.Namespace) -> Path:
    path = Path(args.catalog).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _verify(args: argparse.Namespace) -> int:
    catalog = _catalog(args)
    before = _fingerprint(catalog)
    # These checks must remain strictly read-only; never call render/export/score/enrich.
    jobs = [
        [sys.executable, "scripts/validate.py", "--catalog", str(catalog),
         "--schema", "data/catalog.schema.json"],
        [sys.executable, "scripts/audit_catalog.py", "--catalog", str(catalog),
         "--schema", "data/catalog.schema.json", "--taxonomy", "data/taxonomy.json",
         "--as-of", datetime.now(timezone.utc).date().isoformat()],
    ]
    if not args.skip_tests:
        jobs.append([sys.executable, "-m", "pytest", "tests", "-q"])
    try:
        for job in jobs:
            print("RUN:", " ".join(job), file=sys.stderr)
            result = subprocess.run(job, cwd=ROOT, check=False)
            if result.returncode != 0:
                return result.returncode
        return 0
    finally:
        if _fingerprint(catalog) != before:
            raise RuntimeError("Catalog changed during read-only verification!")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WERKAtlas local, read-only workflow (no GitHub Actions)")
    parser.add_argument("--catalog", default=str(ROOT / "data" / "catalog.json"))
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="Validate, audit and run tests without writing catalog")
    verify.add_argument("--skip-tests", action="store_true")
    find = commands.add_parser("recommend", help="Search catalog with optional all-keywords requirement")
    find.add_argument("--query", required=True)
    find.add_argument("--require-all", action="store_true")
    find.add_argument("--license")
    find.add_argument("--language")
    find.add_argument("--limit", type=int, default=10)
    find.add_argument("--output")
    backlog = commands.add_parser("backlog", help="Produce evidence-review queue, never edit catalog")
    backlog.add_argument("--limit", type=int, default=20)
    backlog.add_argument("--stale-days", type=int, default=90)
    backlog.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            return _verify(args)
        catalog = _catalog(args)
        before = _fingerprint(catalog)
        data = _read_json(catalog)
        if args.command == "recommend":
            result = find_projects(data["entries"], args.query, require_all=args.require_all,
                                   license=args.license, language=args.language, limit=args.limit)
        else:
            if not 1 <= args.limit <= 500:
                raise ValueError("backlog limit must be 1..500")
            result = build_backlog(data, as_of=datetime.now(timezone.utc),
                                   limit=args.limit, stale_days=args.stale_days)
        _dump(result, args.output)
        if _fingerprint(catalog) != before:
            raise RuntimeError("Catalog modified unexpectedly")
        return 0
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
