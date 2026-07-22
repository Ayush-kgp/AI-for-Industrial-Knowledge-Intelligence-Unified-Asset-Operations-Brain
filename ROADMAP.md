# Roadmap — 24 Hours, Solo

## Reality Check (revised)

Priority order, per your call: **this is a CV/portfolio piece first, hackathon submission second.** That changes what gets cut when time runs short. The rule now is: protect technical depth and the things an interviewer would actually ask about; sacrifice demo polish and feature breadth instead.

Concretely, versus the earlier draft of this file:

- **The agentic LLM planner is back in, and it's real** — Gemini function-calling with proper tool schemas and multi-step tool orchestration, not a keyword router. This is the centerpiece of the build. See AGENTS.md for implementation detail. If something has to give later in the day, it is not this.
- **PostgreSQL is back in as a separate service**, alongside Neo4j and Qdrant, matching ARCHITECTURE.md and SCHEMA.md as originally designed. Three purpose-chosen data stores is a more legitimate "system design" story on a resume than one database doing everything. This does add infra setup time and one more thing that can break — accepted, given the priority order above.
- **Stretch features (Lessons Learned, Compliance Flag, Equipment 360°) stay cut.** The planner is where the remaining time goes instead — depth over breadth.
- CV/P&ID parsing and full compliance detection are still out of scope, for the same reason as before (real engineering-time cost, not a quick add).

## Before Hour 0

Do this ahead of the clock starting:
- Write/collect 3–5 demo documents (equipment manual, maintenance log, SOP, inspection report — synthetic is fine, they just need to be internally consistent so the graph and multi-step planner queries are real)
- Draft 4–5 benchmark questions, including at least one that genuinely requires the planner to chain more than one tool call (e.g., "which maintenance procedures followed the last compressor trip?" — needs graph traversal to find the trip, then search for the procedures)
- Get a Gemini API key working, including a test function-calling round trip (not just a plain completion — confirm tool-use works before Hour 0)
- `docker-compose` file for Postgres + Neo4j + Qdrant, pulled and tested

## Hour-by-Hour

**0–2: Infra + skeleton**
Docker-compose Postgres + Neo4j + Qdrant, all reachable. FastAPI skeleton with a health-check endpoint. Confirm a Gemini function-calling test call works. Nothing else until this is green.

**2–8: Ingestion pipeline**
Parsing → OCR (if needed) → Gemini entity extraction → chunking → BGE-M3 embedding → Postgres metadata write → Neo4j graph write → Qdrant vector write (with `neo4j_node_id` in payload). Build and test on one document first, then batch the rest of your demo corpus.

**8–9: Break**
Still worth taking, even with the shifted priorities — Hour 13's planner work needs you sharp, not running on fumes.

**9–13: Retrieval**
Vector search + BM25 in Qdrant, graph traversal in Neo4j, a reasonable fusion of the two (full RRF if time allows, a simpler weighted combination if not — this part doesn't need to be gold-plated), context assembly, Gemini answer generation with citations + confidence. Test against your benchmark questions.

**13–18: Agentic planner (the centerpiece — protect this time block)**
Gemini function-calling planner with real tool schemas: Equipment Lookup, Graph Traversal, Hybrid Search, Metadata Lookup, Citation Collector, Answer Generator. Get single-tool-call queries working first, then the multi-step case (your chained benchmark question from Hour 0). Add reasoning-trace logging as you go — it's cheap to add now and expensive to bolt on later, and it's the part worth screenshotting for a portfolio.

**Checkpoint at Hour 18:** if the multi-step planner case isn't working yet, keep going a bit into the frontend block below rather than abandoning it — this is the piece you don't want to ship half-built, per the stated priority.

**18–20: Frontend**
Next.js + Tailwind, mobile-first, chat view with a citation panel. Add a simple reasoning-trace panel too if the planner logging from the last block is ready — low effort, high resume value, shows the agent's tool-selection process rather than just the final answer.

**20–22: Integration + demo rehearsal**
Run your full benchmark question set end-to-end. Cache known-good answers as a fallback for live-demo flakiness. Fix anything broken in the core pipeline before touching anything cosmetic.

**22–23: Pitch narrative**
Tie the demo explicitly to the business-impact numbers in README.md, and prepare the one-liners for "what about P&IDs / compliance / predictive maintenance" if a judge asks. Still worth doing even with hackathon submission as the secondary goal — a clean narrative is part of the portfolio story too.

**23–24: Buffer**
Last-minute fixes only. Don't start anything new here.
