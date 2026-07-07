# LOOP 1: Taxonomy, Source Mapping, Broad Discovery

**Status:** ✓ Complete
**Date:** 2026-07-07

## Completed Tasks

1. ✅ Finalized taxonomy (81 subcategories across 10 top-level categories)
2. ✅ Built source map (3 tiers: authoritative, high-value, weak signals)
3. ✅ Built query matrix (60+ GitHub search queries)
4. ✅ Inspected official GitHub organizations (MCP, Anthropic, OpenAI, etc.)
5. ✅ Inspected MCP registries and SDKs
6. ✅ Collected initial candidate pool (seed: 49 projects)
7. ✅ Stored candidates in `data/candidates.ndjson` (42 API-collected + 49 seeded)

## Quality Gate

| Criterion | Status |
|---|---|
| Taxonomy exists | ✓ |
| Source map exists | ✓ |
| Query matrix exists | ✓ |
| Candidate data is machine-readable | ✓ |
| Discovery sources recorded | ✓ |
| Obvious false positives filtered | ✓ |

## Limitations

- GitHub API rate limiting prevented full automated collection (unauthenticated 60 req/hr)
- Used knowledge-based seeding to bootstrap the catalog
- Will require GitHub token for future API-heavy loops

## Notes

- Initial discovery targeted 10 key areas of the agent ecosystem
- Seed catalog covers all 10 top-level taxonomy categories
- 42 raw candidates collected via API before rate limiting
- 49 seed entries from known projects cover major ecosystem projects
