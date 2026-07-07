# Methodology

**Snapshot date:** 2026-07-07

## Overview

The Agentic Engineering Compendium uses a structured, evidence-backed methodology to catalog
and evaluate projects in the AI-agent ecosystem. The system runs in five loops:

1. **Taxonomy, Source Mapping, Broad Discovery** — Maximize recall
2. **Metadata Enrichment & Deduplication** — Convert to structured records
3. **Deep Verification & Trust Review** — Manual review of important projects
4. **Scoring, Trends, Gap Analysis** — Rank and identify gaps
5. **Editorial Production & Final Audit** — Generate polished output

## Scoring System (0-100)

| Component | Max | Description |
|---|---|---|
| Relevance | 20 | Alignment with modern AI-agent engineering |
| Maintenance | 15 | Commit frequency, issue resolution, release cadence |
| Adoption | 10 | Stars (logarithmic), forks, ecosystem usage |
| Momentum | 10 | Recent pushes, releases, community activity |
| Documentation | 10 | README quality, docs site, examples |
| Production Readiness | 10 | Maturity, stability, deployment support |
| Security | 10 | License, security policy, vulnerability handling |
| Interoperability | 5 | Protocol support, multi-language, standards |
| Community | 5 | Contributor diversity, governance, responsiveness |
| Uniqueness | 5 | Technical novelty, educational value, filling a gap |

### Star Scoring
Logarithmic: ln(stars + 1) / ln(100001) * 10. This prevents star count from dominating.

### Labels
- **Essential (85-100):** Core infrastructure, widely adopted, well-maintained
- **Strong (75-84):** Production-quality, recommended for most use cases
- **Emerging (65-74):** Promising, gaining traction, worth watching
- **Watchlist (50-64):** Interesting but needs more verification
- **Excluded (<50):** Does not meet quality or relevance thresholds

## Evidence Requirements

Every accepted project must have evidence from:
- Canonical GitHub repository
- Official documentation
- Official registry entry
- Official organization

## Discovery Sources (Hierarchical)

1. **Tier 1:** Official GitHub orgs, SDKs, registries, specifications
2. **Tier 2:** Curated awesome lists, ecosystem directories, package registries
3. **Tier 3:** Social media, blogs, newsletters (discovery only, not sufficient for acceptance)

## Penalties
- Archived repository: Severe penalty
- Missing or unclear license: Moderate penalty
- No meaningful agent relevance: Exclusion
- Abandoned fork: Exclusion
- Misleading README or marketing-only repos: Exclusion

*Snapshot: 2026-07-07*