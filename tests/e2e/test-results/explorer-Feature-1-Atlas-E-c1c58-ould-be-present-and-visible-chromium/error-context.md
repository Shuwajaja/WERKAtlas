# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: explorer.spec.ts >> Feature 1: Atlas Explorer Search & Filters >> Tier 1: Search input should be present and visible
- Location: explorer.spec.ts:9:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:4321/WERKAtlas/
Call log:
  - navigating to "http://localhost:4321/WERKAtlas/", waiting until "load"

```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Feature 1: Atlas Explorer Search & Filters', () => {
  4   | 
  5   |   // ==============================================================================
  6   |   // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  7   |   // ==============================================================================
  8   | 
  9   |   test('Tier 1: Search input should be present and visible', async ({ page }) => {
> 10  |     await page.goto('/WERKAtlas/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:4321/WERKAtlas/
  11  |     const searchInput = page.locator('[data-testid="search-input"]');
  12  |     await expect(searchInput).toBeVisible();
  13  |   });
  14  | 
  15  |   test('Tier 1: Category filter list should be populated', async ({ page }) => {
  16  |     await page.goto('/WERKAtlas/');
  17  |     const categories = page.locator('[data-testid="category-filter"]');
  18  |     await expect(categories.first()).toBeVisible();
  19  |   });
  20  | 
  21  |   test('Tier 1: Sort selector should exist with default value', async ({ page }) => {
  22  |     await page.goto('/WERKAtlas/');
  23  |     const sortSelect = page.locator('[data-testid="sort-select"]');
  24  |     await expect(sortSelect).toBeVisible();
  25  |     await expect(sortSelect).toHaveValue('score-desc');
  26  |   });
  27  | 
  28  |   test('Tier 1: Reset filters button should be initially disabled or hidden', async ({ page }) => {
  29  |     await page.goto('/WERKAtlas/');
  30  |     const resetBtn = page.locator('[data-testid="reset-filters-btn"]');
  31  |     // It should either not be present or disabled until a filter is applied
  32  |     const isDisabled = await resetBtn.isDisabled();
  33  |     const isHidden = !(await resetBtn.isVisible());
  34  |     expect(isDisabled || isHidden).toBeTruthy();
  35  |   });
  36  | 
  37  |   test('Tier 1: Project list container must display multiple project cards', async ({ page }) => {
  38  |     await page.goto('/WERKAtlas/');
  39  |     const cards = page.locator('[data-testid="project-card"]');
  40  |     await expect(cards.first()).toBeVisible();
  41  |   });
  42  | 
  43  |   // ==============================================================================
  44  |   // TIER 2: SEARCH, MULTI-FACETED FILTERING & SORTING LOGIC
  45  |   // ==============================================================================
  46  | 
  47  |   test('Tier 2: Searching for an exact project name should filter results', async ({ page }) => {
  48  |     await page.goto('/WERKAtlas/');
  49  |     const searchInput = page.locator('[data-testid="search-input"]');
  50  |     await searchInput.fill('n8n');
  51  |     const cards = page.locator('[data-testid="project-card"]');
  52  |     await expect(cards).toHaveCount(1);
  53  |     await expect(cards.first()).toContainText('n8n');
  54  |   });
  55  | 
  56  |   test('Tier 2: Filtering by category should narrow the project list', async ({ page }) => {
  57  |     await page.goto('/WERKAtlas/');
  58  |     const categoryFilter = page.locator('[data-testid="category-filter"][value="mcp-ecosystem"]');
  59  |     await categoryFilter.click();
  60  |     const cards = page.locator('[data-testid="project-card"]');
  61  |     // Ensure all displayed cards are in the selected category
  62  |     const count = await cards.count();
  63  |     for (let i = 0; i < count; i++) {
  64  |       await expect(cards.nth(i).locator('[data-testid="project-category"]')).toContainText('MCP');
  65  |     }
  66  |   });
  67  | 
  68  |   test('Tier 2: Combining search text and category filter', async ({ page }) => {
  69  |     await page.goto('/WERKAtlas/');
  70  |     await page.locator('[data-testid="search-input"]').fill('sdk');
  71  |     await page.locator('[data-testid="category-filter"][value="mcp-ecosystem"]').click();
  72  |     const cards = page.locator('[data-testid="project-card"]');
  73  |     await expect(cards.first()).toContainText('sdk');
  74  |   });
  75  | 
  76  |   test('Tier 2: Sorting projects by stars ascending', async ({ page }) => {
  77  |     await page.goto('/WERKAtlas/');
  78  |     const sortSelect = page.locator('[data-testid="sort-select"]');
  79  |     await sortSelect.selectOption('stars-asc');
  80  |     
  81  |     const starsBadges = page.locator('[data-testid="project-stars"]');
  82  |     const count = await starsBadges.count();
  83  |     if (count > 1) {
  84  |       const firstStars = parseInt(await starsBadges.nth(0).innerText() || '0');
  85  |       const secondStars = parseInt(await starsBadges.nth(1).innerText() || '0');
  86  |       expect(firstStars).toBeLessThanOrEqual(secondStars);
  87  |     }
  88  |   });
  89  | 
  90  |   test('Tier 2: Resetting active filters updates list back to baseline', async ({ page }) => {
  91  |     await page.goto('/WERKAtlas/');
  92  |     const initialCount = await page.locator('[data-testid="project-card"]').count();
  93  |     
  94  |     await page.locator('[data-testid="search-input"]').fill('n8n');
  95  |     await expect(page.locator('[data-testid="project-card"]')).toHaveCount(1);
  96  |     
  97  |     await page.locator('[data-testid="reset-filters-btn"]').click();
  98  |     const afterResetCount = await page.locator('[data-testid="project-card"]').count();
  99  |     expect(afterResetCount).toBe(initialCount);
  100 |   });
  101 | 
  102 |   // ==============================================================================
  103 |   // TIER 3: COMPLEX END-TO-END FLOWS
  104 |   // ==============================================================================
  105 | 
  106 |   test('Tier 3: E2E discovery flow with multiple filters and sort', async ({ page }) => {
  107 |     await page.goto('/WERKAtlas/');
  108 |     
  109 |     // Type in search bar
  110 |     await page.locator('[data-testid="search-input"]').fill('model');
```