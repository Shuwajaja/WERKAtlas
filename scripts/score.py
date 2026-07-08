#!/usr/bin/env python3
"""
score.py — LOOP 4: Score and rank catalog entries.

Implements the scoring system from METHODOLOGY.md.
Dimensions and maxima (sum = 100):
  Relevance            20
  Maintenance          15
  Adoption             15
  Momentum             10
  Documentation        10
  Production Readiness 10
  Security             10
  Interoperability      5
  Community             3
  Uniqueness            2

Usage:
    python scripts/score.py --input data/catalog.json --output data/catalog.json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log_stars(stars: int) -> float:
    """Logarithmic star score: ln(stars + 1) / ln(100001) * 10."""
    if stars <= 0:
        return 0.0
    return min(10.0, math.log(stars + 1) / math.log(100_001) * 10)


def days_since(iso_str: str | None) -> int | None:
    """Return days elapsed since an ISO-8601 timestamp, or None."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def score_relevance(entry: dict) -> tuple[float, list[dict]]:
    """Score relevance to modern agent engineering (0–20)."""
    explanations: list[dict] = []
    score = 10.0  # baseline for having been curated

    topics = set(t.lower() for t in entry.get("topics", []))
    name = (entry.get("name") or "").lower()
    desc = (entry.get("description") or "").lower()
    project_type = (entry.get("project_type") or "").lower()

    # Agent-specific topic signals — each matched keyword contributes +1,
    # capped at +5 total to prevent inflation.
    agent_keywords = [
        "ai-agent", "llm-agent", "agent-framework", "agent-runtime",
        "agent-orchestration", "agent-sdk", "mcp", "coding-agent",
        "browser-agent", "autonomous-agent", "agent-memory",
        "multi-agent", "agent-swarm", "agent-tool", "agent-skill",
    ]
    keyword_hits = sum(1 for kw in agent_keywords if kw in topics or kw in name or kw in desc)
    kw_bonus = min(5.0, float(keyword_hits))
    if kw_bonus > 0:
        explanations.append({
            "dimension": "relevance", "impact": "positive",
            "text": f"Matched {keyword_hits} agent-ecosystem keyword(s) in topics/name/description."
        })
    score += kw_bonus

    # Project-type bonus (up to +5)
    type_bonus: dict[str, float] = {
        "framework": 5.0, "runtime": 5.0, "protocol": 5.0,
        "mcp server": 5.0, "mcp client": 5.0, "mcp host": 5.0,
        "sdk": 4.0, "evaluation framework": 4.0, "sandbox": 4.0,
        "application": 3.0, "developer tool": 3.0,
        "library": 2.0, "benchmark": 2.0,
    }
    tb = type_bonus.get(project_type, 0.0)
    if tb > 0:
        explanations.append({
            "dimension": "relevance", "impact": "positive",
            "text": f"Project type '{project_type}' is directly relevant to agent engineering."
        })
    score += tb

    final = min(20.0, score)
    if final < 12:
        explanations.append({
            "dimension": "relevance", "impact": "negative",
            "text": "Limited agent-ecosystem signals detected in metadata."
        })
    return round(final, 2), explanations


def score_maintenance(entry: dict) -> tuple[float, list[dict]]:
    """Score maintenance health (0–15)."""
    explanations: list[dict] = []

    if entry.get("archived", False):
        explanations.append({
            "dimension": "maintenance", "impact": "negative",
            "text": "Repository is archived; no active maintenance."
        })
        return 0.0, explanations

    d = days_since(entry.get("pushed_at"))
    if d is None:
        explanations.append({
            "dimension": "maintenance", "impact": "neutral",
            "text": "No push timestamp available; maintenance status unknown."
        })
        return 5.0, explanations

    if d < 7:
        score = 15.0
        explanations.append({"dimension": "maintenance", "impact": "positive", "text": "Repository received commits in the last 7 days."})
    elif d < 30:
        score = 12.0
        explanations.append({"dimension": "maintenance", "impact": "positive", "text": "Repository received commits in the last 30 days."})
    elif d < 90:
        score = 9.0
        explanations.append({"dimension": "maintenance", "impact": "neutral", "text": "Last commit was 30–90 days ago."})
    elif d < 180:
        score = 6.0
        explanations.append({"dimension": "maintenance", "impact": "negative", "text": "Last commit was 90–180 days ago."})
    elif d < 365:
        score = 3.0
        explanations.append({"dimension": "maintenance", "impact": "negative", "text": "Last commit was 180–365 days ago."})
    else:
        score = 1.0
        explanations.append({"dimension": "maintenance", "impact": "negative", "text": "No commits in over a year; maintenance appears stalled."})

    return score, explanations


