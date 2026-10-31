# Agentic Engineering Compendium — Agent Instructions

Aktueller Stand, Branch-Inventar und Dokumentenkarte: [`STATUS.md`](STATUS.md).

## Purpose

This repository is an evidence-backed, reproducible open-source knowledge base mapping the entire modern AI-agent ecosystem. It is structured like `build-your-own-x` but covers the full agent stack.

## Repository layout

```
agentic-engineering-compendium/
├── STATUS.md              # Führende Statusdatei
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
├── docs/                  # Operative Notizen, Tests, Archiv
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

## Cursor Cloud specific instructions

Catalog scripts are Python standard library. The website is the Astro app in `web/`, configured with `base: '/WERKAtlas/'`.

- Python tests: `python3 -m pytest tests/`
- Catalog schema check: `python scripts/validate.py --catalog data/catalog.json --schema data/catalog.schema.json`
- Dev server (also started on agent boot): from `web/`, `npm run dev -- --host 0.0.0.0 --port 4321`. The site is `http://127.0.0.1:4321/WERKAtlas/`.
- Static build: `npm run build` in `web/` (output in `web/dist`).
- Playwright specs are in `tests/e2e` and use `http://localhost:4321/WERKAtlas/` as `baseURL`. Run `npx playwright test` from `tests/e2e` only while that dev server is up.
