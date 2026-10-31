"""Explorer keeps freshness filtering in the browser, relative to current date."""
from pathlib import Path
ROOT=Path(__file__).parents[1]
PAGE=ROOT/"web/src/pages/explorer.astro"
CLIENT=ROOT/"web/src/scripts/explorer-client.ts"
INDEX=ROOT/"web/src/pages/catalog-index.json.ts"

def test_explorer_freshness_uses_current_clock():
    page=PAGE.read_text(encoding="utf-8")
    client=CLIENT.read_text(encoding="utf-8")
    assert 'id="catalog-freshness"' in page
    assert 'Date.now()-Date.parse(item.checked_at' in client
    assert "2026-10-28T00:00:00Z" not in client

def test_unknown_or_future_check_dates_not_treated_as_fresh():
    page=PAGE.read_text(encoding="utf-8")
    client=CLIENT.read_text(encoding="utf-8")
    index=INDEX.read_text(encoding="utf-8")
    assert '<option value="unknown">Unbekannt</option>' in page
    assert '!Number.isFinite(age) || age<0' in client
    assert 'age<=NINETY_DAYS' in client
    assert 'checked_at:item.checked_at' in index