def score_adoption(entry: dict) -> tuple[float, list[dict]]:
    """Score adoption and ecosystem use (0–15)."""
    explanations: list[dict] = []
    stars = entry.get("stars", 0) or 0
    forks = entry.get("forks", 0) or 0

    # Stars: logarithmic, max 11
    star_score = min(11.0, log_stars(stars) * 1.1)
    # Forks: logarithmic, max 4
    fork_score = min(4.0, math.log(forks + 1) / math.log(10_001) * 4)

    final = min(15.0, star_score + fork_score)

    if stars >= 10_000:
        explanations.append({"dimension": "adoption", "impact": "positive", "text": f"High adoption: {stars:,} stars."})
    elif stars >= 1_000:
        explanations.append({"dimension": "adoption", "impact": "positive", "text": f"Solid adoption: {stars:,} stars."})
    elif stars < 50:
        explanations.append({"dimension": "adoption", "impact": "negative", "text": f"Low adoption signal: fewer than 50 stars."})

    if forks >= 500:
        explanations.append({"dimension": "adoption", "impact": "positive", "text": f"Actively forked: {forks:,} forks."})

    return round(final, 2), explanations


def score_momentum(entry: dict) -> tuple[float, list[dict]]:
    """Score current momentum (0–10)."""
    explanations: list[dict] = []
    score = 2.0  # conservative baseline

    d_push = days_since(entry.get("pushed_at"))
    if d_push is not None:
        if d_push < 7:
            score += 5.0
            explanations.append({"dimension": "momentum", "impact": "positive", "text": "Very recent commit activity (< 7 days)."})
        elif d_push < 30:
            score += 3.0
            explanations.append({"dimension": "momentum", "impact": "positive", "text": "Recent commit activity (< 30 days)."})
        elif d_push < 90:
            score += 1.0

    d_rel = days_since(entry.get("latest_release_at"))
    if d_rel is not None:
        if d_rel < 30:
            score += 3.0
            explanations.append({"dimension": "momentum", "impact": "positive", "text": "New release published in the last 30 days."})
        elif d_rel < 90:
            score += 1.0
            explanations.append({"dimension": "momentum", "impact": "positive", "text": "Release published in the last 90 days."})

    return min(10.0, round(score, 2)), explanations


def score_documentation(entry: dict) -> tuple[float, list[dict]]:
    """Score documentation and onboarding quality (0–10)."""
    explanations: list[dict] = []
    desc = (entry.get("description") or "").strip()
    topics = entry.get("topics", [])
    homepage = entry.get("homepage_url")
    score = 2.0  # baseline for having any description

    if len(desc) > 50:
        score += 2.0
    if len(desc) > 100:
        score += 1.0
        explanations.append({"dimension": "documentation", "impact": "positive", "text": "Description is detailed (> 100 characters)."})
    else:
        explanations.append({"dimension": "documentation", "impact": "negative", "text": "Description is short or missing."})

    if homepage:
        score += 2.0
        explanations.append({"dimension": "documentation", "impact": "positive", "text": "Dedicated homepage or documentation site is linked."})

    if len(topics) >= 5:
        score += 2.0
    elif len(topics) >= 3:
        score += 1.0

    if entry.get("license"):
        score += 1.0

    return min(10.0, round(score, 2)), explanations


def score_production_readiness(entry: dict) -> tuple[float, list[dict]]:
    """Score engineering and production readiness (0–10).

    Signals: release cadence, fork depth, maintenance status, versioning.
    Star count is only a weak proxy here — primary signals are releases and forks.
    """
    explanations: list[dict] = []
    stars = entry.get("stars", 0) or 0
    forks = entry.get("forks", 0) or 0
    score = 2.0  # baseline

    if entry.get("latest_release_at"):
        score += 3.0
        d_rel = days_since(entry.get("latest_release_at"))
        if d_rel is not None and d_rel < 90:
            score += 1.0
            explanations.append({"dimension": "production_readiness", "impact": "positive", "text": "Recent release (< 90 days)."})
        else:
            explanations.append({"dimension": "production_readiness", "impact": "positive", "text": "At least one formal release exists."})
    else:
        explanations.append({"dimension": "production_readiness", "impact": "negative", "text": "No formal release detected."})

    if forks >= 1000:
        score += 2.0
        explanations.append({"dimension": "production_readiness", "impact": "positive", "text": f"Highly forked ({forks:,}), indicating production use."})
    elif forks >= 100:
        score += 1.0

    # Stars as weak readiness signal only at very high thresholds
    if stars >= 10_000:
        score += 1.0

    if entry.get("archived", False):
        score = max(0.0, score - 4.0)
        explanations.append({"dimension": "production_readiness", "impact": "negative", "text": "Repository is archived."})

    return min(10.0, round(score, 2)), explanations


