import os
import uuid
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

def write_to_vector_db(document_id: str, chunks: list, embeddings: list, equipment_tags: list):
    """
    Writes text chunks and their embeddings to Qdrant.
    """
    url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    api_key = os.environ.get("QDRANT_API_KEY")
    collection_name = "Industrial-docs"

    points = []
    print("\n--- GENERATED QDRANT PAYLOADS ---")
    for chunk, embedding in zip(chunks, embeddings):
        point_id = str(uuid.uuid4())
        payload = {
            "chunk": chunk,
            "document_id": document_id,
            "equipment_tag": equipment_tags[0] if equipment_tags else None,
            "neo4j_node_id": document_id,
            "page_number": 1
        }
        
        print(f"Point ID: {point_id}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        # embedding omitted from print for brevity
        
        point = PointStruct(
            id=point_id,
            vector={"BGE-m3": embedding},
            payload=payload
        )
        points.append(point)
    print("--- END QDRANT PAYLOADS ---")

    if not points:
        return

    try:
        client = QdrantClient(url=url, api_key=api_key)

        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print("Successfully wrote to Qdrant.")
    except Exception as e:
        print(f"Could not connect or write to Qdrant: {e}")
        print("Assuming running in test mode without DB.")
        
    return points

