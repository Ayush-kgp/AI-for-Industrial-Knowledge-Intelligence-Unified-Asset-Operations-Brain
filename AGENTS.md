# Agent Instructions

Read this before writing any code in this repo. It exists to stop scope creep during the hackathon — the biggest risk to this project isn't a missing feature, it's building the wrong thing well.

## Hard Scope Boundaries

Do NOT build, even if it seems like a small addition:
- Computer vision / P&ID drawing parsing
- Live IoT integration
- Predictive maintenance or RCA beyond what's needed for the MVP's graph-traversal demo query
- Enterprise authentication (no login system — assume single-user/demo context)
- Distributed microservices — this is one FastAPI service talking to three data stores, not a service mesh
- Compliance/regulatory gap detection as a working feature (stretch only, after MVP is stable)

If a task seems to require one of these, stop and flag it rather than implementing a partial version.

## Single-Responsibility Storage — Non-Negotiable

- PostgreSQL: metadata only. Never write vectors or graph relationships here.
- Neo4j: entities and relationships only. Never write raw chunk text or embeddings here.
- Qdrant: vectors + chunk text + payload (including `neo4j_node_id`) only. Never treat this as the source of truth for entity relationships.

If new code needs to store something, the storage decision should be obvious from this list. If it isn't, ask before picking a store.

## Schema Freeze

The Neo4j node/relationship schema and Qdrant payload shape (see SCHEMA.md) are frozen after Phase 2. Do not add new node types, relationship types, or payload fields after that point without explicit confirmation — downstream ingestion and retrieval code depends on this staying stable.

## Trust Requirements — Every Answer, No Exceptions

Every response the Copilot generates must include:
- Citations (which source chunk/document it came from)
- A confidence indicator
- The source snippet itself

No answer should be shipped without all three, even in early testing — build this in from the first working version, not bolted on later.

## Agentic Planner — Build This For Real, Not a Router

This is the centerpiece of the project for portfolio purposes. Don't reduce it to a keyword-matching router under time pressure — cut something else first (frontend polish, a stretch feature, demo rehearsal time) before cutting this.

- Use Gemini's function-calling / tool-use API, not a hand-rolled if/else intent classifier.
- Define real tool schemas for each tool: Equipment Lookup, Graph Traversal, Hybrid Search, Metadata Lookup, Citation Collector, Answer Generator — each with a clear input/output contract.
- The planner should be able to make more than one tool call per query when the question genuinely needs it. Example: "which maintenance procedures followed the last compressor trip?" needs Graph Traversal (find the trip event) → Hybrid Search (find the procedures) → Citation Collector. This multi-step behavior is what separates a real agent from a router, and it's the most demo-able and resume-able piece of the whole system.
- Log the planner's tool-selection reasoning somewhere visible — a debug endpoint or a reasoning-trace panel in the UI. This is a strong demo moment for judges and the exact artifact you'll want to point to later when this project comes up in an interview.
- Keep the "one real agent, several tools" framing. Don't spin up separate named "agents" per tool — that reads as agent-washing a normal pipeline, which undercuts the resume value rather than adding to it.

## Build Order (de-risk infra first)

1. Database Connectivity (Neo4j, Qdrant, Postgres). Note: We are currently running against hosted free-tier instances (Neo4j Aura, Qdrant Cloud, Supabase/Neon), not local containers, due to local Docker limitations. The docker-compose.yml file remains for reference.
2. Ingestion pipeline stages, each independently testable (parsing, OCR, entity extraction, chunking, embedding, graph update, vector update, metadata update).
3. Hybrid retrieval (vector + BM25 + graph), then the planner on top of it.
4. FastAPI endpoints, then the Next.js chat UI with citation panel.

Don't start the frontend before ingestion + retrieval produce a real answer end-to-end via a script or API call — a working backend answer with no UI beats a polished UI with no real answer underneath it.

## Testing Expectation

Each ingestion stage should be testable in isolation with a small sample document, without needing the full pipeline to run. Don't write pipeline code that can only be verified end-to-end — that makes debugging under hackathon time pressure much harder.
