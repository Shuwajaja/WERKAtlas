#!/usr/bin/env python3
"""Local WERKAtlas news radar: official RSS/Atom feeds, no LLM, no GitHub Actions.

A headline is a linked claim by its publisher, not independently verified fact.
No code or HTML from feeds is executed. Failed sources are reported, not silently hidden.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import re
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ATOM="{http://www.w3.org/2005/Atom}"
MAX_BYTES=5_000_000
CATEGORIES={"Modelle & Produkte","Forschung","Open Source","Infrastruktur","Paper","Branche","Agenten & Tools","GitHub Releases"}
TRACKING={"utm_source","utm_medium","utm_campaign","utm_content","utm_term","fbclid","gclid"}
CATEGORY_KEYWORDS={
    "Sicherheit":("security","vulnerability","cve-","exploit","prompt injection","safety","vulnerabilit","sicherheits"),
    "Modelle & Produkte":("model","llm","gpt","gemini","claude","mistral","qwen","kimi","deepseek","release","api"),
    "Agenten & Tools":("agent","mcp","workflow","coding","tool","openclaw","browser","orchestration"),
    "Infrastruktur":("gpu","cuda","nvidia","inference","cloud","server","hardware","chip"),
    "Forschung":("research","paper","benchmark","training","eval","study"),
}


def plain(value: str | None, limit: int=360) -> str:
    s=re.sub(r"<[^>]*>", " ", html.unescape(value or ""))
    s=re.sub(r"\s+", " ", s).strip()
    return s[:limit]


def canonical_url(value: str) -> str | None:
    value=(value or "").strip()
    try:
        u=urllib.parse.urlsplit(value)
    except ValueError:
        return None
    if u.scheme not in {"https","http"} or not u.netloc or u.username or u.password:
        return None
    filtered=[(k,v) for k,v in urllib.parse.parse_qsl(u.query,keep_blank_values=True)
              if k.casefold() not in TRACKING and not k.casefold().startswith("utm_")]
    return urllib.parse.urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path or "/",
                                   urllib.parse.urlencode(filtered),""))


def timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt=parsedate_to_datetime(value)
    except (TypeError,ValueError,IndexError):
        try:
            dt=datetime.fromisoformat(value.replace("Z","+00:00"))
        except (TypeError,ValueError):
            return None
    if dt.tzinfo is None:
        dt=dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def classify(title: str, description: str, default_category: str) -> str:
    text=(title+" "+description).casefold()
    for label,words in CATEGORY_KEYWORDS.items():
        if any(re.search(r"(?<!\w)"+re.escape(word),text) for word in words):
            return label
    return default_category


def parse_feed(raw: bytes, source: dict, *, now: datetime | None=None,
               days: int=30) -> list[dict]:
    if len(raw)>MAX_BYTES:
        raise ValueError("Feed exceeds 5MB cap")
    root=ET.fromstring(raw)
    is_atom=root.tag==ATOM+"feed"
    if root.tag not in {"rss","{http://purl.org/rss/1.0/}RDF",ATOM+"feed","RDF"} and not root.tag.endswith("}RDF"):
        raise ValueError("Not an RSS or Atom feed")
    now=(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    nodes=root.findall(f"{ATOM}entry") if is_atom else root.findall(".//item")
    records=[]
    for node in nodes[:source.get("max_items",25)]:
        if is_atom:
            title=node.findtext(f"{ATOM}title")
            links=node.findall(f"{ATOM}link")
            url=next((x.attrib.get("href") for x in links if x.attrib.get("rel") in (None,"alternate")),None)
            description=node.findtext(f"{ATOM}summary") or node.findtext(f"{ATOM}content")
            date=node.findtext(f"{ATOM}published") or node.findtext(f"{ATOM}updated")
        else:
            title=node.findtext("title")
            url=node.findtext("link")
            description=node.findtext("description")
            date=node.findtext("pubDate") or node.findtext("{http://purl.org/dc/elements/1.1/}date")
        title=plain(title,200)
        clean=canonical_url(url or "")
        dt=timestamp(date)
        if not title or clean is None or dt is None:
            continue
        parsed=datetime.fromisoformat(dt)
        if parsed>now+timedelta(hours=2) or parsed<now-timedelta(days=days):
            continue
        summary=plain(description,150)
        records.append({
            "title":title,"url":clean,"summary":summary,
            "published_at":dt,"source_id":source["id"],"source_name":source["name"],
            "source_kind":source["kind"],"category":classify(title,summary,source["category"]),
            "verification":"publisher_claim" if source["kind"]!="research" else "research_preprint",
        })
    return records


def fetch_one(source: dict, *, days: int=30, now:datetime|None=None,
              timeout:float=15.0) -> tuple[list[dict], dict]:
    url=source["url"]
    if not url.startswith("https://"):
        raise ValueError("Only trusted HTTPS sources accepted")
    request=urllib.request.Request(url,headers={
        "User-Agent":"WERKAtlas-NewsRadar/0.1 (+local news monitor)",
        "Accept":"application/rss+xml,application/atom+xml,application/xml,text/xml,*/*"
    })
    try:
        with urllib.request.urlopen(request,timeout=timeout) as response:
            length=response.headers.get("Content-Length")
            if length and int(length)>MAX_BYTES:
                raise ValueError("Feed Content-Length exceeds cap")
            raw=response.read(MAX_BYTES+1)
        items=parse_feed(raw,source,now=now,days=days)
        return items,{"id":source["id"],"name":source["name"],"status":"ok",
                      "count":len(items),"url":url}
    except (OSError,ValueError,ET.ParseError,TimeoutError) as exc:
        return [],{"id":source["id"],"name":source["name"],"status":"error",
                   "error_type":type(exc).__name__,"url":url}


def aggregate(inputs: list[tuple[list[dict],dict]], *, now:datetime|None=None,
              limit:int=280) -> dict:
    now=(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    sources=[status for _,status in inputs]
    dedup={}
    for items,_ in inputs:
        for item in items:
            key=item["url"].rstrip("/").casefold()
            prev=dedup.get(key)
            if prev is None or item["published_at"]>prev["published_at"]:
                dedup[key]=item
    articles=sorted(dedup.values(),key=lambda x:(x["published_at"],x["title"]),reverse=True)[:limit]
    return {
        "generated_at":now.isoformat(),
        "schema_version":1,
        "successful_sources":sum(s["status"]=="ok" for s in sources),
        "failed_sources":sum(s["status"]!="ok" for s in sources),
        "sources":sources,
        "count":len(articles),
        "articles":articles,
        "disclaimer":"Links are source claims or research preprints, not independently verified facts. Availability and dates may vary.",
    }


def build_news(config:dict, *,days:int=30,max_workers:int=5, now:datetime|None=None,
               fetch=fetch_one) -> dict:
    sources=config["sources"]
    if len({s["id"] for s in sources})!=len(sources):
        raise ValueError("Duplicate source identifiers")
    if any(s["category"] not in CATEGORIES for s in sources):
        raise ValueError("Unrecognized category")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures=[executor.submit(fetch,s,days=days,now=now) for s in sources]
        results=[future.result() for future in futures]
    return aggregate(results,now=now)


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description="Build local multi-source AI/tech news radar")
    parser.add_argument("--sources",default=str(ROOT/"data/news-sources.json"))
    parser.add_argument("--output",default=str(ROOT/"web/public/news/latest.json"))
    parser.add_argument("--days",type=int,default=21)
    parser.add_argument("--workers",type=int,default=5)
    args=parser.parse_args(argv)
    if not 1<=args.days<=90 or not 1<=args.workers<=8:
        parser.error("days must be 1..90; workers must be 1..8")
    config=json.loads(Path(args.sources).read_text(encoding="utf-8"))
    result=build_news(config,days=args.days,max_workers=args.workers)
    out=Path(args.output).resolve()
    if out==Path(ROOT/"data/catalog.json").resolve():
        raise SystemExit("Refusing to overwrite canonical catalog")
    if result["successful_sources"]==0:
        print("No usable sources, refusing to overwrite news output",file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True,exist_ok=True)
    # Atomic replacement, keeps previous feed if the updater stops mid-write.
    tmp=out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(out)
    print(json.dumps({"articles":result["count"],
                      "sources_ok":result["successful_sources"],
                      "sources_failed":result["failed_sources"],
                      "output":str(out)},ensure_ascii=False))
    return 0


if __name__=="__main__":raise SystemExit(main())
