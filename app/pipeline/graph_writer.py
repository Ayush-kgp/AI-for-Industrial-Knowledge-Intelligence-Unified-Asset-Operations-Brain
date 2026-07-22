import os
import json
from neo4j import GraphDatabase
from app.pipeline.extractor import ExtractedEntities

def write_to_graph(document_id: str, document_title: str, entities: ExtractedEntities):
    """
    Writes extracted entities and relationships to Neo4j.
    """
    uri = os.environ.get("NEO4J_URI", "neo4j+s://localhost:7687")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    auth = (user, password) if user and password else None

    print("\n--- GENERATED CYPHER QUERIES ---")
    queries_to_run = []

    # Create the main document node
    type_map = {
        "procedure": "Procedure",
        "maintenancerecord": "MaintenanceRecord",
        "inspectionfinding": "InspectionFinding"
    }
    cleaned_type = entities.document_type.lower().replace("_", "").replace("-", "").replace(" ", "")
    doc_label = type_map.get(cleaned_type, "Document")

    queries_to_run.append((
        f"""
        MERGE (d:Document {{id: $document_id}})
        ON CREATE SET d.title = $title,
                      d.document_type = $doc_type,
                      d.is_stub = false
        ON MATCH SET d:{doc_label},
                     d.title = $title,
                     d.document_type = $doc_type,
                     d.is_stub = false
        """,
        {"document_id": document_id, "title": document_title, "doc_type": entities.document_type}
    ))

    # Equipment
    for tag in entities.equipment_tags:
        queries_to_run.append((
            """
            MERGE (e:Equipment {equipment_tag: $tag})
            """,
            {"tag": tag}
        ))
        
        if doc_label == "InspectionFinding":
            queries_to_run.append((
                """
                MATCH (d:Document {id: $document_id})
                MATCH (e:Equipment {equipment_tag: $tag})
                MERGE (e)-[:INSPECTED_ON]->(d)
                """,
                {"document_id": document_id, "tag": tag}
            ))
        else:
            queries_to_run.append((
                """
                MATCH (d:Document {id: $document_id})
                MATCH (e:Equipment {equipment_tag: $tag})
                MERGE (d)-[:MENTIONED_IN]->(e)
                """,
                {"document_id": document_id, "tag": tag}
            ))

    # Personnel
    for person in entities.personnel:
        queries_to_run.append((
            """
            MERGE (p:Person {name: $name})
            SET p.role = $role
            """,
            {"name": person.name, "role": person.role}
        ))
        
        maintenance_roles = ["technician", "maintainer", "mechanic"]
        is_maintenance = any(m_role in person.role.lower() for m_role in maintenance_roles)
        
        if is_maintenance and entities.equipment_tags:
            for tag in entities.equipment_tags:
                queries_to_run.append((
                    """
                    MATCH (p:Person {name: $name})
                    MATCH (e:Equipment {equipment_tag: $tag})
                    MERGE (e)-[:MAINTAINED_BY]->(p)
                    """,
                    {"name": person.name, "tag": tag}
                ))
        else:
            # Default MENTIONED_IN
            queries_to_run.append((
                """
                MATCH (d:Document {id: $document_id})
                MATCH (p:Person {name: $name})
                MERGE (d)-[:MENTIONED_IN]->(p)
                """,
                {"document_id": document_id, "name": person.name}
            ))
            
    # Regulatory Clauses
    for clause in entities.regulatory_clauses:
        queries_to_run.append((
            """
            MATCH (d:Document {id: $document_id})
            MERGE (r:RegulatoryClause {clause_id: $clause})
            MERGE (d)-[:GOVERNED_BY]->(r)
            """,
            {"document_id": document_id, "clause": clause}
        ))
        
    # Prior Events
    for event in entities.referenced_prior_events:
        queries_to_run.append((
            """
            MATCH (d:Document {id: $document_id})
            MERGE (stub:Document {title: $event_title})
            ON CREATE SET stub.is_stub = true
            MERGE (d)-[:PRECEDED_BY]->(stub)
            """,
            {"document_id": document_id, "event_title": event}
        ))

    # Referenced Documents
    for ref_doc in entities.referenced_documents:
        ref_title = ref_doc.get("title")
        if not ref_title:
            continue
            
        rel_type = ref_doc.get("relationship", "RELATED_TO").upper()
        # Sanitize relationship type just in case
        if rel_type not in ["UPDATES", "SUPERSEDES", "ISSUED_IN_RESPONSE_TO"]:
            rel_type = "RELATED_TO"
            
        queries_to_run.append((
            f"""
            MATCH (d:Document {{id: $document_id}})
            MERGE (stub:Document {{title: $ref_title}})
            ON CREATE SET stub.is_stub = true
            MERGE (d)-[:{rel_type}]->(stub)
            """,
            {"document_id": document_id, "ref_title": ref_title}
        ))

    # Print out all queries
    for q, params in queries_to_run:
        print(f"Query:\n{q.strip()}\nParams: {json.dumps(params)}\n")

    print("--- END CYPHER QUERIES ---")

    # Try to execute against Neo4j
    try:
        with GraphDatabase.driver(uri, auth=auth) as driver:
            with driver.session() as session:
                for query, params in queries_to_run:
                    session.run(query, **params)
        print("Successfully wrote to Neo4j.")
    except Exception as e:
        print(f"Could not connect or write to Neo4j: {e}")
        print("Assuming running in test mode without DB.")
        
    return queries_to_run

