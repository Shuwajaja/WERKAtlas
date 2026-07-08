# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: brand.spec.ts >> Feature 4: WERK Branding & CSS Design Tokens >> Tier 1: Footer contains WERK trademark and copy notice
- Location: brand.spec.ts:21:7

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
  3   | test.describe('Feature 4: WERK Branding & CSS Design Tokens', () => {
  4   | 
  5   |   // ==============================================================================
  6   |   // TIER 1: ELEMENT EXISTENCE & INITIAL STATE
  7   |   // ==============================================================================
  8   | 
  9   |   test('Tier 1: Page header contains WERKLogo or brand title', async ({ page }) => {
  10  |     await page.goto('/WERKAtlas/');
  11  |     const logo = page.locator('[data-testid="brand-logo"]');
  12  |     await expect(logo).toBeVisible();
  13  |   });
  14  | 
  15  |   test('Tier 1: Theme toggle button is present on the page', async ({ page }) => {
  16  |     await page.goto('/WERKAtlas/');
  17  |     const toggle = page.locator('[data-testid="theme-toggle-btn"]');
  18  |     await expect(toggle).toBeVisible();
  19  |   });
  20  | 
  21  |   test('Tier 1: Footer contains WERK trademark and copy notice', async ({ page }) => {
> 22  |     await page.goto('/WERKAtlas/');
      |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:4321/WERKAtlas/
  23  |     const footer = page.locator('[data-testid="brand-footer"]');
  24  |     await expect(footer).toBeVisible();
  25  |     await expect(footer).toContainText('WERK');
  26  |   });
  27  | 
  28  |   // ==============================================================================
  29  |   // TIER 2: CSS TOKEN VALIDATION & RESPONSIVE DESIGN
  30  |   // ==============================================================================
  31  | 
  32  |   test('Tier 2: Body uses WERK design token font-family', async ({ page }) => {
  33  |     await page.goto('/WERKAtlas/');
  34  |     const font = await page.evaluate(() => {
  35  |       const style = window.getComputedStyle(document.body);
  36  |       return style.fontFamily;
  37  |     });
  38  |     // WERK design system specifies brand-sans (e.g. Geist, Inter, system-ui)
  39  |     expect(font).toContain('sans-serif');
  40  |   });
  41  | 
  42  |   test('Tier 2: Main theme color uses Cool Graphite custom property or hex values', async ({ page }) => {
  43  |     await page.goto('/WERKAtlas/');
  44  |     const color = await page.evaluate(() => {
  45  |       const el = document.documentElement;
  46  |       return window.getComputedStyle(el).getPropertyValue('--color-cool-graphite') ||
  47  |              window.getComputedStyle(el).getPropertyValue('--werk-theme-color');
  48  |     });
  49  |     // Check that we have a CSS variable set for WERK branding
  50  |     expect(color).toBeDefined();
  51  |   });
  52  | 
  53  |   test('Tier 2: Navigation bar background has correct styling', async ({ page }) => {
  54  |     await page.goto('/WERKAtlas/');
  55  |     const nav = page.locator('[data-testid="brand-nav"]');
  56  |     await expect(nav).toBeVisible();
  57  |   });
  58  | 
  59  |   test('Tier 2: Theme loads correct default mode (dark/light matching media query)', async ({ page }) => {
  60  |     await page.goto('/WERKAtlas/');
  61  |     const htmlThemeAttr = await page.locator('html').getAttribute('data-theme');
  62  |     expect(htmlThemeAttr).toMatch(/dark|light/);
  63  |   });
  64  | 
  65  |   // ==============================================================================
  66  |   // TIER 3: COMPLEX END-TO-END FLOWS
  67  |   // ==============================================================================
  68  | 
  69  |   test('Tier 3: E2E Theme toggling changes body styles and page variables', async ({ page }) => {
  70  |     await page.goto('/WERKAtlas/');
  71  |     const html = page.locator('html');
  72  |     const initialTheme = await html.getAttribute('data-theme');
  73  |     
  74  |     // Toggle the theme
  75  |     await page.locator('[data-testid="theme-toggle-btn"]').click();
  76  |     
  77  |     const toggledTheme = await html.getAttribute('data-theme');
  78  |     expect(toggledTheme).not.toBe(initialTheme);
  79  |     
  80  |     // Toggle back
  81  |     await page.locator('[data-testid="theme-toggle-btn"]').click();
  82  |     const finalTheme = await html.getAttribute('data-theme');
  83  |     expect(finalTheme).toBe(initialTheme);
  84  |   });
  85  | 
  86  |   test('Tier 3: Persists user-selected theme preference across page reloads', async ({ page }) => {
  87  |     await page.goto('/WERKAtlas/');
  88  |     
  89  |     // Change to alternative theme
  90  |     const html = page.locator('html');
  91  |     const initialTheme = await html.getAttribute('data-theme');
  92  |     await page.locator('[data-testid="theme-toggle-btn"]').click();
  93  |     const alternativeTheme = await html.getAttribute('data-theme');
  94  |     
  95  |     // Reload page
  96  |     await page.reload();
  97  |     
  98  |     const reloadedTheme = await html.getAttribute('data-theme');
  99  |     expect(reloadedTheme).toBe(alternativeTheme);
  100 |   });
  101 | 
  102 |   // ==============================================================================
  103 |   // TIER 4: EDGE CASES & RESILIENCY
  104 |   // ==============================================================================
  105 | 
  106 |   test('Tier 4: Responsive typography - titles scale gracefully on mobile screens', async ({ page }) => {
  107 |     // Set viewport to mobile size
  108 |     await page.setViewportSize({ width: 375, height: 667 });
  109 |     await page.goto('/WERKAtlas/');
  110 |     
  111 |     const title = page.locator('[data-testid="brand-title"]');
  112 |     await expect(title).toBeVisible();
  113 |     
  114 |     const fontSize = await title.evaluate((el) => window.getComputedStyle(el).fontSize);
  115 |     // Typography should scale or wrap appropriately without overflow
  116 |     expect(parseFloat(fontSize)).toBeLessThan(50);
  117 |   });
  118 | 
  119 |   test('Tier 4: Custom styles injected via query params does not compromise layout integrity', async ({ page }) => {
  120 |     // Check that style parameter hacks/overrides don't crash rendering
  121 |     await page.goto('/WERKAtlas/?theme=invalid_theme_value');
  122 |     
```