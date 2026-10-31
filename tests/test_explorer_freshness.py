"""Explorer freshness must be relative to today, not a frozen research snapshot."""
from pathlib import Path

EXPLORER = Path(__file__).parents[1] / "web" / "src" / "pages" / "explorer.astro"


def test_explorer_freshness_uses_current_clock():
    text = EXPLORER.read_text(encoding="utf-8")
    assert "const AS_OF = Date.now();" in text
    assert "2026-10-28T00:00:00Z" not in text
    assert "In den letzten 90 Tagen geprüft" in text


def test_unknown_or_future_check_dates_not_treated_as_fresh():
    text = EXPLORER.read_text(encoding="utf-8")
    assert 'value="unknown"' in text
    assert "!Number.isFinite(age) || age < 0" in text
    assert "age <= NINETY_DAYS" in text
