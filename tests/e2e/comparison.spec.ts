import { test, expect } from '@playwright/test';

test.describe('Feature 2: Project Comparison View', () => {

  // ==============================================================================
  // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  // ==============================================================================

  test('Tier 1: Compare button should be present on project cards', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const compareBtn = page.locator('[data-testid="compare-btn"]').first();
    await expect(compareBtn).toBeVisible();
  });

  test('Tier 1: Comparison drawer / bar should be initially hidden', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const comparisonBar = page.locator('[data-testid="comparison-bar"]');
    await expect(comparisonBar).toBeHidden();
  });

  test('Tier 1: Compare view page elements should exist', async ({ page }) => {
    await page.goto('/WERKAtlas/?compare=n8n-io/n8n');
    const table = page.locator('[data-testid="comparison-table"]');
    await expect(table).toBeVisible();
  });

  // ==============================================================================
  // TIER 2: COMPARISON SELECTION & INTERACTION LOGIC
  // ==============================================================================

  test('Tier 2: Clicking compare button on a card reveals comparison bar', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    await page.locator('[data-testid="compare-btn"]').first().click();
    const comparisonBar = page.locator('[data-testid="comparison-bar"]');
    await expect(comparisonBar).toBeVisible();
  });

  test('Tier 2: Showing count of selected projects in comparison bar', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    await page.locator('[data-testid="compare-btn"]').nth(0).click();
    await page.locator('[data-testid="compare-btn"]').nth(1).click();
    
    const countBadge = page.locator('[data-testid="comparison-count"]');
    await expect(countBadge).toContainText('2');
  });

  test('Tier 2: Removing a project from selection updates counts', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    await page.locator('[data-testid="compare-btn"]').nth(0).click();
    await page.locator('[data-testid="compare-btn"]').nth(1).click();
    
    // Remove one project inside the comparison bar
    await page.locator('[data-testid="remove-compare-item"]').first().click();
    const countBadge = page.locator('[data-testid="comparison-count"]');
    await expect(countBadge).toContainText('1');
  });

  test('Tier 2: Comparing less than 2 projects shows validation warning on compare page', async ({ page }) => {
    await page.goto('/WERKAtlas/?compare=n8n-io/n8n');
    const warning = page.locator('[data-testid="comparison-warning"]');
    await expect(warning).toBeVisible();
    await expect(warning).toContainText('Select at least');
  });

  test('Tier 2: Comparison table columns map to selected projects', async ({ page }) => {
    await page.goto('/WERKAtlas/?compare=n8n-io/n8n,ollama/ollama');
    const columns = page.locator('[data-testid="comparison-column"]');
    await expect(columns).toHaveCount(2);
    await expect(columns.nth(0)).toContainText('n8n');
    await expect(columns.nth(1)).toContainText('ollama');
  });

  // ==============================================================================
  // TIER 3: COMPLEX END-TO-END FLOWS
  // ==============================================================================

  test('Tier 3: E2E selection, launch, and comparison table inspection', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    
    // Select first two projects
    await page.locator('[data-testid="compare-btn"]').nth(0).click();
    await page.locator('[data-testid="compare-btn"]').nth(1).click();
    
    // Launch compare page from bar
    await page.locator('[data-testid="launch-comparison-btn"]').click();
    
    // Assert we are on comparison page and table renders properly
    await expect(page).toHaveURL(/.*compare=.*/);
    const table = page.locator('[data-testid="comparison-table"]');
    await expect(table).toBeVisible();
    
    // Check metric rows like Score or Stars
    const scoreRow = page.locator('[data-testid="comparison-row-score"]');
    await expect(scoreRow).toBeVisible();
  });

  test('Tier 3: Clearing all selected projects resets the view state', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    await page.locator('[data-testid="compare-btn"]').nth(0).click();
    await page.locator('[data-testid="compare-btn"]').nth(1).click();
    
    await page.locator('[data-testid="clear-comparison-btn"]').click();
    await expect(page.locator('[data-testid="comparison-bar"]')).toBeHidden();
  });

  // ==============================================================================
  // TIER 4: EDGE CASES & RESILIENCY
  // ==============================================================================

  test('Tier 4: Enforce max comparison limit of 3 projects', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    
    // Select 4 projects
    await page.locator('[data-testid="compare-btn"]').nth(0).click();
    await page.locator('[data-testid="compare-btn"]').nth(1).click();
    await page.locator('[data-testid="compare-btn"]').nth(2).click();
    
    // The 4th button should either be disabled, or clicking it should trigger a warning
    const fourthBtn = page.locator('[data-testid="compare-btn"]').nth(3);
    const isBtnDisabled = await fourthBtn.isDisabled();
    
    if (!isBtnDisabled) {
      await fourthBtn.click();
      const warningToast = page.locator('[data-testid="comparison-limit-toast"]');
      await expect(warningToast).toBeVisible();
    } else {
      expect(isBtnDisabled).toBeTruthy();
    }
  });

  test('Tier 4: Missing property handling in comparison grid', async ({ page }) => {
    // If we compare a project with null values, the grid shouldn't break and should show fallback '-'
    await page.goto('/WERKAtlas/?compare=n8n-io/n8n,some-obscure-project');
    const columns = page.locator('[data-testid="comparison-column"]');
    await expect(columns).toHaveCount(2);
    
    const fallbackVal = page.locator('[data-testid="comparison-val-missing"]').first();
    await expect(fallbackVal).toBeVisible();
    await expect(fallbackVal).toContainText('-');
  });

  test('Tier 4: Comparison link sharing persists state perfectly', async ({ page }) => {
    const shareUrl = '/WERKAtlas/?compare=n8n-io/n8n,ollama/ollama,weaviate/weaviate';
    await page.goto(shareUrl);
    
    const columns = page.locator('[data-testid="comparison-column"]');
    await expect(columns).toHaveCount(3);
  });
});
