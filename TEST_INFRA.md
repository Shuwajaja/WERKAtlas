# WERKAtlas E2E Test Infrastructure (TEST_INFRA)

This document provides a comprehensive technical overview of the dual-layer E2E testing framework designed for the modernized WERKAtlas project.

---

## 1. Test Architecture Overview

WERKAtlas uses a **dual-layer** test suite to validate both the data processing backend and the Astro-based web frontend:

1. **Data Pipeline E2E Suite (Python + pytest)**:
   - Validates the data scripts (`score.py`, `classify.py`, `export.py`, `update_trends.py`, `validate.py`).
   - Ensures data integrity, scoring weights, taxonomy rules, exporter format generation, and trend calculation.
   - Files: `tests/test_e2e_pipeline.py` (54 tests), along with existing unit tests under `tests/`.

2. **Astro Frontend E2E Suite (Playwright + TypeScript)**:
   - Validates the interactive features, page routing, search/filtering, and branding layout of the website.
   - Runs against the Astro dev server or build preview at `http://localhost:4321/WERKAtlas/`.
   - Files: `tests/e2e/*.spec.ts` (52 tests), structured in `tests/e2e/explorer.spec.ts`, `tests/e2e/comparison.spec.ts`, `tests/e2e/pages.spec.ts`, and `tests/e2e/brand.spec.ts`.

---

## 2. Dependencies & Installation

### Backend Pipeline Suite
- **Python Version**: 3.10.x
- **Packages**:
  - `pytest` (Test runner)
  - Standard libraries used: `json`, `csv`, `math`, `sys`, `os`, `subprocess`, `unittest.mock`

Installation:
```bash
pip install pytest
```

### Frontend Playwright Suite
- **Node.js**: v22+
- **Packages**:
  - `@playwright/test` (E2E browser testing framework)
  - `typescript` (For compiling TypeScript spec files)

Installation:
```bash
cd tests/e2e
npm install
npx playwright install
```

---

## 3. Mock Strategy & Isolation

### Data Pipeline Tests
- **Temporary Directories (`tmp_path`)**: The suite leverages pytest's built-in `tmp_path` fixture to dynamically create separate input catalog files and output directories. This ensures that the production catalog (`data/catalog.json`) is never modified or polluted by E2E test runs.
- **Git Simulation (`unittest.mock.patch`)**: The trend calculation tests mock the Git repository history loader `update_trends.get_catalog_from_git` to return deterministic historical snapshots (e.g. mock stars 30 and 90 days ago). This allows E2E testing of the momentum delta algorithms without running slow Git command trees.
- **Argv patching**: Python's `sys.argv` is mocked during tests to execute the command-line entry points of pipeline scripts (`main()`) directly inside the same process.

### Frontend Playwright Tests
- **Data-TestId Anchors**: Instead of relying on fragile CSS class structures or text content that might change, the Playwright selectors strictly target stable `data-testid` attributes (e.g. `data-testid="search-input"`, `data-testid="project-card"`, `data-testid="compare-btn"`).
- **Astro Server Isolation**: Tests navigate to the Astro application configured in `playwright.config.ts`. The config points to `http://localhost:4321/WERKAtlas/`.

---

## 4. Automation & Execution Commands

### Running Data Pipeline Tests
To run all Python pipeline tests:
```bash
python -m pytest tests/test_e2e_pipeline.py
```
To run all tests in the project (including unit tests):
```bash
python -m pytest
```

### Running Frontend Playwright Tests
1. Ensure the Astro site is running locally:
   ```bash
   npm run dev -- --port 4321
   ```
2. Run the Playwright suite:
   ```bash
   cd tests/e2e
   npx playwright test
   ```
3. To view the HTML test report:
   ```bash
   npx playwright show-report
   ```
