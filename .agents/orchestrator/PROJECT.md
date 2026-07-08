# Project: WERKAtlas Modernization

## Architecture
- **Data Source**: Canonical `data/catalog.json` containing metadata, links, description, and scores for agentic engineering projects.
- **Python Data Pipeline**:
  - `scripts/score.py`: Computes individual metric scores and a total score (max 100).
  - `scripts/validate.py` / pytest: Validates JSON against schema and runs sanity tests.
  - New Python module/script to export `catalog.json` to JSON, NDJSON, and CSV format, compute historical trends/momentum, and enforce strict classification without naive fallbacks.
- **Astro Static Site**:
  - Located under `/web` or root. Base path: `/WERKAtlas/`.
  - Driven by the generated JSON catalog.
  - Atlas Explorer: Search, filter (multi-faceted), sort, and compare view.
  - Pages: Main page, category pages, project detail pages.
  - WERK Brand: Custom CSS tokens, industrial/editorial styling, high readability, newsreader-style headings.

## Milestones

### Implementation Track
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | UTF-8 Fix & Test Baseline | Fix encoding issues in test suite so `pytest` runs cleanly on Windows. | None | DONE |
| M2 | Data Pipeline Enhancements | Align scoring weights to exactly 100 points, update `catalog.schema.json`, fix uniqueness/security score rules, remove naive fallback classification, implement export to JSON, NDJSON, CSV, and implement historical trend/momentum computation. | M1 | DONE |
| M3 | Astro Setup & Design System | Setup Astro + TypeScript static site with `/WERKAtlas/` base path. Define CSS tokens, industrial/editorial style. | M2 | PLANNED |
| M4 | Static Site Pages & Atlas Explorer | Build main page, category pages, project detail pages, and Atlas Explorer (with search, multi-faceted filtering, sorting, and comparison view). | M3 | PLANNED |
| M5 | CI/CD & Deploy Workflow | Setup GitHub Actions for validation and pages deployment. | M4 | PLANNED |
| M6 | E2E Integration and Adversarial Hardening | Pass E2E test suite (Tiers 1-4) and run adversarial coverage hardening (Tier 5). | M5, E2ET | PLANNED |

### E2E Testing Track
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2ET | E2E Test Suite | Design and implement an opaque-box E2E test suite covering Tiers 1-4. Generate `TEST_READY.md`. | M1 | PLANNED |

## Interface Contracts
- **Data Exporter API**: The exporter script will output:
  - `dist/catalog.json`: Full canonical JSON catalog.
  - `dist/catalog.ndjson`: NDJSON format of the catalog.
  - `dist/catalog.csv`: Flattened CSV format.
  - Trend metrics: each entry must have a trend/momentum field computed from history.
- **Astro Component Contracts**:
  - `base`: `/WERKAtlas/`
  - Comparison mode: URL search param or local storage selection state for comparing up to 3 projects.

## Code Layout
- `data/catalog.json`: Source catalog
- `data/catalog.schema.json`: Source schema
- `scripts/`: Data pipeline and scripts
- `tests/`: Unit and pipeline tests
- `web/` or root: Astro project directory (TBD)
- `tests/e2e/`: E2E test cases
