# WERKAtlas: lokale Abläufe ohne GitHub Actions

**Regel:** Keine GitHub Actions für diese Entwicklungsabläufe starten. Der Katalog bleibt bei Recherche, Validierung und Berichten bytegleich. `data/catalog.json` ist die einzige kanonische Datenquelle.

## 1. Vor jeder Änderung: lokal prüfen

Windows / PowerShell:

```powershell
cd C:\Workplace\WERKAtlas-Main-Verify
py scripts/local_workflow.py verify
```

Linux / macOS:

```bash
python3 scripts/local_workflow.py verify
# Alternativ: make (Default ist nun read-only verify)
```

Der Befehl validiert Schema und doppelte IDs, prüft den Katalog gegen den **heutigen UTC-Stichtag** und führt die Python-Tests aus. Der SHA-256 des Katalogs wird davor und danach kontrolliert. `--skip-tests` beschleunigt bei Bedarf die reine Schema-/Bestandsprüfung.

## 2. Nach passenden Projekten suchen

```powershell
py scripts/local_workflow.py recommend --query "voice sip" --require-all --limit 10
py scripts/local_workflow.py recommend --query "voice" --license MIT --limit 5 --output research/voice-review.json
```

- `--require-all` bedeutet: **jeder Suchbegriff muss in vorhandenen Katalogfeldern belegbar sein**. Keine semantische Behauptung, kein automatischer Check der GitHub-Originalquellen.
- Ohne `--require-all` sind Teiltreffer erlaubt; `unmatched_terms` und `unknown_fields` zeigen die Grenzen.
- `--output` erstellt **nur eine neue Datei**, niemals ein bestehendes Dokument oder die kanonischen `data/`-Dateien. Bereits vorhandene Pfade führen zum Fehler.
- Das Suchergebnis ist **keine** automatische Lizenzprüfung oder Funktionsgarantie. Vor einer Empfehlung offizielle Repos prüfen.

## 3. Metadatenlücken priorisieren

```powershell
py scripts/local_workflow.py backlog --limit 20 --output research/metadata/mein-review.json
```

Keine Datenaktualisierung, kein GitHub-API-Aufruf, keine erdachten Lizenzen. Der Bericht dient als Review-Queue. Neues `checked_at` erst nach echtem Quellencheck.

## 4. Änderungsvorschläge sicher verarbeiten

1. Vorhandene Katalog-ID oder neue Repo-URL finden. Dubletten abgleichen.
2. Offizielle README, LICENSE, Releases und aktuelle Commits prüfen; Quellen hinterlegen.
3. Zunächst kleine Diff-Berichte/Review-PRs erstellen; **nicht** `catalog.json` massenhaft überschreiben.
4. Änderungen lokal mit `verify` testen. Das eigentliche Apply/Commit erfolgt separat nach Prüfung.
5. Kein Deploy, kein automatischer Merge und keine GitHub Actions durch dieses lokale Workflow-CLI.

## 5. Gesperrte alte Make-Ziele

`make` ist nun identisch zu `make verify` und schreibt **nichts** um. Die alten Ziele `collect`, `enrich`, `classify`, `score`, `render`, `clean`, `setup` sind im Makefile deaktiviert. Besonders das frühere `make clean` hätte `data/catalog.json` gelöscht. Die zugrundeliegenden Skripte sind weiterhin vorhanden; sie dürfen nur nach Backup und gezielter Prüfung manuell verwendet werden. Eine Datenmigration ist nicht erfolgt.

**Wichtig:** Das Repository besitzt derzeit noch historische Dateien unter `.github/workflows/`. Diese lokalen Anweisungen führen sie nicht aus, deaktivieren sie aber auch nicht. Änderungen daran müssen separat auf Auswirkungen auf bestehende GitHub-Pages-Veröffentlichung und andere Abläufe geprüft werden.
