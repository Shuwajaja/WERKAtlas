#!/usr/bin/env python3
"""
seed_catalog.py — Create an initial seed catalog from known projects.

This bypasses API rate limits by building entries from our knowledge base,
then verifying them with minimal API calls.

Usage:
    python scripts/seed_catalog.py [--output data/catalog.json]
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


SNAPSHOT_DATE = "2026-07-07"
USER_AGENT = "agentic-engineering-compendium/1.0"


def verify_repo(owner: str, repo: str) -> dict | None:
    """Verify a repo exists and fetch its metadata."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def make_entry(owner: str, repo: str, category: str, ptype: str, description: str,
               secondary: list = None, protocols: list = None, 
               deployment: list = None, capabilities: list = None,
               security_notes: list = None) -> dict:
    """Create a catalog entry structure."""
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": f"{owner}/{repo}",
        "name": repo,
        "owner": owner,
        "repository": f"{owner}/{repo}",
        "repository_url": f"https://github.com/{owner}/{repo}",
        "homepage_url": None,
        "description": description,
        "primary_category": category,
        "secondary_categories": secondary or [],
        "project_type": ptype,
        "capabilities": capabilities or [],
        "protocols": protocols or [],
        "compatible_hosts": [],
        "deployment_modes": deployment or [],
        "official_status": "official" if owner in (
            "modelcontextprotocol", "anthropics", "openai", "microsoft",
            "langchain-ai", "crewAI", "huggingface"
        ) else "community",
        "official_evidence": [f"https://github.com/{owner}/{repo}"],
        "primary_language": None,
        "languages": [],
        "topics": [],
        "license": None,
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "created_at": None,
        "updated_at": None,
        "pushed_at": None,
        "latest_release_at": None,
        "archived": False,
        "is_fork": False,
        "maintenance_status": "active",
        "documentation_quality": 0,
        "production_readiness": 0,
        "security_transparency": 0,
        "score_components": {
            "relevance": 0, "maintenance": 0, "adoption": 0, "momentum": 0,
            "documentation": 0, "production_readiness": 0, "security": 0,
            "interoperability": 0, "community": 0, "uniqueness": 0
        },
        "score": 0,
        "confidence": "low",
        "trend_data": {"stars_30d": None, "stars_90d": None, "method": None},
        "install_methods": [],
        "security_notes": security_notes or [],
        "limitations": [],
        "source_urls": [f"https://github.com/{owner}/{repo}"],
        "discovered_from": ["seed-catalog"],
        "checked_at": now,
    }
    return entry


