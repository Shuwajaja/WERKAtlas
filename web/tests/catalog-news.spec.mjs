import {test, expect} from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
const screenshots=path.resolve(import.meta.dirname,"..","screenshots");

test("Explorer loads just 18 real project cards and filters without errors",async({page},testInfo)=>{
 const errors=[];
 page.on("pageerror",e=>errors.push(e.message));
 await page.goto("explorer/");
 await expect(page.locator("#catalog-count")).toContainText("1.516");
 await expect(page.locator('[data-testid="catalog-card"]')).toHaveCount(18);
 await expect(page.locator("#catalog-more")).toBeVisible();
 await page.locator("#catalog-search").fill("n8n");
 await expect(page.locator('[data-testid="catalog-card"]').first()).toBeVisible();
 await expect(page.locator("#catalog-count")).not.toContainText("1.516");
 await page.locator("#catalog-reset").click();
 await expect(page.locator('[data-testid="catalog-card"]')).toHaveCount(18);
 await page.locator("#view-list").click();
 await expect(page.locator("#catalog-projects")).toHaveClass(/list/);
 await page.locator("#view-grid").click();
 await expect(page.locator("#catalog-projects")).not.toHaveClass(/list/);
 expect(errors).toEqual([]);
 await page.screenshot({path:path.join(screenshots,testInfo.project.name+"-explorer.png"),fullPage:true});
});
test("News feed shows source labels, filter and source links",async({page},testInfo)=>{
 const errors=[];
 page.on("pageerror",e=>errors.push(e.message));
 await page.goto("news/");
 await expect(page.locator('[data-testid="news-article"]').first()).toBeVisible();
 const first=page.locator('[data-testid="news-article"]').first();
 await expect(first.locator("a").first()).toHaveAttribute("href",/^https?:\/\//);
 await expect(first.locator(".radar-kind")).toBeVisible();
 await page.locator("#news-kind").selectOption("official");
 await expect(page.locator('[data-testid="news-article"]').first()).toBeVisible();
 await expect(page.locator('[data-testid="news-article"]').first().locator(".radar-kind")).toHaveText("Hersteller");
 await page.locator("#news-search").fill("___unfindable___");
 await expect(page.locator("#news-empty")).toBeVisible();
 await page.locator("#news-search").fill("");
 expect(errors).toEqual([]);
 await page.screenshot({path:path.join(screenshots,testInfo.project.name+"-news.png"),fullPage:true});
});
test("Both pages fit mobile/desktop widths",async({page})=>{
 for(const url of ["explorer/","news/"]){
  await page.goto(url);
  await expect(page.locator(url.startsWith("explorer")?"#catalog-count":"#news-count")).toBeVisible();
  const w=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth}));
  expect(w.scroll, url+" horizontal overflow").toBeLessThanOrEqual(w.width+2);
 }
});

test("Sources view lists configured feeds and visible status",async({page})=>{
 await page.goto("sources/");
 await expect(page.getByRole("heading",{name:/woher kommen die/i})).toBeVisible();
 await expect(page.locator(".sources-card")).toHaveCount(21);
 await expect(page.getByText("OpenAI News")).toBeVisible();
 await expect(page.getByText("Hugging Face")).toBeVisible();
 await expect(page.getByRole("link",{name:/original-feed ansehen/i}).first()).toHaveAttribute("href",/^https:\/\//);
});
test("Mobile research navigation exposes projects, news and sources",async({page},testInfo)=>{
 await page.goto("explorer/");
 if(testInfo.project.name!=="mobile")return;
 const nav=page.getByRole("navigation",{name:"Mobile Navigation"});
 await expect(nav.getByRole("link",{name:"News"})).toBeVisible();
 await nav.getByRole("link",{name:"News"}).click();
 await expect(page).toHaveURL(/\/WERKAtlas\/news\//);
 await nav.getByRole("link",{name:"Quellen"}).click();
 await expect(page).toHaveURL(/\/WERKAtlas\/sources\//);
});
