# M3 Setup Proposal: Astro + TypeScript Static Site for WERKAtlas

This report details the recommended setup, configuration, design system architecture, page templates, and dynamic data loading strategy for the static site representation of the **Agentic Engineering Compendium (WERKAtlas)**.

---

## 1. Project Location & Structure

To keep the repository root clean and adhere to the **Workplace Root Contract (AGENTS.md)** and local agent rules (where only metadata/canonical documents should reside at the root), the Astro project MUST be placed in a dedicated `/web` subdirectory.

### Proposed Directory Layout

```text
agentic-engineering-compendium/
├── data/                      # Catalog files (raw data)
│   ├── catalog.json           # Main dataset (805 entries)
│   ├── taxonomy.json          # Taxonomy categories
│   └── catalog.schema.json    # JSON Schema
├── web/                       # Astro + TypeScript web project
│   ├── package.json           # Web-specific dependencies
│   ├── tsconfig.json          # TypeScript compilation options
│   ├── astro.config.mjs       # Astro configuration
│   ├── tailwind.config.mjs   # Tailwind configurations & theme tokens
│   ├── public/                # Static assets (images, fonts, robots.txt)
│   └── src/
│       ├── components/        # Reusable UI parts (badges, cards, tables)
│       ├── layouts/           # Main Layouts (BaseLayout.astro, ProjectLayout.astro)
│       ├── pages/             # File-based routes
│       │   ├── index.astro    # Main Landing / Overview page
│       │   ├── explorer.astro # Interactive Atlas Explorer (Dual-Panel UI)
│       │   ├── category/
│       │   │   └── [id].astro # Dynamically generated Category pages
│       │   └── project/
│       │       └── [id].astro # Dynamically generated Project detail pages
│       ├── styles/            # Global styling and custom fonts
│       └── utils/             # Data loading & parsing utilities (Zod schemas, filtering)
```

---

## 2. Dependencies & Configurations

### Dependencies (`web/package.json`)
The following configuration includes the minimal dependency footprint needed for an industrial editorial look, complete type safety, and fast local searching:

```json
{
  "name": "werkatlas-web",
  "type": "module",
  "version": "1.0.0",
  "scripts": {
    "dev": "astro dev",
    "start": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "astro": "astro"
  },
  "dependencies": {
    "astro": "^4.11.0",
    "tailwindcss": "^3.4.4",
    "@astrojs/tailwind": "^5.1.0",
    "lucide-astro": "^0.399.0",
    "zod": "^3.23.8",
    "fuse.js": "^7.0.0"
  },
  "devDependencies": {
    "typescript": "^5.5.2",
    "@types/node": "^20.14.9"
  }
}
```

### Astro Configuration (`web/astro.config.mjs`)
To deploy successfully onto GitHub Pages under the path `/WERKAtlas/`, configuration for the site name and path prefix is required:

```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://wbs-edu.github.io', // Placeholder, update to actual production host
  base: '/WERKAtlas/',
  output: 'static',
  integrations: [tailwind()],
  vite: {
    // Allows importing JSON files from outside /web (e.g. "../data/catalog.json")
    server: {
      fs: {
        allow: ['..']
      }
    }
  }
});
```

