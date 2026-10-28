"""Search-index entries keep a stable key order."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_search_index import INDEX_FIELDS, slim_entry  # noqa: E402


def test_slim_entry_key_order_is_stable():
    entry = {"id": "acme/widget", "repository": "acme/widget", "name": "Widget"}
    keys = list(slim_entry(entry).keys())
    assert keys == sorted(INDEX_FIELDS) + ["slug"]
    assert list(slim_entry(entry).keys()) == keys
