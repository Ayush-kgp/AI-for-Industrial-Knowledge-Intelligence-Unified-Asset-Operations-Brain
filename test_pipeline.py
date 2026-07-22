import os
import sys
from dotenv import load_dotenv

# Load environment variables (for Gemini API Key)
load_dotenv()

from app.pipeline.parser import parse_pdf
from app.pipeline.extractor import extract_entities
from app.pipeline.chunker import chunk_text
from app.pipeline.embedder import generate_embedding
from app.pipeline.graph_writer import write_to_graph
from app.pipeline.vector_writer import write_to_vector_db

def main():
    print("=== Pipeline Stage 1-6 Test ===\n")
    
    pdf_path = "demo_manual.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Did you run generate_pdf.py?")
        sys.exit(1)
        
    print("1. [Parser] Extracting text from PDF...")
    parsed_text = parse_pdf(pdf_path)
    print("--- PARSED TEXT PREVIEW ---")
    print(parsed_text[:300] + "...\n")
    
    print("2. [Extractor] Using mocked entities to avoid 503...")
    from app.pipeline.extractor import ExtractedEntities, Person
    entities = ExtractedEntities(
        document_type="MAINTENANCE RECORD",
        equipment_tags=["C-101"],
        dates=["October 15, 2023"],
        personnel=[
            Person(name="Jane Smith", role="Technician"),
            Person(name="John Doe", role="Supervisor")
        ],
        regulatory_clauses=["OSHA standard 1910.119 (Process Safety Management)"],
        referenced_prior_events=["Q3 pressure trip incident"]
    )
    print("--- EXTRACTED ENTITIES JSON ---")
    print(entities.model_dump_json(indent=2) + "\n")
    
    print("3. [Chunker] Chunking text...")
    chunks = chunk_text(parsed_text, max_chars=500)
    print(f"--- GENERATED {len(chunks)} CHUNKS ---")
    
    print("4. [Embedder] Generating embeddings...")
    try:
        sample_chunk = chunks[0] if chunks else "Sample text"
        vector = generate_embedding(sample_chunk)
        print(f"Vector dimensions: {len(vector)}")
    except Exception as e:
        print(f"Embedding failed: {e}")
        return

    doc_id = "doc-demo-12345"
    doc_title = "Demo Maintenance Record"

    print("\n5. [Graph Writer] Writing entities to Neo4j...")
    try:
        write_to_graph(doc_id, doc_title, entities)
        print("Graph write successful.\n")
    except Exception as e:
        print(f"Graph write failed: {e}\n")

    print("6. [Vector Writer] Writing embeddings to Qdrant...")
    try:
        write_to_vector_db(doc_id, chunks, [vector], entities.equipment_tags)
        print("Vector write successful.\n")
    except Exception as e:
        print(f"Vector write failed: {e}\n")
        
    print("7. [Metadata Writer] Writing status to Postgres...")
    try:
        from app.pipeline.metadata_writer import sync_update_ingestion_status
        sync_update_ingestion_status(doc_id, "complete", "pipeline_test", None)
        print("Metadata write successful.\n")
    except Exception as e:
        print(f"Metadata write failed: {e}\n")
        
    print("\n8. [Verification] Querying live databases...")
    
    # 1. Neo4j Verification
    print("\n--- NEO4J VERIFICATION ---")
    try:
        from neo4j import GraphDatabase
        uri = os.environ.get("NEO4J_URI", "neo4j+s://localhost:7687")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        auth = (user, password) if user and password else None
        
        with GraphDatabase.driver(uri, auth=auth) as driver:
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN labels(n) as labels, properties(n) as props LIMIT 3")
                records = list(result)
                for record in records:
                    print(f"Node: {record['labels']} - {record['props']}")
    except Exception as e:
        print(f"Neo4j Verification Failed: {e}")

    # 2. Qdrant Verification
    print("\n--- QDRANT VERIFICATION ---")
    try:
        from qdrant_client import QdrantClient
        q_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
        q_api = os.environ.get("QDRANT_API_KEY")
        client = QdrantClient(url=q_url, api_key=q_api)
        
        scroll_res = client.scroll(collection_name="Industrial-docs", limit=1)
        if scroll_res and scroll_res[0]:
            pt = scroll_res[0][0]
            print(f"Point ID: {pt.id}")
            print(f"Payload: {pt.payload}")
        else:
            print("No points found in Qdrant.")
    except Exception as e:
        print(f"Qdrant Verification Failed: {e}")

    # 3. Postgres Verification
    print("\n--- POSTGRES VERIFICATION ---")
    import asyncio
    async def verify_postgres():
        import asyncpg
        pg_uri = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/hackathon_db")
        try:
            conn = await asyncpg.connect(pg_uri)
            # Need to test inserting a document first if it doesn't exist so the metadata_writer test actually had something to update
            # But here we just query whatever is in the ingestion_events table
            events = await conn.fetch("SELECT document_id, stage, status FROM ingestion_events LIMIT 3")
            for e in events:
                print(f"Event: Doc {e['document_id']} | Stage {e['stage']} | Status {e['status']}")
            await conn.close()
        except Exception as e:
            print(f"Postgres Verification Failed: {e}")
            
    asyncio.run(verify_postgres())

    print("\nPipeline Test Complete!")

if __name__ == "__main__":
    main()
