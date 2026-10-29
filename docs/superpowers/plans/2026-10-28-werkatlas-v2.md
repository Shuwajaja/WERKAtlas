# WERKAtlas v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein Agent findet in den bestehenden 1468 Katalogeinträgen ein passendes Werkzeug über `search`, `get_project` und `list_categories`. Neue Funde werden ein Review-PR. `main` bleibt frei von ungeprüften Radar-Übernahmen.

**Architecture:** Kanonische Daten bleiben `data/catalog.json` plus `data/taxonomy.json`. Die Suche liest diese Dateien. Sie bekommt keine Vektordatenbank und keinen zweiten Katalog. Die Astro-Oberfläche bleibt die menschliche Ansicht derselben Daten und wird erst verändert, wenn der MCP-Vertrag steht. Das Zielbild steht in `docs/superpowers/specs/2026-10-28-werkatlas-v2-ziel.md`.

**Tech Stack:** Python 3.10, pytest, vorhandenes JSON-Schema, Astro/Zod im bestehenden `web/`, GitHub Actions. MCP spricht JSON-RPC über stdin/stdout mit der Standardbibliothek. Kein MCP-SDK, kein Repomix, keine bezahlte Embedding-API.

## Global Constraints

- Nur das Repository Shuwajaja/WERKAtlas bearbeiten.
- TruthLens, Artifact Hub, Bridge und andere Projekte nicht integrieren.
- Keine neue Datenbank oder Orchestrierungsplattform ohne nachgewiesenen Bedarf.
- Keine automatischen Installationen. Repomix nicht installieren und nicht über viele Repositories laufen lassen.
- Unbekannte Informationen nicht erfinden. Fehlende Werte bleiben leer und gelten als unbekannt.
- Jede Änderung ist ein kleiner, testbarer Review-PR. Kein Merge und kein Deploy durch den Agenten.
- Tests, Dokumentation, Sicherheitsprüfung und Rollback gehören zu jedem PR.
- Katalogänderungen gelangen nur über Review-PRs nach `main`, nie durch einen direkten Push.
- Jeder akzeptierte neue Projekteintrag braucht einen Beleg aus dem kanonischen Repository, den offiziellen Docs oder einer offiziellen Registry.
- Beschreibungen neuer Einträge sind neutral und 12–30 Wörter. Vorhandene Abweichungen werden gemeldet, in P0 nicht umgeschrieben.
- Sterne sind kein Qualitätsmaß. Archivierte und veraltete Einträge bleiben sichtbar.
- Sicherheitsrelevante MCP-Server brauchen eine ausdrückliche Sicherheitsnotiz.
- Subagenten schreiben nur nach `research/subagents/`.
- Kein Ausführen von Drittcode. Keine bezahlten APIs.
- `scripts/render.py` nicht über das Repository laufen lassen. Ein Probelauf schreibt README und CATALOG kürzer als die committeten Dateien.
- PR #1 (Instagram-GitHub-Reconciliation, 48 neue Einträge) ist am 2026-10-29 auf `main` gemergt (`1516` Einträge). Weitere Katalogänderungen weiterhin nur über kleine Review-PRs.

---

## Bestandsaudit (main, Stand 2026-10-28, Europe/Berlin)

Geprüft wurde `origin/main` bei `1f04367926d3be5f35180147c31cd5d02d8e5363`. Katalog-Snapshot `2026-07-07`, `schema_version` 1.0, `count` 1468, `entries` 1468.

### Was bereits trägt

- Astro-Site unter `web/` mit Basispfad `/WERKAtlas/`. Seiten: Start, Explorer, Methodik, Projektdetail, Trending, Watchlist. `web/src/utils/dataLoader.ts` importiert `data/catalog.json` und prüft mit Zod.
- Explorer filtert bereits Text, Kategorie, Scoring-Tier und Sortierung im Browser.
- Die Detailseite zeigt Score-Komponenten, Sterne, Forks, Lizenz (wenn vorhanden), Protokolle und Sprachen.
- `scripts/validate.py` prüft Pflichtfelder, Score-Bereich, Dubletten der Repository-Zeichenkette und beendet bei Schemafehlern oder Dubletten mit Code 1.
- `scripts/score.py` vergibt maximal 100 Punkte. Sterne gehen logarithmisch ein. `maintenance` hängt von `days_since(now)` ab, deshalb verändert ein blindes Neutaxieren die Scores ohne neue Metadaten.
- Taxonomie `data/taxonomy.json` Version 1.0, Gruppen A–J, 81 Unterkategorien.
- Tests: `tests/test_schema.py`, `test_duplicates.py`, `test_scoring.py`, `test_rendering.py`, `test_e2e_pipeline.py`. Playwright erwartet unter `tests/e2e/comparison.spec.ts` eine Vergleichsansicht, die im UI fehlt.
- `validate.yml` läuft bei PR und Push auf `main`. `deploy.yml` veröffentlicht Pages nur bei Push auf `main` und `workflow_dispatch`.

