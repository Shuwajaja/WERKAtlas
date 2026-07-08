# Handoff Report: E2E Test Infrastructure Design

This report presents the analysis of the current WERKAtlas codebase and environment, and proposes a concrete E2E testing infrastructure for the Data Pipeline and the Astro Static Site.

---

## 1. Observation

### Codebase Structure
Direct exploration of `C:\Workplace\agentic-engineering-compendium` reveals the following structure:
- **Scripts Directory** (`C:\Workplace\agentic-engineering-compendium\scripts\`):
  - `score.py`: Computes individual metric scores and a total score.
  - `validate.py`: Validates catalog JSON data against `catalog.schema.json`.
  - `render.py`: Generates the static Markdown files (e.g. `README.md`, `CATALOG.md`, `LANDSCAPE.md`).
- **Tests Directory** (`C:\Workplace\agentic-engineering-compendium\tests\`):
  - `test_scoring.py`: Validates log star logic and scoring ranges.
  - `test_duplicates.py`: Checks for duplicate repositories/IDs.
  - `test_schema.py`: Verifies existence and requirements of `data/catalog.json`.
  - `test_rendering.py`: Verifies generated Markdown outputs.
- **Data Directory** (`C:\Workplace\agentic-engineering-compendium\data\`):
  - `catalog.json`: The core JSON repository database.
  - `catalog.schema.json`: JSON Schema for catalog entries.
  - `taxonomy.json`: Classification structure.

### Environment Capabilities
- **Python**: Installed (v3.10.10).
- **Python Packages**:
  - `pytest` (v9.0.2)
  - `pytest-asyncio` (v1.3.0)
  - `pytest-cov` (v7.1.0)
  - `pytest-repeat` (v0.9.4)
  - `pytest-rerunfailures` (v16.1)
  - `pytest-timeout` (v2.4.0)
  - `pytest-xdist` (v3.8.0)
- **Node & npm**:
  - `node` (v22.14.0)
  - `npm` (v10.9.2)

### Test Run Baseline
Running the test command:
```powershell
python -m pytest
```
Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.10.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Workplace\agentic-engineering-compendium
plugins: anyio-4.12.1, deepeval-3.9.6, hypothesis-6.152.2, langsmith-0.7.22, asyncio-1.3.0, cov-7.1.0, repeat-0.9.4, rerunfailures-16.1, timeout-2.4.0, xdist-3.8.0, respx-0.23.1
collected 17 items

tests\test_duplicates.py ..                                              [ 11%]
tests\test_rendering.py ......                                           [ 47%]
tests\test_schema.py ....                                                [ 70%]
tests\test_scoring.py .....                                              [100%]
============================= 17 passed in 1.01s ==============================
```

---

## 2. Logic Chain

1. **Python Environment & Data Pipeline E2E**:
   - The current data pipeline relies entirely on Python scripts (`scripts/score.py`, `scripts/validate.py`, etc.).
   - The testing suite is written using `pytest`, which runs successfully in 1.01 seconds.
   - Therefore, the Data Pipeline E2E tests should be implemented as a new test file under `tests/` (e.g., `tests/test_pipeline_e2e.py`) to run alongside the existing test suite, ensuring frictionless integration.

2. **Node Environment & Astro Frontend E2E**:
   - The Astro Static Site will be a Node-based project written in TypeScript.
   - Node.js (v22.14) and npm (v10.9.2) are available locally.
   - Frontend E2E testing (asserting interactions like searching, filtering, and visual regression) is best served by **Playwright**.
   - Therefore, a Node-based Playwright configuration co-located with the Astro project (in `web/` or `/tests/e2e/`) is the optimal approach.

---

## 3. Caveats

- **Astro Code Base**: The Astro project (`/web` or root) is currently in the **PLANNED** phase (M3/M4) and has not yet been checked in.
- **Playwright Installation**: Playwright npm packages are not yet installed in `agentic-engineering-compendium`. They must be added once `web/package.json` is initialized.

---

## 4. Conclusion & Recommended Design

We recommend a **Dual-Layer E2E Testing Framework** separating the data pipeline verification from visual/behavioral static site testing.

### A. Data Pipeline E2E Tests (Python + Pytest)
Implement E2E test cases in `tests/test_pipeline_e2e.py` verifying:
1. **Total Weight Sum**: Sum of all 10 component weights inside `score.py` is exactly `100.0`.
2. **Score Bounds**: Every scored repository has `0 <= score <= 100`.
3. **Strict Classification**: Checks that `primary_category` and `secondary_categories` match the taxonomy.json entries without naive fallback classifications.
4. **Data Exporter Outputs**: Verifies that running the new exporter script generates:
   - `dist/catalog.json` (valid JSON)
   - `dist/catalog.ndjson` (newline-delimited JSON)
   - `dist/catalog.csv` (CSV format with expected header fields)
5. **Trend/Momentum Metrics**: Verifies that trend metrics are present, non-null, and correctly scaled based on historical metadata.

### B. Astro Frontend E2E Tests (Node.js + Playwright)
Create an E2E folder under `web/tests-e2e/` using TypeScript Playwright.

#### 1. Search & Filter Tests
Assert that typing in the search bar dynamically filters items, and checking categories/tags updates the results accordingly.
```typescript
import { test, expect } from '@playwright/test';

test.describe('Atlas Explorer Search & Filter', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/WERKAtlas/');
  });

  test('should search and filter projects', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search"]');
    await searchInput.fill('n8n');
    await expect(page.locator('.project-card')).toContainText('n8n');

    // Filter by category
    await page.click('text="Frameworks and runtimes"');
    await expect(page.locator('.project-card')).toHaveCount(1);
  });
});
```

#### 2. Project Comparison View
Verify that up to 3 selected projects can be compared side-by-side using URL search parameters (e.g., `?compare=repo1,repo2,repo3`) or local storage states.
```typescript
test('should display side-by-side comparison of up to 3 selected projects', async ({ page }) => {
  await page.goto('/WERKAtlas/?compare=n8n-io/n8n,openinterpreter/openinterpreter');
  const compareColumns = page.locator('.comparison-column');
  await expect(compareColumns).toHaveCount(2);
  await expect(compareColumns.first()).toContainText('n8n');
});
```

#### 3. Styling & Custom Design Tokens Assertions
Verify that the industrial/editorial layout styling is applied using brand colors and fonts.
```typescript
test('should verify custom CSS tokens and newsreader styling', async ({ page }) => {
  const heading = page.locator('h1');
  // Check newsreader-style headings (serif font-family or custom font class)
  await expect(heading).toHaveCSS('font-family', /serif/);
  // Check background / text readability
  await expect(page.locator('body')).toHaveCSS('background-color', 'rgb(255, 255, 255)'); // Example white/editorial bg
});
```

---

## 5. Verification Method

### Step 1: Verify Current Tests Pass
Run the pytest test suite to ensure the environment is correct:
```powershell
python -m pytest
```

### Step 2: Implement the Pipeline E2E Test
Create a new file `tests/test_pipeline_e2e.py` with mock validation logic matching the scoring weights.

### Step 3: Initialize Playwright E2E Setup
Once the Astro site is initialized in the `web/` directory:
```bash
cd web
npm init -y
npm init playwright@latest
```
Configure `playwright.config.ts` to use:
- `baseURL: 'http://localhost:4321/WERKAtlas/'`
- A local dev server configuration:
```typescript
webServer: {
  command: 'npm run dev',
  url: 'http://localhost:4321/WERKAtlas/',
  reuseExistingServer: !process.env.CI,
}
```
