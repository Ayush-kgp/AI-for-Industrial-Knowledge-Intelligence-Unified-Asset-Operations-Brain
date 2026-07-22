import os
import json
from neo4j import GraphDatabase

def get_graph_driver():
    uri = os.environ.get("NEO4J_URI", "").replace("neo4j+s://", "neo4j+ssc://")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    return GraphDatabase.driver(uri, auth=(user, password))

def get_equipment_history(equipment_tag: str) -> str:
    """
    Retrieves the history of events, documents, and personnel related to a specific equipment tag.
    Returns a JSON string representing the timeline.
    """
    driver = get_graph_driver()
    try:
        # Query for documents mentioning the equipment, plus linked events/people/clauses
        query = """
        MATCH (e:Equipment {equipment_tag: $tag})
        OPTIONAL MATCH (e)<-[:MENTIONED_IN|MAINTAINED_BY]-(d:Document)
        OPTIONAL MATCH (d)-[:PRECEDED_BY]->(stub:Document {is_stub: true})
        OPTIONAL MATCH (d)-[:GOVERNED_BY]->(r:RegulatoryClause)
        OPTIONAL MATCH (d)-[:MENTIONED_IN]->(p:Person)
        RETURN d.title AS doc_title, 
               d.document_type AS doc_type, 
               d.id AS doc_id,
               stub.title AS prior_event,
               collect(DISTINCT r.clause_id) AS regulations,
               collect(DISTINCT p.name + ' (' + coalesce(p.role, 'Unknown') + ')') AS personnel
        """
        records, summary, keys = driver.execute_query(query, tag=equipment_tag)
        
        results = []
        for record in records:
            if record["doc_id"]:
                results.append({
                    "document_id": record["doc_id"],
                    "document_title": record["doc_title"],
                    "document_type": record["doc_type"],
                    "prior_event": record["prior_event"],
                    "regulations": record["regulations"],
                    "personnel": record["personnel"]
                })
        
        return json.dumps({"equipment_tag": equipment_tag, "history": results}, indent=2)
    finally:
        driver.close()

def find_related_documents(document_id: str, title: str) -> str:
    """
    Finds documents related to a given document ID or title/name (such as preceding incidents or subsequent actions).
    You must provide either document_id or title. For whichever one you don't use, pass an empty string "".
    Use title for partial case-insensitive matches (e.g. 'compressor trip').
    """
    if not document_id and not title:
        return json.dumps({"error": "Must provide either document_id or title"})
        
    driver = get_graph_driver()
    try:
        # Match by ID or by partial title
        if document_id:
            match_clause = "MATCH (d:Document {id: $doc_id})"
            params = {"doc_id": document_id}
        else:
            # Tokenize the search title and do an OR match for partial fuzzy matching
            tokens = [t.lower() for t in title.split() if len(t) > 2]
            if not tokens:
                tokens = [title.lower()]
            where_conditions = " OR ".join([f"toLower(d.title) CONTAINS '{t}'" for t in tokens])
            match_clause = f"MATCH (d:Document) WHERE {where_conditions}"
            params = {}

        query = f"""
        {match_clause}
        MATCH (d)-[r]-(related:Document)
        RETURN d.id AS source_id,
               d.title AS source_title,
               type(r) AS relationship_type,
               related.id AS related_id,
               related.title AS related_title,
               related.is_stub AS is_stub
        LIMIT 50
        """
        records, summary, keys = driver.execute_query(query, **params)
        
        results = []
        for record in records:
            results.append({
                "source_id": record["source_id"],
                "source_title": record["source_title"],
                "relationship_type": record["relationship_type"],
                "related_id": record["related_id"],
                "related_title": record["related_title"],
                "related_is_stub": record["is_stub"]
            })
            
        return json.dumps({"related_documents": results}, indent=2)
    finally:
        driver.close()

