#!/usr/bin/env python3
"""
collect.py — LOOP 1: Candidate collection from GitHub API and known sources.

Collects candidates into data/candidates.ndjson.

Usage:
    python scripts/collect.py [--candidates-file data/candidates.ndjson] [--sources-file data/sources.json]
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ── Config ──────────────────────────────────────────────────────────────────
BASE_URL = "https://api.github.com"
USER_AGENT = "agentic-engineering-compendium/1.0"
REQUEST_DELAY = 2.0  # seconds between unauthenticated requests
MAX_RETRIES = 3
SNAPSHOT_DATE = "2026-07-07"

# ── Rate limit tracking ─────────────────────────────────────────────────────

class RateLimiter:
    """Simple rate limiter for unauthenticated GitHub API access."""
    
    def __init__(self):
        self.remaining = 60
        self.reset_time = 0
        self.last_request = 0.0
    
    def wait(self):
        """Wait to respect rate limits and request delay."""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request = time.time()
    
    def update_from_headers(self, headers):
        """Update rate limit info from response headers."""
        remaining = headers.get("X-RateLimit-Remaining")
        if remaining is not None:
            self.remaining = int(remaining)
        reset = headers.get("X-RateLimit-Reset")
        if reset is not None:
            self.reset_time = int(reset)
    
    def check_limit(self):
        """Check if we're approaching the rate limit."""
        if self.remaining <= 2:
            wait_time = max(self.reset_time - time.time(), 0) + 5
            if wait_time > 0 and wait_time < 3600:
                print(f"  Rate limit near: waiting {wait_time:.0f}s until reset...")
                time.sleep(wait_time)
                return True
        return False


rate_limiter = RateLimiter()


# ── HTTP helpers ────────────────────────────────────────────────────────────

