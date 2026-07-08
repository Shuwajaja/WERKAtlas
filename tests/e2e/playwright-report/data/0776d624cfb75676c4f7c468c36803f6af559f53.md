# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: comparison.spec.ts >> Feature 2: Project Comparison View >> Tier 2: Removing a project from selection updates counts
- Location: comparison.spec.ts:47:7

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
  3   | test.describe('Feature 2: Project Comparison View', () => {
  4   | 
  5   |   // ==============================================================================
  6   |   // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  7   |   // ==============================================================================
  8   | 
  9   |   test('Tier 1: Compare button should be present on project cards', async ({ page }) => {
  10  |     await page.goto('/WERKAtlas/');
  11  |     const compareBtn = page.locator('[data-testid="compare-btn"]').first();
  12  |     await expect(compareBtn).toBeVisible();
  13  |   });
  14  | 
  15  |   test('Tier 1: Comparison drawer / bar should be initially hidden', async ({ page }) => {
  16  |     await page.goto('/WERKAtlas/');
  17  |     const comparisonBar = page.locator('[data-testid="comparison-bar"]');
  18  |     await expect(comparisonBar).toBeHidden();
  19  |   });
  20  | 
  21  |   test('Tier 1: Compare view page elements should exist', async ({ page }) => {
  22  |     await page.goto('/WERKAtlas/?compare=n8n-io/n8n');
  23  |     const table = page.locator('[data-testid="comparison-table"]');
  24  |     await expect(table).toBeVisible();
  25  |   });
  26  | 
  27  |   // ==============================================================================
  28  |   // TIER 2: COMPARISON SELECTION & INTERACTION LOGIC
  29  |   // ==============================================================================
  30  | 
  31  |   test('Tier 2: Clicking compare button on a card reveals comparison bar', async ({ page }) => {
  32  |     await page.goto('/WERKAtlas/');
  33  |     await page.locator('[data-testid="compare-btn"]').first().click();
  34  |     const comparisonBar = page.locator('[data-testid="comparison-bar"]');
  35  |     await expect(comparisonBar).toBeVisible();
  36  |   });
  37  | 
  38  |   test('Tier 2: Showing count of selected projects in comparison bar', async ({ page }) => {
  39  |     await page.goto('/WERKAtlas/');
  40  |     await page.locator('[data-testid="compare-btn"]').nth(0).click();
  41  |     await page.locator('[data-testid="compare-btn"]').nth(1).click();
  42  |     
  43  |     const countBadge = page.locator('[data-testid="comparison-count"]');
  44  |     await expect(countBadge).toContainText('2');
  45  |   });
  46  | 
  47  |   test('Tier 2: Removing a project from selection updates counts', async ({ page }) => {
> 48  |     await page.goto('/WERKAtlas/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:4321/WERKAtlas/
  49  |     await page.locator('[data-testid="compare-btn"]').nth(0).click();
  50  |     await page.locator('[data-testid="compare-btn"]').nth(1).click();
  51  |     
  52  |     // Remove one project inside the comparison bar
  53  |     await page.locator('[data-testid="remove-compare-item"]').first().click();
  54  |     const countBadge = page.locator('[data-testid="comparison-count"]');
  55  |     await expect(countBadge).toContainText('1');
  56  |   });
  57  | 
  58  |   test('Tier 2: Comparing less than 2 projects shows validation warning on compare page', async ({ page }) => {
  59  |     await page.goto('/WERKAtlas/?compare=n8n-io/n8n');
  60  |     const warning = page.locator('[data-testid="comparison-warning"]');
  61  |     await expect(warning).toBeVisible();
  62  |     await expect(warning).toContainText('Select at least');
  63  |   });
  64  | 
  65  |   test('Tier 2: Comparison table columns map to selected projects', async ({ page }) => {
  66  |     await page.goto('/WERKAtlas/?compare=n8n-io/n8n,ollama/ollama');
  67  |     const columns = page.locator('[data-testid="comparison-column"]');
  68  |     await expect(columns).toHaveCount(2);
  69  |     await expect(columns.nth(0)).toContainText('n8n');
  70  |     await expect(columns.nth(1)).toContainText('ollama');
  71  |   });
  72  | 
  73  |   // ==============================================================================
  74  |   // TIER 3: COMPLEX END-TO-END FLOWS
  75  |   // ==============================================================================
  76  | 
  77  |   test('Tier 3: E2E selection, launch, and comparison table inspection', async ({ page }) => {
  78  |     await page.goto('/WERKAtlas/');
  79  |     
  80  |     // Select first two projects
  81  |     await page.locator('[data-testid="compare-btn"]').nth(0).click();
  82  |     await page.locator('[data-testid="compare-btn"]').nth(1).click();
  83  |     
  84  |     // Launch compare page from bar
  85  |     await page.locator('[data-testid="launch-comparison-btn"]').click();
  86  |     
  87  |     // Assert we are on comparison page and table renders properly
  88  |     await expect(page).toHaveURL(/.*compare=.*/);
  89  |     const table = page.locator('[data-testid="comparison-table"]');
  90  |     await expect(table).toBeVisible();
  91  |     
  92  |     // Check metric rows like Score or Stars
  93  |     const scoreRow = page.locator('[data-testid="comparison-row-score"]');
  94  |     await expect(scoreRow).toBeVisible();
  95  |   });
  96  | 
  97  |   test('Tier 3: Clearing all selected projects resets the view state', async ({ page }) => {
  98  |     await page.goto('/WERKAtlas/');
  99  |     await page.locator('[data-testid="compare-btn"]').nth(0).click();
  100 |     await page.locator('[data-testid="compare-btn"]').nth(1).click();
  101 |     
  102 |     await page.locator('[data-testid="clear-comparison-btn"]').click();
  103 |     await expect(page.locator('[data-testid="comparison-bar"]')).toBeHidden();
  104 |   });
  105 | 
  106 |   // ==============================================================================
  107 |   // TIER 4: EDGE CASES & RESILIENCY
  108 |   // ==============================================================================
  109 | 
  110 |   test('Tier 4: Enforce max comparison limit of 3 projects', async ({ page }) => {
  111 |     await page.goto('/WERKAtlas/');
  112 |     
  113 |     // Select 4 projects
  114 |     await page.locator('[data-testid="compare-btn"]').nth(0).click();
  115 |     await page.locator('[data-testid="compare-btn"]').nth(1).click();
  116 |     await page.locator('[data-testid="compare-btn"]').nth(2).click();
  117 |     
  118 |     // The 4th button should either be disabled, or clicking it should trigger a warning
  119 |     const fourthBtn = page.locator('[data-testid="compare-btn"]').nth(3);
  120 |     const isBtnDisabled = await fourthBtn.isDisabled();
  121 |     
  122 |     if (!isBtnDisabled) {
  123 |       await fourthBtn.click();
  124 |       const warningToast = page.locator('[data-testid="comparison-limit-toast"]');
  125 |       await expect(warningToast).toBeVisible();
  126 |     } else {
  127 |       expect(isBtnDisabled).toBeTruthy();
  128 |     }
  129 |   });
  130 | 
  131 |   test('Tier 4: Missing property handling in comparison grid', async ({ page }) => {
  132 |     // If we compare a project with null values, the grid shouldn't break and should show fallback '-'
  133 |     await page.goto('/WERKAtlas/?compare=n8n-io/n8n,some-obscure-project');
  134 |     const columns = page.locator('[data-testid="comparison-column"]');
  135 |     await expect(columns).toHaveCount(2);
  136 |     
  137 |     const fallbackVal = page.locator('[data-testid="comparison-val-missing"]').first();
  138 |     await expect(fallbackVal).toBeVisible();
  139 |     await expect(fallbackVal).toContainText('-');
  140 |   });
  141 | 
  142 |   test('Tier 4: Comparison link sharing persists state perfectly', async ({ page }) => {
  143 |     const shareUrl = '/WERKAtlas/?compare=n8n-io/n8n,ollama/ollama,weaviate/weaviate';
  144 |     await page.goto(shareUrl);
  145 |     
  146 |     const columns = page.locator('[data-testid="comparison-column"]');
  147 |     await expect(columns).toHaveCount(3);
  148 |   });
```