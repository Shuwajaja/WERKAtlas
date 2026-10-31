"""Evidence-aware, read-only lexical discovery of existing WERKAtlas entries.

This deliberately does not claim semantic understanding or evaluate software quality.
Missing information is surfaced as unknown and never treated as a positive signal.
"""

from __future__ import annotations

import re
import unicodedata

STOP = frozenset({
    "a", "an", "and", "are", "der", "die", "das", "ein", "eine", "einen",
    "find", "finde", "for", "für", "ich", "in", "ist", "mit", "of",
    "or", "oder", "please", "project", "projects", "projekt", "projekte",
    "search", "suche", "the", "to", "und", "was", "welche", "what",
})
ALIASES = {
    "telefon": ("phone", "telephony", "calling", "call", "sip", "pstn", "telefon"),
    "telefonagent": ("voice", "phone", "calling", "sip", "agent"),
    "telefonanbindung": ("phone", "telephony", "sip", "pstn", "calling"),
    "voice": ("voice", "speech", "audio"),
    "sprachagent": ("voice", "speech", "audio", "agent"),
    "selbsthostbar": ("self-host", "selfhost", "self hosted", "on-prem", "docker"),
    "selfhost": ("self-host", "selfhost", "self hosted", "on-prem", "docker"),
}
SEARCHABLE = (
    ("name", 5),
    ("id", 4),
    ("description", 3),
    ("capabilities", 3),
    ("topics", 2),
    ("project_type", 2),
    ("protocols", 2),
)


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _terms(query: str) -> list[str]:
    return list(dict.fromkeys(
        part for part in re.findall(r"[^\W_]+", _normalize(query)[:300])
        if len(part) > 1 and part not in STOP
    ))[:16]


def _values(entry: dict, field: str) -> str:
    value = entry.get(field)
    if isinstance(value, list):
        return " ".join(str(part) for part in value if isinstance(part, str))
    return str(value or "")


def recommend_projects(
    entries: list[dict],
    query: str,
    *,
    limit: int = 10,
    license: str | None = None,
    language: str | None = None,
    project_type: str | None = None,
    min_score: float | None = None,
    include_archived: bool = False,
) -> list[dict]:
    """Return lexical matches with evidence; leave unknown metadata explicitly unknown."""
    terms = _terms(query)
    if not terms:
        return []
    limit = max(1, min(int(limit), 50))
    results: list[dict] = []

    for entry in entries:
        if not include_archived and entry.get("archived") is True:
            continue
        if license and _normalize(entry.get("license")) != _normalize(license):
            continue
        if project_type and _normalize(entry.get("project_type")) != _normalize(project_type):
            continue
        languages = entry.get("languages") or []
        langs = [entry.get("primary_language"), *languages] if isinstance(languages, list) else [entry.get("primary_language")]
        if language and not any(_normalize(item) == _normalize(language) for item in langs):
            continue
        score = entry.get("score")
        if min_score is not None and (not isinstance(score, (int, float)) or score < min_score):
            continue

        matched: list[str] = []
        evidence_fields: dict[str, list[str]] = {}
        relevance = 0
        for term in terms:
            variants = ALIASES.get(term, (term,))
            hits = [
                (field, weight)
                for field, weight in SEARCHABLE
                if any(alias in _normalize(_values(entry, field)) for alias in variants)
            ]
            if hits:
                matched.append(term)
                strongest = max(hits, key=lambda x: x[1])
                relevance += strongest[1]
                evidence_fields[term] = [field for field, _ in hits]
        if not matched:
            continue

        results.append({
            "id": entry.get("id"),
            "name": entry.get("name"),
            "repository_url": entry.get("repository_url"),
            "description": entry.get("description"),
            "primary_category": entry.get("primary_category"),
            "project_type": entry.get("project_type"),
            "score": score,
            "license": entry.get("license"),
            "primary_language": entry.get("primary_language"),
            "archived": entry.get("archived"),
            "checked_at": entry.get("checked_at"),
            "matched_terms": matched,
            "unmatched_terms": [term for term in terms if term not in matched],
            "matched_fields": evidence_fields,
            "lexical_relevance": relevance,
            "unknown_fields": [
                field for field in ("license", "checked_at", "maintenance_status")
                if not entry.get(field)
            ],
            "ranking_note": "Lexical match only; catalog scores and dates may be stale.",
        })
    results.sort(
        key=lambda item: (
            -len(item["matched_terms"]), -item["lexical_relevance"],
            -(item["score"] if isinstance(item["score"], (int, float)) else -1),
            str(item["id"]),
        )
    )
    return results[:limit]
