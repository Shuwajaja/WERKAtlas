"""GitHub workflow files must remain valid YAML."""

from pathlib import Path


def test_validate_workflow_has_no_multiline_inline_python():
    text = Path(".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert 'run: python -c "' not in text


def test_validate_workflow_runs_pytest():
    text = Path(".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "python -m pytest tests/" in text
