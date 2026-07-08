# WERKAtlas E2E Test Suite Readiness Report (TEST_READY)

This document shows the breakdown of the dual-layer E2E test cases mapped across the 9 features of the modernized WERKAtlas project.

## Summary of Total Test Cases

- **Total Test Cases**: 106
  - **Data Pipeline Suite (Python)**: 54
  - **Astro Frontend Suite (Playwright)**: 52
- **Required Minimum**: 104+
- **Attestation Status**:
  - **Backend Data Pipeline Suite (Python)**: **PASSING**
  - **Astro Frontend Suite (Playwright)**: **READY / EXPECTED TO FAIL** (expected to fail until the Astro static site is developed in Milestone M3/M4, conforming to TDD expectations)

---

## Test Grid: Coverage Across Features and Tiers

The following matrix displays the test case count per feature across Tiers 1–4:

| Feature ID & Name | Tier 1 (Unit/Boundary) | Tier 2 (Integration) | Tier 3 (System E2E) | Tier 4 (Edge/Compliance) | Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **F1: Search & Multi-Faceted Filtering** | 5 | 5 | 2 | 2 | **14** |
| **F2: Comparison View** | 3 | 5 | 2 | 3 | **13** |
| **F3: Categories & Project Detail Pages** | 5 | 4 | 2 | 2 | **13** |
| **F4: WERK Brand & Custom Design Tokens** | 3 | 4 | 2 | 3 | **12** |
| **F5: Scoring Engine & Weights** | 5 | 5 | 1 | 1 | **12** |
| **F6: Uniqueness & Security Rules** | 5 | 5 | 0 | 0 | **10** |
| **F7: Classification Engine** | 5 | 5 | 1 | 1 | **12** |
| **F8: Data Exporter** | 5 | 5 | 1 | 0 | **11** |
| **F9: Trend/Momentum Engine** | 5 | 5 | 1 | 1 | **12** |
| **TOTALS** | **41** | **42** | **12** | **11** | **106** |

### Tier Definition
- **Tier 1 (Unit & Boundary Validation)**: Initial states, basic elements, boundary values, zero/null cases. (Target: >=5 per feature for key targets)
- **Tier 2 (Component & Logic Integration)**: Detailed logic execution, data transformation, multiple parameter updates. (Target: >=5 per feature for key targets)
- **Tier 3 (System-Level & Pipeline E2E)**: End-to-end flows, multi-step navigation, deep-linking, files creation and validation.
- **Tier 4 (Boundary, Edge Cases & Compliance)**: Extreme outliers, security/injection robustness, layout under stress.

---

## Direct Traceability of Test Cases

### Data Pipeline E2E Suite (`tests/test_e2e_pipeline.py`)

- **Feature 5 (Scoring Engine & Weights)**
  - Tier 1: `test_tier1_scoring_weight_alignment`, `test_tier1_scoring_bounds_empty_entry`, `test_tier1_scoring_bounds_max_entry`, `test_tier1_relevance_minimum_value`, `test_tier1_adoption_score_non_negative`
  - Tier 2: `test_tier2_scoring_framework_type_bonus`, `test_tier2_scoring_mcp_type_bonus`, `test_tier2_scoring_maintenance_decay_30d`, `test_tier2_scoring_momentum_release_cadence`, `test_tier2_scoring_confidence_formula`
  - Tier 3: `test_tier3_full_pipeline_flow` (integrated scoring run)
  - Tier 4: `test_tier4_scoring_boundary_scores`

- **Feature 6 (Uniqueness & Security Rules)**
  - Tier 1: `test_tier1_uniqueness_default_baseline`, `test_tier1_security_default_baseline`, `test_tier1_uniqueness_non_negative`, `test_tier1_security_transparency_bounds`, `test_tier1_security_notes_penalty_bounds`
  - Tier 2: `test_tier2_uniqueness_keyword_bonus`, `test_tier2_uniqueness_project_type_scaling`, `test_tier2_uniqueness_mcp_compatibility_bonus`, `test_tier2_security_transparency_license_bonus`, `test_tier2_security_notes_penalty_scaling`

