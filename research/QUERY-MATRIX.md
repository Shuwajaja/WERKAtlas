# GitHub Query Matrix

## Query Strategy

For each concept, search: exact phrase, topic, repo name+description, README, recently updated, most-starred, recently created.

## Core Agent Queries

| Query | Purpose | Priority |
|---|---|---|
| `topic:ai-agent` | GitHub topic tag | High |
| `topic:llm-agent` | Alternative topic tag | High |
| `ai-agent in:name,description` | Broad name/desc match | High |
| `agent-framework in:name,description` | Framework discovery | High |
| `agent-runtime in:name,description` | Runtime discovery | Medium |
| `agent-orchestration in:name,description` | Orchestration | Medium |
| `multi-agent in:name,description` | Multi-agent systems | High |
| `agent-swarm in:name,description` | Swarm systems | Medium |
| `build-your-own-agent in:readme` | Tutorial discovery | Medium |

## Coding Agent Queries

| Query | Purpose | Priority |
|---|---|---|
| `topic:coding-agent` | Coding agent topic | High |
| `topic:software-engineering-agent` | SWE agent topic | Medium |
| `coding-agent in:name,description` | Name/desc match | High |
| `software-engineering-agent in:name,description` | SE agent match | High |
| `code-agent in:name,description` | Code agent match | Medium |
| `swe-agent in:name,description` | SWE agent match | High |
| `code-interpreter in:name,description` | Code execution | Medium |

## MCP Ecosystem Queries

| Query | Purpose | Priority |
|---|---|---|
| `topic:mcp-server` | MCP server topic | High |
| `topic:mcp-client` | MCP client topic | High |
| `topic:model-context-protocol` | MCP topic | High |
| `model-context-protocol in:name,description` | MCP projects | High |
| `mcp-server in:name,description` | Named MCP servers | High |
| `mcp-client in:name,description` | Named MCP clients | High |
| `mcp-host in:name,description` | MCP hosts | Medium |
| `mcp-gateway in:name,description` | MCP gateways | Medium |
| `mcp-proxy in:name,description` | MCP proxies | Medium |
| `mcp-registry in:name,description` | MCP registries | Medium |
| `mcp-inspector in:name,description` | MCP debugging | Medium |
| `mcp-security in:name,description` | MCP security | Medium |
| `mcp-sdk in:name,description` | MCP SDKs | Medium |
| `mcp-tool in:name,description` | MCP tools | Medium |

## Browser & Computer-Use Agents

| Query | Purpose | Priority |
|---|---|---|
| `topic:browser-agent` | Browser agent topic | High |
| `topic:computer-use` | Computer use topic | High |
| `browser-agent in:name,description` | Browser agents | High |
| `computer-use in:name,description` | Computer use | High |
| `web-agent in:name,description` | Web agents | Medium |
| `playwright-agent in:name,description` | Playwright agents | Medium |
| `selenium-agent in:name,description` | Selenium agents | Low |

## Memory, Context, Retrieval

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-memory` | Agent memory topic | High |
| `agent-memory in:name,description` | Memory systems | High |
| `topic:retrieval-augmented` | RAG topic | High |
| `topic:knowledge-graph` | Knowledge graph topic | Medium |
| `rag in:name,description` | RAG systems | High |
| `vector-store in:name,description` | Vector stores | Medium |
| `context-engineer in:name,description` | Context engineering | Low |

## Evaluation & Benchmarks

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-evaluation` | Agent eval topic | High |
| `topic:llm-benchmark` | LLM benchmark topic | Medium |
| `agent-evaluation in:name,description` | Eval frameworks | High |
| `agent-benchmark in:name,description` | Benchmarks | High |
| `llm-eval in:name,description` | LLM evaluation | Medium |

## Security & Sandbox

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-security` | Agent security topic | Medium |
| `topic:llm-security` | LLM security topic | Medium |
| `topic:ai-sandbox` | AI sandbox topic | Medium |
| `agent-sandbox in:name,description` | Sandbox systems | High |
| `ai-safety in:name,description` | AI safety | Medium |
| `guardrails in:name,description` | Guardrails | High |

## Observability & Operations

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-observability` | Agent observability topic | Medium |
| `topic:llm-observability` | LLM observability topic | Medium |
| `agent-observability in:name,description` | Observability | High |
| `llm-tracing in:name,description` | LLM tracing | High |
| `agent-tracing in:name,description` | Agent tracing | Medium |

## Models & Infrastructure

| Query | Purpose | Priority |
|---|---|---|
| `topic:llm-gateway` | LLM gateway topic | Medium |
| `topic:model-router` | Model router topic | Low |
| `llm-gateway in:name,description` | LLM gateways | High |
| `model-router in:name,description` | Model routing | Medium |
| `inference-server in:name,description` | Inference servers | High |
| `topic:inference-server` | Inference topic | Medium |
| `topic:llm-serving` | LLM serving topic | Medium |

## Tool Calling & Function Calling

| Query | Purpose | Priority |
|---|---|---|
| `topic:tool-calling` | Tool calling topic | Medium |
| `topic:function-calling` | Function calling topic | Medium |
| `tool-calling in:name,description` | Tool calling libs | High |
| `function-calling in:name,description` | Function calling | High |

## Agent Protocols

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-protocol` | Agent protocol topic | Medium |
| `agent-protocol in:name,description` | Agent protocols | High |
| `topic:a2a` | Agent-to-Agent topic | Medium |
| `topic:anp` | Agent Network Protocol | Low |

## Agent Skills & Plugins

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-skills` | Agent skills topic | Low |
| `agent-skills in:name,description` | Skills packages | Medium |
| `agent-plugins in:name,description` | Plugin systems | Medium |
| `agent-tools in:name,description` | Tool collections | Medium |

## Durable & Long-Running Agents

| Query | Purpose | Priority |
|---|---|---|
| `durable-agent in:name,description` | Durable agents | Medium |
| `long-running-agent in:name,description` | Long-running | Medium |
| `agent-worker in:name,description` | Agent workers | Medium |
| `background-agent in:name,description` | Background agents | Low |

## Agent Control Plane

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-control-plane` | Control plane topic | Low |
| `agent-control-plane in:name,description` | Control planes | Medium |
| `agent-platform in:name,description` | Agent platforms | High |
| `agent-deployment in:name,description` | Deployment | Medium |

## Agent UIs & Workspaces

| Query | Purpose | Priority |
|---|---|---|
| `topic:agent-ui` | Agent UI topic | Low |
| `agent-ui in:name,description` | Agent interfaces | Medium |
| `agent-workspace in:name,description` | Agent workspaces | Medium |
| `chat-interface in:name,description` | Chat interfaces | Low |

## Organization-Specific Queries

For each org in sources.json, inspect all public repos.

## Language-Specific Variants

Where useful, add language filter: `language:python`, `language:typescript`, `language:rust`, `language:go`, `language:java`, `language:kotlin`, `language:swift`

## Exclusions

Filter out: game NPC agents, monitoring agents (traditional), real-estate agents, generic software agents unrelated to LLM/AI.