### Harte Befunde auf dem aktuellen Katalog

Keine. Konkret:

| Prüfung | Ergebnis |
| --- | --- |
| `count` gegen `len(entries)` | 1468 = 1468 |
| doppelte `id` oder `repository` | 0 |
| Groß-/Kleinschreibungskollision | 0 |
| `id` ohne genau einen Schrägstrich | 0 |
| `id` ungleich `repository` | 0 |
| `owner` ungleich Präfix der `id` | 0 |
| `repository_url` ungleich `https://github.com/{id}` | 0 |
| fehlende Pflichtfelder | 0 |
| `project_type` außerhalb des Schema-Enums | 0 |
| `primary_category` außerhalb der Taxonomie | 0 |
| `official_status` oder `confidence` ungültig | 0 |
| Score außerhalb 0–100 oder mehr als 0,2 neben der Komponentensumme | 0 (größte Abweichung 0,05 durch Gleitkomma) |
| negative oder nicht-ganzzahlige Sterne | 0 |
| Eintrag ohne `source_urls` und ohne `discovered_from` | 0 |

46 Kategorien sind belegt. Die größten: J.81 198, H.55 154, D.20 141, B.6 131, C.13 96, E.35 85, F.38 69, G.44 50. 13 Projekttypen, davon `template` 578 und `framework` 313.

### Weiche Befunde, keine erfundenen Nachträge

Diese Werte bleiben unbekannt, bis eine spätere Prüfung sie aus einer Quelle belegt.

| Befund | Anzahl von 1468 |
| --- | --- |
| `license` leer | 1428 |
| `maintenance_status` `unclear` | 1466 |
| `maintenance_status` `archived` | 2 |
| Beschreibung unter 12 Wörtern | 585 |
| Beschreibung über 30 Wörter | 65 |
| `checked_at` älter als 90 Tage, bezogen auf 2026-10-28 | 1468 |
| `homepage_url` leer | 1429 |
| `created_at` leer | 1427 |
| `pushed_at` leer | 725 |
| `official_evidence` leer | 1468 |
| `security_notes` oder `limitations` gesetzt | 0 |
| `official_status` `official` | 0 |
| `agent_type`, `unique_features`, `cost`, `integration_type`, `system_fit`, `verification` | jeweils 0 belegt |

`checked_at` liegt für alle Einträge zwischen 2026-07-07 16:39 UTC und 2026-07-07 18:45 UTC. `source_urls` und `discovered_from` sind bei jedem Eintrag vorhanden. Confidence: high 40, medium 1340, low 88. Archiviert-Flag `true`: 2.

### Pipeline-Risiken, die P0 nicht verändert

- `.github/workflows/scheduled-update.yml` klassifiziert, bewertet neu, schreibt einen Snapshot, baut den Suchindex, ruft `render.py` ohne die Pflichtargumente `--catalog`, `--taxonomy` und `--output` auf, committet und pusht nach `main`, danach Pages-Deploy. Das widerspricht der Review-PR-Regel. Ein Neutaxieren verändert Scores allein durch das Datum.
- `data/search-index.json` ist eine einzeilige JSON-Datei. `slim_entry` iteriert das Set `INDEX_FIELDS`, die Schlüsselreihenfolge ist dadurch laufabhängig. Die Website liest diese Datei nicht. `dataLoader.ts` liest `catalog.json`.
- `scripts/export.py` würde NDJSON und CSV neu schreiben und dabei `score_label` sowie ältere Score-Stände verändern. Nicht ausführen.
- Vergleich: `tests/e2e/comparison.spec.ts` erwartet `data-testid="compare-btn"`, `comparison-bar` und `comparison-table` auf der Startseite. In `web/src` gibt es diese Test-IDs nicht.

