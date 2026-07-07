#!/usr/bin/env python3
"""
META-LOOP CONTROLLER — Der Loop, der die Loops steuert.

Führt alle 5 Forschungs-Loos immer wieder aus, bis:
  a) Keine neuen Projekte mehr gefunden werden
  b) Alle Loops erfolgreich durchliefen
  c) Max 10 Iterationen erreicht

Nach jedem kompletten Zyklus: Classify → Score → Render → Validate.

Usage:
    python scripts/meta_loop.py              # Unendlich bis Abbruch
    python scripts/meta_loop.py --max-cycles 3
    python scripts/meta_loop.py --continuous  # Läuft 24/7 und wiederholt fehlgeschlagene Loops
"""

import json, os, sys, time, subprocess, datetime
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = Path(__file__).parent.parent
SCRIPTS = BASE / 'scripts'
CATALOG = BASE / 'data' / 'catalog.json'
STATE_FILE = BASE / 'data' / '_meta_loop_state.json'

# ── State Management ──────────────────────────────────────────────────────

def load_state():
    default = {
        'cycle': 0,
        'total_new_all_time': 0,
        'loop_stats': {str(i): {'attempts': 0, 'successes': 0, 'total_found': 0} for i in range(1, 6)},
        'last_run': None,
        'consecutive_empty_loops': 0,
        'pipeline_status': {'classify': False, 'score': False, 'render': False, 'validate': False},
    }
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, encoding='utf-8') as f:
                saved = json.load(f)
                # Merge with defaults (für neue Felder)
                for k, v in default.items():
                    if k not in saved:
                        saved[k] = v
                return saved
        except:
            pass
    return default

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def get_catalog_size():
    if CATALOG.exists():
        with open(CATALOG, encoding='utf-8') as f:
            return len(json.load(f).get('entries', []))
    return 0

# ── Loop Runner ───────────────────────────────────────────────────────────

LOOP_NAMES = {
    1: 'TOP-DOWN',
    2: 'NICHE',
    3: 'TRENDING',
    4: 'DEEP DIVE',
    5: 'LONGSHOT',
}

LOOP_MAX_RETRIES = {
    1: 5,   # High priority - viele Runs
    2: 5,   # High priority
    3: 3,   # Medium
    4: 10,  # Braucht oft Rate-Limit-Reset
    5: 3,   # Medium (HN + Longshots)
}

def run_loop(loop_num):
    """Führe einen einzelnen Loop aus und gib die Anzahl neuer Candidates zurück."""
    script = str(SCRIPTS / 'loop_orchestrator.py')
    result = subprocess.run(
        [sys.executable, script, '--loop', str(loop_num)],
        capture_output=True, text=True, timeout=300
    )
    
    # Parse output for "total new" or check candidates file
    stdout = result.stdout
    stderr = result.stderr
    
    # Zähle Candidates im Loop-Candidates-File
    cand_file = BASE / 'data' / 'loop_candidates.ndjson'
    old_count = 0
    if cand_file.exists():
        # Lese vorherige Zeilenzahl aus State
        pass
    
    # Merge
    merge_result = subprocess.run(
        [sys.executable, script, '--merge-only'],
        capture_output=True, text=True, timeout=30
    )
    
    # Parse merge output
    new_entries = 0
    for line in merge_result.stdout.split('\n'):
        if 'Neue Eintraege' in line or 'Einträge' in line:
            try:
                new_entries = int(''.join(filter(str.isdigit, line.split(':')[-1])))
            except:
                pass
    
    success = result.returncode == 0
    rate_limited = 'RATE-LIMIT' in stdout or 'rate limit' in stderr.lower()
    
    return {
        'success': success,
        'new_entries': new_entries,
        'rate_limited': rate_limited,
        'stdout': stdout[-500:] if stdout else '',
        'stderr': stderr[-500:] if stderr else '',
    }

# ── Pipeline Steps ────────────────────────────────────────────────────────

def run_pipeline_step(script_name, args=''):
    """Führe einen Pipeline-Schritt aus."""
    script = str(SCRIPTS / script_name)
    cmd = f'"{sys.executable}" "{script}" {args}'
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=True)
    return result.returncode == 0