### TypeScript Configuration (`web/tsconfig.json`)
Strict mode is recommended to guarantee type-safety against the dataset:

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@components/*": ["src/components/*"],
      "@layouts/*": ["src/layouts/*"],
      "@utils/*": ["src/utils/*"],
      "@data/*": ["../data/*"]
    },
    "jsx": "react-jsx",
    "jsxImportSource": "react"
  }
}
```

---

## 3. WERK Brand "Cool Graphite" Design System

The layout embodies an **industrial, blueprint-style editorial design** matching the "Cool Graphite" palette:

### Custom CSS Tokens (Tailwind Extensions)

```javascript
// web/tailwind.config.mjs
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: '#0C0D0E', // Darkest background
          900: '#121416', // Slate dark body background
          800: '#1C1F22', // Card & Panel Backgrounds
          700: '#2C3035', // Borders, gridlines
          600: '#495057', // Accent labels
          400: '#ADB5BD', // Body text
          100: '#E9ECEF', // Highlight text
          50: '#F8F9FA',  // Bright headings
        },
        caution: {
          yellow: '#FFC107',  // Interactive highlights / warnings
          orange: '#F97316',  // Secondary accents / high relevance
        },
        steel: {
          border: '#373B40',
          glare: '#4E545C'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'SF Mono', 'Menlo', 'monospace'],
        sans: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
      },
      spacing: {
        // Tight, grid-based incremental rhythm
        'grid-xs': '4px',
        'grid-sm': '8px',
        'grid-md': '12px',
        'grid-lg': '16px',
        'grid-xl': '24px',
      },
      borderRadius: {
        // Rigid, engineering layout
        'none': '0px',
        'sm': '2px',
        'DEFAULT': '4px',
      },
      boxShadow: {
        // Flat, retro-industrial offset shadows
        'flat-sm': '1px 1px 0px 0px #000000',
        'flat-md': '3px 3px 0px 0px #000000',
        'flat-lg': '5px 5px 0px 0px #000000',
        'flat-caution': '3px 3px 0px 0px #FFC107',
      }
    },
  },
  plugins: [],
}
```

### Layout Grid Style
- **Pattern**: Technical blueprints. Add a CSS-grid background overlay using SVG lines:
  ```css
  .bg-blueprint {
    background-size: 40px 40px;
    background-image: 
      linear-gradient(to right, rgba(55, 59, 64, 0.2) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(55, 59, 64, 0.2) 1px, transparent 1px);
  }
  ```
- **Rigidity**: Borders are thick (`border-2 border-steel-border`) with sharp corners (`rounded-none`).
- **Data visualization**: Mini sparklines or bar meters representing scoring components (Relevance, Maintenance, Adoption, etc.) using simple HTML/CSS bar shapes rather than heavy canvas charts.

---

## 4. Layouts & Templates Design

### Page A: BaseLayout (`src/layouts/BaseLayout.astro`)
Provides the scaffolding for all pages:
- **Header**: Main product title (`WERKAtlas // Compendium`), snapshot metadata (`2026-07-07`), totals bar (e.g. `805 Projects / 10 Domains`).
- **Sidebar**: Standard navigation links: `Dashboard`, `Atlas Explorer`, `Trending`, `Watchlist`, `Methodology`.
- **Main Area**: Scrollable viewport with blueprint grid borders.

### Page B: Main / Dashboard (`src/pages/index.astro`)
- **Key Metrics Panel**: A dense horizontal layout showing total projects, category distributions, average scores, and top licenses.
- **Featured Categories**: 10 card components mapping taxonomy groups A through J.
- **Top Picks**: High-score projects (Score > 75) displayed in an editorial showcase.

### Page C: Atlas Explorer (`src/pages/explorer.astro`)
An interactive dual-panel workbench:
- **Left Panel (Width 1/4)**: A sticky collapsible navigation tree containing the complete category taxonomy (`A.1` through `J.81`). Selecting a subcategory immediately triggers filtering.
- **Right Panel (Width 3/4)**:
  - Global Search and filters: Search by project name/owner, filter by `Project Type`, `Official Status`, and minimum `Score`.
  - Dense Data Table: Shows columns for `ID` (owner/repo), `Score`, `Official Status`, `Project Type`, `Primary Language`, and `Description`. Sortable by clicking column headers. Powered by client-side JavaScript referencing a mini search index generated at compile time.

### Page D: Category Page (`src/pages/category/[id].astro`)
Dynamic pages generated at build time using `getStaticPaths()` mapping the categories defined in `taxonomy.json`:
- **Header**: Large category ID and name (e.g., `Category B.6 — Agent Frameworks`) and full description.
- **Listings**: Paginated listing of entries matching this category (or secondary categories), ordered descending by score.

### Page E: Project Details (`src/pages/project/[id].astro`)
Details page generated at build time mapping the unique canonical repository IDs (replacing slash with dash, e.g. `microsoft-autogen` for route resolution):
- **Canonical Header**: Project name, owner, repository link, homepage link, license info, and dates.
- **Score Component Grid**: A structured dashboard presenting the overall score (e.g., `78/100`) alongside its components:
  - Relevance, Maintenance, Adoption, Momentum, Documentation, Production Readiness, Security, Interoperability.
- **Metadata Sidebar**: Capabilities tags, supported protocols, compatible runtimes/hosts, and deployment modes.
- **Critical Sections**: Distinct sections showing **Security notes** (e.g., warnings for sensitive MCP servers) and **Limitations**.

---

## 5. Dynamic Data Loading Strategy (Static Site Generation)

Since Astro compiles the application to a pure static site (SSG), loading the 805 items in `catalog.json` must be managed efficiently at build time.

### Utility Module (`src/utils/dataLoader.ts`)
We parse and type-safe the JSON data using Zod, ensuring zero invalid records can disrupt site rendering:

```typescript
import { z } from 'zod';
import catalogRaw from '../../../data/catalog.json';
import taxonomyRaw from '../../../data/taxonomy.json';

// Zod Schema to type-check incoming data
export const CatalogEntrySchema = z.object({
  id: z.string(),
  name: z.string(),
  owner: z.string(),
  repository: z.string(),
  repository_url: z.string().url(),
  homepage_url: z.string().url().nullable().optional(),
  description: z.string(),
  primary_category: z.string(),
  secondary_categories: z.array(z.string()).optional().default([]),
  project_type: z.string(),
  capabilities: z.array(z.string()).optional().default([]),
  protocols: z.array(z.string()).optional().default([]),
  compatible_hosts: z.array(z.string()).optional().default([]),
  deployment_modes: z.array(z.string()).optional().default([]),
  official_status: z.enum(['official', 'community', 'unclear']),
  official_evidence: z.array(z.string()).optional().default([]),
  primary_language: z.string().nullable().optional(),
  languages: z.array(z.string()).optional().default([]),
  stars: z.number(),
  forks: z.number(),
  open_issues: z.number(),
  score: z.number(),
  confidence: z.enum(['high', 'medium', 'low']),
  score_components: z.object({
    relevance: z.number(),
    maintenance: z.number(),
    adoption: z.number(),
    momentum: z.number(),
    documentation: z.number(),
    production_readiness: z.number(),
    security: z.number(),
    interoperability: z.number(),
    community: z.number(),
    uniqueness: z.number(),
  }),
  install_methods: z.array(z.string()).optional().default([]),
  security_notes: z.array(z.string()).optional().default([]),
  limitations: z.array(z.string()).optional().default([]),
});

export type CatalogEntry = z.infer<typeof CatalogEntrySchema>;

// Validate and export catalog entries
export const catalogEntries: CatalogEntry[] = catalogRaw.map((entry) => {
  try {
    return CatalogEntrySchema.parse(entry);
  } catch (e) {
    console.error(`Validation failed for project: ${entry.id}`, e);
    throw e;
  }
});

// Export Taxonomy
export const taxonomy = taxonomyRaw;
```

### Static Path Generation

#### 1. Category Page Route: `src/pages/category/[id].astro`
```astro
---
import BaseLayout from '@layouts/BaseLayout.astro';
import { catalogEntries, taxonomy } from '@utils/dataLoader';

export async function getStaticPaths() {
  const categories = Object.keys(taxonomy.categories).flatMap(mainCatKey => {
    const subcats = taxonomy.categories[mainCatKey].subcategories;
    return Object.keys(subcats).map(subcatKey => ({
      params: { id: subcatKey },
      props: { 
        categoryName: subcats[subcatKey].name,
        categoryDesc: subcats[subcatKey].description,
        mainCatName: taxonomy.categories[mainCatKey].name
      }
    }));
  });
  return categories;
}

const { id } = Astro.params;
const { categoryName, categoryDesc, mainCatName } = Astro.props;

// Filter matching projects
const projects = catalogEntries.filter(
  (p) => p.primary_category === id || p.secondary_categories?.includes(id)
).sort((a, b) => b.score - a.score);
---
<BaseLayout title={`Category ${id} - ${categoryName}`}>
  <!-- Category Listing UI -->
</BaseLayout>
```

#### 2. Project Details Route: `src/pages/project/[id].astro`
```astro
---
import BaseLayout from '@layouts/BaseLayout.astro';
import { catalogEntries } from '@utils/dataLoader';

export async function getStaticPaths() {
  return catalogEntries.map((entry) => {
    // Replace '/' to make safe URL parameter strings (e.g. microsoft/autogen -> microsoft-autogen)
    const urlId = entry.id.replace('/', '-');
    return {
      params: { id: urlId },
      props: { project: entry }
    };
  });
}

const { project } = Astro.props;
---
<BaseLayout title={`${project.name} Details`}>
  <!-- Project Detail UI -->
</BaseLayout>
```

### Client-side Search and Filter Index
Since downloading all 3.2MB of `catalog.json` on the client during page loads is expensive, a lighter payload is generated for client-side search. Astro can output a compact search index at build time inside a customized page route, or we can compile the searchable records directly into a static JSON asset like `/public/search-index.json`.

```typescript
// Proposed build-step or custom endpoint (src/pages/search-index.json.ts)
import { catalogEntries } from '@utils/dataLoader';

export async function GET() {
  // Strip heavy metrics & descriptions for search index efficiency
  const searchIndex = catalogEntries.map(p => ({
    i: p.id,            // ID
    n: p.name,          // Name
    o: p.owner,         // Owner
    d: p.description,   // Description
    c: p.primary_category,
    t: p.project_type,
    s: p.score
  }));

  return new Response(JSON.stringify(searchIndex), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```
*Note: This reduces the client payload from 3.2MB to ~150KB for fast, reactive client-side fuzzy searching using Fuse.js.*
