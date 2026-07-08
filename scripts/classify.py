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
    
    # --- Known-correct overrides (prevent misclassification) ---
    # These are checked BEFORE general topic-matching rules.
    # Vector databases must never fall through to agent-framework.
    if any(k in repo or k in name for k in ["qdrant", "weaviate", "milvus", "chroma", "pinecone", "vespa"]):
        return ("F.38", ["F.43"])  # vector-store / database
    # Workflow automation platforms
    if any(k in repo or k in name for k in ["n8n", "zapier", "make-com"]):
        return ("B.8", ["E.36"])  # workflow orchestration
    # MCP official SDK repos
    if "modelcontextprotocol" in repo and "sdk" in repo:
        return ("D.22", ["D.20", "D.21"])  # MCP SDK
    # MCP Inspector
    if "modelcontextprotocol" in repo and "inspector" in repo:
        return ("D.26", ["D.22"])  # MCP developer tool

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
    
    # Safe general rules for remaining entries
    
    # Specific known edge cases
    if "china-dictatorship" in repo or "gege-circle" in repo or ".config" in name or "ftc" in name.lower() or "skystone" in name.lower() or "w3c" in desc.lower() or "freno" in repo or "qr-font" in repo or "macsurf" in repo or "netsurf" in desc.lower():
        return ("J.81", [])
    if "dolt" in repo:
        return ("F.43", ["F.37"])
    if "judge0" in repo:
        return ("G.48", ["G.49"])
    if "decryptprompt" in name or "decryptprompt" in repo or "prompt" in name or "prompt" in topics or "cliclack" in repo or "clack" in desc:
        return ("E.31", [])
    if "every-embodied" in repo or "embodied" in name or "embodied" in desc:
        return ("G.51", [])
    if "ultravox" in repo or "ultravox" in name:
        return ("G.52", [])
    if "openapi.net" in repo or "openapi" in name:
        return ("E.34", [])
    if "openmed" in repo or "openmed" in name:
        return ("J.80", [])
    if "gpt-oss" in repo:
        return ("I.67", [])
    if "gitnexus" in repo or "gitnexus" in name:
        return ("C.18", [])
    if "ml-intern" in repo or "ml-intern" in name:
        return ("C.13", [])
    if "sourcegraph" in repo:
        return ("C.18", ["C.13"])
    if "clip" in repo or "clip" in name or "pytorch-image-models" in repo:
        return ("I.67", [])
    if "tiktoken" in repo or "tiktoken" in name or "compression" in desc or "compress" in desc or "sqz" in name:
        return ("F.41", [])
    if "ocr" in name.lower() or "ocr" in desc.lower():
        return ("I.67", [])
    if "parameter-golf" in repo or "attentive-neural-processes" in repo or "anp" in topics or "attentive-neural-process" in repo or "gpconvcnp" in repo or "anplus" in topics:
        return ("I.67", [])
    if "mxc" in repo or "containment" in desc:
        return ("G.49", [])
    if "mscclpp" in repo:
        return ("E.34", [])
    if "lisa" in repo or "lisa" in name:
        return ("H.55", [])
    if "purplellama" in repo or "privacy-filter" in repo or "security" in desc or "safety" in desc or "humanize" in repo:
        return ("H.57", ["H.58"])
    if "create-llama" in repo or "upgrader" in repo:
        return ("J.81", [])
    if "luxas" in repo:
        return ("J.73", [])
    if "gabriel" in name or "gabriel" in repo:
        return ("J.74", [])
    if "qlib" in repo or "qlib" in name:
        return ("J.74", [])
    if "get-shit-done" in repo:
        return ("C.13", [])
    if "executorch" in repo:
        return ("I.66", [])
    if "autotrain" in repo:
        return ("I.67", [])
    if "ai-jsx" in repo:
        return ("B.6", [])
    if "datalayer" in name:
        return ("F.43", [])
    if "ttyd" in repo:
        return ("C.14", [])
    if "firecrawl" in desc.lower() or "crw" in repo:
        return ("G.47", [])

    # Database / persistence
    if any(k in name or k in desc for k in ["postgres", "postgresql", "redis", "mysql", "sqlite", "database", "db"]):
        return ("F.43", [])

    # Voice / audio / multimodal
    if any(k in name or k in desc for k in ["voice", "receptionist", "audio", "speech", "multimodal", "phone"]):
        return ("G.52", [])

    # PR / Code Review
    if any(k in name or k in desc for k in ["review", "pr-review", "code-review", "reviewbot"]):
        return ("C.16", [])

    # Evaluation / Testing
    if any(k in name or k in desc or k in topics for k in ["eval", "evaluation", "conformance", "test", "tests", "testing"]):
        return ("H.55", [])

    # Benchmarks / Datasets / countdowns
    if any(k in name or k in desc or k in topics for k in ["benchmark", "metrics", "deadlines"]):
        return ("H.56", [])

    # SRE / DevOps / Deployment
    if any(k in name or k in desc for k in ["helm", "charts", "actions", "setup", "deploy", "docker", "kubernetes", "k8s", "dns"]):
        return ("J.75", [])

    # Presentation / PPT
    if any(k in name or k in desc for k in ["ppt", "powerpoint", "slides", "presentation", "deck"]):
        return ("J.81", [])
        
    # Inference and runtime serving
    if any(k in repo or k in name or k in desc for k in ["onnxruntime", "triton-inference-server", "optimum", "accelerate", "vllm", "llama-cpp"]):
        return ("I.65", ["I.67"])

    # Official SDKs / API Client Libraries
    if any(k in repo or k in name for k in ["openai-python", "openai-node", "generative-ai-python", "generative-ai-js", "google-genai", "cohere-python", "anthropic-sdk", "openai-dotnet", "openai-go", "openai-java", "generative-ai-swift", "generative-ai-android", "generative-ai-dart", "langfuse-python", "langfuse-js", "hf-hub"]):
        return ("E.35", ["E.36"])

    if "sdk" in name or "sdk" in desc or "client" in name or "client" in desc or "library" in name or "library" in desc:
        if any(k in repo or k in name or k in desc for k in ["openai", "gemini", "anthropic", "llama", "cohere", "langfuse"]):
            return ("E.35", ["E.36"])

    # Ecosystem Fallback
    owner = (entry.get("owner") or "").lower()
    if owner in [
        "modelcontextprotocol", "langchain-ai", "run-llama", "huggingface", "openai",
        "anthropics", "microsoft", "google-gemini", "fixie-ai", "agno-agi",
        "gptscript-ai", "e2b-dev", "crewai", "composiohq"
    ]:
        if "mcp" in repo or "mcp" in name or "mcp" in desc:
            return ("D.20", [])
        return ("J.81", [])

    # Datasets
    if any(k in topics or k in name or k in desc for k in ["dataset", "datasets"]):
        return ("H.56", [])

    # Protocols and specifications
    if any(k in topics or k in name or k in desc for k in ["protocol", "specification", "specifications", "cross-agent", "interoperability-standard"]):
        return ("E.34", [])

    # Connectors & Integration platforms
    if any(k in topics or k in name or k in desc for k in ["integration", "connector", "pipeline", "etl", "data movement", "data-integration"]):
        return ("E.36", [])

    # DevOps, SRE, automation
    if any(k in topics or k in name or k in desc for k in ["devops", "sre", "ansible", "automation", "kubernetes", "k8s", "deploy"]):
        return ("J.75", [])

    # Coding and programming
    if any(k in topics or k in name or k in desc for k in ["coding", "programming", "codebase", "developer-tool"]):
        return ("C.13", ["C.18"])

    # Benchmarks and evaluation
    if any(k in topics or k in name or k in desc for k in ["benchmark", "benchmarks", "evaluation", "evals"]):
        return ("H.55", ["H.56"])

    # MCP specific subcategories
    if "mcp" in topics or "mcp" in name or "mcp" in desc or "model-context-protocol" in topics or "model context protocol" in desc:
        if "sdk" in name or "sdk" in topics or "sdk" in desc:
            return ("D.22", ["D.20", "D.21"])
        if "registry" in name or "registry" in topics or "registry" in desc:
            return ("D.23", ["D.28"])
        if "client" in name or "client" in topics or "client" in desc or "host" in name or "host" in topics or "host" in desc:
            return ("D.21", ["D.20"])
        if "server" in name or "server" in topics or "server" in desc:
            return ("D.20", ["D.22"])

    # Agent Skills
    if any(k in topics or k in name or k in desc for k in ["skill", "skills"]):
        return ("E.29", ["E.30"])

    # Templates, examples, starter kits, demos
    if any(k in repo or k in name or k in topics or k in desc for k in [
        "template", "starter-kit", "starter kit", "boilerplate", "example", "examples",
        "demo", "demos", "sample", "samples", "starter", "cookbook", "tutorial", "starter-template"
    ]):
        return ("J.81", ["A.1"])

    # Vector Databases / RAG
    if any(k in topics or k in name or k in desc for k in [
        "vector-database", "vector-search", "vector-store", "vector-index", "embeddings", "rag", "retrieval", "search-engine", "semantic-search"
    ]):
        return ("F.38", ["F.43"])

    # IDE / Editor extensions
    if any(k in topics or k in name or k in desc for k in [
        "vscode", "extension", "plugin", "addon", "copilot", "cursor"
    ]):
        return ("C.15", ["C.13"])

    # UI, workspace, chat interface
    if any(k in topics or k in name or k in desc for k in [
        "ui", "webui", "chat", "dashboard", "workspace", "interface", "desktop", "assistant", "assistant-platform"
    ]):
        return ("J.77", ["J.78"])

    # NOTE: The previous naive fallback
    #   has_agent AND has_tech -> B.6 (agent framework)
    # has been intentionally removed.
    # Projects that mention 'agent' and 'library' (e.g. vector databases with
    # agent integration examples) must NOT default to agent-framework.
    # Unclassified entries require manual review.

    # Return None to require manual classification if no specific rules match.
    return (None, [])


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
