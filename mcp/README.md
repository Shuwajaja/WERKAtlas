# WERKAtlas MCP

Nur-lesender Zugriff auf `data/catalog.json`. Der Server installiert nichts, startet keine Shell und schreibt keine Datei.

```bash
python mcp/server.py --catalog data/catalog.json --taxonomy data/taxonomy.json
```

Transport ist JSON-RPC 2.0 als **eine JSON-Zeile pro Nachricht** auf stdin und stdout (MCP-stdio-Spezifikation).

| Werkzeug | Wirkung |
| --- | --- |
| `search` | Text in ID, Name, Repository, Beschreibung, Kategorie und Projekttyp. Optional `category`, `limit` 1–50. |
| `get_project` | Ein Eintrag mit exakter ID `owner/name`. |
| `list_categories` | Die 81 Unterkategorien der Taxonomie. |

Leere Felder bleiben leer. Eine Sicherheitsnotiz wird nur zurückgegeben, wenn sie schon im Katalog steht.
