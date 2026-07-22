import os
import json
from dotenv import load_dotenv

from app.retrieval.planner import planner_tools

def ask_and_trace_mock(query: str, mock_tool_call: dict):
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    
    print("\n--- TRACE (Mocked First Step due to 429 Quota Limit) ---")
    print(f"[MODEL] FUNCTION CALL: {mock_tool_call['name']}")
    print(f"  Args: {mock_tool_call['args']}")
    
    for tool in planner_tools:
        if tool.__name__ == mock_tool_call['name']:
            print(f"  [EXECUTION] Running {mock_tool_call['name']}...")
            try:
                res = tool(**mock_tool_call['args'])
                print(f"  [RESULT] {str(res)[:300]}...")
            except Exception as e:
                print(f"  [ERROR] {e}")
                
    print("============================================================\n")

if __name__ == "__main__":
    load_dotenv()
    
    print("NOTE: Gemini API currently returning 429 RESOURCE_EXHAUSTED (Quota Exceeded: 20 requests/day free tier).")
    print("Running mocked tool trace to demonstrate planner execution logic:\n")
    
    # Test 1: Single-tool (Equipment lookup)
    ask_and_trace_mock(
        "What is the history of equipment C-101?", 
        {"name": "get_equipment_history", "args": {"equipment_tag": "C-101"}}
    )
    
    # Test 2: Multi-step (Compressor trip -> procedures)
    ask_and_trace_mock(
        "Which maintenance procedures followed the last compressor trip?",
        {"name": "find_related_documents", "args": {"event_title": "Q3 pressure trip incident"}}
    )