### Sicherheitslage von P0

Der Audit liest lokale JSON-Dateien und schreibt nur, wenn `--report` gesetzt ist. Er öffnet kein Netzwerk, startet keinen Prozess und ändert `data/catalog.json` nicht. Rollback ist `git revert` des P0-Commits. Der Katalog bleibt bytegleich.

---

## Zielbild und Ausführungsreihenfolge

Das Ziel ist in `docs/superpowers/specs/2026-10-28-werkatlas-v2-ziel.md` festgehalten. Diese Reihenfolge gilt. Die Task-Nummern weiter unten sind Arbeitsanweisungen, keine Freigabe, sie parallel zu bauen.

| Schritt | Aufgabe | Task unten | Schreibt den Katalog |
| --- | --- | --- | --- |
| 1. Bestand | Audit der Identitätsregeln. Offen als PR #2. | Task 1, erledigt | nein |
| 2. Bestand | Täglicher Workflow pusht nicht mehr nach `main` und bewertet nicht neu. | Task 2 | nein |
| 3. Nutzen | Feldsuche und read-only MCP: `search`, `get_project`, `list_categories`. | Task 5 | nein |
| 4. Datenqualität | Eine belegte GitHub-Differenz pro PR. Leere Felder bleiben leer. README-Badge 742 nicht blind neu rendern. | Task 4, danach erst Task 3 | nein, bis ein eigener Apply-PR den Beleg zeigt |
| 5. Research | Radar-Vorschläge und Instagram-IDs nur als Bericht. | Task 8 | nein |
| 6. Oberfläche | Filter, Quellen, Aktualität, Vergleich. | Task 6, Task 7 | nein |
| später | Stabile Schlüsselreihenfolge, falls der Suchindex neu gebaut wird. Die Website liest ihn nicht. | Task 9 | nein |

Am 2026-10-28 liegen 678 Einträge bei Score mindestens 50 und 790 darunter. Das README-Badge „accepted 742 / excluded 726“ ist der ältere Render derselben Schwelle, nicht die heutige Zählung. `data/candidates.ndjson` ist nicht im Repository. Die 110 Instagram-IDs sind Research und kein importierter Bestand.

Der Workflow `.github/workflows/scheduled-update.yml` läuft um 02:00 UTC, also 03:00 Uhr Europe/Berlin. Der gewünschte Radar um 08:00 Uhr Europe/Berlin ist davon getrennt und darf Vorschläge liefern, ohne Zeilen einzufügen.

Repomix bleibt außerhalb dieser Schritte. Ein Mensch kann es später für genau ein Repository aufrufen. CI installiert es nicht.

---

### Task 1: Nur-lesender Katalog-Audit (P0)

**Files:**
- Create: `scripts/audit_catalog.py`
- Create: `tests/test_audit_catalog.py`
- Modify: `Makefile` (Ziel `audit`)
- Modify: `.github/workflows/validate.yml` (ein nur-lesender Schritt)
- Create: `docs/superpowers/plans/2026-10-28-werkatlas-v2.md`

**Interfaces:**
- Consumes: `data/catalog.json`, `data/catalog.schema.json`, `data/taxonomy.json`
- Produces: `audit_catalog(catalog, schema, taxonomy, *, as_of: datetime, stale_days: int = 90) -> dict` mit den Schlüsseln `entry_count`, `declared_count`, `hard_errors`, `soft_findings`, `passed`. CLI-Exit 0 ohne harte Fehler, sonst 1.

- [x] **Step 1: Write the failing test**

