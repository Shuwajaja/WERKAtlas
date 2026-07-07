#!/usr/bin/env python3
"""
deep_research.py — Multi-Source Deep Research for Hidden Gems.

Sucht nach versteckten Perlen im AI-Agent-Ökosystem über:
1. HackerNews API (Top Stories, Show HN, Ask HN)
2. GitHub Deep Search (Topics, READMEs, Sort by recent/new)
3. GitHub Trends (aktuelle 7 Tage, neue Repos)
4. Kuratierte Community-Listen

Usage:
    python scripts/deep_research.py --catalog data/catalog.json --output data/candidates.ndjson
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).parent.parent
USER_AGENT = "agentic-engineering-compendium/1.0"
REQUEST_DELAY = 1.0
SNAPSHOT_DATE = "2026-07-07"

now = datetime.now(timezone.utc).isoformat()

# ── Caching ────────────────────────────────────────────────────────────────

_cache = {}
CACHE_FILE = BASE / "data" / "_research_cache.json"

def load_cache():
    global _cache
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding="utf-8-sig") as f:
            try:
                _cache = json.load(f)
            except:
                _cache = {}

def save_cache():
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(_cache, f, indent=2)


# ── HTTP Helpers ───────────────────────────────────────────────────────────

def fetch_json(url, cache_key=None, use_cache=True):
    if use_cache and cache_key and cache_key in _cache:
        print(f"    [cache] {url[:80]}")
        return _cache[cache_key]
    
    time.sleep(REQUEST_DELAY)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if cache_key:
                _cache[cache_key] = data
                save_cache()
            return data
    except Exception as e:
        print(f"    [error] {url[:60]}: {e}")
        return None


# ── 1. HackerNews API ──────────────────────────────────────────────────────

HN_BASE = "https://hacker-news.firebaseio.com/v0"

def search_hackernews_agent_threads():
    """Finde die wichtigsten HackerNews Threads zu AI Agents."""
    print("\n=== 1. HackerNews: AI Agent Threads ===")
    
    results = []
    
    # Hole Top Stories (letzte 200)
    print("  Fetching top stories...")
    story_ids = fetch_json(f"{HN_BASE}/topstories.json", cache_key="hn_topstories")
    if not story_ids:
        return results
    
    # Nimm die 30 aktuellsten
    for story_id in story_ids[:30]:
        story = fetch_json(f"{HN_BASE}/item/{story_id}.json", cache_key=f"hn_item_{story_id}")
        if not story:
            continue
        
        title = (story.get("title") or "").lower()
        url = story.get("url") or ""
        
        # Suche nach AI/Agent-relevanten Threads
        keywords = [
            "ai agent", "agent", "mcp", "model context", "llm", "claude", 
            "chatgpt", "gpt", "openai", "coding agent", "autonomous", 
            "tool use", "function calling", "rag", "vector", "embedding",
            "langchain", "langgraph", "autogen", "crewai", "browser agent",
            "computer use", "sandbox", "ai coding", "swe-agent", "aider",
        ]
        
        if any(k in title for k in keywords):
            print(f"  Found: {story.get('title')}")
            results.append({
                "source": "hackernews",
                "title": story.get("title"),
                "url": url or f"https://news.ycombinator.com/item?id={story_id}",
                "points": story.get("score"),
                "descendants": story.get("descendants"),
                "by": story.get("by"),
                "time": datetime.fromtimestamp(story.get("time", 0), tz=timezone.utc).isoformat() if story.get("time") else None,
                "relevance": "ai-agent",
                "checked_at": now,
            })
    
    # Show HN: Neue Projekte
    print("  Fetching Show HN stories...")
    show_ids = fetch_json(f"{HN_BASE}/showstories.json", cache_key="hn_showstories")
    if show_ids:
        for story_id in show_ids[:20]:
            story = fetch_json(f"{HN_BASE}/item/{story_id}.json", cache_key=f"hn_show_{story_id}")
            if not story:
                continue
            title = (story.get("title") or "").lower()
            if any(k in title for k in ["ai", "agent", "llm", "mcp"]):
                print(f"  Show HN: {story.get('title')}")
                results.append({
                    "source": "hackernews_show",
                    "title": story.get("title"),
                    "url": story.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                    "points": story.get("score"),
                    "relevance": "show-hn-project",
                    "checked_at": now,
                })
    
    print(f"  Total HN results: {len(results)}")
    return results


# ── 2. GitHub Deep Search ──────────────────────────────────────────────────

GITHUB_API = "https://api.github.com"

def github_search(query, sort="stars", order="desc", page=1, per_page=50):
    """GitHub API Suche mit verschiedenen Sortierungen."""
    url = f"{GITHUB_API}/search/repositories?q={urllib.parse.quote(query)}&sort={sort}&order={order}&page={page}&per_page={per_page}"
    time.sleep(2.0)  # Rate limit protection
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"    GitHub API Error {e.code}: {e.reason[:50]}")
        if e.code == 403:
            print("    RATE LIMITED — will continue with what we have")
        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def github_deep_search():
    """Tiefergehende GitHub-Suche mit verschiedenen Strategien."""
    print("\n=== 2. GitHub Deep Search ===")
    
    existing_ids = set()
    cat_path = BASE / "data" / "catalog.json"
    if cat_path.exists():
        with open(cat_path, encoding="utf-8-sig") as f:
            cat = json.load(f)
            existing_ids = set(e["id"] for e in cat.get("entries", []))
    
    all_candidates = []
    
    # Strategie A: Neu erstellte Projekte (sort by created)
    print("\n  [A] Neu erstellte AI-Agent-Projekte...")
    queries_new = [
        "ai-agent created:>2026-01-01",
        "mcp-server created:>2026-01-01",
        "llm-agent created:>2026-01-01",
        "browser-agent created:>2026-01-01",
        "autonomous-agent created:>2026-01-01",
    ]
    for q in queries_new:
        result = github_search(q, sort="stars", order="desc")
        if result and result.get("items"):
            for item in result["items"][:20]:
                rid = item["full_name"]
                if rid not in existing_ids:
                    all_candidates.append(("github_new", q, item))
                    existing_ids.add(rid)
    
    # Strategie B: Wenig Stars aber hohe Relevanz (recently updated)
    print("\n  [B] Nischen-Projekte (recently pushed, <1000 stars)...")
    queries_niche = [
        "topic:ai-agent stars:<1000",
        "topic:mcp-server stars:<500 pushed:>2026-03-01",
        "agent-framework stars:<500 language:rust",
        "agent-framework stars:<500 language:go",
        "agent-framework stars:<500 language:python",
        "computer-use stars:<1000",
        "agent-memory stars:<1000",
        "agent-security stars:<500",
        "guardrails stars:<500",
        "agent-evaluation stars:<500",
        "agent-observability stars:<500",
        "multi-agent stars:<1000",
        "agent-sandbox stars:<500",
        "tool-calling stars:<500",
    ]
    for q in queries_niche:
        result = github_search(q, sort="updated", order="desc")
        if result and result.get("items"):
            for item in result["items"][:10]:
                rid = item["full_name"]
                if rid not in existing_ids:
                    all_candidates.append(("github_niche", q, item))
                    existing_ids.add(rid)
    
    # Strategie C: Trending (most stars, recently)
    print("\n  [C] Trending Projekte (most stars, last 3 months)...")
    queries_trending = [
        "ai-agent created:>2025-04-01 stars:>100",
        "mcp created:>2025-04-01 stars:>100",
        "coding-agent created:>2025-04-01",
        "agent-tool created:>2025-04-01",
    ]
    for q in queries_trending:
        result = github_search(q, sort="stars", order="desc")
        if result and result.get("items"):
            for item in result["items"][:15]:
                rid = item["full_name"]
                if rid not in existing_ids:
                    all_candidates.append(("github_trending", q, item))
                    existing_ids.add(rid)
    
    # Strategie D: Sprachen-Vielfalt (Rust, Go, Java, Kotlin)
    print("\n  [D] Language-spezifische Agent-Projekte...")
    queries_lang = [
        "ai-agent language:rust stars:>50",
        "ai-agent language:go stars:>50",
        "ai-agent language:java stars:>50",
        "ai-agent language:kotlin stars:>50",
        "ai-agent language:swift stars:>50",
        "mcp-server language:rust",
        "mcp-server language:go",
        "mcp-client language:rust",
        "mcp-client language:go",
    ]
    for q in queries_lang:
        result = github_search(q, sort="stars", order="desc")
        if result and result.get("items"):
            for item in result["items"][:5]:
                rid = item["full_name"]
                if rid not in existing_ids:
                    all_candidates.append(("github_language", q, item))
                    existing_ids.add(rid)
    
    return all_candidates


# ── 3. GitHub Organization Deep Dive ───────────────────────────────────────

def github_org_repos(org):
    """Hole alle Repos einer Organisation."""
    url = f"{GITHUB_API}/orgs/{org}/repos?per_page=100&sort=pushed"
    time.sleep(2.0)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except:
        return []


def deep_org_discovery():
    """Suche in weniger bekannten GitHub Organizations."""
    print("\n=== 3. GitHub Organization Deep Dive ===")
    
    existing_ids = set()
    cat_path = BASE / "data" / "catalog.json"
    if cat_path.exists():
        with open(cat_path, encoding="utf-8-sig") as f:
            cat = json.load(f)
            existing_ids = set(e["id"] for e in cat.get("entries", []))
    
    # Organisationen, die spannende Agent-Projekte haben könnten
    orgs_to_check = [
        "e2b-dev",           # Cloud sandboxes
        "composiohq",        # Tool integrations
        "gptscript-ai",      # Script-based agents
        "fixie-ai",          # AI platform
        "chainlit",          # Chat UI
        "embedchain",        # RAG
        "superagent-ai",     # Agent framework
        "getmetal",          # Memory/RAG
        "superlinked",       # Vector search
        "homanp",            # Superagent
        "largeworldai",      # Agent infrastructure
        "agpt-co",           # AutoGPT org
        "microsoft",         # Viele Agent-Projekte
        "anthropics",        # Claude ecosystem
        "openai",            # OpenAI ecosystem
        "langchain-ai",      # LangChain ecosystem
        "crewAI",            # Multi-agent
        "huggingface",       # Transformers, smolagents
        "run-llama",         # LlamaIndex
        "AutoMQ",            # AutoMQ
        "composiohq",        # Tool integration
        "plandex-ai",        # Coding agent
    ]
    
    all_found = []
    for org in orgs_to_check:
        repos = github_org_repos(org)
        if not repos:
            continue
        for repo in repos:
            rid = repo["full_name"]
            if rid in existing_ids:
                continue
            # Filtere Relevanz
            topics = [t.lower() for t in repo.get("topics", [])]
            name = (repo.get("name") or "").lower()
            desc = (repo.get("description") or "").lower()
            
            relevant_keywords = [
                "agent", "ai", "llm", "mcp", "gpt", "claude", "rag", "vector",
                "embedding", "chat", "cognition", "autonomous", "tool", "skill",
                "plugin", "function calling", "knowledge", "memory", "orchestrat",
                "swarm", "multi-agent", "browser", "computer-use", "sandbox",
                "eval", "guardrail", "observability", "tracing"
            ]
            
            if any(k in " ".join(topics + [name, desc]) for k in relevant_keywords):
                stars = repo.get("stargazers_count", 0)
                print(f"  {rid}: {stars}★ — {repo.get('description','')[:60]}")
                all_found.append(("github_org", org, repo))
                existing_ids.add(rid)
    
    print(f"  New org repos found: {len(all_found)}")
    return all_found


# ── 4. Awesome Lists Cross-Reference ───────────────────────────────────────

def awesome_lists_cross_reference():
    """Cross-reference bekannte Awesome Lists für versteckte Perlen."""
    print("\n=== 4. Awesome Lists Cross-Reference ===")
    
    awesome_sources = {
        "awesome-ai-agents": "e2b-dev/awesome-ai-agents",
        "awesome-mcp-servers": "punkpeye/awesome-mcp-servers",
        "awesome-ai-coding-agents": "nicepkg/awesome-ai-coding-agents",
        "awesome-chatgpt-prompts": "f/awesome-chatgpt-prompts",
    }
    
    existing_ids = set()
    cat_path = BASE / "data" / "catalog.json"
    if cat_path.exists():
        with open(cat_path, encoding="utf-8-sig") as f:
            cat = json.load(f)
            existing_ids = set(e["id"] for e in cat.get("entries", []))
    
    found = []
    for list_name, repo in awesome_sources.items():
        # Lese README via API (als Base64 encoded)
        url = f"{GITHUB_API}/repos/{repo}/readme"
        time.sleep(2.0)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                import base64
                content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                
                # Extrahiere GitHub-Links
                import re
                gh_links = re.findall(r"github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)", content)
                for link in gh_links:
                    if link not in existing_ids:
                        found.append({"list": list_name, "repo": link})
                        existing_ids.add(link)
                
                print(f"  {list_name}: {len(gh_links)} links extracted, {len(found)} new")
        except Exception as e:
            print(f"  {list_name}: error - {e}")
    
    return found


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("DEEP RESEARCH: Hidden Gems & Community Projects")
    print(f"Snapshot: {SNAPSHOT_DATE}")
    print("=" * 70)
    
    load_cache()
    
    all_candidates = []
    
    # 1. HackerNews
    hn_results = search_hackernews_agent_threads()
    
    # 2. GitHub Deep Search
    gh_candidates = github_deep_search()
    
    # 3. Organization Deep Dive
    org_candidates = deep_org_discovery()
    
    # 4. Awesome Lists 
    awesome_found = awesome_lists_cross_reference()
    
    # Sammle alles
    print("\n\n" + "=" * 70)
    print("ERGEBNISSE")
    print("=" * 70)
    print(f"  HackerNews Threads:        {len(hn_results)}")
    print(f"  GitHub Deep Search:        {len(gh_candidates)}")
    print(f"  Organization Deep Dive:    {len(org_candidates)}")
    print(f"  Awesome List Referenzen:   {len(awesome_found)}")
    
    total_new = len(gh_candidates) + len(org_candidates)
    print(f"\n  Neue Katalog-Kandidaten:   {total_new}")
    print(f"  HN Threads zur Recherche:  {len(hn_results)}")
    print(f"  Awesome List Verweise:     {len(awesome_found)}")
    
    # Speichere HN-Ergebnisse
    hn_path = BASE / "research" / "subagents" / "hackernews_finds.json"
    with open(hn_path, "w", encoding="utf-8") as f:
        json.dump(hn_results, f, indent=2, ensure_ascii=False)
    print(f"\n  HackerNews Ergebnisse: {hn_path}")
    
    # Speichere GitHub-Kandidaten als NDJSON
    cand_path = BASE / "data" / "deep_candidates.ndjson"
    with open(cand_path, "w", encoding="utf-8") as f:
        for source, query, item in gh_candidates:
            record = {
                "id": item["full_name"],
                "name": item.get("name"),
                "owner": item.get("owner", {}).get("login"),
                "repository": item.get("full_name"),
                "repository_url": item.get("html_url"),
                "description": item.get("description"),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language"),
                "topics": item.get("topics", []),
                "source": source,
                "query": query,
                "checked_at": now,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        for source, org, item in org_candidates:
            record = {
                "id": item["full_name"],
                "name": item.get("name"),
                "owner": item.get("owner", {}).get("login"),
                "repository": item.get("full_name"),
                "repository_url": item.get("html_url"),
                "description": item.get("description"),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language"),
                "topics": item.get("topics", []),
                "source": source,
                "query": org,
                "checked_at": now,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"  Kandidaten gespeichert: {cand_path}")
    
    # Awesome-List Referenzen speichern
    awesome_path = BASE / "research" / "subagents" / "awesome_references.json"
    with open(awesome_path, "w", encoding="utf-8") as f:
        json.dump(awesome_found, f, indent=2, ensure_ascii=False)
    print(f"  Awesome References: {awesome_path}")
    
    print("\n" + "=" * 70)
    print("NÄCHSTE SCHRITTE:")
    print("  1. python scripts/enrich.py --candidates data/deep_candidates.ndjson --catalog data/catalog.tmp.json")
    print("  2. Manuelle Prüfung: research/subagents/awesome_references.json")
    print("  3. HackerNews Threads lesen: research/subagents/hackernews_finds.json")
    print("  4. Neue Einträge in catalog.json mergen")
    print("  5. make score && make render && make validate")


if __name__ == "__main__":
    main()
