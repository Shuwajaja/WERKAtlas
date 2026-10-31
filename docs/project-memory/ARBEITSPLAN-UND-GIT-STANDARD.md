# WERKAtlas – Arbeitsstandard und nächste Schritte

Stand: 31.10.2026. Aktueller Entwicklungsbranch: `feat/news-hub-readable-catalog-20261031`.

## Verantwortliche Dateien
- Kanonischer Projektkatalog: `data/catalog.json`, historische Daten nicht ungeprüft überschreiben.
- Verifizierte GitHub-Metadaten: `data/verified-github.json` (separater Stand).
- News-Quellenkonfiguration: `data/news-sources.json`.
- Letzter exportierter Feed-Stand für die statische Website: `web/public/news/latest.json`.
- Projektgedächtnis: `docs/project-memory/WERKAtlas-PROJEKTGEDAECHTNIS-2026-10-31.md`.

## Arbeitsregeln
1. **Keine GitHub Actions**: Kein PR und kein Merge auf main, solange vorhandene GitHub-Workflows ungewollt ausgelöst werden könnten.
2. Lokal testen: `py -m pytest tests -q`, `cd web; npm run build; npm run test:ui`.
3. Generierte News sind **Daten**, keine Quellcodeänderung. Die lokale tägliche Aktualisierung ändert `web/public/news/latest.json`; diese Änderung **nicht automatisch committen** oder per `git add -A` versehentlich mitnehmen.
4. News nur als knappe Meldungen mit Original-URL, Datum und Quellentyp anzeigen; keine erfundenen Zusammenfassungen oder ungeprüften Qualitätsurteile.
5. Git-Änderungen vor dem Commit gezielt stagen, `git diff --cached --check` und `git diff --cached --stat` ausführen.
6. Änderungen an Katalog, Lizenz und Bewertungen separat prüfen. Der veröffentlichte GitHub-Pages-Stand bleibt von lokalen Experimenten getrennt.

## Phasenplan
- **1. Projektwissen/Git-Hygiene:** Projektgedächtnis und Standards in `docs/` sichern. Generierte News-Daten getrennt behandeln.
- **2. Explorer:** Kategoriebezeichnungen verständlicher machen, Filter und vorhandenen Projektvergleich testen; Karten-, Listen- und Mobilansicht ohne Funktionsverlust verbessern.
- **3. News-Radar:** Quellenverzeichnis und Erreichbarkeit dokumentieren; Dubletten und KI-Relevanz mit Tests verbessern; nicht zu Marketing-News-Abfallhalde werden.
- **4. Metadaten/Trends:** 93 ungeklärte Repos prüfen, SPDX nicht mit kommerzieller Freigabe gleichsetzen; Wachstum nur aus echten Beobachtungen berechnen.
- **5. MCP/CodeReuseLab:** strukturierte Task-Search, Provenienz und Review-Queue, keine automatische Codeübernahme.
- **6. Abnahme/Bereitstellung:** frischer Git-Clone, lokale Python- und Browserprüfungen, dokumentierter manueller Deploy-Weg **ohne GitHub Actions**.

## Letzter belegter Teststand
- 177 Python-Tests und 10 Playwright-Browsertests am 31.10.2026 erfolgreich (vor der jetzigen nächsten Entwicklungsphase).
- Explorer-Karten 18 pro Anzeige, separater Suchindex; News-Radar 21 RSS/Atom-Quellen.
- Windows-Aufgaben: `WERKAtlas_Local_Radar` 08:00 Uhr sowie `WERKAtlas_News_Refresh` 12:00, 16:00 und 20:00 Uhr; Ausführung nur bei verfügbarem Windows-PC/Berechtigungen.

**Aktueller Status:** Nicht alle sechs Phasen fertig. Entwicklung erfolgt inkrementell und mit nachprüfbaren Ergebnissen.