`tests/test_audit_catalog.py` importiert `audit_catalog` und prüft: ein gültiger Mini-Katalog besteht; doppelte ID, Case-Kollision, falscher Owner, falsche URL, Zähldifferenz, unbekannte Kategorie, ungültiger Typ und Score-Abweichung über 0,2 sind harte Fehler; eine Abweichung von 0,05, eine leere Lizenz, eine kurze Beschreibung und ein über 90 Tage altes `checked_at` sind weich. Der echte Katalog hat `passed is True`, 1468 Einträge und die weichen Zähler aus dem Bestandsaudit. Ein CLI-Lauf lässt den SHA-256 von `data/catalog.json` unverändert.

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_audit_catalog.py -v`

Expected: Fehler beim Import, weil `scripts/audit_catalog.py` fehlt. Beobachtet: `ModuleNotFoundError: No module named 'audit_catalog'`.

- [x] **Step 3: Write minimal implementation**

`scripts/audit_catalog.py` implementiert genau die Schnittstelle oben. Harte Fehler: Zähldifferenz, doppelte ID, doppeltes Repository, Case-Kollision, ID-Form, ID ungleich Repository, Owner, `repository_url`, Pflichtfelder, Projekttyp, Kategorie, `official_status`, `confidence`, Score-Bereich, Komponentensumme außerhalb 0,2, nicht-numerische Komponenten, unlesbares `checked_at`, Sterne keine nichtnegative Ganzzahl. Weiche Zähler: `license_missing`, `maintenance_unclear`, `description_under_12_words`, `description_over_30_words`, `checked_at_stale`, `source_urls_missing`, `discovered_from_missing`, `unknown_agent_type`, `unknown_unique_features`, `unknown_cost`, `unknown_integration_type`, `unknown_system_fit`, `unknown_verification`. Das Skript füllt keine dieser Felder.

Makefile:

```make
audit:
	python scripts/audit_catalog.py --catalog data/catalog.json --schema data/catalog.schema.json --taxonomy data/taxonomy.json --as-of 2026-10-28
```

`validate.yml` erhält nach dem vorhandenen Validate-Schritt:

```yaml
      - name: Audit catalog invariants
        run: python scripts/audit_catalog.py --catalog data/catalog.json --schema data/catalog.schema.json --taxonomy data/taxonomy.json --as-of 2026-10-28
```

- [x] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_audit_catalog.py tests/test_schema.py tests/test_duplicates.py -v`

Expected: PASS. Danach `python3 scripts/audit_catalog.py --catalog data/catalog.json --schema data/catalog.schema.json --taxonomy data/taxonomy.json --as-of 2026-10-28` mit Exit 0. Beobachtet am 2026-10-28: 16 Tests bestanden, Audit Exit 0, 0 harte Fehler.

- [x] **Step 5: Commit**

```bash
git add scripts/audit_catalog.py tests/test_audit_catalog.py Makefile .github/workflows/validate.yml docs/superpowers/plans/2026-10-28-werkatlas-v2.md
git commit -m "feat: add a read-only catalog audit gate"
```

**Rollback:** Commit zurücknehmen. `data/catalog.json` ist nicht Teil des Diffs.

**Security:** Nur lokale Lesepfade. `--report` schreibt ausschließlich den angegebenen Pfad und ist im CI-Schritt nicht gesetzt.

---

### Task 2: Cron schreibt nicht mehr auf main (P1)

**Files:**
- Modify: `.github/workflows/scheduled-update.yml`
- Test: Workflow-Datei enthält keinen `git push`.

**Interfaces:**
- Consumes: Task 1 CLI
- Produces: ein täglicher nur-lesender Audit-Job mit `permissions: contents: read`

- [ ] **Step 1: Write the failing test**

```python
def test_scheduled_update_does_not_push_main():
    text = Path(".github/workflows/scheduled-update.yml").read_text(encoding="utf-8")
    assert "git push" not in text
    assert "git commit" not in text
    assert "render.py" not in text
    assert "audit_catalog.py" in text
    assert "contents: read" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scheduled_update_is_readonly.py::test_scheduled_update_does_not_push_main -v`

Expected: FAIL, weil die Datei `git push origin main` enthält.

- [ ] **Step 3: Write minimal implementation**

Die Workflow-Datei wird ersetzt durch Checkout, Python 3.10 und:

```yaml
permissions:
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: python scripts/audit_catalog.py --catalog data/catalog.json --schema data/catalog.schema.json --taxonomy data/taxonomy.json --as-of 2026-10-28
```

