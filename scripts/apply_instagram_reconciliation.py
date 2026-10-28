#!/usr/bin/env python3
"""Apply the 2026-10-28 Instagram GitHub research reconciliation to the catalog.

The execution plan file WERKAtlas_v2_Ausfuehrungsplan.md was not in the
repository or on Google Drive. This script uses the public GitHub metadata
checked on 2026-10-28 for the 110 verified repository identities in that
research set.

Original catalog rows are kept. Scores, descriptions, and star counts of
existing rows are not recomputed. License and archived status are filled
only where the catalog value was missing or contradicted by the GitHub API.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.score import (  # noqa: E402
    compute_confidence,
    compute_score_label,
    score_adoption,
    score_community,
    score_documentation,
    score_interoperability,
    score_maintenance,
    score_momentum,
    score_production_readiness,
    score_relevance,
    score_security,
    score_uniqueness,
)
from scripts.validate import validate_schema  # noqa: E402

RESEARCH = ROOT / "research" / "instagram-github-2026-10-28"
CATALOG_PATH = ROOT / "data" / "catalog.json"
SCHEMA_PATH = ROOT / "data" / "catalog.schema.json"
TAXONOMY_PATH = ROOT / "data" / "taxonomy.json"
NDJSON_PATH = ROOT / "data" / "catalog.ndjson"
CSV_PATH = ROOT / "data" / "catalog.csv"
BASELINE_PATH = RESEARCH / "baseline-protected-sha256.json"
PRE_PATCH_PATH = RESEARCH / "pre-patch-fields.json"
REPORT_PATH = RESEARCH / "RECONCILIATION.md"

DISCOVERY_TAG = "instagram-github-research-2026-10-28"
CHECKED_AT = "2026-10-28T12:40:00+00:00"
MUTABLE_FIELDS = (
    "license",
    "archived",
    "maintenance_status",
    "limitations",
    "discovered_from",
)
ARCHIVED_NOTE = "GitHub listed this repository as archived on 2026-10-28."

EXISTING_LIMITATIONS = {
    "anthropics/skills": [
        "The pdf skill license is governed by Anthropic service terms, not an open-source grant. Check each skill's LICENSE.txt before copying it."
    ],
    "upstash/context7": [
        "Hosted documentation service. Provider quotas and data handling need a separate check before production use."
    ],
    "HKUDS/Vibe-Trading": [
        "This is a trading-agent repository. The catalog entry does not assess financial performance or trading risk."
    ],
}


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def word_count(text: str) -> int:
    return len(text.split())


def taxonomy_codes(taxonomy: dict) -> set[str]:
    codes = set()
    for group in taxonomy["categories"].values():
        codes.update(group["subcategories"].keys())
    return codes


def append_unique(items: list, value: str) -> list:
    result = list(items or [])
    if value not in result:
        result.append(value)
    return result


def protected_blob(entry: dict) -> str:
    protected = {key: value for key, value in entry.items() if key not in MUTABLE_FIELDS}
    return json.dumps(protected, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def protected_hash(entry: dict) -> str:
    return hashlib.sha256(protected_blob(entry).encode("utf-8")).hexdigest()


def write_baseline(entries: list[dict]) -> None:
    if BASELINE_PATH.exists():
        return
    payload = {
        "algorithm": "sha256",
        "mutable_fields": list(MUTABLE_FIELDS),
        "source": "data/catalog.json before instagram-github-research-2026-10-28",
        "count": len(entries),
        "ids": [entry["id"] for entry in entries],
        "hashes": {entry["id"]: protected_hash(entry) for entry in entries},
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def spdx_of(meta: dict) -> str | None:
    info = meta.get("licenseInfo") or {}
    spdx = info.get("spdxId")
    if not spdx:
        return None
    return spdx


def topics_of(meta: dict) -> list[str]:
    nodes = ((meta.get("repositoryTopics") or {}).get("nodes")) or []
    names = []
    for node in nodes:
        topic = ((node or {}).get("topic") or {}).get("name")
        if topic:
            names.append(topic)
    return names


def languages_of(meta: dict) -> list[str]:
    edges = ((meta.get("languages") or {}).get("edges")) or []
    names = []
    for edge in edges:
        name = ((edge or {}).get("node") or {}).get("name")
        if name:
            names.append(name)
    return names


def homepage_of(meta: dict) -> str | None:
    homepage = (meta.get("homepageUrl") or "").strip()
    if homepage.startswith("https://") or homepage.startswith("http://"):
        return homepage
    return None


def mentions_mcp(meta: dict) -> bool:
    topics = " ".join(topics_of(meta)).lower()
    description = (meta.get("description") or "").lower()
    blob = f"{topics} {description}"
    return "mcp" in blob or "model context protocol" in blob


def score_entry(entry: dict) -> None:
    parts = [
        score_relevance(entry),
        score_maintenance(entry),
        score_adoption(entry),
        score_momentum(entry),
        score_documentation(entry),
        score_production_readiness(entry),
        score_security(entry),
        score_interoperability(entry),
        score_community(entry),
        score_uniqueness(entry),
    ]
    keys = [
        "relevance",
        "maintenance",
        "adoption",
        "momentum",
        "documentation",
        "production_readiness",
        "security",
        "interoperability",
        "community",
        "uniqueness",
    ]
    components = {}
    explanations = []
    for key, (value, notes) in zip(keys, parts):
        components[key] = value
        explanations.extend(notes)
    total = round(sum(components.values()), 1)
    if total > 100:
        raise SystemExit(f"Score overflow for {entry['id']}: {total}")
    entry["score_components"] = components
    entry["score"] = total
    entry["score_label"] = compute_score_label(total)
    entry["score_explanations"] = explanations
    entry["confidence"] = compute_confidence(entry)


def build_entry(spec: dict, meta: dict) -> dict:
    repo_id = spec["id"]
    owner = repo_id.split("/", 1)[0]
    repository_url = f"https://github.com/{repo_id}"
    primary_language = (meta.get("primaryLanguage") or {}).get("name")
    protocols = ["MCP"] if mentions_mcp(meta) else []
    entry = {
        "id": repo_id,
        "name": spec["name"],
        "owner": owner,
        "repository": repo_id,
        "repository_url": repository_url,
        "homepage_url": homepage_of(meta),
        "description": spec["description"],
        "primary_category": spec["primary_category"],
        "secondary_categories": list(spec.get("secondary_categories") or []),
        "project_type": spec["project_type"],
        "capabilities": [],
        "protocols": protocols,
        "compatible_hosts": [],
        "deployment_modes": list(spec.get("deployment_modes") or []),
        "official_status": spec["official_status"],
        "official_evidence": [repository_url] if spec["official_status"] == "official" else [],
        "primary_language": primary_language,
        "languages": languages_of(meta) or ([primary_language] if primary_language else []),
        "topics": topics_of(meta),
        "license": spdx_of(meta),
        "stars": int(meta["stargazerCount"]),
        "forks": int(meta["forkCount"]),
        "open_issues": int((meta.get("issues") or {}).get("totalCount") or 0),
        "created_at": meta.get("createdAt"),
        "updated_at": meta.get("updatedAt"),
        "pushed_at": meta.get("pushedAt"),
        "latest_release_at": (meta.get("latestRelease") or {}).get("publishedAt"),
        "archived": bool(meta.get("isArchived")),
        "is_fork": bool(meta.get("isFork")),
        "maintenance_status": "archived" if meta.get("isArchived") else "unclear",
        "documentation_quality": 0,
        "production_readiness": 0,
        "security_transparency": 0,
        "trend_data": {"stars_30d": None, "stars_90d": None, "method": None},
        "install_methods": [],
        "security_notes": list(spec.get("security_notes") or []),
        "limitations": list(spec.get("limitations") or []),
        "source_urls": [repository_url],
        "discovered_from": [DISCOVERY_TAG],
        "checked_at": CHECKED_AT,
    }
    if entry["archived"]:
        entry["limitations"] = append_unique(entry["limitations"], ARCHIVED_NOTE)
    score_entry(entry)
    return entry


def patch_existing(entry: dict, meta: dict) -> list[str]:
    changes = []
    spdx = spdx_of(meta)
    if not entry.get("license") and spdx:
        entry["license"] = spdx
        changes.append(f"license {spdx}")
    if meta.get("isArchived") and not entry.get("archived"):
        entry["archived"] = True
        if entry.get("maintenance_status") in (None, "unclear"):
            entry["maintenance_status"] = "archived"
        entry["limitations"] = append_unique(entry.get("limitations") or [], ARCHIVED_NOTE)
        changes.append("archived")
    for note in EXISTING_LIMITATIONS.get(entry["id"], []):
        before = list(entry.get("limitations") or [])
        entry["limitations"] = append_unique(before, note)
        if entry["limitations"] != before:
            changes.append("limitation")
    before_sources = list(entry.get("discovered_from") or [])
    entry["discovered_from"] = append_unique(before_sources, DISCOVERY_TAG)
    if entry["discovered_from"] != before_sources:
        changes.append("discovered_from")
    return changes


def validate_entry(entry: dict, schema: dict, codes: set[str]) -> None:
    errors = validate_schema(entry, schema)
    if errors:
        raise SystemExit(f"{entry['id']}: {errors}")
    count = word_count(entry["description"])
    if not 12 <= count <= 30:
        raise SystemExit(f"{entry['id']} description has {count} words: {entry['description']}")
    for code in [entry["primary_category"], *entry.get("secondary_categories", [])]:
        if code not in codes:
            raise SystemExit(f"{entry['id']} unknown category {code}")
    for mode in entry.get("deployment_modes") or []:
        if mode not in ("local-first", "self-hosted", "cloud", "hybrid"):
            raise SystemExit(f"{entry['id']} bad deployment mode {mode}")


def update_ndjson(by_id: dict[str, dict], added_ids: list[str]) -> None:
    lines = NDJSON_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        return
    key_order = list(json.loads(lines[0]).keys())
    rewritten = []
    for line in lines:
        obj = json.loads(line)
        current = by_id.get(obj["id"])
        if current is not None and obj.get("license") != current.get("license"):
            obj["license"] = current.get("license")
            line = json.dumps(obj, ensure_ascii=False)
        rewritten.append(line)
    for repo_id in added_ids:
        entry = by_id[repo_id]
        shaped = {key: entry.get(key) for key in key_order}
        rewritten.append(json.dumps(shaped, ensure_ascii=False))
    text = "\n".join(rewritten)
    if rewritten:
        text += "\n"
    NDJSON_PATH.write_text(text, encoding="utf-8")


def update_csv(by_id: dict[str, dict], added_ids: list[str]) -> None:
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        current = by_id.get(row["id"])
        if current is not None:
            row["license"] = current.get("license") or ""
    existing_ids = {row["id"] for row in rows}
    for repo_id in added_ids:
        if repo_id in existing_ids:
            continue
        entry = by_id[repo_id]
        rows.append({field: "" if entry.get(field) is None else entry.get(field, "") for field in fieldnames})
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(summary: dict) -> None:
    lines = [
        "# Instagram GitHub research reconciliation",
        "",
        "Checked: 2026-10-28 (GitHub API, no paid model or vendor API).",
        "",
        "`WERKAtlas_v2_Ausfuehrungsplan.md` was not in the repository and not on Google Drive.",
        "The 110 verified repository identities come from the Instagram GitHub Research files",
        "(MASTER-KATALOG, decision report, and a fresh public GitHub read of each repository).",
        "Drive originals were not modified.",
        "",
        "## Result",
        "",
        f"- Verified repository identities: {summary['verified']}",
        f"- Already in the catalog: {summary['already_present']}",
        f"- Added: {summary['added']}",
        f"- Excluded from the catalog, with a reason: {summary['excluded']}",
        f"- License values filled where the catalog had none: {summary['licenses_filled']}",
        f"- Archived flags corrected from GitHub: {summary['archived_corrected']}",
        f"- Catalog entries before / after: {summary['before']} / {summary['after']}",
        "",
        "Existing descriptions, star counts, timestamps, and scores were left as stored.",
        "A later scoring run would move maintenance scores because it uses the current date.",
        "New entries were scored once with `scripts/score.py` on 2026-10-28.",
        "",
        "Protected fields of every pre-existing entry are hashed in",
        "`baseline-protected-sha256.json`. Mutable fields are license, archived,",
        "maintenance_status, limitations, and discovered_from.",
        "",
        "## Excluded",
        "",
    ]
    for repo_id, reason in summary["exclusion_rows"]:
        lines.append(f"- `{repo_id}` — {reason}")
    lines.extend(["", "## Added", ""])
    for repo_id in summary["added_ids"]:
        lines.append(f"- `{repo_id}`")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    catalog = load_json(CATALOG_PATH)
    metadata = load_json(RESEARCH / "github-metadata.json")
    additions = load_json(RESEARCH / "additions.json")
    exclusions = load_json(RESEARCH / "exclusions.json")
    schema = load_json(SCHEMA_PATH)
    codes = taxonomy_codes(load_json(TAXONOMY_PATH))

    if len(metadata) != 110:
        raise SystemExit(f"Expected 110 GitHub metadata records, found {len(metadata)}")

    addition_ids = [item["id"] for item in additions]
    if len(addition_ids) != len(set(addition_ids)):
        raise SystemExit("Duplicate addition ids")
    overlap = set(addition_ids) & set(exclusions)
    if overlap:
        raise SystemExit(f"Addition/exclusion overlap: {sorted(overlap)}")
    present_lower = {entry["id"].lower() for entry in catalog["entries"]}
    missing = sorted(
        repo_id
        for repo_id in metadata
        if repo_id not in addition_ids
        and repo_id not in exclusions
        and repo_id.lower() not in present_lower
    )
    extra = sorted((set(addition_ids) | set(exclusions)) - set(metadata))
    if missing or extra:
        raise SystemExit(f"Decision set does not match metadata. missing={missing} extra={extra}")
    excluded_present = sorted(repo_id for repo_id in exclusions if repo_id.lower() in present_lower)
    if excluded_present:
        raise SystemExit(f"Excluded repository is already in the catalog: {excluded_present}")

    for spec in additions:
        count = word_count(spec["description"])
        if not 12 <= count <= 30:
            raise SystemExit(f"{spec['id']} description has {count} words")
        if spec["id"] not in metadata or metadata[spec["id"]].get("error"):
            raise SystemExit(f"Missing GitHub metadata for {spec['id']}")

    entries = catalog["entries"]
    write_baseline(entries)
    baseline_ids = load_json(BASELINE_PATH)["ids"]
    by_lower = {entry["id"].lower(): entry for entry in entries}
    original_ids = set(baseline_ids)
    original_lower = {entry_id.lower() for entry_id in original_ids}

    licenses_filled = 0
    archived_corrected = 0
    already = 0
    for repo_id, meta in metadata.items():
        existing = by_lower.get(repo_id.lower())
        if existing is None or repo_id.lower() not in original_lower:
            continue
        already += 1
        before_license = existing.get("license")
        before_archived = bool(existing.get("archived"))
        patch_existing(existing, meta)
        if not before_license and existing.get("license"):
            licenses_filled += 1
        if existing.get("archived") and not before_archived:
            archived_corrected += 1

    added_ids = []
    for spec in additions:
        if spec["id"].lower() in by_lower:
            continue
        entry = build_entry(spec, metadata[spec["id"]])
        validate_entry(entry, schema, codes)
        entries.append(entry)
        by_lower[entry["id"].lower()] = entry
        added_ids.append(entry["id"])

    for repo_id in exclusions:
        if repo_id.lower() in {entry_id.lower() for entry_id in original_ids}:
            raise SystemExit(f"Refusing to drop an original catalog entry: {repo_id}")
        if repo_id.lower() in by_lower and repo_id not in original_ids:
            raise SystemExit(f"Excluded repository is present in the catalog: {repo_id}")

    catalog["count"] = len(entries)
    if catalog["count"] != len(by_lower):
        raise SystemExit("Duplicate catalog ids after reconciliation")

    text = json.dumps(catalog, indent=2, ensure_ascii=False)
    CATALOG_PATH.write_text(text, encoding="utf-8")

    by_id = {entry["id"]: entry for entry in entries}
    update_ndjson(by_id, added_ids)
    update_csv(by_id, added_ids)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_search_index.py")],
        cwd=ROOT,
        check=True,
    )

    pre_patch = load_json(PRE_PATCH_PATH) if PRE_PATCH_PATH.exists() else {}
    final_by_id = {entry["id"]: entry for entry in entries}
    if pre_patch:
        licenses_filled = sum(
            1
            for entry_id, previous in pre_patch.items()
            if not previous.get("license") and final_by_id[entry_id].get("license")
        )
        archived_corrected = sum(
            1
            for entry_id, previous in pre_patch.items()
            if final_by_id[entry_id].get("archived") and not previous.get("archived")
        )
    write_report(
        {
            "verified": len(metadata),
            "already_present": len(pre_patch) or already,
            "added": len(addition_ids),
            "excluded": len(exclusions),
            "licenses_filled": licenses_filled,
            "archived_corrected": archived_corrected,
            "before": len(original_ids),
            "after": len(entries),
            "exclusion_rows": sorted(exclusions.items()),
            "added_ids": addition_ids,
        }
    )
    print(
        f"Reconciled {len(metadata)} repos: "
        f"{already} existing, {len(added_ids)} added this run, {len(exclusions)} excluded. "
        f"Catalog {len(original_ids)} -> {len(entries)}."
    )


if __name__ == "__main__":
    main()
