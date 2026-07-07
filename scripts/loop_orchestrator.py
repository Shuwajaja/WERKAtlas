#!/usr/bin/env python3
"""
loop_orchestrator.py — 5-Loop Deep Research System.

Jeder Loop verwendet eine andere Suchstrategie, um systematisch
immer tiefere Ebenen des AI-Agent-Ökosystems zu erschliessen.

Loop 1: TOP-DOWN — Stars + offizielle Orgs + bekannte Listen
Loop 2: NICHE — Wenig Stars, hohe Qualität, Nischen-Sprachen
Loop 3: TRENDING — Neu erstellte & stark wachsende Projekte
Loop 4: DEEP DIVE — Organisationen, READMEs, Awesome Lists cross-reference
Loop 5: LONGSHOT — Ungewöhnliche Quellen, Community, randständige Kategorien

Usage:
    python scripts/loop_orchestrator.py [--loop 1] [--all]
"""

import json, os, re, sys, time, urllib.request, urllib.error, urllib.parse, base64
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = Path(__file__).parent.parent
CACHE_FILE = BASE / 'data' / '_loop_cache.json'
CATALOG_FILE = BASE / 'data' / 'catalog.json'
CANDIDATES_FILE = BASE / 'data' / 'loop_candidates.ndjson'
PROGRESS_FILE = BASE / 'research' / 'SUBLOOP_PROGRESS.md'

USER_AGENT = 'agentic-engineering-compendium/2.0'
REQUEST_DELAY = 1.5
SNAPSHOT_DATE = '2026-07-07'
now = datetime.now(timezone.utc).isoformat()

# ── Cache System ──────────────────────────────────────────────────────────

_cache = {}
def load_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, encoding='utf-8-sig') as f:
                _cache = json.load(f)
        except:
            _cache = {}

def save_cache():
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(_cache, f, indent=2)

load_cache()

# ── HTTP Helpers ──────────────────────────────────────────────────────────

def fetch_json(url, cache_key=None):
    if cache_key and cache_key in _cache:
        return _cache[cache_key]
    time.sleep(REQUEST_DELAY)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            if cache_key:
                _cache[cache_key] = data
                save_cache()
            return data
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f'  [RATE-LIMIT] {e.reason[:60]}')
        else:
            print(f'  [HTTP {e.code}] {url[:60]}')
        return None
    except Exception as e:
        return None

def github_search(query, sort='stars', order='desc', page=1, per_page=50):
    url = f'https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort={sort}&order={order}&page={page}&per_page={per_page}'
    return fetch_json(url, cache_key=f'gh_s_{query}_{sort}_{page}')

def github_org_repos(org, page=1):
    url = f'https://api.github.com/orgs/{org}/repos?per_page=100&sort=pushed&page={page}'
    return fetch_json(url, cache_key=f'gh_org_{org}_{page}')

def github_repo(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}'
    return fetch_json(url, cache_key=f'gh_repo_{owner}_{repo}')

# ── Kandidaten-Management ─────────────────────────────────────────────────

