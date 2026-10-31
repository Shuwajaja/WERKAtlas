#!/usr/bin/env python3
"""Surgical README statistics refresh. Never runs destructive render.py."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def refresh_readme(content: str, entries: list[dict]) -> str:
    total=len(entries)
    essential=sum(e["score"]>=85 for e in entries)
    strong=sum(75<=e["score"]<85 for e in entries)
    emerging=sum(65<=e["score"]<75 for e in entries)
    watchlist=sum(50<=e["score"]<65 for e in entries)
    excluded=sum(e["score"]<50 for e in entries)
    accepted=total-excluded
    changed=content
    changed=re.sub(r'!\[Projects\]\(https://img.shields.io/badge/projects-\d+-2563eb\)',
                   f'![Projects](https://img.shields.io/badge/projects-{total}-2563eb)',changed,count=1)
    changed=re.sub(r'!\[Accepted\]\(https://img.shields.io/badge/accepted-\d+-16a34a\)',
                   f'![Accepted](https://img.shields.io/badge/accepted-{accepted}-16a34a)',changed,count=1)
    changed=re.sub(r'\| \d+ \| \d+ \| \d+ \| 10 \| 81 \| [^|]+ \|',
                   f'| {total} | {accepted} | {excluded} | 10 | 81 | Historischer Katalog-Snapshot |',
                   changed,count=1)
    rows={
        "Essential":(essential,"85+"),"Strong":(strong,"75-84"),"Emerging":(emerging,"65-74"),
        "Watchlist":(watchlist,"50-64"),"Excluded":(excluded,"<50"),
    }
    for label,(count,interval) in rows.items():
        pattern=r'\| '+label+r' \| [^|]+ \| \d+ \|'
        changed,n=re.subn(pattern,lambda m:f'| {label} | {interval} | {count} |',changed,count=1)
        if n!=1:raise ValueError("Missing score row: "+label)
    notice=("> **Datenhinweis (31.10.2026):** Die Kennzahlen oben sind aus "
            "`data/catalog.json` neu gezählt. Einige lange README-Projektlisten "
            "sind historische Ausschnitte, keine aktuellen Ranglisten. Aktuelle "
            "GitHub-Metadaten und ihre Grenzen stehen im lokalen `data/verified-github.json` "
            "und unter `/WERKAtlas/quality/`. Der alte Score ist kein "
            "aktuelles Sicherheits- oder Lizenzgutachten.\n\n")
    if "Datenhinweis (31.10.2026)" not in changed:
        anchor="## Start Here\n"
        if anchor not in changed:raise ValueError("README marker missing")
        changed=changed.replace(anchor,notice+anchor,1)
    return changed


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args=parser.parse_args()
    src=ROOT/"README.md"
    text=src.read_text(encoding="utf-8")
    entries=json.loads((ROOT/"data/catalog.json").read_text(encoding="utf-8"))["entries"]
    result=refresh_readme(text,entries)
    if args.write:
        src.write_text(result,encoding="utf-8")
        print("README summary refreshed, no other files modified")
    else:
        print("README summary "+("current" if result==text else "outdated; pass --write"))
    return 0 if result==text or args.write else 2

if __name__=="__main__":raise SystemExit(main())
