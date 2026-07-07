#!/usr/bin/env python3
"""Filtere die Deep-Research-Kandidaten und mergt die relevanten in den Katalog."""
import json, os, re, sys

# Force UTF-8 output for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = r'C:\Workplace\agentic-engineering-compendium'

# Lade Kandidaten
candidates = []
with open(os.path.join(BASE, 'data', 'deep_candidates.ndjson'), encoding='utf-8-sig') as f:
    for line in f:
        line = line.strip()
        if line:
            candidates.append(json.loads(line))

# Lade bestehenden Katalog
with open(os.path.join(BASE, 'data', 'catalog.json'), encoding='utf-8') as f:
    catalog = json.load(f)

existing_ids = set(e['id'] for e in catalog['entries'])

# Agent-relevante Keywords
AGENT_KEYWORDS = re.compile(r'(agent|mcp|llm|ai[ -]?(assist|tool|code|coding|power|driven)|'
    r'autonomous|browser[ -]?(agent|automation)|rag|vector|embedding|retrieval|'
    r'tool[ -]?calling|function[ -]?calling|model[ -]?context[ -]?protocol|'
    r'chatgpt|claude|gpt|openai|sandbox|code[ -]?execution|'
    r'workflow[ -]?orchestrat|multi[ -]?agent|prompt[ -]?(engineering|optim)|'
    r'evaluation|benchmark|developer[ -]?tool|code[ -]?review|code[ -]?generation|'
    r'knowledge[ -]?graph|vector[ -]?database|observability|tracing|monitoring|'
    r'skill|plugin|extension|integration|automation|workflow|'
    r'chat[ -]?interface|assistant|orchestrat)', re.IGNORECASE)

FALSE_KEYWORDS = re.compile(r'(stock|trading|crypto|investment|portfolio|'
    r'diet|fitness|workout|health|career|resume|job[ -]?search|interview|'
    r'game|gaming|npc|minecraft|movie|music|spotify|'
    r'real[ -]?estate|property|rent|sport|football|soccer|basketball|'
    r'social[ -]?media|instagram|tiktok)', re.IGNORECASE)

relevant = []
false_positives = []
neutral = []

for c in candidates:
    name = (c.get('name') or '').lower()
    desc = (c.get('description') or '').lower()
    topics = ' '.join(c.get('topics', []) or []).lower()
    fulltext = f"{name} {c['repository'].lower()} {desc} {topics}"
    
    is_false = bool(FALSE_KEYWORDS.search(fulltext))
    is_agent = bool(AGENT_KEYWORDS.search(fulltext))
    
    if is_false and not is_agent:
        false_positives.append(c)
    elif is_agent:
        relevant.append(c)
    else:
        neutral.append(c)

relevant.sort(key=lambda x: x.get('stars', 0), reverse=True)

print(f'Insgesamt Kandidaten: {len(candidates)}')
print(f'Davon relevant (AI/Agent): {len(relevant)}')
print(f'False Positives: {len(false_positives)}')
print(f'Neutral/Unclear: {len(neutral)}')

print(f'\n=== TOP 50 RELEVANTE NEUE KANDIDATEN ===')
for c in relevant[:50]:
    new_flag = 'NEU' if c['repository'] not in existing_ids else 'DUP'
    print(f'  [{new_flag}] {c["repository"]:50s} Stars={c["stars"]:>6d}  Lang={str(c.get("language") or "?"):>10s}')
    desc = (c.get('description') or '')[:80]
    if desc:
        print(f'         {desc}')

print(f'\n=== TOP 20 NEUTRALE (koennten relevant sein) ===')
neutral.sort(key=lambda x: x.get('stars', 0), reverse=True)
for c in neutral[:20]:
    new_flag = 'NEU' if c['repository'] not in existing_ids else 'DUP'
    print(f'  [{new_flag}] {c["repository"]:50s} Stars={c["stars"]:>6d}  Lang={str(c.get("language") or "?"):>10s}')
    desc = (c.get('description') or '')[:80]
    if desc:
        print(f'         {desc}')

# Statistik
new_relevant = [c for c in relevant if c['repository'] not in existing_ids]
print(f'\n=== ZUSAMMENFASSUNG ===')
print(f'Neue Katalog-Kandidaten (relevant): {len(new_relevant)}')
print(f'\nTop 15 neue Projekte:')
for c in new_relevant[:15]:
    print(f'  Stars={c["stars"]:>6d}  {c["repository"]}')
    print(f'         {c.get("description","")[:100]}')

# Speichere relevante Kandidaten separat
output = os.path.join(BASE, 'data', 'filtered_candidates.ndjson')
with open(output, 'w', encoding='utf-8') as f:
    for c in relevant:
        if c['repository'] not in existing_ids:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')
print(f'\nGefilterte Kandidaten gespeichert: {output}')
print(f'Anzahl: {len(new_relevant)}')