`deploy.yml` bleibt unverändert. Ein Push auf `main` veröffentlicht Pages weiterhin. Der Cron deployed nicht mehr und bewertet nicht neu.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scheduled_update_is_readonly.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/scheduled-update.yml tests/test_scheduled_update_is_readonly.py
git commit -m "fix: stop the daily workflow from pushing main"
```

**Rollback:** Die vorige Workflow-Datei wiederherstellen. Bis dahin gibt es keinen automatischen Score-Lauf.

---

### Task 3: Optionale Modellfelder ohne Befüllung (P2)

**Files:**
- Modify: `data/catalog.schema.json` Eigenschaften, nicht `required`
- Modify: `web/src/utils/dataLoader.ts` Zod-Objekt
- Test: `tests/test_schema.py` und ein schmaler Zod-Vertragscheck, falls vorhanden

**Interfaces:**
- Consumes: bestehende Einträge ohne diese Schlüssel
- Produces: optionale, nullable Felder `agent_type` (string oder null), `unique_features` (Array von Strings), `cost` (string oder null), `integration_type` (string oder null), `system_fit` (string oder null), `verification` (Array von Strings). Kein Enum, solange keine belegte Werteliste existiert.

- [ ] **Step 1: Write the failing test**

```python
def test_future_fields_are_optional_and_absent():
    schema = json.loads(Path("data/catalog.schema.json").read_text(encoding="utf-8"))
    for field in ("agent_type", "unique_features", "cost", "integration_type", "system_fit", "verification"):
        assert field in schema["properties"]
        assert field not in schema["required"]
    catalog = json.loads(Path("data/catalog.json").read_text(encoding="utf-8"))
    assert all(field not in entry for entry in catalog["entries"] for field in (
        "agent_type", "unique_features", "cost", "integration_type", "system_fit", "verification"
    ))
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL, `agent_type` fehlt in `properties`.

- [ ] **Step 3: Write minimal implementation**

Schema-Eigenschaften ergänzen, Zod um `.nullable().optional()` erweitern. Keinen Katalogeintrag anfassen. Ein `npm run build` im Verzeichnis `web/` muss mit dem unveränderten Katalog durchlaufen. `web/dist` danach mit `git restore web/dist` verwerfen, falls der Build getrackte Dateien ändert.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_schema.py -v` und `npm run build` in `web/`.

- [ ] **Step 5: Commit**

```bash
git add data/catalog.schema.json web/src/utils/dataLoader.ts tests/test_schema.py
git commit -m "feat: allow unknown model fields without backfilling them"
```

**Rollback:** Schema- und Zod-Diff zurücknehmen. Alte Einträge bleiben gültig, weil die Felder optional sind.

---

### Task 4: Inkrementeller GitHub-Bericht für eine ID (P3)

**Files:**
- Create: `scripts/refresh_github_report.py`
- Create: `tests/test_refresh_github_report.py`

**Interfaces:**
- Consumes: eine Katalog-ID und ein bereits geladenes GitHub-JSON-Objekt mit `stargazerCount`, `forkCount`, `isArchived`, `pushedAt`, `licenseInfo.spdxId`
- Produces: `build_refresh_report(entry: dict, github: dict) -> dict` mit `id`, `changes`, `unchanged`, `skipped_unknown`. Das Skript schreibt den Katalog nicht. Ein Apply-Modus existiert nicht.

- [ ] **Step 1: Write the failing test**

```python
def test_report_proposes_stars_and_does_not_invent_license_when_github_has_none():
    entry = {"id": "acme/widget", "stars": 10, "license": None, "archived": False, "description": "bleibt"}
    github = {"stargazerCount": 12, "isArchived": False, "licenseInfo": None, "pushedAt": "2026-10-01T00:00:00Z"}
    report = build_refresh_report(entry, github)
    assert report["changes"]["stars"] == {"from": 10, "to": 12}
    assert "license" not in report["changes"]
    assert "description" not in report["changes"]
```

- [ ] **Step 2: Run test to verify it fails**

Expected: Importfehler.

- [ ] **Step 3: Write minimal implementation**

Vergleich nur für `stars`, `forks`, `archived`, `pushed_at` und `license`. `license` nur vorschlagen, wenn der Katalogwert leer ist und GitHub eine konkrete SPDX-ID liefert. `NOASSERTION` nicht als belegte Lizenz schreiben. Beschreibung, Kategorie, Score und die sechs Zukunftsfelder nie anfassen. Die CLI druckt JSON nach stdout. Netzwerk nur, wenn `--fetch` gesetzt ist, über `gh api graphql` für genau eine ID. Tests rufen `--fetch` nicht auf.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_refresh_github_report.py -v`

