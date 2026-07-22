import os
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('BAAI/bge-m3')

def get_qdrant_client():
    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")
    return QdrantClient(url=url, api_key=api_key)

def semantic_search_chunks(query: str) -> str:
    """
    Performs a semantic search over document chunks in Qdrant to find relevant text.
    Returns a JSON string containing the matched chunks, their document IDs, and associated Neo4j node IDs.
    """
    limit = 5
    client = get_qdrant_client()
    
    # Generate embedding for the query
    embedding = embedder.encode(query).tolist()
    
    # Search in Qdrant using the named vector 'BGE-m3'
    collection_name = "Industrial-docs"
    
    try:
        search_result = client.query_points(
            collection_name=collection_name,
            query=embedding,
            using="BGE-m3",
            limit=limit,
            with_payload=True
        )
        
        results = []
        for hit in search_result.points:
            payload = hit.payload
            results.append({
                "score": hit.score,
                "chunk": payload.get("chunk"),
                "document_id": payload.get("document_id"),
                "equipment_tag": payload.get("equipment_tag"),
                "neo4j_node_id": payload.get("neo4j_node_id"),
                "page_number": payload.get("page_number")
            })
            
        return json.dumps({"query": query, "results": results}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
