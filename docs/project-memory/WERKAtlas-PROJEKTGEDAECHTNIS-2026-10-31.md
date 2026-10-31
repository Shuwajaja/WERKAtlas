# WERKAtlas – Projektgedächtnis und Übergabe
Stand: 31.10.2026, Europe/Berlin

## Projektidentität
- GitHub: `Shuwajaja/WERKAtlas`; CodeReuseLab ist ein **separates** privates Repository `Shuwajaja/CodeReuseLab`.
- Leitbild: WERKAtlas recherchiert/katalogisiert/bewertet GitHub-Projekte und führt einen quellentransparenten KI-/Tech-News-Radar. CodeReuseLab analysiert und extrahiert nach Freigabe wiederverwendbare Komponenten.
- Keine GitHub Actions für neue Entwicklungs- und Testabläufe. WERKAtlas hat noch historische Workflow-Dateien auf `main`; deshalb Änderungen zunächst auf Branches ohne PR/Merge, soweit Actions ausgelöst würden.

## WERKAtlas stabile Basis
- Katalog `data/catalog.json`: 1.516 Projekte, historischer Snapshot 2026-07-07.
- P0–P5 Feature-Branch: `feat/six-phase-local-atlas-20261031`, Commit `6c5bf5ad4fe5f93ab663a29f99e66d14c46c8b8e` (getestet, nach GitHub gepusht, nicht auf main).
- Verifizierte Sidecar-Daten: `data/verified-github.json`, 1.423 Repos über GitHub GraphQL bestätigt, davon 1.121 SPDX-Werte; 93 ungeklärt. Lizenz-ID ist **keine** rechtliche Code-Nutzungsfreigabe.
- Sicheres lokales Workflow-CLI: `py scripts/local_workflow.py verify`; `recommend --query 'voice sip' --require-all`; `backlog`.
- P3: `scripts/explain_quality.py` trennt vorläufige Qualitätssignale und Task-Keyword-Treffer, keine unbelegten Benchmarks.
- Radar: `scripts/metadata_graphql.py`, `metadata_probe.py`, `radar_local.py`, `verified_trends.py`, `daily_local.py`, `run_research_hub.py`.
- Bekannte lokale Tests der Basis: 170/170 Python-Tests; 1.522 Astro-Seiten im damaligen Build. Diese Zahlen stammen vom vorigen Feature-Branch-Stand.

## Aktueller UI/News-Ausbau (laufende Arbeit dieser Unterhaltung)
- Arbeitsverzeichnis am verbundenen Windows-Rechner: `C:\Workplace\WERKAtlas-Main-Verify`.
- Aktueller Arbeitsbranch: `feat/news-hub-readable-catalog-20261031`, basierend auf dem P0–P5-Branch. **Noch nicht als fertig committed/gepusht bestätigt** zum Zeitpunkt der Übergabe.
- Explorer `web/src/pages/explorer.astro` neu als Dark/Mint-Design mit kompaktem Index `web/src/pages/catalog-index.json.ts`, `web/src/scripts/explorer-client.ts`, 18 sichtbaren Karten pro Abschnitt, Themenchips, Suche, Sortierung, Karten-/Listenansicht, Filtern für Lizenz/SPDX, verifizierte Metadaten, Wartung und Aktualität. Der anfängliche HTML-Umfang sank von ca. 6,5 MB auf ca. 9 KB plus Index von ca. 1,2 MB.
- News-Seite `web/src/pages/news.astro` plus `news-client.ts`; Quellenverzeichnis `sources.astro`; mobile Navigation in `BaseLayout.astro`.
- Feed-Konfiguration `data/news-sources.json` mit 21 RSS-/Atom-Quellen: OpenAI, DeepMind, Google Research/AI, Hugging Face, Qwen, NVIDIA, Microsoft Research, arXiv, TechCrunch, Ars Technica, MIT Technology Review, The Decoder, Simon Willison, GitHub-Releases u. a. Nicht alle bekannten Anbieter haben eigene Feeds.
- Aktualisierung `py scripts/news_radar.py --days 21` oder `py scripts/run_research_hub.py --news-only`: ca. 280 jüngere Einträge; letzter wiederholter Abruf 21/21 Quellen erfolgreich. Jeder Eintrag hat Ursprungslink, Quellenart und Veröffentlichungsdatum. Herstellerbehauptungen, unabhängige Medien und Preprints sind ausdrücklich unterschieden, nicht automatisch bestätigt.
- News-Datensatz: `web/public/news/latest.json`, lokal generiert und nicht automatisch auf die öffentliche Website deployed.
- Windows-Task-Scheduler: `WERKAtlas_Local_Radar` 08:00 (GitHub+News); `WERKAtlas_News_Refresh` 12:00, 16:00, 20:00 (News), lokale Zeit, Benutzerkontext, kein GitHub Actions. Nur bei verfügbarem PC/Benutzer; Taskstatus als Ready geprüft.
- Lokal zuletzt 177/177 Python-Tests grün und 10/10 Playwright-Chrome-Browsertests grün (Desktop und 390px-Smartphone). Quellenansicht, Navigation, Suchfilter geprüft. Nachfolgende Änderungen und abschließender Git-Commit müssen erneut geprüft werden.
- Screenshots lokal: `docs/previews/explorer-desktop.png`, `docs/previews/news-desktop.png`, `docs/previews/news-mobile.png`.
- Lokale Astro-Website über `cd web && npm run dev -- --host 127.0.0.1 --port 4321`; Adresse `http://127.0.0.1:4321/WERKAtlas/` und `/explorer/`, `/news/`, `/sources/`, `/quality/`. Nur lokal, keine öffentliche Live-Veröffentlichung.

## Offene nächste Schritte
1. Laufende Änderungen im Branch `feat/news-hub-readable-catalog-20261031` auf Git-Status prüfen, Desktop/mobile Browser-Tests erneut ausführen, temporäre Build- und Testartefakte nicht einchecken, sorgfältig committen und Branch pushen **ohne PR**, sofern Actions auf PR getriggert werden.
2. README/`docs/NEWS-AND-EXPLORER-2026-10-31.md` final prüfen.
3. Quellenumfang weiter kuratieren: z. B. offizielle Quellen für Anthropic, Meta, DeepSeek/GLM/Kimi/MiniMax, Forschung und Sicherheit, nur nach Existenz-/Aktualitätsprüfung; keine erfundenen Feeds.
4. Nachrichten-Ranking/Deduplikation verbessern, Relevanz nach KI/Agenten/LLMs/Entwicklung/OSS und Spam-Ausschlüsse, Herkunftsnachweise beibehalten.
5. Bei Bedarf einen sicheren Veröffentlichungsweg der statischen Website ohne GitHub Actions festlegen. Das öffentliche GitHub-Pages-Deployment ist nicht aktuell.
6. Ungeklärte 93 GitHub-Repos und 1.400 historische Lizenzlücken weiterhin quellenbasiert bearbeiten; beobachtete Trends erst nach mehreren echten Datums-Snapshots.

## Sicherheit und Arbeitsprinzip
- Reuse-first, Open Source und kostengünstig/selfhostbar.
- Read-only als Standard; keine produktiven VPS-Eingriffe und keine unfreigegebenen Katalogänderungen.
- Keine Secrets in Chat, Repo oder Berichten. GitHub Credential Manager-Token nur kurzzeitig und in-memory.
- CodeReuseLab (private GitHub repo) zuletzt v0.6 auf main, commit `6b3eee1`, lokale Tests und React-Vorschau mit 28 Unit- und 6 Browsertests. Kein GitHub Actions im CodeReuseLab.
