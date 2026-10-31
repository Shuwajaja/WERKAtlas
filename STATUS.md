# STATUS

Stand: 2026-10-31. Basis: `main` bei `fadfb50` (Merge von PR #13). Diese Datei ist die führende Übersicht. Sie ändert keine Katalogdaten.

Es gibt acht Remote-Branches, deren Commits nicht in der Historie von `main` liegen. Fünf davon sind inhaltlich schon in `main`. Drei hängen linear zusammen und sind als ein PR gebündelt. Kein Branch wurde gelöscht, keiner wurde per Force-Push umgeschrieben, nichts wurde gemergt.

## Acht Branches

| Branch | Inhalt | Schon in `main`? | Vorschlag |
| --- | --- | --- | --- |
| `cursor/cloud-agent-dev-env-26ef` | Ein Commit, zehn Zeilen in `AGENTS.md` (Dev-Server, pytest, Playwright). | Inhalt ja. `AGENTS.md` ist bytegleich mit `main`. Der Commit `2f93292` selbst ist kein Ancestor; dieselbe Notiz kam über PR #11 (`2e1cd6c`). | Verwerfen. Kein zweites PR. Branch bleibt. |
| `feat/metadata-review-backlog-20261031` | `scripts/metadata_backlog.py`, Prioritäten-JSON, Tests. | Ja. PR #17 ist gemergt. Ein Merge mit `main` ergibt denselben Tree wie `main`. | Verwerfen. Branch bleibt. |
| `feat/werkatlas-ranked-discovery-20261031` | Read-only MCP-Tool `recommend`. | Ja. PR #15 ist gemergt. Merge-Tree gleich `main`. | Verwerfen. Branch bleibt. |
| `fix/scheduled-audit-live-date-2026-10-31` | Geplanter Audit nutzt das aktuelle UTC-Datum. | Ja. PR #14 ist gemergt. Merge-Tree gleich `main`. | Verwerfen. Branch bleibt. |
| `fix/werkatlas-explorer-current-freshness-20261031` | Explorer-Aktualität relativ zu jetzt, unbekannte Daten als `unknown`. | Ja. PR #16 ist gemergt. Merge-Tree gleich `main`. | Verwerfen. Branch bleibt. |
| `improve/safe-local-workflows-20261031` | Makefile-Default `verify`; destruktive Ziele abgeschaltet. Ein Commit `606cc6e`. | Nein. | Bündeln. Ancestor der beiden folgenden Branches. Kein eigenes PR. |
| `feat/six-phase-local-atlas-20261031` | Offline P0–P5: lokale Workflows plus Metadaten-Snapshots und Qualitätsskripte. Commits `606cc6e`, `6c5bf5a`. | Nein. | Bündeln. Ancestor des News-Hub-Branches. Kein eigenes PR. |
| `feat/news-hub-readable-catalog-20261031` | Die beiden vorigen Commits plus lesbarer Katalog, News-Radar und Handoff. Vier Commits, 50 Dateien gegenüber dem Merge-Base. | Nein. | PR, gemeinsam mit den zwei Ancestors. |

Das Bündel liegt auf `cursor/bundle-local-atlas-news-b5e7` (Merge von `feat/news-hub-readable-catalog-20261031` auf aktuelles `main`, ohne die Ursprungsbranches zu verändern): https://github.com/Shuwajaja/WERKAtlas/pull/18

Diese Statusdatei und die Dokumentenverschiebung: https://github.com/Shuwajaja/WERKAtlas/pull/19

## Weitere Remote-Branches

Diese Tips sind Ancestors von `main`. Vorschlag jeweils: verwerfen, Branch nicht löschen.

| Branch | Enthalten über |
| --- | --- |
| `cursor/werkatlas-v2-repo-reconciliation-e194` | PR #1 |
| `cursor/werkatlas-v2-p0-audit-e194` | PR #2 |
| `cursor/werkatlas-v2-p1-no-direct-push-e194` | PR #4 |
| `cursor/werkatlas-v2-p4-mcp-e194` | PR #5 |
| `cursor/werkatlas-v2-p3-github-refresh-e194` | PR #6 |
| `cursor/werkatlas-v2-p7-instagram-dry-run-e194` | PR #7 |
| `cursor/werkatlas-v2-p8-search-index-order-e194` | PR #8 |
| `cursor/werkatlas-v2-p5-filters-compare-e194` | PR #9 |
| `research/atlas-radar-2026-10-29` | PR #10 |
| `cursor/werkatlas-v2-agents-cloud-docs-e194` | PR #11 |
| `cursor/werkatlas-v2-plan-reconciliation-note-e194` | PR #12 |
| `research/atlas-radar-2026-10-30` | PR #13 |

## Dokumente im Hauptordner

Kanonische Katalog- und Vertragsdateien bleiben im Hauptordner: `README.md`, `AGENTS.md`, `BUILD-YOUR-OWN.md`, `CATALOG.md`, `LANDSCAPE.md`, `TOP-PICKS.md`, `TRENDING.md`, `WATCHLIST.md`, `ARCHIVED.md`, `METHODOLOGY.md`, `CONTRIBUTING.md`, `SECURITY.md`, `STATUS.md`.

Verschoben, nichts gelöscht:

| Bisher | Jetzt | Warum |
| --- | --- | --- |
| `ORIGINAL_REQUEST.md` | `docs/archive/ORIGINAL_REQUEST.md` | Wortlaut der Anfrage vom 2026-07-08. Historisch. |
| `PLANS.md` | `docs/archive/PLANS.md` | Frühe Loop-Checkliste. Der v2-Plan liegt unter `docs/superpowers/plans/`. |
| `TEST_READY.md` | `docs/archive/TEST_READY.md` | Punktuelle Test-Attestierung aus einem früheren Meilenstein. Die Astro-App existiert inzwischen. |
| `TEST_INFRA.md` | `docs/testing/TEST_INFRA.md` | Weiterhin die technische Beschreibung der E2E-Suites, kein Katalogeinstieg. |

Historische Notizen unter `.agents/` nennen noch die alten Windows-Pfade. Das sind Arbeitsprotokolle, keine Laufzeitverweise. Die kanonischen Pfade stehen in dieser Datei.

## Prüfung dieses Stands

Auf dem Bündel-Branch, vor dem Öffnen des PR:

- `python3 -m pytest tests/ -q --ignore=tests/e2e` → 177 passed, 2 Warnungen (pytest-Fixture-Deprecation, unverändert aus dem Bestand).
- `python3 scripts/validate.py --catalog data/catalog.json --schema data/catalog.schema.json` → VALIDATION PASSED, 1516 Einträge.
- Playwright `web/tests/catalog-news.spec.mjs`: in diesem Lauf nicht ausgeführt.
- `scripts/with_github_token.ps1`, GraphQL- und News-Abrufe: nicht ausgeführt. Im Diff liegt kein API-Key. Das Skript liest zur Laufzeit den Windows-Git-Credential-Manager und gibt das Geheimnis nicht aus.

## Offenes

- PR #18 und PR #19 sind Vorschläge und sind nicht gemergt.
- Ob die großen Snapshot-Dateien (`data/verified-github.json`, `research/metadata/2026-10-31-graphql-all1516.json`, `web/public/news/latest.json`) noch dem Live-Stand von GitHub entsprechen: UNKNOWN. Sie wurden hier nicht neu abgefragt.
- Ob die neuen Astro-Seiten im Browser die Katalognavigation und den News-Hub korrekt zeigen: UNKNOWN. Kein Playwright-Lauf und kein Browser-Check in diesem Arbeitsgang.
- Ob GitHub die alten Branches nach dem Merge des Bündels noch anzeigt: sie bleiben absichtlich liegen.
