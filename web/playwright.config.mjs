import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir:"./tests",
  testMatch:"*.spec.mjs",
  timeout:30000,
  expect:{timeout:10000},
  reporter:[["list"]],
  workers:1,
  retries:0,
  projects:[
    {name:"desktop",use:{browserName:"chromium",channel:"chrome",viewport:{width:1400,height:900}}},
    {name:"mobile",use:{browserName:"chromium",channel:"chrome",viewport:{width:390,height:844},isMobile:true,hasTouch:true}},
  ],
  use:{baseURL:"http://127.0.0.1:4393/WERKAtlas/"},
  webServer:{command:"npm run dev -- --host 127.0.0.1 --port 4393",
    url:"http://127.0.0.1:4393/WERKAtlas/",reuseExistingServer:false,timeout:90000},
  outputDir:"./test-results",
});
