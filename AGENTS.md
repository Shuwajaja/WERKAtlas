# Agentic Engineering Compendium — Agent Instructions

## Purpose

This repository is an evidence-backed, reproducible open-source knowledge base mapping the entire modern AI-agent ecosystem. It is structured like `build-your-own-x` but covers the full agent stack.

## Repository layout

```
agentic-engineering-compendium/
├── README.md              # Landing page
├── BUILD-YOUR-OWN.md      # Build-from-scratch tutorials
├── CATALOG.md             # Full human-readable catalog
├── LANDSCAPE.md           # Ecosystem layer map
├── TOP-PICKS.md           # Curated selections
├── TRENDING.md            # Momentum and growth
├── WATCHLIST.md           # Promising but unverified
├── ARCHIVED.md            # Historical / educational
├── METHODOLOGY.md         # Scoring, evidence rules
├── CONTRIBUTING.md        # How to contribute
├── SECURITY.md            # Security policy
├── data/                  # Machine-readable catalog
│   ├── catalog.json
│   ├── catalog.csv
│   ├── catalog.schema.json
│   ├── candidates.ndjson
│   ├── rejected.json
│   ├── sources.json
│   └── taxonomy.json
├── research/              # Research artifacts
│   ├── PROGRESS.md
│   ├── DECISIONS.md
│   ├── SOURCE-MAP.md
│   ├── QUERY-MATRIX.md
│   ├── LOOP-1.md .. LOOP-5.md
│   └── subagents/
├── scripts/               # Automation
│   ├── collect.py
│   ├── enrich.py
│   ├── classify.py
│   ├── score.py
│   ├── render.py
│   ├── validate.py
│   └── check_links.py
├── tests/
└── .github/
```

## Agent rules

1. **Only the main agent writes canonical files** (`data/catalog.json`, `README.md`, taxonomy files).
2. **Subagents write only to `research/subagents/`** — never to canonical files.
3. **Every accepted project must have evidence** from canonical repository, official docs, or official registry.
4. **No invented metadata.** Null = unknown.
5. **Neutral descriptions only** (12–30 words, no marketing language).
6. **Stars ≠ quality.** Score uses logarithmic star weighting.
7. **Archived/stale status must be visible.** Do not silently delete historical projects.
8. **Security-sensitive MCP servers** require explicit security notes.
9. **Respect rate limits.** Cache API responses. Use retries and timeouts.
10. **No execution of third-party code.**
11. **No pushing to remote** unless explicitly enabled.

## Loop protocol

- LOOP 1: Taxonomy, source mapping, broad discovery (maximize recall)
- LOOP 2: Metadata enrichment, normalization, deduplication
- LOOP 3: Deep verification and trust review (subagents)
- LOOP 4: Scoring, trends, gap analysis
- LOOP 5: Editorial production, rendering, final audit

Each loop produces a `research/LOOP-N.md` report and the quality gate must pass before proceeding.

## Snapshot date

2026-07-07
