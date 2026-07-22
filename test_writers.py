import pytest
from app.pipeline.graph_writer import write_to_graph
from app.pipeline.vector_writer import write_to_vector_db
from app.pipeline.extractor import ExtractedEntities, Person

def test_graph_writer_maintenance_record():
    entities = ExtractedEntities(
        document_type="MaintenanceRecord",
        equipment_tags=["C-101"],
        dates=["October 15, 2023"],
        personnel=[
            Person(name="Jane Smith", role="Technician"),
            Person(name="John Doe", role="Supervisor")
        ],
        regulatory_clauses=["OSHA 1910.119"],
        referenced_prior_events=["Q3 incident"]
    )
    
    # Run the graph writer (we patched it to return the queries_to_run list)
    queries = write_to_graph("doc-1", "Test Doc", entities)
    
    # Verify the document creation Cypher
    doc_query, doc_params = queries[0]
    assert "CREATE (d:Document:MaintenanceRecord" in doc_query
    assert doc_params["document_id"] == "doc-1"
    
    # Verify equipment creation & edge
    eq_query, eq_params = queries[1]
    assert "MERGE (e:Equipment {equipment_tag: $tag})" in eq_query
    assert eq_params["tag"] == "C-101"
    
    # Verify MENTIONED_IN for Document->Equipment (fallback)
    ment_eq_query, ment_eq_params = queries[2]
    assert "MERGE (d)-[:MENTIONED_IN]->(e)" in ment_eq_query
    assert ment_eq_params["tag"] == "C-101"
    
    # Verify MAINTAINED_BY for Jane Smith
    # queries[3] is the Person merge, queries[4] is the relationship
    rel_jane_q, rel_jane_p = queries[4]
    assert "MERGE (e)-[:MAINTAINED_BY]->(p)" in rel_jane_q
    assert rel_jane_p["name"] == "Jane Smith"
    
    # Verify MENTIONED_IN for John Doe
    # queries[5] is Person merge, queries[6] is the relationship
    rel_john_q, rel_john_p = queries[6]
    assert "MERGE (d)-[:MENTIONED_IN]->(p)" in rel_john_q
    assert rel_john_p["name"] == "John Doe"

def test_graph_writer_inspection_finding():
    entities = ExtractedEntities(
        document_type="InspectionFinding",
        equipment_tags=["C-101"],
        dates=[],
        personnel=[],
        regulatory_clauses=[],
        referenced_prior_events=[]
    )
    
    queries = write_to_graph("doc-2", "Test Inspection", entities)
    
    doc_query, _ = queries[0]
    assert "CREATE (d:Document:InspectionFinding" in doc_query
    
    # queries[1] is Equipment merge
    # queries[2] should be INSPECTED_ON edge
    rel_q, rel_p = queries[2]
    assert "MERGE (e)-[:INSPECTED_ON]->(d)" in rel_q
    assert rel_p["tag"] == "C-101"

def test_graph_writer_no_equipment():
    entities = ExtractedEntities(
        document_type="Procedure",
        equipment_tags=[], # No equipment
        dates=[],
        personnel=[Person(name="Alice", role="Operator")],
        regulatory_clauses=[],
        referenced_prior_events=[]
    )
    
    queries = write_to_graph("doc-3", "General Proc", entities)
    
    # queries[0]: Create doc
    # queries[1]: MERGE Person Alice
    # queries[2]: MENTIONED_IN between Doc and Alice
    rel_q, rel_p = queries[2]
    assert "MERGE (d)-[:MENTIONED_IN]->(p)" in rel_q
    assert rel_p["name"] == "Alice"
    
def test_vector_writer_payloads():
    chunks = ["chunk 1", "chunk 2"]
    embeddings = [[0.1, 0.2], [0.3, 0.4]] # mocked embeddings
    equipment_tags = ["C-101"]
    
    points = write_to_vector_db("doc-4", chunks, embeddings, equipment_tags)
    
    assert len(points) == 2
    
    # Assert correct payload structure for first point
    payload1 = points[0].payload
    assert payload1["chunk"] == "chunk 1"
    assert payload1["document_id"] == "doc-4"
    assert payload1["equipment_tag"] == "C-101"
    assert payload1["neo4j_node_id"] == "doc-4"
    assert payload1["page_number"] == 1
    
    # Assert for second point
    payload2 = points[1].payload
    assert payload2["chunk"] == "chunk 2"

def test_vector_writer_no_equipment():
    chunks = ["chunk 1"]
    embeddings = [[0.1, 0.2]]
    equipment_tags = []
    
    points = write_to_vector_db("doc-5", chunks, embeddings, equipment_tags)
    assert points[0].payload["equipment_tag"] is None
