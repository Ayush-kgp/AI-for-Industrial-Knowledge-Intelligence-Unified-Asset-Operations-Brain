import os
from dotenv import load_dotenv

from app.retrieval.planner import ask_planner

if __name__ == "__main__":
    load_dotenv()
    
    # Test 1: Single-tool (Equipment lookup)
    query = "What maintenance followed the Q3 pressure trip on C-101?"
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    ask_planner(query)
    
    # Test 2: Multi-step (Compressor trip -> procedures)
    # query2 = "Which maintenance procedures followed the last compressor trip?"
    # ask_planner(query2)
