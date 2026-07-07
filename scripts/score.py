#!/usr/bin/env python3
"""
score.py — LOOP 4: Score and rank catalog entries.

Implements the scoring system from METHODOLOGY.md.

Usage:
    python scripts/score.py --input data/catalog.json --output data/catalog.json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone


def log_stars(stars: int) -> float:
    """Logarithmic star score: ln(stars + 1) / ln(100001) * 10."""
    if stars <= 0:
        return 0
    return min(10, math.log(stars + 1) / math.log(100001) * 10)


def score_relevance(entry: dict) -> float:
    """Score relevance to modern agent engineering (0-20).
    
    Based on topics, description keywords, and project type.
    """
    score = 10  # baseline for having been included
    
    topics = set(t.lower() for t in entry.get("topics", []))
    name = (entry.get("name") or "").lower()
    desc = (entry.get("description") or "").lower()
    project_type = (entry.get("project_type") or "").lower()
    
    # Direct agent keywords
    agent_keywords = ["ai-agent", "llm-agent", "agent-framework", "agent-runtime",
                      "agent-orchestration", "agent-sdk", "mcp", "coding-agent",
                      "browser-agent", "autonomous-agent", "agent-memory",
                      "multi-agent", "agent-swarm", "agent-tool", "agent-skill"]
    
    for kw in agent_keywords:
        if kw in topics or kw in name or kw in desc:
            score += 2
            break
    
    # Project type bonuses
    type_bonus = {
        "framework": 3,
        "runtime": 3,
        "sdk": 2,
        "mcp server": 3,
        "mcp client": 3,
        "application": 2,
        "developer tool": 2,
        "protocol": 3,
        "evaluation framework": 3,
        "sandbox": 3,
    }
    score += type_bonus.get(project_type, 1)
    
    return min(20, score)


def score_maintenance(entry: dict) -> float:
    """Score maintenance health (0-15)."""
    if entry.get("archived", False):
        return 0
    
    pushed_at = entry.get("pushed_at")
    if not pushed_at:
        return 5
    
    try:
        pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_since_push = (now - pushed).days
    except (ValueError, TypeError):
        return 5
    
    if days_since_push < 7:
        return 15
    elif days_since_push < 30:
        return 12
    elif days_since_push < 90:
        return 9
    elif days_since_push < 180:
        return 6
    elif days_since_push < 365:
        return 3
    else:
        return 1


def score_adoption(entry: dict) -> float:
    """Score adoption and ecosystem use (0-10)."""
    stars = entry.get("stars", 0)
    forks = entry.get("forks", 0)
    
    star_score = log_stars(stars)
    fork_score = min(3, math.log(forks + 1) / math.log(10001) * 3)
    
    return min(10, star_score + fork_score)


def score_momentum(entry: dict) -> float:
    """Score current momentum (0-10).
    
    Based on recent pushes and releases.
    """
    score = 3  # baseline
    
    pushed_at = entry.get("pushed_at")
    if pushed_at:
        try:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_since_push = (now - pushed).days
            
            if days_since_push < 7:
                score += 5
            elif days_since_push < 30:
                score += 3
            elif days_since_push < 90:
                score += 1
        except:
            pass
    
    release_at = entry.get("latest_release_at")
    if release_at:
        try:
            released = datetime.fromisoformat(release_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_since_release = (now - released).days
            
            if days_since_release < 30:
                score += 2
            elif days_since_release < 90:
                score += 1
        except:
            pass
    
    return min(10, score)


def score_documentation(entry: dict) -> float:
    """Score documentation and onboarding (0-10)."""
    desc = (entry.get("description") or "").strip()
    topics = entry.get("topics", [])
    homepage = entry.get("homepage_url")
    
    score = 2  # baseline for having a description
    
    if len(desc) > 50:
        score += 2
    if len(desc) > 100:
        score += 1
    
    if homepage:
        score += 2
    
    if len(topics) >= 3:
        score += 1
    if len(topics) >= 5:
        score += 1
    
    # License presence
    if entry.get("license"):
        score += 1
    
    return min(10, score)


def score_production_readiness(entry: dict) -> float:
    """Score engineering and production readiness (0-10)."""
    stars = entry.get("stars", 0)
    forks = entry.get("forks", 0)
    open_issues = entry.get("open_issues", 0)
    
    score = 2  # baseline
    
    # Size and activity signals
    if stars >= 1000:
        score += 2
    if stars >= 10000:
        score += 2
    if forks >= 100:
        score += 1
    if forks >= 1000:
        score += 1
    
    # Release cadence
    if entry.get("latest_release_at"):
        score += 2
    
    return min(10, score)


def score_security(entry: dict) -> float:
    """Score security and operational transparency (0-10)."""
    score = 3  # baseline
    
    if entry.get("license"):
        score += 2
    
    # High profile projects typically have better security practices
    stars = entry.get("stars", 0)
    if stars >= 5000:
        score += 2
    if stars >= 50000:
        score += 1
    
    # Security notes (from verification)
    security_notes = entry.get("security_notes", [])
    if security_notes:
        score -= 1  # flagged but aware
    
    return max(0, min(10, score))


def score_interoperability(entry: dict) -> float:
    """Score interoperability and standards support (0-5)."""
    score = 0
    
    protocols = entry.get("protocols", [])
    if "mcp" in str(protocols).lower() or "mcp" in str(entry.get("topics", [])).lower():
        score += 2
    
    compatible_hosts = entry.get("compatible_hosts", [])
    if compatible_hosts:
        score += 1
    
    # Multi-language support
    languages = entry.get("languages", [])
    if len(languages) >= 3:
        score += 1
    if len(languages) >= 5:
        score += 1
    
    return min(5, score)


def score_community(entry: dict) -> float:
    """Score community and governance (0-5)."""
    stars = entry.get("stars", 0)
    forks = entry.get("forks", 0)
    
    score = 1  # baseline
    
    if stars >= 1000:
        score += 1
    if stars >= 10000:
        score += 1
    if forks >= 200:
        score += 1
    if forks >= 1000:
        score += 1
    
    return min(5, score)


def score_uniqueness(entry: dict) -> float:
    """Score technical uniqueness or educational value (0-5)."""
    # Placeholder - will be refined in LOOP 3 verification
    stars = entry.get("stars", 0)
    
    # Very high star repos are often unique/foundational
    if stars >= 50000:
        return 5
    elif stars >= 10000:
        return 4
    elif stars >= 5000:
        return 3
    elif stars >= 1000:
        return 2
    else:
        return 1


def compute_confidence(entry: dict) -> str:
    """Compute evidence confidence level."""
    score = 0
    
    if entry.get("repository_url"):
        score += 1
    if entry.get("license"):
        score += 1
    if entry.get("stars", 0) > 0:
        score += 1
    if entry.get("forks", 0) > 0:
        score += 1
    if entry.get("description"):
        score += 1
    if entry.get("pushed_at"):
        score += 1
    if entry.get("created_at"):
        score += 1
    if len(entry.get("topics", [])) >= 3:
        score += 1
    if entry.get("project_type"):
        score += 1
    if entry.get("primary_category"):
        score += 1
    
    if score >= 9:
        return "high"
    elif score >= 6:
        return "medium"
    else:
        return "low"


def main():
    parser = argparse.ArgumentParser(description="Score and rank catalog entries")
    parser.add_argument("--input", default="data/catalog.json")
    parser.add_argument("--output", default="data/catalog.json")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Agentic Engineering Compendium — Scoring (LOOP 4)")
    print("=" * 60)
    
    with open(args.input, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    entries = data.get("entries", [])
    print(f"Scoring {len(entries)} entries...")
    
    for entry in entries:
        components = {
            "relevance": score_relevance(entry),
            "maintenance": score_maintenance(entry),
            "adoption": score_adoption(entry),
            "momentum": score_momentum(entry),
            "documentation": score_documentation(entry),
            "production_readiness": score_production_readiness(entry),
            "security": score_security(entry),
            "interoperability": score_interoperability(entry),
            "community": score_community(entry),
            "uniqueness": score_uniqueness(entry),
        }
        
        total_score = sum(components.values())
        confidence = compute_confidence(entry)
        
        entry["score_components"] = components
        entry["score"] = round(total_score, 1)
        entry["confidence"] = confidence
    
    # Sort by score descending
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    
    # Stats
    scores = [e.get("score", 0) for e in entries]
    labels = {"essential": [], "strong": [], "emerging": [], "watchlist": []}
    for e in entries:
        s = e.get("score", 0)
        if s >= 85:
            labels["essential"].append(e.get("id"))
        elif s >= 75:
            labels["strong"].append(e.get("id"))
        elif s >= 65:
            labels["emerging"].append(e.get("id"))
        elif s >= 50:
            labels["watchlist"].append(e.get("id"))
    
    print(f"\nScore distribution:")
    print(f"  Essential (85-100): {len(labels['essential'])}")
    print(f"  Strong (75-84):     {len(labels['strong'])}")
    print(f"  Emerging (65-74):   {len(labels['emerging'])}")
    print(f"  Watchlist (50-64):  {len(labels['watchlist'])}")
    print(f"  Excluded (<50):     {len([s for s in scores if s < 50])}")
    
    print(f"\n  Min score: {min(scores):.1f}")
    print(f"  Max score: {max(scores):.1f}")
    print(f"  Avg score: {sum(scores)/len(scores):.1f}")
    
    # Write updated catalog
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nOutput written to {args.output}")


if __name__ == "__main__":
    main()
