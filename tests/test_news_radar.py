"""WERKAtlas News Radar regression tests: RSS, Atom, freshness, integrity."""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from news_radar import parse_feed, aggregate, canonical_url, plain, build_news
from run_research_hub import commands_for

NOW=datetime(2026,10,31,14,0,tzinfo=timezone.utc)
SOURCE={"id":"test","name":"Demo News","kind":"official","category":"Modelle & Produkte","max_items":10,"url":"https://example.org/rss"}

def test_parse_rss_links_dates_and_filters_html():
    feed=b'''<?xml version="1.0"?><rss version="2.0"><channel>
      <item><title>New AI model</title><link>https://example.com/news?a=1&amp;utm_source=rss</link>
      <description>&lt;p&gt;Shipping &amp;amp; testing&lt;/p&gt;</description>
      <pubDate>Sat, 31 Oct 2026 10:00:00 GMT</pubDate></item>
      <item><title>Too old</title><link>https://example.com/old</link>
      <pubDate>Sat, 31 Oct 2020 10:00:00 GMT</pubDate></item>
    </channel></rss>'''
    rows=parse_feed(feed,SOURCE,now=NOW,days=21)
    assert len(rows)==1
    assert rows[0]["url"]=="https://example.com/news?a=1"
    assert rows[0]["verification"]=="publisher_claim"
    assert "<p>" not in rows[0]["summary"]

def test_atom_release_and_research_preprint():
    atom=b'''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
      <entry><title>New release</title><link href="https://github.com/org/repo/releases/tag/v1" rel="alternate"/>
      <updated>2026-10-31T08:00:00Z</updated><summary>Agent tools</summary></entry>
      </feed>'''
    source={**SOURCE,"kind":"release","category":"GitHub Releases"}
    rows=parse_feed(atom,source,now=NOW)
    assert rows[0]["source_kind"]=="release"
    assert rows[0]["category"] in {"GitHub Releases","Agenten & Tools","Modelle & Produkte"}

def test_invalid_link_and_future_date_ignored():
    assert canonical_url("javascript:alert(1)") is None
    assert canonical_url("https://user:pass@example.com/path") is None
    feed=b'''<rss><channel><item><title>Oops</title><link>javascript:evil()</link>
       <pubDate>Sat, 31 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>'''
    assert parse_feed(feed,SOURCE,now=NOW)==[]

def test_dedup_and_source_failures_reported():
    item={"title":"News","url":"https://example.com/a","published_at":"2026-10-31T10:00:00+00:00","source_name":"Test",
          "source_id":"one","source_kind":"official","category":"Forschung","summary":"","verification":"publisher_claim"}
    result=aggregate([([item],{"id":"one","status":"ok"}),([dict(item)],{"id":"two","status":"error"})],now=NOW)
    assert result["count"]==1
    assert result["failed_sources"]==1

def test_news_config_and_failure_continue():
    sources=json.loads((ROOT/"data/news-sources.json").read_text(encoding="utf-8"))["sources"]
    assert len(sources)>=15
    assert len({x["id"] for x in sources})==len(sources)
    def fake_fetch(source,**kwargs):
        return [],{"id":source["id"],"status":"error","error_type":"Test"}
    result=build_news({"sources":sources[:2]},now=NOW,fetch=fake_fetch)
    assert result["failed_sources"]==2
    assert result["count"]==0

def test_daily_wrapper_runs_news_even_if_github_already_done():
    only_news=commands_for("2026-10-31",True)
    assert len(only_news)==1 and only_news[0][1].endswith("news_radar.py")
    all_tasks=commands_for("2026-10-31",False)
    assert len(all_tasks)==2 and all_tasks[1][1].endswith("daily_local.py")

def test_saved_news_is_source_labeled():
    report=json.loads((ROOT/"web/public/news/latest.json").read_text(encoding="utf-8"))
    assert report["successful_sources"]>=10
    assert all(item["url"].startswith(("http://","https://")) for item in report["articles"])
    assert all(item["verification"] in ("publisher_claim","research_preprint") for item in report["articles"])
    assert all("published_at" in item and item["source_name"] for item in report["articles"])
