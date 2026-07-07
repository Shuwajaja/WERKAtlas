#!/usr/bin/env python3
"""
classify.py — LOOP 2: Classify candidates into taxonomy categories.

Reads an enriched catalog, assigns primary and secondary categories,
and writes back the classified catalog.

Usage:
    python scripts/classify.py --input data/catalog.json --taxonomy data/taxonomy.json --output data/catalog.json
"""

import argparse
import json
import sys
from pathlib import Path


def load_taxonomy(path: str) -> dict:
    """Load taxonomy from JSON."""
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_catalog(path: str) -> list:
    """Load catalog entries."""
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("entries", [])


def infer_category(entry: dict, taxonomy: dict) -> tuple:
    """Infer primary and secondary categories from available metadata."""
    topics = set(t.lower() for t in entry.get("topics", []))
    name = (entry.get("name") or "").lower()
    desc = (entry.get("description") or "").lower()
    repo = (entry.get("repository") or "").lower()
    
    # Category inference rules (ordered most specific first)
    
    # D. MCP Ecosystem
    if any(t in topics or t in name or t in desc for t in [
        "mcp-server", "mcp-client", "mcp-host", "model-context-protocol",
        "mcp-sdk", "mcp-gateway", "mcp-proxy", "mcp-registry",
        "mcp-inspector", "mcp-security", "mcp-tool"
    ]):
        if "mcp-server" in topics or (("mcp-server" in name or "mcp server" in desc) and "mcp-client" not in name):
            return ("D.20", ["D.22", "D.28"])
        if "mcp-client" in topics or "mcp-client" in name or "mcp client" in desc:
            return ("D.21", ["D.22"])
        if "mcp-sdk" in topics or any(s in repo for s in ["python-sdk", "typescript-sdk", "java-sdk", "kotlin-sdk", "go-sdk"]):
            return ("D.22", ["D.20"])
        if "mcp-registry" in topics or "mcp-registry" in name:
            return ("D.23", ["D.28"])
        if "mcp-gateway" in topics or "mcp-gateway" in name or "mcp-gateway" in repo:
            return ("D.24", ["D.21"])
        if "mcp" in topics or "mcp" in name:
            return ("D.20", ["D.22"])
    
    # C. Coding Agents
    if any(t in topics or t in name or t in desc for t in [
        "coding-agent", "software-engineering-agent", "swe-agent", "code-agent",
        "code-interpreter"
    ]):
        if "swe-bench" in topics or "swe-bench" in name:
            return ("C.19", ["H.56"])
        if "software-engineering-agent" in topics:
            return ("C.13", ["C.14"])
        return ("C.13", ["C.14", "C.18"])
    
    # Check for specific coding agent names
    code_agent_names = ["aider", "swe-agent", "open-interpreter", "claude-code",
                        "codex", "copilot", "cursor", "windsurf", "bamt"]
    if any(a in name for a in code_agent_names):
        if "codex" in name or "copilot" in name or "cursor" in name:
            return ("C.15", ["C.13"])
        return ("C.13", ["C.14"])
    
    # B. Frameworks & Runtimes
    if any(t in topics or t in name or t in desc for t in [
        "agent-framework", "ai-agent-framework", "agent-runtime", "llm-framework"
    ]):
        return ("B.6", ["E.35"])
    
    if "multi-agent" in topics or "multi-agent" in name or "agent-swarm" in topics or "swarm" in topics:
        return ("B.9", ["B.8"])
    
    if any(t in topics or t in name for t in ["langgraph", "workflow", "agent-orchestration"]):
        return ("B.8", ["B.6"])
    
    # G. Browser & Computer Use
    if any(t in topics or t in name or t in desc for t in [
        "browser-agent", "computer-use", "web-agent", "playwright-agent"
    ]):
        return ("G.44", ["G.45"])
    
    if "computer-use" in topics or "computer-use" in name or "computer use" in desc:
        return ("G.45", ["G.44"])
    
    if "sandbox" in topics or "sandbox" in name or "ai-sandbox" in topics:
        return ("G.49", ["G.48"])
    
    # F. Context, Knowledge, Memory
    if any(t in topics or t in name or t in desc for t in [
        "agent-memory", "memory", "rag", "retrieval-augmented",
        "knowledge-graph", "vector-store", "vector-database", "chroma",
        "weaviate", "qdrant", "milvus", "pinecone"
    ]):
        if "rag" in topics or "rag" in name:
            return ("F.38", ["F.37"])
        if "vector" in topics or "vector" in name:
            return ("F.38", ["F.39"])
        if "memory" in topics or "memory" in name:
            return ("F.37", ["F.38"])
        if "knowledge-graph" in topics:
            return ("F.39", ["F.38"])
    
    # H. Reliability & Operations
    if any(t in topics or t in name or t in desc for t in [
        "agent-observability", "llm-observability", "llm-tracing", "agent-tracing"
    ]):
        return ("H.53", ["H.54"])
    
    if any(t in topics or t in name or t in desc for t in [
        "agent-evaluation", "llm-evaluation", "agent-benchmark", "llm-benchmark",
        "deepeval", "ragas", "evaluation-framework"
    ]):
        return ("H.55", ["H.56"])
    
    if any(t in topics or t in name or t in desc for t in [
        "guardrails", "agent-security", "llm-security", "ai-safety"
    ]):
        return ("H.57", ["H.58"])
    
    # I. Models & Infrastructure
    if any(t in topics or t in name or t in desc for t in [
        "llm-gateway", "model-router", "model-gateway", "inference-server",
        "llm-serving", "vllm", "ollama"
    ]):
        return ("I.64", ["I.65"])
    
    if "inference-server" in topics or "inference" in name:
        return ("I.65", ["I.64"])
    
    if "ollama" in name or "local" in name and "model" in desc:
        return ("I.66", ["I.67"])
    
    # E. Tools & Interoperability
    if any(t in topics or t in name or t in desc for t in [
        "tool-calling", "function-calling", "agent-skills", "agent-plugins",
        "composio", "agent-protocol"
    ]):
        return ("E.35", ["E.34"])
    
    if "agent-protocol" in topics or "agent-protocol" in name:
        return ("E.34", ["E.35"])
    
    # J. Applications
    if any(t in topics or t in name or t in desc for t in [
        "agent-ui", "agent-workspace", "chat-interface", "agent-dashboard"
    ]):
        return ("J.77", ["J.78"])
    
    if "no-code" in topics or "low-code" in name or "no-code" in desc:
        return ("J.79", ["J.77"])
    
    # A. Learning
    if any(t in topics or t in name or t in desc for t in [
        "tutorial", "build-your-own", "course", "workshop", "learning",
        "reference-implementation", "cookbook"
    ]):
        return ("A.1", ["A.3"])
    
    # Default: try to infer from repo content
    # Frameworks are often larger, well-organized repos
    if entry.get("stars", 0) > 5000 and entry.get("languages", []):
        return ("B.6", [])
    
    # Best guess
    return ("J.81", [])