def score_security(entry: dict) -> tuple[float, list[dict]]:
    """Score security and operational transparency (0–10).

    Based on verifiable signals only: security_transparency field (set during enrichment),
    license presence, security notes. Stars are NOT used as a security signal.
    """
    explanations: list[dict] = []
    score = 4.0  # neutral baseline (unknown)

    transparency = entry.get("security_transparency")
    if transparency is not None and isinstance(transparency, (int, float)) and transparency > 0:
        # Enricher-provided signal (0–10 scale from enrich.py)
        score = float(transparency)
        if score >= 7:
            explanations.append({"dimension": "security", "impact": "positive", "text": "Security policy or disclosure process detected."})
        elif score <= 3:
            explanations.append({"dimension": "security", "impact": "negative", "text": "No security documentation found."})
    else:
        explanations.append({"dimension": "security", "impact": "neutral", "text": "Security posture unknown; no enrichment data available."})

    # License as a weak positive signal (open licenses enable security review)
    if entry.get("license"):
        score = min(10.0, score + 1.0)
        explanations.append({"dimension": "security", "impact": "positive", "text": f"Open-source license ({entry['license']}) enables community security review."})
    else:
        score = max(0.0, score - 1.0)
        explanations.append({"dimension": "security", "impact": "negative", "text": "No license declared."})

    # Explicit security warnings reduce score
    notes = entry.get("security_notes", [])
    if notes:
        penalty = min(4.0, len(notes) * 1.5)
        score = max(0.0, score - penalty)
        explanations.append({
            "dimension": "security", "impact": "negative",
            "text": f"{len(notes)} known security concern(s) documented."
        })

    return round(min(10.0, score), 2), explanations


def score_interoperability(entry: dict) -> tuple[float, list[dict]]:
    """Score interoperability and standards support (0–5)."""
    explanations: list[dict] = []
    score = 0.0

    protocols = [p.lower() for p in entry.get("protocols", [])]
    topics = [t.lower() for t in entry.get("topics", [])]

    if "mcp" in protocols or "mcp" in topics or "mcp" in (entry.get("description") or "").lower():
        score += 2.0
        explanations.append({"dimension": "interoperability", "impact": "positive", "text": "Supports the Model Context Protocol (MCP)."})

    if "a2a" in protocols:
        score += 1.0
        explanations.append({"dimension": "interoperability", "impact": "positive", "text": "Supports Agent-to-Agent (A2A) protocol."})

    compatible_hosts = entry.get("compatible_hosts", [])
    if compatible_hosts:
        score += 1.0

    languages = entry.get("languages", [])
    if len(languages) >= 5:
        score += 1.0
        explanations.append({"dimension": "interoperability", "impact": "positive", "text": f"Available in {len(languages)} programming languages."})
    elif len(languages) >= 3:
        score += 0.5

    return min(5.0, round(score, 2)), explanations


def score_community(entry: dict) -> tuple[float, list[dict]]:
    """Score community and governance (0–3).

    Uses forks as the primary signal (forks indicate active downstream use),
    with stars as a secondary signal.
    """
    explanations: list[dict] = []
    forks = entry.get("forks", 0) or 0
    stars = entry.get("stars", 0) or 0
    score = 0.5  # minimal baseline

    if forks >= 2000:
        score += 1.5
        explanations.append({"dimension": "community", "impact": "positive", "text": f"Large community: {forks:,} forks."})
    elif forks >= 500:
        score += 1.0
        explanations.append({"dimension": "community", "impact": "positive", "text": f"Active community: {forks:,} forks."})
    elif forks >= 100:
        score += 0.5

    if stars >= 10_000:
        score += 1.0
    elif stars >= 2_000:
        score += 0.5

    return min(3.0, round(score, 2)), explanations


def score_uniqueness(entry: dict) -> tuple[float, list[dict]]:
    """Score technical uniqueness or educational value (0–2).

    Based on verifiable technical signals:
    - Rare project type (protocol, benchmark, research project, etc.)
    - Protocol support (own protocols or emerging standards)
    - Self-described as reference implementation or novel approach
    - Not derivable from star count alone.
    """
    explanations: list[dict] = []
    score = 0.5  # neutral baseline

    ptype = (entry.get("project_type") or "").lower()
    unique_type_bonus: dict[str, float] = {
        "protocol": 1.5,
        "reference implementation": 1.5,
        "benchmark": 1.0,
        "dataset": 1.0,
        "research project": 1.0,
        "evaluation framework": 1.0,
        "sandbox": 0.5,
        "observability platform": 0.5,
    }
    tb = unique_type_bonus.get(ptype, 0.0)
    if tb > 0:
        score += tb
        explanations.append({
            "dimension": "uniqueness", "impact": "positive",
            "text": f"Project type '{ptype}' represents a rare and specialised niche."
        })

    # Own protocols or emerging standard support
    protocols = entry.get("protocols", [])
    if protocols and len(protocols) >= 1:
        score += 0.5
        explanations.append({"dimension": "uniqueness", "impact": "positive", "text": "Supports at least one interoperability protocol."})

    # Self-described novelty keywords in description (weak signal, capped)
    desc = (entry.get("description") or "").lower()
    novelty_kws = ["novel", "first", "pioneering", "educational", "reference", "experimental", "alternative"]
    if any(kw in desc for kw in novelty_kws):
        score += 0.25

    if score <= 0.5:
        explanations.append({
            "dimension": "uniqueness", "impact": "neutral",
            "text": "No strong differentiation signals detected; using neutral baseline."
        })

    return min(2.0, round(score, 2)), explanations


