#!/usr/bin/env python3
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'catalog.json')
print(f'Reading {path}...')

with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

fixed = 0
for e in d['entries']:
    cat = e.get('primary_category')
    if cat is None or cat == 'TEST':
        e['primary_category'] = 'J.81'
        fixed += 1

print(f'Fixed {fixed} entries')

tmp = path + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, path)

with open(path, 'r', encoding='utf-8') as f:
    d2 = json.load(f)

n = sum(1 for e in d2['entries'] if e.get('primary_category') is None)
print(f'Remaining null: {n}')
print(f'Total: {len(d2["entries"])}')
print(f'Sample: {[e.get("primary_category") for e in d2["entries"][:3]]}')
