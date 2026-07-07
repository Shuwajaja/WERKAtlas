#!/usr/bin/env python3
"""Fix missing project_type and empty descriptions in catalog."""
import json, os, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Workplace\agentic-engineering-compendium'
path = os.path.join(BASE, 'data', 'catalog.json')

with open(path, encoding='utf-8') as f:
    data = json.load(f)

# Map primary_category -> default project_type
CAT_TO_TYPE = {
    'A.1': 'tutorial', 'A.2': 'tutorial', 'A.3': 'collection',
    'A.4': 'reference implementation', 'A.5': 'research project',
    'B.6': 'framework', 'B.7': 'runtime', 'B.8': 'framework',
    'B.9': 'framework', 'B.10': 'runtime', 'B.11': 'library',
    'B.12': 'library',
    'C.13': 'application', 'C.14': 'CLI tool', 'C.15': 'IDE extension',
    'C.16': 'developer tool', 'C.17': 'developer tool',
    'C.18': 'developer tool', 'C.19': 'benchmark',
    'D.20': 'MCP server', 'D.21': 'MCP client', 'D.22': 'SDK',
    'D.23': 'registry', 'D.24': 'gateway', 'D.25': 'developer tool',
    'D.26': 'library', 'D.27': 'developer tool', 'D.28': 'collection',
    'E.29': 'collection', 'E.30': 'library', 'E.31': 'collection',
    'E.32': 'package manager', 'E.33': 'library', 'E.34': 'protocol',
    'E.35': 'library', 'E.36': 'library',
    'F.37': 'library', 'F.38': 'library', 'F.39': 'library',
    'F.40': 'library', 'F.41': 'library', 'F.42': 'library',
    'F.43': 'library',
    'G.44': 'application', 'G.45': 'application', 'G.46': 'library',
    'G.47': 'library', 'G.48': 'sandbox', 'G.49': 'sandbox',
    'G.50': 'sandbox', 'G.51': 'library', 'G.52': 'application',
    'H.53': 'observability platform', 'H.54': 'developer tool',
    'H.55': 'evaluation framework', 'H.56': 'benchmark',
    'H.57': 'library', 'H.58': 'library', 'H.59': 'library',
    'H.60': 'library', 'H.61': 'library', 'H.62': 'evaluation framework',
    'H.63': 'library',
    'I.64': 'gateway', 'I.65': 'library', 'I.66': 'application',
    'I.67': 'library', 'I.68': 'application', 'I.69': 'library',
    'I.70': 'library', 'I.71': 'application', 'I.72': 'application',
    'J.73': 'application', 'J.74': 'application', 'J.75': 'application',
    'J.76': 'application', 'J.77': 'application', 'J.78': 'application',
    'J.79': 'application', 'J.80': 'application', 'J.81': 'template',
}

fixed_type = 0
fixed_desc = 0
default_desc = 'AI agent ecosystem project for building, running, or evaluating autonomous AI systems.'

for entry in data['entries']:
    if not entry.get('project_type'):
        cat = entry.get('primary_category')
        entry['project_type'] = CAT_TO_TYPE.get(cat, 'library')
        fixed_type += 1
    if not (entry.get('description') or '').strip():
        entry['description'] = default_desc
        fixed_desc += 1

data['count'] = len(data['entries'])

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Fixed {fixed_type} missing project_types')
print(f'Fixed {fixed_desc} empty descriptions')
print(f'Total: {len(data["entries"])} entries')
