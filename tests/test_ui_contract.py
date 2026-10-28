"""The existing pages expose the filter, source, and comparison hooks."""

from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_explorer_and_detail_expose_filter_and_source_hooks():
    explorer = (ROOT / "web/src/pages/explorer.astro").read_text(encoding="utf-8")
    detail = (ROOT / "web/src/pages/project/[slug].astro").read_text(encoding="utf-8")
    for element_id in ("explorer-license", "explorer-maintenance", "explorer-freshness"):
        assert f'id="{element_id}"' in explorer
    assert 'data-testid="source-urls"' in detail
    assert "unbekannt" in detail
    assert "data-checked" in explorer


def test_homepage_exposes_the_comparison_contract():
    index = (ROOT / "web/src/pages/index.astro").read_text(encoding="utf-8")
    for test_id in (
        "compare-btn",
        "comparison-bar",
        "comparison-count",
        "comparison-table",
        "comparison-warning",
        "comparison-column",
        "comparison-row-score",
        "comparison-val-missing",
        "launch-comparison-btn",
        "clear-comparison-btn",
        "remove-compare-item",
        "comparison-limit-toast",
    ):
        assert test_id in index
    assert "Select at least" in index
