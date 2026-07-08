import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute()))
sys.stdout.reconfigure(encoding='utf-8')
import json
from classify import infer_category

def main():
    with open('data/catalog.json', 'r', encoding='utf-8-sig') as f:
        catalog = json.load(f)
    with open('data/taxonomy.json', 'r', encoding='utf-8-sig') as f:
        taxonomy = json.load(f)

    fails = []
    for e in catalog['entries']:
        prim, sec = infer_category(e, taxonomy)
        if prim is None:
            fails.append(e)

    print(f"Total fails: {len(fails)}")
    for e in fails[:30]:
        print(f"ID: {e['id']}")
        print(f"  Name: {e.get('name')}")
        print(f"  Topics: {e.get('topics')}")
        print(f"  Desc: {e.get('description')}")
        print(f"  Orig Cat: {e.get('primary_category')}")
        print("-" * 40)

if __name__ == '__main__':
    main()