def build_seed_catalog() -> list:
    """Build the complete seed catalog from known projects."""
    entries = []
    
    # ── A. Learning & Foundations ──
    entries.append(make_entry(
        "codecrafters-io", "build-your-own-x",
        "A.1", "collection",
        "Curated list of implementation tutorials for building diverse technologies from scratch."
    ))
    entries.append(make_entry(
        "anthropics", "anthropic-cookbook",
        "A.3", "collection",
        "Collection of recipes and patterns for building with the Claude API and agents."
    ))
    entries.append(make_entry(
        "openai", "openai-cookbook",
        "A.3", "collection",
        "Examples and guides for using the OpenAI API across various applications."
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "specification",
        "A.4", "protocol",
        "Official specification defining the Model Context Protocol for tool and resource integration."
    ))
    
    # ── B. Frameworks & Runtimes ──
    entries.append(make_entry(
        "langchain-ai", "langchain",
        "B.6", "framework",
        "Framework for building context-aware reasoning applications with LLMs and tool integration.",
        secondary=["E.35"], protocols=["MCP"], deployment=["self-hosted", "cloud"],
        capabilities=["rag", "tool-use", "chains", "agents"]
    ))
    entries.append(make_entry(
        "langchain-ai", "langgraph",
        "B.8", "framework",
        "Framework for building stateful, multi-actor agent workflows with graph-based orchestration.",
        secondary=["B.6", "B.12"], deployment=["self-hosted", "cloud"],
        capabilities=["graph-orchestration", "state-management"]
    ))
    entries.append(make_entry(
        "microsoft", "autogen",
        "B.6", "framework",
        "Multi-agent conversation framework enabling cooperative LLM agent interactions and task execution.",
        secondary=["B.9"], capabilities=["multi-agent", "conversation"]
    ))
    entries.append(make_entry(
        "microsoft", "semantic-kernel",
        "B.6", "SDK",
        "SDK for integrating AI models into applications with plugins, planners, and memory.",
        secondary=["E.30", "F.37"], protocols=["MCP"], capabilities=["plugins", "planning", "memory"]
    ))
    entries.append(make_entry(
        "crewAI", "crewai",
        "B.9", "framework",
        "Multi-agent orchestration framework for assembling and coordinating role-based AI agent teams.",
        secondary=["B.6"], capabilities=["multi-agent", "role-based", "task-delegation"]
    ))
    entries.append(make_entry(
        "i-am-bee", "bee-agent-framework",
        "B.6", "framework",
        "Framework for building production-ready agent systems with modular tools and memory.",
        secondary=["F.37"], capabilities=["modular", "memory", "tools"]
    ))
    entries.append(make_entry(
        "run-llama", "llama_index",
        "B.6", "framework",
        "Data framework for building LLM applications with indexing, retrieval, and agent capabilities.",
        secondary=["F.38", "F.37"], capabilities=["rag", "indexing", "agents"]
    ))
    entries.append(make_entry(
        "openai", "openai-agents-python",
        "B.6", "SDK",
        "OpenAI's official Python SDK for building agent-based applications with tool use.",
        capabilities=["agent", "tool-use", "multi-agent"]
    ))
    entries.append(make_entry(
        "openai", "openai-agents-node",
        "B.6", "SDK",
        "OpenAI's official Node.js SDK for building agent-based applications with tool use.",
        capabilities=["agent", "tool-use", "multi-agent"]
    ))
    entries.append(make_entry(
        "agno-agi", "agno",
        "B.6", "framework",
        "Framework for building multi-modal agents with memory, knowledge, and tool integration.",
        secondary=["F.37", "E.35"], capabilities=["multi-modal", "memory", "tools"]
    ))
    
    # ── C. Coding & Software Engineering Agents ──
    entries.append(make_entry(
        "anthropics", "claude-code",
        "C.14", "CLI tool",
        "Terminal-native AI agent for software development that reads, writes, and executes code interactively.",
        capabilities=["code-generation", "terminal", "file-ops"]
    ))
    entries.append(make_entry(
        "Aider-AI", "aider",
        "C.13", "CLI tool",
        "AI pair programming assistant that edits code in local git repositories through natural language.",
        capabilities=["code-editing", "git-integration"]
    ))
    entries.append(make_entry(
        "OpenInterpreter", "open-interpreter",
        "C.14", "application",
        "Natural language interface for computers that translates instructions into executable code.",
        secondary=["G.45"], capabilities=["code-execution", "computer-use"]
    ))
    entries.append(make_entry(
        "princeton-nlp", "SWE-agent",
        "C.13", "application",
        "Software engineering agent that can autonomously fix issues in real GitHub repositories.",
        capabilities=["bug-fixing", "github-integration"]
    ))
    entries.append(make_entry(
        "features", "coder",
        "C.15", "IDE extension",
        "AI coding assistant integrated directly into Visual Studio Code as an extension.",
        capabilities=["code-completion", "IDE-integration"]
    ))
    entries.append(make_entry(
        "sweepai", "sweep",
        "C.13", "application",
        "AI-powered junior developer that turns bug reports and feature requests into code changes.",
        capabilities=["code-generation", "pr-creation"]
    ))
    
    # ── D. MCP Ecosystem ──
    entries.append(make_entry(
        "modelcontextprotocol", "python-sdk",
        "D.22", "SDK",
        "Official Python SDK for building MCP servers and clients with async support.",
        protocols=["MCP"]
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "typescript-sdk",
        "D.22", "SDK",
        "Official TypeScript SDK for building MCP servers and clients.",
        protocols=["MCP"]
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "java-sdk",
        "D.22", "SDK",
        "Official Java SDK for building MCP servers and clients.",
        protocols=["MCP"]
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "kotlin-sdk",
        "D.22", "SDK",
        "Official Kotlin SDK for building MCP servers and clients.",
        protocols=["MCP"]
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "servers",
        "D.20", "collection",
        "Reference implementations of official MCP servers for filesystem, git, database, and web tools.",
        secondary=["A.4"], protocols=["MCP"], deployment=["self-hosted"],
        security_notes=["Filesystem, shell, and database access servers require careful permission management"]
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "registry",
        "D.23", "registry",
        "Official registry for discovering and publishing MCP server implementations.",
        protocols=["MCP"]
    ))
    entries.append(make_entry(
        "modelcontextprotocol", "inspector",
        "D.25", "developer tool",
        "Official developer tool for inspecting, testing, and debugging MCP server connections.",
        protocols=["MCP"]
    ))
    
    # ── F. Context, Knowledge, Memory ──
    entries.append(make_entry(
        "mem0ai", "mem0",
        "F.37", "library",
        "Memory layer for AI agents that learns from user interactions and maintains persistent context.",
        capabilities=["memory", "user-profile", "context"]
    ))
    entries.append(make_entry(
        "letta-ai", "letta",
        "F.37", "framework",
        "Framework for building agents with extended memory and persistent state across conversations.",
        secondary=["F.40"], capabilities=["memory", "state-management"]
    ))
    entries.append(make_entry(
        "chroma-core", "chroma",
        "F.38", "library",
        "Embedding database for AI applications with vector search and metadata filtering.",
        secondary=["F.43"], capabilities=["vector-search", "embeddings"]
    ))
    entries.append(make_entry(
        "weaviate", "weaviate",
        "F.38", "application",
        "Open-source vector database with hybrid search, graph filtering, and AI-native integrations.",
        secondary=["F.43"], capabilities=["vector-search", "hybrid-search"]
    ))
    entries.append(make_entry(
        "qdrant", "qdrant",
        "F.38", "application",
        "Vector similarity search engine with a focus on performance and extended filtering capabilities.",
        secondary=["F.43"], capabilities=["vector-search", "filtering"]
    ))
    entries.append(make_entry(
        "milvus-io", "milvus",
        "F.38", "application",
        "Cloud-native vector database for scalable similarity search and AI applications.",
        secondary=["F.43"], deployment=["self-hosted", "cloud"],
        capabilities=["vector-search", "scalable"]
    ))
    
    # ── G. Execution & Interaction ──
    entries.append(make_entry(
        "browser-use", "browser-use",
        "G.44", "library",
        "Library for building AI agents that can control web browsers to perform complex tasks.",
        capabilities=["browser-automation", "web-navigation"]
    ))
    entries.append(make_entry(
        "microsoft", "playwright",
        "G.47", "library",
        "Cross-browser automation framework for web testing and browser-based agent interactions.",
        secondary=["G.44"], capabilities=["browser-automation", "testing"]
    ))
    
    # ── H. Reliability & Operations ──
    entries.append(make_entry(
        "confident-ai", "deepeval",
        "H.55", "evaluation framework",
        "Evaluation framework for LLM applications with metrics, testing, and CI integration.",
        secondary=["H.62"], capabilities=["llm-evaluation", "testing", "ci-integration"]
    ))
    entries.append(make_entry(
        "explodinggradients", "ragas",
        "H.55", "evaluation framework",
        "Evaluation framework for Retrieval-Augmented Generation systems with actionable metrics.",
        secondary=["F.38"], capabilities=["rag-evaluation", "metrics"]
    ))
    entries.append(make_entry(
        "guardrails-ai", "guardrails",
        "H.57", "framework",
        "Framework for adding guardrails and validation to LLM applications for reliability and safety.",
        secondary=["H.58"], capabilities=["input-validation", "output-validation", "safety"]
    ))
    entries.append(make_entry(
        "langfuse", "langfuse",
        "H.53", "observability platform",
        "Open-source observability platform for LLM applications with tracing, evaluation, and monitoring.",
        secondary=["H.54", "H.55"], deployment=["self-hosted", "cloud"],
        capabilities=["tracing", "monitoring", "evaluation"]
    ))
    
    # ── I. Models & Infrastructure ──
    entries.append(make_entry(
        "ollama", "ollama",
        "I.66", "application",
        "Local model runner for managing and serving LLMs on consumer hardware with a simple API.",
        secondary=["I.67"], deployment=["local-first"],
        capabilities=["local-llm", "model-serving"]
    ))
    entries.append(make_entry(
        "vllm-project", "vllm",
        "I.65", "library",
        "High-throughput LLM inference engine with PagedAttention for efficient memory management.",
        secondary=["I.64"], deployment=["self-hosted"],
        capabilities=["inference-serving", "high-throughput"]
    ))
    entries.append(make_entry(
        "lm-sys", "FastChat",
        "I.65", "application",
        "Platform for training, serving, and evaluating LLMs with a web-based chat interface.",
        deployment=["self-hosted"], capabilities=["model-serving", "chat-interface"]
    ))
    entries.append(make_entry(
        "khoj-ai", "khoj",
        "J.73", "application",
        "AI-powered personal search assistant that indexes notes, documents, and code for semantic retrieval.",
        secondary=["F.38"], capabilities=["search", "knowledge-management"]
    ))
    
    # ── J. Applications & Interfaces ──
    entries.append(make_entry(
        "n8n-io", "n8n",
        "J.79", "application",
        "Workflow automation platform with AI agent capabilities and extensive integration library.",
        secondary=["B.8"], deployment=["self-hosted", "cloud"],
        capabilities=["workflow-automation", "integrations"]
    ))
    entries.append(make_entry(
        "FlowiseAI", "Flowise",
        "J.79", "application",
        "Low-code visual platform for building LLM applications with drag-and-drop workflow design.",
        deployment=["self-hosted"], capabilities=["no-code", "visual-builder"]
    ))
    
    # ── E. Skills, Extensions & Interoperability ──
    entries.append(make_entry(
        "composiohq", "composio",
        "E.35", "SDK",
        "Platform for integrating AI agents with external tools and APIs through standardized connectors.",
        secondary=["E.36"], protocols=["MCP"],
        capabilities=["tool-integration", "connectors"]
    ))
    entries.append(make_entry(
        "getzep", "zep",
        "F.37", "library",
        "Memory service for AI assistants with persistent knowledge, entity extraction, and dialogue history.",
        secondary=["F.43"], capabilities=["memory", "entity-extraction"]
    ))
    
    # Security
    entries.append(make_entry(
        "anthropics", "prompt-eng-interactive-tutorial",
        "A.3", "tutorial",
        "Interactive course for learning prompt engineering and agent development techniques."
    ))
    
    # Emerging / newer
    entries.append(make_entry(
        "plandex-ai", "plandex",
        "C.13", "CLI tool",
        "AI coding assistant that plans and implements complex changes across multiple files.",
        capabilities=["planning", "multi-file-editing"]
    ))
    
    return entries


