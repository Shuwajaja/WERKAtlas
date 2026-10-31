# WERKAtlas News & Project Explorer (31.10.2026)

**Status:** Lokaler Research-Hub auf dem separaten Feature-Branch. Keine GitHub Actions, keine automatische Katalogänderung und kein automatisches öffentliches Deployment.

## Was ist neu?

- `/WERKAtlas/explorer/` lädt statt 1.516 vollständigen HTML-Karten einen kompakten Suchindex und zeigt 18 Karten pro Abschnitt. Suchen nach Wörtern in Name, Beschreibung, Kategorie, Themen, Fähigkeiten und Protokollen; Filter für Lizenz/SPDX, verifizierte GitHub-Metadaten, Wartung und Prüfdatum; Sortierung, Listenansicht, Themenchips.
- `/WERKAtlas/news/` führt KI-/Tech-Artikel, Forschung, Anbieter-Ankündigungen und ausgewählte GitHub-Releases getrennt vom Projektkatalog zusammen. Suche, Quelle, Datum und Themen sind filterbar.
- `/WERKAtlas/sources/` zeigt alle Feeds mit Abrufstatus, Quellentyp und Original-URL. Herstellerankündigungen sind keine verifizierten technischen Aussagen, Preprints keine Peer-Review-Papers.
- `data/news-sources.json` enthält die kuratierte Quellenliste, aktuell 21 offizielle/sekundäre/akademische/release RSS- und Atom-Feeds.

## News aktualisieren

```powershell
cd C:\Workplace\WERKAtlas-Main-Verify
py scripts/news_radar.py --days 21
py scripts/run_research_hub.py --news-only
```

Die beiden Befehle aktualisieren `web/public/news/latest.json` atomar. HTML aus Feeds wird nicht ausgeführt, Tracking-Parameter werden aus URLs entfernt. Es wird kein fremder Artikeltext vollständig veröffentlicht, nur Titel, kurze Teaser, Publikationsdatum und Original-Link. Ein Quellenfehler bleibt sichtbar.

Konfiguration: RSS/Atom URL in `data/news-sources.json` eintragen (HTTPS) und manuell erneut testen. **Nicht jeder Anbieter hat einen eigenen RSS-Feed:** Anthropic und Meta AI fehlen deshalb bei direkten Hersteller-News. Zusätzliche offizielle Release-Feeds können eingefügt werden; scraping ist nicht Bestandteil dieses Systems.

## Lokale Automatisierung

Zwei Windows-Aufgaben wurden eingerichtet:

- `WERKAtlas_Local_Radar` täglich um **08:00** lokaler Zeit: GitHub-Metadaten/Radar und News.
- `WERKAtlas_News_Refresh` täglich um **12:00, 16:00, 20:00**: nur News.

Nur wenn Windows eingeschaltet ist und das Benutzerkonto läuft, werden die Aufgaben ausgeführt. `scripts/install_daily_task.ps1 -Install` richtet diese Zeitpläne erneut ein. Die News-Snapshots werden lokal geändert, nicht automatisch zur öffentlichen Webseite hochgeladen.

Zur Deaktivierung:

```powershell
Unregister-ScheduledTask -TaskName WERKAtlas_Local_Radar -Confirm:$false
Unregister-ScheduledTask -TaskName WERKAtlas_News_Refresh -Confirm:$false
```

## Prüfen, testen und Oberfläche starten

```powershell
py -m pytest tests -q
cd web
npm ci --ignore-scripts
npm run build
npm run test:ui
npm run dev -- --host 127.0.0.1 --port 4321
```

Im Browser lokal `http://127.0.0.1:4321/WERKAtlas/explorer/` oder `http://127.0.0.1:4321/WERKAtlas/news/` öffnen.

**Wichtig:** Die öffentliche GitHub-Pages-Webseite wird nicht automatisch aktualisiert. Das bleibt eine separate Entscheidung ohne GitHub Actions. Die Meldungen sind Quellenhinweise, kein allgemeiner Wahrheits-, Lizenz- oder Software-Sicherheitsnachweis.
