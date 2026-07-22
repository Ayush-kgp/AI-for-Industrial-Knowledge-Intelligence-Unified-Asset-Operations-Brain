import os
import json
import asyncio
import asyncpg

from .graph_tools import get_graph_driver

async def async_get_document_status(document_id: str):
    uri = os.environ.get("DATABASE_URL")
    try:
        conn = await asyncpg.connect(uri)
        record = await conn.fetchrow(
            "SELECT id, title, ingestion_status FROM documents WHERE id = $1", 
            document_id
        )
        await conn.close()
        
        if record:
            return {
                "document_id": record["id"],
                "title": record["title"],
                "status": record["ingestion_status"]
            }
            
        # Fallback to Neo4j to see if it's a stub or missing from Postgres
        driver = get_graph_driver()
        try:
            records, _, _ = driver.execute_query(
                "MATCH (d:Document {id: $id}) RETURN d.title as title, coalesce(d.is_stub, false) as is_stub",
                id=document_id
            )
            if records:
                return {
                    "document_id": document_id,
                    "title": records[0]["title"],
                    "status": "Stub/Unprocessed (Graph Only)" if records[0]["is_stub"] else "Graph Only (Missing from Postgres metadata)"
                }
        finally:
            driver.close()
            
        return {"error": "Document not found in Postgres or Neo4j"}
    except Exception as e:
        return {"error": str(e)}

def get_document_status(document_id: str) -> str:
    """
    Retrieves the current metadata status of a document from Postgres.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_get_document_status(document_id))
    loop.close()
    return json.dumps(result, indent=2)
