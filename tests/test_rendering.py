"""Test rendering output."""

from pathlib import Path


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