def github_request(url: str) -> dict | list | None:
    """Make a GitHub API request with rate limiting and retries."""
    rate_limiter.wait()
    
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                rate_limiter.update_from_headers(resp.headers)
                data = json.loads(resp.read().decode())
                
                # Check pagination
                link_header = resp.headers.get("Link", "")
                next_url = None
                if 'rel="next"' in link_header:
                    for part in link_header.split(","):
                        if 'rel="next"' in part:
                            next_url = part.split(";")[0].strip().strip("<>")
                            break
                
                return {"data": data, "next_url": next_url}
        
        except urllib.error.HTTPError as e:
            if e.code == 403 and rate_limiter.remaining == 0:
                # Rate limited
                rate_limiter.update_from_headers(e.headers)
                wait_time = max(rate_limiter.reset_time - time.time(), 0) + 10
                print(f"  Rate limited. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                continue
            elif e.code == 404:
                return None
            elif e.code >= 500:
                print(f"  Server error {e.code} on {url}, retry {attempt+1}/{MAX_RETRIES}")
                time.sleep(5 * (attempt + 1))
                continue
            else:
                print(f"  HTTP {e.code} on {url}: {e.reason}")
                return None
        
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  Network error on {url}: {e}, retry {attempt+1}/{MAX_RETRIES}")
            time.sleep(5 * (attempt + 1))
            continue
    
    print(f"  Failed after {MAX_RETRIES} retries: {url}")
    return None


def github_search(query: str, page: int = 1, per_page: int = 100) -> dict | None:
    """Search GitHub repositories."""
    url = f"{BASE_URL}/search/repositories?q={urllib.parse.quote(query)}&page={page}&per_page={per_page}"
    return github_request(url)


def github_org_repos(org: str, page: int = 1, per_page: int = 100) -> dict | None:
    """Get repositories for an organization."""
    url = f"{BASE_URL}/orgs/{urllib.parse.quote(org)}/repos?page={page}&per_page={per_page}"
    return github_request(url)


def github_repo(owner: str, repo: str) -> dict | None:
    """Get a single repository."""
    url = f"{BASE_URL}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}"
    return github_request(url)


# ── Candidate processing ────────────────────────────────────────────────────

def make_candidate(item: dict, source: str) -> dict:
    """Convert a GitHub API item to a candidate record."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": item.get("full_name", ""),
        "name": item.get("name", ""),
        "owner": item.get("owner", {}).get("login", ""),
        "repository": item.get("full_name", ""),
        "repository_url": item.get("html_url", ""),
        "homepage_url": item.get("homepage"),
        "description": item.get("description"),
        "primary_category": None,
        "secondary_categories": [],
        "project_type": None,
        "topics": item.get("topics", []),
        "license": item.get("license", {}).get("spdx_id") if item.get("license") else None,
        "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0),
        "open_issues": item.get("open_issues_count", 0),
        "language": item.get("language"),
        "languages": [item.get("language")] if item.get("language") else [],
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "pushed_at": item.get("pushed_at"),
        "archived": item.get("archived", False),
        "is_fork": item.get("fork", False),
        "discovered_from": [source],
        "checked_at": now,
    }


def save_candidate(candidate: dict, filepath: str):
    """Append a candidate to the NDJSON file."""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(candidate, ensure_ascii=False) + "\n")


def load_existing_ids(filepath: str) -> set:
    """Load existing candidate IDs to avoid duplicates."""
    if not os.path.exists(filepath):
        return set()
    ids = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    ids.add(obj.get("id"))
                except json.JSONDecodeError:
                    continue
    return ids


# ── Core collectors ─────────────────────────────────────────────────────────

def collect_search_queries(candidates_file: str, queries: list[str], source_prefix: str):
    """Collect candidates from a list of GitHub search queries."""
    existing_ids = load_existing_ids(candidates_file)
    total_new = 0
    
    for query in queries:
        print(f"  Searching: {query}")
        page = 1
        page_results = 0
        
        while page <= 10:  # Max 10 pages per query
            result = github_search(query, page=page)
            if result is None:
                break
            
            items = result["data"].get("items", [])
            if not items:
                break
            
            for item in items:
                repo_id = item.get("full_name", "")
                full_name = item.get("full_name", "")
                if not full_name:
                    continue
                    
                # Skip existing
                if repo_id in existing_ids:
                    continue
                
                # Skip obviously irrelevant
                desc = (item.get("description") or "").lower()
                name = (item.get("name") or "").lower()
                
                candidate = make_candidate(item, f"{source_prefix}: {query}")
                save_candidate(candidate, candidates_file)
                existing_ids.add(repo_id)
                total_new += 1
                page_results += 1
            
            # Check for next page
            if result.get("next_url"):
                page += 1
            else:
                break
            
            # Rate limit check
            rate_limiter.check_limit()
        
        print(f"    Found {page_results} new candidates (page 1-{page})")
    
    return total_new


def collect_org_repos(candidates_file: str, orgs: list[str]):
    """Collect all public repos from specified GitHub organizations."""
    existing_ids = load_existing_ids(candidates_file)
    total_new = 0
    
    for org in orgs:
        print(f"  Organization: {org}")
        page = 1
        org_results = 0
        
        while page <= 5:  # Max 5 pages per org
            result = github_org_repos(org, page=page)
            if result is None:
                break
            
            items = result["data"]
            if not items:
                break
            
            for item in items:
                repo_id = item.get("full_name", "")
                if not repo_id:
                    continue
                
                if repo_id in existing_ids:
                    continue
                
                candidate = make_candidate(item, f"org: {org}")
                save_candidate(candidate, candidates_file)
                existing_ids.add(repo_id)
                total_new += 1
                org_results += 1
            
            if result.get("next_url"):
                page += 1
            else:
                break
            
            rate_limiter.check_limit()
        
        print(f"    Found {org_results} new repos from {org}")
    
    return total_new


def collect_known_repos(candidates_file: str):
    """Collect well-known repos that should definitely be in the catalog."""
    known_repos = [
        # MCP Ecosystem
        ("modelcontextprotocol", "specification"),
        ("modelcontextprotocol", "python-sdk"),
        ("modelcontextprotocol", "typescript-sdk"),
        ("modelcontextprotocol", "java-sdk"),
        ("modelcontextprotocol", "kotlin-sdk"),
        ("modelcontextprotocol", "servers"),
        ("modelcontextprotocol", "registry"),
        ("modelcontextprotocol", "inspector"),
        
        # Agent Frameworks
        ("anthropics", "claude-code"),
        ("openai", "openai-agents-python"),
        ("openai", "openai-agents-node"),
        ("langchain-ai", "langchain"),
        ("langchain-ai", "langgraph"),
        ("langchain-ai", "langsmith"),
        ("crewAI", "crewai"),
        ("microsoft", "autogen"),
        ("microsoft", "semantic-kernel"),
        ("microsoft", "TaskWeaver"),
        ("microsoft", "TinyTroupe"),
        
        # Coding Agents
        ("features", "coder"),
        ("Aider-AI", "aider"),
        ("OpenInterpreter", "open-interpreter"),
        ("plandex-ai", "plandex"),
        ("princeton-nlp", "SWE-agent"),
        ("sweepai", "sweep"),
        ("paul-gauthier", "aider"),
        
        # Memory & Context
        ("mem0ai", "mem0"),
        ("letta-ai", "letta"),
        ("run-llama", "llama_index"),
        ("hwchase17", "chroma"),
        ("weaviate", "weaviate"),
        ("qdrant", "qdrant"),
        
        # Browser Agents
        ("browser-use", "browser-use"),
        ("nicepkg", "nicepkg"),
        
        # Evaluation
        ("confident-ai", "deepeval"),
        ("explodinggradients", "ragas"),
        ("hamelsmu", "SEAL"),
        
        # Security
        ("guardrails-ai", "guardrails"),
        ("pytorch", "executorch"),
        
        # Operations
        ("langfuse", "langfuse"),
        ("helicone", "helicone"),
        ("log10-io", "log10"),
        
        # Infrastructure
        ("ollama", "ollama"),
        ("lm-sys", "FastChat"),
        ("vllm-project", "vllm"),
        ("khoj-ai", "khoj"),
        
        # Applications
        ("go-skynet", "go-skynet"),
        ("n8n-io", "n8n"),
        ("FlowiseAI", "Flowise"),
        ("getzep", "zep"),
        
        # Tool Calling
        ("composiohq", "composio"),
        ("agno-agi", "Agno"),
        
        # Multi-Agent
        ("i-am-bee", "bee-agent-framework"),
        ("microsoft", "gpt-orchestrator"),
        ("joaomdmoura", "crewAI"),
        
        # Deployment
        ("dstackai", "dstack"),
        ("modal-com", "modal"),
        ("bentoml", "BentoML"),
        
        # Knowledge & Retrieval
        ("run-llama", "llama_index"),
        ("gchurch", "letta"),
        ("embedchain", "embedchain"),
        
        # Tutorials
        ("codecrafters-io", "build-your-own-x"),
        
        # Identity (recent)
        ("stainless-api", "stainless"),
        ("anthropics", "anthropic-cookbook"),
    ]
    
    existing_ids = load_existing_ids(candidates_file)
    total_new = 0
    
    for owner, repo in known_repos:
        repo_id = f"{owner}/{repo}"
        if repo_id in existing_ids:
            continue
        
        print(f"  Fetching: {repo_id}")
        result = github_repo(owner, repo)
        if result is None:
            print(f"    Not found: {repo_id}")
            continue
        
        item = result["data"]
        candidate = make_candidate(item, "known-repo-list")
        save_candidate(candidate, candidates_file)
        existing_ids.add(repo_id)
        total_new += 1
        rate_limiter.check_limit()
    
    return total_new


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Collect candidates for the Agentic Engineering Compendium")
    parser.add_argument("--candidates-file", default="data/candidates.ndjson",
                       help="Path to candidates NDJSON file")
    parser.add_argument("--sources-file", default="data/sources.json",
                       help="Path to sources JSON file")
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.candidates_file) or ".", exist_ok=True)
    
    print("=" * 60)
    print("Agentic Engineering Compendium — Candidate Collection (LOOP 1)")
    print(f"Snapshot date: {SNAPSHOT_DATE}")
    print("=" * 60)
    
    # Load sources
    sources = {}
    if os.path.exists(args.sources_file):
        with open(args.sources_file, "r") as f:
            sources = json.load(f)
    
    total_candidates = 0
    
    # Step 1: Collect known important repos
    print("\n[Step 1] Collecting known important repositories...")
    new = collect_known_repos(args.candidates_file)
    total_candidates += new
    print(f"  Total from known repos: {new}")
    
    # Step 2: Collect organization repos
    print("\n[Step 2] Collecting organization repositories...")
    orgs = sources.get("tier_1_authoritative", {}).get("github_orgs", [])
    # Limit orgs for unauthenticated access
    orgs = orgs[:10]
    new = collect_org_repos(args.candidates_file, orgs)
    total_candidates += new
    print(f"  Total from org repos: {new}")
    
    # Step 3: Search queries (core queries only)
    print("\n[Step 3] Running search queries...")
    core_queries = [
        # Agent frameworks
        "ai-agent in:name,description,topics",
        "agent-framework in:name,description,topics",
        "topic:ai-agent",
        # MCP
        "topic:mcp-server",
        "topic:mcp-client",
        "model-context-protocol in:name,description",
        # Coding agents
        "topic:coding-agent",
        "coding-agent in:name,description",
        "swe-agent in:name,description",
        # Multi-agent
        "multi-agent in:name,description,topics",
        "topic:multi-agent",
        # Browser/computer use
        "topic:browser-agent",
        "browser-agent in:name,description",
        "topic:computer-use",
        "computer-use in:name,description",
        # Memory/RAG
        "topic:agent-memory",
        "agent-memory in:name,description",
        # Evaluation
        "topic:agent-evaluation",
        "agent-evaluation in:name,description",
        # Security/Guardrails
        "guardrails in:name,description,topics",
        "ai-sandbox in:name,description",
        # Observability
        "llm-tracing in:name,description",
        "agent-observability in:name,description",
        # Tools
        "topic:tool-calling",
        "tool-calling in:name,description",
        # Infrastructure
        "llm-gateway in:name,description",
        "inference-server in:name,description,topics",
        "topic:inference-server",
        # Agent protocols
        "topic:agent-protocol",
        "agent-protocol in:name,description",
    ]
    new = collect_search_queries(args.candidates_file, core_queries, "search-query")
    total_candidates += new
    print(f"  Total from search queries: {new}")
    
    # Summary
    with open(args.candidates_file, "r", encoding="utf-8") as f:
        final_count = sum(1 for _ in f)
    
    print("\n" + "=" * 60)
    print(f"Candidate collection complete!")
    print(f"  File: {args.candidates_file}")
    print(f"  Total candidates: {final_count}")
    print(f"  New candidates: {total_candidates}")
    print("=" * 60)


if __name__ == "__main__":
    main()