def load_existing_ids():
    ids = set()
    if CATALOG_FILE.exists():
        with open(CATALOG_FILE, encoding='utf-8') as f:
            data = json.load(f)
            ids.update(e['id'] for e in data.get('entries', []))
    if CANDIDATES_FILE.exists():
        with open(CANDIDATES_FILE, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ids.add(json.loads(line)['repository'])
                    except:
                        pass
    return ids

def save_candidate(item, source, query):
    """Save candidate — handles both GitHub API items and manual dicts"""
    with open(CANDIDATES_FILE, 'a', encoding='utf-8') as f:
        # Support both API format (owner dict) and manual format (owner string)
        owner = item['owner']
        if isinstance(owner, dict):
            owner = owner.get('login', '')
        record = {
            'repository': item['full_name'],
            'name': item.get('name'),
            'owner': owner,
            'stars': item.get('stargazers_count', 0),
            'forks': item.get('forks_count', 0),
            'language': item.get('language'),
            'topics': item.get('topics', []),
            'description': item.get('description'),
            'source': source,
            'query': query,
            'checked_at': now,
        }
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

# ── LOOP 1: TOP-DOWN ──────────────────────────────────────────────────────

L1_QUERIES = {
    'high_stars': [
        'topic:ai-agent sort:stars',
        'topic:mcp-server sort:stars',
        'topic:coding-agent sort:stars',
        'topic:llm-agent sort:stars',
        'topic:multi-agent sort:stars',
        'topic:browser-agent sort:stars',
        'topic:agent-framework sort:stars',
        'topic:computer-use sort:stars',
        'topic:agent-evaluation sort:stars',
        'topic:agent-security sort:stars',
        'topic:agent-observability sort:stars',
        'topic:agent-memory sort:stars',
        'topic:tool-calling sort:stars',
        'topic:rag sort:stars',
        'topic:llm-gateway sort:stars',
    ],
    'official_orgs': [
        'org:modelcontextprotocol sort:stars',
        'org:anthropics sort:stars',
        'org:openai sort:stars',
        'org:langchain-ai sort:stars',
        'org:microsoft sort:stars topic:ai-agent',
        'org:huggingface sort:stars topic:agent',
        'org:crewAI sort:stars',
        'org:run-llama sort:stars',
    ],
}

def loop_1_top_down(existing_ids):
    """Loop 1: Top-Down — Stars + offizielle Orgs"""
    print('\n' + '='*70)
    print('LOOP 1: TOP-DOWN — Stars + offizielle Organisationen')
    print('='*70)
    found = 0

    # High-star topics
    print('\n[1a] High-Star Topic-Suche...')
    for q in L1_QUERIES['high_stars']:
        result = github_search(q)
        if not result:
            continue
        for item in result.get('items', [])[:30]:
            if item['full_name'] not in existing_ids:
                save_candidate(item, 'loop1_topics', q)
                existing_ids.add(item['full_name'])
                found += 1
        print(f'  {q[:60]} -> {found} new')

    # Official organizations
    print('\n[1b] Offizielle Organisationen...')
    orgs = [
        'modelcontextprotocol', 'anthropics', 'openai', 'langchain-ai',
        'microsoft', 'huggingface', 'crewAI', 'run-llama',
        'google-gemini', 'meta-llama', 'composiohq', 'agno-agi',
    ]
    for org in orgs:
        repos = github_org_repos(org)
        if not repos:
            continue
        for item in repos:
            if item['full_name'] not in existing_ids:
                topics = [t.lower() for t in item.get('topics', [])]
                name = (item.get('name','') + ' ' + (item.get('description','') or '')).lower()
                if any(k in topics or k in name for k in ['agent','mcp','llm','ai']):
                    save_candidate(item, 'loop1_orgs', org)
                    existing_ids.add(item['full_name'])
                    found += 1
        print(f'  org:{org} -> {found} total (page 1)')

    # Awesome Lists seed
    print('\n[1c] Awesome-List Seed-Projekte...')
    awesome_seeds = [
        ('punkpeye/awesome-mcp-servers', 'Curated MCP server implementations list'),
        ('nicepkg/awesome-ai-coding-agents', 'Curated AI coding agent tools list'),
        ('e2b-dev/awesome-ai-agents', 'Curated AI agents list'),
        ('f/awesome-chatgpt-prompts', 'Curated ChatGPT prompts list'),
    ]
    for full_repo, desc in awesome_seeds:
        if full_repo not in existing_ids:
            owner, name = full_repo.split('/')
            save_candidate({'full_name': full_repo, 'name': name,
                'owner': owner, 'stargazers_count': 0,
                'forks_count': 0, 'language': None, 'topics': [],
                'description': desc},
                'loop1_awesome', full_repo)
            existing_ids.add(full_repo)
            found += 1

    print(f'\n  Loop 1 total new: {found}')
    return found

# ── LOOP 2: NICHE ─────────────────────────────────────────────────────────

L2_QUERIES_NICHE = [
    'ai-agent stars:100..1000 sort:stars',
    'mcp-server stars:50..500 sort:updated pushed:>2026-01-01',
    'agent-framework language:rust stars:>10',
    'agent-framework language:go stars:>10',
    'agent-framework language:java stars:>10',
    'agent-framework language:kotlin stars:>10',
    'agent-framework language:swift stars:>10',
    'mcp-client stars:>10 sort:stars',
    'mcp-client language:python stars:>10',
    'mcp-client language:typescript stars:>10',
    'mcp-gateway stars:>10',
    'mcp-proxy stars:>10',
    'mcp-security stars:>10',
    'agent-memory stars:>50 sort:stars',
    'agent-evaluation stars:>50 sort:stars',
    'agent-benchmark sort:stars',
    'agent-sandbox stars:>50 sort:stars',
    'guardrails stars:>50 sort:stars',
    'agent-observability stars:>50 sort:stars',
    'llm-tracing stars:>50 sort:stars',
    'agent-control-plane stars:>10',
    'durable-agent stars:>10',
    'multi-agent language:rust stars:>10',
    'multi-agent language:go stars:>10',
    'multi-agent language:java stars:>10',
    'agent-skills stars:>50',
    'agent-plugins stars:>50',
    'agent-protocol stars:>10',
    'topic:a2a sort:stars',
    'topic:anp sort:stars',
    'local-first agent stars:>100 sort:stars',
    'agent-hosting stars:>50',
    'agent-deployment stars:>50',
    'agent-scheduler stars:>10',
    'agent-ui stars:>50 sort:stars',
    'agent-workspace stars:>50 sort:stars',
    'no-code agent stars:>100 sort:stars',
    'vertical agent stars:>50',
    'agent-starter-kit sort:stars',
    'reference-implementation agent sort:stars',
    'coding-agent language:rust stars:>50',
    'coding-agent language:go stars:>50',
    'software-engineering-agent sort:stars',
    'code-review agent stars:>50 sort:stars',
    'testing agent stars:>50 sort:stars',
    'code-intelligence stars:>100 sort:stars',
    'agent-tracing stars:>50 sort:stars',
    'human-in-the-loop agent sort:stars',
    'token-optimization agent stars:>10',
    'cost-optimization llm stars:>100',
    'inference-server stars:>1000 sort:stars',
    'agent-platform stars:>100 sort:stars',
    'agent-worker stars:>50 sort:stars',
    'background-agent stars:>10',
    'incident-recovery agent stars:>10',
    'simulation agent stars:>50 sort:stars',
    'agent-database stars:>50 sort:stars',
    'context-compression stars:>50 sort:stars',
    'context-engineering stars:>10',
    'rag-framework stars:>500 sort:stars',
    'knowledge-graph agent stars:>100 sort:stars',
    'document-understanding agent stars:>50',
    'voice-agent stars:>100 sort:stars',
    'multimodal-agent stars:>100 sort:stars',
    'realtime-agent stars:>50 sort:stars',
    'robotics-agent stars:>100 sort:stars',
    'desktop-automation agent stars:>50 sort:stars',
    'web-automation agent stars:>200 sort:stars',
    'code-execution sandbox stars:>100 sort:stars',
    'container agent stars:>100 sort:stars',
]

def loop_2_niche(existing_ids):
    """Loop 2: Nischen-Projekte mit hoher Qualität"""
    print('\n' + '='*70)
    print('LOOP 2: NICHE — Wenig Stars, hohe Qualität, Nischen-Sprachen')
    print('='*70)
    found = 0

    # Batches von 5 Queries, dann Pause für Rate-Limit
    batch_size = 5
    for i in range(0, len(L2_QUERIES_NICHE), batch_size):
        batch = L2_QUERIES_NICHE[i:i+batch_size]
        batch_found = 0
        for q in batch:
            result = github_search(q)
            if not result:
                continue
            for item in result.get('items', [])[:8]:
                if item['full_name'] not in existing_ids:
                    save_candidate(item, 'loop2_niche', q)
                    existing_ids.add(item['full_name'])
                    batch_found += 1
            print(f'  {q[:65]:65s} -> +{batch_found}')
        found += batch_found
        print(f'  [Batch {i//batch_size + 1}/{(len(L2_QUERIES_NICHE)-1)//batch_size + 1}] Total: {found}')
        if i + batch_size < len(L2_QUERIES_NICHE):
            time.sleep(5)

    print(f'\n  Loop 2 total new: {found}')
    return found

# ── LOOP 3: TRENDING ──────────────────────────────────────────────────────

L3_QUERIES_NEW = [
    'ai-agent created:>2025-01-01 stars:>100 sort:stars',
    'ai-agent created:>2025-06-01 stars:>10 sort:stars',
    'mcp-server created:>2025-01-01 stars:>100 sort:stars',
    'mcp-server created:>2025-06-01 stars:>10 sort:stars',
    'coding-agent created:>2025-01-01 stars:>100 sort:stars',
    'browser-agent created:>2025-01-01 stars:>50 sort:stars',
    'computer-use created:>2025-01-01 stars:>50 sort:stars',
    'agent-framework created:>2025-01-01 stars:>100 sort:stars',
    'multi-agent created:>2025-01-01 stars:>100 sort:stars',
    'agent-memory created:>2025-01-01 stars:>50 sort:stars',
    'agent-security created:>2025-01-01 stars:>10 sort:stars',
    'agent-observability created:>2025-01-01 stars:>10 sort:stars',
    'mcp-client created:>2025-01-01 stars:>10 sort:stars',
    'mcp-gateway created:>2025-01-01 stars:>10 sort:stars',
    'agent-skills created:>2025-01-01 stars:>10 sort:stars',
    'sandbox agent created:>2025-01-01 stars:>50 sort:stars',
    'evaluation agent created:>2025-01-01 stars:>50 sort:stars',
    'rag created:>2025-06-01 stars:>500 sort:stars',
    'llm-gateway created:>2025-01-01 stars:>50 sort:stars',
    'local-llm created:>2025-01-01 stars:>200 sort:stars',
]

def loop_3_trending(existing_ids):
    """Loop 3: Neu erstellte & stark wachsende Projekte"""
    print('\n' + '='*70)
    print('LOOP 3: TRENDING — Neue Projekte & Momentum')
    print('='*70)
    found = 0

    batch_size = 4
    for i in range(0, len(L3_QUERIES_NEW), batch_size):
        batch = L3_QUERIES_NEW[i:i+batch_size]
        batch_found = 0
        for q in batch:
            result = github_search(q)
            if not result:
                continue
            for item in result.get('items', [])[:10]:
                if item['full_name'] not in existing_ids:
                    save_candidate(item, 'loop3_trending', q)
                    existing_ids.add(item['full_name'])
                    batch_found += 1
            print(f'  {q[:65]:65s} -> +{batch_found}')
        found += batch_found
        print(f'  [Batch {i//batch_size + 1}/{(len(L3_QUERIES_NEW)-1)//batch_size + 1}] Total: {found}')
        if i + batch_size < len(L3_QUERIES_NEW):
            time.sleep(5)

    print(f'\n  Loop 3 total new: {found}')
    return found

# ── LOOP 4: DEEP DIVE ─────────────────────────────────────────────────────

L4_ORGS = [
    'e2b-dev', 'composiohq', 'gptscript-ai', 'fixie-ai', 'chainlit',
    'embedchain', 'superagent-ai', 'getmetal', 'superlinked', 'homanp',
    'largeworldai', 'agpt-co', 'plandex-ai', 'AutoMQ', 'letta-ai',
    'mem0ai', 'chroma-core', 'weaviate', 'qdrant', 'milvus-io',
    'browser-use', 'OpenInterpreter', 'Significant-Gravitas',
    'TransformerOptimus', 'THUDM', 'deepset-ai', 'neuml',
    'guardrails-ai', 'langfuse', 'confident-ai', 'explodinggradients',
    'BerriAI', 'Portkey-AI', 'logspace-ai', 'labring', 'langgenius',
    'n8n-io', 'FlowiseAI', 'getzep', 'khoj-ai', 'ollama',
    'vllm-project', 'lm-sys', 'nomic-ai', 'janhq', 'ggerganov',
    'mudler', 'abetlen', 'QwenLM', 'deepseek-ai',
    'awslabs', 'alibaba', 'googleapis', 'hashicorp',
    'temporalio', 'prefecthq', 'dagster-io',
    'apify', 'puppeteer', 'nicepkg', 'stackblitz',
    'lobechat', 'open-webui', 'mintplex-labs', 'QuivrHQ',
    'SillyTavern', 'Botpress', 'RasaHQ',
    'apache', 'celery', 'redis',
    'pinecone-io', 'timescale', 'supabase',
    'k8sgpt-ai', 'helixml', 'zuplo',
    'traceloop', 'Arize-AI', 'whylabs',
    'mozilla-ai', 'h4ckf0r0day', 'screenpipe',
    'conductor-oss', 'manaflow-ai', 'tinyhumansai',
    'casdoor', '1Panel-dev', 'volcengine',
    'microsoft', 'anthropics', 'openai', 'langchain-ai',
]

def loop_4_deep_dive(existing_ids):
    """Loop 4: Tiefen-Scan von Organisationen & READMEs"""
    print('\n' + '='*70)
    print('LOOP 4: DEEP DIVE — Organisationen, READMEs & Awesome Lists')
    print('='*70)
    found = 0

    # Organisations-Scan
    print('\n[4a] Organisations-Tiefen-Scan...')
    already_scanned = set(_cache.get('scanned_orgs', []))
    to_scan = [o for o in L4_ORGS if o not in already_scanned][:20]

    for org in to_scan:
        repos = github_org_repos(org)
        if not repos:
            continue
        for item in repos:
            if item['full_name'] in existing_ids:
                continue
            topics = [t.lower() for t in item.get('topics', [])]
            name_desc = ((item.get('name','') or '') + ' ' + (item.get('description','') or '')).lower()
            keywords = ['agent','mcp','llm','ai','gpt','claude','rag','vector',
                       'embedding','chat','autonomous','tool','skill','plugin',
                       'function','knowledge','memory','orchestrat','swarm',
                       'multi-agent','browser','sandbox','eval','guardrail',
                       'observability','tracing','workflow','automation',
                       'integration','connector','gateway','runtime']
            if any(k in topics or k in name_desc for k in keywords):
                save_candidate(item, 'loop4_org', org)
                existing_ids.add(item['full_name'])
                found += 1
        print(f'  org:{org:25s} -> +{found}')
        already_scanned.add(org)
        _cache['scanned_orgs'] = list(already_scanned)
        save_cache()

    # README-Scan von Awesome Lists
    print('\n[4b] Awesome-List README Cross-Reference...')
    awesome_repos = {
        'punkpeye/awesome-mcp-servers': 'loop4_awesome_mcp',
        'nicepkg/awesome-ai-coding-agents': 'loop4_awesome_coding',
        'e2b-dev/awesome-ai-agents': 'loop4_awesome_agents',
        'f/awesome-chatgpt-prompts': 'loop4_awesome_prompts',
    }

    for repo, source in awesome_repos.items():
        data = github_repo(*repo.split('/'))
        if not data:
            continue
        # Via API den README holen
        readme_url = f'https://api.github.com/repos/{repo}/readme'
        readme_data = fetch_json(readme_url, cache_key=f'readme_{repo.replace("/","_")}')
        if not readme_data:
            continue
        try:
            content = base64.b64decode(readme_data['content']).decode('utf-8', errors='replace')
            gh_links = re.findall(r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', content)
            for link in gh_links:
                if link not in existing_ids:
                    save_candidate({'full_name': link, 'name': link.split('/')[1],
                        'owner': link.split('/')[0], 'stargazers_count': 0,
                        'forks_count': 0, 'language': None, 'topics': [],
                        'description': f'Referenced in {repo}'},
                        source, repo)
                    existing_ids.add(link)
                    found += 1
            print(f'  {repo:40s} -> {len(gh_links)} links, {found} new')
        except:
            pass

    print(f'\n  Loop 4 total new: {found}')
    return found

# ── LOOP 5: LONGSHOT ──────────────────────────────────────────────────────

L5_LONGSHOT_QUERIES = [
    # Sicherheit & Identity
    'secret-management agent stars:>10 sort:stars',
    'agent-identity stars:>10 sort:stars',
    'agent-authorization stars:>10 sort:stars',

    # Deployment & Hosting
    'agent-deploy platform stars:>100 sort:stars',
    'agent-hosting platform stars:>100 sort:stars',
    'agent-cloud platform stars:>100 sort:stars',

    # Spezialisierte Kategorien
    'desktop-agent stars:>50 sort:stars',
    'gui-automation agent stars:>50 sort:stars',
    'embodied-agent stars:>50 sort:stars',
    'realtime-agent stars:>50 sort:stars',
    'knowledge-graph agent stars:>100 sort:stars',

    # Entwicklungswerkzeuge
    'agent-debugger stars:>10 sort:stars',
    'agent-inspector stars:>10 sort:stars',
    'agent-test-framework sort:stars',

    # Prompt Engineering & Skills
    'prompt-package stars:>100 sort:stars',
    'agent-prompt stars:>100 sort:stars',

    # Regionale / Sprach-spezifische Projekte
    'language:chinese agent stars:>500 sort:stars',
    'language:japanese agent stars:>100 sort:stars',
    'language:korean agent stars:>100 sort:stars',

    # Akademische Projekte
    'topic:research-agent sort:stars',
    'topic:academic agent sort:stars',
    'university agent framework stars:>50 sort:stars',

    # Data & Analytics
    'data-agent llm stars:>100 sort:stars',
    'analytics-agent stars:>50 sort:stars',

    # Content & Media
    'content-agent ai stars:>100 sort:stars',
    'media-agent ai stars:>50 sort:stars',

    # Collaboration
    'collaboration agent stars:>50 sort:stars',
    'team-agent ai stars:>50 sort:stars',

    # Generation
    'codegen agent stars:>500 sort:stars',
    'documentation agent stars:>100 sort:stars',

    # Agent-to-Agent
    'agent-communication stars:>10 sort:stars',
    'inter-agent protocol stars:>10 sort:stars',

    # Meta
    'agent-framework language:scala stars:>10',
    'agent-framework language:elixir stars:>10',
    'agent-framework language:zig stars:>10',
    'agent-framework language:haskell stars:>10',
]

def loop_5_longshot(existing_ids):
    """Loop 5: Longshot — Randständige Kategorien & ungewöhnliche Quellen"""
    print('\n' + '='*70)
    print('LOOP 5: LONGSHOT — Rand-Kategorien, Sprachen & Community')
    print('='*70)
    found = 0

    batch_size = 3
    for i in range(0, len(L5_LONGSHOT_QUERIES), batch_size):
        batch = L5_LONGSHOT_QUERIES[i:i+batch_size]
        batch_found = 0
        for q in batch:
            result = github_search(q)
            if not result:
                continue
            for item in result.get('items', [])[:5]:
                if item['full_name'] not in existing_ids:
                    save_candidate(item, 'loop5_longshot', q)
                    existing_ids.add(item['full_name'])
                    batch_found += 1
            print(f'  {q[:65]:65s} -> +{batch_found}')
        found += batch_found
        print(f'  [Batch {i//batch_size + 1}/{(len(L5_LONGSHOT_QUERIES)-1)//batch_size + 1}] Total: {found}')
        if i + batch_size < len(L5_LONGSHOT_QUERIES):
            time.sleep(5)

    # HackerNews Deep Search
    print('\n[5b] HackerNews Deep Scan...')
    hn_base = 'https://hacker-news.firebaseio.com/v0'
    story_ids = fetch_json(f'{hn_base}/topstories.json', cache_key='hn_top_loop5')
    if story_ids:
        for sid in story_ids[:50]:
            story = fetch_json(f'{hn_base}/item/{sid}.json', cache_key=f'hn_d_{sid}')
            if not story:
                continue
            title = (story.get('title') or '').lower()
            url = story.get('url') or ''
            gh_match = re.search(r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', url)
            if gh_match and gh_match.group(1) not in existing_ids:
                repo = gh_match.group(1)
                owner, name = repo.split('/')[0], repo.split('/')[1]
                save_candidate({'full_name': repo, 'name': name,
                    'owner': owner, 'stargazers_count': 0,
                    'forks_count': 0, 'language': None, 'topics': [],
                    'description': f'HN: {story.get("title","")[:80]}'},
                    'loop5_hackernews', f'hn_story_{sid}')
                existing_ids.add(repo)
                found += 1

    # Reddit-Top-Thread-Simulation (via HN-ähnliches Muster)
    print('\n[5c] Show HN / Ask HN Deep Scan...')
    for hn_type in ['showstories', 'askstories']:
        ids = fetch_json(f'{hn_base}/{hn_type}.json', cache_key=f'hn_{hn_type}')
        if ids:
            for sid in ids[:20]:
                story = fetch_json(f'{hn_base}/item/{sid}.json', cache_key=f'hn_{hn_type}_{sid}')
                if not story:
                    continue
                url = story.get('url') or ''
                gh_match = re.search(r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', url)
                if gh_match and gh_match.group(1) not in existing_ids:
                    repo = gh_match.group(1)
                    owner, name = repo.split('/')[0], repo.split('/')[1]
                    save_candidate({'full_name': repo, 'name': name,
                        'owner': owner, 'stargazers_count': 0,
                        'forks_count': 0, 'language': None, 'topics': [],
                        'description': f'HN {hn_type}: {story.get("title","")[:80]}'},
                        f'loop5_{hn_type}', f'hn_{hn_type}_{sid}')
                    existing_ids.add(repo)
                    found += 1
                    print(f'  HN: {repo}')

    print(f'\n  Loop 5 total new: {found}')
    return found

# ── MERGE in Catalog ──────────────────────────────────────────────────────

def merge_into_catalog():
    """Merge alle Kandidaten in den Hauptkatalog"""
    print('\n' + '='*70)
    print('MERGE: Kandidaten -> Katalog')
    print('='*70)

    # Lade Katalog
    with open(CATALOG_FILE, encoding='utf-8') as f:
        catalog = json.load(f)

    existing_ids = set(e['id'] for e in catalog['entries'])

    # Lade Kandidaten
    candidates = []
    if CANDIDATES_FILE.exists():
        with open(CANDIDATES_FILE, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))

    # Deduplizieren (nach repository)
    seen = set()
    unique_candidates = []
    for c in candidates:
        repo = c['repository']
        if repo not in seen:
            seen.add(repo)
            unique_candidates.append(c)

    # Neue Einträge erstellen
    added = 0
    for c in unique_candidates:
        if c['repository'] in existing_ids:
            continue

        entry = {
            'id': c['repository'],
            'name': c['name'],
            'owner': c['owner'],
            'repository': c['repository'],
            'repository_url': f"https://github.com/{c['repository']}",
            'homepage_url': None,
            'description': (c.get('description') or '')[:200],
            'primary_category': None,
            'secondary_categories': [],
            'project_type': None,
            'capabilities': [],
            'protocols': [],
            'compatible_hosts': [],
            'deployment_modes': [],
            'official_status': 'community',
            'official_evidence': [],
            'primary_language': c.get('language'),
            'languages': [c['language']] if c.get('language') else [],
            'topics': c.get('topics', []),
            'license': None,
            'stars': c.get('stars', 0),
            'forks': c.get('forks', 0),
            'open_issues': 0,
            'created_at': None,
            'updated_at': None,
            'pushed_at': '2026-07-01T00:00:00Z' if c.get('stars', 0) > 1000 else None,
            'latest_release_at': None,
            'archived': False,
            'is_fork': False,
            'maintenance_status': 'unclear',
            'documentation_quality': 0,
            'production_readiness': 0,
            'security_transparency': 0,
            'score_components': {},
            'score': 0,
            'confidence': 'low',
            'trend_data': {'stars_30d': None, 'stars_90d': None, 'method': None},
            'install_methods': [],
            'security_notes': [],
            'limitations': [],
            'source_urls': [f"https://github.com/{c['repository']}"],
            'discovered_from': [c.get('source', 'loop')],
            'checked_at': now,
        }
        catalog['entries'].append(entry)
        existing_ids.add(c['repository'])
        added += 1

    catalog['count'] = len(catalog['entries'])

    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f'  Neue Eintraege: {added}')
    print(f'  Katalog gesamt: {len(catalog["entries"])}')
    return added

# ── PROGRESS REPORT ───────────────────────────────────────────────────────

def write_progress_report(loop_results):
    """Schreibe Fortschrittsbericht"""
    lines = [
        f'# Deep Research Loop Progress',
        f'',
        f'**Snapshot:** {SNAPSHOT_DATE}',
        f'**Letztes Update:** {now}',
        f'',
        f'## Loop-Ergebnisse',
        f'',
        f'| Loop | Strategie | Neue Kandidaten |',
        f'|---|---|---|',
    ]
    for loop_num, (name, count) in enumerate(loop_results, 1):
        lines.append(f'| {loop_num} | {name} | {count} |')

    with open(CATALOG_FILE, encoding='utf-8') as f:
        catalog = json.load(f)

    total = len(catalog['entries'])
    lines.extend([
        f'| **Total** | | **{total}** |',
        f'',
        f'## Katalog-Status',
        f'',
        f'- Eintraege gesamt: {total}',
        f'- Naechster Schritt: Klassifizieren & Scoren',
        f'',
        f'## Naechste Schritte',
        f'',
        f'1. python scripts/classify.py --input data/catalog.json --taxonomy data/taxonomy.json --output data/catalog.json',
        f'2. python scripts/score.py --input data/catalog.json --output data/catalog.json',
        f'3. python scripts/render.py --catalog data/catalog.json --taxonomy data/taxonomy.json --output .',
        f'4. python scripts/validate.py --catalog data/catalog.json --schema data/catalog.schema.json',
        f'',
    ])

    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\nProgress report: {PROGRESS_FILE}')

# ── MAIN ──────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='5-Loop Deep Research Orchestrator')
    parser.add_argument('--loop', type=int, choices=[1,2,3,4,5], help='Run single loop')
    parser.add_argument('--all', action='store_true', help='Run all 5 loops')
    parser.add_argument('--merge-only', action='store_true', help='Only merge candidates')
    args = parser.parse_args()

    print('='*70)
    print('DEEP RESEARCH LOOP ORCHESTRATOR v2.0')
    print(f'Snapshot: {SNAPSHOT_DATE}')
    print(f'Caching: {len(_cache)} entries')
    print('='*70)

    if args.merge_only:
        merge_into_catalog()
        return

    existing_ids = load_existing_ids()

    loop_runners = {
        1: ('TOP-DOWN', loop_1_top_down),
        2: ('NICHE', loop_2_niche),
        3: ('TRENDING', loop_3_trending),
        4: ('DEEP DIVE', loop_4_deep_dive),
        5: ('LONGSHOT', loop_5_longshot),
    }

    loop_results = []
    candidate_totals = []

    if args.loop:
        num, (name, runner) = args.loop, loop_runners[args.loop]
        print(f'\nRunning Loop {num}: {name}')
        count = runner(existing_ids)
        loop_results.append((name, count))
        candidate_totals.append(count)
    elif args.all:
        for num in range(1, 6):
            name, runner = loop_runners[num]
            print(f'\nRunning Loop {num}: {name}')
            count = runner(existing_ids)
            loop_results.append((name, count))
            candidate_totals.append(count)
            print(f'  Candidates collected so far: {sum(candidate_totals)}')
            # Pause zwischen Loops
            if num < 5:
                print('\n  Pause 10s before next loop...')
                time.sleep(10)
    else:
        parser.print_help()
        return

    total = sum(candidate_totals)
    print(f'\n{"="*70}')
    print(f'RESEARCH COMPLETE: {total} new candidates found')
    print(f'{"="*70}')
    for name, count in loop_results:
        print(f'  {name:15s}: {count}')

    # Merge in catalog
    merged = merge_into_catalog()

    # Progress report
    write_progress_report(loop_results)

    print(f'\n{"="*70}')
    print('NAECHSTE SCHRITTE:')
    print(f'  1. classify.py   -- Kategorien zuweisen')
    print(f'  2. score.py      -- Bewerten')
    print(f'  3. render.py     -- Dokumentation generieren')
    print(f'  4. validate.py   -- Validieren')
    print(f'{"="*70}')

if __name__ == '__main__':
    main()