# ---------------------------------------------------------------------------
# Score label
# ---------------------------------------------------------------------------

SCORE_LABELS = [
    (85.0, "essential"),
    (75.0, "strong"),
    (65.0, "emerging"),
    (50.0, "watchlist"),
    (0.0,  "minimal"),
]

def compute_score_label(score: float) -> str:
    for threshold, label in SCORE_LABELS:
        if score >= threshold:
            return label
    return "minimal"


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------

def compute_confidence(entry: dict) -> str:
    """Compute evidence confidence level based on metadata completeness."""
    points = sum([
        bool(entry.get("repository_url")),
        bool(entry.get("license")),
        (entry.get("stars", 0) or 0) > 0,
        (entry.get("forks", 0) or 0) > 0,
        bool(entry.get("description")),
        bool(entry.get("pushed_at")),
        bool(entry.get("created_at")),
        len(entry.get("topics", [])) >= 3,
        bool(entry.get("project_type")),
        bool(entry.get("primary_category")),
    ])
    if points >= 9:
        return "high"
    if points >= 6:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Score and rank catalog entries")
    parser.add_argument("--input", default="data/catalog.json")
    parser.add_argument("--output", default="data/catalog.json")
    args = parser.parse_args()

    print("=" * 60)
    print("WERKAtlas — Scoring (score.py)")
    print("Dimensions: 20+15+15+10+10+10+10+5+3+2 = 100 pts max")
    print("=" * 60)

    with open(args.input, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    entries = data.get("entries", [])
    print(f"Scoring {len(entries)} entries...")

    for entry in entries:
        r_score, r_exp     = score_relevance(entry)
        m_score, m_exp     = score_maintenance(entry)
        a_score, a_exp     = score_adoption(entry)
        mo_score, mo_exp   = score_momentum(entry)
        d_score, d_exp     = score_documentation(entry)
        pr_score, pr_exp   = score_production_readiness(entry)
        sec_score, sec_exp = score_security(entry)
        i_score, i_exp     = score_interoperability(entry)
        c_score, c_exp     = score_community(entry)
        u_score, u_exp     = score_uniqueness(entry)

        components = {
            "relevance":            r_score,
            "maintenance":          m_score,
            "adoption":             a_score,
            "momentum":             mo_score,
            "documentation":        d_score,
            "production_readiness": pr_score,
            "security":             sec_score,
            "interoperability":     i_score,
            "community":            c_score,
            "uniqueness":           u_score,
        }

        total = round(sum(components.values()), 1)
        assert total <= 100.1, f"Score overflow for {entry.get('id')}: {total}"

        all_explanations = (
            r_exp + m_exp + a_exp + mo_exp + d_exp +
            pr_exp + sec_exp + i_exp + c_exp + u_exp
        )

        entry["score_components"]  = components
        entry["score"]             = total
        entry["score_label"]       = compute_score_label(total)
        entry["score_explanations"] = all_explanations
        entry["confidence"]        = compute_confidence(entry)

    # Sort by score descending
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)

    # Stats
    scores = [e.get("score", 0) for e in entries]
    label_counts: dict[str, int] = {}
    for e in entries:
        lbl = e.get("score_label", "minimal")
        label_counts[lbl] = label_counts.get(lbl, 0) + 1

    print(f"\nScore distribution:")
    print(f"  Essential  (>=85): {label_counts.get('essential', 0)}")
    print(f"  Strong   (75-84):  {label_counts.get('strong', 0)}")
    print(f"  Emerging (65-74):  {label_counts.get('emerging', 0)}")
    print(f"  Watchlist(50-64):  {label_counts.get('watchlist', 0)}")
    print(f"  Minimal    (<50):  {label_counts.get('minimal', 0)}")
    print(f"\n  Min: {min(scores):.1f}  Max: {max(scores):.1f}  Avg: {sum(scores)/len(scores):.1f}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to {args.output}")


if __name__ == "__main__":
    main()
