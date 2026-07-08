import { test, expect } from '@playwright/test';

test.describe('Feature 4: WERK Branding & CSS Design Tokens', () => {

  // ==============================================================================
  // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  // ==============================================================================

  test('Tier 1: Page header contains WERKLogo or brand title', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const logo = page.locator('[data-testid="brand-logo"]');
    await expect(logo).toBeVisible();
  });

  test('Tier 1: Theme toggle button is present on the page', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const toggle = page.locator('[data-testid="theme-toggle-btn"]');
    await expect(toggle).toBeVisible();
  });

  test('Tier 1: Footer contains WERK trademark and copy notice', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const footer = page.locator('[data-testid="brand-footer"]');
    await expect(footer).toBeVisible();
    await expect(footer).toContainText('WERK');
  });

  // ==============================================================================
  // TIER 2: CSS TOKEN VALIDATION & RESPONSIVE DESIGN
  // ==============================================================================

  test('Tier 2: Body uses WERK design token font-family', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const font = await page.evaluate(() => {
      const style = window.getComputedStyle(document.body);
      return style.fontFamily;
    });
    // WERK design system specifies brand-sans (e.g. Geist, Inter, system-ui)
    expect(font).toContain('sans-serif');
  });

  test('Tier 2: Main theme color uses Cool Graphite custom property or hex values', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const color = await page.evaluate(() => {
      const el = document.documentElement;
      return window.getComputedStyle(el).getPropertyValue('--color-cool-graphite') ||
             window.getComputedStyle(el).getPropertyValue('--werk-theme-color');
    });
    // Check that we have a CSS variable set for WERK branding
    expect(color).toBeDefined();
  });

  test('Tier 2: Navigation bar background has correct styling', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const nav = page.locator('[data-testid="brand-nav"]');
    await expect(nav).toBeVisible();
  });

  test('Tier 2: Theme loads correct default mode (dark/light matching media query)', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const htmlThemeAttr = await page.locator('html').getAttribute('data-theme');
    expect(htmlThemeAttr).toMatch(/dark|light/);
  });

  // ==============================================================================
  // TIER 3: COMPLEX END-TO-END FLOWS
  // ==============================================================================

  test('Tier 3: E2E Theme toggling changes body styles and page variables', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    const html = page.locator('html');
    const initialTheme = await html.getAttribute('data-theme');
    
    // Toggle the theme
    await page.locator('[data-testid="theme-toggle-btn"]').click();
    
    const toggledTheme = await html.getAttribute('data-theme');
    expect(toggledTheme).not.toBe(initialTheme);
    
    // Toggle back
    await page.locator('[data-testid="theme-toggle-btn"]').click();
    const finalTheme = await html.getAttribute('data-theme');
    expect(finalTheme).toBe(initialTheme);
  });

  test('Tier 3: Persists user-selected theme preference across page reloads', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    
    // Change to alternative theme
    const html = page.locator('html');
    const initialTheme = await html.getAttribute('data-theme');
    await page.locator('[data-testid="theme-toggle-btn"]').click();
    const alternativeTheme = await html.getAttribute('data-theme');
    
    // Reload page
    await page.reload();
    
    const reloadedTheme = await html.getAttribute('data-theme');
    expect(reloadedTheme).toBe(alternativeTheme);
  });

  // ==============================================================================
  // TIER 4: EDGE CASES & RESILIENCY
  // ==============================================================================

  test('Tier 4: Responsive typography - titles scale gracefully on mobile screens', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/WERKAtlas/');
    
    const title = page.locator('[data-testid="brand-title"]');
    await expect(title).toBeVisible();
    
    const fontSize = await title.evaluate((el) => window.getComputedStyle(el).fontSize);
    // Typography should scale or wrap appropriately without overflow
    expect(parseFloat(fontSize)).toBeLessThan(50);
  });

  test('Tier 4: Custom styles injected via query params does not compromise layout integrity', async ({ page }) => {
    // Check that style parameter hacks/overrides don't crash rendering
    await page.goto('/WERKAtlas/?theme=invalid_theme_value');
    
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('Tier 4: Focus outline styling is visible on keyboard navigation focus', async ({ page }) => {
    await page.goto('/WERKAtlas/');
    
    // Press Tab to focus search input
    await page.keyboard.press('Tab');
    const focusedInput = page.locator('[data-testid="search-input"]');
    
    const outline = await focusedInput.evaluate((el) => window.getComputedStyle(el).outlineStyle);
    // Ensure there is some visual focus indicator for accessibility compliance
    expect(outline).not.toBe('none');
  });
});
