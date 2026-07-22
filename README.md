# Industrial Knowledge Intelligence Platform

**One-liner:** An AI platform that turns fragmented industrial documents (engineering drawings, maintenance records, SOPs, inspection reports) into a single, citation-grounded, graph-aware knowledge base — so engineers *discover* knowledge instead of *searching* for it.

Built for the "AI for Industrial Knowledge Intelligence: Unified Asset & Operations Brain" hackathon track.

---

## Why This Matters (the business case — don't skip this in the pitch)

The problem statement backs the "knowledge fragmentation" claim with real numbers. These should show up in the demo narrative, not just this file:

- Professionals in asset-intensive industries spend an average of **35% of working hours** searching for information or recreating documents that already exist (McKinsey, 2024).
- A typical large Indian plant runs across **7–12 disconnected document systems** (P&IDs, work orders, SOPs, inspection records, regulatory filings) — NASSCOM-EY.
- Document fragmentation contributes to **18–22% of unplanned downtime** in Indian heavy industry (BIS Research).
- **~25% of India's experienced industrial engineers/operators retire within a decade**, taking undocumented operational knowledge with them — a one-way loss once it happens.

This is the "so what" the architecture needs to keep pointing back to. A judge should be able to connect every MVP feature to one of these four numbers.

---

## MVP Scope

**Building:**
1. Universal Document Ingestion (PDF/scanned/text → parsed, chunked, entity-extracted)
2. Knowledge Graph Construction (Neo4j — equipment, documents, procedures, maintenance records, findings, people, regulatory clauses)
3. Expert Knowledge Copilot (hybrid RAG + graph traversal, citation-grounded answers with confidence scores)

**Explicitly not building (say this proactively, don't wait to be asked):**
- Full predictive maintenance / RCA agent
- Live IoT integration
- Computer Vision / P&ID drawing digitization — *this is in the official "suggested technologies" list, so have a one-line answer ready: scope cut for the hackathon window, first roadmap item post-MVP*
- Compliance/regulatory gap detection as a first-class feature — *also named in the evaluation focus; pushed to stretch, same rule: have the answer ready*
- Enterprise authentication
- Distributed microservices

**Stretch (only after MVP is demo-stable):**
- Lessons Learned / Failure Intelligence
- Compliance Flag (map procedures against regulations)
- Equipment 360° view

---

## Success Metrics (mapped to what's actually judged)

The evaluation focus in the problem statement names these directly — treat them as your test plan, not just marketing copy:

| Judged on | How the MVP demonstrates it |
|---|---|
| Entity extraction accuracy | Show extracted equipment tags / dates / personnel against a known-answer doc during demo |
| Query answer quality | Domain-expert benchmark questions, answered with citations + confidence |
| Knowledge graph linkage completeness | A cross-document graph-traversal query (Story 3) that vector search alone can't answer |
| Time-to-answer vs. traditional search | Have a "search this manually" comparison ready, even informally timed |
| Cross-functional knowledge discovery | Equipment 360° or Lessons Learned as the "wow" moment |
| Compliance gap detection accuracy | *Gap — currently stretch scope. Decide before the pitch whether to demo a minimal version or explicitly narrate it as roadmap* |

Judging weights (reconstructed from a partially garbled table in the problem doc — verify against the original before finalizing prep): Business Impact 25%, Technical Excellence 25%, Scalability 20%, User Experience 15%, Innovation 15%.

---

## Core Principles

- **Scope discipline** — MVP is exactly the three items above. Nothing else until they work end-to-end.
- **Trust first** — every answer carries citations, confidence, and source snippets. No unsupported claims, ever.
- **Graph > chatbot** — every demo moment should showcase something vector search alone couldn't answer.
- **Single responsibility** — each storage layer owns exactly one job (see ARCHITECTURE.md). Never duplicate responsibilities across stores.

---

## Repo Docs

- `ARCHITECTURE.md` — system design, tech stack, data flow, known risks
- `SCHEMA.md` — Neo4j graph schema, Qdrant payload shape, Postgres tables
- `AGENTS.md` — ground rules for the coding agent (Antigravity) working in this repo
- `ROADMAP.md` — phased plan with time budget *(coming once hackathon duration/team size is confirmed)*
