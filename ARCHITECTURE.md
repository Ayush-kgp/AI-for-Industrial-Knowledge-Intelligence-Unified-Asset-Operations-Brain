# Architecture

## High-Level Flow

```
                    Document Upload
                           |
                           v
                 Document Processing Pipeline
                           |
        +------------------+--------------------+
        v                  v                     v
Metadata Store       Knowledge Graph        Vector Store
(PostgreSQL)            (Neo4j)                (Qdrant)
        |                  |                     |
        +------------+-----+----------------+----+
                     v
             Agentic Query Planner
                     |
       +-------------+-------------+
       v             v             v
 Hybrid Retrieval   Graph Search   Metadata Lookup
                     |
                     v
             Context Assembly
                     |
                     v
          Gemini Answer Generation
                     |
                     v
     Answer + Citations + Confidence
```

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Backend | FastAPI | Async endpoints, REST |
| Metadata store | PostgreSQL | Never stores vectors |
| Vector store | Qdrant | Dense + sparse (BM25) vectors, chunk metadata, Neo4j node IDs |
| Knowledge graph | Neo4j | Entities + relationships |
| Embeddings | BGE-M3 | Runs locally, multilingual |
| LLM | Gemini 2.5 Flash | OCR, entity extraction, answer generation — NOT embeddings |
| Frontend | Next.js + Tailwind | Mobile-first (matches the problem statement's "for field technicians, not just desktops" requirement) |

## Storage Responsibility (single-responsibility rule — do not violate)

| Store | Owns | Never stores |
|---|---|---|
| PostgreSQL | Document metadata, upload history, versions, ingestion status, processing timestamps | Vectors, graph relationships |
| Neo4j | Equipment, Documents, SOPs, Maintenance Records, Inspection Findings, Personnel, Regulatory Clauses + their relationships | Raw chunk text, embeddings |
| Qdrant | Dense/sparse embeddings, chunk text, chunk metadata, `neo4j_node_id` pointer | Canonical entity relationships |

The `neo4j_node_id` stored in every Qdrant payload is the key optimization: retrieval jumps straight to the correct graph node instead of re-querying Neo4j by name/ID. This is worth calling out explicitly in the demo — it's a concrete "why our GraphRAG is faster" answer.

## Ingestion Pipeline (each stage independently testable)

```
Upload -> File Parsing -> OCR (if needed) -> Entity Extraction ->
Metadata Extraction -> Chunking -> Embedding Generation ->
Graph Update -> Vector Update -> Metadata Update
```

Incremental indexing: new documents are parsed and merged into existing graph/vector/metadata stores without a full rebuild, with version history preserved. This is worth demoing explicitly (upload doc #2, show the graph update live) — it's evidence of production thinking, which supports the Technical Excellence and Scalability criteria.

## Hybrid Retrieval

1. Understand intent (equipment IDs, doc type, maintenance vs. compliance intent)
2. Planner decides: vector-only / graph-only / hybrid
3. Execute: semantic search, BM25, graph traversal
4. Fuse results via Reciprocal Rank Fusion
5. Assemble context
6. Generate grounded answer (citations + confidence + source snippets, no exceptions)

## Agentic Query Planner (the one real agent)

Tools available to the planner:
- Equipment Lookup — retrieve equipment metadata
- Graph Traversal — find related entities
- Hybrid Search — retrieve supporting documents
- Metadata Lookup — retrieve document history
- Citation Collector — collect supporting chunks
- Answer Generator — produce final response

Keep this as genuine orchestration (planner picks tools per query), not a fixed linear chain, and not a proliferation of narrowly-scoped "agents" for their own sake.

## Known Risks & Mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| 3 stateful services (Postgres, Neo4j, Qdrant) to stand up | Biggest single point of hackathon-day failure | Docker-compose all three on day 1 before writing pipeline code; verify connectivity first |
| Single LLM dependency (Gemini) for OCR + extraction + generation | Rate limits / connectivity issues during a live demo are common failure modes | Cache a known-good demo run (pre-computed answers) as a fallback path |
| Local BGE-M3 inference | Can be slow without GPU | Benchmark early; have a smaller/faster fallback model identified |
| Graph schema changes after Phase 2 | Downstream ingestion/retrieval code breaks silently | Freeze schema after Phase 2 (see SCHEMA.md); any change after that requires explicit review |
| CV/P&ID parsing and compliance detection are out of MVP scope | Both are explicitly named in the official problem statement | Have a one-line "scope cut, here's the roadmap" answer ready for judges |