def main():
    parser = argparse.ArgumentParser(description="Seed initial catalog")
    parser.add_argument("--output", default="data/catalog.json")
    parser.add_argument("--verify", action="store_true", help="Verify repos via API")
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    
    print("=" * 60)
    print("Building seed catalog...")
    print("=" * 60)
    
    entries = build_seed_catalog()
    print(f"Created {len(entries)} seed entries")
    
    # Optional verification
    if args.verify:
        print("\nVerifying repositories...")
        for i, e in enumerate(entries):
            owner, repo = e["owner"], e["name"]
            result = verify_repo(owner, repo)
            if result:
                e["stars"] = result.get("stargazers_count", 0)
                e["forks"] = result.get("forks_count", 0)
                e["open_issues"] = result.get("open_issues_count", 0)
                e["primary_language"] = result.get("language")
                e["languages"] = [result.get("language")] if result.get("language") else []
                e["topics"] = result.get("topics", [])
                e["license"] = result["license"].get("spdx_id") if result.get("license") else None
                e["created_at"] = result.get("created_at")
                e["updated_at"] = result.get("updated_at")
                e["pushed_at"] = result.get("pushed_at")
                e["archived"] = result.get("archived", False)
                e["maintenance_status"] = "archived" if result.get("archived") else "active"
                e["homepage_url"] = result.get("homepage")
                print(f"  VERIFIED {owner}/{repo}: {e['stars']} stars")
            else:
                print(f"  NOT FOUND {owner}/{repo}")
        
        print(f"\nVerified {len(entries)} repositories")
    
    # Write catalog
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "snapshot_date": SNAPSHOT_DATE,
            "count": len(entries),
            "schema_version": "1.0",
            "entries": entries,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nCatalog written to {args.output}")
    print(f"Total entries: {len(entries)}")
    print("\nTo enrich with API data: python scripts/seed_catalog.py --verify")
    print("To classify:        python scripts/classify.py")
    print("To score:           python scripts/score.py")
    print("To render:          python scripts/render.py")
    print("To validate:        python scripts/validate.py")


if __name__ == "__main__":
    main()