- **Feature 7 (Classification Engine)**
  - Tier 1: `test_tier1_classification_no_match_returns_none`, `test_tier1_classification_mcp_server_mapping`, `test_tier1_classification_coding_agent_mapping`, `test_tier1_classification_framework_mapping`, `test_tier1_classification_learning_mapping`
  - Tier 2: `test_tier2_classification_specificity_order`, `test_tier2_classification_swe_bench_evaluation`, `test_tier2_classification_memory_vector_db`, `test_tier2_classification_observability_tracing`, `test_tier2_classification_security_guardrails`
  - Tier 3: `test_tier3_full_pipeline_flow` (integrated classification run)
  - Tier 4: `test_tier4_classification_no_fallback_strictness`

- **Feature 8 (Data Exporter)**
  - Tier 1: `test_tier1_exporter_handles_empty_entries`, `test_tier1_exporter_json_contents`, `test_tier1_exporter_ndjson_line_count`, `test_tier1_exporter_csv_headers`, `test_tier1_exporter_csv_data_alignment`
  - Tier 2: `test_tier2_exporter_ensures_directory_creation`, `test_tier2_exporter_correctly_escapes_csv_fields`, `test_tier2_exporter_excludes_non_schema_properties`, `test_tier2_exporter_handles_null_values_in_fields`, `test_tier2_exporter_maintains_utf8_encoding`
  - Tier 3: `test_tier3_full_pipeline_flow` (integrated export check)

- **Feature 9 (Trend/Momentum Engine)**
  - Tier 1: `test_tier1_trend_populates_empty_historical_map`, `test_tier1_trend_git_loader_handling`, `test_tier1_trend_populates_valid_historical_map`, `test_tier1_trend_ignores_unknown_ids`, `test_tier1_trend_updates_file_in_place`
  - Tier 2: `test_tier2_trend_handles_missing_pushed_at`, `test_tier2_trend_does_not_modify_existing_fields`, `test_tier2_trend_compares_multiple_historical_dates`, `test_tier2_trend_handles_empty_entries_in_history`, `test_tier2_trend_engine_preserves_schema`
  - Tier 3: `test_tier3_validation_rules_compliance` (integrated validation run)
  - Tier 4: `test_tier3_validation_rules_compliance` (integrated validation rules check)

---

### Astro Frontend E2E Suite (`tests/e2e/`)

- **Feature 1 (Search & Multi-Faceted Filtering) - `tests/e2e/explorer.spec.ts`**
  - Tier 1: Initial state visibility of Search box, Category filter populating, Sort selector defaults, Reset filters button initial state, card list rendering.
  - Tier 2: Filtering on exact search string, category button click refinement, query combination (text + category), sorting by stars, reset filter action.
  - Tier 3: E2E complex query flow (search + category + language + sort order check), URL deep-linking persistence.
  - Tier 4: Special characters / injection resiliency, infinite scroll pagination loads.

- **Feature 2 (Comparison View) - `tests/e2e/comparison.spec.ts`**
  - Tier 1: Compare button visibility on cards, initial hidden drawer bar, direct navigation to comparison page element validation.
  - Tier 2: Clicking compare displays bar, selected count badge increments, removing projects updates drawer state, comparing < 2 projects validation.
  - Tier 3: Multi-select launch and grid navigation E2E flow, clear-all selection reset behavior.
  - Tier 4: Maximum comparison bounds enforcement (3 items limit), missing parameters grid rendering placeholder, deep-link share URL persistence.

- **Feature 3 (Categories & Project Detail Pages) - `tests/e2e/pages.spec.ts`**
  - Tier 1: Category list page header and card section check, project detail page title, score breakdown panel, repository metadata panel presence.
  - Tier 2: Category page badge counts, detail page score breakdown values, navigation breadcrumbs, trend chart container rendering.
  - Tier 3: E2E explorer-to-detail page routing, breadcrumbs click path navigation.
  - Tier 4: 404 project not found fallback, empty license metadata grace handling.

- **Feature 4 (WERK Brand & Custom Design Tokens) - `tests/e2e/brand.spec.ts`**
  - Tier 1: Header logo check, theme toggler button check, footer branding and trade notice.
  - Tier 2: Body font-family WERK-sans token, WERK custom property theme variables, navigation bar branding class structure, default system-preference theme loading.
  - Tier 3: Theme toggle click changes data-theme attribute, local storage theme state reload check.
  - Tier 4: Mobile screen viewport typography scaling, invalid styling parameter injection resiliency, keyboard focus outlines visibility.