- [ ] **Step 5: Commit**

```bash
git add scripts/refresh_github_report.py tests/test_refresh_github_report.py
git commit -m "feat: report one GitHub metadata diff without writing the catalog"
```

**Rollback:** Dateien entfernen. Es gibt keinen Schreibpfad.

---

### Task 5: Nur-lesender MCP-Server (P4)

**Files:**
- Create: `mcp/server.py`
- Create: `tests/test_mcp_server.py`
- Create: `mcp/README.md`

**Interfaces:**
- Consumes: Katalog und Taxonomie über Funktionsargumente, in der CLI über lokale Pfade
- Produces:
  - `search_projects(entries, query: str, category: str | None, limit: int) -> list[dict]`
  - `get_project(entries, project_id: str) -> dict | None`
  - `list_categories(taxonomy: dict) -> list[dict]`
  - `handle_message(message: dict, entries, taxonomy) -> dict` für JSON-RPC `initialize`, `tools/list`, `tools/call`

Werkzeuge: `search`, `get_project`, `list_categories`. Transport: MCP-Content-Length-Framing auf stdin/stdout. Keine Shell, kein Schreiben, kein Drittmodul.

- [ ] **Step 1: Write the failing test**

```python
def test_search_matches_name_and_get_project_returns_the_same_id():
    entries = [{"id": "acme/widget", "name": "Widget", "description": "alpha", "primary_category": "D.20"}]
    found = search_projects(entries, "widget", None, 10)
    assert found[0]["id"] == "acme/widget"
    assert get_project(entries, "missing/repo") is None


def test_tools_call_rejects_unknown_tool():
    response = handle_message(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "shell", "arguments": {}}},
        [],
        {"categories": {}},
    )
    assert "error" in response
```

- [ ] **Step 2: Run test to verify it fails**

Expected: Importfehler.

- [ ] **Step 3: Write minimal implementation**

`search` vergleicht die kleingeschriebene Anfrage mit `id`, `name`, `description` und `primary_category`. `limit` wird auf 1–50 begrenzt. `get_project` sucht die exakte `id`. `list_categories` liefert `{id, name, group}` aus der Taxonomie. `tools/call` für jeden anderen Namen liefert einen JSON-RPC-Fehler und startet nichts. README beschreibt den Startbefehl `python mcp/server.py --catalog data/catalog.json --taxonomy data/taxonomy.json` und den Hinweis, dass der Server keine Installationen und keine Schreibzugriffe ausführt.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_mcp_server.py -v`

- [ ] **Step 5: Commit**

```bash
git add mcp/server.py mcp/README.md tests/test_mcp_server.py
git commit -m "feat: add a read-only catalog MCP server"
```

**Rollback:** Verzeichnis `mcp/` und den Test entfernen. Die Website bleibt unberührt.

**Security:** Kein `subprocess`, kein `eval`, Argumente nur als Suchtext und ID. Sicherheitsnotizen eines Eintrags werden mit zurückgegeben, wenn das Feld existiert, und nicht ergänzt.

---

### Task 6: Filter, Quellen und Aktualität (P5)

**Files:**
- Modify: `web/src/pages/explorer.astro`
- Modify: `web/src/pages/project/[slug].astro`
- Test: vorhandene Explorer-Datenattribute bleiben; neue Selects heißen `explorer-license`, `explorer-maintenance`, `explorer-freshness`

**Interfaces:**
- Consumes: `catalogEntries` aus `dataLoader.ts`
- Produces: drei zusätzliche Filter. Lizenz: alle / vorhanden / unbekannt. Wartung: alle plus die vorhandenen Statuswerte. Aktualität: alle / geprüft in den letzten 90 Tagen / älter, bezogen auf ein im Seitenquelltext gesetztes Datum `2026-10-28`. Die Detailseite zeigt `checked_at`, `source_urls`, `discovered_from` und den Text „unbekannt“, wenn Lizenz oder Wartung fehlen.

- [ ] **Step 1: Write the failing test**

```python
def test_explorer_and_detail_expose_filter_and_source_hooks():
    explorer = Path("web/src/pages/explorer.astro").read_text(encoding="utf-8")
    detail = Path("web/src/pages/project/[slug].astro").read_text(encoding="utf-8")
    for element_id in ("explorer-license", "explorer-maintenance", "explorer-freshness"):
        assert f'id="{element_id}"' in explorer
    assert 'data-testid="source-urls"' in detail
    assert "unbekannt" in detail
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL, die IDs fehlen.

