import os
import asyncio
import asyncpg

async def update_ingestion_status(document_id: str, status: str, stage: str, error_message: str = None):
    """
    Updates the ingestion status in PostgreSQL.
    """
    uri = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/hackathon_db")
    
    print("\n--- GENERATED POSTGRES QUERIES ---")
    print(f"UPDATE documents SET ingestion_status = '{status}' WHERE id = '{document_id}'")
    print(f"INSERT INTO ingestion_events (document_id, stage, status, error_message) VALUES ('{document_id}', '{stage}', '{status}', '{error_message}')")
    print("--- END POSTGRES QUERIES ---")
    
    try:
        conn = await asyncpg.connect(uri)
        
        # Update documents table
        await conn.execute(
            "UPDATE documents SET ingestion_status = $1 WHERE id = $2",
            status, document_id
        )
        
        # Insert event
        await conn.execute(
            """
            INSERT INTO ingestion_events (document_id, stage, status, started_at, error_message) 
            VALUES ($1, $2, $3, CURRENT_TIMESTAMP, $4)
            """,
            document_id, stage, status, error_message
        )
        
        await conn.close()
        print("Successfully updated Postgres.")
    except Exception as e:
        print(f"Could not connect to Postgres: {e}")
        print("Assuming running in test mode without DB.")

def sync_update_ingestion_status(document_id: str, status: str, stage: str, error_message: str = None):
    asyncio.run(update_ingestion_status(document_id, status, stage, error_message))
