# WERKAtlas MCP

Nur-lesender Zugriff auf `data/catalog.json`. Der Server installiert nichts, startet keine Shell und schreibt keine Datei.

```bash
python mcp/server.py --catalog data/catalog.json --taxonomy data/taxonomy.json
```

Transport ist JSON-RPC 2.0 als **eine JSON-Zeile pro Nachricht** auf stdin und stdout (MCP-stdio-Spezifikation).

| Werkzeug | Wirkung |
| --- | --- |
| `search` | Text in ID, Name, Repository, Beschreibung, Kategorie und Projekttyp. Optional `category`, `limit` 1–50. |
| `recommend` | Belegbare lexikalische Treffer mit sortierter Übereinstimmung, `matched_terms`, `unmatched_terms` und `unknown_fields`. Filter: Lizenz, Sprache, Projekttyp, Mindestscore, archivierte Projekte. Kein Modellaufruf und keine Garantie für technische Eignung. |\n| `get_project` | Ein Eintrag mit exakter ID `owner/name`. |
| `list_categories` | Die 81 Unterkategorien der Taxonomie. |

Leere Felder bleiben leer. Eine Sicherheitsnotiz wird nur zurückgegeben, wenn sie schon im Katalog steht.

## Beispiel für die Agentenrecherche

`recommend({"query":"voice SIP","license":"MIT","limit":5})` liefert ausschließlich Katalogeinträge und markiert unbekannte Daten. Die Reihenfolge gewichtet Texttreffer, **nicht** tatsächliche Softwarequalität. `get_project` liefert anschließend das unveränderte vollständige Projektobjekt mit Quellen. Für eine belastbare Empfehlung muss ein Agent GitHub-Lizenz und Wartung separat aktuell prüfen.

Die Suche schreibt keine Katalogdaten, führt keinen Repo-Code aus und benötigt keine externe API.