- [ ] **Step 3: Write minimal implementation**

Die bestehende `updateExplorer`-Funktion bekommt drei weitere Bedingungen. Keine neuen Scores und keine Vergleichslogik in diesem PR. Leere Quellenfelder werden als „Keine Quellenangabe“ angezeigt, nicht durch erfundene URLs ersetzt.

- [ ] **Step 4: Run test to verify it passes**

Explorer im Browser: Textfilter, Kategorie, die drei neuen Filter, leere Treffermenge, Reset. Detailseite: Quellen und `checked_at` sichtbar. Desktop und eine schmale Viewport-Breite.

- [ ] **Step 5: Commit**

```bash
git add web/src/pages/explorer.astro web/src/pages/project/[slug].astro
git commit -m "feat: filter the explorer by license, maintenance, and freshness"
```

**Rollback:** Die beiden Seiten auf die vorige Fassung zurücksetzen.

---

### Task 7: Vergleichsansicht laut vorhandenem Vertrag (P6)

**Files:**
- Modify: `web/src/pages/index.astro`
- Test: `tests/e2e/comparison.spec.ts` bleibt die Spezifikation

**Interfaces:**
- Consumes: `data-testid="compare-btn"` an Projektkarten, Query `?compare=owner/repo,owner/repo`
- Produces: `comparison-bar`, `comparison-count`, `remove-compare-item`, `comparison-table`, `comparison-column`, `comparison-warning` mit dem Text „Select at least“. Maximal die Felder, die der Katalog bereits hat. Keine berechnete Sieger-Spalte.

- [ ] **Step 1: Write the failing test**

`tests/e2e/comparison.spec.ts` ist der Vertrag und bleibt unverändert. Der erste fehlende Haken ist die Karte:

```ts
test('Tier 1: Compare button should be present on project cards', async ({ page }) => {
  await page.goto('/WERKAtlas/');
  await expect(page.locator('[data-testid="compare-btn"]').first()).toBeVisible();
});
```

Run: `npx playwright test comparison.spec.ts` mit `tests/e2e/playwright.config.ts`.

Expected: FAIL, weil `compare-btn` im DOM fehlt.

- [ ] **Step 2: Run test to verify it fails**

Den ersten Tier-1-Test ausführen und das Fehlen von `compare-btn` sehen.

- [ ] **Step 3: Write minimal implementation**

Auswahlzustand in `sessionStorage` unter dem Schlüssel `werkatlas-compare`. Die Tabelle zeigt Name, Kategorie, Score, Sterne, Lizenz, Wartung und `checked_at`. Fehlende Lizenz erscheint als „unbekannt“. Ein Eintrag mit weniger als zwei gültigen IDs zeigt die Warnung und keine erfundenen Spalten.

- [ ] **Step 4: Run test to verify it passes**

Die Vergleichsspezifikation und danach die Startseite manuell: zwei Karten wählen, eine entfernen, Tabelle mit zwei bekannten Repositories öffnen, unbekannte ID ignorieren.

- [ ] **Step 5: Commit**

```bash
git add web/src/pages/index.astro
git commit -m "feat: compare two catalog projects from the existing page contract"
```

**Rollback:** Startseite zurücksetzen. Explorer und Katalog bleiben gleich.

---

### Task 8: Instagram-IDs nur prüfen (P7)

**Files:**
- Create: `scripts/instagram_id_dry_run.py`
- Create: `tests/test_instagram_id_dry_run.py`

**Interfaces:**
- Consumes: `classify_ids(catalog_ids: set[str], verified_ids: list[str]) -> dict` mit `present`, `absent`, `invalid`, `duplicate_input`
- Produces: JSON-Bericht. Exit 1, wenn eine ID nicht genau ein `owner/name` ist. Exit 0, wenn alle IDs formal gültig sind, auch wenn sie im Katalog fehlen. Kein `--apply`.

