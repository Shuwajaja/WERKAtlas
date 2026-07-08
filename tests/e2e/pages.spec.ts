import { test, expect } from '@playwright/test';

test.describe('Feature 3: Categories & Project Detail Pages', () => {

  // ==============================================================================
  // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  // ==============================================================================

  test('Tier 1: Category list page has category header', async ({ page }) => {
    await page.goto('/WERKAtlas/category/mcp-ecosystem/');
    const header = page.locator('[data-testid="category-header"]');
    await expect(header).toBeVisible();
  });

  test('Tier 1: Category list page contains projects list', async ({ page }) => {
    await page.goto('/WERKAtlas/category/mcp-ecosystem/');
    const list = page.locator('[data-testid="category-project-list"]');
    await expect(list).toBeVisible();
  });

  test('Tier 1: Project detail page displays project title', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    const title = page.locator('[data-testid="project-title"]');
    await expect(title).toBeVisible();
  });

  test('Tier 1: Score breakdown card exists on detail page', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    const card = page.locator('[data-testid="score-breakdown-card"]');
    await expect(card).toBeVisible();
  });

  test('Tier 1: Repository metadata panel is present', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    const panel = page.locator('[data-testid="metadata-panel"]');
    await expect(panel).toBeVisible();
  });

  // ==============================================================================
  // TIER 2: RENDERING LOGIC & NAVIGATION BREADCRUMBS
  // ==============================================================================

  test('Tier 2: Category page displays correct project counts', async ({ page }) => {
    await page.goto('/WERKAtlas/category/mcp-ecosystem/');
    const countBadge = page.locator('[data-testid="category-count-badge"]');
    await expect(countBadge).toBeVisible();
    const countText = await countBadge.innerText();
    expect(parseInt(countText || '0')).toBeGreaterThan(0);
  });

  test('Tier 2: Detail page displays correct score components breakdown values', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    const maintenanceVal = page.locator('[data-testid="score-component-maintenance"]');
    await expect(maintenanceVal).toBeVisible();
    await expect(maintenanceVal).not.toBeEmpty();
  });

  test('Tier 2: Breadcrumbs are displayed on category and project pages', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    const breadcrumbs = page.locator('[data-testid="breadcrumbs"]');
    await expect(breadcrumbs).toBeVisible();
    await expect(breadcrumbs.locator('a').first()).toContainText('Home');
  });

  test('Tier 2: Trends chart container is rendered on detail page', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    const chart = page.locator('[data-testid="trend-chart-container"]');
    await expect(chart).toBeVisible();
  });

  // ==============================================================================
  // TIER 3: COMPLEX END-TO-END FLOWS
  // ==============================================================================

  test('Tier 3: E2E navigation from Explorer list to Detail page', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    
    // Find first project card and get its title link
    const firstCardLink = page.locator('[data-testid="project-card-link"]').first();
    const expectedTitle = await firstCardLink.locator('[data-testid="project-name"]').innerText();
    
    // Click to navigate
    await firstCardLink.click();
    
    // Assert detail page loaded
    await expect(page).toHaveURL(/.*\/project\/.*/);
    const detailTitle = await page.locator('[data-testid="project-title"]').innerText();
    expect(detailTitle.toLowerCase()).toContain(expectedTitle.toLowerCase());
  });

  test('Tier 3: Navigation via breadcrumbs back to category and home', async ({ page }) => {
    await page.goto('/WERKAtlas/project/n8n-io-n8n/');
    
    // Click category breadcrumb
    await page.locator('[data-testid="breadcrumb-category"]').click();
    await expect(page).toHaveURL(/.*\/category\/.*/);
    
    // Click home breadcrumb
    await page.locator('[data-testid="breadcrumb-home"]').click();
    await expect(page).toHaveURL(/\/WERKAtlas\/$/);
  });

  // ==============================================================================
  // TIER 4: EDGE CASES & RESILIENCY
  // ==============================================================================

  test('Tier 4: Navigating to non-existent project slug shows friendly 404 page', async ({ page }) => {
    await page.goto('/WERKAtlas/project/non-existent-slug/');
    
    const notFoundMessage = page.locator('[data-testid="not-found-message"]');
    await expect(notFoundMessage).toBeVisible();
    await expect(notFoundMessage).toContainText('Project not found');
  });

  test('Tier 4: Page handles projects with missing license gracefully without crash', async ({ page }) => {
    // Navigate to a project known or crafted to have missing license / metadata
    await page.goto('/WERKAtlas/project/missing-metadata-project-slug/');
    
    const licenseBadge = page.locator('[data-testid="metadata-license"]');
    await expect(licenseBadge).toContainText('Unknown');
  });
});