def run_pipeline():
    """Classify → Score → Render → Validate"""
    print('\n' + '█'*70)
    print('█  PIPELINE: Classify → Score → Render → Validate')
    print('█'*70)
    
    print('\n📊 Classify...')
    ok = run_pipeline_step('classify.py', '--input data/catalog.json --taxonomy data/taxonomy.json --output data/catalog.json')
    print(f'  {"✅" if ok else "❌"} Classify')
    
    print('\n📊 Score...')
    ok = run_pipeline_step('score.py', '--input data/catalog.json --output data/catalog.json')
    print(f'  {"✅" if ok else "❌"} Score')
    
    print('\n📊 Render...')
    ok = run_pipeline_step('render.py', '--catalog data/catalog.json --taxonomy data/taxonomy.json --output .')
    print(f'  {"✅" if ok else "❌"} Render')
    
    print('\n📊 Validate...')
    ok = run_pipeline_step('validate.py', '--catalog data/catalog.json --schema data/catalog.schema.json')
    print(f'  {"✅" if ok else "❌"} Validate')
    return ok

# ── Meta-Loop ─────────────────────────────────────────────────────────────

def meta_loop(max_cycles=10, continuous=False):
    """Der Meta-Loop: Steuert alle 5 Loops in wiederholten Zyklen."""
    
    state = load_state()
    catalog_size_start = get_catalog_size()
    
    print('╔' + '═'*68 + '╗')
    print('║' + ' '*20 + 'META-LOOP CONTROLLER v2.0' + ' '*21 + '║')
    print('║' + ' '*6 + 'Der Loop, der die Loops steuert, die die Loops steuern' + ' '*6 + '║')
    print('╚' + '═'*68 + '╝')
    print()
    print(f'📁 Katalog: {catalog_size_start} Einträge')
    print(f'🔄 Bisherige Zyklen: {state["cycle"]}')
    print(f'📦 Gesamt neu: {state["total_new_all_time"]}')
    print(f'🔁 Continuous Mode: {"ON" if continuous else "OFF"}')
    print()
    
    cycle = state['cycle']
    
    while cycle < max_cycles:
        cycle += 1
        cycle_new = 0
        loop_errors = []
        
        print('\n' + '═'*70)
        print(f'🌍 META-ZYKLUS {cycle}/{max_cycles}')
        print(f'⏰ {datetime.datetime.now().strftime("%H:%M:%S")}')
        print(f'📁 Katalog aktuell: {get_catalog_size()} Einträge')
        print('═'*70)
        
        # ── Loop 1: TOP-DOWN ──
        print('\n─── LOOP 1: TOP-DOWN ───')
        for attempt in range(LOOP_MAX_RETRIES[1]):
            state['loop_stats']['1']['attempts'] += 1
            result = run_loop(1)
            cycle_new += result['new_entries']
            state['loop_stats']['1']['total_found'] += result['new_entries']
            
            if result['new_entries'] > 0:
                state['loop_stats']['1']['successes'] += 1
                print(f'  ✅ {result["new_entries"]} neue Projekte gefunden!')
                break
            elif result['rate_limited']:
                wait = min(30 * (attempt + 1), 300)
                print(f'  ⏳ Rate Limited — warte {wait}s... (Versuch {attempt+1}/{LOOP_MAX_RETRIES[1]})')
                time.sleep(wait)
            else:
                if attempt < LOOP_MAX_RETRIES[1] - 1:
                    print(f'  🔄 Keine neuen, versuche erneut...')
                    time.sleep(10)
                break
        
        # ── Loop 2: NICHE ──
        print('\n─── LOOP 2: NICHE ───')
        for attempt in range(LOOP_MAX_RETRIES[2]):
            state['loop_stats']['2']['attempts'] += 1
            result = run_loop(2)
            cycle_new += result['new_entries']
            state['loop_stats']['2']['total_found'] += result['new_entries']
            
            if result['new_entries'] > 0:
                state['loop_stats']['2']['successes'] += 1
                print(f'  ✅ {result["new_entries"]} neue Projekte gefunden!')
                break
            elif result['rate_limited']:
                wait = min(60 * (attempt + 1), 600)
                print(f'  ⏳ Rate Limited — warte {wait}s... (Versuch {attempt+1}/{LOOP_MAX_RETRIES[2]})')
                time.sleep(wait)
            else:
                break
        
        # ── Loop 3: TRENDING ──
        print('\n─── LOOP 3: TRENDING ───')
        for attempt in range(LOOP_MAX_RETRIES[3]):
            state['loop_stats']['3']['attempts'] += 1
            result = run_loop(3)
            cycle_new += result['new_entries']
            state['loop_stats']['3']['total_found'] += result['new_entries']
            
            if result['new_entries'] > 0:
                state['loop_stats']['3']['successes'] += 1
                print(f'  ✅ {result["new_entries"]} neue Projekte gefunden!')
                break
            elif result['rate_limited']:
                wait = min(60 * (attempt + 1), 600)
                print(f'  ⏳ Rate Limited — warte {wait}s...')
                time.sleep(wait)
            else:
                break
        
        # ── Loop 4: DEEP DIVE ──
        print('\n─── LOOP 4: DEEP DIVE ───')
        for attempt in range(LOOP_MAX_RETRIES[4]):
            state['loop_stats']['4']['attempts'] += 1
            result = run_loop(4)
            cycle_new += result['new_entries']
            state['loop_stats']['4']['total_found'] += result['new_entries']
            
            if result['new_entries'] > 0:
                state['loop_stats']['4']['successes'] += 1
                print(f'  ✅ {result["new_entries"]} neue Projekte gefunden!')
                break
            elif result['rate_limited']:
                wait = min(120 * (attempt + 1), 3600)
                remaining = wait
                print(f'  ⏳ Rate Limited — warte {remaining//60}m {remaining%60}s... (Versuch {attempt+1}/{LOOP_MAX_RETRIES[4]})')
                # Zeige Countdown
                for tick in range(wait // 10):
                    time.sleep(10)
                    remaining -= 10
                    if remaining % 60 == 0:
                        print(f'     Noch {remaining//60}m...', end='\r')
                print()
            else:
                break
        
        # ── Loop 5: LONGSHOT ──
        print('\n─── LOOP 5: LONGSHOT ───')
        for attempt in range(LOOP_MAX_RETRIES[5]):
            state['loop_stats']['5']['attempts'] += 1
            result = run_loop(5)
            cycle_new += result['new_entries']
            state['loop_stats']['5']['total_found'] += result['new_entries']
            
            if result['new_entries'] > 0:
                state['loop_stats']['5']['successes'] += 1
                print(f'  ✅ {result["new_entries"]} neue Projekte gefunden!')
                break
            elif result['rate_limited']:
                wait = min(60 * (attempt + 1), 600)
                print(f'  ⏳ Rate Limited — warte {wait}s...')
                time.sleep(wait)
            else:
                break
        
        # ── Zyklus-Auswertung ──
        state['total_new_all_time'] += cycle_new
        state['cycle'] = cycle
        state['last_run'] = datetime.datetime.now().isoformat()
        
        catalog_size = get_catalog_size()
        
        print('\n' + '─'*70)
        print(f'📊 ZYKLUS {cycle} ERGEBNIS:')
        print(f'  🆕 Neue in diesem Zyklus: {cycle_new}')
        print(f'  📁 Katalog jetzt: {catalog_size} Einträge')
        print(f'  📦 Gesamt seit Start: {state["total_new_all_time"]}')
        
        if cycle_new == 0:
            state['consecutive_empty_loops'] += 1
            print(f'  ⚠️  Leerer Zyklus #{state["consecutive_empty_loops"]}')
        else:
            state['consecutive_empty_loops'] = 0
        
        # ── Pipeline ausführen ──
        print('\n🔄 Führe Pipeline aus...')
        pipeline_ok = run_pipeline()
        print(f'\n  Pipeline: {"✅ ALLES OK" if pipeline_ok else "⚠️  FEHLER"}'  )
        
        # ── Speichere State ──
        save_state(state)
        
        # ── Abbruch-Bedingungen ──
        if state['consecutive_empty_loops'] >= 3:
            print('\n' + '🎯'*35)
            print('🎯  META-LOOP ABGESCHLOSSEN: 3 leere Zyklen hintereinander')
            print('🎯'*35)
            print('\nKeine neuen Projekte mehr auffindbar. Ökosystem vollständig gescannt!')
            break
        
        if cycle >= max_cycles:
            print(f'\nMax Zyklen ({max_cycles}) erreicht.')
            break
        
        if continuous:
            # Warte 30 Minuten vor nächstem Zyklus (damit Rate Limits sich erholen)
            wait_minutes = 30
            print(f'\n⏳ Continuous Mode: Warte {wait_minutes}m vor nächstem Zyklus...')
            for m in range(wait_minutes):
                time.sleep(60)
                if m % 5 == 0:
                    print(f'  ... noch {wait_minutes - m}m')
    
    # ── Final Summary ──
    print('\n' + '█'*70)
    print('█  META-LOOP FINAL SUMMARY')
    print('█'*70)
    print(f'\n📊 Gesamtstatistik:')
    print(f'  Zyklen durchlaufen: {cycle}')
    print(f'  Katalog am Start:   {catalog_size_start}')
    print(f'  Katalog am Ende:    {get_catalog_size()}')
    print(f'  Neu gefunden:       {state["total_new_all_time"]}')
    print(f'  Leere Zyklen:       {state["consecutive_empty_loops"]}')
    print()
    print(f'📊 Loop-Performance:')
    for num in range(1, 6):
        s = state['loop_stats'][str(num)]
        found = s['total_found']
        attempts = s['attempts']
        successes = s['successes']
        print(f'  Loop {num} ({LOOP_NAMES[num]}): {found} found in {attempts} attempts ({successes} successes)')
    
    catalog_size_end = get_catalog_size()
    print(f'\n📁 Endgültiger Katalog: {catalog_size_end} Einträge')
    
    if pipeline_ok:
        print(f'📄 CATALOG.md: ~{os.path.getsize(str(BASE / "CATALOG.md")) // 1024} KB')
    
    print(f'\n💡 Nächste Schritte:')
    print(f'  1. GitHub Token setzen → python scripts/meta_loop.py --continuous')
    print(f'  2. Manuelle Verifikation der Top-Projekte')
    print(f'  3. Lizenzen via API nachtragen')
    print(f'  4. make check-links')
    print()
    print(f'⏰ Beendet: {datetime.datetime.now().strftime("%H:%M:%S")}')

# ── Rate Limit Check ──────────────────────────────────────────────────────

def check_rate_limit():
    """Prüfe GitHub Rate Limit Status."""
    import urllib.request, json
    try:
        req = urllib.request.Request(
            'https://api.github.com/rate_limit',
            headers={'User-Agent': 'meta-loop/2.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            resources = data.get('resources', {})
            core = resources.get('core', {})
            search = resources.get('search', {})
            remaining = core.get('remaining', 0)
            reset = core.get('reset', 0)
            search_remaining = search.get('remaining', 0)
            
            if remaining > 0 or search_remaining > 0:
                return True, remaining, search_remaining
            else:
                reset_time = datetime.datetime.fromtimestamp(reset)
                wait_seconds = max(0, (reset_time - datetime.datetime.now()).total_seconds())
                return False, remaining, wait_seconds
    except:
        return None, 0, 0

# ── Main ──────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Meta-Loop Controller für 5-Loop Research')
    parser.add_argument('--max-cycles', type=int, default=10, help='Maximale Zyklen')
    parser.add_argument('--continuous', action='store_true', help='24/7 Modus mit automatischen Pausen')
    parser.add_argument('--dry-run', action='store_true', help='Nur Status anzeigen')
    parser.add_argument('--reset-state', action='store_true', help='State zurücksetzen')
    args = parser.parse_args()
    
    if args.reset_state and STATE_FILE.exists():
        STATE_FILE.unlink()
        print('State zurückgesetzt.')
        return
    
    # Rate Limit Check
    available, remaining, wait = check_rate_limit()
    if available is None:
        print('⚠️  GitHub API nicht erreichbar (Netzwerk?)')
    elif available:
        print(f'✅ GitHub API: {remaining} Requests verfügbar')
    else:
        wait_m = int(wait // 60)
        wait_s = int(wait % 60)
        print(f'⏳ GitHub API: Rate Limited. Reset in {wait_m}m {wait_s}s')
        if not args.dry_run:
            print(f'   Warte auf Reset...')
            # Warte nur wenn es sinnvoll ist (< 1h)
            if wait < 3600:
                for i in range(int(wait), 0, -60):
                    print(f'   Noch {i//60}m...', end='\r')
                    time.sleep(min(60, wait))
                print()
                print('✅ Rate Limit zurückgesetzt!')
    
    if args.dry_run:
        state = load_state()
        print(f'\n📊 State:')
        print(f'  Zyklen: {state["cycle"]}')
        print(f'  Total neu: {state["total_new_all_time"]}')
        print(f'  Katalog: {get_catalog_size()} Einträge')
        print(f'  Consecutive empty: {state["consecutive_empty_loops"]}')
        print(f'  Letzter Run: {state["last_run"]}')
        print()
        print(f'📊 Loop Stats:')
        for num in range(1, 6):
            s = state['loop_stats'][str(num)]
            print(f'  Loop {num}: {s}')
        return
    
    meta_loop(max_cycles=args.max_cycles, continuous=args.continuous)

if __name__ == '__main__':
    main()
