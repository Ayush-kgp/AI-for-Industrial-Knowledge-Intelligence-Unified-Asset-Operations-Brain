import os
import asyncio
from dotenv import load_dotenv

from app.pipeline.parser import parse_pdf
from app.pipeline.extractor import extract_entities
from app.pipeline.graph_writer import write_to_graph
from app.pipeline.vector_writer import write_to_vector_db
from app.pipeline.metadata_writer import update_ingestion_status
from sentence_transformers import SentenceTransformer

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    # Extremely simplified chunker for demo purposes
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

async def ingest_file(filename: str, doc_id: str):
    print(f"\n{'='*50}\nIngesting {filename} as {doc_id}\n{'='*50}")
    
    print("1. [Parser] Extracting text...")
    text = parse_pdf(filename)
    
    print("2. [Extractor] Extracting entities via Gemini...")
    entities = extract_entities(text)
    
    print("3. [Chunker] Chunking text...")
    chunks = chunk_text(text)
    
    print("4. [Embedder] Generating embeddings...")
    embedder = SentenceTransformer('BAAI/bge-m3')
    embeddings = embedder.encode(chunks)
    
    print("5. [Graph Writer] Writing to Neo4j...")
    write_to_graph(doc_id, filename, entities)
    
    print("6. [Vector Writer] Writing to Qdrant...")
    write_to_vector_db(doc_id, chunks, embeddings.tolist(), entities.equipment_tags)
    
    print("7. [Metadata Writer] Writing to Postgres...")
    await update_ingestion_status(doc_id, "complete", "batch_ingest", None)
    
    print(f"Finished {filename}!\n")

async def main():
    load_dotenv()
    files = [
        ("incident_q3_trip.pdf", "doc-incident-100"),
        ("sop_c101.pdf", "doc-sop-200"),
        ("inspection_q3.pdf", "doc-inspection-300")
    ]
    
    for filename, doc_id in files:
        await ingest_file(filename, doc_id)
        
    print("\nBatch Ingestion Complete!")

if __name__ == "__main__":
    asyncio.run(main())
