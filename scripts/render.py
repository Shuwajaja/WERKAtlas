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
from collections import Counter
from html import escape


MOJIBAKE_REPLACEMENTS = {
    "â€”": "-",
    "â€“": "-",
    "Ã¤": "ae",
    "Ã¶": "oe",
    "Ã¼": "ue",
    "Ã„": "Ae",
    "Ã–": "Oe",
    "Ãœ": "Ue",
    "ÃŸ": "ss",
}


def clean_text(value: object) -> str:
    """Return compact display-safe text for generated Markdown."""
    text = "" if value is None else str(value)
    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return " ".join(text.split())


def truncate(value: object, limit: int) -> str:
    """Trim text without cutting words where possible."""
    text = clean_text(value)
    if len(text) <= limit:
        return text
    trimmed = text[: limit - 1].rsplit(" ", 1)[0].strip()
    return f"{trimmed}..." if trimmed else f"{text[: limit - 4]}..."


def details_summary(value: object) -> str:
    """Escape text used inside HTML summary tags."""
    return escape(clean_text(value), quote=False)


def load_catalog(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_taxonomy(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_category_path(taxonomy: dict, cat_id: str):
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
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.1f}k" if n < 100000 else f"{n/1000:.0f}k"
    return str(n)


def score_label(score: float) -> str:
    if score >= 85:
        return "ESSENTIAL"
    if score >= 75:
        return "STRONG"
    if score >= 65:
        return "EMERGING"
    if score >= 50:
        return "WATCHLIST"
    return "EXCLUDED"


def score_badge(score: float) -> str:
    if score >= 85: return "Essential"
    if score >= 75: return "Strong"
    if score >= 65: return "Emerging"
    if score >= 50: return "Watchlist"
    return "Excluded"


def official_badge(status: str) -> str:
    if status == "official": return "Official"
    return "Community"


def _render_toc(taxonomy: dict, accepted: list) -> list:
    """Render table of contents."""
    cat_counts = Counter()
    for e in accepted:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                cat_counts[group["name"]] += 1
                break

    lines = ["## Inhalt", ""]
    for name, count in sorted(cat_counts.items()):
        anchor = name.lower().replace(" ", "-").replace(",", "").replace("&", "and").replace(".", "").replace("(", "").replace(")", "")
        lines.append(f"- [{name}](#{anchor}) — {count} Projekte")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _render_category_section(group_name: str, projects: list, taxonomy: dict) -> list:
    """Render a full category section with all projects."""
    lines = []
    lines.append(f"## {group_name}")
    lines.append("")

    # Subcategory breakdown
    subcat_counts = Counter()
    cat_map = {}
    for e in projects:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                name = group["subcategories"][pc]["name"]
                subcat_counts[name] += 1
                cat_map[e["id"]] = name
                break

    if subcat_counts:
        lines.append("| Subkategorie | Projekte |")
        lines.append("|---|---|")
        for name, count in sorted(subcat_counts.items()):
            lines.append(f"| {name} | {count} |")
        lines.append("")

    # Each project as a details/summary card
    for p in sorted(projects, key=lambda x: x.get("score", 0), reverse=True):
        repo = p.get("repository", "?")
        name = p.get("name", repo.split("/")[-1])
        desc = (p.get("description") or "")[:120]
        score = p.get("score", 0)
        stars = p.get("stars", 0)
        lang = p.get("primary_language") or p.get("language") or ""
        official = p.get("official_status", "community")
        sec_notes = p.get("security_notes", [])

        # Summary line with badges
        star_str = format_stars(stars)
        badge = score_badge(score)
        official_str = "Official" if official == "official" else "Community"
        
        summary = f"[{repo}](https://github.com/{repo})  Star:{star_str}  Score:{score}  Status:{badge}"
        if official == "official":
            summary += "  Official"
        if lang:
            summary += f"  ({lang})"
        if sec_notes:
            summary += "  [Security]"

        lines.append(f"<details>")
        lines.append(f"<summary><strong>{summary}</strong></summary>")
        lines.append("")
        lines.append(f"> {desc}")
        lines.append("")
        lines.append(f"| Kategorie | Sprache | Status | Score | Stars |")
        lines.append(f"|---|---|---|---|---|")
        subcat = cat_map.get(p["id"], p.get("primary_category", "?"))
        lines.append(f"| {subcat} | {lang or '?'} | {official_str} | {score}/100 | {star_str} |")
        lines.append("")

        if p.get("topics"):
            tags = " ".join(f"`{t}`" for t in p["topics"][:8])
            lines.append(f"Tags: {tags}")
            lines.append("")

        if sec_notes:
            notes = "; ".join(sec_notes[:3])
            lines.append(f"Security: {notes}")
            lines.append("")

        lines.append(f"[GitHub](https://github.com/{repo})")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return lines


def _anchor(name: str) -> str:
    return (
        clean_text(name)
        .lower()
        .replace(" ", "-")
        .replace(",", "")
        .replace("&", "and")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
    )


def _render_toc(taxonomy: dict, accepted: list) -> list:
    """Render a readable table of contents."""
    cat_counts = Counter()
    for e in accepted:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                cat_counts[group["name"]] += 1
                break

    lines = ["## Contents", ""]
    for name, count in sorted(cat_counts.items()):
        lines.append(f"- [{clean_text(name)}](#{_anchor(name)}) - {count} projects")
    lines.extend(["", "---", ""])
    return lines


def _render_category_section(group_name: str, projects: list, taxonomy: dict) -> list:
    """Render a category section as compact, readable project cards."""
    lines = [f"## {clean_text(group_name)}", ""]

    subcat_counts = Counter()
    cat_map = {}
    for e in projects:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                name = clean_text(group["subcategories"][pc]["name"])
                subcat_counts[name] += 1
                cat_map[e["id"]] = name
                break

    if subcat_counts:
        lines.append("| Subcategory | Projects |")
        lines.append("|---|---:|")
        for name, count in sorted(subcat_counts.items()):
            lines.append(f"| {name} | {count} |")
        lines.append("")

    for p in sorted(projects, key=lambda x: x.get("score", 0), reverse=True):
        repo = clean_text(p.get("repository", "?"))
        desc = truncate(p.get("description") or "", 180)
        score = p.get("score", 0)
        stars = format_stars(p.get("stars", 0))
        lang = clean_text(p.get("primary_language") or p.get("language") or "?")
        official = p.get("official_status", "community")
        official_str = "Official" if official == "official" else "Community"
        sec_notes = [clean_text(note) for note in p.get("security_notes", [])]

        summary = f"{repo} - {stars} stars - score {score}/100 - {score_badge(score)} - {lang}"
        if official == "official":
            summary += " - Official"
        if sec_notes:
            summary += " - security notes"

        lines.append("<details>")
        lines.append(f"<summary><strong>{details_summary(summary)}</strong></summary>")
        lines.append("")
        if desc:
            lines.append(f"> {desc}")
            lines.append("")
        lines.append(f"[Open repository](https://github.com/{repo})")
        lines.append("")
        lines.append("| Category | Language | Status | Score | Stars |")
        lines.append("|---|---|---|---:|---:|")
        subcat = clean_text(cat_map.get(p["id"], p.get("primary_category", "?")))
        lines.append(f"| {subcat} | {lang} | {official_str} | {score}/100 | {stars} |")
        lines.append("")

        topics = [clean_text(t) for t in p.get("topics", [])[:8]]
        if topics:
            lines.append("**Tags:** " + " ".join(f"`{t}`" for t in topics))
            lines.append("")

        if sec_notes:
            lines.append("**Security notes:** " + "; ".join(sec_notes[:3]))
            lines.append("")

        lines.append("</details>")
        lines.append("")

    return lines


def render_readme(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Render README.md as a comprehensive scrollable catalog."""
    entries = catalog.get("entries", [])
    accepted = [e for e in entries if e.get("score", 0) >= 50]
    excluded = [e for e in entries if e.get("score", 0) < 50]

    lines = []
    strong = sum(1 for e in accepted if e.get("score", 0) >= 75)
    emerging = sum(1 for e in accepted if 65 <= e.get("score", 0) < 75)
    watchlist = sum(1 for e in accepted if 50 <= e.get("score", 0) < 65)

    # ── HEADER ──
    lines.append("# Agentic Engineering Compendium")
    lines.append("")
    lines.append("> A searchable, evidence-oriented map of the AI-agent engineering ecosystem.")
    lines.append("")
    lines.append(f"**Snapshot:** {snapshot_date}")
    lines.append(f"**Catalog:** {len(entries)} projects ({len(accepted)} scored >= 50, {len(excluded)} excluded)")
    lines.append("**Taxonomy:** 10 top-level categories, 81 subcategories")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── NAVIGATION ──
    lines.extend(_render_toc(taxonomy, accepted))

    # ── SCORE DISTRIBUTION ──
    lines.append("## Score Distribution")
    lines.append("")
    lines.append(f"| Rating | Score range | Projects |")
    lines.append(f"|---|---|---|")
    essential = sum(1 for e in accepted if e.get("score", 0) >= 85)
    strong_only = sum(1 for e in accepted if 75 <= e.get("score", 0) < 85)
    lines.append(f"| Essential | 85+ | {essential} |")
    lines.append(f"| Strong | 75-84 | {strong_only} |")
    lines.append(f"| Emerging | 65-74 | {emerging} |")
    lines.append(f"| Watchlist | 50-64 | {watchlist} |")
    lines.append(f"| Excluded | <50 | {len(excluded)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── TOP 10 ──
    lines.append("## Top 10 Projects")
    lines.append("")
    sorted_all = sorted(accepted, key=lambda x: x.get("score", 0), reverse=True)
    lines.append("| # | Project | Stars | Score |")
    lines.append("|---|---|---|---|")
    for i, p in enumerate(sorted_all[:10], 1):
        repo = p.get("repository", "?")
        stars = format_stars(p.get("stars", 0))
        score = p.get("score", 0)
        desc = (p.get("description") or "")[:60]
        lines.append(f"| {i} | [{repo}](https://github.com/{repo}) | {stars} | {score} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── ALL PROJECTS BY CATEGORY ──
    lines.append("# Complete Catalog")
    lines.append(f"")
    lines.append(f"**{len(accepted)} projects** grouped by category. Expand a project for details.")
    lines.append("")

    # Group by top-level category
    grouped = {}
    for e in accepted:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                grouped.setdefault(group["name"], []).append(e)
                break

    for group_name in sorted(grouped.keys()):
        projects = grouped[group_name]
        lines.extend(_render_category_section(group_name, projects, taxonomy))

    # ── EXCLUDED ──
    if excluded:
        lines.append("## Excluded Projects")
        lines.append("")
        lines.append(f"**{len(excluded)} Projekte** mit Score < 50 (zu wenig Daten oder unbestätigt).")
        lines.append("")
        lines.append("<details>")
        lines.append("<summary>Excluded Liste anzeigen</summary>")
        lines.append("")
        for e in sorted(excluded, key=lambda x: x.get("stars", 0), reverse=True)[:50]:
            repo = e.get("repository", "?")
            stars = format_stars(e.get("stars", 0))
            lines.append(f"- [{repo}](https://github.com/{repo}) — Stars:{stars}")
        if len(excluded) > 50:
            lines.append(f"- ... und {len(excluded) - 50} weitere")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # ── FOOTER ──
    lines.append("---")
    lines.append("")
    lines.append("## Ueber das Compendium")
    lines.append("")
    lines.append("Generiert durch 5-Loop Research Orchestrator mit Meta-Loop Controller.")
    lines.append("")
    lines.append(f"| Ressource | Beschreibung |")
    lines.append(f"|---|---|")
    lines.append(f"| [CATALOG.md](CATALOG.md) | Volle kategorisierte Liste |")
    lines.append(f"| [LANDSCAPE.md](LANDSCAPE.md) | Architektur-Uebersicht |")
    lines.append(f"| [TOP-PICKS.md](TOP-PICKS.md) | Kuratierte Auswahl |")
    lines.append(f"| [TRENDING.md](TRENDING.md) | Momentum-Analyse |")
    lines.append(f"| [METHODOLOGY.md](METHODOLOGY.md) | Scoring |")
    lines.append(f"| [AGENTS.md](AGENTS.md) | Agent-Instructions |")
    lines.append(f"| [data/](data/) | Maschinenlesbare Daten |")
    lines.append(f"| [scripts/](scripts/) | Automatisierung |")
    lines.append("")
    lines.append("```bash")
    lines.append("# Alles regenerieren (braucht GitHub Token fuer API)")
    lines.append("make all")
    lines.append("# Meta-Loop starten")
    lines.append("python scripts/meta_loop.py --continuous")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append(f"*Snapshot: {snapshot_date} | {len(entries)} Projekte | Meta-Loop Controller*")

    return "\n".join(lines)


def render_readme(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Render README.md as a showcase front page plus the complete catalog."""
    entries = catalog.get("entries", [])
    accepted = [e for e in entries if e.get("score", 0) >= 50]
    excluded = [e for e in entries if e.get("score", 0) < 50]
    sorted_all = sorted(accepted, key=lambda x: x.get("score", 0), reverse=True)

    essential = sum(1 for e in accepted if e.get("score", 0) >= 85)
    strong = sum(1 for e in accepted if 75 <= e.get("score", 0) < 85)
    emerging = sum(1 for e in accepted if 65 <= e.get("score", 0) < 75)
    watchlist = sum(1 for e in accepted if 50 <= e.get("score", 0) < 65)

    lines = [
        "# Agentic Engineering Compendium",
        "",
        "> A searchable, evidence-oriented map of the AI-agent engineering ecosystem.",
        "",
        f"![Snapshot](https://img.shields.io/badge/snapshot-{snapshot_date.replace('-', '--')}-111111)",
        f"![Projects](https://img.shields.io/badge/projects-{len(entries)}-2563eb)",
        f"![Accepted](https://img.shields.io/badge/accepted-{len(accepted)}-16a34a)",
        "![Categories](https://img.shields.io/badge/categories-81-7c3aed)",
        "![Format](https://img.shields.io/badge/format-GitHub%20Markdown-0f172a)",
        "",
        "| Projects | Accepted | Excluded | Top-level categories | Subcategories | Snapshot |",
        "|---:|---:|---:|---:|---:|---|",
        f"| {len(entries)} | {len(accepted)} | {len(excluded)} | 10 | 81 | {snapshot_date} |",
        "",
        "## Start Here",
        "",
        "| Need | Start with |",
        "|---|---|",
        "| Best production-ready projects | [Top 25 Projects](#top-25-projects) |",
        "| Category navigation | [Contents](#contents) |",
        "| Ecosystem shape | [Ecosystem Map](#ecosystem-map) |",
        "| Full data dump in one page | [Complete Catalog](#complete-catalog) |",
        "| Scoring rules | [Methodology](METHODOLOGY.md) |",
        "",
        "## Ecosystem Map",
        "",
        "```mermaid",
        "flowchart LR",
        '  root["Agentic Engineering"]',
        '  root --> apps["Applications & Interfaces"]',
        '  root --> code["Coding Agents"]',
        '  root --> ctx["Context & Memory"]',
        '  root --> exec["Execution & Interaction"]',
        '  root --> fw["Frameworks & Runtimes"]',
        '  root --> mcp["MCP Ecosystem"]',
        '  root --> ops["Reliability & Operations"]',
        '  root --> infra["Models & Infrastructure"]',
        '  root --> skills["Skills & Interop"]',
        "  fw --> mcp",
        "  code --> exec",
        "  ctx --> ops",
        "  apps --> skills",
        "```",
        "",
        "---",
        "",
    ]

    lines.extend(_render_toc(taxonomy, accepted))

    lines.extend([
        "## Score Distribution",
        "",
        "| Rating | Score range | Projects |",
        "|---|---:|---:|",
        f"| Essential | 85+ | {essential} |",
        f"| Strong | 75-84 | {strong} |",
        f"| Emerging | 65-74 | {emerging} |",
        f"| Watchlist | 50-64 | {watchlist} |",
        f"| Excluded | <50 | {len(excluded)} |",
        "",
        "---",
        "",
        "## Top 25 Projects",
        "",
        "| # | Project | Stars | Score | Category |",
        "|---:|---|---:|---:|---|",
    ])

    for i, p in enumerate(sorted_all[:25], 1):
        repo = clean_text(p.get("repository", "?"))
        stars = format_stars(p.get("stars", 0))
        score = p.get("score", 0)
        cat = clean_text(get_category_name(taxonomy, p.get("primary_category", "")))
        lines.append(f"| {i} | [{repo}](https://github.com/{repo}) | {stars} | {score} | {cat} |")

    lines.extend([
        "",
        "---",
        "",
        "# Complete Catalog",
        "",
        f"**{len(accepted)} projects** grouped by category. Expand a project for details.",
        "",
    ])

    grouped = {}
    for e in accepted:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                grouped.setdefault(group["name"], []).append(e)
                break

    for group_name in sorted(grouped.keys()):
        lines.extend(_render_category_section(group_name, grouped[group_name], taxonomy))

    if excluded:
        lines.extend([
            "## Excluded Projects",
            "",
            f"**{len(excluded)} projects** with score < 50 (insufficient data or not yet confirmed).",
            "",
            "<details>",
            "<summary>Show excluded projects</summary>",
            "",
        ])
        for e in sorted(excluded, key=lambda x: x.get("stars", 0), reverse=True)[:50]:
            repo = clean_text(e.get("repository", "?"))
            stars = format_stars(e.get("stars", 0))
            lines.append(f"- [{repo}](https://github.com/{repo}) - {stars} stars")
        if len(excluded) > 50:
            lines.append(f"- ... and {len(excluded) - 50} more")
        lines.extend(["", "</details>", ""])

    lines.extend([
        "---",
        "",
        "## About",
        "",
        "Generated by the five-loop research orchestrator with a meta-loop controller.",
        "",
        "| Resource | Description |",
        "|---|---|",
        "| [CATALOG.md](CATALOG.md) | Full categorized list |",
        "| [LANDSCAPE.md](LANDSCAPE.md) | Architecture overview |",
        "| [TOP-PICKS.md](TOP-PICKS.md) | Curated high-score set |",
        "| [TRENDING.md](TRENDING.md) | Momentum analysis |",
        "| [METHODOLOGY.md](METHODOLOGY.md) | Scoring method |",
        "| [AGENTS.md](AGENTS.md) | Agent instructions |",
        "| [data/](data/) | Machine-readable data |",
        "| [scripts/](scripts/) | Automation |",
        "",
        "```bash",
        "# Regenerate docs from checked-in data",
        "make all",
        "# Start the meta-loop controller",
        "python scripts/meta_loop.py --continuous",
        "```",
        "",
        "---",
        f"*Snapshot: {snapshot_date} | {len(entries)} projects | Meta-loop controller*",
    ])

    return "\n".join(lines)


def render_catalog(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Render CATALOG.md — full categorized listing."""
    entries = catalog.get("entries", [])
    accepted = [e for e in entries if e.get("score", 0) >= 50]

    lines = []
    lines.append("# Full Catalog")
    lines.append("")
    lines.append(f"> {len(accepted)} accepted projects across the AI-agent ecosystem.")
    lines.append("")
    lines.append(f"**Snapshot:** {snapshot_date}")
    lines.append("")

    # Group by top-level category
    grouped = {}
    for e in accepted:
        pc = e.get("primary_category", "")
        for group in taxonomy.get("categories", {}).values():
            if pc in group.get("subcategories", {}):
                grouped.setdefault(group["name"], []).append(e)
                break

    for group_name in sorted(grouped.keys()):
        projects = sorted(grouped[group_name], key=lambda x: x.get("score", 0), reverse=True)
        lines.append(f"## {group_name}")
        lines.append("")

        for p in projects:
            repo = p.get("repository", "?")
            desc = (p.get("description") or "")[:150]
            score = p.get("score", 0)
            stars = format_stars(p.get("stars", 0))
            lang = p.get("primary_language") or p.get("language") or ""
            lines.append(f"### [{repo}](https://github.com/{repo})")
            lines.append("")
            lines.append(f"**Stars:** {stars} | **Score:** {score} | **Language:** {lang or '?'} | "
                         f"**Status:** {official_badge(p.get('official_status', 'community'))}")
            lines.append("")
            if desc:
                lines.append(f">{desc}")
                lines.append("")
            if p.get("topics"):
                lines.append(" ".join(f"`{t}`" for t in p["topics"][:5]))
                lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def render_build_your_own(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Build-your-own style tutorial listing."""
    entries = catalog.get("entries", [])
    tutorials = [e for e in entries if e.get("primary_category") and e.get("primary_category", "").startswith("A.")]
    
    lines = []
    lines.append("# Build Your Own")
    lines.append(f"")
    lines.append("> Learn agentic engineering from first principles.")
    lines.append("")
    
    if tutorials:
        for t in tutorials:
            repo = t.get("repository", "?")
            desc = (t.get("description") or "No description")[:200]
            lines.append(f"- [{repo}](https://github.com/{repo}) — {desc}")
    else:
        lines.append("No tutorials cataloged yet.")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")
    
    return "\n".join(lines)


def render_landscape(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Ecosystem landscape overview."""
    entries = catalog.get("entries", [])
    accepted = [e for e in entries if e.get("score", 0) >= 50]

    lines = []
    lines.append("# Ecosystem Landscape")
    lines.append("")
    lines.append("> How the layers of the AI-agent ecosystem fit together.")
    lines.append("")
    lines.append(f"**Snapshot:** {snapshot_date}")
    lines.append("")
    
    for group in taxonomy.get("categories", {}).values():
        gname = group["name"]
        subcats = group.get("subcategories", {})
        
        # Count projects in this group
        count = 0
        for e in accepted:
            pc = e.get("primary_category", "")
            if pc in subcats:
                count += 1
        
        lines.append(f"### {gname}")
        lines.append("")
        lines.append(f"_{group.get('description', '')}_")
        lines.append("")
        lines.append(f"**{count} projects** across {len(subcats)} subcategories:")
        lines.append("")
        for sc_id, sc in sorted(subcats.items()):
            sc_count = sum(1 for e in accepted if e.get("primary_category") == sc_id)
            lines.append(f"- **{sc['name']}** ({sc_count})")
        lines.append("")

    return "\n".join(lines)


def render_top_picks(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Curated top picks."""
    entries = catalog.get("entries", [])
    strong = [e for e in entries if e.get("score", 0) >= 75]

    lines = []
    lines.append("# Top Picks")
    lines.append("")
    lines.append(f"> {len(strong)} projects with Strong rating (score >= 75)")
    lines.append("")
    lines.append(f"**Snapshot:** {snapshot_date}")
    lines.append("")

    for p in sorted(strong, key=lambda x: x.get("score", 0), reverse=True):
        repo = p.get("repository", "?")
        desc = (p.get("description") or "No description")[:200]
        score = p.get("score", 0)
        stars = format_stars(p.get("stars", 0))
        cat = p.get("primary_category", "")
        lines.append(f"### [{repo}](https://github.com/{repo})")
        lines.append(f"")
        lines.append(f"**Score:** {score}/100 | **Stars:** {stars} | **Category:** {get_category_name(taxonomy, cat)}")
        lines.append("")
        if desc:
            lines.append(f">{desc}")
            lines.append("")

    return "\n".join(lines)


def render_trending(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Trending / momentum analysis."""
    entries = catalog.get("entries", [])
    def get_momentum(e):
        stars = e.get("stars", 0)
        trend = e.get("trend_data") or {}
        stars_30d = trend.get("stars_30d")
        if stars_30d is None:
            return 0
        growth = max(0, stars - stars_30d)
        growth_rate = growth / max(1, stars_30d)
        return growth * (1 + growth_rate)
    sorted_trending = sorted(entries, key=get_momentum, reverse=True)

    lines = []
    lines.append("# Trending")
    lines.append("")
    lines.append("> Fast-growing projects sorted by 30-day growth and growth velocity.")
    lines.append("")
    lines.append(f"**Snapshot:** {snapshot_date}")
    lines.append("")

    lines.append("| # | Project | Stars | Score |")
    lines.append("|---|---|---|---|")
    for i, p in enumerate(sorted_trending[:50], 1):
        repo = p.get("repository", "?")
        stars = format_stars(p.get("stars", 0))
        score = p.get("score", 0)
        lines.append(f"| {i} | [{repo}](https://github.com/{repo}) | {stars} | {score} |")

    return "\n".join(lines)


def render_watchlist(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Watchlist — promising but unverified."""
    watchlist = [e for e in catalog.get("entries", []) if 50 <= e.get("score", 0) < 65]

    lines = []
    lines.append("# Watchlist")
    lines.append("")
    lines.append(f"> {len(watchlist)} projects with potential but needing verification")
    lines.append("")
    lines.append(f"**Snapshot:** {snapshot_date}")
    lines.append("")

    for p in sorted(watchlist, key=lambda x: x.get("stars", 0), reverse=True):
        repo = p.get("repository", "?")
        stars = format_stars(p.get("stars", 0))
        score = p.get("score", 0)
        lines.append(f"- [{repo}](https://github.com/{repo}) — Stars:{stars}, Score:{score}")

    return "\n".join(lines)


def render_archived(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Archived / stale projects."""
    archived = [e for e in catalog.get("entries", []) if e.get("archived")]

    lines = []
    lines.append("# Archived / Stale Projects")
    lines.append("")
    if archived:
        for p in archived:
            lines.append(f"- {p.get('repository', '?')}")
    else:
        lines.append("No archived projects in the catalog.")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")

    return "\n".join(lines)


def render_methodology(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Scoring methodology."""
    lines = []
    lines.append("# Methodology")
    lines.append("")
    lines.append("## Scoring Dimensions")
    lines.append("")
    lines.append("| Dimension | Weight | Description |")
    lines.append("|---|---|---|")
    dims = [
        ("Relevance", 20, "How central to the AI-agent ecosystem"),
        ("Maintenance", 15, "Recent commits, releases, issue response"),
        ("Adoption", 15, "Stars, forks, community size (logarithmic)"),
        ("Momentum", 10, "Growth rate, recent activity"),
        ("Documentation", 10, "README quality, docs site, examples"),
        ("Production Readiness", 10, "Maturity, stability, deployment support"),
        ("Security", 10, "License, security policy, vulnerability handling"),
        ("Interoperability", 5, "APIs, standards, integrations"),
        ("Community", 3, "Contributors, discussions, ecosystem"),
        ("Uniqueness", 2, "Differentiation from similar projects"),
    ]
    for name, weight, desc in dims:
        lines.append(f"| {name} | {weight}% | {desc} |")
    lines.append("")
    lines.append("## Rules")
    lines.append("")
    rules = [
        "Stars use logarithmic weighting (100k stars != 100x 1k stars)",
        "Excluded (score < 50): too few data, inactive, or unconfirmed",
        "Null metadata = unknown (never invented)",
        "Security-sensitive MCP servers require explicit security notes",
        "Official status requires supporting evidence",
        "All descriptions must be neutral (12-30 words, no marketing)",
    ]
    for r in rules:
        lines.append(f"- {r}")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")

    return "\n".join(lines)


def render_contributing(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Contribution guidelines."""
    lines = []
    lines.append("# Contributing")
    lines.append("")
    lines.append("## How to Add a Project")
    lines.append("")
    lines.append("1. Open an issue using the **Suggest Project** template")
    lines.append("2. Include the GitHub repository URL")
    lines.append("3. Provide a brief description (12-30 words, neutral)")
    lines.append("4. Suggest a primary category from the taxonomy")
    lines.append("")
    lines.append("## How to Correct Metadata")
    lines.append("")
    lines.append("Use the **Correct Metadata** template for any errors.")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")

    return "\n".join(lines)


def render_security(catalog: dict, taxonomy: dict, snapshot_date: str) -> str:
    """Security policy."""
    lines = []
    lines.append("# Security Policy")
    lines.append("")
    lines.append("## Reporting a Vulnerability")
    lines.append("")
    lines.append("Please open an issue using the **Security Concern** template.")
    lines.append("")
    lines.append("## Security-Sensitive Projects")
    lines.append("")
    lines.append("The following MCP servers have security implications:")
    lines.append("")
    security_items = [e for e in catalog.get("entries", []) if e.get("security_notes")]
    for item in security_items:
        lines.append(f"- [{item['repository']}](https://github.com/{item['repository']})")
        for note in item.get("security_notes", []):
            lines.append(f"  - {note}")
    lines.append("")
    lines.append(f"*Snapshot: {snapshot_date}*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render catalog to Markdown")
    parser.add_argument("--catalog", required=True, help="Path to catalog.json")
    parser.add_argument("--taxonomy", required=True, help="Path to taxonomy.json")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    catalog = load_catalog(args.catalog)
    taxonomy = load_taxonomy(args.taxonomy)
    snapshot_date = catalog.get("snapshot_date", "2026-07-07")

    # Render functions map
    renderers = {
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

    print("=" * 60)
    print("Rendering (LOOP 5)")
    print("=" * 60)

    for filename, render_fn in renderers.items():
        output_path = os.path.join(args.output, filename)
        content = render_fn(catalog, taxonomy, snapshot_date)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        size = os.path.getsize(output_path)
        kb = size / 1024
        if kb > 100:
            print(f"  Generated {filename} ({kb:.0f} KB)")
        else:
            print(f"  Generated {filename}")

    print("Rendering complete! Generated 11 files.")


if __name__ == "__main__":
    main()
