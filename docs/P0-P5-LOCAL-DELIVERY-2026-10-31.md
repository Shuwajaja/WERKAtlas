# WERKAtlas: P0–P5 lokaler Ausbau (31.10.2026)

**Kein GitHub Actions.** Dies ist ein überprüfbarer, Review-first Ausbau auf einem separaten Git-Branch. Weder eine Website-Bereitstellung noch das automatische Mergen von Katalogänderungen sind freigegeben. Der öffentliche Atlas bleibt bis zu einem kontrollierten Deployment beim bisherigen Snapshot.

## Status

| Phase | Implementiert und lokal prüfbar | Noch nicht erledigt |
|---|---|---|
| P0: Sicherheit | Standard-`make` ist read-only; `scripts/local_workflow.py verify` validiert Schema, prüft Daten und führt Tests aus. | Historische GitHub-Actions-Dateien existieren weiterhin im Repo, werden nicht für diese Arbeit ausgeführt |
| P1: Metadaten | Vollabgleich aller 1.516 GitHub-IDs: 1.423 verifizierte Repos, 1.121 mit SPDX-Lizenzkennung. `data/verified-github.json` zeigt die geprüften Werte, ohne den historischen Katalog zu überschreiben. | 93 Repos konnten nicht bestätigt werden. SPDX sagt noch nichts über kommerzielle Nutzbarkeit aus; manuelle Lizenzprüfung bleibt nötig. |
| P2: Suche | Read-only `recommend`-MCP und lokale `--require-all`-Suche. Explorer durchsucht zusätzlich Topics, Protokolle und Capabilities und verlangt alle Wörter. | Keine verifizierte semantische Suche, Treffer belegen nur vorhandenen Katalogtext |
| P3: Bewertung | `scripts/explain_quality.py` trennt belegbare Qualitäts-Signale (mit Coverage) von Keyword-Task-Fit. Alte Scores bleiben als `legacy_score` markiert. | Keine allgemeine empirische Nutzenbewertung oder echte Sicherheitszertifizierung |
| P4: Research/Trends | Lokaler Radar, tägliche Schnappschüsse, echte Zeitvergleiche. Windows-Aufgabe `WERKAtlas_Local_Radar` wurde für 08:00 Uhr lokal eingerichtet. | Betrieb nur bei verfügbarem Rechner/Benutzer, erste geplante Ausführung noch nicht beobachtet; echte 7/30/90-Tage-Trends benötigen weitere Zeitpunkte. |
| P5: Oberfläche | Neue Seite `/WERKAtlas/quality/`, Quelle und Katalog-Snapshot sichtbar, bessere Mehrwortsuche und korrekte Behandlung unbekannter Lizenzen. | Live-Site noch nicht deployed; Browser-E2E nach Live-Deployment separat prüfen |

## Lokal auf Windows ausführen

```powershell
cd C:\Workplace\WERKAtlas-Main-Verify

# P0: Validierung, Audit und Tests (schreibt keine Katalogdaten)
py scripts/local_workflow.py verify

# P1: echte GitHub-REST-Daten, nur neue Reportdatei
py scripts/metadata_probe.py --limit 10 --offset 20 --output research/metadata/next-ten.json

# P2: All-Words-Suche; unvollständige Treffer werden ausgeschlossen
py scripts/local_workflow.py recommend --query "voice sip" --require-all

# P3: Qualität und Tasks-Fit trennen
py scripts/explain_quality.py --query "voice sip" --limit 10

# P4: GitHub-Radar und bestätigte Trends
py scripts/radar_local.py --query "voice agent sip" --limit 10 --output research/metadata/radar-new.json
py scripts/daily_local.py --batch-size 10

# P5: neue Astro-Website bauen (kein Deployment)
cd web
npm ci --ignore-scripts
npm run build
```

Beispielberichte aus dem Lauf 31.10.2026: `research/metadata/2026-10-31-github-proposals.json` (12 API-Treffer), `research/metadata/2026-10-31-voice-radar.json` (10 Kandidaten), `research/metadata/2026-10-31-quality-vs-fit.json`, `research/local-daily/2026-10-31-summary.json`.

## Review-/Importregeln

1. Repos nur anhand der offiziellen GitHub-Identität akzeptieren.
2. `NOASSERTION`, fehlende Lizenz und ein mit Stars besetzter Datensatz gelten nicht als Rechtsfreigabe.
3. `pushed_at`, `stars`, `forks`, `archived`, `license` werden im Review-Bericht aus GitHub-Fakten vorgeschlagen. Das Katalogfeld `checked_at` darf erst aktualisiert werden, wenn die relevante Eintragsbeschreibung geprüft wurde.
4. API-Ausfälle, Rate-Limits und fehlende Quellen erzeugen keinen Ersatzwert.
5. Tages-Snapshots dürfen nie rückdatiert werden. Wenn ein Mindestabstand fehlt, wird `insufficient_history` oder `insufficient_time_span` ausgegeben.
6. Keine GitHub Actions, keine automatische produktive Installation oder fremde Codeausführung, keine Auto-Merges.
7. Bei Datenübernahme: kleine Review-Diffs, Validierung und Rollback vor Deployment.

## Grenze der Vollständigkeit

P0–P5 sind als lokale, testbare Funktionspfade umgesetzt. Das ist **nicht gleichbedeutend** mit der vollständigen Ermittlung aller Projektfakten, 100 % Lizenzdeckung, finalen Qualitäts-Scores, einer produktiv laufenden Uhrzeit-Automation oder einer aktualisierten öffentlichen Website. Diese Arbeit hängt von echten Quellenprüfungen, zeitlichen Beobachtungen und einem separaten Deployment-Prozess ohne GitHub Actions ab.

## Vollabgleich der Metadaten und lokaler Zeitplan

- Offizieller GitHub-GraphQL-Bericht: `research/metadata/2026-10-31-graphql-all1516.json` (1.516 IDs, davon 1.423 verifiziert, 93 ungeklärt).
- Kompakte Website-Quellschicht: `data/verified-github.json` (1.121 konkrete SPDX-Kennungen).
- Wiederholung in einer gebündelten, **lesenden** Abfrage mit vorhandenem Windows-Git-Login:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/with_github_token.ps1 -Limit 100 -Offset 100 -Output research/metadata/new-review.json
```

Der Token wird nur zur Laufzeit aus dem bestehenden Windows-Git-Credential-Manager gelesen, nicht gespeichert oder ausgegeben. Bei einem Fehlschlag bleibt eine Partial-Datei als lokaler Prüfstand erhalten.

Die Windows-Aufgabe `WERKAtlas_Local_Radar` ruft lokal täglich um 08:00 `scripts/daily_local.py --batch-size 10` auf. Sie wurde mit dem aktuellen Benutzerkonto und begrenzten Rechten registriert, **nicht** über GitHub Actions. Zum Deaktivieren:

```powershell
Unregister-ScheduledTask -TaskName WERKAtlas_Local_Radar -Confirm:$false
```

Aktuell ist der Ablauf nur im Arbeitsverzeichnis des verbundenen Windows-Rechners aktiv. Der GitHub-Branch wurde noch nicht nach `main` übernommen und die öffentliche GitHub-Pages-Website nicht bereitgestellt.
