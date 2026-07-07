"""Test rendering output."""

from pathlib import Path
import re


def test_readme_exists():
    """Test that README.md was generated."""
    path = Path(__file__).parent.parent / "README.md"
    assert path.exists(), "README.md not found"


def test_catalog_md_exists():
    """Test that CATALOG.md exists."""
    path = Path(__file__).parent.parent / "CATALOG.md"
    assert path.exists(), "CATALOG.md not found"


def test_landscape_exists():
    """Test that LANDSCAPE.md exists."""
    path = Path(__file__).parent.parent / "LANDSCAPE.md"
    assert path.exists(), "LANDSCAPE.md not found"


def test_methodology_exists():
    """Test that METHODOLOGY.md exists."""
    path = Path(__file__).parent.parent / "METHODOLOGY.md"
    assert path.exists(), "METHODOLOGY.md not found"


def test_taxonomy_exists():
    """Test that taxonomy.json exists."""
    path = Path(__file__).parent.parent / "data" / "taxonomy.json"
    assert path.exists(), "taxonomy.json not found"


def test_schema_exists():
    """Test that catalog.schema.json exists."""
    path = Path(__file__).parent.parent / "data" / "catalog.schema.json"
    assert path.exists(), "catalog.schema.json not found"


def test_readme_has_readable_markdown_spacing():
    """README should render as readable GitHub Markdown, not a compressed blob."""
    path = Path(__file__).parent.parent / "README.md"
    text = path.read_text(encoding="utf-8")

    assert "# Agentic Engineering Compendium\n\n>" in text
    assert "![Snapshot]" in text
    assert "\n\n## Start Here\n\n" in text
    assert "\n\n## Ecosystem Map\n\n```mermaid\n" in text
    assert "\n\n## Contents\n\n" in text
    assert "\n\n| Rating | Score range | Projects |\n" in text
    assert "\n\n## Top 25 Projects\n\n" in text
    assert "\n\n# Complete Catalog\n\n" in text
    assert "\n</details>\n\n<details>\n" in text


def test_generated_markdown_has_no_mojibake():
    """Generated docs should not contain common UTF-8 decoding artifacts."""
    root = Path(__file__).parent.parent
    generated = [
        "README.md",
        "CATALOG.md",
        "BUILD-YOUR-OWN.md",
        "WATCHLIST.md",
        "ARCHIVED.md",
    ]

    for name in generated:
        text = (root / name).read_text(encoding="utf-8")
        assert not re.search(r"â.|Ã.", text), f"mojibake found in {name}"
