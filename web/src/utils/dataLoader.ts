import { z } from 'zod';
import catalogRaw from '../../../data/catalog.json';
import taxonomyRaw from '../../../data/taxonomy.json';

// Zod Schema to type-check incoming data based on catalog.schema.json
export const CatalogEntrySchema = z.object({
  id: z.string(),
  name: z.string(),
  owner: z.string(),
  repository: z.string(),
  repository_url: z.string(),
  homepage_url: z.string().nullable().optional(),
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
  topics: z.array(z.string()).optional().default([]),
  license: z.string().nullable().optional(),
  stars: z.number().optional().default(0),
  forks: z.number().optional().default(0),
  open_issues: z.number().optional().default(0),
  created_at: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
  pushed_at: z.string().nullable().optional(),
  latest_release_at: z.string().nullable().optional(),
  archived: z.boolean().optional().default(false),
  is_fork: z.boolean().optional().default(false),
  maintenance_status: z.string().optional(),
  documentation_quality: z.number().optional(),
  production_readiness: z.number().optional(),
  security_transparency: z.number().optional(),
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
  trend_data: z.object({
    stars_30d: z.number().nullable().optional(),
    stars_90d: z.number().nullable().optional(),
    method: z.string().nullable().optional(),
  }).optional(),
  install_methods: z.array(z.string()).optional().default([]),
  security_notes: z.array(z.string()).optional().default([]),
  limitations: z.array(z.string()).optional().default([]),
  source_urls: z.array(z.string()).optional().default([]),
  discovered_from: z.array(z.string()).optional().default([]),
  checked_at: z.string()
});

export type CatalogEntry = z.infer<typeof CatalogEntrySchema>;

// Validate and export catalog entries
export const catalogEntries: CatalogEntry[] = (catalogRaw.entries as any[]).map((entry) => {
  try {
    return CatalogEntrySchema.parse(entry);
  } catch (e) {
    console.error(`Validation failed for project: ${entry.id}`, e);
    throw e;
  }
});

// Export Taxonomy
export interface Subcategory {
  name: string;
  description: string;
}

export interface Category {
  name: string;
  subcategories: Record<string, Subcategory>;
}

export interface Taxonomy {
  categories: Record<string, Category>;
}

export const taxonomy = taxonomyRaw as unknown as Taxonomy;
