# Design Decisions

## Architectural Decisions

### ADR-001: No GitHub CLI Available
**Date:** 2026-07-07
**Context:** `gh` is not installed on this system.
**Decision:** Use direct HTTP API via Python `urllib`/`requests` with rate-limit awareness.
**Consequence:** 60 req/hr limit for unauthenticated access. Will implement exponential backoff and caching.
**Status:** Accepted

### ADR-002: Unauthenticated GitHub API
**Date:** 2026-07-07
**Context:** No `GITHUB_TOKEN` configured. Unauthenticated access has strict rate limits.
**Decision:** Continue with reduced request volume. Prioritize most important repositories. Document the limitation.
**Status:** Accepted

### ADR-003: Python + uv for Scripts
**Date:** 2026-07-07
**Context:** Need reproducible, cross-platform scripts.
**Decision:** Use Python 3 with `uv` for dependency management and execution.
**Status:** Accepted

### ADR-004: NDJSON for Candidate Pool
**Date:** 2026-07-07
**Context:** Large number of candidates that need append-friendly format.
**Decision:** Use NDJSON (newline-delimited JSON) for raw candidates; JSON for final catalog.
**Status:** Accepted

---

*Last updated: 2026-07-07 17:47 UTC*
