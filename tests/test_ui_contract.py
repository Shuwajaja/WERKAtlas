"""Public pages preserve project filters, source provenance and comparison hooks."""
from pathlib import Path
ROOT=Path(__file__).parent.parent

def test_explorer_and_detail_expose_filter_and_source_hooks():
    explorer=(ROOT/"web/src/pages/explorer.astro").read_text(encoding="utf-8")
    client=(ROOT/"web/src/scripts/explorer-client.ts").read_text(encoding="utf-8")
    index=(ROOT/"web/src/pages/catalog-index.json.ts").read_text(encoding="utf-8")
    detail=(ROOT/"web/src/pages/project/[slug].astro").read_text(encoding="utf-8")
    for element_id in ("catalog-license","catalog-maintenance","catalog-freshness"):
        assert f'id="{element_id}"' in explorer
        assert f'"{element_id}"' in client
    assert 'data-testid="source-urls"' in detail
    assert "unbekannt" in detail
    assert "checked_at:item.checked_at" in index
    assert "maintenance_status:item.maintenance_status" in index

def test_homepage_exposes_the_comparison_contract():
    index=(ROOT/"web/src/pages/index.astro").read_text(encoding="utf-8")
    for test_id in (
        "compare-btn","comparison-bar","comparison-count","comparison-table",
        "comparison-warning","comparison-column","comparison-row-score",
        "comparison-val-missing","launch-comparison-btn","clear-comparison-btn",
        "remove-compare-item","comparison-limit-toast",
    ):
        assert test_id in index
    assert "Select at least" in index
