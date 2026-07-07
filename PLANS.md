# Execution Plan

## Overview

Build the Agentic Engineering Compendium — a comprehensive, evidence-backed, reproducible knowledge base of the AI-agent ecosystem.

## Phase 0: Setup & Infrastructure ✓
- [x] Create project directory structure
- [x] Set up control files (AGENTS.md, PLANS.md, research files)
- [x] Check GitHub CLI auth and API access
- [x] Create schema, taxonomy, and data structures
- [x] Create Makefile and script stubs
- [x] Create query matrix and source map

## LOOP 1: Taxonomy, Source Mapping, Broad Discovery
- [ ] Implement `collect.py` — GitHub API search and collection
- [ ] Inspect official orgs & registries (MCP, Anthropic, OpenAI, etc.)
- [ ] Run query matrix through GitHub API
- [ ] Collect broad candidate pool (aim 1000+)
- [ ] Store in `data/candidates.ndjson`
- [ ] Produce `research/LOOP-1.md`

## LOOP 2: Metadata Enrichment & Deduplication
- [ ] Implement `enrich.py` — fetch repo metadata
- [ ] Implement `classify.py` — classify categories
- [ ] Normalize names, resolve forks/mirrors
- [ ] Create `data/catalog.json`
- [ ] Produce `research/LOOP-2.md`

## LOOP 3: Deep Verification & Trust Review
- [ ] Spawn 6 parallel subagents for category clusters
- [ ] Each subagent verifies and reports findings
- [ ] Manually verify Essential candidates
- [ ] Create `data/rejected.json`
- [ ] Produce `research/LOOP-3.md`

## LOOP 4: Scoring, Trends, Gap Analysis
- [ ] Implement `score.py` with full scoring system
- [ ] Calculate scores and confidence
- [ ] Rank within categories
- [ ] Identify gaps and search for underrepresented
- [ ] Check emerging projects
- [ ] Produce `research/LOOP-4.md`

## LOOP 5: Editorial Production & Final Audit
- [ ] Implement `render.py` — generate all Markdown files
- [ ] Implement `validate.py` — validation checks
- [ ] Implement `check_links.py` — link checker
- [ ] Generate: README, CATALOG, LANDSCAPE, TOP-PICKS, TRENDING, WATCHLIST, ARCHIVED, METHODOLOGY, BUILD-YOUR-OWN
- [ ] Run validation
- [ ] Final self-audit
- [ ] Produce `research/LOOP-5.md`
- [ ] Final report

## Success Criteria

300+ accepted projects, 1000+ candidates evaluated, all categories covered, scoring reproducible, no duplicates, all checks pass.
