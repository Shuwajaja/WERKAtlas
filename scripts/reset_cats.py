#!/usr/bin/env python3
"""Reset all primary_categories to null, then re-classify."""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'catalog.json')

with open(path, 'r', encoding='utf-8-sig') as f:
    d = json.load(f)

for e in d['entries']:
    e['primary_category'] = None

tmp = path + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, path)

print(f'Reset {len(d["entries"])} entries')
