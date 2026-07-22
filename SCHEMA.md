# Schema

**Freeze this after Phase 2.** Any change after that point should be a deliberate, reviewed decision — not something the coding agent does mid-pipeline because it's convenient.

## Neo4j — Knowledge Graph

**Nodes:**
- Equipment
- Document
- Procedure
- MaintenanceRecord
- InspectionFinding
- Person
- RegulatoryClause

**Relationships:**
- `MENTIONED_IN`
- `MAINTAINED_BY`
- `FOLLOWS`
- `INSPECTED_ON`
- `RELATED_TO`
- `PRECEDED_BY`
- `GOVERNED_BY`
- `UPDATES` (Added after Hour 2-8 extraction revealed inter-document causal references that RELATED_TO couldn't distinguish. Freeze resumes after this addition.)
- `SUPERSEDES` (Added after Hour 2-8 extraction revealed inter-document causal references that RELATED_TO couldn't distinguish. Freeze resumes after this addition.)
- `ISSUED_IN_RESPONSE_TO` (Added after Hour 2-8 extraction revealed inter-document causal references that RELATED_TO couldn't distinguish. Freeze resumes after this addition.)

## Qdrant — Vector Store Payload

Every point payload should carry:
- `chunk` (text)
- `document_id`
- `equipment_tag`
- `neo4j_node_id` — enables retrieval to jump straight to the correct graph node instead of re-querying Neo4j
- `page_number`

Plus the dense (BGE-M3) and sparse (BM25) vectors themselves.

## PostgreSQL — Metadata Store (proposed — adjust as ingestion pipeline concretizes)

This isn't specified in detail in the source plan, so treat these as a starting draft, not a locked contract:

**`documents`**
- `id`, `title`, `source_type` (pdf/scan/spreadsheet/email), `upload_timestamp`, `current_version_id`, `ingestion_status` (queued/parsing/ocr/extracting/embedding/graph_updating/complete/failed)

**`document_versions`**
- `id`, `document_id`, `version_number`, `uploaded_at`, `file_path`, `checksum`

**`ingestion_events`**
- `id`, `document_id`, `stage`, `status`, `started_at`, `completed_at`, `error_message`

Keep this store metadata-only. If you find yourself adding a column for embeddings or graph relationships here, that's a single-responsibility violation — it belongs in Qdrant or Neo4j instead.