def main():
    parser = argparse.ArgumentParser(description="Classify catalog entries")
    parser.add_argument("--input", default="data/catalog.json")
    parser.add_argument("--taxonomy", default="data/taxonomy.json")
    parser.add_argument("--output", default="data/catalog.json")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Agentic Engineering Compendium — Classification (LOOP 2)")
    print("=" * 60)
    
    taxonomy = load_taxonomy(args.taxonomy)
    entries = load_catalog(args.input)
    
    print(f"Classifying {len(entries)} entries...")
    
    classified = 0
    for entry in entries:
        if entry.get("primary_category") is None:
            primary, secondary = infer_category(entry, taxonomy)
            entry["primary_category"] = primary
            entry["secondary_categories"] = list(set(secondary))
            classified += 1
    
    print(f"Classified {classified} entries (already classified: {len(entries) - classified})")
    
    # Count by category
    from collections import Counter
    cat_counts = Counter(e.get("primary_category", "unknown") for e in entries)
    print("\nCategory distribution:")
    for cat, count in cat_counts.most_common():
        cat_name = "unknown"
        for group in taxonomy.get("categories", {}).values():
            if cat in group.get("subcategories", {}):
                cat_name = group["subcategories"][cat]["name"]
                break
        print(f"  {cat}: {count} ({cat_name})")
    
    # Write output
    with open(args.output, "w", encoding="utf-8-sig") as f:
        json.dump({
            "snapshot_date": entries[0].get("checked_at", "2026-07-07")[:10] if entries else "2026-07-07",
            "count": len(entries),
            "schema_version": "1.0",
            "entries": entries,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nOutput written to {args.output}")


if __name__ == "__main__":
    main()
