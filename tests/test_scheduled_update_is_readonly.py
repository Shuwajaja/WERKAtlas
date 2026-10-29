"""The daily workflow may look, and it may not publish."""

from pathlib import Path


def test_scheduled_update_does_not_push_main():
    text = Path(".github/workflows/scheduled-update.yml").read_text(encoding="utf-8")
    assert "git push" not in text
    assert "git commit" not in text
    assert "render.py" not in text
    assert "score.py" not in text
    assert "classify.py" not in text
    assert "deploy-pages" not in text
    assert "contents: read" in text
    assert "audit_catalog.py" in text
    assert "validate.py" in text