- [ ] **Step 1: Write the failing test**

```python
def test_dry_run_splits_present_and_absent_without_writing():
    report = classify_ids({"acme/widget"}, ["acme/widget", "other/repo", "acme/widget"])
    assert report["present"] == ["acme/widget"]
    assert report["absent"] == ["other/repo"]
    assert report["duplicate_input"] == ["acme/widget"]
```

- [ ] **Step 2: Run test to verify it fails**

Expected: Importfehler.

- [ ] **Step 3: Write minimal implementation**

Die CLI liest `--ids` als JSON-Liste. Sie lehnt Dateien ab, deren Schlüssel `drive`, `screenshot` oder `file_id` heißen, und beendet dann mit Exit 2, damit keine privaten Drive-Bezeichner in den Bericht gelangen. Sie gibt nur `owner/name` aus.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_instagram_id_dry_run.py -v`

- [ ] **Step 5: Commit**

```bash
git add scripts/instagram_id_dry_run.py tests/test_instagram_id_dry_run.py
git commit -m "feat: classify verified GitHub ids without importing them"
```

**Rollback:** Die beiden Dateien entfernen.

---

### Task 9: Stabile Suchindex-Schlüssel (P8)

**Files:**
- Modify: `scripts/build_search_index.py` Funktion `slim_entry`
- Test: `tests/test_search_index_order.py`

**Interfaces:**
- Consumes: `INDEX_FIELDS`
- Produces: `slim_entry` schreibt Schlüssel in sortierter Reihenfolge und danach `slug`. Der committete Index wird in diesem PR nicht neu gebaut.

- [ ] **Step 1: Write the failing test**

```python
def test_slim_entry_key_order_is_stable():
    from build_search_index import slim_entry
    entry = {"id": "acme/widget", "repository": "acme/widget", "name": "Widget"}
    assert list(slim_entry(entry).keys()) == list(slim_entry(entry).keys())
    assert list(slim_entry(entry).keys())[-1] == "slug"
```

Die Laufgleichheit allein ist kein Beweis. Zusätzlich die Schlüssel mit `sorted(INDEX_FIELDS) + ["slug"]` vergleichen.

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL, solange die Iteration der Set-Reihenfolge folgt und von `sorted(INDEX_FIELDS)` abweicht. Falls die aktuelle Interpreter-Reihenfolge zufällig gleich ist, den Test auf die explizite Liste stützen.

- [ ] **Step 3: Write minimal implementation**

```python
for field in sorted(INDEX_FIELDS):
    result[field] = entry.get(field)
```

`data/search-index.json` nicht regenerieren. Ein Neubau würde die einzeilige Datei und damit das Review unlesbar machen, ohne die Website zu ändern.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_search_index_order.py -v`

- [ ] **Step 5: Commit**

```bash
git add scripts/build_search_index.py tests/test_search_index_order.py
git commit -m "fix: sort search index fields for a stable rebuild"
```

**Rollback:** Die Schleife zurücksetzen.

---

## Selbstprüfung

- Das Ziel ist ein lesender Zugriff auf den bestehenden Katalog, gemessen an `search`, `get_project` und `list_categories`.
- Architektur, Pipeline, Suche, Astro, Workflows und Tests stehen im Bestandsaudit. Kein Schritt baut daraus ein neues System.
- Dubletten, GitHub-IDs, Quellen, Alter und Schema sind die harten und weichen Regeln von Task 1.
- Ausführungsreihenfolge: Bestand sichern, dann MCP, dann belegte Datenqualität, dann Research-Berichte, dann UI. Task 3 wartet, bis Task 4 einen Beleg hat. Task 6 und Task 7 warten auf Task 5.
- Der Schreibvorgang in den Katalog bleibt einem eigenen Apply-PR vorbehalten.
- 742 ist das alte README-Badge. Die heutige Schwelle Score mindestens 50 trifft 678 Einträge.
- Repomix hat keinen Task und keine Installation.
- Instagram ist Task 8 und nur eine ID-Prüfung.
- Kein Task öffnet eine Datenbank, eine Embedding-Pipeline oder ein zweites Repository.
