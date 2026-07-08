# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: pages.spec.ts >> Feature 3: Categories & Project Detail Pages >> Tier 3: Navigation via breadcrumbs back to category and home
- Location: pages.spec.ts:91:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:4321/WERKAtlas/project/n8n-io-n8n/
Call log:
  - navigating to "http://localhost:4321/WERKAtlas/project/n8n-io-n8n/", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Feature 3: Categories & Project Detail Pages', () => {
  4   | 
  5   |   // ==============================================================================
  6   |   // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  7   |   // ==============================================================================
  8   | 
  9   |   test('Tier 1: Category list page has category header', async ({ page }) => {
  10  |     await page.goto('/WERKAtlas/category/mcp-ecosystem/');
  11  |     const header = page.locator('[data-testid="category-header"]');
  12  |     await expect(header).toBeVisible();
  13  |   });
  14  | 
  15  |   test('Tier 1: Category list page contains projects list', async ({ page }) => {
  16  |     await page.goto('/WERKAtlas/category/mcp-ecosystem/');
  17  |     const list = page.locator('[data-testid="category-project-list"]');
  18  |     await expect(list).toBeVisible();
  19  |   });
  20  | 
  21  |   test('Tier 1: Project detail page displays project title', async ({ page }) => {
  22  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
  23  |     const title = page.locator('[data-testid="project-title"]');
  24  |     await expect(title).toBeVisible();
  25  |   });
  26  | 
  27  |   test('Tier 1: Score breakdown card exists on detail page', async ({ page }) => {
  28  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
  29  |     const card = page.locator('[data-testid="score-breakdown-card"]');
  30  |     await expect(card).toBeVisible();
  31  |   });
  32  | 
  33  |   test('Tier 1: Repository metadata panel is present', async ({ page }) => {
  34  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
  35  |     const panel = page.locator('[data-testid="metadata-panel"]');
  36  |     await expect(panel).toBeVisible();
  37  |   });
  38  | 
  39  |   // ==============================================================================
  40  |   // TIER 2: RENDERING LOGIC & NAVIGATION BREADCRUMBS
  41  |   // ==============================================================================
  42  | 
  43  |   test('Tier 2: Category page displays correct project counts', async ({ page }) => {
  44  |     await page.goto('/WERKAtlas/category/mcp-ecosystem/');
  45  |     const countBadge = page.locator('[data-testid="category-count-badge"]');
  46  |     await expect(countBadge).toBeVisible();
  47  |     const countText = await countBadge.innerText();
  48  |     expect(parseInt(countText || '0')).toBeGreaterThan(0);
  49  |   });
  50  | 
  51  |   test('Tier 2: Detail page displays correct score components breakdown values', async ({ page }) => {
  52  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
  53  |     const maintenanceVal = page.locator('[data-testid="score-component-maintenance"]');
  54  |     await expect(maintenanceVal).toBeVisible();
  55  |     await expect(maintenanceVal).not.toBeEmpty();
  56  |   });
  57  | 
  58  |   test('Tier 2: Breadcrumbs are displayed on category and project pages', async ({ page }) => {
  59  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
  60  |     const breadcrumbs = page.locator('[data-testid="breadcrumbs"]');
  61  |     await expect(breadcrumbs).toBeVisible();
  62  |     await expect(breadcrumbs.locator('a').first()).toContainText('Home');
  63  |   });
  64  | 
  65  |   test('Tier 2: Trends chart container is rendered on detail page', async ({ page }) => {
  66  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
  67  |     const chart = page.locator('[data-testid="trend-chart-container"]');
  68  |     await expect(chart).toBeVisible();
  69  |   });
  70  | 
  71  |   // ==============================================================================
  72  |   // TIER 3: COMPLEX END-TO-END FLOWS
  73  |   // ==============================================================================
  74  | 
  75  |   test('Tier 3: E2E navigation from Explorer list to Detail page', async ({ page }) => {
  76  |     await page.goto('/WERKAtlas/');
  77  |     
  78  |     // Find first project card and get its title link
  79  |     const firstCardLink = page.locator('[data-testid="project-card-link"]').first();
  80  |     const expectedTitle = await firstCardLink.locator('[data-testid="project-name"]').innerText();
  81  |     
  82  |     // Click to navigate
  83  |     await firstCardLink.click();
  84  |     
  85  |     // Assert detail page loaded
  86  |     await expect(page).toHaveURL(/.*\/project\/.*/);
  87  |     const detailTitle = await page.locator('[data-testid="project-title"]').innerText();
  88  |     expect(detailTitle.toLowerCase()).toContain(expectedTitle.toLowerCase());
  89  |   });
  90  | 
  91  |   test('Tier 3: Navigation via breadcrumbs back to category and home', async ({ page }) => {
> 92  |     await page.goto('/WERKAtlas/project/n8n-io-n8n/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:4321/WERKAtlas/project/n8n-io-n8n/
  93  |     
  94  |     // Click category breadcrumb
  95  |     await page.locator('[data-testid="breadcrumb-category"]').click();
  96  |     await expect(page).toHaveURL(/.*\/category\/.*/);
  97  |     
  98  |     // Click home breadcrumb
  99  |     await page.locator('[data-testid="breadcrumb-home"]').click();
  100 |     await expect(page).toHaveURL(/\/WERKAtlas\/$/);
  101 |   });
  102 | 
  103 |   // ==============================================================================
  104 |   // TIER 4: EDGE CASES & RESILIENCY
  105 |   // ==============================================================================
  106 | 
  107 |   test('Tier 4: Navigating to non-existent project slug shows friendly 404 page', async ({ page }) => {
  108 |     await page.goto('/WERKAtlas/project/non-existent-slug/');
  109 |     
  110 |     const notFoundMessage = page.locator('[data-testid="not-found-message"]');
  111 |     await expect(notFoundMessage).toBeVisible();
  112 |     await expect(notFoundMessage).toContainText('Project not found');
  113 |   });
  114 | 
  115 |   test('Tier 4: Page handles projects with missing license gracefully without crash', async ({ page }) => {
  116 |     // Navigate to a project known or crafted to have missing license / metadata
  117 |     await page.goto('/WERKAtlas/project/missing-metadata-project-slug/');
  118 |     
  119 |     const licenseBadge = page.locator('[data-testid="metadata-license"]');
  120 |     await expect(licenseBadge).toContainText('Unknown');
  121 |   });
  122 | });
  123 | 
```