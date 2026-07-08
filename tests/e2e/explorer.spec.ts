import { test, expect } from '@playwright/test';

test.describe('Feature 1: Atlas Explorer Search & Filters', () => {

  // ==============================================================================
  // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  // ==============================================================================

  test('Tier 1: Search input should be present and visible', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const searchInput = page.locator('[data-testid="search-input"]');
    await expect(searchInput).toBeVisible();
  });

  test('Tier 1: Category filter list should be populated', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const categories = page.locator('[data-testid="category-filter"]');
    await expect(categories.first()).toBeVisible();
  });

  test('Tier 1: Sort selector should exist with default value', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const sortSelect = page.locator('[data-testid="sort-select"]');
    await expect(sortSelect).toBeVisible();
    await expect(sortSelect).toHaveValue('score-desc');
  });

  test('Tier 1: Reset filters button should be initially disabled or hidden', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const resetBtn = page.locator('[data-testid="reset-filters-btn"]');
    // It should either not be present or disabled until a filter is applied
    const isDisabled = await resetBtn.isDisabled();
    const isHidden = !(await resetBtn.isVisible());
    expect(isDisabled || isHidden).toBeTruthy();
  });

  test('Tier 1: Project list container must display multiple project cards', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const cards = page.locator('[data-testid="project-card"]');
    await expect(cards.first()).toBeVisible();
  });

  // ==============================================================================
  // TIER 2: SEARCH, MULTI-FACETED FILTERING & SORTING LOGIC
  // ==============================================================================

  test('Tier 2: Searching for an exact project name should filter results', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const searchInput = page.locator('[data-testid="search-input"]');
    await searchInput.fill('n8n');
    const cards = page.locator('[data-testid="project-card"]');
    await expect(cards).toHaveCount(1);
    await expect(cards.first()).toContainText('n8n');
  });

  test('Tier 2: Filtering by category should narrow the project list', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const categoryFilter = page.locator('[data-testid="category-filter"][value="mcp-ecosystem"]');
    await categoryFilter.click();
    const cards = page.locator('[data-testid="project-card"]');
    // Ensure all displayed cards are in the selected category
    const count = await cards.count();
    for (let i = 0; i < count; i++) {
      await expect(cards.nth(i).locator('[data-testid="project-category"]')).toContainText('MCP');
    }
  });

  test('Tier 2: Combining search text and category filter', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    await page.locator('[data-testid="search-input"]').fill('sdk');
    await page.locator('[data-testid="category-filter"][value="mcp-ecosystem"]').click();
    const cards = page.locator('[data-testid="project-card"]');
    await expect(cards.first()).toContainText('sdk');
  });

  test('Tier 2: Sorting projects by stars ascending', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const sortSelect = page.locator('[data-testid="sort-select"]');
    await sortSelect.selectOption('stars-asc');
    
    const starsBadges = page.locator('[data-testid="project-stars"]');
    const count = await starsBadges.count();
    if (count > 1) {
      const firstStars = parseInt(await starsBadges.nth(0).innerText() || '0');
      const secondStars = parseInt(await starsBadges.nth(1).innerText() || '0');
      expect(firstStars).toBeLessThanOrEqual(secondStars);
    }
  });

  test('Tier 2: Resetting active filters updates list back to baseline', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const initialCount = await page.locator('[data-testid="project-card"]').count();
    
    await page.locator('[data-testid="search-input"]').fill('n8n');
    await expect(page.locator('[data-testid="project-card"]')).toHaveCount(1);
    
    await page.locator('[data-testid="reset-filters-btn"]').click();
    const afterResetCount = await page.locator('[data-testid="project-card"]').count();
    expect(afterResetCount).toBe(initialCount);
  });

  // ==============================================================================
  // TIER 3: COMPLEX END-TO-END FLOWS
  // ==============================================================================

  test('Tier 3: E2E discovery flow with multiple filters and sort', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    
    // Type in search bar
    await page.locator('[data-testid="search-input"]').fill('model');
    // Select category filter
    await page.locator('[data-testid="category-filter"][value="models-infra"]').click();
    // Select language filter
    await page.locator('[data-testid="language-filter"][value="python"]').click();
    // Change sort to score-desc
    await page.locator('[data-testid="sort-select"]').selectOption('score-desc');
    
    // Assert highest scoring matching project is on top
    const firstCard = page.locator('[data-testid="project-card"]').first();
    await expect(firstCard).toBeVisible();
    await expect(firstCard.locator('[data-testid="project-category"]')).toContainText('Model');
  });

  test('Tier 3: Deep-linking of filter criteria via query parameters', async ({ page }) => {
    // Open explorer directly with query parameters
    await page.goto('/WERKAtlas/?q=ollama&cat=models-infra');
    
    const searchInput = page.locator('[data-testid="search-input"]');
    await expect(searchInput).toHaveValue('ollama');
    
    const cards = page.locator('[data-testid="project-card"]');
    await expect(cards).toHaveCount(1);
    await expect(cards.first()).toContainText('ollama');
  });

  // ==============================================================================
  // TIER 4: EDGE CASES & RESILIENCY
  // ==============================================================================

  test('Tier 4: Search input handles special characters and SQL injection attempts gracefully', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const searchInput = page.locator('[data-testid="search-input"]');
    await searchInput.fill("' OR 1=1 --");
    
    const noResultsMsg = page.locator('[data-testid="no-results-message"]');
    await expect(noResultsMsg).toBeVisible();
  });

  test('Tier 4: Extreme pagination / infinite scroll stability', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    // Scroll down multiple times
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    
    const cards = page.locator('[data-testid="project-card"]');
    expect(await cards.count()).toBeGreaterThan(0);
  });
});
