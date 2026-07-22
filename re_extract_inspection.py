import asyncio
from dotenv import load_dotenv

from app.pipeline.parser import parse_pdf
from app.pipeline.extractor import extract_entities
from app.pipeline.graph_writer import write_to_graph
from app.pipeline.metadata_writer import update_ingestion_status

async def main():
    load_dotenv()
    filename = "inspection_q3.pdf"
    doc_id = "doc-inspection-300"
    
    print(f"\n{'='*50}\nRe-extracting {filename} as {doc_id}\n{'='*50}")
    
    text = parse_pdf(filename)
    entities = extract_entities(text)
    
    print("Entities:", entities.model_dump_json(indent=2))
    
    # We only want to rewrite the graph to create the edges, we don't need to touch vector/metadata again.
    write_to_graph(doc_id, filename, entities)

if __name__ == "__main__":
    asyncio.run(main())
