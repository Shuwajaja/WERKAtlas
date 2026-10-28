# WERKAtlas v2 Ziel

Stand der Entscheidung: 2026-10-28, Europe/Berlin. Bezugsstand im Git: `main` `1f04367926d3be5f35180147c31cd5d02d8e5363`.

## Ziel

WERKAtlas bleibt dieses eine Repository. Ein Agent beantwortet „welches Werkzeug passt?“ aus `data/catalog.json` mit drei lesenden Aufrufen: `search`, `get_project`, `list_categories`. Ein Mensch sieht denselben Bestand in der vorhandenen Astro-Oberfläche. Neue Funde werden ein Review-PR. Nichts landet ungeprüft auf `main`.

Das ist der Nutzen von v2. Kein zweiter Katalog, keine neue Datenbank, kein Spiegel der Codebasen.

## Woran wir erkennen, dass es fertig genug ist

- `search("mcp server")` liefert vorhandene Einträge aus dem Katalog, ohne GitHub zu klonen und ohne API-Key.
- `get_project("owner/name")` liefert genau diesen Eintrag oder eine klare Fehlmeldung.
- `list_categories` liefert die 81 Unterkategorien aus `data/taxonomy.json`.
- Der tägliche GitHub-Workflow schreibt nicht mehr auf `main`.
- Ein Vorschlag aus dem 08:00-Radar oder aus der Instagram-Liste wird erst dann ein Katalogeintrag, wenn ein Review-PR den GitHub-Beleg enthält.
- Lizenz, Agententyp, Unique Features, Kosten, Integrationsart, System-Fit und Prüfnachweis bleiben leer, solange keine Quelle sie nennt.

## Was sinnvoll ist

Die schnelle Suche ist eine Feldsuche über die 1468 kurzen Katalogsätze: Name, Beschreibung, Kategorie, Projekttyp, Score. Der Katalog enthält bereits 122 MCP-Server oder MCP-Clients und 130 Einträge in den Skill-Kategorien E.*. Eine Vektordatenbank wäre ein zweites System. Sie kommt erst infrage, wenn diese Feldsuche nachweislich die passenden Werkzeuge verfehlt.

Repomix bleibt ein manuelles Werkzeug für genau ein Repository. GitHub bleibt die Codequelle. Atlas speichert Wissen, Bewertung und Fundstelle.

Cursor baut den Atlas: Code, Tests, Review-PRs. ChatGPT und ChatGPT Work recherchieren, bewerten und pflegen Vorschläge. Der Radar um 08:00 Uhr Europe/Berlin liefert Vorschläge und übernimmt keine Projekte.

## Was die Zahlen bedeuten

| Zahl | Bedeutung | Belegt am 2026-10-28 |
| --- | --- | --- |
| 1468 | Einträge in `data/catalog.json`, Snapshot 2026-07-07 | ja |
| 678 | Einträge mit Score mindestens 50, gezählt an diesem Stand | ja |
| 790 | Einträge unter Score 50 | ja |
| 742 | Badge „Accepted“ im README, damals Score mindestens 50 | nur als alter Render-Stand, nicht als heutige Zählung |
| 726 | Badge „Excluded“ im README | nur als alter Render-Stand |
| 110 | Instagram-Research-IDs aus der vorherigen Prüfung | nicht in `main` importiert |
| 742 als Kandidatendatei | keine | `data/candidates.ndjson` liegt nicht im Repository |

Das README wird in diesem Schritt nicht neu gerendert. `scripts/render.py` schreibt die Markdown-Dateien kürzer als der committete Stand.

## Reihenfolge

1. Bestand sichern. Der Audit in PR #2 hält die Identitätsregeln fest. Offen bleibt: `.github/workflows/scheduled-update.yml` läuft um 02:00 UTC, das ist 03:00 Uhr Europe/Berlin, klassifiziert, bewertet neu und pusht auf `main`. Das ist nicht der 08:00-Radar. Solange dieser Job schreibt, ist der Bestand nicht gesichert.
2. Suche und read-only MCP auf `data/catalog.json`. Das ist der erste Nutzen für Cursor und andere Agenten.
3. Datenqualität in kleinen PRs. Nur Korrekturen mit GitHub-Beleg. Lücken bleiben sichtbar. Kein Neutaxieren des ganzen Katalogs, weil `scripts/score.py` den Wartungsscore aus dem Tagesdatum ableitet.
4. Research-Automation. Radar, Releases und die 110 Instagram-IDs erzeugen einen Bericht oder einen Review-PR. Kein Apply-Schalter, der den Katalog still überschreibt.
5. Oberfläche. Filter, Quellen, Aktualität und der im Playwright-Vertrag schon beschriebene Vergleich. Dieselben Felder, die MCP ausliefert.

## Rollengrenze

Cursor merged nicht und deployed nicht. ChatGPT erfindet keine Metadaten, die im Katalog leer sind. Der Radar fügt keine Zeile ein.
