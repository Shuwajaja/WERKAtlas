#!/usr/bin/env python3
"""
render.py — LOOP 5: Generate all Markdown documentation from catalog data.

Usage:
    python scripts/render.py --catalog data/catalog.json --taxonomy data/taxonomy.json --output .
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_catalog(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_taxonomy(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_category_path(taxonomy: dict, cat_id: str) -> str | None:
    """Get the full category name path from taxonomy."""
    for group_id, group in taxonomy.get("categories", {}).items():
        if cat_id in group.get("subcategories", {}):
            return f"{group['name']} > {group['subcategories'][cat_id]['name']}"
    return cat_id


def get_category_name(taxonomy: dict, cat_id: str) -> str:
    """Get short category name."""
    for group in taxonomy.get("categories", {}).values():
        if cat_id in group.get("subcategories", {}):
            return group["subcategories"][cat_id]["name"]
    return cat_id


def format_stars(n: int) -> str:
    """Format star count with k/m suffixes."""
    if n >= 1000:
        return f"{n/1000:.1f}k" if n < 100000 else f"{n/1000:.0f}k"
    return str(n)


def score_label(score: float) -> str:
    if score >= 85:
        return "🟢 Essential"
    elif score >= 75:
        return "🔵 Strong"
    elif score >= 65:
        return "🟡 Emerging"
    elif score >= 50:
        return "🟠 Watchlist"
    else:
        return "⚪ Excluded"


def render_readme(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = catalog.get("entries", [])
    accepted = [e for e in entries if e.get("score", 0) >= 50]
    
    lines = []
    lines.append(f"# Agentic Engineering Compendium")
    lines.append("")
    lines.append("> Build, evaluate, connect, secure, and operate AI agents—from first principles to production.")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append(f"**Candidates evaluated:** {len(entries)}")
    lines.append(f"**Accepted projects:** {len(accepted)}")
    lines.append("")
    lines.append("A comprehensive, evidence-backed, reproducible knowledge base mapping the entire modern AI-agent ecosystem. ")
    lines.append("Inspired by the clarity of [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x), ")
    lines.append("but covering the full agent stack—from frameworks to deployment, from MCP to memory systems.")
    lines.append("")
    lines.append("## Contents")
    lines.append("")
    lines.append("- [Full Catalog](CATALOG.md) — Complete categorized listing")
    lines.append("- [Build Your Own](BUILD-YOUR-OWN.md) — Implementation tutorials")
    lines.append("- [Ecosystem Landscape](LANDSCAPE.md) — How layers fit together")
    lines.append("- [Top Picks](TOP-PICKS.md) — Curated selections by category")
    lines.append("- [Trending](TRENDING.md) — Momentum and growth")
    lines.append("- [Watchlist](WATCHLIST.md) — Promising but unverified")
    lines.append("- [Archived](ARCHIVED.md) — Historical and educational")
    lines.append("- [Methodology](METHODOLOGY.md) — Scoring, evidence, and selection")
    lines.append("- [Contribute](CONTRIBUTING.md) — How to add projects")
    lines.append("")
    lines.append("## Quick Navigation")
    lines.append("")
    lines.append("| Category | Projects |")
    lines.append("|---|---|")
    
    # Count by category group
    from collections import Counter
    cat_counts = Counter()
    for e in accepted:
        pc = e.get("primary_category", "")
        for group_id, group in taxonomy.get("categories", {}).items():
            if pc in group.get("subcategories", {}):
                cat_counts[group["name"]] += 1
                break
    
    for name, count in sorted(cat_counts.items()):
        lines.append(f"| {name} | {count} |")
    
    lines.append("")
    lines.append("## Top Projects by Category")
    lines.append("")
    
    # Group by top-level category
    grouped = {}
    for e in accepted:
        pc = e.get("primary_category", "")
        for group_id, group in taxonomy.get("categories", {}).items():
            if pc in group.get("subcategories", {}):
                grouped.setdefault(group["name"], []).append(e)
                break
    
    for group_name in sorted(grouped.keys()):
        projects = sorted(grouped[group_name], key=lambda x: x.get("score", 0), reverse=True)
        top = projects[:3]
        lines.append(f"### {group_name}")
        for p in top:
            name = p.get("name", "?")
            repo = p.get("repository", "?")
            desc = p.get("description", "") or ""
            score = p.get("score", 0)
            stars = format_stars(p.get("stars", 0))
            lines.append(f"- [{name}](https://github.com/{repo}) — {desc} (★{stars}, Score {score})")
        lines.append("")
    
    lines.append("## Methodology")
    lines.append("")
    lines.append("Projects are scored on 10 dimensions (0-100 total): relevance, maintenance, adoption, momentum,")
    lines.append("documentation, production readiness, security, interoperability, community, and uniqueness.")
    lines.append("Stars use logarithmic weighting. Full details in [METHODOLOGY.md](METHODOLOGY.md).")
    lines.append("")
    lines.append("## License and Disclaimer")
    lines.append("")
    lines.append("This is a research compilation. Project logos, names, and trademarks belong to their respective owners.")
    lines.append("Scores are editorial classifications, not objective truth. No endorsement implied.")
    lines.append("")
    lines.append("---")
    lines.append(f"*Snapshot: {snapshot_date}*")
    
    return "\n".join(lines)


def render_catalog(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = sorted(catalog.get("entries", []), key=lambda e: e.get("score", 0), reverse=True)
    accepted = [e for e in entries if e.get("score", 0) >= 50]
    
    lines = []
    lines.append(f"# Full Catalog")
    lines.append("")
    lines.append(f"{len(accepted)} accepted projects (★ = stars, S = score, C = confidence)")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("| Legend | |")
    lines.append("|---|---|")
    lines.append("| 🟢 Essential (85-100) | 🔵 Strong (75-84) |")
    lines.append("| 🟡 Emerging (65-74) | 🟠 Watchlist (50-64) |")
    lines.append("")
    
    # Group by top-level category
    from collections import defaultdict
    grouped = defaultdict(list)
    for e in accepted:
        pc = e.get("primary_category", "")
        for group_id, group in taxonomy.get("categories", {}).items():
            if pc in group.get("subcategories", {}):
                grouped[group_id].append(e)
                break
        else:
            grouped["ZZ"].append(e)
    
    for group_id in sorted(grouped.keys()):
        if group_id == "ZZ":
            continue
        group = taxonomy.get("categories", {}).get(group_id, {})
        group_name = group.get("name", group_id)
        lines.append(f"## {group_name}")
        lines.append("")
        
        # Group by subcategory
        sub_groups = defaultdict(list)
        for e in grouped[group_id]:
            sub_groups[e.get("primary_category", "unknown")].append(e)
        
        for sub_id in sorted(sub_groups.keys()):
            sub_name = get_category_name(taxonomy, sub_id)
            lines.append(f"### {sub_name}")
            lines.append("")
            
            for e in sub_groups[sub_id]:
                name = e.get("name", "?")
                repo = e.get("repository", "?")
                desc = (e.get("description") or "")[:120]
                ptype = e.get("project_type") or "?"
                lang = e.get("primary_language") or "?"
                deploy = ", ".join(e.get("deployment_modes", [])) or "?"
                stars = format_stars(e.get("stars", 0))
                score = e.get("score", 0)
                conf = e.get("confidence", "low")
                license_spdx = e.get("license") or "?"
                updated = (e.get("updated_at") or "?")[:10]
                label = score_label(score)
                
                lines.append(f"- [{name}](https://github.com/{repo}) — {desc}.")
                lines.append(f"  `{ptype}` `{lang}` `{deploy}`")
                lines.append(f"  ★ {stars} · Updated {updated} · {license_spdx} · {label} S={score} C={conf}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_landscape(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    lines = []
    lines.append("# Agentic Ecosystem Landscape")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("## Layer Architecture")
    lines.append("")
    lines.append("```")
    lines.append("┌──────────────────────────────────────┐")
    lines.append("│      User Interfaces & Workspaces     │  J. Applications")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│        Agent Applications             │  Knowledge work, research, DevOps")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│     Frameworks & Runtimes             │  B. Agent construction & execution")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│  Planning / Memory / Workflow         │  F. Context, reasoning, state")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│    Tools / Skills / MCP / Protocols   │  D+E. Integration & interoperability")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│   Sandbox / Browser / Execution       │  G. Safe execution environments")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│     Model Gateway / Inference         │  I. Model infrastructure")
    lines.append("├──────────────────────────────────────┤")
    lines.append("│   Tracing / Evaluation / Security     │  H. Reliability & operations")
    lines.append("└──────────────────────────────────────┘")
    lines.append("```")
    lines.append("")
    lines.append("## Layer Descriptions")
    lines.append("")
    lines.append("### User Layer (J)")
    lines.append("Chat interfaces, dashboards, workspaces, no-code builders, and vertical agent applications.")
    lines.append("")
    lines.append("### Application Layer (J, C)")
    lines.append("Coding agents, research agents, DevOps agents, and knowledge-work agents that users interact with directly.")
    lines.append("")
    lines.append("### Framework Layer (B)")
    lines.append("Agent frameworks, runtimes, graph orchestrators, multi-agent systems, and durable execution engines.")
    lines.append("These provide the programming model for building agents.")
    lines.append("")
    lines.append("### Intelligence Layer (B.12, F)")
    lines.append("Planning, reasoning, task decomposition, memory systems, RAG, knowledge graphs, and context engineering.")
    lines.append("")
    lines.append("### Integration Layer (D, E)")
    lines.append("MCP servers/clients/SDKs, tool-calling libraries, agent protocols, skills, and connectors.")
    lines.append("This is where agents connect to external tools and data sources.")
    lines.append("")
    lines.append("### Execution Layer (G)")
    lines.append("Browser agents, computer-use agents, sandboxes, code execution, and containers.")
    lines.append("Safe environments for agents to take actions.")
    lines.append("")
    lines.append("### Infrastructure Layer (I)")
    lines.append("Model gateways, inference servers, local stacks, cloud platforms, agent scheduling, and control planes.")
    lines.append("")
    lines.append("### Operations Layer (H)")
    lines.append("Observability, tracing, evaluation, benchmarks, guardrails, security, and cost management.")
    lines.append("")
    lines.append("## Mermaid Diagram")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph TD")
    lines.append("    UI[User Interfaces] --> Apps[Agent Applications]")
    lines.append("    Apps --> Frameworks[Frameworks & Runtimes]")
    lines.append("    Frameworks --> Intel[Planning/Memory/Context]")
    lines.append("    Intel --> Tools[Tools/MCP/Protocols]")
    lines.append("    Tools --> Sandbox[Sandbox/Browser/Execution]")
    lines.append("    Sandbox --> Model[Model Gateway/Inference]")
    lines.append("    Model --> Ops[Tracing/Eval/Security]")
    lines.append("    Ops -.->|Feedback| UI")
    lines.append("```")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    
    return "\n".join(lines)


def render_top_picks(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = sorted(catalog.get("entries", []), key=lambda e: e.get("score", 0), reverse=True)
    accepted = [e for e in entries if e.get("score", 0) >= 50]
    
    lines = []
    lines.append("# Top Picks")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("Carefully scoped selections. These are editorial recommendations, not objective rankings.")
    lines.append("")
    
    sections = [
        ("Best Starting Points for Learning", lambda e: e.get("primary_category", "").startswith("A.")),
        ("Strongest General-Purpose Frameworks", lambda e: e.get("primary_category") == "B.6"),
        ("Strongest MCP Infrastructure", lambda e: e.get("primary_category", "").startswith("D.")),
        ("Strongest Coding Agents", lambda e: e.get("primary_category", "").startswith("C.")),
        ("Strongest Local-First Options", lambda e: "local-first" in e.get("deployment_modes", []) or e.get("primary_category") == "I.66"),
        ("Strongest Evaluation Systems", lambda e: e.get("primary_category") in ("H.55", "H.56")),
        ("Strongest Sandbox Systems", lambda e: e.get("primary_category") in ("G.49", "G.48")),
        ("Strongest Observability Systems", lambda e: e.get("primary_category") in ("H.53", "H.54")),
        ("Strongest Memory & RAG Systems", lambda e: e.get("primary_category") in ("F.37", "F.38")),
    ]
    
    for title, filter_fn in sections:
        picks = [e for e in accepted if filter_fn(e)][:5]
        if picks:
            lines.append(f"## {title}")
            lines.append("")
            for p in picks:
                name = p.get("name", "?")
                repo = p.get("repository", "?")
                desc = (p.get("description") or "")[:100]
                score = p.get("score", 0)
                stars = format_stars(p.get("stars", 0))
                lines.append(f"- [{name}](https://github.com/{repo}) — {desc} (★{stars}, Score {score})")
            lines.append("")
    
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_trending(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = sorted(catalog.get("entries", []), key=lambda e: e.get("score", 0), reverse=True)
    
    lines = []
    lines.append("# Trending Projects")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("Trend data uses momentum proxy (recent pushes, releases, activity) when exact star growth is unavailable.")
    lines.append("")
    
    # Sort by momentum score (highest first)
    by_momentum = sorted(entries, key=lambda e: e.get("score_components", {}).get("momentum", 0), reverse=True)
    
    lines.append("## High Momentum (Established)")
    lines.append("")
    for e in by_momentum[:10]:
        name = e.get("name", "?")
        repo = e.get("repository", "?")
        score = e.get("score", 0)
        momentum = e.get("score_components", {}).get("momentum", 0)
        pushed = (e.get("pushed_at") or "?")[:10]
        lines.append(f"- [{name}](https://github.com/{repo}) — Momentum {momentum}/10, Total Score {score}, Pushed {pushed}")
    lines.append("")
    
    lines.append("## Recently Created (Emerging)")
    lines.append("")
    by_created = sorted(
        [e for e in entries if e.get("created_at")],
        key=lambda e: e.get("created_at", ""),
        reverse=True,
    )[:10]
    for e in by_created:
        name = e.get("name", "?")
        repo = e.get("repository", "?")
        created = (e.get("created_at") or "?")[:10]
        stars = format_stars(e.get("stars", 0))
        lines.append(f"- [{name}](https://github.com/{repo}) — Created {created}, ★{stars}")
    
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_watchlist(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = catalog.get("entries", [])
    watchlist = [e for e in entries if e.get("score", 0) >= 50 and e.get("confidence") == "low"]
    
    lines = []
    lines.append("# Watchlist")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append(f"**Projects:** {len(watchlist)}")
    lines.append("")
    lines.append("Projects that appear promising but require deeper verification.")
    lines.append("")
    
    if watchlist:
        for e in watchlist:
            name = e.get("name", "?")
            repo = e.get("repository", "?")
            desc = (e.get("description") or "No description")[:100]
            stars = format_stars(e.get("stars", 0))
            score = e.get("score", 0)
            lines.append(f"- [{name}](https://github.com/{repo}) — {desc} (★{stars}, Score {score})")
    else:
        lines.append("*No projects currently on the watchlist.*")
    
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_archived(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = catalog.get("entries", [])
    archived = [e for e in entries if e.get("archived", False)]
    stale = [e for e in entries if not e.get("archived") and e.get("maintenance_status") in ("stale", "slow")]
    
    lines = []
    lines.append("# Archived & Historical Projects")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("This section preserves historically important or educational projects.")
    lines.append("Archived or stale status does not negate educational value.")
    lines.append("")
    
    if archived:
        lines.append("## Archived Repositories")
        lines.append("")
        for e in archived:
            name = e.get("name", "?")
            repo = e.get("repository", "?")
            desc = (e.get("description") or "No description")[:100]
            stars = format_stars(e.get("stars", 0))
            score = e.get("score", 0)
            updated = (e.get("updated_at") or "?")[:10]
            lines.append(f"- [{name}](https://github.com/{repo}) — {desc} (★{stars}, Score {score}, Updated {updated})")
    else:
        lines.append("*No archived repositories in current catalog.*")
    
    lines.append("")
    if stale:
        lines.append("## Stale / Slow Maintenance")
        lines.append("")
        for e in stale:
            name = e.get("name", "?")
            repo = e.get("repository", "?")
            status = e.get("maintenance_status", "unclear")
            desc = (e.get("description") or "No description")[:100]
            lines.append(f"- [{name}](https://github.com/{repo}) — {desc} (Status: {status})")
    else:
        lines.append("*No stale repositories in current catalog.*")
    
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_methodology(snapshot_date: str) -> str:
    lines = []
    lines.append("# Methodology")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("The Agentic Engineering Compendium uses a structured, evidence-backed methodology to catalog")
    lines.append("and evaluate projects in the AI-agent ecosystem. The system runs in five loops:")
    lines.append("")
    lines.append("1. **Taxonomy, Source Mapping, Broad Discovery** — Maximize recall")
    lines.append("2. **Metadata Enrichment & Deduplication** — Convert to structured records")
    lines.append("3. **Deep Verification & Trust Review** — Manual review of important projects")
    lines.append("4. **Scoring, Trends, Gap Analysis** — Rank and identify gaps")
    lines.append("5. **Editorial Production & Final Audit** — Generate polished output")
    lines.append("")
    lines.append("## Scoring System (0-100)")
    lines.append("")
    lines.append("| Component | Max | Description |")
    lines.append("|---|---|---|")
    lines.append("| Relevance | 20 | Alignment with modern AI-agent engineering |")
    lines.append("| Maintenance | 15 | Commit frequency, issue resolution, release cadence |")
    lines.append("| Adoption | 10 | Stars (logarithmic), forks, ecosystem usage |")
    lines.append("| Momentum | 10 | Recent pushes, releases, community activity |")
    lines.append("| Documentation | 10 | README quality, docs site, examples |")
    lines.append("| Production Readiness | 10 | Maturity, stability, deployment support |")
    lines.append("| Security | 10 | License, security policy, vulnerability handling |")
    lines.append("| Interoperability | 5 | Protocol support, multi-language, standards |")
    lines.append("| Community | 5 | Contributor diversity, governance, responsiveness |")
    lines.append("| Uniqueness | 5 | Technical novelty, educational value, filling a gap |")
    lines.append("")
    lines.append("### Star Scoring")
    lines.append("Logarithmic: ln(stars + 1) / ln(100001) * 10. This prevents star count from dominating.")
    lines.append("")
    lines.append("### Labels")
    lines.append("- **Essential (85-100):** Core infrastructure, widely adopted, well-maintained")
    lines.append("- **Strong (75-84):** Production-quality, recommended for most use cases")
    lines.append("- **Emerging (65-74):** Promising, gaining traction, worth watching")
    lines.append("- **Watchlist (50-64):** Interesting but needs more verification")
    lines.append("- **Excluded (<50):** Does not meet quality or relevance thresholds")
    lines.append("")
    lines.append("## Evidence Requirements")
    lines.append("")
    lines.append("Every accepted project must have evidence from:")
    lines.append("- Canonical GitHub repository")
    lines.append("- Official documentation")
    lines.append("- Official registry entry")
    lines.append("- Official organization")
    lines.append("")
    lines.append("## Discovery Sources (Hierarchical)")
    lines.append("")
    lines.append("1. **Tier 1:** Official GitHub orgs, SDKs, registries, specifications")
    lines.append("2. **Tier 2:** Curated awesome lists, ecosystem directories, package registries")
    lines.append("3. **Tier 3:** Social media, blogs, newsletters (discovery only, not sufficient for acceptance)")
    lines.append("")
    lines.append("## Penalties")
    lines.append("- Archived repository: Severe penalty")
    lines.append("- Missing or unclear license: Moderate penalty")
    lines.append("- No meaningful agent relevance: Exclusion")
    lines.append("- Abandoned fork: Exclusion")
    lines.append("- Misleading README or marketing-only repos: Exclusion")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_contributing(snapshot_date: str) -> str:
    lines = []
    lines.append("# Contributing")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("## How to Contribute")
    lines.append("")
    lines.append("### Suggest a Project")
    lines.append("Open an issue with:")
    lines.append("- Canonical project name")
    lines.append("- Repository URL")
    lines.append("- Category (from taxonomy)")
    lines.append("- Project type")
    lines.append("- Neutral description (12-30 words)")
    lines.append("- Evidence of maintenance (last commit, release)")
    lines.append("- License information")
    lines.append("- Official/community status")
    lines.append("- Reason for inclusion")
    lines.append("- Disclosure of affiliation")
    lines.append("- Security considerations (for sensitive MCP servers)")
    lines.append("")
    lines.append("### Correct Metadata")
    lines.append("Open an issue describing the correction needed.")
    lines.append("")
    lines.append("### Report Archived/Security Issues")
    lines.append("Use the appropriate issue template.")
    lines.append("")
    lines.append("## Development")
    lines.append("")
    lines.append("```bash")
    lines.append("# Install dependencies")
    lines.append("make setup")
    lines.append("")
    lines.append("# Run the full pipeline")
    lines.append("make all")
    lines.append("")
    lines.append("# Validate only")
    lines.append("make validate")
    lines.append("")
    lines.append("# Run tests")
    lines.append("make test")
    lines.append("```")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_security(snapshot_date: str) -> str:
    lines = []
    lines.append("# Security Policy")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("## Reporting Vulnerabilities")
    lines.append("")
    lines.append("If you discover a security vulnerability in a listed project, report it to the project maintainers")
    lines.append("following their disclosure policy.")
    lines.append("")
    lines.append("For issues with the compendium itself (data integrity, credential leaks),")
    lines.append("please open an issue.")
    lines.append("")
    lines.append("## Security Notes in the Catalog")
    lines.append("")
    lines.append("MCP servers with filesystem, shell, browser, credential, database, email, cloud,")
    lines.append("or infrastructure access are flagged with security notes in the catalog.")
    lines.append("")
    lines.append("## Best Practices for MCP Security")
    lines.append("")
    lines.append("- Validate MCP server source code before deployment")
    lines.append("- Use permission systems to limit server capabilities")
    lines.append("- Never expose MCP servers with shell/filesystem access to untrusted users")
    lines.append("- Review MCP server configurations for credential exposure")
    lines.append("- Run MCP servers in isolated environments where possible")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def render_build_your_own(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    entries = catalog.get("entries", [])
    tutorials = [e for e in entries if e.get("primary_category") == "A.1"]
    
    lines = []
    lines.append("# Build Your Own Agentic Stack")
    lines.append("")
    lines.append(f"**Snapshot date:** {snapshot_date}")
    lines.append("")
    lines.append("A curated collection of implementation-oriented tutorials for building agent technology from scratch.")
    lines.append("")
    lines.append("## Build Your Own")
    lines.append("")
    
    # Group by topic
    topics = {
        "Agent Loop": [],
        "MCP Server": [],
        "MCP Client": [],
        "Memory System": [],
        "Evaluation": [],
        "General": tutorials,
    }
    
    for topic, projects in topics.items():
        if projects:
            lines.append(f"### {topic}")
            lines.append("")
            for p in projects:
                name = p.get("name", "?")
                repo = p.get("repository", "?")
                desc = (p.get("description") or "No description")[:100]
                lang = p.get("primary_language") or "?"
                lines.append(f"- [{name}](https://github.com/{repo}) — {desc} `{lang}`")
            lines.append("")
    
    if not tutorials:
        lines.append("*No implementation-oriented tutorials in current catalog yet.*")
        lines.append("Help us grow this section by [contributing](https://github.com/your-org/agentic-engineering-compendium)!")
        lines.append("")
    
    lines.append(f"*Snapshot: {snapshot_date}*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render Markdown documentation from catalog")
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--taxonomy", default="data/taxonomy.json")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    print("=" * 60)
    print("Agentic Engineering Compendium — Rendering (LOOP 5)")
    print("=" * 60)
    
    catalog = load_catalog(args.catalog)
    taxonomy = load_taxonomy(args.taxonomy)
    snapshot_date = catalog.get("snapshot_date", "2026-07-07")
    
    render_fns = {
        "README.md": render_readme,
        "BUILD-YOUR-OWN.md": render_build_your_own,
        "CATALOG.md": render_catalog,
        "LANDSCAPE.md": render_landscape,
        "TOP-PICKS.md": render_top_picks,
        "TRENDING.md": render_trending,
        "WATCHLIST.md": render_watchlist,
        "ARCHIVED.md": render_archived,
        "METHODOLOGY.md": render_methodology,
        "CONTRIBUTING.md": render_contributing,
        "SECURITY.md": render_security,
    }
    
    for filename, render_fn in render_fns.items():
        if filename in ("METHODOLOGY.md", "CONTRIBUTING.md", "SECURITY.md"):
            content = render_fn(snapshot_date)
        else:
            content = render_fn(catalog, taxonomy, snapshot_date)
        
        output_path = os.path.join(args.output, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"  Generated {output_path}")
    
    print(f"\nRendering complete! Generated {len(render_fns)} files.")


if __name__ == "__main__":
    main()
