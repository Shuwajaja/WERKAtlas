#!/usr/bin/env python3
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Workplace\agentic-engineering-compendium\data\catalog.json'
with open(path, 'r', encoding='utf-8-sig') as f:
    d = json.load(f)

seen = set()
unique = []
removed = 0
for e in d['entries']:
    r = e['repository']
    if r in seen:
        removed += 1
        print(f'  Duplicate: {r}')
    else:
        seen.add(r)
        unique.append(e)

d['entries'] = unique
d['count'] = len(unique)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'Removed {removed} duplicates')
print(f'Total: {len(unique)}')
